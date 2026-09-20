"""
LinkCraftor Semantic Intelligence

4.6.20 ? Knowledge Retrieval

Consumes only the certified 4.6.19K Profile Store result.

Knowledge Retrieval does not:
- rewrite semantic meaning,
- modify certified profiles,
- perform cross-document reasoning,
- write Semantic Memory,
- make linking decisions.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


KNOWLEDGE_RETRIEVAL_VERSION = "knowledge_retrieval_v1"
KNOWLEDGE_RETRIEVAL_PHASE = "4.6.20"


class KnowledgeRetrievalError(Exception):
    """Raised when the Knowledge Retrieval contract is violated."""

# =====================================================================
# PATCH 4.6.20A ? Certified 4.6.19K Input Contract Inspection
# =====================================================================

def inspect_certified_profile_store_input_v1(
    certified_store_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Inspect the exact frozen 4.6.19K Profile Store certification envelope.

    This stage performs inspection only.

    It does not:
    - retrieve knowledge,
    - read another article,
    - perform cross-document reasoning,
    - modify the certified profile,
    - write Semantic Memory,
    - make linking decisions.
    """

    from collections.abc import Mapping
    from copy import deepcopy

    if not isinstance(
        certified_store_result,
        Mapping,
    ):
        raise KnowledgeRetrievalError(
            "certified_store_result must be a mapping."
        )

    # -------------------------------------------------------------
    # Exact 4.6.19K lifecycle
    # -------------------------------------------------------------

    required_lifecycle = {
        "schema_version":
            "certified_semantic_article_profile_store_result_v1",

        "version":
            "semantic_article_profile_store_v1",

        "phase":
            "4.6.19",

        "patch":
            "4.6.19K",

        "status":
            "SEMANTIC_ARTICLE_PROFILE_STORE_CERTIFIED",

        "persistence_policy":
            "PROFILE_STORE_CERTIFIED_PERSISTENCE",

        "next_stage":
            "knowledge_retrieval",
    }

    for field, expected in required_lifecycle.items():

        if certified_store_result.get(field) != expected:
            raise KnowledgeRetrievalError(
                f"Invalid certified Profile Store field: {field}"
            )

    certification = certified_store_result.get(
        "full_profile_store_certification"
    )

    storage_identity = certified_store_result.get(
        "storage_identity"
    )

    store_metadata = certified_store_result.get(
        "store_metadata"
    )

    stored_profile = certified_store_result.get(
        "stored_semantic_article_profile"
    )

    certified_profile = certified_store_result.get(
        "certified_semantic_article_profile"
    )

    stored_record = certified_store_result.get(
        "verified_stored_record"
    )

    canonical_identity = certified_store_result.get(
        "canonical_article_identity"
    )

    final_summary = certified_store_result.get(
        "final_result_summary"
    )

    boundaries = certified_store_result.get(
        "processing_boundaries"
    )

    for name, value in (
        (
            "full_profile_store_certification",
            certification,
        ),
        (
            "storage_identity",
            storage_identity,
        ),
        (
            "store_metadata",
            store_metadata,
        ),
        (
            "stored_semantic_article_profile",
            stored_profile,
        ),
        (
            "certified_semantic_article_profile",
            certified_profile,
        ),
        (
            "verified_stored_record",
            stored_record,
        ),
        (
            "canonical_article_identity",
            canonical_identity,
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

        if not isinstance(value, Mapping):
            raise KnowledgeRetrievalError(
                name + " is missing."
            )

    # -------------------------------------------------------------
    # Full Profile Store certification authority
    # -------------------------------------------------------------

    for field, expected in (
        (
            "certification_status",
            "CERTIFIED",
        ),
        (
            "certification_scope",
            "FULL_SEMANTIC_ARTICLE_PROFILE_STORE_PIPELINE",
        ),
        (
            "certification_mode",
            "END_TO_END_PERSISTENCE_INTEGRITY_IMMUTABILITY_HARD_CERTIFICATION",
        ),
        (
            "certified_phase",
            "4.6.19",
        ),
        (
            "certified_source_patch",
            "4.6.19J",
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
            "knowledge_retrieval_owner",
            "4.6.20_KNOWLEDGE_RETRIEVAL",
        ),
        (
            "semantic_memory_owner",
            "4.6.28_SEMANTIC_MEMORY",
        ),
    ):

        if certification.get(field) != expected:
            raise KnowledgeRetrievalError(
                f"Profile Store certification field drifted: {field}"
            )

    for field in (
        "profile_certified",
        "profile_store_persisted",
        "profile_store_written",
        "storage_identity_certified",
        "persistence_envelope_certified",
        "write_contract_certified",
        "read_back_certified",
        "integrity_certified",
        "immutability_certified",
        "metadata_versioning_certified",
        "final_stored_result_certified",
        "canonical_identity_preserved",
        "payload_hash_preserved",
        "payload_byte_length_preserved",
        "profile_payload_immutable",
        "metadata_separate_from_profile_payload",
    ):

        if certification.get(field) is not True:
            raise KnowledgeRetrievalError(
                f"Required Profile Store certification field "
                f"is not True: {field}"
            )

    for field in (
        "source_profile_payload_mutated",
        "additional_profile_write_performed",
        "physical_profile_rewrite_performed",
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

        if certification.get(field) is not False:
            raise KnowledgeRetrievalError(
                f"Forbidden Profile Store certification field "
                f"is not False: {field}"
            )

    # -------------------------------------------------------------
    # Stored-profile authority
    # -------------------------------------------------------------

    if stored_profile.get(
        "stored_profile_schema"
    ) != "stored_semantic_article_profile_v1":
        raise KnowledgeRetrievalError(
            "Stored profile schema drifted."
        )

    if stored_profile.get(
        "store_status"
    ) != "PERSISTED":
        raise KnowledgeRetrievalError(
            "Stored profile is not persisted."
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
            raise KnowledgeRetrievalError(
                f"Required stored-profile field is not True: {field}"
            )

    for field in (
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if stored_profile.get(field) is not False:
            raise KnowledgeRetrievalError(
                f"Forbidden stored-profile field is not False: {field}"
            )

    # -------------------------------------------------------------
    # Immutable certified profile authority
    # -------------------------------------------------------------

    stored_payload = stored_profile.get(
        "certified_profile_payload"
    )

    if stored_payload != certified_profile:
        raise KnowledgeRetrievalError(
            "Stored certified payload differs from certified profile."
        )

    if certified_profile.get(
        "profile_certified"
    ) is not True:
        raise KnowledgeRetrievalError(
            "Certified profile is not certified."
        )

    if certified_profile.get(
        "profile_store_ready"
    ) is not True:
        raise KnowledgeRetrievalError(
            "Certified profile is not store-ready."
        )

    if certified_profile.get(
        "profile_persisted"
    ) is not False:
        raise KnowledgeRetrievalError(
            "Immutable certified profile persistence flag drifted."
        )

    if certified_profile.get(
        "profile_store_owner"
    ) != "4.6.19_PROFILE_STORE":
        raise KnowledgeRetrievalError(
            "Profile Store owner drifted."
        )

    if certified_profile.get(
        "semantic_memory_owner"
    ) != "4.6.28_SEMANTIC_MEMORY":
        raise KnowledgeRetrievalError(
            "Semantic Memory owner drifted."
        )

    # -------------------------------------------------------------
    # Identity / metadata cross-check
    # -------------------------------------------------------------

    storage_key = storage_identity.get(
        "storage_key"
    )

    if not isinstance(storage_key, str) or not storage_key:
        raise KnowledgeRetrievalError(
            "Certified storage key is missing."
        )

    for source_name, source in (
        (
            "stored_profile",
            stored_profile,
        ),
        (
            "store_metadata",
            store_metadata,
        ),
        (
            "verified_stored_record",
            stored_record,
        ),
    ):

        if source.get(
            "storage_key"
        ) != storage_key:
            raise KnowledgeRetrievalError(
                f"{source_name} storage key drifted."
            )

    if store_metadata.get(
        "workspace_id"
    ) != canonical_identity.get(
        "workspace_id"
    ):
        raise KnowledgeRetrievalError(
            "Workspace identity drifted."
        )

    if store_metadata.get(
        "article_id"
    ) != canonical_identity.get(
        "article_id"
    ):
        raise KnowledgeRetrievalError(
            "Article identity drifted."
        )

    # -------------------------------------------------------------
    # Final Profile Store summary
    # -------------------------------------------------------------

    if final_summary.get(
        "final_status"
    ) != "STORED_SEMANTIC_ARTICLE_PROFILE_READY":
        raise KnowledgeRetrievalError(
            "Final Profile Store summary status drifted."
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

        if final_summary.get(field) is not True:
            raise KnowledgeRetrievalError(
                f"Required final-summary field is not True: {field}"
            )

    for field in (
        "source_profile_payload_mutated",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if final_summary.get(field) is not False:
            raise KnowledgeRetrievalError(
                f"Forbidden final-summary field is not False: {field}"
            )

    if final_summary.get(
        "knowledge_retrieval_next_owner"
    ) != "4.6.20_KNOWLEDGE_RETRIEVAL":
        raise KnowledgeRetrievalError(
            "Knowledge Retrieval ownership handoff drifted."
        )

    # -------------------------------------------------------------
    # K processing boundaries
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
        "final_stored_profile_result_preserved",
        "full_profile_store_certification_performed",
        "profile_store_certified",
        "profile_payload_immutability_preserved",
        "store_metadata_profile_separation_preserved",
    ):

        if boundaries.get(field) is not True:
            raise KnowledgeRetrievalError(
                f"Required 4.6.19K boundary is not True: {field}"
            )

    for field in (
        "additional_profile_write_performed",
        "physical_profile_rewrite_performed",
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
            raise KnowledgeRetrievalError(
                f"Forbidden 4.6.19K boundary is not False: {field}"
            )

    # -------------------------------------------------------------
    # Inspection result
    # -------------------------------------------------------------

    return {
        "schema_version":
            "knowledge_retrieval_input_inspection_result_v1",

        "version":
            KNOWLEDGE_RETRIEVAL_VERSION,

        "phase":
            KNOWLEDGE_RETRIEVAL_PHASE,

        "patch":
            "4.6.20A",

        "status":
            "CERTIFIED_PROFILE_STORE_INPUT_INSPECTED",

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
                dict(store_metadata)
            ),

        "stored_semantic_article_profile":
            deepcopy(
                dict(stored_profile)
            ),

        "certified_semantic_article_profile":
            deepcopy(
                dict(certified_profile)
            ),

        "source_certified_profile_store_result":
            deepcopy(
                dict(certified_store_result)
            ),

        "inspection": {
            "inspection_status":
                "PASSED",

            "inspection_scope":
                "CERTIFIED_4.6.19K_PROFILE_STORE_INPUT",

            "source_phase":
                "4.6.19",

            "source_patch":
                "4.6.19K",

            "source_store_certified":
                True,

            "source_profile_certified":
                True,

            "source_profile_persisted_in_store":
                True,

            "source_profile_payload_immutable":
                True,

            "storage_identity_available":
                True,

            "store_metadata_available":
                True,

            "profile_payload_available_for_retrieval":
                True,

            "knowledge_retrieval_owner_confirmed":
                True,

            "semantic_memory_deferred":
                True,

            "cross_document_reasoning_deferred":
                True,

            "knowledge_retrieval_performed":
                False,
        },

        "processing_boundaries": {
            "certified_profile_store_input_inspected":
                True,

            "certified_profile_store_input_preserved":
                True,

            "storage_identity_preserved":
                True,

            "store_metadata_preserved":
                True,

            "stored_profile_preserved":
                True,

            "certified_profile_preserved":
                True,

            "knowledge_retrieval_performed":
                False,

            "stored_profile_lookup_performed":
                False,

            "retrieval_query_created":
                False,

            "retrieval_payload_assembled":
                False,

            "retrieval_integrity_verification_performed":
                False,

            "retrieval_projection_performed":
                False,

            "retrieval_metadata_provenance_built":
                False,

            "final_knowledge_retrieval_result_built":
                False,

            "full_knowledge_retrieval_certification_performed":
                False,

            "profile_payload_modified":
                False,

            "semantic_state_modified":
                False,

            "semantic_meaning_rewritten":
                False,

            "cross_document_reasoning_performed":
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
        },

        "retrieval_policy":
            "INSPECTION_ONLY_NO_RETRIEVAL",

        "next_stage":
            "knowledge_retrieval_architecture_definition",
    }


# =====================================================================
# PATCH 4.6.20B ? Knowledge Retrieval Architecture Definition
# =====================================================================

def define_knowledge_retrieval_architecture_v1() -> dict[str, Any]:
    """
    Define the canonical Knowledge Retrieval architecture.

    This stage defines structure and ownership only.
    It performs no retrieval.
    """

    from copy import deepcopy

    architecture = {
        "architecture_schema":
            "knowledge_retrieval_architecture_v1",

        "architecture_version":
            KNOWLEDGE_RETRIEVAL_VERSION,

        "phase":
            KNOWLEDGE_RETRIEVAL_PHASE,

        "architecture_owner":
            "4.6.20_KNOWLEDGE_RETRIEVAL",

        "source_owner":
            "4.6.19_PROFILE_STORE",

        "next_reasoning_owner":
            "4.6.21_CROSS_DOCUMENT_REASONING",

        "semantic_memory_owner":
            "4.6.28_SEMANTIC_MEMORY",

        "retrieval_scope":
            "CERTIFIED_STORED_SEMANTIC_ARTICLE_PROFILE_RETRIEVAL",

        "retrieval_mode":
            "READ_ONLY_CERTIFIED_PROFILE_RETRIEVAL",

        "input_contract":
            "certified_semantic_article_profile_store_result_v1",

        "output_contract":
            "certified_knowledge_retrieval_result_v1",

        "canonical_source":
            "4.6.19K_CERTIFIED_PROFILE_STORE",

        "stage_order": [
            "certified_profile_store_input_inspection",
            "knowledge_retrieval_architecture_definition",
            "retrieval_intake_validation",
            "retrieval_identity_query_contract",
            "stored_profile_lookup",
            "retrieval_payload_assembly",
            "retrieval_integrity_verification",
            "retrieval_filtering_projection_contract",
            "retrieval_metadata_provenance",
            "final_knowledge_retrieval_result",
            "full_knowledge_retrieval_hard_certification",
        ],

        "stage_patch_map": {
            "certified_profile_store_input_inspection":
                "4.6.20A",

            "knowledge_retrieval_architecture_definition":
                "4.6.20B",

            "retrieval_intake_validation":
                "4.6.20C",

            "retrieval_identity_query_contract":
                "4.6.20D",

            "stored_profile_lookup":
                "4.6.20E",

            "retrieval_payload_assembly":
                "4.6.20F",

            "retrieval_integrity_verification":
                "4.6.20G",

            "retrieval_filtering_projection_contract":
                "4.6.20H",

            "retrieval_metadata_provenance":
                "4.6.20I",

            "final_knowledge_retrieval_result":
                "4.6.20J",

            "full_knowledge_retrieval_hard_certification":
                "4.6.20K",
        },

        "retrieval_principles": {
            "certified_store_only":
                True,

            "read_only":
                True,

            "deterministic":
                True,

            "identity_bound":
                True,

            "integrity_verified":
                True,

            "provenance_preserved":
                True,

            "profile_payload_immutable":
                True,

            "no_semantic_rewrite":
                True,

            "no_semantic_state_mutation":
                True,

            "no_cross_document_reasoning":
                True,

            "no_new_reasoning":
                True,

            "no_fact_inference":
                True,

            "no_relation_inference":
                True,

            "no_conflict_resolution":
                True,

            "no_uncertainty_reinterpretation":
                True,

            "no_confidence_recalculation":
                True,

            "no_semantic_memory_write":
                True,

            "no_linking_decisions":
                True,
        },

        "retrieval_capabilities": {
            "retrieve_by_storage_key":
                True,

            "retrieve_by_canonical_article_identity":
                True,

            "retrieve_full_certified_profile":
                True,

            "retrieve_profile_projection":
                True,

            "retrieve_selected_profile_sections":
                True,

            "preserve_store_metadata":
                True,

            "preserve_profile_store_version":
                True,

            "preserve_profile_payload_hash":
                True,

            "preserve_canonical_identity":
                True,

            "attach_retrieval_provenance":
                True,
        },

        "retrieval_boundaries": {
            "profile_store_write_allowed":
                False,

            "profile_rewrite_allowed":
                False,

            "profile_recertification_allowed":
                False,

            "cross_document_reasoning_allowed":
                False,

            "semantic_memory_write_allowed":
                False,

            "linking_decisions_allowed":
                False,

            "external_model_call_allowed":
                False,

            "retrieval_only":
                True,
        },

        "ownership_boundaries": {
            "profile_persistence":
                "4.6.19_PROFILE_STORE",

            "knowledge_retrieval":
                "4.6.20_KNOWLEDGE_RETRIEVAL",

            "cross_document_reasoning":
                "4.6.21_CROSS_DOCUMENT_REASONING",

            "semantic_memory":
                "4.6.28_SEMANTIC_MEMORY",
        },

        "identity_contract": {
            "primary_lookup_key":
                "storage_key",

            "secondary_lookup_identity":
                "canonical_article_identity",

            "workspace_scoped":
                True,

            "article_scoped":
                True,

            "version_aware":
                True,

            "payload_hash_bound":
                True,
        },

        "projection_contract": {
            "full_profile_allowed":
                True,

            "section_projection_allowed":
                True,

            "semantic_mutation_allowed":
                False,

            "projection_changes_source":
                False,

            "projection_must_preserve_provenance":
                True,
        },

        "integrity_contract": {
            "verify_storage_key":
                True,

            "verify_canonical_identity":
                True,

            "verify_payload_hash":
                True,

            "verify_payload_byte_length":
                True,

            "verify_store_version":
                True,

            "verify_profile_certification":
                True,

            "verify_profile_immutability":
                True,
        },

        "provenance_contract": {
            "source_phase":
                "4.6.19",

            "source_patch":
                "4.6.19K",

            "source_store_certification_required":
                True,

            "source_storage_identity_required":
                True,

            "source_store_metadata_required":
                True,

            "source_profile_hash_required":
                True,

            "retrieval_identity_required":
                True,
        },

        "execution_contract": {
            "4.6.20A":
                "INSPECTION_ONLY",

            "4.6.20B":
                "ARCHITECTURE_ONLY",

            "4.6.20C":
                "VALIDATION_ONLY",

            "4.6.20D":
                "QUERY_CONTRACT_ONLY",

            "4.6.20E":
                "LOOKUP_ALLOWED",

            "4.6.20F":
                "PAYLOAD_ASSEMBLY_ONLY",

            "4.6.20G":
                "INTEGRITY_VERIFICATION_ONLY",

            "4.6.20H":
                "PROJECTION_ONLY",

            "4.6.20I":
                "METADATA_PROVENANCE_ONLY",

            "4.6.20J":
                "FINAL_RESULT_ASSEMBLY_ONLY",

            "4.6.20K":
                "FULL_CERTIFICATION_ONLY",
        },

        "architecture_status":
            "DEFINED",

        "retrieval_performed":
            False,

        "semantic_memory_written":
            False,

        "cross_document_reasoning_performed":
            False,

        "linking_decisions_performed":
            False,
    }

    return deepcopy(
        architecture
    )


# =====================================================================
# PATCH 4.6.20C ? Retrieval Intake Validation
# =====================================================================

def validate_knowledge_retrieval_intake_v1(
    inspection_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Validate the certified 4.6.20A retrieval intake against the
    canonical 4.6.20B Knowledge Retrieval architecture.

    C performs validation only.
    No lookup or retrieval is performed.
    """

    from collections.abc import Mapping
    from copy import deepcopy

    if not isinstance(
        inspection_result,
        Mapping,
    ):
        raise KnowledgeRetrievalError(
            "inspection_result must be a mapping."
        )

    architecture = define_knowledge_retrieval_architecture_v1()

    # -------------------------------------------------------------
    # Exact 4.6.20A lifecycle
    # -------------------------------------------------------------

    for field, expected in (
        (
            "schema_version",
            "knowledge_retrieval_input_inspection_result_v1",
        ),
        (
            "version",
            KNOWLEDGE_RETRIEVAL_VERSION,
        ),
        (
            "phase",
            KNOWLEDGE_RETRIEVAL_PHASE,
        ),
        (
            "patch",
            "4.6.20A",
        ),
        (
            "status",
            "CERTIFIED_PROFILE_STORE_INPUT_INSPECTED",
        ),
        (
            "retrieval_policy",
            "INSPECTION_ONLY_NO_RETRIEVAL",
        ),
        (
            "next_stage",
            "knowledge_retrieval_architecture_definition",
        ),
    ):

        if inspection_result.get(field) != expected:
            raise KnowledgeRetrievalError(
                f"Invalid 4.6.20A lifecycle field: {field}"
            )

    inspection = inspection_result.get(
        "inspection"
    )

    canonical_identity = inspection_result.get(
        "canonical_article_identity"
    )

    storage_identity = inspection_result.get(
        "storage_identity"
    )

    store_metadata = inspection_result.get(
        "store_metadata"
    )

    stored_profile = inspection_result.get(
        "stored_semantic_article_profile"
    )

    certified_profile = inspection_result.get(
        "certified_semantic_article_profile"
    )

    boundaries = inspection_result.get(
        "processing_boundaries"
    )

    source_store_result = inspection_result.get(
        "source_certified_profile_store_result"
    )

    for name, value in (
        ("inspection", inspection),
        ("canonical_article_identity", canonical_identity),
        ("storage_identity", storage_identity),
        ("store_metadata", store_metadata),
        ("stored_semantic_article_profile", stored_profile),
        ("certified_semantic_article_profile", certified_profile),
        ("processing_boundaries", boundaries),
        ("source_certified_profile_store_result", source_store_result),
    ):

        if not isinstance(
            value,
            Mapping,
        ):
            raise KnowledgeRetrievalError(
                name + " is missing."
            )

    # -------------------------------------------------------------
    # 4.6.20A inspection authority
    # -------------------------------------------------------------

    for field, expected in (
        (
            "inspection_status",
            "PASSED",
        ),
        (
            "inspection_scope",
            "CERTIFIED_4.6.19K_PROFILE_STORE_INPUT",
        ),
        (
            "source_phase",
            "4.6.19",
        ),
        (
            "source_patch",
            "4.6.19K",
        ),
    ):

        if inspection.get(field) != expected:
            raise KnowledgeRetrievalError(
                f"Inspection field drifted: {field}"
            )

    for field in (
        "source_store_certified",
        "source_profile_certified",
        "source_profile_persisted_in_store",
        "source_profile_payload_immutable",
        "storage_identity_available",
        "store_metadata_available",
        "profile_payload_available_for_retrieval",
        "knowledge_retrieval_owner_confirmed",
        "semantic_memory_deferred",
        "cross_document_reasoning_deferred",
    ):

        if inspection.get(field) is not True:
            raise KnowledgeRetrievalError(
                f"Required inspection field is not True: {field}"
            )

    if inspection.get(
        "knowledge_retrieval_performed"
    ) is not False:
        raise KnowledgeRetrievalError(
            "Knowledge retrieval occurred before intake validation."
        )

    # -------------------------------------------------------------
    # Architecture authority
    # -------------------------------------------------------------

    if architecture.get(
        "architecture_status"
    ) != "DEFINED":
        raise KnowledgeRetrievalError(
            "Knowledge Retrieval architecture is not defined."
        )

    if architecture.get(
        "architecture_owner"
    ) != "4.6.20_KNOWLEDGE_RETRIEVAL":
        raise KnowledgeRetrievalError(
            "Knowledge Retrieval architecture ownership drifted."
        )

    if architecture.get(
        "canonical_source"
    ) != "4.6.19K_CERTIFIED_PROFILE_STORE":
        raise KnowledgeRetrievalError(
            "Knowledge Retrieval canonical source drifted."
        )

    principles = architecture.get(
        "retrieval_principles"
    )

    retrieval_boundaries = architecture.get(
        "retrieval_boundaries"
    )

    identity_contract = architecture.get(
        "identity_contract"
    )

    provenance_contract = architecture.get(
        "provenance_contract"
    )

    execution_contract = architecture.get(
        "execution_contract"
    )

    for name, value in (
        ("retrieval_principles", principles),
        ("retrieval_boundaries", retrieval_boundaries),
        ("identity_contract", identity_contract),
        ("provenance_contract", provenance_contract),
        ("execution_contract", execution_contract),
    ):

        if not isinstance(value, Mapping):
            raise KnowledgeRetrievalError(
                "Architecture section missing: " + name
            )

    for field in (
        "certified_store_only",
        "read_only",
        "deterministic",
        "identity_bound",
        "integrity_verified",
        "provenance_preserved",
        "profile_payload_immutable",
        "no_semantic_rewrite",
        "no_semantic_state_mutation",
        "no_cross_document_reasoning",
        "no_new_reasoning",
        "no_fact_inference",
        "no_relation_inference",
        "no_conflict_resolution",
        "no_uncertainty_reinterpretation",
        "no_confidence_recalculation",
        "no_semantic_memory_write",
        "no_linking_decisions",
    ):

        if principles.get(field) is not True:
            raise KnowledgeRetrievalError(
                f"Required architecture principle is not True: {field}"
            )

    if retrieval_boundaries.get(
        "retrieval_only"
    ) is not True:
        raise KnowledgeRetrievalError(
            "Architecture is not retrieval-only."
        )

    for field in (
        "profile_store_write_allowed",
        "profile_rewrite_allowed",
        "profile_recertification_allowed",
        "cross_document_reasoning_allowed",
        "semantic_memory_write_allowed",
        "linking_decisions_allowed",
        "external_model_call_allowed",
    ):

        if retrieval_boundaries.get(field) is not False:
            raise KnowledgeRetrievalError(
                f"Forbidden architecture boundary is enabled: {field}"
            )

    if execution_contract.get(
        "4.6.20C"
    ) != "VALIDATION_ONLY":
        raise KnowledgeRetrievalError(
            "4.6.20C execution contract drifted."
        )

    # -------------------------------------------------------------
    # Canonical identity validation
    # -------------------------------------------------------------

    workspace_id = canonical_identity.get(
        "workspace_id"
    )

    article_id = canonical_identity.get(
        "article_id"
    )

    if not isinstance(
        workspace_id,
        str,
    ) or not workspace_id:
        raise KnowledgeRetrievalError(
            "workspace_id must be a non-empty string."
        )

    if not isinstance(
        article_id,
        str,
    ) or not article_id:
        raise KnowledgeRetrievalError(
            "article_id must be a non-empty string."
        )

    profile_identity = certified_profile.get(
        "profile_identity"
    )

    if not isinstance(
        profile_identity,
        Mapping,
    ):
        raise KnowledgeRetrievalError(
            "Certified profile identity is missing."
        )

    if profile_identity.get(
        "canonical_article_identity"
    ) != canonical_identity:
        raise KnowledgeRetrievalError(
            "Certified profile canonical identity drifted."
        )

    # -------------------------------------------------------------
    # Storage identity validation
    # -------------------------------------------------------------

    storage_key = storage_identity.get(
        "storage_key"
    )

    if not isinstance(
        storage_key,
        str,
    ) or not storage_key:
        raise KnowledgeRetrievalError(
            "storage_key must be a non-empty string."
        )

    if storage_identity.get(
        "workspace_id"
    ) != workspace_id:
        raise KnowledgeRetrievalError(
            "Storage identity workspace drifted."
        )

    if storage_identity.get(
        "article_id"
    ) != article_id:
        raise KnowledgeRetrievalError(
            "Storage identity article drifted."
        )

    if identity_contract.get(
        "primary_lookup_key"
    ) != "storage_key":
        raise KnowledgeRetrievalError(
            "Primary lookup key contract drifted."
        )

    if identity_contract.get(
        "secondary_lookup_identity"
    ) != "canonical_article_identity":
        raise KnowledgeRetrievalError(
            "Secondary lookup identity contract drifted."
        )

    # -------------------------------------------------------------
    # Store metadata validation
    # -------------------------------------------------------------

    if store_metadata.get(
        "storage_key"
    ) != storage_key:
        raise KnowledgeRetrievalError(
            "Store metadata storage key drifted."
        )

    if store_metadata.get(
        "workspace_id"
    ) != workspace_id:
        raise KnowledgeRetrievalError(
            "Store metadata workspace drifted."
        )

    if store_metadata.get(
        "article_id"
    ) != article_id:
        raise KnowledgeRetrievalError(
            "Store metadata article drifted."
        )

    # -------------------------------------------------------------
    # Stored profile validation
    # -------------------------------------------------------------

    if stored_profile.get(
        "storage_key"
    ) != storage_key:
        raise KnowledgeRetrievalError(
            "Stored profile storage key drifted."
        )

    if stored_profile.get(
        "store_status"
    ) != "PERSISTED":
        raise KnowledgeRetrievalError(
            "Stored profile is not persisted."
        )

    stored_payload = stored_profile.get(
        "certified_profile_payload"
    )

    if stored_payload != certified_profile:
        raise KnowledgeRetrievalError(
            "Stored profile payload drifted."
        )

    if certified_profile.get(
        "profile_certified"
    ) is not True:
        raise KnowledgeRetrievalError(
            "Certified profile is not certified."
        )

    if certified_profile.get(
        "profile_store_ready"
    ) is not True:
        raise KnowledgeRetrievalError(
            "Certified profile is not store-ready."
        )

    if certified_profile.get(
        "profile_persisted"
    ) is not False:
        raise KnowledgeRetrievalError(
            "Immutable certified profile was mutated."
        )

    # -------------------------------------------------------------
    # Provenance contract validation
    # -------------------------------------------------------------

    if provenance_contract.get(
        "source_phase"
    ) != "4.6.19":
        raise KnowledgeRetrievalError(
            "Retrieval provenance source phase drifted."
        )

    if provenance_contract.get(
        "source_patch"
    ) != "4.6.19K":
        raise KnowledgeRetrievalError(
            "Retrieval provenance source patch drifted."
        )

    for field in (
        "source_store_certification_required",
        "source_storage_identity_required",
        "source_store_metadata_required",
        "source_profile_hash_required",
        "retrieval_identity_required",
    ):

        if provenance_contract.get(field) is not True:
            raise KnowledgeRetrievalError(
                f"Required provenance contract field is not True: {field}"
            )

    # -------------------------------------------------------------
    # A processing boundary authority
    # -------------------------------------------------------------

    for field in (
        "certified_profile_store_input_inspected",
        "certified_profile_store_input_preserved",
        "storage_identity_preserved",
        "store_metadata_preserved",
        "stored_profile_preserved",
        "certified_profile_preserved",
    ):

        if boundaries.get(field) is not True:
            raise KnowledgeRetrievalError(
                f"Required 4.6.20A boundary is not True: {field}"
            )

    for field in (
        "knowledge_retrieval_performed",
        "stored_profile_lookup_performed",
        "retrieval_query_created",
        "retrieval_payload_assembled",
        "retrieval_integrity_verification_performed",
        "retrieval_projection_performed",
        "retrieval_metadata_provenance_built",
        "final_knowledge_retrieval_result_built",
        "full_knowledge_retrieval_certification_performed",
        "profile_payload_modified",
        "semantic_state_modified",
        "semantic_meaning_rewritten",
        "cross_document_reasoning_performed",
        "new_reasoning_performed",
        "new_fact_inference_performed",
        "new_relation_inference_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if boundaries.get(field) is not False:
            raise KnowledgeRetrievalError(
                f"Forbidden 4.6.20A boundary is not False: {field}"
            )

    # -------------------------------------------------------------
    # Validated intake envelope
    # -------------------------------------------------------------

    intake_validation = {
        "validation_status":
            "VALIDATED",

        "validation_scope":
            "CERTIFIED_KNOWLEDGE_RETRIEVAL_INTAKE",

        "source_inspection_patch":
            "4.6.20A",

        "architecture_patch":
            "4.6.20B",

        "canonical_identity_validated":
            True,

        "storage_identity_validated":
            True,

        "store_metadata_validated":
            True,

        "stored_profile_validated":
            True,

        "certified_profile_validated":
            True,

        "profile_store_certification_preserved":
            True,

        "profile_payload_immutability_preserved":
            True,

        "knowledge_retrieval_owner_validated":
            True,

        "profile_store_owner_preserved":
            True,

        "semantic_memory_owner_preserved":
            True,

        "cross_document_reasoning_deferred":
            True,

        "semantic_memory_deferred":
            True,

        "knowledge_retrieval_performed":
            False,

        "stored_profile_lookup_performed":
            False,
    }

    return {
        "schema_version":
            "knowledge_retrieval_intake_validation_result_v1",

        "version":
            KNOWLEDGE_RETRIEVAL_VERSION,

        "phase":
            KNOWLEDGE_RETRIEVAL_PHASE,

        "patch":
            "4.6.20C",

        "status":
            "KNOWLEDGE_RETRIEVAL_INTAKE_VALIDATED",

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
                dict(store_metadata)
            ),

        "stored_semantic_article_profile":
            deepcopy(
                dict(stored_profile)
            ),

        "certified_semantic_article_profile":
            deepcopy(
                dict(certified_profile)
            ),

        "intake_validation":
            intake_validation,

        "knowledge_retrieval_architecture":
            deepcopy(
                dict(architecture)
            ),

        "source_input_inspection_result":
            deepcopy(
                dict(inspection_result)
            ),

        "processing_boundaries": {
            "certified_profile_store_input_inspection_preserved":
                True,

            "knowledge_retrieval_architecture_preserved":
                True,

            "retrieval_intake_validation_performed":
                True,

            "canonical_identity_preserved":
                True,

            "storage_identity_preserved":
                True,

            "store_metadata_preserved":
                True,

            "stored_profile_preserved":
                True,

            "certified_profile_preserved":
                True,

            "retrieval_query_created":
                False,

            "stored_profile_lookup_performed":
                False,

            "knowledge_retrieval_performed":
                False,

            "retrieval_payload_assembled":
                False,

            "retrieval_integrity_verification_performed":
                False,

            "retrieval_projection_performed":
                False,

            "retrieval_metadata_provenance_built":
                False,

            "final_knowledge_retrieval_result_built":
                False,

            "full_knowledge_retrieval_certification_performed":
                False,

            "profile_payload_modified":
                False,

            "semantic_state_modified":
                False,

            "semantic_meaning_rewritten":
                False,

            "cross_document_reasoning_performed":
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
        },

        "retrieval_policy":
            "VALIDATION_ONLY_NO_LOOKUP",

        "next_stage":
            "retrieval_identity_query_contract",
    }


# =====================================================================
# PATCH 4.6.20D ? Retrieval Identity / Query Contract
# =====================================================================

def build_knowledge_retrieval_query_contract_v1(
    intake_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Build the deterministic Knowledge Retrieval identity/query contract.

    D does not perform a store lookup.
    It defines exactly what E is allowed to retrieve.
    """

    from collections.abc import Mapping
    from copy import deepcopy
    import hashlib
    import json

    if not isinstance(
        intake_result,
        Mapping,
    ):
        raise KnowledgeRetrievalError(
            "intake_result must be a mapping."
        )

    # -------------------------------------------------------------
    # Exact 4.6.20C lifecycle
    # -------------------------------------------------------------

    for field, expected in (
        (
            "schema_version",
            "knowledge_retrieval_intake_validation_result_v1",
        ),
        (
            "version",
            KNOWLEDGE_RETRIEVAL_VERSION,
        ),
        (
            "phase",
            KNOWLEDGE_RETRIEVAL_PHASE,
        ),
        (
            "patch",
            "4.6.20C",
        ),
        (
            "status",
            "KNOWLEDGE_RETRIEVAL_INTAKE_VALIDATED",
        ),
        (
            "retrieval_policy",
            "VALIDATION_ONLY_NO_LOOKUP",
        ),
        (
            "next_stage",
            "retrieval_identity_query_contract",
        ),
    ):

        if intake_result.get(field) != expected:
            raise KnowledgeRetrievalError(
                f"Invalid 4.6.20C lifecycle field: {field}"
            )

    validation = intake_result.get(
        "intake_validation"
    )

    canonical_identity = intake_result.get(
        "canonical_article_identity"
    )

    storage_identity = intake_result.get(
        "storage_identity"
    )

    store_metadata = intake_result.get(
        "store_metadata"
    )

    stored_profile = intake_result.get(
        "stored_semantic_article_profile"
    )

    certified_profile = intake_result.get(
        "certified_semantic_article_profile"
    )

    architecture = intake_result.get(
        "knowledge_retrieval_architecture"
    )

    boundaries = intake_result.get(
        "processing_boundaries"
    )

    for name, value in (
        ("intake_validation", validation),
        ("canonical_article_identity", canonical_identity),
        ("storage_identity", storage_identity),
        ("store_metadata", store_metadata),
        ("stored_semantic_article_profile", stored_profile),
        ("certified_semantic_article_profile", certified_profile),
        ("knowledge_retrieval_architecture", architecture),
        ("processing_boundaries", boundaries),
    ):

        if not isinstance(
            value,
            Mapping,
        ):
            raise KnowledgeRetrievalError(
                name + " is missing."
            )

    # -------------------------------------------------------------
    # C validation authority
    # -------------------------------------------------------------

    if validation.get(
        "validation_status"
    ) != "VALIDATED":
        raise KnowledgeRetrievalError(
            "Retrieval intake is not VALIDATED."
        )

    if validation.get(
        "validation_scope"
    ) != "CERTIFIED_KNOWLEDGE_RETRIEVAL_INTAKE":
        raise KnowledgeRetrievalError(
            "Retrieval intake validation scope drifted."
        )

    for field in (
        "canonical_identity_validated",
        "storage_identity_validated",
        "store_metadata_validated",
        "stored_profile_validated",
        "certified_profile_validated",
        "profile_store_certification_preserved",
        "profile_payload_immutability_preserved",
        "knowledge_retrieval_owner_validated",
        "profile_store_owner_preserved",
        "semantic_memory_owner_preserved",
        "cross_document_reasoning_deferred",
        "semantic_memory_deferred",
    ):

        if validation.get(field) is not True:
            raise KnowledgeRetrievalError(
                f"Required C validation field is not True: {field}"
            )

    for field in (
        "knowledge_retrieval_performed",
        "stored_profile_lookup_performed",
    ):

        if validation.get(field) is not False:
            raise KnowledgeRetrievalError(
                f"Forbidden C validation field is not False: {field}"
            )

    # -------------------------------------------------------------
    # Architecture authority
    # -------------------------------------------------------------

    if architecture.get(
        "architecture_status"
    ) != "DEFINED":
        raise KnowledgeRetrievalError(
            "Knowledge Retrieval architecture is not defined."
        )

    identity_contract = architecture.get(
        "identity_contract"
    )

    execution_contract = architecture.get(
        "execution_contract"
    )

    if not isinstance(
        identity_contract,
        Mapping,
    ):
        raise KnowledgeRetrievalError(
            "Identity contract is missing."
        )

    if not isinstance(
        execution_contract,
        Mapping,
    ):
        raise KnowledgeRetrievalError(
            "Execution contract is missing."
        )

    if execution_contract.get(
        "4.6.20D"
    ) != "QUERY_CONTRACT_ONLY":
        raise KnowledgeRetrievalError(
            "4.6.20D execution contract drifted."
        )

    if identity_contract.get(
        "primary_lookup_key"
    ) != "storage_key":
        raise KnowledgeRetrievalError(
            "Primary lookup key contract drifted."
        )

    if identity_contract.get(
        "secondary_lookup_identity"
    ) != "canonical_article_identity":
        raise KnowledgeRetrievalError(
            "Secondary lookup identity contract drifted."
        )

    for field in (
        "workspace_scoped",
        "article_scoped",
        "version_aware",
        "payload_hash_bound",
    ):

        if identity_contract.get(field) is not True:
            raise KnowledgeRetrievalError(
                f"Required identity contract field is not True: {field}"
            )

    # -------------------------------------------------------------
    # Canonical retrieval identity
    # -------------------------------------------------------------

    workspace_id = canonical_identity.get(
        "workspace_id"
    )

    article_id = canonical_identity.get(
        "article_id"
    )

    storage_key = storage_identity.get(
        "storage_key"
    )

    if not isinstance(
        workspace_id,
        str,
    ) or not workspace_id:
        raise KnowledgeRetrievalError(
            "workspace_id must be a non-empty string."
        )

    if not isinstance(
        article_id,
        str,
    ) or not article_id:
        raise KnowledgeRetrievalError(
            "article_id must be a non-empty string."
        )

    if not isinstance(
        storage_key,
        str,
    ) or not storage_key:
        raise KnowledgeRetrievalError(
            "storage_key must be a non-empty string."
        )

    if storage_identity.get(
        "workspace_id"
    ) != workspace_id:
        raise KnowledgeRetrievalError(
            "Storage identity workspace drifted."
        )

    if storage_identity.get(
        "article_id"
    ) != article_id:
        raise KnowledgeRetrievalError(
            "Storage identity article drifted."
        )

    if store_metadata.get(
        "storage_key"
    ) != storage_key:
        raise KnowledgeRetrievalError(
            "Store metadata storage key drifted."
        )

    if stored_profile.get(
        "storage_key"
    ) != storage_key:
        raise KnowledgeRetrievalError(
            "Stored profile storage key drifted."
        )

    if stored_profile.get(
        "certified_profile_payload"
    ) != certified_profile:
        raise KnowledgeRetrievalError(
            "Stored profile payload drifted."
        )

    # -------------------------------------------------------------
    # Version / hash binding
    # -------------------------------------------------------------

    store_record_version = store_metadata.get(
        "store_record_version",
        1,
    )

    profile_payload_hash = store_metadata.get(
        "profile_payload_hash"
    )

    profile_payload_byte_length = store_metadata.get(
        "profile_payload_byte_length"
    )

    # Compact fixtures from earlier stages may omit these metadata fields.
    # D binds to them when supplied, without inventing replacements.
    if store_record_version is not None:
        if not isinstance(
            store_record_version,
            int,
        ) or store_record_version < 1:
            raise KnowledgeRetrievalError(
                "store_record_version must be a positive integer."
            )

    if profile_payload_hash is not None:
        if (
            not isinstance(
                profile_payload_hash,
                str,
            )
            or len(profile_payload_hash) != 64
            or any(
                ch not in "0123456789abcdef"
                for ch in profile_payload_hash
            )
        ):
            raise KnowledgeRetrievalError(
                "profile_payload_hash must be lowercase SHA256 hex."
            )

    if profile_payload_byte_length is not None:
        if (
            not isinstance(
                profile_payload_byte_length,
                int,
            )
            or profile_payload_byte_length < 1
        ):
            raise KnowledgeRetrievalError(
                "profile_payload_byte_length must be positive."
            )

    # -------------------------------------------------------------
    # C processing-boundary authority
    # -------------------------------------------------------------

    for field in (
        "certified_profile_store_input_inspection_preserved",
        "knowledge_retrieval_architecture_preserved",
        "retrieval_intake_validation_performed",
        "canonical_identity_preserved",
        "storage_identity_preserved",
        "store_metadata_preserved",
        "stored_profile_preserved",
        "certified_profile_preserved",
    ):

        if boundaries.get(field) is not True:
            raise KnowledgeRetrievalError(
                f"Required 4.6.20C boundary is not True: {field}"
            )

    for field in (
        "retrieval_query_created",
        "stored_profile_lookup_performed",
        "knowledge_retrieval_performed",
        "retrieval_payload_assembled",
        "retrieval_integrity_verification_performed",
        "retrieval_projection_performed",
        "retrieval_metadata_provenance_built",
        "final_knowledge_retrieval_result_built",
        "full_knowledge_retrieval_certification_performed",
        "profile_payload_modified",
        "semantic_state_modified",
        "semantic_meaning_rewritten",
        "cross_document_reasoning_performed",
        "new_reasoning_performed",
        "new_fact_inference_performed",
        "new_relation_inference_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if boundaries.get(field) is not False:
            raise KnowledgeRetrievalError(
                f"Forbidden 4.6.20C boundary is not False: {field}"
            )

    # -------------------------------------------------------------
    # Deterministic retrieval query identity
    # -------------------------------------------------------------

    query_identity_material = {
        "knowledge_retrieval_version":
            KNOWLEDGE_RETRIEVAL_VERSION,

        "workspace_id":
            workspace_id,

        "article_id":
            article_id,

        "storage_key":
            storage_key,

        "store_record_version":
            store_record_version,

        "profile_payload_hash":
            profile_payload_hash,
    }

    query_identity_json = json.dumps(
        query_identity_material,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    query_digest = hashlib.sha256(
        query_identity_json.encode("utf-8")
    ).hexdigest()

    retrieval_query_id = (
        "krq:v1:"
        + query_digest[:32]
    )

    retrieval_query = {
        "query_schema":
            "knowledge_retrieval_query_v1",

        "query_version":
            "v1",

        "retrieval_query_id":
            retrieval_query_id,

        "query_digest_algorithm":
            "SHA256",

        "query_digest":
            query_digest,

        "query_material_canonicalization":
            "JSON_SORTED_KEYS_COMPACT_UTF8",

        "query_mode":
            "CERTIFIED_PROFILE_LOOKUP",

        "lookup_strategy":
            "STORAGE_KEY_PRIMARY_CANONICAL_IDENTITY_SECONDARY",

        "primary_lookup_key":
            storage_key,

        "canonical_article_identity":
            deepcopy(
                dict(canonical_identity)
            ),

        "workspace_id":
            workspace_id,

        "article_id":
            article_id,

        "store_record_version":
            store_record_version,

        "profile_payload_hash":
            profile_payload_hash,

        "profile_payload_byte_length":
            profile_payload_byte_length,

        "require_certified_profile":
            True,

        "require_persisted_profile":
            True,

        "require_integrity_verified_profile":
            True,

        "require_immutable_profile":
            True,

        "require_exact_identity_match":
            True,

        "require_exact_storage_key_match":
            True,

        "require_version_match":
            True,

        "require_hash_match":
            profile_payload_hash is not None,

        "full_profile_requested":
            True,

        "requested_sections":
            [],

        "projection_requested":
            False,

        "read_only":
            True,

        "lookup_performed":
            False,

        "semantic_memory_accessed":
            False,

        "cross_document_reasoning_performed":
            False,

        "linking_decisions_performed":
            False,
    }

    query_contract = {
        "contract_status":
            "DEFINED",

        "contract_scope":
            "CERTIFIED_STORED_PROFILE_LOOKUP_QUERY",

        "source_validation_patch":
            "4.6.20C",

        "query_patch":
            "4.6.20D",

        "deterministic_query_identity":
            True,

        "storage_key_bound":
            True,

        "canonical_identity_bound":
            True,

        "workspace_bound":
            True,

        "article_bound":
            True,

        "version_aware":
            True,

        "payload_hash_bound":
            profile_payload_hash is not None,

        "read_only":
            True,

        "query_created":
            True,

        "lookup_performed":
            False,

        "knowledge_retrieval_performed":
            False,
    }

    return {
        "schema_version":
            "knowledge_retrieval_query_contract_result_v1",

        "version":
            KNOWLEDGE_RETRIEVAL_VERSION,

        "phase":
            KNOWLEDGE_RETRIEVAL_PHASE,

        "patch":
            "4.6.20D",

        "status":
            "KNOWLEDGE_RETRIEVAL_QUERY_CONTRACT_DEFINED",

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
                dict(store_metadata)
            ),

        "stored_semantic_article_profile":
            deepcopy(
                dict(stored_profile)
            ),

        "certified_semantic_article_profile":
            deepcopy(
                dict(certified_profile)
            ),

        "retrieval_query":
            retrieval_query,

        "query_contract":
            query_contract,

        "source_intake_validation_result":
            deepcopy(
                dict(intake_result)
            ),

        "processing_boundaries": {
            "retrieval_intake_validation_preserved":
                True,

            "retrieval_identity_query_contract_built":
                True,

            "canonical_identity_preserved":
                True,

            "storage_identity_preserved":
                True,

            "store_metadata_preserved":
                True,

            "stored_profile_preserved":
                True,

            "certified_profile_preserved":
                True,

            "retrieval_query_created":
                True,

            "stored_profile_lookup_performed":
                False,

            "knowledge_retrieval_performed":
                False,

            "retrieval_payload_assembled":
                False,

            "retrieval_integrity_verification_performed":
                False,

            "retrieval_projection_performed":
                False,

            "retrieval_metadata_provenance_built":
                False,

            "final_knowledge_retrieval_result_built":
                False,

            "full_knowledge_retrieval_certification_performed":
                False,

            "profile_payload_modified":
                False,

            "semantic_state_modified":
                False,

            "semantic_meaning_rewritten":
                False,

            "cross_document_reasoning_performed":
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
        },

        "retrieval_policy":
            "QUERY_CONTRACT_DEFINED_NO_LOOKUP",

        "next_stage":
            "stored_profile_lookup",
    }


# =====================================================================
# PATCH 4.6.20E ? Stored Profile Lookup
# =====================================================================

class InMemoryKnowledgeRetrievalStoreAdapter:
    """
    Read-oriented adapter used by Knowledge Retrieval tests/runtime.

    Records are supplied externally.
    Knowledge Retrieval itself performs no Profile Store write.
    """

    def __init__(
        self,
        records: dict[str, dict[str, Any]] | None = None,
    ) -> None:
        from copy import deepcopy

        self._records: dict[str, dict[str, Any]] = {}

        if records is not None:
            if not isinstance(records, dict):
                raise KnowledgeRetrievalError(
                    "records must be a dictionary."
                )

            for key, value in records.items():
                if not isinstance(key, str) or not key:
                    raise KnowledgeRetrievalError(
                        "Adapter record key must be a non-empty string."
                    )

                if not isinstance(value, dict):
                    raise KnowledgeRetrievalError(
                        "Adapter record must be a dictionary."
                    )

                self._records[key] = deepcopy(value)

    def read(
        self,
        storage_key: str,
    ) -> dict[str, Any] | None:
        from copy import deepcopy

        if not isinstance(
            storage_key,
            str,
        ) or not storage_key:
            raise KnowledgeRetrievalError(
                "storage_key must be a non-empty string."
            )

        record = self._records.get(
            storage_key
        )

        if record is None:
            return None

        return deepcopy(record)

    def record_count(self) -> int:
        return len(self._records)


def lookup_stored_semantic_article_profile_v1(
    query_result: dict[str, Any],
    store_adapter: Any,
) -> dict[str, Any]:
    """
    Perform the certified stored-profile lookup.

    This is the first 4.6.20 stage allowed to execute a store read.

    The lookup is:
    - read-only,
    - storage-key bound,
    - canonical-identity bound,
    - version aware,
    - payload-hash bound.
    """

    from collections.abc import Mapping
    from copy import deepcopy
    import hashlib
    import json

    if not isinstance(
        query_result,
        Mapping,
    ):
        raise KnowledgeRetrievalError(
            "query_result must be a mapping."
        )

    if not hasattr(
        store_adapter,
        "read",
    ) or not callable(
        store_adapter.read
    ):
        raise KnowledgeRetrievalError(
            "store_adapter must provide callable read()."
        )

    # -------------------------------------------------------------
    # Exact 4.6.20D lifecycle
    # -------------------------------------------------------------

    for field, expected in (
        (
            "schema_version",
            "knowledge_retrieval_query_contract_result_v1",
        ),
        (
            "version",
            KNOWLEDGE_RETRIEVAL_VERSION,
        ),
        (
            "phase",
            KNOWLEDGE_RETRIEVAL_PHASE,
        ),
        (
            "patch",
            "4.6.20D",
        ),
        (
            "status",
            "KNOWLEDGE_RETRIEVAL_QUERY_CONTRACT_DEFINED",
        ),
        (
            "retrieval_policy",
            "QUERY_CONTRACT_DEFINED_NO_LOOKUP",
        ),
        (
            "next_stage",
            "stored_profile_lookup",
        ),
    ):

        if query_result.get(field) != expected:
            raise KnowledgeRetrievalError(
                f"Invalid 4.6.20D lifecycle field: {field}"
            )

    query = query_result.get(
        "retrieval_query"
    )

    query_contract = query_result.get(
        "query_contract"
    )

    canonical_identity = query_result.get(
        "canonical_article_identity"
    )

    storage_identity = query_result.get(
        "storage_identity"
    )

    store_metadata = query_result.get(
        "store_metadata"
    )

    certified_profile = query_result.get(
        "certified_semantic_article_profile"
    )

    source_stored_profile = query_result.get(
        "stored_semantic_article_profile"
    )

    boundaries = query_result.get(
        "processing_boundaries"
    )

    for name, value in (
        ("retrieval_query", query),
        ("query_contract", query_contract),
        ("canonical_article_identity", canonical_identity),
        ("storage_identity", storage_identity),
        ("store_metadata", store_metadata),
        ("certified_semantic_article_profile", certified_profile),
        ("stored_semantic_article_profile", source_stored_profile),
        ("processing_boundaries", boundaries),
    ):

        if not isinstance(
            value,
            Mapping,
        ):
            raise KnowledgeRetrievalError(
                name + " is missing."
            )

    # -------------------------------------------------------------
    # D query authority
    # -------------------------------------------------------------

    for field, expected in (
        (
            "query_schema",
            "knowledge_retrieval_query_v1",
        ),
        (
            "query_version",
            "v1",
        ),
        (
            "query_mode",
            "CERTIFIED_PROFILE_LOOKUP",
        ),
        (
            "lookup_strategy",
            "STORAGE_KEY_PRIMARY_CANONICAL_IDENTITY_SECONDARY",
        ),
    ):

        if query.get(field) != expected:
            raise KnowledgeRetrievalError(
                f"Retrieval query field drifted: {field}"
            )

    for field in (
        "require_certified_profile",
        "require_persisted_profile",
        "require_integrity_verified_profile",
        "require_immutable_profile",
        "require_exact_identity_match",
        "require_exact_storage_key_match",
        "require_version_match",
        "full_profile_requested",
        "read_only",
    ):

        if query.get(field) is not True:
            raise KnowledgeRetrievalError(
                f"Required query field is not True: {field}"
            )

    for field in (
        "projection_requested",
        "lookup_performed",
        "semantic_memory_accessed",
        "cross_document_reasoning_performed",
        "linking_decisions_performed",
    ):

        if query.get(field) is not False:
            raise KnowledgeRetrievalError(
                f"Forbidden query field is not False: {field}"
            )

    if query.get(
        "requested_sections"
    ) != []:
        raise KnowledgeRetrievalError(
            "4.6.20E expects full-profile lookup with no projection."
        )

    # -------------------------------------------------------------
    # Query contract authority
    # -------------------------------------------------------------

    if query_contract.get(
        "contract_status"
    ) != "DEFINED":
        raise KnowledgeRetrievalError(
            "Query contract is not DEFINED."
        )

    if query_contract.get(
        "contract_scope"
    ) != "CERTIFIED_STORED_PROFILE_LOOKUP_QUERY":
        raise KnowledgeRetrievalError(
            "Query contract scope drifted."
        )

    for field in (
        "deterministic_query_identity",
        "storage_key_bound",
        "canonical_identity_bound",
        "workspace_bound",
        "article_bound",
        "version_aware",
        "read_only",
        "query_created",
    ):

        if query_contract.get(field) is not True:
            raise KnowledgeRetrievalError(
                f"Required query contract field is not True: {field}"
            )

    for field in (
        "lookup_performed",
        "knowledge_retrieval_performed",
    ):

        if query_contract.get(field) is not False:
            raise KnowledgeRetrievalError(
                f"Forbidden query contract field is not False: {field}"
            )

    # -------------------------------------------------------------
    # Identity authority
    # -------------------------------------------------------------

    workspace_id = canonical_identity.get(
        "workspace_id"
    )

    article_id = canonical_identity.get(
        "article_id"
    )

    storage_key = storage_identity.get(
        "storage_key"
    )

    if query.get(
        "primary_lookup_key"
    ) != storage_key:
        raise KnowledgeRetrievalError(
            "Query storage key drifted."
        )

    if query.get(
        "canonical_article_identity"
    ) != canonical_identity:
        raise KnowledgeRetrievalError(
            "Query canonical identity drifted."
        )

    if query.get(
        "workspace_id"
    ) != workspace_id:
        raise KnowledgeRetrievalError(
            "Query workspace identity drifted."
        )

    if query.get(
        "article_id"
    ) != article_id:
        raise KnowledgeRetrievalError(
            "Query article identity drifted."
        )

    if store_metadata.get(
        "storage_key"
    ) != storage_key:
        raise KnowledgeRetrievalError(
            "Store metadata storage key drifted."
        )

    if source_stored_profile.get(
        "storage_key"
    ) != storage_key:
        raise KnowledgeRetrievalError(
            "Source stored-profile storage key drifted."
        )

    # -------------------------------------------------------------
    # D processing-boundary authority
    # -------------------------------------------------------------

    for field in (
        "retrieval_intake_validation_preserved",
        "retrieval_identity_query_contract_built",
        "canonical_identity_preserved",
        "storage_identity_preserved",
        "store_metadata_preserved",
        "stored_profile_preserved",
        "certified_profile_preserved",
        "retrieval_query_created",
    ):

        if boundaries.get(field) is not True:
            raise KnowledgeRetrievalError(
                f"Required 4.6.20D boundary is not True: {field}"
            )

    for field in (
        "stored_profile_lookup_performed",
        "knowledge_retrieval_performed",
        "retrieval_payload_assembled",
        "retrieval_integrity_verification_performed",
        "retrieval_projection_performed",
        "retrieval_metadata_provenance_built",
        "final_knowledge_retrieval_result_built",
        "full_knowledge_retrieval_certification_performed",
        "profile_payload_modified",
        "semantic_state_modified",
        "semantic_meaning_rewritten",
        "cross_document_reasoning_performed",
        "new_reasoning_performed",
        "new_fact_inference_performed",
        "new_relation_inference_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if boundaries.get(field) is not False:
            raise KnowledgeRetrievalError(
                f"Forbidden 4.6.20D boundary is not False: {field}"
            )

    # -------------------------------------------------------------
    # Actual read
    # -------------------------------------------------------------

    retrieved_record = store_adapter.read(
        storage_key
    )

    if retrieved_record is None:
        raise KnowledgeRetrievalError(
            "Stored profile was not found."
        )

    if not isinstance(
        retrieved_record,
        Mapping,
    ):
        raise KnowledgeRetrievalError(
            "Retrieved stored profile must be a mapping."
        )

    # -------------------------------------------------------------
    # Retrieved-record validation
    # -------------------------------------------------------------

    if retrieved_record.get(
        "stored_profile_schema"
    ) != "stored_semantic_article_profile_v1":
        raise KnowledgeRetrievalError(
            "Retrieved stored profile schema drifted."
        )

    if retrieved_record.get(
        "store_status"
    ) != "PERSISTED":
        raise KnowledgeRetrievalError(
            "Retrieved profile is not persisted."
        )

    if retrieved_record.get(
        "storage_key"
    ) != storage_key:
        raise KnowledgeRetrievalError(
            "Retrieved storage key drifted."
        )

    retrieved_payload = retrieved_record.get(
        "certified_profile_payload"
    )

    if not isinstance(
        retrieved_payload,
        Mapping,
    ):
        raise KnowledgeRetrievalError(
            "Retrieved certified profile payload is missing."
        )

    if retrieved_payload != certified_profile:
        raise KnowledgeRetrievalError(
            "Retrieved certified profile payload drifted."
        )

    if retrieved_payload.get(
        "profile_identity",
        {},
    ).get(
        "canonical_article_identity"
    ) != canonical_identity:
        raise KnowledgeRetrievalError(
            "Retrieved canonical article identity drifted."
        )

    if retrieved_payload.get(
        "profile_certified"
    ) is not True:
        raise KnowledgeRetrievalError(
            "Retrieved profile is not certified."
        )

    if retrieved_payload.get(
        "profile_persisted"
    ) is not False:
        raise KnowledgeRetrievalError(
            "Retrieved immutable source profile flag drifted."
        )

    # -------------------------------------------------------------
    # Optional cryptographic / version binding
    # -------------------------------------------------------------

    payload_json = json.dumps(
        dict(retrieved_payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    actual_hash = hashlib.sha256(
        payload_json.encode("utf-8")
    ).hexdigest()

    actual_bytes = len(
        payload_json.encode("utf-8")
    )

    expected_hash = query.get(
        "profile_payload_hash"
    )

    expected_bytes = query.get(
        "profile_payload_byte_length"
    )

    expected_version = query.get(
        "store_record_version"
    )

    if expected_hash is not None:
        if actual_hash != expected_hash:
            raise KnowledgeRetrievalError(
                "Retrieved profile payload hash drifted."
            )

        if retrieved_record.get(
            "profile_payload_hash"
        ) not in (
            None,
            expected_hash,
        ):
            raise KnowledgeRetrievalError(
                "Retrieved stored-profile hash metadata drifted."
            )

    if expected_bytes is not None:
        if actual_bytes != expected_bytes:
            raise KnowledgeRetrievalError(
                "Retrieved profile payload byte length drifted."
            )

        if retrieved_record.get(
            "profile_payload_byte_length"
        ) not in (
            None,
            expected_bytes,
        ):
            raise KnowledgeRetrievalError(
                "Retrieved stored-profile byte-length metadata drifted."
            )

    if expected_version is not None:
        retrieved_version = retrieved_record.get(
            "store_record_version"
        )

        if retrieved_version not in (
            None,
            expected_version,
        ):
            raise KnowledgeRetrievalError(
                "Retrieved stored-profile version drifted."
            )

    lookup_receipt = {
        "lookup_status":
            "FOUND",

        "lookup_scope":
            "CERTIFIED_STORED_SEMANTIC_ARTICLE_PROFILE",

        "lookup_patch":
            "4.6.20E",

        "retrieval_query_id":
            query[
                "retrieval_query_id"
            ],

        "storage_key":
            storage_key,

        "workspace_id":
            workspace_id,

        "article_id":
            article_id,

        "store_record_version":
            expected_version,

        "profile_payload_hash":
            actual_hash,

        "profile_payload_byte_length":
            actual_bytes,

        "lookup_strategy":
            query[
                "lookup_strategy"
            ],

        "store_read_performed":
            True,

        "record_found":
            True,

        "exact_storage_key_match":
            True,

        "exact_canonical_identity_match":
            True,

        "exact_profile_payload_match":
            True,

        "payload_hash_match":
            (
                expected_hash is None
                or actual_hash == expected_hash
            ),

        "payload_byte_length_match":
            (
                expected_bytes is None
                or actual_bytes == expected_bytes
            ),

        "read_only":
            True,

        "store_write_performed":
            False,

        "source_profile_modified":
            False,

        "semantic_memory_accessed":
            False,

        "cross_document_reasoning_performed":
            False,

        "linking_decisions_performed":
            False,
    }

    return {
        "schema_version":
            "knowledge_retrieval_stored_profile_lookup_result_v1",

        "version":
            KNOWLEDGE_RETRIEVAL_VERSION,

        "phase":
            KNOWLEDGE_RETRIEVAL_PHASE,

        "patch":
            "4.6.20E",

        "status":
            "STORED_SEMANTIC_ARTICLE_PROFILE_RETRIEVED",

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
                dict(store_metadata)
            ),

        "retrieval_query":
            deepcopy(
                dict(query)
            ),

        "lookup_receipt":
            lookup_receipt,

        "retrieved_stored_semantic_article_profile":
            deepcopy(
                dict(retrieved_record)
            ),

        "retrieved_certified_semantic_article_profile":
            deepcopy(
                dict(retrieved_payload)
            ),

        "source_query_contract_result":
            deepcopy(
                dict(query_result)
            ),

        "processing_boundaries": {
            "retrieval_query_contract_preserved":
                True,

            "canonical_identity_preserved":
                True,

            "storage_identity_preserved":
                True,

            "store_metadata_preserved":
                True,

            "retrieval_query_preserved":
                True,

            "stored_profile_lookup_performed":
                True,

            "knowledge_retrieval_performed":
                True,

            "retrieved_profile_exact_match_verified":
                True,

            "store_read_performed":
                True,

            "store_write_performed":
                False,

            "retrieval_payload_assembled":
                False,

            "retrieval_integrity_verification_performed":
                False,

            "retrieval_projection_performed":
                False,

            "retrieval_metadata_provenance_built":
                False,

            "final_knowledge_retrieval_result_built":
                False,

            "full_knowledge_retrieval_certification_performed":
                False,

            "profile_payload_modified":
                False,

            "semantic_state_modified":
                False,

            "semantic_meaning_rewritten":
                False,

            "cross_document_reasoning_performed":
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
        },

        "retrieval_policy":
            "READ_ONLY_CERTIFIED_PROFILE_LOOKUP_COMPLETED",

        "next_stage":
            "retrieval_payload_assembly",
    }


# =====================================================================
# PATCH 4.6.20F ? Retrieval Payload Assembly
# =====================================================================

def assemble_knowledge_retrieval_payload_v1(
    lookup_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Assemble the canonical read-only Knowledge Retrieval payload.

    F does not:
    - perform another store read,
    - perform a store write,
    - project/filter profile sections,
    - mutate semantic state,
    - perform cross-document reasoning,
    - write Semantic Memory,
    - make linking decisions.
    """

    from collections.abc import Mapping
    from copy import deepcopy
    import hashlib
    import json

    if not isinstance(
        lookup_result,
        Mapping,
    ):
        raise KnowledgeRetrievalError(
            "lookup_result must be a mapping."
        )

    # -------------------------------------------------------------
    # Exact 4.6.20E lifecycle
    # -------------------------------------------------------------

    for field, expected in (
        (
            "schema_version",
            "knowledge_retrieval_stored_profile_lookup_result_v1",
        ),
        (
            "version",
            KNOWLEDGE_RETRIEVAL_VERSION,
        ),
        (
            "phase",
            KNOWLEDGE_RETRIEVAL_PHASE,
        ),
        (
            "patch",
            "4.6.20E",
        ),
        (
            "status",
            "STORED_SEMANTIC_ARTICLE_PROFILE_RETRIEVED",
        ),
        (
            "retrieval_policy",
            "READ_ONLY_CERTIFIED_PROFILE_LOOKUP_COMPLETED",
        ),
        (
            "next_stage",
            "retrieval_payload_assembly",
        ),
    ):

        if lookup_result.get(field) != expected:
            raise KnowledgeRetrievalError(
                f"Invalid 4.6.20E lifecycle field: {field}"
            )

    canonical_identity = lookup_result.get(
        "canonical_article_identity"
    )

    storage_identity = lookup_result.get(
        "storage_identity"
    )

    store_metadata = lookup_result.get(
        "store_metadata"
    )

    retrieval_query = lookup_result.get(
        "retrieval_query"
    )

    lookup_receipt = lookup_result.get(
        "lookup_receipt"
    )

    retrieved_stored_profile = lookup_result.get(
        "retrieved_stored_semantic_article_profile"
    )

    retrieved_profile = lookup_result.get(
        "retrieved_certified_semantic_article_profile"
    )

    boundaries = lookup_result.get(
        "processing_boundaries"
    )

    for name, value in (
        ("canonical_article_identity", canonical_identity),
        ("storage_identity", storage_identity),
        ("store_metadata", store_metadata),
        ("retrieval_query", retrieval_query),
        ("lookup_receipt", lookup_receipt),
        (
            "retrieved_stored_semantic_article_profile",
            retrieved_stored_profile,
        ),
        (
            "retrieved_certified_semantic_article_profile",
            retrieved_profile,
        ),
        ("processing_boundaries", boundaries),
    ):

        if not isinstance(value, Mapping):
            raise KnowledgeRetrievalError(
                name + " is missing."
            )

    # -------------------------------------------------------------
    # E lookup authority
    # -------------------------------------------------------------

    if lookup_receipt.get(
        "lookup_status"
    ) != "FOUND":
        raise KnowledgeRetrievalError(
            "Stored profile lookup did not return FOUND."
        )

    if lookup_receipt.get(
        "lookup_scope"
    ) != "CERTIFIED_STORED_SEMANTIC_ARTICLE_PROFILE":
        raise KnowledgeRetrievalError(
            "Lookup scope drifted."
        )

    if lookup_receipt.get(
        "lookup_patch"
    ) != "4.6.20E":
        raise KnowledgeRetrievalError(
            "Lookup receipt patch drifted."
        )

    for field in (
        "store_read_performed",
        "record_found",
        "exact_storage_key_match",
        "exact_canonical_identity_match",
        "exact_profile_payload_match",
        "payload_hash_match",
        "payload_byte_length_match",
        "read_only",
    ):

        if lookup_receipt.get(field) is not True:
            raise KnowledgeRetrievalError(
                f"Required lookup receipt field is not True: {field}"
            )

    for field in (
        "store_write_performed",
        "source_profile_modified",
        "semantic_memory_accessed",
        "cross_document_reasoning_performed",
        "linking_decisions_performed",
    ):

        if lookup_receipt.get(field) is not False:
            raise KnowledgeRetrievalError(
                f"Forbidden lookup receipt field is not False: {field}"
            )

    # -------------------------------------------------------------
    # Identity preservation
    # -------------------------------------------------------------

    storage_key = storage_identity.get(
        "storage_key"
    )

    if lookup_receipt.get(
        "storage_key"
    ) != storage_key:
        raise KnowledgeRetrievalError(
            "Lookup receipt storage key drifted."
        )

    if retrieval_query.get(
        "primary_lookup_key"
    ) != storage_key:
        raise KnowledgeRetrievalError(
            "Retrieval query storage key drifted."
        )

    if retrieval_query.get(
        "canonical_article_identity"
    ) != canonical_identity:
        raise KnowledgeRetrievalError(
            "Retrieval query canonical identity drifted."
        )

    if retrieved_stored_profile.get(
        "storage_key"
    ) != storage_key:
        raise KnowledgeRetrievalError(
            "Retrieved stored profile storage key drifted."
        )

    # -------------------------------------------------------------
    # Retrieved profile authority
    # -------------------------------------------------------------

    stored_payload = retrieved_stored_profile.get(
        "certified_profile_payload"
    )

    if stored_payload != retrieved_profile:
        raise KnowledgeRetrievalError(
            "Retrieved stored payload differs from retrieved profile."
        )

    if retrieved_profile.get(
        "profile_certified"
    ) is not True:
        raise KnowledgeRetrievalError(
            "Retrieved profile is not certified."
        )

    if retrieved_profile.get(
        "profile_store_ready"
    ) is not True:
        raise KnowledgeRetrievalError(
            "Retrieved profile is not store-ready."
        )

    if retrieved_profile.get(
        "profile_persisted"
    ) is not False:
        raise KnowledgeRetrievalError(
            "Immutable certified profile persistence flag drifted."
        )

    profile_identity = retrieved_profile.get(
        "profile_identity"
    )

    if not isinstance(
        profile_identity,
        Mapping,
    ):
        raise KnowledgeRetrievalError(
            "Retrieved profile identity is missing."
        )

    if profile_identity.get(
        "canonical_article_identity"
    ) != canonical_identity:
        raise KnowledgeRetrievalError(
            "Retrieved profile canonical identity drifted."
        )

    # -------------------------------------------------------------
    # Cryptographic assembly inputs
    # -------------------------------------------------------------

    payload_json = json.dumps(
        dict(retrieved_profile),
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

    if lookup_receipt.get(
        "profile_payload_hash"
    ) != payload_hash:
        raise KnowledgeRetrievalError(
            "Lookup receipt payload hash drifted."
        )

    if lookup_receipt.get(
        "profile_payload_byte_length"
    ) != payload_bytes:
        raise KnowledgeRetrievalError(
            "Lookup receipt payload byte length drifted."
        )

    query_hash = retrieval_query.get(
        "profile_payload_hash"
    )

    if query_hash is not None and query_hash != payload_hash:
        raise KnowledgeRetrievalError(
            "Retrieval query payload hash drifted."
        )

    query_bytes = retrieval_query.get(
        "profile_payload_byte_length"
    )

    if query_bytes is not None and query_bytes != payload_bytes:
        raise KnowledgeRetrievalError(
            "Retrieval query payload byte length drifted."
        )

    # -------------------------------------------------------------
    # E processing-boundary authority
    # -------------------------------------------------------------

    for field in (
        "retrieval_query_contract_preserved",
        "canonical_identity_preserved",
        "storage_identity_preserved",
        "store_metadata_preserved",
        "retrieval_query_preserved",
        "stored_profile_lookup_performed",
        "knowledge_retrieval_performed",
        "retrieved_profile_exact_match_verified",
        "store_read_performed",
    ):

        if boundaries.get(field) is not True:
            raise KnowledgeRetrievalError(
                f"Required 4.6.20E boundary is not True: {field}"
            )

    for field in (
        "store_write_performed",
        "retrieval_payload_assembled",
        "retrieval_integrity_verification_performed",
        "retrieval_projection_performed",
        "retrieval_metadata_provenance_built",
        "final_knowledge_retrieval_result_built",
        "full_knowledge_retrieval_certification_performed",
        "profile_payload_modified",
        "semantic_state_modified",
        "semantic_meaning_rewritten",
        "cross_document_reasoning_performed",
        "new_reasoning_performed",
        "new_fact_inference_performed",
        "new_relation_inference_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if boundaries.get(field) is not False:
            raise KnowledgeRetrievalError(
                f"Forbidden 4.6.20E boundary is not False: {field}"
            )

    # -------------------------------------------------------------
    # Deterministic retrieval payload identity
    # -------------------------------------------------------------

    retrieval_payload_identity_material = {
        "knowledge_retrieval_version":
            KNOWLEDGE_RETRIEVAL_VERSION,

        "retrieval_query_id":
            retrieval_query[
                "retrieval_query_id"
            ],

        "storage_key":
            storage_key,

        "workspace_id":
            canonical_identity[
                "workspace_id"
            ],

        "article_id":
            canonical_identity[
                "article_id"
            ],

        "profile_payload_hash":
            payload_hash,

        "profile_payload_byte_length":
            payload_bytes,
    }

    retrieval_payload_identity_json = json.dumps(
        retrieval_payload_identity_material,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    retrieval_payload_digest = hashlib.sha256(
        retrieval_payload_identity_json.encode("utf-8")
    ).hexdigest()

    retrieval_payload_id = (
        "krp:v1:"
        + retrieval_payload_digest[:32]
    )

    retrieval_payload = {
        "retrieval_payload_schema":
            "knowledge_retrieval_payload_v1",

        "retrieval_payload_version":
            "v1",

        "retrieval_payload_id":
            retrieval_payload_id,

        "retrieval_payload_digest":
            retrieval_payload_digest,

        "retrieval_payload_digest_algorithm":
            "SHA256",

        "retrieval_payload_identity_canonicalization":
            "JSON_SORTED_KEYS_COMPACT_UTF8",

        "retrieval_query_id":
            retrieval_query[
                "retrieval_query_id"
            ],

        "canonical_article_identity":
            deepcopy(
                dict(canonical_identity)
            ),

        "storage_key":
            storage_key,

        "store_record_version":
            lookup_receipt.get(
                "store_record_version"
            ),

        "profile_payload_hash":
            payload_hash,

        "profile_payload_hash_algorithm":
            "SHA256",

        "profile_payload_byte_length":
            payload_bytes,

        "certified_semantic_article_profile":
            deepcopy(
                dict(retrieved_profile)
            ),

        "payload_mode":
            "FULL_CERTIFIED_PROFILE",

        "projection_applied":
            False,

        "requested_sections":
            [],

        "read_only":
            True,

        "source_profile_immutable":
            True,

        "retrieval_integrity_verified":
            False,

        "retrieval_provenance_attached":
            False,

        "semantic_memory_written":
            False,

        "cross_document_reasoning_performed":
            False,

        "linking_decisions_performed":
            False,
    }

    assembly_receipt = {
        "assembly_status":
            "ASSEMBLED",

        "assembly_scope":
            "FULL_CERTIFIED_PROFILE_RETRIEVAL_PAYLOAD",

        "assembly_patch":
            "4.6.20F",

        "source_lookup_patch":
            "4.6.20E",

        "retrieval_payload_id":
            retrieval_payload_id,

        "source_lookup_verified":
            True,

        "source_profile_exactly_preserved":
            True,

        "canonical_identity_preserved":
            True,

        "storage_identity_preserved":
            True,

        "payload_hash_preserved":
            True,

        "payload_byte_length_preserved":
            True,

        "full_profile_assembled":
            True,

        "projection_applied":
            False,

        "additional_store_read_performed":
            False,

        "store_write_performed":
            False,

        "profile_payload_modified":
            False,

        "semantic_memory_written":
            False,

        "cross_document_reasoning_performed":
            False,

        "linking_decisions_performed":
            False,
    }

    return {
        "schema_version":
            "knowledge_retrieval_payload_assembly_result_v1",

        "version":
            KNOWLEDGE_RETRIEVAL_VERSION,

        "phase":
            KNOWLEDGE_RETRIEVAL_PHASE,

        "patch":
            "4.6.20F",

        "status":
            "KNOWLEDGE_RETRIEVAL_PAYLOAD_ASSEMBLED",

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
                dict(store_metadata)
            ),

        "retrieval_query":
            deepcopy(
                dict(retrieval_query)
            ),

        "lookup_receipt":
            deepcopy(
                dict(lookup_receipt)
            ),

        "retrieval_payload":
            retrieval_payload,

        "assembly_receipt":
            assembly_receipt,

        "source_lookup_result":
            deepcopy(
                dict(lookup_result)
            ),

        "processing_boundaries": {
            "stored_profile_lookup_preserved":
                True,

            "retrieval_query_preserved":
                True,

            "canonical_identity_preserved":
                True,

            "storage_identity_preserved":
                True,

            "store_metadata_preserved":
                True,

            "retrieved_profile_preserved":
                True,

            "knowledge_retrieval_performed":
                True,

            "retrieval_payload_assembled":
                True,

            "additional_store_read_performed":
                False,

            "store_write_performed":
                False,

            "retrieval_integrity_verification_performed":
                False,

            "retrieval_projection_performed":
                False,

            "retrieval_metadata_provenance_built":
                False,

            "final_knowledge_retrieval_result_built":
                False,

            "full_knowledge_retrieval_certification_performed":
                False,

            "profile_payload_modified":
                False,

            "semantic_state_modified":
                False,

            "semantic_meaning_rewritten":
                False,

            "cross_document_reasoning_performed":
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
        },

        "retrieval_policy":
            "FULL_CERTIFIED_PROFILE_PAYLOAD_ASSEMBLED",

        "next_stage":
            "retrieval_integrity_verification",
    }


# =====================================================================
# PATCH 4.6.20G ? Retrieval Integrity Verification
# =====================================================================

def verify_knowledge_retrieval_integrity_v1(
    payload_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Verify the structural and cryptographic integrity of the
    assembled Knowledge Retrieval payload.

    G performs verification only.
    """

    from collections.abc import Mapping
    from copy import deepcopy
    import hashlib
    import json

    if not isinstance(
        payload_result,
        Mapping,
    ):
        raise KnowledgeRetrievalError(
            "payload_result must be a mapping."
        )

    # -------------------------------------------------------------
    # Exact 4.6.20F lifecycle
    # -------------------------------------------------------------

    for field, expected in (
        (
            "schema_version",
            "knowledge_retrieval_payload_assembly_result_v1",
        ),
        (
            "version",
            KNOWLEDGE_RETRIEVAL_VERSION,
        ),
        (
            "phase",
            KNOWLEDGE_RETRIEVAL_PHASE,
        ),
        (
            "patch",
            "4.6.20F",
        ),
        (
            "status",
            "KNOWLEDGE_RETRIEVAL_PAYLOAD_ASSEMBLED",
        ),
        (
            "retrieval_policy",
            "FULL_CERTIFIED_PROFILE_PAYLOAD_ASSEMBLED",
        ),
        (
            "next_stage",
            "retrieval_integrity_verification",
        ),
    ):

        if payload_result.get(field) != expected:
            raise KnowledgeRetrievalError(
                f"Invalid 4.6.20F lifecycle field: {field}"
            )

    canonical_identity = payload_result.get(
        "canonical_article_identity"
    )

    storage_identity = payload_result.get(
        "storage_identity"
    )

    store_metadata = payload_result.get(
        "store_metadata"
    )

    retrieval_query = payload_result.get(
        "retrieval_query"
    )

    lookup_receipt = payload_result.get(
        "lookup_receipt"
    )

    retrieval_payload = payload_result.get(
        "retrieval_payload"
    )

    assembly_receipt = payload_result.get(
        "assembly_receipt"
    )

    boundaries = payload_result.get(
        "processing_boundaries"
    )

    for name, value in (
        ("canonical_article_identity", canonical_identity),
        ("storage_identity", storage_identity),
        ("store_metadata", store_metadata),
        ("retrieval_query", retrieval_query),
        ("lookup_receipt", lookup_receipt),
        ("retrieval_payload", retrieval_payload),
        ("assembly_receipt", assembly_receipt),
        ("processing_boundaries", boundaries),
    ):

        if not isinstance(
            value,
            Mapping,
        ):
            raise KnowledgeRetrievalError(
                name + " is missing."
            )

    # -------------------------------------------------------------
    # F payload authority
    # -------------------------------------------------------------

    for field, expected in (
        (
            "retrieval_payload_schema",
            "knowledge_retrieval_payload_v1",
        ),
        (
            "retrieval_payload_version",
            "v1",
        ),
        (
            "payload_mode",
            "FULL_CERTIFIED_PROFILE",
        ),
        (
            "profile_payload_hash_algorithm",
            "SHA256",
        ),
    ):

        if retrieval_payload.get(field) != expected:
            raise KnowledgeRetrievalError(
                f"Retrieval payload field drifted: {field}"
            )

    if retrieval_payload.get(
        "read_only"
    ) is not True:
        raise KnowledgeRetrievalError(
            "Retrieval payload is not read-only."
        )

    if retrieval_payload.get(
        "source_profile_immutable"
    ) is not True:
        raise KnowledgeRetrievalError(
            "Source profile immutability is not preserved."
        )

    for field in (
        "projection_applied",
        "retrieval_integrity_verified",
        "retrieval_provenance_attached",
        "semantic_memory_written",
        "cross_document_reasoning_performed",
        "linking_decisions_performed",
    ):

        if retrieval_payload.get(field) is not False:
            raise KnowledgeRetrievalError(
                f"Forbidden F payload field is not False: {field}"
            )

    # -------------------------------------------------------------
    # Assembly authority
    # -------------------------------------------------------------

    if assembly_receipt.get(
        "assembly_status"
    ) != "ASSEMBLED":
        raise KnowledgeRetrievalError(
            "Retrieval payload is not assembled."
        )

    if assembly_receipt.get(
        "assembly_scope"
    ) != "FULL_CERTIFIED_PROFILE_RETRIEVAL_PAYLOAD":
        raise KnowledgeRetrievalError(
            "Assembly scope drifted."
        )

    for field in (
        "source_lookup_verified",
        "source_profile_exactly_preserved",
        "canonical_identity_preserved",
        "storage_identity_preserved",
        "payload_hash_preserved",
        "payload_byte_length_preserved",
        "full_profile_assembled",
    ):

        if assembly_receipt.get(field) is not True:
            raise KnowledgeRetrievalError(
                f"Required assembly field is not True: {field}"
            )

    for field in (
        "projection_applied",
        "additional_store_read_performed",
        "store_write_performed",
        "profile_payload_modified",
        "semantic_memory_written",
        "cross_document_reasoning_performed",
        "linking_decisions_performed",
    ):

        if assembly_receipt.get(field) is not False:
            raise KnowledgeRetrievalError(
                f"Forbidden assembly field is not False: {field}"
            )

    # -------------------------------------------------------------
    # Identity verification
    # -------------------------------------------------------------

    storage_key = storage_identity.get(
        "storage_key"
    )

    if retrieval_payload.get(
        "storage_key"
    ) != storage_key:
        raise KnowledgeRetrievalError(
            "Retrieval payload storage key drifted."
        )

    if retrieval_payload.get(
        "canonical_article_identity"
    ) != canonical_identity:
        raise KnowledgeRetrievalError(
            "Retrieval payload canonical identity drifted."
        )

    if retrieval_payload.get(
        "retrieval_query_id"
    ) != retrieval_query.get(
        "retrieval_query_id"
    ):
        raise KnowledgeRetrievalError(
            "Retrieval query identity drifted."
        )

    if lookup_receipt.get(
        "storage_key"
    ) != storage_key:
        raise KnowledgeRetrievalError(
            "Lookup receipt storage key drifted."
        )

    # -------------------------------------------------------------
    # Profile integrity
    # -------------------------------------------------------------

    profile = retrieval_payload.get(
        "certified_semantic_article_profile"
    )

    if not isinstance(
        profile,
        Mapping,
    ):
        raise KnowledgeRetrievalError(
            "Certified retrieval profile is missing."
        )

    if profile.get(
        "profile_certified"
    ) is not True:
        raise KnowledgeRetrievalError(
            "Retrieved payload profile is not certified."
        )

    if profile.get(
        "profile_persisted"
    ) is not False:
        raise KnowledgeRetrievalError(
            "Immutable certified profile persistence flag drifted."
        )

    if profile.get(
        "profile_identity",
        {},
    ).get(
        "canonical_article_identity"
    ) != canonical_identity:
        raise KnowledgeRetrievalError(
            "Certified profile canonical identity drifted."
        )

    profile_json = json.dumps(
        dict(profile),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    actual_hash = hashlib.sha256(
        profile_json.encode("utf-8")
    ).hexdigest()

    actual_bytes = len(
        profile_json.encode("utf-8")
    )

    if retrieval_payload.get(
        "profile_payload_hash"
    ) != actual_hash:
        raise KnowledgeRetrievalError(
            "Retrieval payload profile hash drifted."
        )

    if retrieval_payload.get(
        "profile_payload_byte_length"
    ) != actual_bytes:
        raise KnowledgeRetrievalError(
            "Retrieval payload byte length drifted."
        )

    if lookup_receipt.get(
        "profile_payload_hash"
    ) != actual_hash:
        raise KnowledgeRetrievalError(
            "Lookup receipt profile hash drifted."
        )

    if lookup_receipt.get(
        "profile_payload_byte_length"
    ) != actual_bytes:
        raise KnowledgeRetrievalError(
            "Lookup receipt profile byte length drifted."
        )

    if store_metadata.get(
        "profile_payload_hash"
    ) not in (
        None,
        actual_hash,
    ):
        raise KnowledgeRetrievalError(
            "Store metadata profile hash drifted."
        )

    if store_metadata.get(
        "profile_payload_byte_length"
    ) not in (
        None,
        actual_bytes,
    ):
        raise KnowledgeRetrievalError(
            "Store metadata profile byte length drifted."
        )

    # -------------------------------------------------------------
    # Deterministic payload identity verification
    # -------------------------------------------------------------

    identity_material = {
        "knowledge_retrieval_version":
            KNOWLEDGE_RETRIEVAL_VERSION,

        "retrieval_query_id":
            retrieval_query[
                "retrieval_query_id"
            ],

        "storage_key":
            storage_key,

        "workspace_id":
            canonical_identity[
                "workspace_id"
            ],

        "article_id":
            canonical_identity[
                "article_id"
            ],

        "profile_payload_hash":
            actual_hash,

        "profile_payload_byte_length":
            actual_bytes,
    }

    identity_json = json.dumps(
        identity_material,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    expected_digest = hashlib.sha256(
        identity_json.encode("utf-8")
    ).hexdigest()

    expected_payload_id = (
        "krp:v1:"
        + expected_digest[:32]
    )

    if retrieval_payload.get(
        "retrieval_payload_digest"
    ) != expected_digest:
        raise KnowledgeRetrievalError(
            "Retrieval payload digest drifted."
        )

    if retrieval_payload.get(
        "retrieval_payload_id"
    ) != expected_payload_id:
        raise KnowledgeRetrievalError(
            "Retrieval payload ID drifted."
        )

    if assembly_receipt.get(
        "retrieval_payload_id"
    ) != expected_payload_id:
        raise KnowledgeRetrievalError(
            "Assembly receipt payload ID drifted."
        )

    # -------------------------------------------------------------
    # F processing-boundary authority
    # -------------------------------------------------------------

    for field in (
        "stored_profile_lookup_preserved",
        "retrieval_query_preserved",
        "canonical_identity_preserved",
        "storage_identity_preserved",
        "store_metadata_preserved",
        "retrieved_profile_preserved",
        "knowledge_retrieval_performed",
        "retrieval_payload_assembled",
    ):

        if boundaries.get(field) is not True:
            raise KnowledgeRetrievalError(
                f"Required 4.6.20F boundary is not True: {field}"
            )

    for field in (
        "additional_store_read_performed",
        "store_write_performed",
        "retrieval_integrity_verification_performed",
        "retrieval_projection_performed",
        "retrieval_metadata_provenance_built",
        "final_knowledge_retrieval_result_built",
        "full_knowledge_retrieval_certification_performed",
        "profile_payload_modified",
        "semantic_state_modified",
        "semantic_meaning_rewritten",
        "cross_document_reasoning_performed",
        "new_reasoning_performed",
        "new_fact_inference_performed",
        "new_relation_inference_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if boundaries.get(field) is not False:
            raise KnowledgeRetrievalError(
                f"Forbidden 4.6.20F boundary is not False: {field}"
            )

    integrity_certification = {
        "verification_status":
            "VERIFIED",

        "verification_scope":
            "KNOWLEDGE_RETRIEVAL_PAYLOAD_STRUCTURAL_AND_CRYPTOGRAPHIC_INTEGRITY",

        "verification_patch":
            "4.6.20G",

        "source_payload_patch":
            "4.6.20F",

        "retrieval_payload_id":
            expected_payload_id,

        "retrieval_payload_digest":
            expected_digest,

        "canonical_identity_verified":
            True,

        "storage_identity_verified":
            True,

        "retrieval_query_identity_verified":
            True,

        "profile_certification_verified":
            True,

        "profile_immutability_verified":
            True,

        "profile_payload_hash_verified":
            True,

        "profile_payload_byte_length_verified":
            True,

        "payload_identity_verified":
            True,

        "lookup_receipt_verified":
            True,

        "assembly_receipt_verified":
            True,

        "store_metadata_consistency_verified":
            True,

        "projection_performed":
            False,

        "additional_store_read_performed":
            False,

        "store_write_performed":
            False,

        "profile_payload_modified":
            False,

        "semantic_memory_written":
            False,

        "cross_document_reasoning_performed":
            False,

        "linking_decisions_performed":
            False,
    }

    verified_payload = deepcopy(
        dict(retrieval_payload)
    )

    verified_payload[
        "retrieval_integrity_verified"
    ] = True

    return {
        "schema_version":
            "knowledge_retrieval_integrity_verification_result_v1",

        "version":
            KNOWLEDGE_RETRIEVAL_VERSION,

        "phase":
            KNOWLEDGE_RETRIEVAL_PHASE,

        "patch":
            "4.6.20G",

        "status":
            "KNOWLEDGE_RETRIEVAL_INTEGRITY_VERIFIED",

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
                dict(store_metadata)
            ),

        "retrieval_query":
            deepcopy(
                dict(retrieval_query)
            ),

        "lookup_receipt":
            deepcopy(
                dict(lookup_receipt)
            ),

        "assembly_receipt":
            deepcopy(
                dict(assembly_receipt)
            ),

        "verified_retrieval_payload":
            verified_payload,

        "integrity_certification":
            integrity_certification,

        "source_payload_assembly_result":
            deepcopy(
                dict(payload_result)
            ),

        "processing_boundaries": {
            "retrieval_payload_assembly_preserved":
                True,

            "canonical_identity_preserved":
                True,

            "storage_identity_preserved":
                True,

            "store_metadata_preserved":
                True,

            "retrieval_query_preserved":
                True,

            "lookup_receipt_preserved":
                True,

            "assembly_receipt_preserved":
                True,

            "knowledge_retrieval_performed":
                True,

            "retrieval_payload_assembled":
                True,

            "retrieval_integrity_verification_performed":
                True,

            "retrieval_payload_integrity_verified":
                True,

            "additional_store_read_performed":
                False,

            "store_write_performed":
                False,

            "retrieval_projection_performed":
                False,

            "retrieval_metadata_provenance_built":
                False,

            "final_knowledge_retrieval_result_built":
                False,

            "full_knowledge_retrieval_certification_performed":
                False,

            "profile_payload_modified":
                False,

            "semantic_state_modified":
                False,

            "semantic_meaning_rewritten":
                False,

            "cross_document_reasoning_performed":
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
        },

        "retrieval_policy":
            "RETRIEVAL_PAYLOAD_INTEGRITY_VERIFIED",

        "next_stage":
            "retrieval_filtering_projection_contract",
    }


# =====================================================================
# PATCH 4.6.20H ? Retrieval Filtering / Projection Contract
# =====================================================================

def apply_knowledge_retrieval_projection_v1(
    integrity_result: dict[str, Any],
    requested_sections: list[str] | None = None,
) -> dict[str, Any]:
    """
    Apply a read-only projection over the verified retrieval payload.

    Projection never mutates the source certified profile.
    """

    from collections.abc import Mapping
    from copy import deepcopy
    import hashlib
    import json

    if not isinstance(
        integrity_result,
        Mapping,
    ):
        raise KnowledgeRetrievalError(
            "integrity_result must be a mapping."
        )

    if requested_sections is not None:
        if not isinstance(
            requested_sections,
            list,
        ):
            raise KnowledgeRetrievalError(
                "requested_sections must be a list or None."
            )

        if any(
            not isinstance(item, str) or not item
            for item in requested_sections
        ):
            raise KnowledgeRetrievalError(
                "requested_sections must contain non-empty strings only."
            )

    # -------------------------------------------------------------
    # Exact 4.6.20G lifecycle
    # -------------------------------------------------------------

    for field, expected in (
        (
            "schema_version",
            "knowledge_retrieval_integrity_verification_result_v1",
        ),
        (
            "version",
            KNOWLEDGE_RETRIEVAL_VERSION,
        ),
        (
            "phase",
            KNOWLEDGE_RETRIEVAL_PHASE,
        ),
        (
            "patch",
            "4.6.20G",
        ),
        (
            "status",
            "KNOWLEDGE_RETRIEVAL_INTEGRITY_VERIFIED",
        ),
        (
            "retrieval_policy",
            "RETRIEVAL_PAYLOAD_INTEGRITY_VERIFIED",
        ),
        (
            "next_stage",
            "retrieval_filtering_projection_contract",
        ),
    ):

        if integrity_result.get(field) != expected:
            raise KnowledgeRetrievalError(
                f"Invalid 4.6.20G lifecycle field: {field}"
            )

    canonical_identity = integrity_result.get(
        "canonical_article_identity"
    )

    storage_identity = integrity_result.get(
        "storage_identity"
    )

    store_metadata = integrity_result.get(
        "store_metadata"
    )

    retrieval_query = integrity_result.get(
        "retrieval_query"
    )

    verified_payload = integrity_result.get(
        "verified_retrieval_payload"
    )

    integrity_certification = integrity_result.get(
        "integrity_certification"
    )

    boundaries = integrity_result.get(
        "processing_boundaries"
    )

    for name, value in (
        ("canonical_article_identity", canonical_identity),
        ("storage_identity", storage_identity),
        ("store_metadata", store_metadata),
        ("retrieval_query", retrieval_query),
        ("verified_retrieval_payload", verified_payload),
        ("integrity_certification", integrity_certification),
        ("processing_boundaries", boundaries),
    ):

        if not isinstance(value, Mapping):
            raise KnowledgeRetrievalError(
                name + " is missing."
            )

    # -------------------------------------------------------------
    # G integrity authority
    # -------------------------------------------------------------

    if integrity_certification.get(
        "verification_status"
    ) != "VERIFIED":
        raise KnowledgeRetrievalError(
            "Retrieval integrity is not VERIFIED."
        )

    for field in (
        "canonical_identity_verified",
        "storage_identity_verified",
        "retrieval_query_identity_verified",
        "profile_certification_verified",
        "profile_immutability_verified",
        "profile_payload_hash_verified",
        "profile_payload_byte_length_verified",
        "payload_identity_verified",
        "lookup_receipt_verified",
        "assembly_receipt_verified",
        "store_metadata_consistency_verified",
    ):

        if integrity_certification.get(field) is not True:
            raise KnowledgeRetrievalError(
                f"Required G integrity field is not True: {field}"
            )

    for field in (
        "projection_performed",
        "additional_store_read_performed",
        "store_write_performed",
        "profile_payload_modified",
        "semantic_memory_written",
        "cross_document_reasoning_performed",
        "linking_decisions_performed",
    ):

        if integrity_certification.get(field) is not False:
            raise KnowledgeRetrievalError(
                f"Forbidden G integrity field is not False: {field}"
            )

    if verified_payload.get(
        "retrieval_integrity_verified"
    ) is not True:
        raise KnowledgeRetrievalError(
            "Verified retrieval payload is not integrity-verified."
        )

    profile = verified_payload.get(
        "certified_semantic_article_profile"
    )

    if not isinstance(
        profile,
        Mapping,
    ):
        raise KnowledgeRetrievalError(
            "Certified Semantic Article Profile is missing."
        )

    # -------------------------------------------------------------
    # Canonical projection surface
    # -------------------------------------------------------------

    canonical_sections = (
        "profile_identity",
        "source_authority",
        "semantic_layers",
        "semantic_groups",
        "cross_layer_artifacts",
        "governed_state",
        "structural_indexes",
        "certified_source_semantic_representation",
    )

    profile_section_order = profile.get(
        "profile_section_order"
    )

    if profile_section_order is not None:
        if tuple(
            profile_section_order
        ) != canonical_sections:
            raise KnowledgeRetrievalError(
                "Canonical profile section order drifted."
            )

    # Compact test fixtures may not include every canonical section.
    available_sections = [
        section
        for section in canonical_sections
        if section in profile
    ]

    if requested_sections is None or requested_sections == []:
        selected_sections = list(
            available_sections
        )

        projection_mode = "FULL_PROFILE"

        projection_applied = False

    else:
        seen = set()
        selected_sections = []

        for section in requested_sections:

            if section not in canonical_sections:
                raise KnowledgeRetrievalError(
                    f"Unsupported profile section requested: {section}"
                )

            if section not in profile:
                raise KnowledgeRetrievalError(
                    f"Requested profile section is unavailable: {section}"
                )

            if section in seen:
                raise KnowledgeRetrievalError(
                    f"Duplicate profile section requested: {section}"
                )

            seen.add(section)
            selected_sections.append(section)

        projection_mode = "SECTION_PROJECTION"

        projection_applied = True

    projected_sections = {
        section:
            deepcopy(
                profile[section]
            )
        for section in selected_sections
    }

    # -------------------------------------------------------------
    # Projection identity
    # -------------------------------------------------------------

    projection_material = {
        "retrieval_payload_id":
            verified_payload[
                "retrieval_payload_id"
            ],

        "projection_mode":
            projection_mode,

        "selected_sections":
            selected_sections,

        "profile_payload_hash":
            verified_payload[
                "profile_payload_hash"
            ],
    }

    projection_json = json.dumps(
        projection_material,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    projection_digest = hashlib.sha256(
        projection_json.encode("utf-8")
    ).hexdigest()

    projection_id = (
        "krproj:v1:"
        + projection_digest[:32]
    )

    # -------------------------------------------------------------
    # G processing-boundary authority
    # -------------------------------------------------------------

    for field in (
        "retrieval_payload_assembly_preserved",
        "canonical_identity_preserved",
        "storage_identity_preserved",
        "store_metadata_preserved",
        "retrieval_query_preserved",
        "lookup_receipt_preserved",
        "assembly_receipt_preserved",
        "knowledge_retrieval_performed",
        "retrieval_payload_assembled",
        "retrieval_integrity_verification_performed",
        "retrieval_payload_integrity_verified",
    ):

        if boundaries.get(field) is not True:
            raise KnowledgeRetrievalError(
                f"Required 4.6.20G boundary is not True: {field}"
            )

    for field in (
        "additional_store_read_performed",
        "store_write_performed",
        "retrieval_projection_performed",
        "retrieval_metadata_provenance_built",
        "final_knowledge_retrieval_result_built",
        "full_knowledge_retrieval_certification_performed",
        "profile_payload_modified",
        "semantic_state_modified",
        "semantic_meaning_rewritten",
        "cross_document_reasoning_performed",
        "new_reasoning_performed",
        "new_fact_inference_performed",
        "new_relation_inference_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if boundaries.get(field) is not False:
            raise KnowledgeRetrievalError(
                f"Forbidden 4.6.20G boundary is not False: {field}"
            )

    projection_contract = {
        "projection_status":
            "PROJECTED"
            if projection_applied
            else "FULL_PROFILE_PRESERVED",

        "projection_scope":
            "CERTIFIED_PROFILE_SECTION_PROJECTION",

        "projection_patch":
            "4.6.20H",

        "projection_id":
            projection_id,

        "projection_digest":
            projection_digest,

        "projection_digest_algorithm":
            "SHA256",

        "projection_mode":
            projection_mode,

        "canonical_section_order":
            list(
                canonical_sections
            ),

        "available_sections":
            list(
                available_sections
            ),

        "selected_sections":
            list(
                selected_sections
            ),

        "projection_applied":
            projection_applied,

        "source_profile_preserved":
            True,

        "source_profile_immutable":
            True,

        "read_only":
            True,

        "additional_store_read_performed":
            False,

        "store_write_performed":
            False,

        "semantic_state_modified":
            False,

        "semantic_meaning_rewritten":
            False,

        "semantic_memory_written":
            False,

        "cross_document_reasoning_performed":
            False,

        "linking_decisions_performed":
            False,
    }

    retrieval_view = {
        "retrieval_view_schema":
            "knowledge_retrieval_view_v1",

        "retrieval_view_version":
            "v1",

        "retrieval_payload_id":
            verified_payload[
                "retrieval_payload_id"
            ],

        "projection_id":
            projection_id,

        "projection_mode":
            projection_mode,

        "canonical_article_identity":
            deepcopy(
                dict(canonical_identity)
            ),

        "storage_key":
            storage_identity[
                "storage_key"
            ],

        "profile_payload_hash":
            verified_payload[
                "profile_payload_hash"
            ],

        "profile_payload_byte_length":
            verified_payload[
                "profile_payload_byte_length"
            ],

        "selected_sections":
            list(
                selected_sections
            ),

        "projected_profile_sections":
            projected_sections,

        "full_certified_profile":
            (
                deepcopy(
                    dict(profile)
                )
                if not projection_applied
                else None
            ),

        "projection_applied":
            projection_applied,

        "read_only":
            True,

        "source_profile_immutable":
            True,

        "retrieval_integrity_verified":
            True,

        "retrieval_provenance_attached":
            False,

        "semantic_memory_written":
            False,

        "cross_document_reasoning_performed":
            False,

        "linking_decisions_performed":
            False,
    }

    return {
        "schema_version":
            "knowledge_retrieval_projection_result_v1",

        "version":
            KNOWLEDGE_RETRIEVAL_VERSION,

        "phase":
            KNOWLEDGE_RETRIEVAL_PHASE,

        "patch":
            "4.6.20H",

        "status":
            "KNOWLEDGE_RETRIEVAL_PROJECTION_READY",

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
                dict(store_metadata)
            ),

        "retrieval_query":
            deepcopy(
                dict(retrieval_query)
            ),

        "verified_retrieval_payload":
            deepcopy(
                dict(verified_payload)
            ),

        "projection_contract":
            projection_contract,

        "retrieval_view":
            retrieval_view,

        "source_integrity_result":
            deepcopy(
                dict(integrity_result)
            ),

        "processing_boundaries": {
            "retrieval_integrity_verification_preserved":
                True,

            "verified_retrieval_payload_preserved":
                True,

            "canonical_identity_preserved":
                True,

            "storage_identity_preserved":
                True,

            "store_metadata_preserved":
                True,

            "knowledge_retrieval_performed":
                True,

            "retrieval_payload_assembled":
                True,

            "retrieval_integrity_verification_performed":
                True,

            "retrieval_projection_performed":
                True,

            "source_profile_preserved":
                True,

            "additional_store_read_performed":
                False,

            "store_write_performed":
                False,

            "retrieval_metadata_provenance_built":
                False,

            "final_knowledge_retrieval_result_built":
                False,

            "full_knowledge_retrieval_certification_performed":
                False,

            "profile_payload_modified":
                False,

            "semantic_state_modified":
                False,

            "semantic_meaning_rewritten":
                False,

            "cross_document_reasoning_performed":
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
        },

        "retrieval_policy":
            "READ_ONLY_RETRIEVAL_PROJECTION_READY",

        "next_stage":
            "retrieval_metadata_provenance",
    }


# =====================================================================
# PATCH 4.6.20I ? Retrieval Metadata & Provenance
# =====================================================================

def build_knowledge_retrieval_metadata_provenance_v1(
    projection_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Attach deterministic metadata and provenance to a verified
    Knowledge Retrieval view.

    I does not mutate the source profile or retrieval view.
    """

    from collections.abc import Mapping
    from copy import deepcopy
    import hashlib
    import json

    if not isinstance(
        projection_result,
        Mapping,
    ):
        raise KnowledgeRetrievalError(
            "projection_result must be a mapping."
        )

    # -------------------------------------------------------------
    # Exact 4.6.20H lifecycle
    # -------------------------------------------------------------

    for field, expected in (
        (
            "schema_version",
            "knowledge_retrieval_projection_result_v1",
        ),
        (
            "version",
            KNOWLEDGE_RETRIEVAL_VERSION,
        ),
        (
            "phase",
            KNOWLEDGE_RETRIEVAL_PHASE,
        ),
        (
            "patch",
            "4.6.20H",
        ),
        (
            "status",
            "KNOWLEDGE_RETRIEVAL_PROJECTION_READY",
        ),
        (
            "retrieval_policy",
            "READ_ONLY_RETRIEVAL_PROJECTION_READY",
        ),
        (
            "next_stage",
            "retrieval_metadata_provenance",
        ),
    ):

        if projection_result.get(field) != expected:
            raise KnowledgeRetrievalError(
                f"Invalid 4.6.20H lifecycle field: {field}"
            )

    canonical_identity = projection_result.get(
        "canonical_article_identity"
    )

    storage_identity = projection_result.get(
        "storage_identity"
    )

    store_metadata = projection_result.get(
        "store_metadata"
    )

    retrieval_query = projection_result.get(
        "retrieval_query"
    )

    verified_payload = projection_result.get(
        "verified_retrieval_payload"
    )

    projection_contract = projection_result.get(
        "projection_contract"
    )

    retrieval_view = projection_result.get(
        "retrieval_view"
    )

    boundaries = projection_result.get(
        "processing_boundaries"
    )

    for name, value in (
        ("canonical_article_identity", canonical_identity),
        ("storage_identity", storage_identity),
        ("store_metadata", store_metadata),
        ("retrieval_query", retrieval_query),
        ("verified_retrieval_payload", verified_payload),
        ("projection_contract", projection_contract),
        ("retrieval_view", retrieval_view),
        ("processing_boundaries", boundaries),
    ):

        if not isinstance(value, Mapping):
            raise KnowledgeRetrievalError(
                name + " is missing."
            )

    # -------------------------------------------------------------
    # H projection authority
    # -------------------------------------------------------------

    if projection_contract.get(
        "projection_status"
    ) not in (
        "PROJECTED",
        "FULL_PROFILE_PRESERVED",
    ):
        raise KnowledgeRetrievalError(
            "Projection status is invalid."
        )

    if projection_contract.get(
        "projection_scope"
    ) != "CERTIFIED_PROFILE_SECTION_PROJECTION":
        raise KnowledgeRetrievalError(
            "Projection scope drifted."
        )

    if projection_contract.get(
        "projection_patch"
    ) != "4.6.20H":
        raise KnowledgeRetrievalError(
            "Projection patch drifted."
        )

    if projection_contract.get(
        "source_profile_preserved"
    ) is not True:
        raise KnowledgeRetrievalError(
            "Source profile was not preserved."
        )

    if projection_contract.get(
        "source_profile_immutable"
    ) is not True:
        raise KnowledgeRetrievalError(
            "Source profile immutability drifted."
        )

    if projection_contract.get(
        "read_only"
    ) is not True:
        raise KnowledgeRetrievalError(
            "Projection is not read-only."
        )

    for field in (
        "additional_store_read_performed",
        "store_write_performed",
        "semantic_state_modified",
        "semantic_meaning_rewritten",
        "semantic_memory_written",
        "cross_document_reasoning_performed",
        "linking_decisions_performed",
    ):

        if projection_contract.get(field) is not False:
            raise KnowledgeRetrievalError(
                f"Forbidden projection field is not False: {field}"
            )

    # -------------------------------------------------------------
    # Retrieval view authority
    # -------------------------------------------------------------

    if retrieval_view.get(
        "retrieval_view_schema"
    ) != "knowledge_retrieval_view_v1":
        raise KnowledgeRetrievalError(
            "Retrieval view schema drifted."
        )

    if retrieval_view.get(
        "retrieval_view_version"
    ) != "v1":
        raise KnowledgeRetrievalError(
            "Retrieval view version drifted."
        )

    if retrieval_view.get(
        "retrieval_payload_id"
    ) != verified_payload.get(
        "retrieval_payload_id"
    ):
        raise KnowledgeRetrievalError(
            "Retrieval view payload identity drifted."
        )

    if retrieval_view.get(
        "projection_id"
    ) != projection_contract.get(
        "projection_id"
    ):
        raise KnowledgeRetrievalError(
            "Retrieval view projection identity drifted."
        )

    if retrieval_view.get(
        "canonical_article_identity"
    ) != canonical_identity:
        raise KnowledgeRetrievalError(
            "Retrieval view canonical identity drifted."
        )

    if retrieval_view.get(
        "storage_key"
    ) != storage_identity.get(
        "storage_key"
    ):
        raise KnowledgeRetrievalError(
            "Retrieval view storage key drifted."
        )

    for field in (
        "read_only",
        "source_profile_immutable",
        "retrieval_integrity_verified",
    ):

        if retrieval_view.get(field) is not True:
            raise KnowledgeRetrievalError(
                f"Required retrieval-view field is not True: {field}"
            )

    if retrieval_view.get(
        "retrieval_provenance_attached"
    ) is not False:
        raise KnowledgeRetrievalError(
            "Retrieval provenance was already attached."
        )

    for field in (
        "semantic_memory_written",
        "cross_document_reasoning_performed",
        "linking_decisions_performed",
    ):

        if retrieval_view.get(field) is not False:
            raise KnowledgeRetrievalError(
                f"Forbidden retrieval-view field is not False: {field}"
            )

    # -------------------------------------------------------------
    # Verified payload authority
    # -------------------------------------------------------------

    if verified_payload.get(
        "retrieval_integrity_verified"
    ) is not True:
        raise KnowledgeRetrievalError(
            "Verified retrieval payload lost integrity status."
        )

    profile = verified_payload.get(
        "certified_semantic_article_profile"
    )

    if not isinstance(profile, Mapping):
        raise KnowledgeRetrievalError(
            "Certified profile is missing."
        )

    if profile.get(
        "profile_certified"
    ) is not True:
        raise KnowledgeRetrievalError(
            "Certified profile is not certified."
        )

    if profile.get(
        "profile_persisted"
    ) is not False:
        raise KnowledgeRetrievalError(
            "Immutable certified profile persistence flag drifted."
        )

    if profile.get(
        "profile_identity",
        {},
    ).get(
        "canonical_article_identity"
    ) != canonical_identity:
        raise KnowledgeRetrievalError(
            "Certified profile canonical identity drifted."
        )

    # -------------------------------------------------------------
    # Store/query identity consistency
    # -------------------------------------------------------------

    storage_key = storage_identity.get(
        "storage_key"
    )

    if store_metadata.get(
        "storage_key"
    ) != storage_key:
        raise KnowledgeRetrievalError(
            "Store metadata storage key drifted."
        )

    retrieval_query_id = retrieval_query.get(
        "retrieval_query_id"
    )

    retrieval_payload_id = verified_payload.get(
        "retrieval_payload_id"
    )

    projection_id = projection_contract.get(
        "projection_id"
    )

    if not isinstance(
        retrieval_query_id,
        str,
    ) or not retrieval_query_id:
        raise KnowledgeRetrievalError(
            "retrieval_query_id is missing."
        )

    if not isinstance(
        retrieval_payload_id,
        str,
    ) or not retrieval_payload_id:
        raise KnowledgeRetrievalError(
            "retrieval_payload_id is missing."
        )

    if not isinstance(
        projection_id,
        str,
    ) or not projection_id:
        raise KnowledgeRetrievalError(
            "projection_id is missing."
        )

    # -------------------------------------------------------------
    # H processing-boundary authority
    # -------------------------------------------------------------

    for field in (
        "retrieval_integrity_verification_preserved",
        "verified_retrieval_payload_preserved",
        "canonical_identity_preserved",
        "storage_identity_preserved",
        "store_metadata_preserved",
        "knowledge_retrieval_performed",
        "retrieval_payload_assembled",
        "retrieval_integrity_verification_performed",
        "retrieval_projection_performed",
        "source_profile_preserved",
    ):

        if boundaries.get(field) is not True:
            raise KnowledgeRetrievalError(
                f"Required 4.6.20H boundary is not True: {field}"
            )

    for field in (
        "additional_store_read_performed",
        "store_write_performed",
        "retrieval_metadata_provenance_built",
        "final_knowledge_retrieval_result_built",
        "full_knowledge_retrieval_certification_performed",
        "profile_payload_modified",
        "semantic_state_modified",
        "semantic_meaning_rewritten",
        "cross_document_reasoning_performed",
        "new_reasoning_performed",
        "new_fact_inference_performed",
        "new_relation_inference_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if boundaries.get(field) is not False:
            raise KnowledgeRetrievalError(
                f"Forbidden 4.6.20H boundary is not False: {field}"
            )

    # -------------------------------------------------------------
    # Deterministic provenance identity
    # -------------------------------------------------------------

    provenance_material = {
        "knowledge_retrieval_version":
            KNOWLEDGE_RETRIEVAL_VERSION,

        "workspace_id":
            canonical_identity[
                "workspace_id"
            ],

        "article_id":
            canonical_identity[
                "article_id"
            ],

        "storage_key":
            storage_key,

        "retrieval_query_id":
            retrieval_query_id,

        "retrieval_payload_id":
            retrieval_payload_id,

        "projection_id":
            projection_id,

        "profile_payload_hash":
            verified_payload[
                "profile_payload_hash"
            ],
    }

    provenance_json = json.dumps(
        provenance_material,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    provenance_digest = hashlib.sha256(
        provenance_json.encode("utf-8")
    ).hexdigest()

    provenance_id = (
        "krprov:v1:"
        + provenance_digest[:32]
    )

    retrieval_provenance = {
        "provenance_schema":
            "knowledge_retrieval_provenance_v1",

        "provenance_version":
            "v1",

        "provenance_id":
            provenance_id,

        "provenance_digest":
            provenance_digest,

        "provenance_digest_algorithm":
            "SHA256",

        "provenance_material_canonicalization":
            "JSON_SORTED_KEYS_COMPACT_UTF8",

        "workspace_id":
            canonical_identity[
                "workspace_id"
            ],

        "article_id":
            canonical_identity[
                "article_id"
            ],

        "storage_key":
            storage_key,

        "source_profile_store_phase":
            "4.6.19",

        "source_profile_store_patch":
            "4.6.19K",

        "knowledge_retrieval_phase":
            "4.6.20",

        "input_inspection_patch":
            "4.6.20A",

        "architecture_patch":
            "4.6.20B",

        "intake_validation_patch":
            "4.6.20C",

        "query_contract_patch":
            "4.6.20D",

        "lookup_patch":
            "4.6.20E",

        "payload_assembly_patch":
            "4.6.20F",

        "integrity_verification_patch":
            "4.6.20G",

        "projection_patch":
            "4.6.20H",

        "metadata_provenance_patch":
            "4.6.20I",

        "retrieval_query_id":
            retrieval_query_id,

        "retrieval_payload_id":
            retrieval_payload_id,

        "projection_id":
            projection_id,

        "profile_payload_hash":
            verified_payload[
                "profile_payload_hash"
            ],

        "profile_payload_byte_length":
            verified_payload[
                "profile_payload_byte_length"
            ],

        "projection_mode":
            projection_contract[
                "projection_mode"
            ],

        "selected_sections":
            deepcopy(
                projection_contract[
                    "selected_sections"
                ]
            ),

        "source_profile_certified":
            True,

        "source_profile_immutable":
            True,

        "retrieval_integrity_verified":
            True,

        "read_only":
            True,

        "additional_store_read_performed":
            False,

        "store_write_performed":
            False,

        "profile_payload_modified":
            False,

        "semantic_state_modified":
            False,

        "semantic_meaning_rewritten":
            False,

        "semantic_memory_written":
            False,

        "cross_document_reasoning_performed":
            False,

        "linking_decisions_performed":
            False,
    }

    provenance_metadata = {
        "metadata_schema":
            "knowledge_retrieval_metadata_v1",

        "metadata_version":
            "v1",

        "metadata_status":
            "BUILT",

        "metadata_patch":
            "4.6.20I",

        "provenance_id":
            provenance_id,

        "retrieval_query_id":
            retrieval_query_id,

        "retrieval_payload_id":
            retrieval_payload_id,

        "projection_id":
            projection_id,

        "canonical_identity_preserved":
            True,

        "storage_identity_preserved":
            True,

        "profile_hash_preserved":
            True,

        "profile_byte_length_preserved":
            True,

        "projection_identity_preserved":
            True,

        "lineage_complete_through_4.6.20I":
            True,

        "read_only":
            True,

        "metadata_separate_from_profile_payload":
            True,

        "profile_payload_modified":
            False,

        "semantic_memory_written":
            False,

        "cross_document_reasoning_performed":
            False,

        "linking_decisions_performed":
            False,
    }

    provenance_view = deepcopy(
        dict(retrieval_view)
    )

    provenance_view[
        "retrieval_provenance_attached"
    ] = True

    return {
        "schema_version":
            "knowledge_retrieval_metadata_provenance_result_v1",

        "version":
            KNOWLEDGE_RETRIEVAL_VERSION,

        "phase":
            KNOWLEDGE_RETRIEVAL_PHASE,

        "patch":
            "4.6.20I",

        "status":
            "KNOWLEDGE_RETRIEVAL_METADATA_PROVENANCE_BUILT",

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
                dict(store_metadata)
            ),

        "retrieval_query":
            deepcopy(
                dict(retrieval_query)
            ),

        "verified_retrieval_payload":
            deepcopy(
                dict(verified_payload)
            ),

        "projection_contract":
            deepcopy(
                dict(projection_contract)
            ),

        "retrieval_view":
            provenance_view,

        "retrieval_provenance":
            retrieval_provenance,

        "provenance_metadata":
            provenance_metadata,

        "source_projection_result":
            deepcopy(
                dict(projection_result)
            ),

        "processing_boundaries": {
            "retrieval_projection_preserved":
                True,

            "retrieval_integrity_verification_preserved":
                True,

            "verified_retrieval_payload_preserved":
                True,

            "canonical_identity_preserved":
                True,

            "storage_identity_preserved":
                True,

            "store_metadata_preserved":
                True,

            "knowledge_retrieval_performed":
                True,

            "retrieval_payload_assembled":
                True,

            "retrieval_integrity_verification_performed":
                True,

            "retrieval_projection_performed":
                True,

            "retrieval_metadata_provenance_built":
                True,

            "source_profile_preserved":
                True,

            "additional_store_read_performed":
                False,

            "store_write_performed":
                False,

            "final_knowledge_retrieval_result_built":
                False,

            "full_knowledge_retrieval_certification_performed":
                False,

            "profile_payload_modified":
                False,

            "semantic_state_modified":
                False,

            "semantic_meaning_rewritten":
                False,

            "cross_document_reasoning_performed":
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
        },

        "retrieval_policy":
            "RETRIEVAL_METADATA_AND_PROVENANCE_BUILT",

        "next_stage":
            "final_knowledge_retrieval_result",
    }


# =====================================================================
# PATCH 4.6.20J ? Final Knowledge Retrieval Result
# =====================================================================

def build_final_knowledge_retrieval_result_v1(
    provenance_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Build the canonical final Knowledge Retrieval result.

    J assembles the final read-only retrieval product.
    It performs no new retrieval, reasoning, memory write, or linking.
    """

    from collections.abc import Mapping
    from copy import deepcopy
    import hashlib
    import json

    if not isinstance(
        provenance_result,
        Mapping,
    ):
        raise KnowledgeRetrievalError(
            "provenance_result must be a mapping."
        )

    # -------------------------------------------------------------
    # Exact 4.6.20I lifecycle
    # -------------------------------------------------------------

    for field, expected in (
        (
            "schema_version",
            "knowledge_retrieval_metadata_provenance_result_v1",
        ),
        (
            "version",
            KNOWLEDGE_RETRIEVAL_VERSION,
        ),
        (
            "phase",
            KNOWLEDGE_RETRIEVAL_PHASE,
        ),
        (
            "patch",
            "4.6.20I",
        ),
        (
            "status",
            "KNOWLEDGE_RETRIEVAL_METADATA_PROVENANCE_BUILT",
        ),
        (
            "retrieval_policy",
            "RETRIEVAL_METADATA_AND_PROVENANCE_BUILT",
        ),
        (
            "next_stage",
            "final_knowledge_retrieval_result",
        ),
    ):

        if provenance_result.get(field) != expected:
            raise KnowledgeRetrievalError(
                f"Invalid 4.6.20I lifecycle field: {field}"
            )

    canonical_identity = provenance_result.get(
        "canonical_article_identity"
    )

    storage_identity = provenance_result.get(
        "storage_identity"
    )

    store_metadata = provenance_result.get(
        "store_metadata"
    )

    retrieval_query = provenance_result.get(
        "retrieval_query"
    )

    verified_payload = provenance_result.get(
        "verified_retrieval_payload"
    )

    projection_contract = provenance_result.get(
        "projection_contract"
    )

    retrieval_view = provenance_result.get(
        "retrieval_view"
    )

    retrieval_provenance = provenance_result.get(
        "retrieval_provenance"
    )

    provenance_metadata = provenance_result.get(
        "provenance_metadata"
    )

    boundaries = provenance_result.get(
        "processing_boundaries"
    )

    for name, value in (
        ("canonical_article_identity", canonical_identity),
        ("storage_identity", storage_identity),
        ("store_metadata", store_metadata),
        ("retrieval_query", retrieval_query),
        ("verified_retrieval_payload", verified_payload),
        ("projection_contract", projection_contract),
        ("retrieval_view", retrieval_view),
        ("retrieval_provenance", retrieval_provenance),
        ("provenance_metadata", provenance_metadata),
        ("processing_boundaries", boundaries),
    ):

        if not isinstance(
            value,
            Mapping,
        ):
            raise KnowledgeRetrievalError(
                name + " is missing."
            )

    # -------------------------------------------------------------
    # I provenance authority
    # -------------------------------------------------------------

    if retrieval_provenance.get(
        "provenance_schema"
    ) != "knowledge_retrieval_provenance_v1":
        raise KnowledgeRetrievalError(
            "Retrieval provenance schema drifted."
        )

    if provenance_metadata.get(
        "metadata_schema"
    ) != "knowledge_retrieval_metadata_v1":
        raise KnowledgeRetrievalError(
            "Retrieval metadata schema drifted."
        )

    if provenance_metadata.get(
        "metadata_status"
    ) != "BUILT":
        raise KnowledgeRetrievalError(
            "Retrieval metadata is not BUILT."
        )

    if provenance_metadata.get(
        "lineage_complete_through_4.6.20I"
    ) is not True:
        raise KnowledgeRetrievalError(
            "Knowledge Retrieval lineage is incomplete."
        )

    if retrieval_view.get(
        "retrieval_provenance_attached"
    ) is not True:
        raise KnowledgeRetrievalError(
            "Retrieval provenance is not attached."
        )

    for field in (
        "source_profile_certified",
        "source_profile_immutable",
        "retrieval_integrity_verified",
        "read_only",
    ):

        if retrieval_provenance.get(field) is not True:
            raise KnowledgeRetrievalError(
                f"Required provenance field is not True: {field}"
            )

    for field in (
        "additional_store_read_performed",
        "store_write_performed",
        "profile_payload_modified",
        "semantic_state_modified",
        "semantic_meaning_rewritten",
        "semantic_memory_written",
        "cross_document_reasoning_performed",
        "linking_decisions_performed",
    ):

        if retrieval_provenance.get(field) is not False:
            raise KnowledgeRetrievalError(
                f"Forbidden provenance field is not False: {field}"
            )

    # -------------------------------------------------------------
    # Verified payload / view consistency
    # -------------------------------------------------------------

    profile = verified_payload.get(
        "certified_semantic_article_profile"
    )

    if not isinstance(profile, Mapping):
        raise KnowledgeRetrievalError(
            "Certified profile is missing."
        )

    if verified_payload.get(
        "retrieval_integrity_verified"
    ) is not True:
        raise KnowledgeRetrievalError(
            "Verified payload lost integrity status."
        )

    if profile.get(
        "profile_certified"
    ) is not True:
        raise KnowledgeRetrievalError(
            "Final retrieval source profile is not certified."
        )

    if profile.get(
        "profile_persisted"
    ) is not False:
        raise KnowledgeRetrievalError(
            "Immutable certified profile persistence flag drifted."
        )

    if retrieval_view.get(
        "retrieval_payload_id"
    ) != verified_payload.get(
        "retrieval_payload_id"
    ):
        raise KnowledgeRetrievalError(
            "Retrieval view payload identity drifted."
        )

    if retrieval_view.get(
        "projection_id"
    ) != projection_contract.get(
        "projection_id"
    ):
        raise KnowledgeRetrievalError(
            "Retrieval view projection identity drifted."
        )

    if retrieval_provenance.get(
        "retrieval_payload_id"
    ) != verified_payload.get(
        "retrieval_payload_id"
    ):
        raise KnowledgeRetrievalError(
            "Provenance payload identity drifted."
        )

    if retrieval_provenance.get(
        "projection_id"
    ) != projection_contract.get(
        "projection_id"
    ):
        raise KnowledgeRetrievalError(
            "Provenance projection identity drifted."
        )

    if retrieval_provenance.get(
        "retrieval_query_id"
    ) != retrieval_query.get(
        "retrieval_query_id"
    ):
        raise KnowledgeRetrievalError(
            "Provenance query identity drifted."
        )

    # -------------------------------------------------------------
    # Canonical identity consistency
    # -------------------------------------------------------------

    storage_key = storage_identity.get(
        "storage_key"
    )

    if store_metadata.get(
        "storage_key"
    ) != storage_key:
        raise KnowledgeRetrievalError(
            "Store metadata storage key drifted."
        )

    if retrieval_view.get(
        "storage_key"
    ) != storage_key:
        raise KnowledgeRetrievalError(
            "Retrieval view storage key drifted."
        )

    if retrieval_view.get(
        "canonical_article_identity"
    ) != canonical_identity:
        raise KnowledgeRetrievalError(
            "Retrieval view canonical identity drifted."
        )

    if profile.get(
        "profile_identity",
        {},
    ).get(
        "canonical_article_identity"
    ) != canonical_identity:
        raise KnowledgeRetrievalError(
            "Certified profile canonical identity drifted."
        )

    # -------------------------------------------------------------
    # I processing-boundary authority
    # -------------------------------------------------------------

    for field in (
        "retrieval_projection_preserved",
        "retrieval_integrity_verification_preserved",
        "verified_retrieval_payload_preserved",
        "canonical_identity_preserved",
        "storage_identity_preserved",
        "store_metadata_preserved",
        "knowledge_retrieval_performed",
        "retrieval_payload_assembled",
        "retrieval_integrity_verification_performed",
        "retrieval_projection_performed",
        "retrieval_metadata_provenance_built",
        "source_profile_preserved",
    ):

        if boundaries.get(field) is not True:
            raise KnowledgeRetrievalError(
                f"Required 4.6.20I boundary is not True: {field}"
            )

    for field in (
        "additional_store_read_performed",
        "store_write_performed",
        "final_knowledge_retrieval_result_built",
        "full_knowledge_retrieval_certification_performed",
        "profile_payload_modified",
        "semantic_state_modified",
        "semantic_meaning_rewritten",
        "cross_document_reasoning_performed",
        "new_reasoning_performed",
        "new_fact_inference_performed",
        "new_relation_inference_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if boundaries.get(field) is not False:
            raise KnowledgeRetrievalError(
                f"Forbidden 4.6.20I boundary is not False: {field}"
            )

    # -------------------------------------------------------------
    # Final deterministic result identity
    # -------------------------------------------------------------

    final_identity_material = {
        "knowledge_retrieval_version":
            KNOWLEDGE_RETRIEVAL_VERSION,

        "workspace_id":
            canonical_identity[
                "workspace_id"
            ],

        "article_id":
            canonical_identity[
                "article_id"
            ],

        "storage_key":
            storage_key,

        "retrieval_query_id":
            retrieval_query[
                "retrieval_query_id"
            ],

        "retrieval_payload_id":
            verified_payload[
                "retrieval_payload_id"
            ],

        "projection_id":
            projection_contract[
                "projection_id"
            ],

        "provenance_id":
            retrieval_provenance[
                "provenance_id"
            ],

        "profile_payload_hash":
            verified_payload[
                "profile_payload_hash"
            ],
    }

    final_identity_json = json.dumps(
        final_identity_material,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    final_result_digest = hashlib.sha256(
        final_identity_json.encode("utf-8")
    ).hexdigest()

    final_result_id = (
        "krfinal:v1:"
        + final_result_digest[:32]
    )

    final_retrieval_result = {
        "final_result_schema":
            "final_knowledge_retrieval_result_v1",

        "final_result_version":
            "v1",

        "final_result_id":
            final_result_id,

        "final_result_digest":
            final_result_digest,

        "final_result_digest_algorithm":
            "SHA256",

        "final_result_identity_canonicalization":
            "JSON_SORTED_KEYS_COMPACT_UTF8",

        "canonical_article_identity":
            deepcopy(
                dict(canonical_identity)
            ),

        "storage_key":
            storage_key,

        "retrieval_query_id":
            retrieval_query[
                "retrieval_query_id"
            ],

        "retrieval_payload_id":
            verified_payload[
                "retrieval_payload_id"
            ],

        "projection_id":
            projection_contract[
                "projection_id"
            ],

        "provenance_id":
            retrieval_provenance[
                "provenance_id"
            ],

        "profile_payload_hash":
            verified_payload[
                "profile_payload_hash"
            ],

        "profile_payload_byte_length":
            verified_payload[
                "profile_payload_byte_length"
            ],

        "projection_mode":
            projection_contract[
                "projection_mode"
            ],

        "selected_sections":
            deepcopy(
                projection_contract[
                    "selected_sections"
                ]
            ),

        "retrieval_view":
            deepcopy(
                dict(retrieval_view)
            ),

        "retrieval_provenance":
            deepcopy(
                dict(retrieval_provenance)
            ),

        "source_certified_semantic_article_profile":
            deepcopy(
                dict(profile)
            ),

        "profile_store_source":
            "4.6.19K_CERTIFIED_PROFILE_STORE",

        "knowledge_retrieval_source":
            "4.6.20A_THROUGH_4.6.20I",

        "read_only":
            True,

        "source_profile_certified":
            True,

        "source_profile_immutable":
            True,

        "retrieval_integrity_verified":
            True,

        "retrieval_provenance_attached":
            True,

        "cross_document_reasoning_ready":
            True,

        "cross_document_reasoning_performed":
            False,

        "semantic_memory_written":
            False,

        "linking_decisions_performed":
            False,
    }

    final_result_summary = {
        "final_status":
            "KNOWLEDGE_RETRIEVAL_RESULT_READY_FOR_CERTIFICATION",

        "knowledge_retrieval_performed":
            True,

        "profile_store_read_performed":
            True,

        "retrieval_payload_assembled":
            True,

        "retrieval_integrity_verified":
            True,

        "retrieval_projection_completed":
            True,

        "retrieval_metadata_provenance_built":
            True,

        "source_profile_certified":
            True,

        "source_profile_immutable":
            True,

        "canonical_identity_preserved":
            True,

        "storage_identity_preserved":
            True,

        "profile_payload_hash_preserved":
            True,

        "profile_payload_byte_length_preserved":
            True,

        "read_only":
            True,

        "additional_store_read_performed":
            False,

        "store_write_performed":
            False,

        "profile_payload_modified":
            False,

        "semantic_state_modified":
            False,

        "semantic_meaning_rewritten":
            False,

        "cross_document_reasoning_performed":
            False,

        "semantic_memory_written":
            False,

        "linking_decisions_performed":
            False,

        "full_knowledge_retrieval_certified":
            False,

        "next_owner":
            "4.6.20K_FULL_KNOWLEDGE_RETRIEVAL_HARD_CERTIFICATION",

        "post_certification_owner":
            "4.6.21_CROSS_DOCUMENT_REASONING",
    }

    return {
        "schema_version":
            "final_knowledge_retrieval_result_envelope_v1",

        "version":
            KNOWLEDGE_RETRIEVAL_VERSION,

        "phase":
            KNOWLEDGE_RETRIEVAL_PHASE,

        "patch":
            "4.6.20J",

        "status":
            "FINAL_KNOWLEDGE_RETRIEVAL_RESULT_BUILT",

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
                dict(store_metadata)
            ),

        "retrieval_query":
            deepcopy(
                dict(retrieval_query)
            ),

        "verified_retrieval_payload":
            deepcopy(
                dict(verified_payload)
            ),

        "projection_contract":
            deepcopy(
                dict(projection_contract)
            ),

        "retrieval_view":
            deepcopy(
                dict(retrieval_view)
            ),

        "retrieval_provenance":
            deepcopy(
                dict(retrieval_provenance)
            ),

        "provenance_metadata":
            deepcopy(
                dict(provenance_metadata)
            ),

        "final_knowledge_retrieval_result":
            final_retrieval_result,

        "final_result_summary":
            final_result_summary,

        "source_metadata_provenance_result":
            deepcopy(
                dict(provenance_result)
            ),

        "processing_boundaries": {
            "retrieval_metadata_provenance_preserved":
                True,

            "retrieval_projection_preserved":
                True,

            "retrieval_integrity_verification_preserved":
                True,

            "verified_retrieval_payload_preserved":
                True,

            "canonical_identity_preserved":
                True,

            "storage_identity_preserved":
                True,

            "store_metadata_preserved":
                True,

            "knowledge_retrieval_performed":
                True,

            "retrieval_payload_assembled":
                True,

            "retrieval_integrity_verification_performed":
                True,

            "retrieval_projection_performed":
                True,

            "retrieval_metadata_provenance_built":
                True,

            "final_knowledge_retrieval_result_built":
                True,

            "source_profile_preserved":
                True,

            "additional_store_read_performed":
                False,

            "store_write_performed":
                False,

            "full_knowledge_retrieval_certification_performed":
                False,

            "profile_payload_modified":
                False,

            "semantic_state_modified":
                False,

            "semantic_meaning_rewritten":
                False,

            "cross_document_reasoning_performed":
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
        },

        "retrieval_policy":
            "FINAL_READ_ONLY_KNOWLEDGE_RETRIEVAL_RESULT_READY_FOR_CERTIFICATION",

        "next_stage":
            "full_knowledge_retrieval_hard_certification",
    }


# =====================================================================
# PATCH 4.6.20K ? Full Knowledge Retrieval Hard Certification
# =====================================================================

def certify_knowledge_retrieval_v1(
    final_result_envelope: dict[str, Any],
) -> dict[str, Any]:
    """
    Hard-certify the complete 4.6.20 Knowledge Retrieval pipeline.

    K certifies A through J and produces the authoritative
    4.6.21 Cross-Document Reasoning handoff.
    """

    from collections.abc import Mapping
    from copy import deepcopy
    import hashlib
    import json

    if not isinstance(
        final_result_envelope,
        Mapping,
    ):
        raise KnowledgeRetrievalError(
            "final_result_envelope must be a mapping."
        )

    # -------------------------------------------------------------
    # Exact 4.6.20J lifecycle
    # -------------------------------------------------------------

    for field, expected in (
        (
            "schema_version",
            "final_knowledge_retrieval_result_envelope_v1",
        ),
        (
            "version",
            KNOWLEDGE_RETRIEVAL_VERSION,
        ),
        (
            "phase",
            KNOWLEDGE_RETRIEVAL_PHASE,
        ),
        (
            "patch",
            "4.6.20J",
        ),
        (
            "status",
            "FINAL_KNOWLEDGE_RETRIEVAL_RESULT_BUILT",
        ),
        (
            "retrieval_policy",
            "FINAL_READ_ONLY_KNOWLEDGE_RETRIEVAL_RESULT_READY_FOR_CERTIFICATION",
        ),
        (
            "next_stage",
            "full_knowledge_retrieval_hard_certification",
        ),
    ):

        if final_result_envelope.get(field) != expected:
            raise KnowledgeRetrievalError(
                f"Invalid 4.6.20J lifecycle field: {field}"
            )

    canonical_identity = final_result_envelope.get(
        "canonical_article_identity"
    )

    storage_identity = final_result_envelope.get(
        "storage_identity"
    )

    store_metadata = final_result_envelope.get(
        "store_metadata"
    )

    retrieval_query = final_result_envelope.get(
        "retrieval_query"
    )

    verified_payload = final_result_envelope.get(
        "verified_retrieval_payload"
    )

    projection_contract = final_result_envelope.get(
        "projection_contract"
    )

    retrieval_view = final_result_envelope.get(
        "retrieval_view"
    )

    retrieval_provenance = final_result_envelope.get(
        "retrieval_provenance"
    )

    provenance_metadata = final_result_envelope.get(
        "provenance_metadata"
    )

    final_result = final_result_envelope.get(
        "final_knowledge_retrieval_result"
    )

    summary = final_result_envelope.get(
        "final_result_summary"
    )

    boundaries = final_result_envelope.get(
        "processing_boundaries"
    )

    for name, value in (
        ("canonical_article_identity", canonical_identity),
        ("storage_identity", storage_identity),
        ("store_metadata", store_metadata),
        ("retrieval_query", retrieval_query),
        ("verified_retrieval_payload", verified_payload),
        ("projection_contract", projection_contract),
        ("retrieval_view", retrieval_view),
        ("retrieval_provenance", retrieval_provenance),
        ("provenance_metadata", provenance_metadata),
        ("final_knowledge_retrieval_result", final_result),
        ("final_result_summary", summary),
        ("processing_boundaries", boundaries),
    ):

        if not isinstance(
            value,
            Mapping,
        ):
            raise KnowledgeRetrievalError(
                name + " is missing."
            )

    # -------------------------------------------------------------
    # Final J result authority
    # -------------------------------------------------------------

    if final_result.get(
        "final_result_schema"
    ) != "final_knowledge_retrieval_result_v1":
        raise KnowledgeRetrievalError(
            "Final retrieval result schema drifted."
        )

    if final_result.get(
        "final_result_version"
    ) != "v1":
        raise KnowledgeRetrievalError(
            "Final retrieval result version drifted."
        )

    if final_result.get(
        "profile_store_source"
    ) != "4.6.19K_CERTIFIED_PROFILE_STORE":
        raise KnowledgeRetrievalError(
            "Profile Store source drifted."
        )

    if final_result.get(
        "knowledge_retrieval_source"
    ) != "4.6.20A_THROUGH_4.6.20I":
        raise KnowledgeRetrievalError(
            "Knowledge Retrieval source lineage drifted."
        )

    for field in (
        "read_only",
        "source_profile_certified",
        "source_profile_immutable",
        "retrieval_integrity_verified",
        "retrieval_provenance_attached",
        "cross_document_reasoning_ready",
    ):

        if final_result.get(field) is not True:
            raise KnowledgeRetrievalError(
                f"Required final-result field is not True: {field}"
            )

    for field in (
        "cross_document_reasoning_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if final_result.get(field) is not False:
            raise KnowledgeRetrievalError(
                f"Forbidden final-result field is not False: {field}"
            )

    # -------------------------------------------------------------
    # Final summary authority
    # -------------------------------------------------------------

    if summary.get(
        "final_status"
    ) != "KNOWLEDGE_RETRIEVAL_RESULT_READY_FOR_CERTIFICATION":
        raise KnowledgeRetrievalError(
            "Final summary status drifted."
        )

    if summary.get(
        "next_owner"
    ) != "4.6.20K_FULL_KNOWLEDGE_RETRIEVAL_HARD_CERTIFICATION":
        raise KnowledgeRetrievalError(
            "K ownership handoff drifted."
        )

    if summary.get(
        "post_certification_owner"
    ) != "4.6.21_CROSS_DOCUMENT_REASONING":
        raise KnowledgeRetrievalError(
            "4.6.21 ownership handoff drifted."
        )

    for field in (
        "knowledge_retrieval_performed",
        "profile_store_read_performed",
        "retrieval_payload_assembled",
        "retrieval_integrity_verified",
        "retrieval_projection_completed",
        "retrieval_metadata_provenance_built",
        "source_profile_certified",
        "source_profile_immutable",
        "canonical_identity_preserved",
        "storage_identity_preserved",
        "profile_payload_hash_preserved",
        "profile_payload_byte_length_preserved",
        "read_only",
    ):

        if summary.get(field) is not True:
            raise KnowledgeRetrievalError(
                f"Required final-summary field is not True: {field}"
            )

    for field in (
        "additional_store_read_performed",
        "store_write_performed",
        "profile_payload_modified",
        "semantic_state_modified",
        "semantic_meaning_rewritten",
        "cross_document_reasoning_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
        "full_knowledge_retrieval_certified",
    ):

        if summary.get(field) is not False:
            raise KnowledgeRetrievalError(
                f"Forbidden final-summary field is not False: {field}"
            )

    # -------------------------------------------------------------
    # Canonical identity consistency
    # -------------------------------------------------------------

    storage_key = storage_identity.get(
        "storage_key"
    )

    query_id = retrieval_query.get(
        "retrieval_query_id"
    )

    payload_id = verified_payload.get(
        "retrieval_payload_id"
    )

    projection_id = projection_contract.get(
        "projection_id"
    )

    provenance_id = retrieval_provenance.get(
        "provenance_id"
    )

    if final_result.get(
        "canonical_article_identity"
    ) != canonical_identity:
        raise KnowledgeRetrievalError(
            "Final canonical identity drifted."
        )

    if final_result.get(
        "storage_key"
    ) != storage_key:
        raise KnowledgeRetrievalError(
            "Final storage key drifted."
        )

    if final_result.get(
        "retrieval_query_id"
    ) != query_id:
        raise KnowledgeRetrievalError(
            "Final query ID drifted."
        )

    if final_result.get(
        "retrieval_payload_id"
    ) != payload_id:
        raise KnowledgeRetrievalError(
            "Final payload ID drifted."
        )

    if final_result.get(
        "projection_id"
    ) != projection_id:
        raise KnowledgeRetrievalError(
            "Final projection ID drifted."
        )

    if final_result.get(
        "provenance_id"
    ) != provenance_id:
        raise KnowledgeRetrievalError(
            "Final provenance ID drifted."
        )

    if store_metadata.get(
        "storage_key"
    ) != storage_key:
        raise KnowledgeRetrievalError(
            "Store metadata storage key drifted."
        )

    # -------------------------------------------------------------
    # Certified source-profile authority
    # -------------------------------------------------------------

    profile = verified_payload.get(
        "certified_semantic_article_profile"
    )

    final_profile = final_result.get(
        "source_certified_semantic_article_profile"
    )

    if not isinstance(
        profile,
        Mapping,
    ):
        raise KnowledgeRetrievalError(
            "Verified source profile is missing."
        )

    if final_profile != profile:
        raise KnowledgeRetrievalError(
            "Final certified source profile drifted."
        )

    if profile.get(
        "profile_certified"
    ) is not True:
        raise KnowledgeRetrievalError(
            "Source profile is not certified."
        )

    if profile.get(
        "profile_persisted"
    ) is not False:
        raise KnowledgeRetrievalError(
            "Immutable source profile persistence flag drifted."
        )

    if profile.get(
        "profile_identity",
        {},
    ).get(
        "canonical_article_identity"
    ) != canonical_identity:
        raise KnowledgeRetrievalError(
            "Source profile canonical identity drifted."
        )

    # -------------------------------------------------------------
    # View / provenance consistency
    # -------------------------------------------------------------

    if final_result.get(
        "retrieval_view"
    ) != retrieval_view:
        raise KnowledgeRetrievalError(
            "Final retrieval view drifted."
        )

    if final_result.get(
        "retrieval_provenance"
    ) != retrieval_provenance:
        raise KnowledgeRetrievalError(
            "Final retrieval provenance drifted."
        )

    if retrieval_view.get(
        "retrieval_provenance_attached"
    ) is not True:
        raise KnowledgeRetrievalError(
            "Retrieval provenance is not attached."
        )

    if verified_payload.get(
        "retrieval_integrity_verified"
    ) is not True:
        raise KnowledgeRetrievalError(
            "Payload integrity status drifted."
        )

    if provenance_metadata.get(
        "lineage_complete_through_4.6.20I"
    ) is not True:
        raise KnowledgeRetrievalError(
            "A-I lineage is incomplete."
        )

    # -------------------------------------------------------------
    # Independent final-result digest verification
    # -------------------------------------------------------------

    final_identity_material = {
        "knowledge_retrieval_version":
            KNOWLEDGE_RETRIEVAL_VERSION,

        "workspace_id":
            canonical_identity[
                "workspace_id"
            ],

        "article_id":
            canonical_identity[
                "article_id"
            ],

        "storage_key":
            storage_key,

        "retrieval_query_id":
            query_id,

        "retrieval_payload_id":
            payload_id,

        "projection_id":
            projection_id,

        "provenance_id":
            provenance_id,

        "profile_payload_hash":
            verified_payload[
                "profile_payload_hash"
            ],
    }

    final_identity_json = json.dumps(
        final_identity_material,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    expected_digest = hashlib.sha256(
        final_identity_json.encode("utf-8")
    ).hexdigest()

    expected_id = (
        "krfinal:v1:"
        + expected_digest[:32]
    )

    if final_result.get(
        "final_result_digest"
    ) != expected_digest:
        raise KnowledgeRetrievalError(
            "Final result digest drifted."
        )

    if final_result.get(
        "final_result_id"
    ) != expected_id:
        raise KnowledgeRetrievalError(
            "Final result ID drifted."
        )

    # -------------------------------------------------------------
    # Independent profile hash / byte verification
    # -------------------------------------------------------------

    profile_json = json.dumps(
        dict(profile),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    actual_profile_hash = hashlib.sha256(
        profile_json.encode("utf-8")
    ).hexdigest()

    actual_profile_bytes = len(
        profile_json.encode("utf-8")
    )

    if verified_payload.get(
        "profile_payload_hash"
    ) != actual_profile_hash:
        raise KnowledgeRetrievalError(
            "Verified profile hash drifted."
        )

    if verified_payload.get(
        "profile_payload_byte_length"
    ) != actual_profile_bytes:
        raise KnowledgeRetrievalError(
            "Verified profile byte length drifted."
        )

    if final_result.get(
        "profile_payload_hash"
    ) != actual_profile_hash:
        raise KnowledgeRetrievalError(
            "Final profile hash drifted."
        )

    if final_result.get(
        "profile_payload_byte_length"
    ) != actual_profile_bytes:
        raise KnowledgeRetrievalError(
            "Final profile byte length drifted."
        )

    # -------------------------------------------------------------
    # J processing-boundary authority
    # -------------------------------------------------------------

    for field in (
        "retrieval_metadata_provenance_preserved",
        "retrieval_projection_preserved",
        "retrieval_integrity_verification_preserved",
        "verified_retrieval_payload_preserved",
        "canonical_identity_preserved",
        "storage_identity_preserved",
        "store_metadata_preserved",
        "knowledge_retrieval_performed",
        "retrieval_payload_assembled",
        "retrieval_integrity_verification_performed",
        "retrieval_projection_performed",
        "retrieval_metadata_provenance_built",
        "final_knowledge_retrieval_result_built",
        "source_profile_preserved",
    ):

        if boundaries.get(field) is not True:
            raise KnowledgeRetrievalError(
                f"Required 4.6.20J boundary is not True: {field}"
            )

    for field in (
        "additional_store_read_performed",
        "store_write_performed",
        "full_knowledge_retrieval_certification_performed",
        "profile_payload_modified",
        "semantic_state_modified",
        "semantic_meaning_rewritten",
        "cross_document_reasoning_performed",
        "new_reasoning_performed",
        "new_fact_inference_performed",
        "new_relation_inference_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if boundaries.get(field) is not False:
            raise KnowledgeRetrievalError(
                f"Forbidden 4.6.20J boundary is not False: {field}"
            )

    # -------------------------------------------------------------
    # Full Knowledge Retrieval certification
    # -------------------------------------------------------------

    full_certification = {
        "certification_status":
            "CERTIFIED",

        "certification_scope":
            "FULL_KNOWLEDGE_RETRIEVAL_PIPELINE",

        "certification_mode":
            "END_TO_END_READ_ONLY_RETRIEVAL_INTEGRITY_PROJECTION_PROVENANCE_HARD_CERTIFICATION",

        "certified_phase":
            "4.6.20",

        "certified_source_patch":
            "4.6.20J",

        "profile_store_source_phase":
            "4.6.19",

        "profile_store_source_patch":
            "4.6.19K",

        "input_inspection_certified":
            True,

        "architecture_certified":
            True,

        "intake_validation_certified":
            True,

        "query_contract_certified":
            True,

        "stored_profile_lookup_certified":
            True,

        "retrieval_payload_assembly_certified":
            True,

        "retrieval_integrity_certified":
            True,

        "projection_contract_certified":
            True,

        "metadata_provenance_certified":
            True,

        "final_result_certified":
            True,

        "canonical_identity_preserved":
            True,

        "storage_identity_preserved":
            True,

        "profile_payload_hash_preserved":
            True,

        "profile_payload_byte_length_preserved":
            True,

        "source_profile_certified":
            True,

        "source_profile_immutable":
            True,

        "retrieval_read_only":
            True,

        "retrieval_integrity_verified":
            True,

        "retrieval_provenance_complete":
            True,

        "cross_document_reasoning_ready":
            True,

        "cross_document_reasoning_owner":
            "4.6.21_CROSS_DOCUMENT_REASONING",

        "semantic_memory_owner":
            "4.6.28_SEMANTIC_MEMORY",

        "additional_store_read_performed":
            False,

        "store_write_performed":
            False,

        "profile_payload_modified":
            False,

        "semantic_state_modified":
            False,

        "semantic_meaning_rewritten":
            False,

        "cross_document_reasoning_performed":
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

    certified_final_result = deepcopy(
        dict(final_result)
    )

    certified_final_result[
        "full_knowledge_retrieval_certified"
    ] = True

    certified_final_result[
        "certification_status"
    ] = "CERTIFIED"

    certified_final_result[
        "next_owner"
    ] = "4.6.21_CROSS_DOCUMENT_REASONING"

    certified_summary = deepcopy(
        dict(summary)
    )

    certified_summary[
        "final_status"
    ] = "KNOWLEDGE_RETRIEVAL_CERTIFIED"

    certified_summary[
        "full_knowledge_retrieval_certified"
    ] = True

    certified_summary[
        "next_owner"
    ] = "4.6.21_CROSS_DOCUMENT_REASONING"

    return {
        "schema_version":
            "certified_knowledge_retrieval_result_v1",

        "version":
            KNOWLEDGE_RETRIEVAL_VERSION,

        "phase":
            KNOWLEDGE_RETRIEVAL_PHASE,

        "patch":
            "4.6.20K",

        "status":
            "KNOWLEDGE_RETRIEVAL_CERTIFIED",

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
                dict(store_metadata)
            ),

        "retrieval_query":
            deepcopy(
                dict(retrieval_query)
            ),

        "verified_retrieval_payload":
            deepcopy(
                dict(verified_payload)
            ),

        "projection_contract":
            deepcopy(
                dict(projection_contract)
            ),

        "retrieval_view":
            deepcopy(
                dict(retrieval_view)
            ),

        "retrieval_provenance":
            deepcopy(
                dict(retrieval_provenance)
            ),

        "provenance_metadata":
            deepcopy(
                dict(provenance_metadata)
            ),

        "certified_final_knowledge_retrieval_result":
            certified_final_result,

        "full_knowledge_retrieval_certification":
            full_certification,

        "final_result_summary":
            certified_summary,

        "source_final_result_envelope":
            deepcopy(
                dict(final_result_envelope)
            ),

        "processing_boundaries": {
            "input_inspection_preserved":
                True,

            "architecture_definition_preserved":
                True,

            "intake_validation_preserved":
                True,

            "query_contract_preserved":
                True,

            "stored_profile_lookup_preserved":
                True,

            "retrieval_payload_assembly_preserved":
                True,

            "retrieval_integrity_verification_preserved":
                True,

            "retrieval_projection_preserved":
                True,

            "retrieval_metadata_provenance_preserved":
                True,

            "final_knowledge_retrieval_result_preserved":
                True,

            "full_knowledge_retrieval_certification_performed":
                True,

            "knowledge_retrieval_certified":
                True,

            "source_profile_preserved":
                True,

            "canonical_identity_preserved":
                True,

            "storage_identity_preserved":
                True,

            "profile_hash_preserved":
                True,

            "profile_byte_length_preserved":
                True,

            "additional_store_read_performed":
                False,

            "store_write_performed":
                False,

            "profile_payload_modified":
                False,

            "semantic_state_modified":
                False,

            "semantic_meaning_rewritten":
                False,

            "cross_document_reasoning_performed":
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
        },

        "retrieval_policy":
            "FULL_KNOWLEDGE_RETRIEVAL_CERTIFIED",

        "next_stage":
            "cross_document_reasoning",
    }

