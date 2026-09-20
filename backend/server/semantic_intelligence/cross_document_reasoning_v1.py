"""
LinkCraftor Semantic Intelligence

4.6.21 ? Cross-Document Reasoning

Consumes only certified 4.6.20K Knowledge Retrieval output.

Cross-Document Reasoning does not own:
- Profile Store persistence,
- Knowledge Retrieval,
- Semantic Memory,
- linking decisions.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


CROSS_DOCUMENT_REASONING_VERSION = "cross_document_reasoning_v1"
CROSS_DOCUMENT_REASONING_PHASE = "4.6.21"


class CrossDocumentReasoningError(Exception):
    """Raised when the Cross-Document Reasoning contract is violated."""

# =====================================================================
# PATCH 4.6.21A ? Certified 4.6.20K Input Contract Inspection
# =====================================================================

def inspect_certified_knowledge_retrieval_input_v1(
    certified_retrieval_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Inspect the exact frozen 4.6.20K Knowledge Retrieval contract.

    Inspection only:
    - no cross-document reasoning,
    - no new fact inference,
    - no conflict resolution,
    - no Semantic Memory write,
    - no linking decision.
    """

    from collections.abc import Mapping
    from copy import deepcopy

    if not isinstance(
        certified_retrieval_result,
        Mapping,
    ):
        raise CrossDocumentReasoningError(
            "certified_retrieval_result must be a mapping."
        )

    # -------------------------------------------------------------
    # Exact 4.6.20K lifecycle
    # -------------------------------------------------------------

    for field, expected in (
        (
            "schema_version",
            "certified_knowledge_retrieval_result_v1",
        ),
        (
            "version",
            "knowledge_retrieval_v1",
        ),
        (
            "phase",
            "4.6.20",
        ),
        (
            "patch",
            "4.6.20K",
        ),
        (
            "status",
            "KNOWLEDGE_RETRIEVAL_CERTIFIED",
        ),
        (
            "retrieval_policy",
            "FULL_KNOWLEDGE_RETRIEVAL_CERTIFIED",
        ),
        (
            "next_stage",
            "cross_document_reasoning",
        ),
    ):

        if certified_retrieval_result.get(field) != expected:
            raise CrossDocumentReasoningError(
                f"Invalid certified Knowledge Retrieval field: {field}"
            )

    canonical_identity = certified_retrieval_result.get(
        "canonical_article_identity"
    )

    storage_identity = certified_retrieval_result.get(
        "storage_identity"
    )

    store_metadata = certified_retrieval_result.get(
        "store_metadata"
    )

    retrieval_query = certified_retrieval_result.get(
        "retrieval_query"
    )

    verified_payload = certified_retrieval_result.get(
        "verified_retrieval_payload"
    )

    projection_contract = certified_retrieval_result.get(
        "projection_contract"
    )

    retrieval_view = certified_retrieval_result.get(
        "retrieval_view"
    )

    retrieval_provenance = certified_retrieval_result.get(
        "retrieval_provenance"
    )

    certified_final = certified_retrieval_result.get(
        "certified_final_knowledge_retrieval_result"
    )

    certification = certified_retrieval_result.get(
        "full_knowledge_retrieval_certification"
    )

    summary = certified_retrieval_result.get(
        "final_result_summary"
    )

    boundaries = certified_retrieval_result.get(
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
        (
            "certified_final_knowledge_retrieval_result",
            certified_final,
        ),
        (
            "full_knowledge_retrieval_certification",
            certification,
        ),
        ("final_result_summary", summary),
        ("processing_boundaries", boundaries),
    ):

        if not isinstance(value, Mapping):
            raise CrossDocumentReasoningError(
                name + " is missing."
            )

    # -------------------------------------------------------------
    # Full 4.6.20 certification authority
    # -------------------------------------------------------------

    for field, expected in (
        (
            "certification_status",
            "CERTIFIED",
        ),
        (
            "certification_scope",
            "FULL_KNOWLEDGE_RETRIEVAL_PIPELINE",
        ),
        (
            "certified_phase",
            "4.6.20",
        ),
        (
            "certified_source_patch",
            "4.6.20J",
        ),
        (
            "profile_store_source_phase",
            "4.6.19",
        ),
        (
            "profile_store_source_patch",
            "4.6.19K",
        ),
        (
            "cross_document_reasoning_owner",
            "4.6.21_CROSS_DOCUMENT_REASONING",
        ),
        (
            "semantic_memory_owner",
            "4.6.28_SEMANTIC_MEMORY",
        ),
    ):

        if certification.get(field) != expected:
            raise CrossDocumentReasoningError(
                f"Knowledge Retrieval certification drifted: {field}"
            )

    for field in (
        "input_inspection_certified",
        "architecture_certified",
        "intake_validation_certified",
        "query_contract_certified",
        "stored_profile_lookup_certified",
        "retrieval_payload_assembly_certified",
        "retrieval_integrity_certified",
        "projection_contract_certified",
        "metadata_provenance_certified",
        "final_result_certified",
        "canonical_identity_preserved",
        "storage_identity_preserved",
        "profile_payload_hash_preserved",
        "profile_payload_byte_length_preserved",
        "source_profile_certified",
        "source_profile_immutable",
        "retrieval_read_only",
        "retrieval_integrity_verified",
        "retrieval_provenance_complete",
        "cross_document_reasoning_ready",
    ):

        if certification.get(field) is not True:
            raise CrossDocumentReasoningError(
                f"Required certification field is not True: {field}"
            )

    for field in (
        "additional_store_read_performed",
        "store_write_performed",
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

        if certification.get(field) is not False:
            raise CrossDocumentReasoningError(
                f"Forbidden certification field is not False: {field}"
            )

    # -------------------------------------------------------------
    # Certified final Knowledge Retrieval result
    # -------------------------------------------------------------

    if certified_final.get(
        "full_knowledge_retrieval_certified"
    ) is not True:
        raise CrossDocumentReasoningError(
            "Final Knowledge Retrieval result is not certified."
        )

    if certified_final.get(
        "certification_status"
    ) != "CERTIFIED":
        raise CrossDocumentReasoningError(
            "Certified final result status drifted."
        )

    if certified_final.get(
        "next_owner"
    ) != "4.6.21_CROSS_DOCUMENT_REASONING":
        raise CrossDocumentReasoningError(
            "Cross-Document Reasoning handoff drifted."
        )

    if certified_final.get(
        "cross_document_reasoning_ready"
    ) is not True:
        raise CrossDocumentReasoningError(
            "Certified result is not reasoning-ready."
        )

    if certified_final.get(
        "cross_document_reasoning_performed"
    ) is not False:
        raise CrossDocumentReasoningError(
            "Cross-document reasoning occurred prematurely."
        )

    if certified_final.get(
        "semantic_memory_written"
    ) is not False:
        raise CrossDocumentReasoningError(
            "Semantic Memory was written prematurely."
        )

    if certified_final.get(
        "linking_decisions_performed"
    ) is not False:
        raise CrossDocumentReasoningError(
            "Linking decisions occurred prematurely."
        )

    # -------------------------------------------------------------
    # Source profile / identity preservation
    # -------------------------------------------------------------

    source_profile = certified_final.get(
        "source_certified_semantic_article_profile"
    )

    if not isinstance(source_profile, Mapping):
        raise CrossDocumentReasoningError(
            "Certified source profile is missing."
        )

    if source_profile.get(
        "profile_certified"
    ) is not True:
        raise CrossDocumentReasoningError(
            "Source semantic profile is not certified."
        )

    if source_profile.get(
        "profile_persisted"
    ) is not False:
        raise CrossDocumentReasoningError(
            "Immutable source profile persistence flag drifted."
        )

    if source_profile.get(
        "profile_identity",
        {},
    ).get(
        "canonical_article_identity"
    ) != canonical_identity:
        raise CrossDocumentReasoningError(
            "Source profile canonical identity drifted."
        )

    if certified_final.get(
        "canonical_article_identity"
    ) != canonical_identity:
        raise CrossDocumentReasoningError(
            "Certified final canonical identity drifted."
        )

    storage_key = storage_identity.get(
        "storage_key"
    )

    if certified_final.get(
        "storage_key"
    ) != storage_key:
        raise CrossDocumentReasoningError(
            "Certified final storage key drifted."
        )

    if store_metadata.get(
        "storage_key"
    ) != storage_key:
        raise CrossDocumentReasoningError(
            "Store metadata storage key drifted."
        )

    # -------------------------------------------------------------
    # Retrieval lineage preservation
    # -------------------------------------------------------------

    if certified_final.get(
        "retrieval_query_id"
    ) != retrieval_query.get(
        "retrieval_query_id"
    ):
        raise CrossDocumentReasoningError(
            "Retrieval query identity drifted."
        )

    if certified_final.get(
        "retrieval_payload_id"
    ) != verified_payload.get(
        "retrieval_payload_id"
    ):
        raise CrossDocumentReasoningError(
            "Retrieval payload identity drifted."
        )

    if certified_final.get(
        "projection_id"
    ) != projection_contract.get(
        "projection_id"
    ):
        raise CrossDocumentReasoningError(
            "Projection identity drifted."
        )

    if certified_final.get(
        "provenance_id"
    ) != retrieval_provenance.get(
        "provenance_id"
    ):
        raise CrossDocumentReasoningError(
            "Retrieval provenance identity drifted."
        )

    if certified_final.get(
        "retrieval_view"
    ) != retrieval_view:
        raise CrossDocumentReasoningError(
            "Retrieval view drifted."
        )

    if certified_final.get(
        "retrieval_provenance"
    ) != retrieval_provenance:
        raise CrossDocumentReasoningError(
            "Retrieval provenance drifted."
        )

    # -------------------------------------------------------------
    # Certified summary
    # -------------------------------------------------------------

    if summary.get(
        "final_status"
    ) != "KNOWLEDGE_RETRIEVAL_CERTIFIED":
        raise CrossDocumentReasoningError(
            "Certified summary status drifted."
        )

    if summary.get(
        "full_knowledge_retrieval_certified"
    ) is not True:
        raise CrossDocumentReasoningError(
            "Certified summary flag is false."
        )

    if summary.get(
        "next_owner"
    ) != "4.6.21_CROSS_DOCUMENT_REASONING":
        raise CrossDocumentReasoningError(
            "Certified summary owner drifted."
        )

    # -------------------------------------------------------------
    # 4.6.20K processing boundaries
    # -------------------------------------------------------------

    for field in (
        "input_inspection_preserved",
        "architecture_definition_preserved",
        "intake_validation_preserved",
        "query_contract_preserved",
        "stored_profile_lookup_preserved",
        "retrieval_payload_assembly_preserved",
        "retrieval_integrity_verification_preserved",
        "retrieval_projection_preserved",
        "retrieval_metadata_provenance_preserved",
        "final_knowledge_retrieval_result_preserved",
        "full_knowledge_retrieval_certification_performed",
        "knowledge_retrieval_certified",
        "source_profile_preserved",
        "canonical_identity_preserved",
        "storage_identity_preserved",
        "profile_hash_preserved",
        "profile_byte_length_preserved",
    ):

        if boundaries.get(field) is not True:
            raise CrossDocumentReasoningError(
                f"Required 4.6.20K boundary is not True: {field}"
            )

    for field in (
        "additional_store_read_performed",
        "store_write_performed",
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
            raise CrossDocumentReasoningError(
                f"Forbidden 4.6.20K boundary is not False: {field}"
            )

    return {
        "schema_version":
            "cross_document_reasoning_input_inspection_result_v1",

        "version":
            CROSS_DOCUMENT_REASONING_VERSION,

        "phase":
            CROSS_DOCUMENT_REASONING_PHASE,

        "patch":
            "4.6.21A",

        "status":
            "CERTIFIED_KNOWLEDGE_RETRIEVAL_INPUT_INSPECTED",

        "canonical_article_identity":
            deepcopy(dict(canonical_identity)),

        "storage_identity":
            deepcopy(dict(storage_identity)),

        "retrieval_query":
            deepcopy(dict(retrieval_query)),

        "verified_retrieval_payload":
            deepcopy(dict(verified_payload)),

        "projection_contract":
            deepcopy(dict(projection_contract)),

        "retrieval_view":
            deepcopy(dict(retrieval_view)),

        "retrieval_provenance":
            deepcopy(dict(retrieval_provenance)),

        "certified_knowledge_retrieval_result":
            deepcopy(dict(certified_final)),

        "source_certified_knowledge_retrieval_envelope":
            deepcopy(dict(certified_retrieval_result)),

        "inspection": {
            "inspection_status":
                "PASSED",

            "inspection_scope":
                "CERTIFIED_4.6.20K_KNOWLEDGE_RETRIEVAL_INPUT",

            "source_phase":
                "4.6.20",

            "source_patch":
                "4.6.20K",

            "knowledge_retrieval_certified":
                True,

            "source_profile_certified":
                True,

            "source_profile_immutable":
                True,

            "retrieval_integrity_verified":
                True,

            "retrieval_provenance_complete":
                True,

            "cross_document_reasoning_ready":
                True,

            "cross_document_reasoning_owner_confirmed":
                True,

            "semantic_memory_deferred":
                True,

            "cross_document_reasoning_performed":
                False,
        },

        "processing_boundaries": {
            "certified_knowledge_retrieval_input_inspected":
                True,

            "certified_knowledge_retrieval_input_preserved":
                True,

            "source_profile_preserved":
                True,

            "canonical_identity_preserved":
                True,

            "storage_identity_preserved":
                True,

            "retrieval_lineage_preserved":
                True,

            "cross_document_reasoning_architecture_defined":
                False,

            "reasoning_intake_validation_performed":
                False,

            "document_set_scope_defined":
                False,

            "cross_document_evidence_alignment_performed":
                False,

            "cross_document_relationships_constructed":
                False,

            "cross_document_reasoning_performed":
                False,

            "reasoning_integrity_verification_performed":
                False,

            "reasoning_provenance_built":
                False,

            "final_cross_document_reasoning_result_built":
                False,

            "full_cross_document_reasoning_certification_performed":
                False,

            "source_profile_modified":
                False,

            "retrieval_payload_modified":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,
        },

        "reasoning_policy":
            "CERTIFIED_KNOWLEDGE_RETRIEVAL_INPUT_ONLY",

        "next_stage":
            "cross_document_reasoning_architecture_definition",
    }


# =====================================================================
# PATCH 4.6.21B ? Cross-Document Reasoning Architecture Definition
# =====================================================================

def define_cross_document_reasoning_architecture_v1() -> dict[str, Any]:
    """
    Define the canonical architecture for 4.6.21.

    Architecture definition only.
    No cross-document reasoning is executed here.
    """

    architecture = {
        "architecture_schema":
            "cross_document_reasoning_architecture_v1",

        "architecture_version":
            CROSS_DOCUMENT_REASONING_VERSION,

        "phase":
            CROSS_DOCUMENT_REASONING_PHASE,

        "owner":
            "4.6.21_CROSS_DOCUMENT_REASONING",

        "source_owner":
            "4.6.20_KNOWLEDGE_RETRIEVAL",

        "next_owner":
            "4.6.22_ONTOLOGY_ALIGNMENT",

        "semantic_memory_owner":
            "4.6.28_SEMANTIC_MEMORY",

        "scope":
            "CERTIFIED_MULTI_DOCUMENT_SEMANTIC_REASONING",

        "mode":
            "EVIDENCE_BOUND_READ_ONLY_CROSS_DOCUMENT_REASONING",

        "input_contract":
            "certified_knowledge_retrieval_result_v1",

        "output_contract":
            "certified_cross_document_reasoning_result_v1",

        "canonical_source":
            "4.6.20K_CERTIFIED_KNOWLEDGE_RETRIEVAL",

        "stage_order": [
            "4.6.21A_certified_knowledge_retrieval_input_inspection",
            "4.6.21B_cross_document_reasoning_architecture_definition",
            "4.6.21C_reasoning_intake_validation",
            "4.6.21D_document_set_reasoning_scope_contract",
            "4.6.21E_cross_document_evidence_alignment",
            "4.6.21F_cross_document_relationship_construction",
            "4.6.21G_cross_document_reasoning_execution",
            "4.6.21H_reasoning_integrity_conflict_guard",
            "4.6.21I_reasoning_provenance_evidence_trace",
            "4.6.21J_final_cross_document_reasoning_result",
            "4.6.21K_full_cross_document_reasoning_hard_certification",
        ],

        "principles": {
            "certified_retrieval_inputs_only":
                True,

            "minimum_two_documents_required":
                True,

            "source_profiles_immutable":
                True,

            "retrieval_payloads_immutable":
                True,

            "evidence_bound_reasoning":
                True,

            "reasoning_must_be_traceable":
                True,

            "deterministic_contracts":
                True,

            "document_identity_preserved":
                True,

            "workspace_scope_preserved":
                True,

            "cross_document_claims_require_evidence":
                True,

            "conflicts_must_be_explicit":
                True,

            "uncertainty_must_be_explicit":
                True,

            "no_source_profile_rewrite":
                True,

            "no_retrieval_payload_rewrite":
                True,

            "no_profile_store_write":
                True,

            "no_semantic_memory_write":
                True,

            "no_linking_decision":
                True,

            "no_publication_action":
                True,
        },

        "supported_reasoning": {
            "shared_concept_reasoning":
                True,

            "complementary_information_reasoning":
                True,

            "hierarchical_relationship_reasoning":
                True,

            "prerequisite_relationship_reasoning":
                True,

            "causal_relationship_reasoning":
                True,

            "procedural_sequence_reasoning":
                True,

            "temporal_relationship_reasoning":
                True,

            "supporting_evidence_reasoning":
                True,

            "contradiction_detection":
                True,

            "overlap_duplication_reasoning":
                True,

            "content_gap_reasoning":
                True,

            "topic_progression_reasoning":
                True,

            "information_gain_reasoning":
                True,

            "cross_document_claim_comparison":
                True,

            "cross_document_relation_inference":
                True,
        },

        "relationship_families": [
            "SHARED_TOPIC",
            "SEMANTIC_OVERLAP",
            "COMPLEMENTARY",
            "PARENT_CHILD",
            "PREREQUISITE",
            "CAUSE_EFFECT",
            "PROBLEM_SOLUTION",
            "CONDITION_TREATMENT",
            "SYMPTOM_DIAGNOSIS",
            "DIAGNOSIS_TREATMENT",
            "GENERAL_SPECIFIC",
            "SEQUENCE",
            "TEMPORAL",
            "SUPPORTING_EVIDENCE",
            "COMPARISON",
            "CONTRADICTION",
            "POTENTIAL_DUPLICATION",
            "TOPIC_PROGRESSION",
            "CONTENT_GAP",
            "INFORMATION_GAIN",
        ],

        "evidence_requirements": {
            "document_identity_required":
                True,

            "source_profile_required":
                True,

            "retrieval_provenance_required":
                True,

            "retrieval_integrity_required":
                True,

            "semantic_evidence_required":
                True,

            "relationship_evidence_required":
                True,

            "reasoning_trace_required":
                True,

            "conflict_evidence_required":
                True,

            "uncertainty_evidence_required":
                True,

            "unsupported_relation_forbidden":
                True,

            "unsupported_fact_inference_forbidden":
                True,
        },

        "reasoning_scope_contract": {
            "minimum_documents":
                2,

            "same_workspace_required":
                True,

            "duplicate_article_identity_forbidden":
                True,

            "each_document_must_be_4.6.20K_certified":
                True,

            "document_set_must_be_explicit":
                True,

            "reasoning_scope_must_be_explicit":
                True,

            "reasoning_scope_mutation_forbidden":
                True,
        },

        "evidence_alignment_contract": {
            "align_by_canonical_identity":
                True,

            "align_by_semantic_concepts":
                True,

            "align_by_semantic_groups":
                True,

            "align_by_cross_layer_artifacts":
                True,

            "align_by_governed_state":
                True,

            "align_by_structural_indexes":
                True,

            "preserve_source_evidence":
                True,

            "invent_evidence":
                False,
        },

        "relationship_construction_contract": {
            "relationship_has_source_document":
                True,

            "relationship_has_target_document":
                True,

            "relationship_has_relationship_family":
                True,

            "relationship_has_evidence":
                True,

            "relationship_has_directionality":
                True,

            "relationship_has_confidence_state":
                True,

            "relationship_has_uncertainty_state":
                True,

            "relationship_has_provenance":
                True,

            "relationship_is_linking_decision":
                False,
        },

        "reasoning_execution_contract": {
            "reason_only_over_declared_document_set":
                True,

            "reason_only_over_aligned_evidence":
                True,

            "new_cross_document_relations_allowed":
                True,

            "new_cross_document_reasoning_allowed":
                True,

            "unsupported_new_facts_forbidden":
                True,

            "source_profile_mutation_forbidden":
                True,

            "retrieval_payload_mutation_forbidden":
                True,

            "semantic_memory_write_forbidden":
                True,

            "linking_decision_forbidden":
                True,
        },

        "conflict_guard_contract": {
            "detect_claim_conflicts":
                True,

            "detect_relation_conflicts":
                True,

            "detect_identity_conflicts":
                True,

            "detect_evidence_conflicts":
                True,

            "detect_scope_violations":
                True,

            "conflict_must_not_be_silently_resolved":
                True,

            "uncertainty_must_be_preserved":
                True,

            "conflict_evidence_trace_required":
                True,
        },

        "provenance_contract": {
            "source_phase":
                "4.6.20",

            "source_patch":
                "4.6.20K",

            "reasoning_phase":
                "4.6.21",

            "document_lineage_required":
                True,

            "relationship_lineage_required":
                True,

            "evidence_trace_required":
                True,

            "reasoning_trace_required":
                True,

            "result_digest_required":
                True,
        },

        "ownership_boundaries": {
            "profile_store":
                "4.6.19_PROFILE_STORE",

            "knowledge_retrieval":
                "4.6.20_KNOWLEDGE_RETRIEVAL",

            "cross_document_reasoning":
                "4.6.21_CROSS_DOCUMENT_REASONING",

            "ontology_alignment":
                "4.6.22_ONTOLOGY_ALIGNMENT",

            "semantic_memory":
                "4.6.28_SEMANTIC_MEMORY",

            "linking":
                "DOWNSTREAM_LINKING_PIPELINE",
        },

        "execution_contract": {
            "4.6.21A":
                "INSPECTION_ONLY",

            "4.6.21B":
                "ARCHITECTURE_DEFINITION_ONLY",

            "4.6.21C":
                "VALIDATION_ONLY",

            "4.6.21D":
                "DOCUMENT_SET_AND_SCOPE_CONTRACT_ONLY",

            "4.6.21E":
                "EVIDENCE_ALIGNMENT_ONLY",

            "4.6.21F":
                "RELATIONSHIP_CONSTRUCTION_ONLY",

            "4.6.21G":
                "CROSS_DOCUMENT_REASONING_EXECUTION",

            "4.6.21H":
                "INTEGRITY_AND_CONFLICT_GUARD",

            "4.6.21I":
                "PROVENANCE_AND_EVIDENCE_TRACE",

            "4.6.21J":
                "FINAL_RESULT_ASSEMBLY",

            "4.6.21K":
                "FULL_HARD_CERTIFICATION",
        },

        "architecture_status":
            "DEFINED",

        "cross_document_reasoning_performed":
            False,

        "source_profile_modified":
            False,

        "retrieval_payload_modified":
            False,

        "semantic_memory_written":
            False,

        "linking_decisions_performed":
            False,
    }

    return architecture


# =====================================================================
# PATCH 4.6.21C ? Reasoning Intake Validation
# =====================================================================

def validate_cross_document_reasoning_intake_v1(
    inspection_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Validate the 4.6.21 reasoning intake.

    C validates:
    - exact 4.6.21A inspection lifecycle,
    - exact 4.6.21B architecture authority,
    - certified 4.6.20K source preservation,
    - reasoning readiness and ownership,
    - pre-reasoning boundaries.

    C performs no cross-document reasoning.
    """

    from collections.abc import Mapping
    from copy import deepcopy

    if not isinstance(
        inspection_result,
        Mapping,
    ):
        raise CrossDocumentReasoningError(
            "inspection_result must be a mapping."
        )

    # -------------------------------------------------------------
    # Exact 4.6.21A lifecycle
    # -------------------------------------------------------------

    for field, expected in (
        (
            "schema_version",
            "cross_document_reasoning_input_inspection_result_v1",
        ),
        (
            "version",
            CROSS_DOCUMENT_REASONING_VERSION,
        ),
        (
            "phase",
            CROSS_DOCUMENT_REASONING_PHASE,
        ),
        (
            "patch",
            "4.6.21A",
        ),
        (
            "status",
            "CERTIFIED_KNOWLEDGE_RETRIEVAL_INPUT_INSPECTED",
        ),
        (
            "reasoning_policy",
            "CERTIFIED_KNOWLEDGE_RETRIEVAL_INPUT_ONLY",
        ),
        (
            "next_stage",
            "cross_document_reasoning_architecture_definition",
        ),
    ):

        if inspection_result.get(field) != expected:
            raise CrossDocumentReasoningError(
                f"Invalid 4.6.21A lifecycle field: {field}"
            )

    canonical_identity = inspection_result.get(
        "canonical_article_identity"
    )

    storage_identity = inspection_result.get(
        "storage_identity"
    )

    retrieval_query = inspection_result.get(
        "retrieval_query"
    )

    verified_payload = inspection_result.get(
        "verified_retrieval_payload"
    )

    projection_contract = inspection_result.get(
        "projection_contract"
    )

    retrieval_view = inspection_result.get(
        "retrieval_view"
    )

    retrieval_provenance = inspection_result.get(
        "retrieval_provenance"
    )

    certified_retrieval = inspection_result.get(
        "certified_knowledge_retrieval_result"
    )

    source_envelope = inspection_result.get(
        "source_certified_knowledge_retrieval_envelope"
    )

    inspection = inspection_result.get(
        "inspection"
    )

    boundaries = inspection_result.get(
        "processing_boundaries"
    )

    for name, value in (
        ("canonical_article_identity", canonical_identity),
        ("storage_identity", storage_identity),
        ("retrieval_query", retrieval_query),
        ("verified_retrieval_payload", verified_payload),
        ("projection_contract", projection_contract),
        ("retrieval_view", retrieval_view),
        ("retrieval_provenance", retrieval_provenance),
        (
            "certified_knowledge_retrieval_result",
            certified_retrieval,
        ),
        (
            "source_certified_knowledge_retrieval_envelope",
            source_envelope,
        ),
        ("inspection", inspection),
        ("processing_boundaries", boundaries),
    ):

        if not isinstance(
            value,
            Mapping,
        ):
            raise CrossDocumentReasoningError(
                name + " is missing."
            )

    # -------------------------------------------------------------
    # Inspection authority
    # -------------------------------------------------------------

    if inspection.get(
        "inspection_status"
    ) != "PASSED":
        raise CrossDocumentReasoningError(
            "4.6.21A inspection did not pass."
        )

    if inspection.get(
        "inspection_scope"
    ) != "CERTIFIED_4.6.20K_KNOWLEDGE_RETRIEVAL_INPUT":
        raise CrossDocumentReasoningError(
            "4.6.21A inspection scope drifted."
        )

    if inspection.get(
        "source_phase"
    ) != "4.6.20":
        raise CrossDocumentReasoningError(
            "Inspection source phase drifted."
        )

    if inspection.get(
        "source_patch"
    ) != "4.6.20K":
        raise CrossDocumentReasoningError(
            "Inspection source patch drifted."
        )

    for field in (
        "knowledge_retrieval_certified",
        "source_profile_certified",
        "source_profile_immutable",
        "retrieval_integrity_verified",
        "retrieval_provenance_complete",
        "cross_document_reasoning_ready",
        "cross_document_reasoning_owner_confirmed",
        "semantic_memory_deferred",
    ):

        if inspection.get(field) is not True:
            raise CrossDocumentReasoningError(
                f"Required inspection field is not True: {field}"
            )

    if inspection.get(
        "cross_document_reasoning_performed"
    ) is not False:
        raise CrossDocumentReasoningError(
            "Cross-document reasoning occurred before intake validation."
        )

    # -------------------------------------------------------------
    # Architecture authority
    # -------------------------------------------------------------

    architecture = define_cross_document_reasoning_architecture_v1()

    if architecture.get(
        "architecture_status"
    ) != "DEFINED":
        raise CrossDocumentReasoningError(
            "Cross-Document Reasoning architecture is not defined."
        )

    if architecture.get(
        "owner"
    ) != "4.6.21_CROSS_DOCUMENT_REASONING":
        raise CrossDocumentReasoningError(
            "Cross-Document Reasoning owner drifted."
        )

    if architecture.get(
        "source_owner"
    ) != "4.6.20_KNOWLEDGE_RETRIEVAL":
        raise CrossDocumentReasoningError(
            "Knowledge Retrieval source owner drifted."
        )

    if architecture.get(
        "next_owner"
    ) != "4.6.22_ONTOLOGY_ALIGNMENT":
        raise CrossDocumentReasoningError(
            "Ontology Alignment owner drifted."
        )

    if architecture.get(
        "semantic_memory_owner"
    ) != "4.6.28_SEMANTIC_MEMORY":
        raise CrossDocumentReasoningError(
            "Semantic Memory owner drifted."
        )

    if architecture.get(
        "input_contract"
    ) != "certified_knowledge_retrieval_result_v1":
        raise CrossDocumentReasoningError(
            "Architecture input contract drifted."
        )

    if architecture.get(
        "output_contract"
    ) != "certified_cross_document_reasoning_result_v1":
        raise CrossDocumentReasoningError(
            "Architecture output contract drifted."
        )

    execution_contract = architecture.get(
        "execution_contract"
    )

    if not isinstance(
        execution_contract,
        Mapping,
    ):
        raise CrossDocumentReasoningError(
            "Architecture execution contract is missing."
        )

    if execution_contract.get(
        "4.6.21C"
    ) != "VALIDATION_ONLY":
        raise CrossDocumentReasoningError(
            "4.6.21C execution contract drifted."
        )

    # -------------------------------------------------------------
    # Required architecture principles
    # -------------------------------------------------------------

    principles = architecture.get(
        "principles"
    )

    scope_contract = architecture.get(
        "reasoning_scope_contract"
    )

    evidence_requirements = architecture.get(
        "evidence_requirements"
    )

    reasoning_execution = architecture.get(
        "reasoning_execution_contract"
    )

    ownership = architecture.get(
        "ownership_boundaries"
    )

    for name, value in (
        ("principles", principles),
        ("reasoning_scope_contract", scope_contract),
        ("evidence_requirements", evidence_requirements),
        ("reasoning_execution_contract", reasoning_execution),
        ("ownership_boundaries", ownership),
    ):

        if not isinstance(
            value,
            Mapping,
        ):
            raise CrossDocumentReasoningError(
                f"Architecture {name} is missing."
            )

    for field in (
        "certified_retrieval_inputs_only",
        "minimum_two_documents_required",
        "source_profiles_immutable",
        "retrieval_payloads_immutable",
        "evidence_bound_reasoning",
        "reasoning_must_be_traceable",
        "document_identity_preserved",
        "workspace_scope_preserved",
        "cross_document_claims_require_evidence",
        "conflicts_must_be_explicit",
        "uncertainty_must_be_explicit",
        "no_source_profile_rewrite",
        "no_retrieval_payload_rewrite",
        "no_profile_store_write",
        "no_semantic_memory_write",
        "no_linking_decision",
    ):

        if principles.get(field) is not True:
            raise CrossDocumentReasoningError(
                f"Required architecture principle is not True: {field}"
            )

    if scope_contract.get(
        "minimum_documents"
    ) != 2:
        raise CrossDocumentReasoningError(
            "Minimum document contract must be exactly 2."
        )

    for field in (
        "same_workspace_required",
        "duplicate_article_identity_forbidden",
        "each_document_must_be_4.6.20K_certified",
        "document_set_must_be_explicit",
        "reasoning_scope_must_be_explicit",
        "reasoning_scope_mutation_forbidden",
    ):

        if scope_contract.get(field) is not True:
            raise CrossDocumentReasoningError(
                f"Required reasoning scope field is not True: {field}"
            )

    for field in (
        "document_identity_required",
        "source_profile_required",
        "retrieval_provenance_required",
        "retrieval_integrity_required",
        "semantic_evidence_required",
        "relationship_evidence_required",
        "reasoning_trace_required",
        "unsupported_relation_forbidden",
        "unsupported_fact_inference_forbidden",
    ):

        if evidence_requirements.get(field) is not True:
            raise CrossDocumentReasoningError(
                f"Required evidence field is not True: {field}"
            )

    for field in (
        "reason_only_over_declared_document_set",
        "reason_only_over_aligned_evidence",
        "new_cross_document_relations_allowed",
        "new_cross_document_reasoning_allowed",
        "unsupported_new_facts_forbidden",
        "source_profile_mutation_forbidden",
        "retrieval_payload_mutation_forbidden",
        "semantic_memory_write_forbidden",
        "linking_decision_forbidden",
    ):

        if reasoning_execution.get(field) is not True:
            raise CrossDocumentReasoningError(
                f"Required execution field is not True: {field}"
            )

    # -------------------------------------------------------------
    # Certified retrieval authority
    # -------------------------------------------------------------

    if certified_retrieval.get(
        "full_knowledge_retrieval_certified"
    ) is not True:
        raise CrossDocumentReasoningError(
            "Knowledge Retrieval final result is not certified."
        )

    if certified_retrieval.get(
        "certification_status"
    ) != "CERTIFIED":
        raise CrossDocumentReasoningError(
            "Knowledge Retrieval certification status drifted."
        )

    if certified_retrieval.get(
        "next_owner"
    ) != "4.6.21_CROSS_DOCUMENT_REASONING":
        raise CrossDocumentReasoningError(
            "Knowledge Retrieval next owner drifted."
        )

    if certified_retrieval.get(
        "cross_document_reasoning_ready"
    ) is not True:
        raise CrossDocumentReasoningError(
            "Knowledge Retrieval result is not reasoning-ready."
        )

    for field in (
        "cross_document_reasoning_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if certified_retrieval.get(field) is not False:
            raise CrossDocumentReasoningError(
                f"Forbidden certified retrieval field is not False: {field}"
            )

    # -------------------------------------------------------------
    # Identity / lineage consistency
    # -------------------------------------------------------------

    if certified_retrieval.get(
        "canonical_article_identity"
    ) != canonical_identity:
        raise CrossDocumentReasoningError(
            "Canonical identity drifted."
        )

    if certified_retrieval.get(
        "storage_key"
    ) != storage_identity.get(
        "storage_key"
    ):
        raise CrossDocumentReasoningError(
            "Storage identity drifted."
        )

    if certified_retrieval.get(
        "retrieval_query_id"
    ) != retrieval_query.get(
        "retrieval_query_id"
    ):
        raise CrossDocumentReasoningError(
            "Retrieval query identity drifted."
        )

    if certified_retrieval.get(
        "retrieval_payload_id"
    ) != verified_payload.get(
        "retrieval_payload_id"
    ):
        raise CrossDocumentReasoningError(
            "Retrieval payload identity drifted."
        )

    if certified_retrieval.get(
        "projection_id"
    ) != projection_contract.get(
        "projection_id"
    ):
        raise CrossDocumentReasoningError(
            "Projection identity drifted."
        )

    if certified_retrieval.get(
        "provenance_id"
    ) != retrieval_provenance.get(
        "provenance_id"
    ):
        raise CrossDocumentReasoningError(
            "Retrieval provenance identity drifted."
        )

    source_profile = certified_retrieval.get(
        "source_certified_semantic_article_profile"
    )

    if not isinstance(
        source_profile,
        Mapping,
    ):
        raise CrossDocumentReasoningError(
            "Certified semantic source profile is missing."
        )

    if source_profile.get(
        "profile_certified"
    ) is not True:
        raise CrossDocumentReasoningError(
            "Semantic source profile is not certified."
        )

    if source_profile.get(
        "profile_persisted"
    ) is not False:
        raise CrossDocumentReasoningError(
            "Semantic source profile immutability drifted."
        )

    if source_profile.get(
        "profile_identity",
        {},
    ).get(
        "canonical_article_identity"
    ) != canonical_identity:
        raise CrossDocumentReasoningError(
            "Semantic source profile identity drifted."
        )

    # -------------------------------------------------------------
    # A processing boundaries
    # -------------------------------------------------------------

    for field in (
        "certified_knowledge_retrieval_input_inspected",
        "certified_knowledge_retrieval_input_preserved",
        "source_profile_preserved",
        "canonical_identity_preserved",
        "storage_identity_preserved",
        "retrieval_lineage_preserved",
    ):

        if boundaries.get(field) is not True:
            raise CrossDocumentReasoningError(
                f"Required 4.6.21A boundary is not True: {field}"
            )

    for field in (
        "cross_document_reasoning_architecture_defined",
        "reasoning_intake_validation_performed",
        "document_set_scope_defined",
        "cross_document_evidence_alignment_performed",
        "cross_document_relationships_constructed",
        "cross_document_reasoning_performed",
        "reasoning_integrity_verification_performed",
        "reasoning_provenance_built",
        "final_cross_document_reasoning_result_built",
        "full_cross_document_reasoning_certification_performed",
        "source_profile_modified",
        "retrieval_payload_modified",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if boundaries.get(field) is not False:
            raise CrossDocumentReasoningError(
                f"Forbidden 4.6.21A boundary is not False: {field}"
            )

    intake_validation = {
        "validation_status":
            "VALIDATED",

        "validation_scope":
            "CERTIFIED_CROSS_DOCUMENT_REASONING_INTAKE",

        "source_inspection_patch":
            "4.6.21A",

        "architecture_patch":
            "4.6.21B",

        "knowledge_retrieval_source_phase":
            "4.6.20",

        "knowledge_retrieval_source_patch":
            "4.6.20K",

        "certified_retrieval_input_validated":
            True,

        "canonical_identity_validated":
            True,

        "storage_identity_validated":
            True,

        "retrieval_query_identity_validated":
            True,

        "retrieval_payload_identity_validated":
            True,

        "projection_identity_validated":
            True,

        "retrieval_provenance_identity_validated":
            True,

        "source_profile_certification_validated":
            True,

        "source_profile_immutability_validated":
            True,

        "retrieval_integrity_validated":
            True,

        "reasoning_readiness_validated":
            True,

        "reasoning_owner_validated":
            True,

        "architecture_validated":
            True,

        "minimum_document_requirement_preserved":
            True,

        "same_workspace_requirement_preserved":
            True,

        "evidence_bound_reasoning_required":
            True,

        "semantic_memory_deferred":
            True,

        "ontology_alignment_deferred":
            True,

        "linking_deferred":
            True,

        "document_set_defined":
            False,

        "reasoning_scope_defined":
            False,

        "evidence_alignment_performed":
            False,

        "relationship_construction_performed":
            False,

        "cross_document_reasoning_performed":
            False,
    }

    return {
        "schema_version":
            "cross_document_reasoning_intake_validation_result_v1",

        "version":
            CROSS_DOCUMENT_REASONING_VERSION,

        "phase":
            CROSS_DOCUMENT_REASONING_PHASE,

        "patch":
            "4.6.21C",

        "status":
            "CROSS_DOCUMENT_REASONING_INTAKE_VALIDATED",

        "canonical_article_identity":
            deepcopy(
                dict(canonical_identity)
            ),

        "storage_identity":
            deepcopy(
                dict(storage_identity)
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

        "certified_knowledge_retrieval_result":
            deepcopy(
                dict(certified_retrieval)
            ),

        "intake_validation":
            intake_validation,

        "cross_document_reasoning_architecture":
            deepcopy(
                architecture
            ),

        "source_input_inspection_result":
            deepcopy(
                dict(inspection_result)
            ),

        "processing_boundaries": {
            "certified_knowledge_retrieval_input_inspection_preserved":
                True,

            "cross_document_reasoning_architecture_preserved":
                True,

            "reasoning_intake_validation_performed":
                True,

            "certified_retrieval_input_preserved":
                True,

            "source_profile_preserved":
                True,

            "canonical_identity_preserved":
                True,

            "storage_identity_preserved":
                True,

            "retrieval_lineage_preserved":
                True,

            "document_set_scope_defined":
                False,

            "cross_document_evidence_alignment_performed":
                False,

            "cross_document_relationships_constructed":
                False,

            "cross_document_reasoning_performed":
                False,

            "reasoning_integrity_verification_performed":
                False,

            "reasoning_provenance_built":
                False,

            "final_cross_document_reasoning_result_built":
                False,

            "full_cross_document_reasoning_certification_performed":
                False,

            "source_profile_modified":
                False,

            "retrieval_payload_modified":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,
        },

        "reasoning_policy":
            "VALIDATION_ONLY_NO_CROSS_DOCUMENT_REASONING",

        "next_stage":
            "document_set_reasoning_scope_contract",
    }


# =====================================================================
# PATCH 4.6.21D ? Document Set / Reasoning Scope Contract
# =====================================================================

def build_cross_document_reasoning_scope_contract_v1(
    intake_result: dict[str, Any],
    document_inputs: list[dict[str, Any]],
    reasoning_scope: dict[str, Any],
) -> dict[str, Any]:
    """
    Define the immutable multi-document reasoning set and scope.

    D performs contract construction only.

    No evidence alignment, relationship construction, or
    cross-document reasoning is performed here.
    """

    from collections.abc import Mapping
    from copy import deepcopy
    import hashlib
    import json

    if not isinstance(
        intake_result,
        Mapping,
    ):
        raise CrossDocumentReasoningError(
            "intake_result must be a mapping."
        )

    if not isinstance(
        document_inputs,
        list,
    ):
        raise CrossDocumentReasoningError(
            "document_inputs must be a list."
        )

    if not isinstance(
        reasoning_scope,
        Mapping,
    ):
        raise CrossDocumentReasoningError(
            "reasoning_scope must be a mapping."
        )

    # -------------------------------------------------------------
    # Exact 4.6.21C lifecycle
    # -------------------------------------------------------------

    for field, expected in (
        (
            "schema_version",
            "cross_document_reasoning_intake_validation_result_v1",
        ),
        (
            "version",
            CROSS_DOCUMENT_REASONING_VERSION,
        ),
        (
            "phase",
            CROSS_DOCUMENT_REASONING_PHASE,
        ),
        (
            "patch",
            "4.6.21C",
        ),
        (
            "status",
            "CROSS_DOCUMENT_REASONING_INTAKE_VALIDATED",
        ),
        (
            "reasoning_policy",
            "VALIDATION_ONLY_NO_CROSS_DOCUMENT_REASONING",
        ),
        (
            "next_stage",
            "document_set_reasoning_scope_contract",
        ),
    ):

        if intake_result.get(field) != expected:
            raise CrossDocumentReasoningError(
                f"Invalid 4.6.21C lifecycle field: {field}"
            )

    intake_validation = intake_result.get(
        "intake_validation"
    )

    architecture = intake_result.get(
        "cross_document_reasoning_architecture"
    )

    anchor_identity = intake_result.get(
        "canonical_article_identity"
    )

    anchor_certified = intake_result.get(
        "certified_knowledge_retrieval_result"
    )

    boundaries = intake_result.get(
        "processing_boundaries"
    )

    for name, value in (
        ("intake_validation", intake_validation),
        ("cross_document_reasoning_architecture", architecture),
        ("canonical_article_identity", anchor_identity),
        ("certified_knowledge_retrieval_result", anchor_certified),
        ("processing_boundaries", boundaries),
    ):

        if not isinstance(
            value,
            Mapping,
        ):
            raise CrossDocumentReasoningError(
                name + " is missing."
            )

    # -------------------------------------------------------------
    # C validation authority
    # -------------------------------------------------------------

    if intake_validation.get(
        "validation_status"
    ) != "VALIDATED":
        raise CrossDocumentReasoningError(
            "4.6.21C intake is not VALIDATED."
        )

    if intake_validation.get(
        "validation_scope"
    ) != "CERTIFIED_CROSS_DOCUMENT_REASONING_INTAKE":
        raise CrossDocumentReasoningError(
            "4.6.21C validation scope drifted."
        )

    for field in (
        "certified_retrieval_input_validated",
        "canonical_identity_validated",
        "storage_identity_validated",
        "retrieval_query_identity_validated",
        "retrieval_payload_identity_validated",
        "projection_identity_validated",
        "retrieval_provenance_identity_validated",
        "source_profile_certification_validated",
        "source_profile_immutability_validated",
        "retrieval_integrity_validated",
        "reasoning_readiness_validated",
        "reasoning_owner_validated",
        "architecture_validated",
        "minimum_document_requirement_preserved",
        "same_workspace_requirement_preserved",
        "evidence_bound_reasoning_required",
        "semantic_memory_deferred",
        "ontology_alignment_deferred",
        "linking_deferred",
    ):

        if intake_validation.get(field) is not True:
            raise CrossDocumentReasoningError(
                f"Required C validation field is not True: {field}"
            )

    for field in (
        "document_set_defined",
        "reasoning_scope_defined",
        "evidence_alignment_performed",
        "relationship_construction_performed",
        "cross_document_reasoning_performed",
    ):

        if intake_validation.get(field) is not False:
            raise CrossDocumentReasoningError(
                f"Forbidden C validation field is not False: {field}"
            )

    # -------------------------------------------------------------
    # Architecture authority
    # -------------------------------------------------------------

    if architecture.get(
        "architecture_status"
    ) != "DEFINED":
        raise CrossDocumentReasoningError(
            "Cross-Document Reasoning architecture is not defined."
        )

    scope_arch = architecture.get(
        "reasoning_scope_contract"
    )

    execution_contract = architecture.get(
        "execution_contract"
    )

    supported_reasoning = architecture.get(
        "supported_reasoning"
    )

    relationship_families = architecture.get(
        "relationship_families"
    )

    for name, value in (
        ("reasoning_scope_contract", scope_arch),
        ("execution_contract", execution_contract),
        ("supported_reasoning", supported_reasoning),
    ):

        if not isinstance(
            value,
            Mapping,
        ):
            raise CrossDocumentReasoningError(
                f"Architecture {name} is missing."
            )

    if not isinstance(
        relationship_families,
        list,
    ):
        raise CrossDocumentReasoningError(
            "Architecture relationship families are missing."
        )

    if execution_contract.get(
        "4.6.21D"
    ) != "DOCUMENT_SET_AND_SCOPE_CONTRACT_ONLY":
        raise CrossDocumentReasoningError(
            "4.6.21D execution contract drifted."
        )

    minimum_documents = scope_arch.get(
        "minimum_documents"
    )

    if minimum_documents != 2:
        raise CrossDocumentReasoningError(
            "Canonical minimum document count must be 2."
        )

    # -------------------------------------------------------------
    # Validate requested reasoning scope
    # -------------------------------------------------------------

    scope_name = reasoning_scope.get(
        "scope_name"
    )

    requested_families = reasoning_scope.get(
        "relationship_families"
    )

    if not isinstance(
        scope_name,
        str,
    ) or not scope_name.strip():
        raise CrossDocumentReasoningError(
            "reasoning_scope.scope_name must be a non-empty string."
        )

    if not isinstance(
        requested_families,
        list,
    ) or not requested_families:
        raise CrossDocumentReasoningError(
            "reasoning_scope.relationship_families must be a non-empty list."
        )

    if any(
        not isinstance(item, str) or not item
        for item in requested_families
    ):
        raise CrossDocumentReasoningError(
            "Requested relationship families must be non-empty strings."
        )

    if len(
        requested_families
    ) != len(
        set(requested_families)
    ):
        raise CrossDocumentReasoningError(
            "Duplicate relationship families are forbidden."
        )

    for family in requested_families:

        if family not in relationship_families:
            raise CrossDocumentReasoningError(
                f"Unsupported relationship family requested: {family}"
            )

    include_claim_comparison = reasoning_scope.get(
        "include_claim_comparison",
        False,
    )

    include_content_gap_reasoning = reasoning_scope.get(
        "include_content_gap_reasoning",
        False,
    )

    include_information_gain_reasoning = reasoning_scope.get(
        "include_information_gain_reasoning",
        False,
    )

    for name, value in (
        (
            "include_claim_comparison",
            include_claim_comparison,
        ),
        (
            "include_content_gap_reasoning",
            include_content_gap_reasoning,
        ),
        (
            "include_information_gain_reasoning",
            include_information_gain_reasoning,
        ),
    ):

        if not isinstance(value, bool):
            raise CrossDocumentReasoningError(
                f"{name} must be boolean."
            )

    if (
        include_claim_comparison
        and supported_reasoning.get(
            "cross_document_claim_comparison"
        ) is not True
    ):
        raise CrossDocumentReasoningError(
            "Claim comparison is not supported."
        )

    if (
        include_content_gap_reasoning
        and supported_reasoning.get(
            "content_gap_reasoning"
        ) is not True
    ):
        raise CrossDocumentReasoningError(
            "Content-gap reasoning is not supported."
        )

    if (
        include_information_gain_reasoning
        and supported_reasoning.get(
            "information_gain_reasoning"
        ) is not True
    ):
        raise CrossDocumentReasoningError(
            "Information-gain reasoning is not supported."
        )

    # -------------------------------------------------------------
    # Validate certified document inputs
    # -------------------------------------------------------------

    if len(document_inputs) < minimum_documents:
        raise CrossDocumentReasoningError(
            "At least two certified documents are required."
        )

    validated_documents = []

    workspace_ids = set()
    article_ids = set()

    for index, document in enumerate(
        document_inputs
    ):

        if not isinstance(
            document,
            Mapping,
        ):
            raise CrossDocumentReasoningError(
                f"document_inputs[{index}] must be a mapping."
            )

        for field, expected in (
            (
                "schema_version",
                "certified_knowledge_retrieval_result_v1",
            ),
            (
                "version",
                "knowledge_retrieval_v1",
            ),
            (
                "phase",
                "4.6.20",
            ),
            (
                "patch",
                "4.6.20K",
            ),
            (
                "status",
                "KNOWLEDGE_RETRIEVAL_CERTIFIED",
            ),
            (
                "retrieval_policy",
                "FULL_KNOWLEDGE_RETRIEVAL_CERTIFIED",
            ),
            (
                "next_stage",
                "cross_document_reasoning",
            ),
        ):

            if document.get(field) != expected:
                raise CrossDocumentReasoningError(
                    f"Document {index} failed certified retrieval field: {field}"
                )

        identity = document.get(
            "canonical_article_identity"
        )

        storage_identity = document.get(
            "storage_identity"
        )

        certified_final = document.get(
            "certified_final_knowledge_retrieval_result"
        )

        certification = document.get(
            "full_knowledge_retrieval_certification"
        )

        document_boundaries = document.get(
            "processing_boundaries"
        )

        for name, value in (
            ("canonical_article_identity", identity),
            ("storage_identity", storage_identity),
            (
                "certified_final_knowledge_retrieval_result",
                certified_final,
            ),
            (
                "full_knowledge_retrieval_certification",
                certification,
            ),
            ("processing_boundaries", document_boundaries),
        ):

            if not isinstance(
                value,
                Mapping,
            ):
                raise CrossDocumentReasoningError(
                    f"Document {index} {name} is missing."
                )

        workspace_id = identity.get(
            "workspace_id"
        )

        article_id = identity.get(
            "article_id"
        )

        if not isinstance(
            workspace_id,
            str,
        ) or not workspace_id:
            raise CrossDocumentReasoningError(
                f"Document {index} workspace_id is invalid."
            )

        if not isinstance(
            article_id,
            str,
        ) or not article_id:
            raise CrossDocumentReasoningError(
                f"Document {index} article_id is invalid."
            )

        if article_id in article_ids:
            raise CrossDocumentReasoningError(
                f"Duplicate article identity detected: {article_id}"
            )

        article_ids.add(article_id)
        workspace_ids.add(workspace_id)

        if certification.get(
            "certification_status"
        ) != "CERTIFIED":
            raise CrossDocumentReasoningError(
                f"Document {index} is not certified."
            )

        if certification.get(
            "certification_scope"
        ) != "FULL_KNOWLEDGE_RETRIEVAL_PIPELINE":
            raise CrossDocumentReasoningError(
                f"Document {index} certification scope drifted."
            )

        if certification.get(
            "cross_document_reasoning_ready"
        ) is not True:
            raise CrossDocumentReasoningError(
                f"Document {index} is not reasoning-ready."
            )

        if certified_final.get(
            "full_knowledge_retrieval_certified"
        ) is not True:
            raise CrossDocumentReasoningError(
                f"Document {index} final retrieval result is not certified."
            )

        if certified_final.get(
            "next_owner"
        ) != "4.6.21_CROSS_DOCUMENT_REASONING":
            raise CrossDocumentReasoningError(
                f"Document {index} owner handoff drifted."
            )

        if certified_final.get(
            "canonical_article_identity"
        ) != identity:
            raise CrossDocumentReasoningError(
                f"Document {index} canonical identity drifted."
            )

        if certified_final.get(
            "storage_key"
        ) != storage_identity.get(
            "storage_key"
        ):
            raise CrossDocumentReasoningError(
                f"Document {index} storage identity drifted."
            )

        source_profile = certified_final.get(
            "source_certified_semantic_article_profile"
        )

        if not isinstance(
            source_profile,
            Mapping,
        ):
            raise CrossDocumentReasoningError(
                f"Document {index} source profile is missing."
            )

        if source_profile.get(
            "profile_certified"
        ) is not True:
            raise CrossDocumentReasoningError(
                f"Document {index} source profile is not certified."
            )

        if source_profile.get(
            "profile_persisted"
        ) is not False:
            raise CrossDocumentReasoningError(
                f"Document {index} source profile immutability drifted."
            )

        if source_profile.get(
            "profile_identity",
            {},
        ).get(
            "canonical_article_identity"
        ) != identity:
            raise CrossDocumentReasoningError(
                f"Document {index} source profile identity drifted."
            )

        for field in (
            "cross_document_reasoning_performed",
            "semantic_memory_written",
            "linking_decisions_performed",
        ):

            if certified_final.get(field) is not False:
                raise CrossDocumentReasoningError(
                    f"Document {index} forbidden state already true: {field}"
                )

        if document_boundaries.get(
            "knowledge_retrieval_certified"
        ) is not True:
            raise CrossDocumentReasoningError(
                f"Document {index} retrieval certification boundary missing."
            )

        if document_boundaries.get(
            "source_profile_preserved"
        ) is not True:
            raise CrossDocumentReasoningError(
                f"Document {index} source profile boundary missing."
            )

        for field in (
            "cross_document_reasoning_performed",
            "semantic_memory_written",
            "linking_decisions_performed",
        ):

            if document_boundaries.get(field) is not False:
                raise CrossDocumentReasoningError(
                    f"Document {index} forbidden boundary already true: {field}"
                )

        validated_documents.append(
            {
                "document_index":
                    index,

                "workspace_id":
                    workspace_id,

                "article_id":
                    article_id,

                "canonical_article_identity":
                    deepcopy(dict(identity)),

                "storage_key":
                    storage_identity[
                        "storage_key"
                    ],

                "retrieval_query_id":
                    certified_final.get(
                        "retrieval_query_id"
                    ),

                "retrieval_payload_id":
                    certified_final.get(
                        "retrieval_payload_id"
                    ),

                "projection_id":
                    certified_final.get(
                        "projection_id"
                    ),

                "provenance_id":
                    certified_final.get(
                        "provenance_id"
                    ),

                "profile_payload_hash":
                    certified_final.get(
                        "profile_payload_hash"
                    ),

                "profile_payload_byte_length":
                    certified_final.get(
                        "profile_payload_byte_length"
                    ),

                "knowledge_retrieval_certified":
                    True,

                "source_profile_certified":
                    True,

                "source_profile_immutable":
                    True,

                "retrieval_integrity_verified":
                    certified_final.get(
                        "retrieval_integrity_verified"
                    )
                    is True,

                "cross_document_reasoning_ready":
                    True,
            }
        )

    if len(workspace_ids) != 1:
        raise CrossDocumentReasoningError(
            "All documents must belong to the same workspace."
        )

    workspace_id = next(
        iter(workspace_ids)
    )

    if anchor_identity.get(
        "workspace_id"
    ) != workspace_id:
        raise CrossDocumentReasoningError(
            "Validated intake workspace differs from document set workspace."
        )

    anchor_article_id = anchor_identity.get(
        "article_id"
    )

    if anchor_article_id not in article_ids:
        raise CrossDocumentReasoningError(
            "Validated anchor document must be included in document_inputs."
        )

    # -------------------------------------------------------------
    # C processing-boundary authority
    # -------------------------------------------------------------

    for field in (
        "certified_knowledge_retrieval_input_inspection_preserved",
        "cross_document_reasoning_architecture_preserved",
        "reasoning_intake_validation_performed",
        "certified_retrieval_input_preserved",
        "source_profile_preserved",
        "canonical_identity_preserved",
        "storage_identity_preserved",
        "retrieval_lineage_preserved",
    ):

        if boundaries.get(field) is not True:
            raise CrossDocumentReasoningError(
                f"Required 4.6.21C boundary is not True: {field}"
            )

    for field in (
        "document_set_scope_defined",
        "cross_document_evidence_alignment_performed",
        "cross_document_relationships_constructed",
        "cross_document_reasoning_performed",
        "reasoning_integrity_verification_performed",
        "reasoning_provenance_built",
        "final_cross_document_reasoning_result_built",
        "full_cross_document_reasoning_certification_performed",
        "source_profile_modified",
        "retrieval_payload_modified",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if boundaries.get(field) is not False:
            raise CrossDocumentReasoningError(
                f"Forbidden 4.6.21C boundary is not False: {field}"
            )

    # -------------------------------------------------------------
    # Deterministic document-set identity
    # -------------------------------------------------------------

    canonical_document_identity_set = sorted(
        [
            {
                "workspace_id":
                    item["workspace_id"],

                "article_id":
                    item["article_id"],

                "storage_key":
                    item["storage_key"],

                "retrieval_payload_id":
                    item["retrieval_payload_id"],

                "profile_payload_hash":
                    item["profile_payload_hash"],
            }
            for item in validated_documents
        ],
        key=lambda item: (
            item["workspace_id"],
            item["article_id"],
        ),
    )

    document_set_material = {
        "cross_document_reasoning_version":
            CROSS_DOCUMENT_REASONING_VERSION,

        "workspace_id":
            workspace_id,

        "documents":
            canonical_document_identity_set,
    }

    document_set_json = json.dumps(
        document_set_material,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    document_set_digest = hashlib.sha256(
        document_set_json.encode("utf-8")
    ).hexdigest()

    document_set_id = (
        "cdrset:v1:"
        + document_set_digest[:32]
    )

    # -------------------------------------------------------------
    # Deterministic reasoning-scope identity
    # -------------------------------------------------------------

    canonical_requested_families = [
        family
        for family in relationship_families
        if family in requested_families
    ]

    scope_material = {
        "document_set_id":
            document_set_id,

        "scope_name":
            scope_name.strip(),

        "relationship_families":
            canonical_requested_families,

        "include_claim_comparison":
            include_claim_comparison,

        "include_content_gap_reasoning":
            include_content_gap_reasoning,

        "include_information_gain_reasoning":
            include_information_gain_reasoning,
    }

    scope_json = json.dumps(
        scope_material,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    scope_digest = hashlib.sha256(
        scope_json.encode("utf-8")
    ).hexdigest()

    reasoning_scope_id = (
        "cdrscope:v1:"
        + scope_digest[:32]
    )

    document_set_contract = {
        "document_set_schema":
            "cross_document_reasoning_document_set_v1",

        "document_set_version":
            "v1",

        "document_set_id":
            document_set_id,

        "document_set_digest":
            document_set_digest,

        "document_set_digest_algorithm":
            "SHA256",

        "document_count":
            len(validated_documents),

        "minimum_document_requirement":
            minimum_documents,

        "workspace_id":
            workspace_id,

        "anchor_article_id":
            anchor_article_id,

        "article_ids":
            [
                item["article_id"]
                for item in sorted(
                    validated_documents,
                    key=lambda item: item["article_id"],
                )
            ],

        "documents":
            deepcopy(validated_documents),

        "all_documents_4.6.20K_certified":
            True,

        "same_workspace_validated":
            True,

        "duplicate_article_identity_absent":
            True,

        "anchor_document_included":
            True,

        "source_profiles_immutable":
            True,

        "retrieval_payloads_immutable":
            True,
    }

    reasoning_scope_contract = {
        "reasoning_scope_schema":
            "cross_document_reasoning_scope_v1",

        "reasoning_scope_version":
            "v1",

        "reasoning_scope_id":
            reasoning_scope_id,

        "reasoning_scope_digest":
            scope_digest,

        "reasoning_scope_digest_algorithm":
            "SHA256",

        "scope_name":
            scope_name.strip(),

        "document_set_id":
            document_set_id,

        "relationship_families":
            canonical_requested_families,

        "include_claim_comparison":
            include_claim_comparison,

        "include_content_gap_reasoning":
            include_content_gap_reasoning,

        "include_information_gain_reasoning":
            include_information_gain_reasoning,

        "scope_explicit":
            True,

        "scope_locked":
            True,

        "evidence_bound":
            True,

        "read_only":
            True,

        "evidence_alignment_performed":
            False,

        "relationship_construction_performed":
            False,

        "cross_document_reasoning_performed":
            False,

        "semantic_memory_written":
            False,

        "linking_decisions_performed":
            False,
    }

    return {
        "schema_version":
            "cross_document_reasoning_scope_contract_result_v1",

        "version":
            CROSS_DOCUMENT_REASONING_VERSION,

        "phase":
            CROSS_DOCUMENT_REASONING_PHASE,

        "patch":
            "4.6.21D",

        "status":
            "CROSS_DOCUMENT_REASONING_SCOPE_DEFINED",

        "workspace_id":
            workspace_id,

        "anchor_canonical_article_identity":
            deepcopy(
                dict(anchor_identity)
            ),

        "document_set_contract":
            document_set_contract,

        "reasoning_scope_contract":
            reasoning_scope_contract,

        "cross_document_reasoning_architecture":
            deepcopy(
                dict(architecture)
            ),

        "source_intake_validation_result":
            deepcopy(
                dict(intake_result)
            ),

        "source_certified_document_inputs":
            deepcopy(
                document_inputs
            ),

        "processing_boundaries": {
            "reasoning_intake_validation_preserved":
                True,

            "cross_document_reasoning_architecture_preserved":
                True,

            "certified_document_inputs_preserved":
                True,

            "document_set_scope_defined":
                True,

            "same_workspace_validated":
                True,

            "minimum_document_requirement_validated":
                True,

            "duplicate_article_identity_rejected":
                True,

            "source_profiles_preserved":
                True,

            "retrieval_payloads_preserved":
                True,

            "cross_document_evidence_alignment_performed":
                False,

            "cross_document_relationships_constructed":
                False,

            "cross_document_reasoning_performed":
                False,

            "reasoning_integrity_verification_performed":
                False,

            "reasoning_provenance_built":
                False,

            "final_cross_document_reasoning_result_built":
                False,

            "full_cross_document_reasoning_certification_performed":
                False,

            "source_profile_modified":
                False,

            "retrieval_payload_modified":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,
        },

        "reasoning_policy":
            "DOCUMENT_SET_AND_SCOPE_LOCKED_NO_REASONING",

        "next_stage":
            "cross_document_evidence_alignment",
    }


# =====================================================================
# PATCH 4.6.21E ? Cross-Document Evidence Alignment
# =====================================================================

def align_cross_document_evidence_v1(
    scope_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Align evidence across the locked document set.

    E performs evidence extraction and deterministic alignment only.

    E does not:
    - construct cross-document relationships,
    - execute reasoning,
    - resolve conflicts,
    - write Semantic Memory,
    - make linking decisions.
    """

    from collections.abc import Mapping
    from copy import deepcopy
    import hashlib
    import json

    if not isinstance(
        scope_result,
        Mapping,
    ):
        raise CrossDocumentReasoningError(
            "scope_result must be a mapping."
        )

    # -------------------------------------------------------------
    # Exact 4.6.21D lifecycle
    # -------------------------------------------------------------

    for field, expected in (
        (
            "schema_version",
            "cross_document_reasoning_scope_contract_result_v1",
        ),
        (
            "version",
            CROSS_DOCUMENT_REASONING_VERSION,
        ),
        (
            "phase",
            CROSS_DOCUMENT_REASONING_PHASE,
        ),
        (
            "patch",
            "4.6.21D",
        ),
        (
            "status",
            "CROSS_DOCUMENT_REASONING_SCOPE_DEFINED",
        ),
        (
            "reasoning_policy",
            "DOCUMENT_SET_AND_SCOPE_LOCKED_NO_REASONING",
        ),
        (
            "next_stage",
            "cross_document_evidence_alignment",
        ),
    ):

        if scope_result.get(field) != expected:
            raise CrossDocumentReasoningError(
                f"Invalid 4.6.21D lifecycle field: {field}"
            )

    workspace_id = scope_result.get(
        "workspace_id"
    )

    anchor_identity = scope_result.get(
        "anchor_canonical_article_identity"
    )

    document_set = scope_result.get(
        "document_set_contract"
    )

    reasoning_scope = scope_result.get(
        "reasoning_scope_contract"
    )

    architecture = scope_result.get(
        "cross_document_reasoning_architecture"
    )

    source_documents = scope_result.get(
        "source_certified_document_inputs"
    )

    boundaries = scope_result.get(
        "processing_boundaries"
    )

    for name, value in (
        ("anchor_canonical_article_identity", anchor_identity),
        ("document_set_contract", document_set),
        ("reasoning_scope_contract", reasoning_scope),
        (
            "cross_document_reasoning_architecture",
            architecture,
        ),
        ("processing_boundaries", boundaries),
    ):

        if not isinstance(
            value,
            Mapping,
        ):
            raise CrossDocumentReasoningError(
                name + " is missing."
            )

    if not isinstance(
        source_documents,
        list,
    ):
        raise CrossDocumentReasoningError(
            "source_certified_document_inputs is missing."
        )

    # -------------------------------------------------------------
    # D document-set authority
    # -------------------------------------------------------------

    if document_set.get(
        "document_set_schema"
    ) != "cross_document_reasoning_document_set_v1":
        raise CrossDocumentReasoningError(
            "Document-set schema drifted."
        )

    if document_set.get(
        "document_set_version"
    ) != "v1":
        raise CrossDocumentReasoningError(
            "Document-set version drifted."
        )

    if document_set.get(
        "document_count"
    ) is None or document_set.get(
        "document_count"
    ) < 2:
        raise CrossDocumentReasoningError(
            "Evidence alignment requires at least two documents."
        )

    if document_set.get(
        "workspace_id"
    ) != workspace_id:
        raise CrossDocumentReasoningError(
            "Document-set workspace drifted."
        )

    for field in (
        "all_documents_4.6.20K_certified",
        "same_workspace_validated",
        "duplicate_article_identity_absent",
        "anchor_document_included",
        "source_profiles_immutable",
        "retrieval_payloads_immutable",
    ):

        if document_set.get(field) is not True:
            raise CrossDocumentReasoningError(
                f"Required document-set field is not True: {field}"
            )

    document_descriptors = document_set.get(
        "documents"
    )

    if not isinstance(
        document_descriptors,
        list,
    ) or len(
        document_descriptors
    ) != document_set.get(
        "document_count"
    ):
        raise CrossDocumentReasoningError(
            "Document-set descriptors are invalid."
        )

    if len(
        source_documents
    ) != document_set.get(
        "document_count"
    ):
        raise CrossDocumentReasoningError(
            "Source certified document count drifted."
        )

    # -------------------------------------------------------------
    # D reasoning-scope authority
    # -------------------------------------------------------------

    if reasoning_scope.get(
        "reasoning_scope_schema"
    ) != "cross_document_reasoning_scope_v1":
        raise CrossDocumentReasoningError(
            "Reasoning scope schema drifted."
        )

    if reasoning_scope.get(
        "reasoning_scope_version"
    ) != "v1":
        raise CrossDocumentReasoningError(
            "Reasoning scope version drifted."
        )

    if reasoning_scope.get(
        "document_set_id"
    ) != document_set.get(
        "document_set_id"
    ):
        raise CrossDocumentReasoningError(
            "Reasoning scope document-set identity drifted."
        )

    for field in (
        "scope_explicit",
        "scope_locked",
        "evidence_bound",
        "read_only",
    ):

        if reasoning_scope.get(field) is not True:
            raise CrossDocumentReasoningError(
                f"Required reasoning-scope field is not True: {field}"
            )

    for field in (
        "evidence_alignment_performed",
        "relationship_construction_performed",
        "cross_document_reasoning_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if reasoning_scope.get(field) is not False:
            raise CrossDocumentReasoningError(
                f"Forbidden reasoning-scope field is not False: {field}"
            )

    # -------------------------------------------------------------
    # Architecture authority
    # -------------------------------------------------------------

    if architecture.get(
        "architecture_status"
    ) != "DEFINED":
        raise CrossDocumentReasoningError(
            "Cross-Document Reasoning architecture is not defined."
        )

    execution_contract = architecture.get(
        "execution_contract"
    )

    evidence_contract = architecture.get(
        "evidence_alignment_contract"
    )

    evidence_requirements = architecture.get(
        "evidence_requirements"
    )

    for name, value in (
        ("execution_contract", execution_contract),
        ("evidence_alignment_contract", evidence_contract),
        ("evidence_requirements", evidence_requirements),
    ):

        if not isinstance(
            value,
            Mapping,
        ):
            raise CrossDocumentReasoningError(
                f"Architecture {name} is missing."
            )

    if execution_contract.get(
        "4.6.21E"
    ) != "EVIDENCE_ALIGNMENT_ONLY":
        raise CrossDocumentReasoningError(
            "4.6.21E execution contract drifted."
        )

    for field in (
        "align_by_canonical_identity",
        "align_by_semantic_concepts",
        "align_by_semantic_groups",
        "align_by_cross_layer_artifacts",
        "align_by_governed_state",
        "align_by_structural_indexes",
        "preserve_source_evidence",
    ):

        if evidence_contract.get(field) is not True:
            raise CrossDocumentReasoningError(
                f"Required evidence-alignment field is not True: {field}"
            )

    if evidence_contract.get(
        "invent_evidence"
    ) is not False:
        raise CrossDocumentReasoningError(
            "Evidence invention must remain forbidden."
        )

    # -------------------------------------------------------------
    # D processing-boundary authority
    # -------------------------------------------------------------

    for field in (
        "reasoning_intake_validation_preserved",
        "cross_document_reasoning_architecture_preserved",
        "certified_document_inputs_preserved",
        "document_set_scope_defined",
        "same_workspace_validated",
        "minimum_document_requirement_validated",
        "duplicate_article_identity_rejected",
        "source_profiles_preserved",
        "retrieval_payloads_preserved",
    ):

        if boundaries.get(field) is not True:
            raise CrossDocumentReasoningError(
                f"Required 4.6.21D boundary is not True: {field}"
            )

    for field in (
        "cross_document_evidence_alignment_performed",
        "cross_document_relationships_constructed",
        "cross_document_reasoning_performed",
        "reasoning_integrity_verification_performed",
        "reasoning_provenance_built",
        "final_cross_document_reasoning_result_built",
        "full_cross_document_reasoning_certification_performed",
        "source_profile_modified",
        "retrieval_payload_modified",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if boundaries.get(field) is not False:
            raise CrossDocumentReasoningError(
                f"Forbidden 4.6.21D boundary is not False: {field}"
            )

    # -------------------------------------------------------------
    # Helper: normalize scalar evidence tokens
    # -------------------------------------------------------------

    def collect_scalar_tokens(
        value,
        prefix="",
    ):
        tokens = []

        if isinstance(value, Mapping):

            for key in sorted(
                value.keys(),
                key=str,
            ):

                child_prefix = (
                    f"{prefix}.{key}"
                    if prefix
                    else str(key)
                )

                tokens.extend(
                    collect_scalar_tokens(
                        value[key],
                        child_prefix,
                    )
                )

        elif isinstance(value, list):

            for index, item in enumerate(value):

                child_prefix = (
                    f"{prefix}[{index}]"
                )

                tokens.extend(
                    collect_scalar_tokens(
                        item,
                        child_prefix,
                    )
                )

        elif isinstance(
            value,
            (
                str,
                int,
                float,
                bool,
            ),
        ) or value is None:

            tokens.append(
                {
                    "path":
                        prefix,

                    "value":
                        deepcopy(value),
                }
            )

        return tokens

    # -------------------------------------------------------------
    # Extract admissible evidence from each certified document
    # -------------------------------------------------------------

    descriptor_by_article = {
        item["article_id"]:
            item
        for item in document_descriptors
    }

    aligned_documents = []

    for index, document in enumerate(
        source_documents
    ):

        if not isinstance(
            document,
            Mapping,
        ):
            raise CrossDocumentReasoningError(
                f"Source document {index} is invalid."
            )

        identity = document.get(
            "canonical_article_identity"
        )

        certified_final = document.get(
            "certified_final_knowledge_retrieval_result"
        )

        certification = document.get(
            "full_knowledge_retrieval_certification"
        )

        if not isinstance(
            identity,
            Mapping,
        ):
            raise CrossDocumentReasoningError(
                f"Source document {index} identity is missing."
            )

        if not isinstance(
            certified_final,
            Mapping,
        ):
            raise CrossDocumentReasoningError(
                f"Source document {index} certified final result is missing."
            )

        if not isinstance(
            certification,
            Mapping,
        ):
            raise CrossDocumentReasoningError(
                f"Source document {index} certification is missing."
            )

        article_id = identity.get(
            "article_id"
        )

        if article_id not in descriptor_by_article:
            raise CrossDocumentReasoningError(
                f"Document descriptor is missing for article: {article_id}"
            )

        descriptor = descriptor_by_article[
            article_id
        ]

        if identity.get(
            "workspace_id"
        ) != workspace_id:
            raise CrossDocumentReasoningError(
                f"Document {article_id} workspace drifted."
            )

        if certification.get(
            "certification_status"
        ) != "CERTIFIED":
            raise CrossDocumentReasoningError(
                f"Document {article_id} lost certification."
            )

        if certification.get(
            "cross_document_reasoning_ready"
        ) is not True:
            raise CrossDocumentReasoningError(
                f"Document {article_id} is not reasoning-ready."
            )

        source_profile = certified_final.get(
            "source_certified_semantic_article_profile"
        )

        if not isinstance(
            source_profile,
            Mapping,
        ):
            raise CrossDocumentReasoningError(
                f"Document {article_id} source profile is missing."
            )

        if source_profile.get(
            "profile_certified"
        ) is not True:
            raise CrossDocumentReasoningError(
                f"Document {article_id} source profile is not certified."
            )

        if source_profile.get(
            "profile_persisted"
        ) is not False:
            raise CrossDocumentReasoningError(
                f"Document {article_id} source profile immutability drifted."
            )

        if source_profile.get(
            "profile_identity",
            {},
        ).get(
            "canonical_article_identity"
        ) != identity:
            raise CrossDocumentReasoningError(
                f"Document {article_id} profile identity drifted."
            )

        if descriptor.get(
            "storage_key"
        ) != certified_final.get(
            "storage_key"
        ):
            raise CrossDocumentReasoningError(
                f"Document {article_id} descriptor storage key drifted."
            )

        evidence_sections = {}

        for section_name in (
            "profile_identity",
            "source_authority",
            "semantic_layers",
            "semantic_groups",
            "cross_layer_artifacts",
            "governed_state",
            "structural_indexes",
            "certified_source_semantic_representation",
        ):

            if section_name in source_profile:
                evidence_sections[
                    section_name
                ] = deepcopy(
                    source_profile[
                        section_name
                    ]
                )

        scalar_evidence = collect_scalar_tokens(
            evidence_sections
        )

        evidence_json = json.dumps(
            evidence_sections,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )

        evidence_digest = hashlib.sha256(
            evidence_json.encode("utf-8")
        ).hexdigest()

        aligned_documents.append(
            {
                "document_index":
                    index,

                "workspace_id":
                    workspace_id,

                "article_id":
                    article_id,

                "canonical_article_identity":
                    deepcopy(dict(identity)),

                "storage_key":
                    certified_final.get(
                        "storage_key"
                    ),

                "retrieval_payload_id":
                    certified_final.get(
                        "retrieval_payload_id"
                    ),

                "provenance_id":
                    certified_final.get(
                        "provenance_id"
                    ),

                "profile_payload_hash":
                    certified_final.get(
                        "profile_payload_hash"
                    ),

                "evidence_sections_present":
                    list(
                        evidence_sections.keys()
                    ),

                "evidence_sections":
                    evidence_sections,

                "scalar_evidence":
                    scalar_evidence,

                "evidence_digest":
                    evidence_digest,

                "source_profile_certified":
                    True,

                "source_profile_immutable":
                    True,

                "retrieval_integrity_verified":
                    certified_final.get(
                        "retrieval_integrity_verified"
                    )
                    is True,

                "evidence_invented":
                    False,
            }
        )

    # -------------------------------------------------------------
    # Deterministic pairwise alignment surfaces
    # -------------------------------------------------------------

    aligned_documents_sorted = sorted(
        aligned_documents,
        key=lambda item: item[
            "article_id"
        ],
    )

    pairwise_alignments = []

    for left_index in range(
        len(aligned_documents_sorted)
    ):

        for right_index in range(
            left_index + 1,
            len(aligned_documents_sorted),
        ):

            left = aligned_documents_sorted[
                left_index
            ]

            right = aligned_documents_sorted[
                right_index
            ]

            left_tokens = {
                json.dumps(
                    token,
                    sort_keys=True,
                    separators=(",", ":"),
                    ensure_ascii=True,
                )
                for token in left[
                    "scalar_evidence"
                ]
            }

            right_tokens = {
                json.dumps(
                    token,
                    sort_keys=True,
                    separators=(",", ":"),
                    ensure_ascii=True,
                )
                for token in right[
                    "scalar_evidence"
                ]
            }

            shared_tokens_serialized = sorted(
                left_tokens.intersection(
                    right_tokens
                )
            )

            shared_tokens = [
                json.loads(item)
                for item in shared_tokens_serialized
            ]

            left_only_tokens = [
                json.loads(item)
                for item in sorted(
                    left_tokens.difference(
                        right_tokens
                    )
                )
            ]

            right_only_tokens = [
                json.loads(item)
                for item in sorted(
                    right_tokens.difference(
                        left_tokens
                    )
                )
            ]

            shared_sections = [
                section
                for section in left[
                    "evidence_sections_present"
                ]
                if section in right[
                    "evidence_sections_present"
                ]
            ]

            pair_material = {
                "document_set_id":
                    document_set[
                        "document_set_id"
                    ],

                "reasoning_scope_id":
                    reasoning_scope[
                        "reasoning_scope_id"
                    ],

                "source_article_id":
                    left["article_id"],

                "target_article_id":
                    right["article_id"],

                "source_evidence_digest":
                    left["evidence_digest"],

                "target_evidence_digest":
                    right["evidence_digest"],
            }

            pair_json = json.dumps(
                pair_material,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
            )

            pair_digest = hashlib.sha256(
                pair_json.encode("utf-8")
            ).hexdigest()

            pair_alignment_id = (
                "cdralign:v1:"
                + pair_digest[:32]
            )

            pairwise_alignments.append(
                {
                    "alignment_id":
                        pair_alignment_id,

                    "alignment_digest":
                        pair_digest,

                    "source_article_id":
                        left["article_id"],

                    "target_article_id":
                        right["article_id"],

                    "source_evidence_digest":
                        left["evidence_digest"],

                    "target_evidence_digest":
                        right["evidence_digest"],

                    "shared_evidence_sections":
                        shared_sections,

                    "shared_scalar_evidence":
                        shared_tokens,

                    "source_only_scalar_evidence":
                        left_only_tokens,

                    "target_only_scalar_evidence":
                        right_only_tokens,

                    "shared_scalar_evidence_count":
                        len(shared_tokens),

                    "source_only_scalar_evidence_count":
                        len(left_only_tokens),

                    "target_only_scalar_evidence_count":
                        len(right_only_tokens),

                    "canonical_identity_aligned":
                        True,

                    "workspace_aligned":
                        True,

                    "source_evidence_preserved":
                        True,

                    "target_evidence_preserved":
                        True,

                    "evidence_invented":
                        False,

                    "relationship_constructed":
                        False,

                    "cross_document_reasoning_performed":
                        False,
                }
            )

    expected_pair_count = (
        len(aligned_documents_sorted)
        * (
            len(aligned_documents_sorted) - 1
        )
        // 2
    )

    if len(
        pairwise_alignments
    ) != expected_pair_count:
        raise CrossDocumentReasoningError(
            "Pairwise alignment count is invalid."
        )

    # -------------------------------------------------------------
    # Deterministic alignment package identity
    # -------------------------------------------------------------

    alignment_material = {
        "document_set_id":
            document_set[
                "document_set_id"
            ],

        "reasoning_scope_id":
            reasoning_scope[
                "reasoning_scope_id"
            ],

        "document_evidence_digests": [
            {
                "article_id":
                    item["article_id"],

                "evidence_digest":
                    item["evidence_digest"],
            }
            for item in aligned_documents_sorted
        ],

        "pair_alignment_ids": [
            item["alignment_id"]
            for item in pairwise_alignments
        ],
    }

    alignment_json = json.dumps(
        alignment_material,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    alignment_digest = hashlib.sha256(
        alignment_json.encode("utf-8")
    ).hexdigest()

    alignment_package_id = (
        "cdrevidence:v1:"
        + alignment_digest[:32]
    )

    evidence_alignment_contract = {
        "evidence_alignment_schema":
            "cross_document_evidence_alignment_v1",

        "evidence_alignment_version":
            "v1",

        "evidence_alignment_id":
            alignment_package_id,

        "evidence_alignment_digest":
            alignment_digest,

        "evidence_alignment_digest_algorithm":
            "SHA256",

        "document_set_id":
            document_set[
                "document_set_id"
            ],

        "reasoning_scope_id":
            reasoning_scope[
                "reasoning_scope_id"
            ],

        "workspace_id":
            workspace_id,

        "document_count":
            len(
                aligned_documents_sorted
            ),

        "pair_count":
            len(
                pairwise_alignments
            ),

        "documents":
            aligned_documents_sorted,

        "pairwise_alignments":
            pairwise_alignments,

        "canonical_identity_alignment_completed":
            True,

        "semantic_evidence_alignment_completed":
            True,

        "source_evidence_preserved":
            True,

        "evidence_invented":
            False,

        "relationship_construction_performed":
            False,

        "cross_document_reasoning_performed":
            False,

        "read_only":
            True,

        "semantic_memory_written":
            False,

        "linking_decisions_performed":
            False,
    }

    return {
        "schema_version":
            "cross_document_evidence_alignment_result_v1",

        "version":
            CROSS_DOCUMENT_REASONING_VERSION,

        "phase":
            CROSS_DOCUMENT_REASONING_PHASE,

        "patch":
            "4.6.21E",

        "status":
            "CROSS_DOCUMENT_EVIDENCE_ALIGNED",

        "workspace_id":
            workspace_id,

        "anchor_canonical_article_identity":
            deepcopy(
                dict(anchor_identity)
            ),

        "document_set_contract":
            deepcopy(
                dict(document_set)
            ),

        "reasoning_scope_contract":
            deepcopy(
                dict(reasoning_scope)
            ),

        "evidence_alignment_contract":
            evidence_alignment_contract,

        "cross_document_reasoning_architecture":
            deepcopy(
                dict(architecture)
            ),

        "source_scope_contract_result":
            deepcopy(
                dict(scope_result)
            ),

        "processing_boundaries": {
            "document_set_scope_contract_preserved":
                True,

            "reasoning_intake_validation_preserved":
                True,

            "cross_document_reasoning_architecture_preserved":
                True,

            "certified_document_inputs_preserved":
                True,

            "source_profiles_preserved":
                True,

            "retrieval_payloads_preserved":
                True,

            "cross_document_evidence_alignment_performed":
                True,

            "canonical_identity_alignment_performed":
                True,

            "semantic_evidence_alignment_performed":
                True,

            "cross_document_relationships_constructed":
                False,

            "cross_document_reasoning_performed":
                False,

            "reasoning_integrity_verification_performed":
                False,

            "reasoning_provenance_built":
                False,

            "final_cross_document_reasoning_result_built":
                False,

            "full_cross_document_reasoning_certification_performed":
                False,

            "source_profile_modified":
                False,

            "retrieval_payload_modified":
                False,

            "evidence_invented":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,
        },

        "reasoning_policy":
            "EVIDENCE_ALIGNMENT_ONLY_NO_RELATIONSHIP_REASONING",

        "next_stage":
            "cross_document_relationship_construction",
    }


# =====================================================================
# PATCH 4.6.21F ? Cross-Document Relationship Construction
# =====================================================================

def construct_cross_document_relationships_v1(
    alignment_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Construct deterministic evidence-bound relationship candidates
    from the certified 4.6.21E alignment package.

    F performs relationship construction only.

    It does not:
    - perform full cross-document reasoning,
    - resolve conflicts,
    - infer unsupported facts,
    - write Semantic Memory,
    - make linking decisions.
    """

    from collections.abc import Mapping
    from copy import deepcopy
    import hashlib
    import json

    if not isinstance(
        alignment_result,
        Mapping,
    ):
        raise CrossDocumentReasoningError(
            "alignment_result must be a mapping."
        )

    # -------------------------------------------------------------
    # Exact 4.6.21E lifecycle
    # -------------------------------------------------------------

    for field, expected in (
        (
            "schema_version",
            "cross_document_evidence_alignment_result_v1",
        ),
        (
            "version",
            CROSS_DOCUMENT_REASONING_VERSION,
        ),
        (
            "phase",
            CROSS_DOCUMENT_REASONING_PHASE,
        ),
        (
            "patch",
            "4.6.21E",
        ),
        (
            "status",
            "CROSS_DOCUMENT_EVIDENCE_ALIGNED",
        ),
        (
            "reasoning_policy",
            "EVIDENCE_ALIGNMENT_ONLY_NO_RELATIONSHIP_REASONING",
        ),
        (
            "next_stage",
            "cross_document_relationship_construction",
        ),
    ):

        if alignment_result.get(field) != expected:
            raise CrossDocumentReasoningError(
                f"Invalid 4.6.21E lifecycle field: {field}"
            )

    workspace_id = alignment_result.get(
        "workspace_id"
    )

    document_set = alignment_result.get(
        "document_set_contract"
    )

    reasoning_scope = alignment_result.get(
        "reasoning_scope_contract"
    )

    evidence_alignment = alignment_result.get(
        "evidence_alignment_contract"
    )

    architecture = alignment_result.get(
        "cross_document_reasoning_architecture"
    )

    boundaries = alignment_result.get(
        "processing_boundaries"
    )

    for name, value in (
        ("document_set_contract", document_set),
        ("reasoning_scope_contract", reasoning_scope),
        ("evidence_alignment_contract", evidence_alignment),
        (
            "cross_document_reasoning_architecture",
            architecture,
        ),
        ("processing_boundaries", boundaries),
    ):

        if not isinstance(
            value,
            Mapping,
        ):
            raise CrossDocumentReasoningError(
                name + " is missing."
            )

    # -------------------------------------------------------------
    # E alignment authority
    # -------------------------------------------------------------

    if evidence_alignment.get(
        "evidence_alignment_schema"
    ) != "cross_document_evidence_alignment_v1":
        raise CrossDocumentReasoningError(
            "Evidence alignment schema drifted."
        )

    if evidence_alignment.get(
        "evidence_alignment_version"
    ) != "v1":
        raise CrossDocumentReasoningError(
            "Evidence alignment version drifted."
        )

    if evidence_alignment.get(
        "document_set_id"
    ) != document_set.get(
        "document_set_id"
    ):
        raise CrossDocumentReasoningError(
            "Evidence alignment document-set identity drifted."
        )

    if evidence_alignment.get(
        "reasoning_scope_id"
    ) != reasoning_scope.get(
        "reasoning_scope_id"
    ):
        raise CrossDocumentReasoningError(
            "Evidence alignment reasoning-scope identity drifted."
        )

    if evidence_alignment.get(
        "workspace_id"
    ) != workspace_id:
        raise CrossDocumentReasoningError(
            "Evidence alignment workspace drifted."
        )

    for field in (
        "canonical_identity_alignment_completed",
        "semantic_evidence_alignment_completed",
        "source_evidence_preserved",
        "read_only",
    ):

        if evidence_alignment.get(field) is not True:
            raise CrossDocumentReasoningError(
                f"Required evidence-alignment field is not True: {field}"
            )

    for field in (
        "evidence_invented",
        "relationship_construction_performed",
        "cross_document_reasoning_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if evidence_alignment.get(field) is not False:
            raise CrossDocumentReasoningError(
                f"Forbidden evidence-alignment field is not False: {field}"
            )

    documents = evidence_alignment.get(
        "documents"
    )

    pairs = evidence_alignment.get(
        "pairwise_alignments"
    )

    if not isinstance(
        documents,
        list,
    ) or not isinstance(
        pairs,
        list,
    ):
        raise CrossDocumentReasoningError(
            "Aligned documents or pairwise alignments are missing."
        )

    if len(documents) < 2:
        raise CrossDocumentReasoningError(
            "At least two aligned documents are required."
        )

    if len(pairs) != evidence_alignment.get(
        "pair_count"
    ):
        raise CrossDocumentReasoningError(
            "Pairwise alignment count drifted."
        )

    # -------------------------------------------------------------
    # Architecture authority
    # -------------------------------------------------------------

    if architecture.get(
        "architecture_status"
    ) != "DEFINED":
        raise CrossDocumentReasoningError(
            "Cross-Document Reasoning architecture is not defined."
        )

    execution_contract = architecture.get(
        "execution_contract"
    )

    relationship_contract = architecture.get(
        "relationship_construction_contract"
    )

    architecture_families = architecture.get(
        "relationship_families"
    )

    if not isinstance(
        execution_contract,
        Mapping,
    ):
        raise CrossDocumentReasoningError(
            "Execution contract is missing."
        )

    if not isinstance(
        relationship_contract,
        Mapping,
    ):
        raise CrossDocumentReasoningError(
            "Relationship construction contract is missing."
        )

    if not isinstance(
        architecture_families,
        list,
    ):
        raise CrossDocumentReasoningError(
            "Architecture relationship families are missing."
        )

    if execution_contract.get(
        "4.6.21F"
    ) != "RELATIONSHIP_CONSTRUCTION_ONLY":
        raise CrossDocumentReasoningError(
            "4.6.21F execution contract drifted."
        )

    for field in (
        "relationship_has_source_document",
        "relationship_has_target_document",
        "relationship_has_relationship_family",
        "relationship_has_evidence",
        "relationship_has_directionality",
        "relationship_has_confidence_state",
        "relationship_has_uncertainty_state",
        "relationship_has_provenance",
    ):

        if relationship_contract.get(field) is not True:
            raise CrossDocumentReasoningError(
                f"Required relationship-contract field is not True: {field}"
            )

    if relationship_contract.get(
        "relationship_is_linking_decision"
    ) is not False:
        raise CrossDocumentReasoningError(
            "Relationship construction must not become a linking decision."
        )

    requested_families = reasoning_scope.get(
        "relationship_families"
    )

    if not isinstance(
        requested_families,
        list,
    ) or not requested_families:
        raise CrossDocumentReasoningError(
            "Requested relationship families are missing."
        )

    for family in requested_families:

        if family not in architecture_families:
            raise CrossDocumentReasoningError(
                f"Unsupported relationship family in scope: {family}"
            )

    # -------------------------------------------------------------
    # E processing-boundary authority
    # -------------------------------------------------------------

    for field in (
        "document_set_scope_contract_preserved",
        "reasoning_intake_validation_preserved",
        "cross_document_reasoning_architecture_preserved",
        "certified_document_inputs_preserved",
        "source_profiles_preserved",
        "retrieval_payloads_preserved",
        "cross_document_evidence_alignment_performed",
        "canonical_identity_alignment_performed",
        "semantic_evidence_alignment_performed",
    ):

        if boundaries.get(field) is not True:
            raise CrossDocumentReasoningError(
                f"Required 4.6.21E boundary is not True: {field}"
            )

    for field in (
        "cross_document_relationships_constructed",
        "cross_document_reasoning_performed",
        "reasoning_integrity_verification_performed",
        "reasoning_provenance_built",
        "final_cross_document_reasoning_result_built",
        "full_cross_document_reasoning_certification_performed",
        "source_profile_modified",
        "retrieval_payload_modified",
        "evidence_invented",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if boundaries.get(field) is not False:
            raise CrossDocumentReasoningError(
                f"Forbidden 4.6.21E boundary is not False: {field}"
            )

    # -------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------

    def token_key(token):
        return json.dumps(
            token,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )

    def token_paths(tokens):
        return {
            token.get("path")
            for token in tokens
            if isinstance(token, Mapping)
        }

    def token_values(tokens):
        return {
            json.dumps(
                token.get("value"),
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
            )
            for token in tokens
            if isinstance(token, Mapping)
        }

    # -------------------------------------------------------------
    # Construct evidence-bound candidate relationships
    # -------------------------------------------------------------

    relationship_candidates = []

    for pair in pairs:

        if not isinstance(
            pair,
            Mapping,
        ):
            raise CrossDocumentReasoningError(
                "Pairwise alignment entry is invalid."
            )

        for field in (
            "canonical_identity_aligned",
            "workspace_aligned",
            "source_evidence_preserved",
            "target_evidence_preserved",
        ):

            if pair.get(field) is not True:
                raise CrossDocumentReasoningError(
                    f"Pair alignment field is not True: {field}"
                )

        for field in (
            "evidence_invented",
            "relationship_constructed",
            "cross_document_reasoning_performed",
        ):

            if pair.get(field) is not False:
                raise CrossDocumentReasoningError(
                    f"Pair alignment field is not False: {field}"
                )

        source_article = pair.get(
            "source_article_id"
        )

        target_article = pair.get(
            "target_article_id"
        )

        shared_tokens = pair.get(
            "shared_scalar_evidence"
        )

        source_only = pair.get(
            "source_only_scalar_evidence"
        )

        target_only = pair.get(
            "target_only_scalar_evidence"
        )

        if not isinstance(
            shared_tokens,
            list,
        ) or not isinstance(
            source_only,
            list,
        ) or not isinstance(
            target_only,
            list,
        ):
            raise CrossDocumentReasoningError(
                "Pair evidence surfaces are invalid."
            )

        shared_count = len(
            shared_tokens
        )

        source_only_count = len(
            source_only
        )

        target_only_count = len(
            target_only
        )

        total_unique_surface = (
            shared_count
            + source_only_count
            + target_only_count
        )

        overlap_ratio = (
            shared_count
            / total_unique_surface
            if total_unique_surface
            else 0.0
        )

        source_paths = token_paths(
            source_only
        )

        target_paths = token_paths(
            target_only
        )

        shared_values = token_values(
            shared_tokens
        )

        candidate_specs = []

        # ---------------------------------------------------------
        # SHARED_TOPIC
        # ---------------------------------------------------------

        shared_topic_evidence = [
            token
            for token in shared_tokens
            if (
                "shared_topic"
                in str(
                    token.get("path", "")
                )
                or "primary_group"
                in str(
                    token.get("path", "")
                )
                or "topic_index"
                in str(
                    token.get("path", "")
                )
                or str(
                    token.get("path", "")
                ).endswith(".topic")
            )
        ]

        if (
            "SHARED_TOPIC"
            in requested_families
            and shared_topic_evidence
        ):

            candidate_specs.append(
                {
                    "relationship_family":
                        "SHARED_TOPIC",

                    "directionality":
                        "BIDIRECTIONAL",

                    "evidence":
                        deepcopy(
                            shared_topic_evidence
                        ),

                    "confidence_state":
                        "HIGH",

                    "uncertainty_state":
                        "LOW",
                }
            )

        # ---------------------------------------------------------
        # SEMANTIC_OVERLAP
        # ---------------------------------------------------------

        if (
            "SEMANTIC_OVERLAP"
            in requested_families
            and shared_count > 0
        ):

            candidate_specs.append(
                {
                    "relationship_family":
                        "SEMANTIC_OVERLAP",

                    "directionality":
                        "BIDIRECTIONAL",

                    "evidence":
                        deepcopy(
                            shared_tokens
                        ),

                    "confidence_state":
                        (
                            "HIGH"
                            if overlap_ratio >= 0.50
                            else "MODERATE"
                        ),

                    "uncertainty_state":
                        (
                            "LOW"
                            if overlap_ratio >= 0.50
                            else "MODERATE"
                        ),
                }
            )

        # ---------------------------------------------------------
        # COMPLEMENTARY
        # ---------------------------------------------------------

        if (
            "COMPLEMENTARY"
            in requested_families
            and shared_count > 0
            and source_only_count > 0
            and target_only_count > 0
        ):

            candidate_specs.append(
                {
                    "relationship_family":
                        "COMPLEMENTARY",

                    "directionality":
                        "BIDIRECTIONAL",

                    "evidence": {
                        "shared":
                            deepcopy(
                                shared_tokens
                            ),

                        "source_unique":
                            deepcopy(
                                source_only
                            ),

                        "target_unique":
                            deepcopy(
                                target_only
                            ),
                    },

                    "confidence_state":
                        "MODERATE",

                    "uncertainty_state":
                        "MODERATE",
                }
            )

        # ---------------------------------------------------------
        # POTENTIAL_DUPLICATION
        # ---------------------------------------------------------

        if (
            "POTENTIAL_DUPLICATION"
            in requested_families
            and total_unique_surface > 0
            and overlap_ratio >= 0.80
        ):

            candidate_specs.append(
                {
                    "relationship_family":
                        "POTENTIAL_DUPLICATION",

                    "directionality":
                        "BIDIRECTIONAL",

                    "evidence":
                        deepcopy(
                            shared_tokens
                        ),

                    "confidence_state":
                        "HIGH",

                    "uncertainty_state":
                        "LOW",
                }
            )

        # ---------------------------------------------------------
        # INFORMATION_GAIN
        # ---------------------------------------------------------

        if (
            "INFORMATION_GAIN"
            in requested_families
            and target_only_count > 0
        ):

            candidate_specs.append(
                {
                    "relationship_family":
                        "INFORMATION_GAIN",

                    "directionality":
                        "SOURCE_TO_TARGET",

                    "evidence": {
                        "shared":
                            deepcopy(
                                shared_tokens
                            ),

                        "target_unique":
                            deepcopy(
                                target_only
                            ),
                    },

                    "confidence_state":
                        "MODERATE",

                    "uncertainty_state":
                        "MODERATE",
                }
            )

        # ---------------------------------------------------------
        # CONTENT_GAP
        # ---------------------------------------------------------

        if (
            "CONTENT_GAP"
            in requested_families
            and (
                source_only_count > 0
                or target_only_count > 0
            )
        ):

            candidate_specs.append(
                {
                    "relationship_family":
                        "CONTENT_GAP",

                    "directionality":
                        "BIDIRECTIONAL",

                    "evidence": {
                        "source_unique":
                            deepcopy(
                                source_only
                            ),

                        "target_unique":
                            deepcopy(
                                target_only
                            ),
                    },

                    "confidence_state":
                        "MODERATE",

                    "uncertainty_state":
                        "HIGH",
                }
            )

        # ---------------------------------------------------------
        # CAUSE_EFFECT
        #
        # F is allowed only to construct a candidate when explicit
        # semantic evidence surfaces contain cause/effect language.
        # ---------------------------------------------------------

        combined_paths = {
            str(path).lower()
            for path in (
                source_paths
                | target_paths
            )
        }

        cause_path_present = any(
            (
                "cause"
                in path
                or "effect"
                in path
                or "causal"
                in path
            )
            for path in combined_paths
        )

        cause_value_present = any(
            (
                "cause"
                in value.lower()
                or "effect"
                in value.lower()
            )
            for value in shared_values
        )

        if (
            "CAUSE_EFFECT"
            in requested_families
            and (
                cause_path_present
                or cause_value_present
            )
        ):

            candidate_specs.append(
                {
                    "relationship_family":
                        "CAUSE_EFFECT",

                    "directionality":
                        "UNRESOLVED_DIRECTION",

                    "evidence": {
                        "shared":
                            deepcopy(
                                shared_tokens
                            ),

                        "source_unique":
                            deepcopy(
                                source_only
                            ),

                        "target_unique":
                            deepcopy(
                                target_only
                            ),
                    },

                    "confidence_state":
                        "LOW",

                    "uncertainty_state":
                        "HIGH",
                }
            )

        # ---------------------------------------------------------
        # SUPPORTING_EVIDENCE
        # ---------------------------------------------------------

        if (
            "SUPPORTING_EVIDENCE"
            in requested_families
            and shared_count > 0
        ):

            candidate_specs.append(
                {
                    "relationship_family":
                        "SUPPORTING_EVIDENCE",

                    "directionality":
                        "BIDIRECTIONAL_CANDIDATE",

                    "evidence":
                        deepcopy(
                            shared_tokens
                        ),

                    "confidence_state":
                        "LOW",

                    "uncertainty_state":
                        "HIGH",
                }
            )

        # ---------------------------------------------------------
        # CONTRADICTION
        #
        # F does not resolve contradiction. It may only construct
        # a candidate if the same evidence path exposes unequal
        # scalar values between documents.
        # ---------------------------------------------------------

        def by_path(tokens):
            result = {}

            for token in tokens:

                if not isinstance(
                    token,
                    Mapping,
                ):
                    continue

                path = token.get(
                    "path"
                )

                result.setdefault(
                    path,
                    [],
                ).append(
                    token.get(
                        "value"
                    )
                )

            return result

        source_unique_by_path = by_path(
            source_only
        )

        target_unique_by_path = by_path(
            target_only
        )

        contradictory_paths = []

        for path in sorted(
            set(
                source_unique_by_path
            ).intersection(
                target_unique_by_path
            ),
            key=str,
        ):

            source_values = source_unique_by_path[
                path
            ]

            target_values = target_unique_by_path[
                path
            ]

            if source_values != target_values:

                contradictory_paths.append(
                    {
                        "path":
                            path,

                        "source_values":
                            deepcopy(
                                source_values
                            ),

                        "target_values":
                            deepcopy(
                                target_values
                            ),
                    }
                )

        if (
            "CONTRADICTION"
            in requested_families
            and contradictory_paths
        ):

            candidate_specs.append(
                {
                    "relationship_family":
                        "CONTRADICTION",

                    "directionality":
                        "BIDIRECTIONAL",

                    "evidence":
                        contradictory_paths,

                    "confidence_state":
                        "MODERATE",

                    "uncertainty_state":
                        "HIGH",
                }
            )

        # ---------------------------------------------------------
        # Materialize candidate relationships
        # ---------------------------------------------------------

        for spec in candidate_specs:

            relationship_material = {
                "document_set_id":
                    document_set[
                        "document_set_id"
                    ],

                "reasoning_scope_id":
                    reasoning_scope[
                        "reasoning_scope_id"
                    ],

                "alignment_id":
                    pair[
                        "alignment_id"
                    ],

                "source_article_id":
                    source_article,

                "target_article_id":
                    target_article,

                "relationship_family":
                    spec[
                        "relationship_family"
                    ],

                "directionality":
                    spec[
                        "directionality"
                    ],

                "evidence":
                    spec[
                        "evidence"
                    ],
            }

            relationship_json = json.dumps(
                relationship_material,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
            )

            relationship_digest = hashlib.sha256(
                relationship_json.encode("utf-8")
            ).hexdigest()

            relationship_id = (
                "cdrrel:v1:"
                + relationship_digest[:32]
            )

            relationship_candidates.append(
                {
                    "relationship_schema":
                        "cross_document_relationship_candidate_v1",

                    "relationship_version":
                        "v1",

                    "relationship_id":
                        relationship_id,

                    "relationship_digest":
                        relationship_digest,

                    "relationship_digest_algorithm":
                        "SHA256",

                    "source_article_id":
                        source_article,

                    "target_article_id":
                        target_article,

                    "relationship_family":
                        spec[
                            "relationship_family"
                        ],

                    "directionality":
                        spec[
                            "directionality"
                        ],

                    "evidence":
                        deepcopy(
                            spec[
                                "evidence"
                            ]
                        ),

                    "evidence_alignment_id":
                        pair[
                            "alignment_id"
                        ],

                    "confidence_state":
                        spec[
                            "confidence_state"
                        ],

                    "uncertainty_state":
                        spec[
                            "uncertainty_state"
                        ],

                    "relationship_candidate":
                        True,

                    "relationship_confirmed":
                        False,

                    "evidence_bound":
                        True,

                    "unsupported_fact_inference":
                        False,

                    "source_profile_modified":
                        False,

                    "retrieval_payload_modified":
                        False,

                    "cross_document_reasoning_performed":
                        False,

                    "semantic_memory_written":
                        False,

                    "linking_decision":
                        False,
                }
            )

    relationship_candidates = sorted(
        relationship_candidates,
        key=lambda item: (
            item[
                "source_article_id"
            ],
            item[
                "target_article_id"
            ],
            item[
                "relationship_family"
            ],
            item[
                "relationship_id"
            ],
        ),
    )

    # -------------------------------------------------------------
    # Deterministic relationship package identity
    # -------------------------------------------------------------

    package_material = {
        "document_set_id":
            document_set[
                "document_set_id"
            ],

        "reasoning_scope_id":
            reasoning_scope[
                "reasoning_scope_id"
            ],

        "evidence_alignment_id":
            evidence_alignment[
                "evidence_alignment_id"
            ],

        "relationship_ids": [
            item[
                "relationship_id"
            ]
            for item in relationship_candidates
        ],
    }

    package_json = json.dumps(
        package_material,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    package_digest = hashlib.sha256(
        package_json.encode("utf-8")
    ).hexdigest()

    relationship_package_id = (
        "cdrrels:v1:"
        + package_digest[:32]
    )

    family_counts = {}

    for item in relationship_candidates:

        family = item[
            "relationship_family"
        ]

        family_counts[
            family
        ] = (
            family_counts.get(
                family,
                0,
            )
            + 1
        )

    relationship_construction = {
        "relationship_construction_schema":
            "cross_document_relationship_construction_v1",

        "relationship_construction_version":
            "v1",

        "relationship_package_id":
            relationship_package_id,

        "relationship_package_digest":
            package_digest,

        "relationship_package_digest_algorithm":
            "SHA256",

        "document_set_id":
            document_set[
                "document_set_id"
            ],

        "reasoning_scope_id":
            reasoning_scope[
                "reasoning_scope_id"
            ],

        "evidence_alignment_id":
            evidence_alignment[
                "evidence_alignment_id"
            ],

        "workspace_id":
            workspace_id,

        "pair_count":
            len(pairs),

        "relationship_candidate_count":
            len(
                relationship_candidates
            ),

        "relationship_family_counts":
            family_counts,

        "relationship_candidates":
            relationship_candidates,

        "relationship_construction_performed":
            True,

        "relationships_are_candidates_only":
            True,

        "relationships_confirmed":
            False,

        "evidence_bound":
            True,

        "source_evidence_preserved":
            True,

        "evidence_invented":
            False,

        "cross_document_reasoning_performed":
            False,

        "reasoning_integrity_verification_performed":
            False,

        "read_only":
            True,

        "semantic_memory_written":
            False,

        "linking_decisions_performed":
            False,
    }

    return {
        "schema_version":
            "cross_document_relationship_construction_result_v1",

        "version":
            CROSS_DOCUMENT_REASONING_VERSION,

        "phase":
            CROSS_DOCUMENT_REASONING_PHASE,

        "patch":
            "4.6.21F",

        "status":
            "CROSS_DOCUMENT_RELATIONSHIPS_CONSTRUCTED",

        "workspace_id":
            workspace_id,

        "document_set_contract":
            deepcopy(
                dict(document_set)
            ),

        "reasoning_scope_contract":
            deepcopy(
                dict(reasoning_scope)
            ),

        "evidence_alignment_contract":
            deepcopy(
                dict(evidence_alignment)
            ),

        "relationship_construction_contract":
            relationship_construction,

        "cross_document_reasoning_architecture":
            deepcopy(
                dict(architecture)
            ),

        "source_evidence_alignment_result":
            deepcopy(
                dict(alignment_result)
            ),

        "processing_boundaries": {
            "document_set_scope_contract_preserved":
                True,

            "evidence_alignment_preserved":
                True,

            "cross_document_reasoning_architecture_preserved":
                True,

            "source_profiles_preserved":
                True,

            "retrieval_payloads_preserved":
                True,

            "cross_document_evidence_alignment_performed":
                True,

            "cross_document_relationships_constructed":
                True,

            "relationships_are_candidates_only":
                True,

            "cross_document_reasoning_performed":
                False,

            "reasoning_integrity_verification_performed":
                False,

            "reasoning_provenance_built":
                False,

            "final_cross_document_reasoning_result_built":
                False,

            "full_cross_document_reasoning_certification_performed":
                False,

            "source_profile_modified":
                False,

            "retrieval_payload_modified":
                False,

            "evidence_invented":
                False,

            "unsupported_fact_inference_performed":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,
        },

        "reasoning_policy":
            "RELATIONSHIP_CONSTRUCTION_ONLY_NO_FULL_REASONING",

        "next_stage":
            "cross_document_reasoning_execution",
    }


# =====================================================================
# PATCH 4.6.21G ? Cross-Document Reasoning Execution
# =====================================================================

def execute_cross_document_reasoning_v1(
    relationship_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Execute evidence-bound cross-document reasoning over the
    relationship candidates produced by 4.6.21F.

    G may confirm, reject, or leave a candidate unresolved.

    G does not:
    - mutate source profiles,
    - mutate retrieval payloads,
    - silently resolve conflicts,
    - write Semantic Memory,
    - make linking decisions.
    """

    from collections.abc import Mapping
    from copy import deepcopy
    import hashlib
    import json

    if not isinstance(
        relationship_result,
        Mapping,
    ):
        raise CrossDocumentReasoningError(
            "relationship_result must be a mapping."
        )

    # -------------------------------------------------------------
    # Exact 4.6.21F lifecycle
    # -------------------------------------------------------------

    for field, expected in (
        (
            "schema_version",
            "cross_document_relationship_construction_result_v1",
        ),
        (
            "version",
            CROSS_DOCUMENT_REASONING_VERSION,
        ),
        (
            "phase",
            CROSS_DOCUMENT_REASONING_PHASE,
        ),
        (
            "patch",
            "4.6.21F",
        ),
        (
            "status",
            "CROSS_DOCUMENT_RELATIONSHIPS_CONSTRUCTED",
        ),
        (
            "reasoning_policy",
            "RELATIONSHIP_CONSTRUCTION_ONLY_NO_FULL_REASONING",
        ),
        (
            "next_stage",
            "cross_document_reasoning_execution",
        ),
    ):

        if relationship_result.get(field) != expected:
            raise CrossDocumentReasoningError(
                f"Invalid 4.6.21F lifecycle field: {field}"
            )

    workspace_id = relationship_result.get(
        "workspace_id"
    )

    document_set = relationship_result.get(
        "document_set_contract"
    )

    reasoning_scope = relationship_result.get(
        "reasoning_scope_contract"
    )

    evidence_alignment = relationship_result.get(
        "evidence_alignment_contract"
    )

    construction = relationship_result.get(
        "relationship_construction_contract"
    )

    architecture = relationship_result.get(
        "cross_document_reasoning_architecture"
    )

    boundaries = relationship_result.get(
        "processing_boundaries"
    )

    for name, value in (
        ("document_set_contract", document_set),
        ("reasoning_scope_contract", reasoning_scope),
        ("evidence_alignment_contract", evidence_alignment),
        ("relationship_construction_contract", construction),
        (
            "cross_document_reasoning_architecture",
            architecture,
        ),
        ("processing_boundaries", boundaries),
    ):

        if not isinstance(
            value,
            Mapping,
        ):
            raise CrossDocumentReasoningError(
                name + " is missing."
            )

    # -------------------------------------------------------------
    # F construction authority
    # -------------------------------------------------------------

    if construction.get(
        "relationship_construction_schema"
    ) != "cross_document_relationship_construction_v1":
        raise CrossDocumentReasoningError(
            "Relationship construction schema drifted."
        )

    if construction.get(
        "relationship_construction_version"
    ) != "v1":
        raise CrossDocumentReasoningError(
            "Relationship construction version drifted."
        )

    if construction.get(
        "document_set_id"
    ) != document_set.get(
        "document_set_id"
    ):
        raise CrossDocumentReasoningError(
            "Relationship construction document-set identity drifted."
        )

    if construction.get(
        "reasoning_scope_id"
    ) != reasoning_scope.get(
        "reasoning_scope_id"
    ):
        raise CrossDocumentReasoningError(
            "Relationship construction scope identity drifted."
        )

    if construction.get(
        "evidence_alignment_id"
    ) != evidence_alignment.get(
        "evidence_alignment_id"
    ):
        raise CrossDocumentReasoningError(
            "Relationship construction alignment identity drifted."
        )

    for field in (
        "relationship_construction_performed",
        "relationships_are_candidates_only",
        "evidence_bound",
        "source_evidence_preserved",
        "read_only",
    ):

        if construction.get(field) is not True:
            raise CrossDocumentReasoningError(
                f"Required F construction field is not True: {field}"
            )

    for field in (
        "relationships_confirmed",
        "evidence_invented",
        "cross_document_reasoning_performed",
        "reasoning_integrity_verification_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if construction.get(field) is not False:
            raise CrossDocumentReasoningError(
                f"Forbidden F construction field is not False: {field}"
            )

    candidates = construction.get(
        "relationship_candidates"
    )

    if not isinstance(
        candidates,
        list,
    ):
        raise CrossDocumentReasoningError(
            "Relationship candidates are missing."
        )

    if len(candidates) != construction.get(
        "relationship_candidate_count"
    ):
        raise CrossDocumentReasoningError(
            "Relationship candidate count drifted."
        )

    # -------------------------------------------------------------
    # Architecture authority
    # -------------------------------------------------------------

    if architecture.get(
        "architecture_status"
    ) != "DEFINED":
        raise CrossDocumentReasoningError(
            "Cross-Document Reasoning architecture is not defined."
        )

    execution_contract = architecture.get(
        "execution_contract"
    )

    reasoning_execution = architecture.get(
        "reasoning_execution_contract"
    )

    evidence_requirements = architecture.get(
        "evidence_requirements"
    )

    if not isinstance(
        execution_contract,
        Mapping,
    ):
        raise CrossDocumentReasoningError(
            "Execution contract is missing."
        )

    if not isinstance(
        reasoning_execution,
        Mapping,
    ):
        raise CrossDocumentReasoningError(
            "Reasoning execution contract is missing."
        )

    if not isinstance(
        evidence_requirements,
        Mapping,
    ):
        raise CrossDocumentReasoningError(
            "Evidence requirements are missing."
        )

    if execution_contract.get(
        "4.6.21G"
    ) != "CROSS_DOCUMENT_REASONING_EXECUTION":
        raise CrossDocumentReasoningError(
            "4.6.21G execution contract drifted."
        )

    for field in (
        "reason_only_over_declared_document_set",
        "reason_only_over_aligned_evidence",
        "new_cross_document_relations_allowed",
        "new_cross_document_reasoning_allowed",
        "unsupported_new_facts_forbidden",
        "source_profile_mutation_forbidden",
        "retrieval_payload_mutation_forbidden",
        "semantic_memory_write_forbidden",
        "linking_decision_forbidden",
    ):

        if reasoning_execution.get(field) is not True:
            raise CrossDocumentReasoningError(
                f"Required reasoning-execution field is not True: {field}"
            )

    # -------------------------------------------------------------
    # F processing-boundary authority
    # -------------------------------------------------------------

    for field in (
        "document_set_scope_contract_preserved",
        "evidence_alignment_preserved",
        "cross_document_reasoning_architecture_preserved",
        "source_profiles_preserved",
        "retrieval_payloads_preserved",
        "cross_document_evidence_alignment_performed",
        "cross_document_relationships_constructed",
        "relationships_are_candidates_only",
    ):

        if boundaries.get(field) is not True:
            raise CrossDocumentReasoningError(
                f"Required 4.6.21F boundary is not True: {field}"
            )

    for field in (
        "cross_document_reasoning_performed",
        "reasoning_integrity_verification_performed",
        "reasoning_provenance_built",
        "final_cross_document_reasoning_result_built",
        "full_cross_document_reasoning_certification_performed",
        "source_profile_modified",
        "retrieval_payload_modified",
        "evidence_invented",
        "unsupported_fact_inference_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if boundaries.get(field) is not False:
            raise CrossDocumentReasoningError(
                f"Forbidden 4.6.21F boundary is not False: {field}"
            )

    # -------------------------------------------------------------
    # Reason over candidates
    # -------------------------------------------------------------

    reasoned_relationships = []

    for candidate in candidates:

        if not isinstance(
            candidate,
            Mapping,
        ):
            raise CrossDocumentReasoningError(
                "Relationship candidate entry is invalid."
            )

        if candidate.get(
            "relationship_schema"
        ) != "cross_document_relationship_candidate_v1":
            raise CrossDocumentReasoningError(
                "Candidate schema drifted."
            )

        if candidate.get(
            "relationship_candidate"
        ) is not True:
            raise CrossDocumentReasoningError(
                "Candidate relationship flag is false."
            )

        if candidate.get(
            "relationship_confirmed"
        ) is not False:
            raise CrossDocumentReasoningError(
                "Candidate was prematurely confirmed."
            )

        if candidate.get(
            "evidence_bound"
        ) is not True:
            raise CrossDocumentReasoningError(
                "Candidate is not evidence-bound."
            )

        for field in (
            "unsupported_fact_inference",
            "source_profile_modified",
            "retrieval_payload_modified",
            "cross_document_reasoning_performed",
            "semantic_memory_written",
            "linking_decision",
        ):

            if candidate.get(field) is not False:
                raise CrossDocumentReasoningError(
                    f"Forbidden candidate field is not False: {field}"
                )

        family = candidate.get(
            "relationship_family"
        )

        evidence = candidate.get(
            "evidence"
        )

        if evidence is None:
            raise CrossDocumentReasoningError(
                "Candidate evidence is missing."
            )

        reasoning_status = "UNRESOLVED"
        relationship_confirmed = False
        relationship_rejected = False

        reasoning_basis = []
        reasoning_confidence = candidate.get(
            "confidence_state",
            "LOW",
        )

        reasoning_uncertainty = candidate.get(
            "uncertainty_state",
            "HIGH",
        )

        # ---------------------------------------------------------
        # SHARED_TOPIC
        # ---------------------------------------------------------

        if family == "SHARED_TOPIC":

            if isinstance(
                evidence,
                list,
            ) and len(evidence) > 0:

                reasoning_status = "CONFIRMED"
                relationship_confirmed = True
                reasoning_confidence = "HIGH"
                reasoning_uncertainty = "LOW"

                reasoning_basis.append(
                    "SHARED_TOPIC_EVIDENCE_PRESENT"
                )

            else:
                reasoning_status = "REJECTED"
                relationship_rejected = True

                reasoning_basis.append(
                    "NO_SHARED_TOPIC_EVIDENCE"
                )

        # ---------------------------------------------------------
        # COMPLEMENTARY
        # ---------------------------------------------------------

        elif family == "COMPLEMENTARY":

            if not isinstance(
                evidence,
                Mapping,
            ):
                raise CrossDocumentReasoningError(
                    "Complementary evidence must be a mapping."
                )

            shared = evidence.get(
                "shared"
            )

            source_unique = evidence.get(
                "source_unique"
            )

            target_unique = evidence.get(
                "target_unique"
            )

            if (
                isinstance(shared, list)
                and shared
                and isinstance(
                    source_unique,
                    list,
                )
                and source_unique
                and isinstance(
                    target_unique,
                    list,
                )
                and target_unique
            ):

                reasoning_status = "CONFIRMED"
                relationship_confirmed = True
                reasoning_confidence = "MODERATE"
                reasoning_uncertainty = "LOW"

                reasoning_basis.extend(
                    [
                        "SHARED_CONTEXT_PRESENT",
                        "SOURCE_UNIQUE_INFORMATION_PRESENT",
                        "TARGET_UNIQUE_INFORMATION_PRESENT",
                    ]
                )

            else:
                reasoning_status = "REJECTED"
                relationship_rejected = True

                reasoning_basis.append(
                    "COMPLEMENTARY_EVIDENCE_INCOMPLETE"
                )

        # ---------------------------------------------------------
        # INFORMATION_GAIN
        # ---------------------------------------------------------

        elif family == "INFORMATION_GAIN":

            if not isinstance(
                evidence,
                Mapping,
            ):
                raise CrossDocumentReasoningError(
                    "Information-gain evidence must be a mapping."
                )

            target_unique = evidence.get(
                "target_unique"
            )

            if isinstance(
                target_unique,
                list,
            ) and target_unique:

                reasoning_status = "CONFIRMED"
                relationship_confirmed = True
                reasoning_confidence = "MODERATE"
                reasoning_uncertainty = "LOW"

                reasoning_basis.append(
                    "TARGET_ADDS_UNIQUE_INFORMATION"
                )

            else:
                reasoning_status = "REJECTED"
                relationship_rejected = True

                reasoning_basis.append(
                    "NO_TARGET_INFORMATION_GAIN"
                )

        # ---------------------------------------------------------
        # CONTENT_GAP
        #
        # Candidate is retained as a gap signal, but because a
        # content gap can require higher-level interpretation,
        # the relationship remains unresolved in G.
        # ---------------------------------------------------------

        elif family == "CONTENT_GAP":

            if not isinstance(
                evidence,
                Mapping,
            ):
                raise CrossDocumentReasoningError(
                    "Content-gap evidence must be a mapping."
                )

            source_unique = evidence.get(
                "source_unique"
            )

            target_unique = evidence.get(
                "target_unique"
            )

            if (
                (
                    isinstance(
                        source_unique,
                        list,
                    )
                    and source_unique
                )
                or (
                    isinstance(
                        target_unique,
                        list,
                    )
                    and target_unique
                )
            ):

                reasoning_status = "UNRESOLVED"
                reasoning_confidence = "MODERATE"
                reasoning_uncertainty = "HIGH"

                reasoning_basis.append(
                    "UNIQUE_COVERAGE_DIFFERENCE_PRESENT"
                )

            else:
                reasoning_status = "REJECTED"
                relationship_rejected = True

                reasoning_basis.append(
                    "NO_GAP_EVIDENCE"
                )

        # ---------------------------------------------------------
        # SUPPORTING_EVIDENCE
        #
        # Shared evidence alone establishes possible support, but
        # not enough direction to fully confirm support.
        # ---------------------------------------------------------

        elif family == "SUPPORTING_EVIDENCE":

            if isinstance(
                evidence,
                list,
            ) and evidence:

                reasoning_status = "UNRESOLVED"
                reasoning_confidence = "LOW"
                reasoning_uncertainty = "HIGH"

                reasoning_basis.append(
                    "SHARED_SUPPORT_SURFACE_PRESENT"
                )

            else:
                reasoning_status = "REJECTED"
                relationship_rejected = True

                reasoning_basis.append(
                    "NO_SUPPORT_SURFACE"
                )

        # ---------------------------------------------------------
        # CONTRADICTION
        #
        # F already requires same-path differing values.
        # G can confirm a conflict signal, but H remains owner of
        # integrity/conflict guard and does not silently resolve it.
        # ---------------------------------------------------------

        elif family == "CONTRADICTION":

            if isinstance(
                evidence,
                list,
            ) and evidence:

                reasoning_status = "CONFLICT_DETECTED"
                relationship_confirmed = True
                reasoning_confidence = "MODERATE"
                reasoning_uncertainty = "HIGH"

                reasoning_basis.append(
                    "SAME_PATH_DIFFERING_VALUES"
                )

            else:
                reasoning_status = "REJECTED"
                relationship_rejected = True

                reasoning_basis.append(
                    "NO_CONTRADICTORY_PATH_EVIDENCE"
                )

        # ---------------------------------------------------------
        # SEMANTIC_OVERLAP
        # ---------------------------------------------------------

        elif family == "SEMANTIC_OVERLAP":

            if isinstance(
                evidence,
                list,
            ) and evidence:

                reasoning_status = "CONFIRMED"
                relationship_confirmed = True

                reasoning_basis.append(
                    "SHARED_SEMANTIC_EVIDENCE_PRESENT"
                )

            else:
                reasoning_status = "REJECTED"
                relationship_rejected = True

                reasoning_basis.append(
                    "NO_SEMANTIC_OVERLAP_EVIDENCE"
                )

        # ---------------------------------------------------------
        # POTENTIAL_DUPLICATION
        #
        # Candidate remains unresolved pending H conflict/
        # integrity review.
        # ---------------------------------------------------------

        elif family == "POTENTIAL_DUPLICATION":

            if isinstance(
                evidence,
                list,
            ) and evidence:

                reasoning_status = "UNRESOLVED"
                reasoning_confidence = "HIGH"
                reasoning_uncertainty = "MODERATE"

                reasoning_basis.append(
                    "HIGH_OVERLAP_SURFACE_PRESENT"
                )

            else:
                reasoning_status = "REJECTED"
                relationship_rejected = True

                reasoning_basis.append(
                    "NO_DUPLICATION_EVIDENCE"
                )

        # ---------------------------------------------------------
        # CAUSE_EFFECT
        #
        # Candidate explicitly used unresolved direction in F.
        # G preserves that uncertainty unless evidence already
        # establishes a clear direction.
        # ---------------------------------------------------------

        elif family == "CAUSE_EFFECT":

            direction = candidate.get(
                "directionality"
            )

            if (
                evidence
                and direction
                in (
                    "SOURCE_TO_TARGET",
                    "TARGET_TO_SOURCE",
                )
            ):

                reasoning_status = "CONFIRMED"
                relationship_confirmed = True
                reasoning_confidence = "MODERATE"
                reasoning_uncertainty = "MODERATE"

                reasoning_basis.append(
                    "EXPLICIT_CAUSAL_DIRECTION_AVAILABLE"
                )

            else:
                reasoning_status = "UNRESOLVED"
                reasoning_confidence = "LOW"
                reasoning_uncertainty = "HIGH"

                reasoning_basis.append(
                    "CAUSAL_DIRECTION_NOT_ESTABLISHED"
                )

        # ---------------------------------------------------------
        # Other architecture-approved families
        #
        # G may preserve them as unresolved when F generated a
        # valid evidence-bound candidate but the present executor
        # lacks sufficient family-specific proof to confirm.
        # ---------------------------------------------------------

        else:

            reasoning_status = "UNRESOLVED"
            reasoning_confidence = candidate.get(
                "confidence_state",
                "LOW",
            )
            reasoning_uncertainty = "HIGH"

            reasoning_basis.append(
                "FAMILY_REQUIRES_ADDITIONAL_EVIDENCE_INTERPRETATION"
            )

        reasoning_material = {
            "document_set_id":
                document_set[
                    "document_set_id"
                ],

            "reasoning_scope_id":
                reasoning_scope[
                    "reasoning_scope_id"
                ],

            "relationship_package_id":
                construction[
                    "relationship_package_id"
                ],

            "relationship_id":
                candidate[
                    "relationship_id"
                ],

            "relationship_family":
                family,

            "reasoning_status":
                reasoning_status,

            "reasoning_basis":
                reasoning_basis,

            "confidence_state":
                reasoning_confidence,

            "uncertainty_state":
                reasoning_uncertainty,
        }

        reasoning_json = json.dumps(
            reasoning_material,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )

        reasoning_digest = hashlib.sha256(
            reasoning_json.encode("utf-8")
        ).hexdigest()

        reasoning_id = (
            "cdrreason:v1:"
            + reasoning_digest[:32]
        )

        reasoned_relationships.append(
            {
                "reasoned_relationship_schema":
                    "cross_document_reasoned_relationship_v1",

                "reasoned_relationship_version":
                    "v1",

                "reasoning_id":
                    reasoning_id,

                "reasoning_digest":
                    reasoning_digest,

                "reasoning_digest_algorithm":
                    "SHA256",

                "source_relationship_id":
                    candidate[
                        "relationship_id"
                    ],

                "source_article_id":
                    candidate[
                        "source_article_id"
                    ],

                "target_article_id":
                    candidate[
                        "target_article_id"
                    ],

                "relationship_family":
                    family,

                "directionality":
                    candidate[
                        "directionality"
                    ],

                "reasoning_status":
                    reasoning_status,

                "relationship_confirmed":
                    relationship_confirmed,

                "relationship_rejected":
                    relationship_rejected,

                "reasoning_basis":
                    reasoning_basis,

                "confidence_state":
                    reasoning_confidence,

                "uncertainty_state":
                    reasoning_uncertainty,

                "evidence":
                    deepcopy(
                        candidate[
                            "evidence"
                        ]
                    ),

                "evidence_alignment_id":
                    candidate[
                        "evidence_alignment_id"
                    ],

                "evidence_bound":
                    True,

                "reasoning_trace_present":
                    True,

                "conflict_silently_resolved":
                    False,

                "unsupported_fact_inference":
                    False,

                "source_profile_modified":
                    False,

                "retrieval_payload_modified":
                    False,

                "cross_document_reasoning_performed":
                    True,

                "semantic_memory_written":
                    False,

                "linking_decision":
                    False,
            }
        )

    reasoned_relationships = sorted(
        reasoned_relationships,
        key=lambda item: (
            item[
                "source_article_id"
            ],
            item[
                "target_article_id"
            ],
            item[
                "relationship_family"
            ],
            item[
                "reasoning_id"
            ],
        ),
    )

    # -------------------------------------------------------------
    # Aggregate statuses
    # -------------------------------------------------------------

    status_counts = {}

    family_counts = {}

    for item in reasoned_relationships:

        status = item[
            "reasoning_status"
        ]

        family = item[
            "relationship_family"
        ]

        status_counts[
            status
        ] = (
            status_counts.get(
                status,
                0,
            )
            + 1
        )

        family_counts[
            family
        ] = (
            family_counts.get(
                family,
                0,
            )
            + 1
        )

    # -------------------------------------------------------------
    # Deterministic reasoning package identity
    # -------------------------------------------------------------

    package_material = {
        "document_set_id":
            document_set[
                "document_set_id"
            ],

        "reasoning_scope_id":
            reasoning_scope[
                "reasoning_scope_id"
            ],

        "relationship_package_id":
            construction[
                "relationship_package_id"
            ],

        "reasoning_ids": [
            item[
                "reasoning_id"
            ]
            for item in reasoned_relationships
        ],
    }

    package_json = json.dumps(
        package_material,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    package_digest = hashlib.sha256(
        package_json.encode("utf-8")
    ).hexdigest()

    reasoning_package_id = (
        "cdrreasoning:v1:"
        + package_digest[:32]
    )

    reasoning_execution = {
        "reasoning_execution_schema":
            "cross_document_reasoning_execution_v1",

        "reasoning_execution_version":
            "v1",

        "reasoning_package_id":
            reasoning_package_id,

        "reasoning_package_digest":
            package_digest,

        "reasoning_package_digest_algorithm":
            "SHA256",

        "document_set_id":
            document_set[
                "document_set_id"
            ],

        "reasoning_scope_id":
            reasoning_scope[
                "reasoning_scope_id"
            ],

        "evidence_alignment_id":
            evidence_alignment[
                "evidence_alignment_id"
            ],

        "relationship_package_id":
            construction[
                "relationship_package_id"
            ],

        "workspace_id":
            workspace_id,

        "reasoned_relationship_count":
            len(
                reasoned_relationships
            ),

        "reasoning_status_counts":
            status_counts,

        "relationship_family_counts":
            family_counts,

        "reasoned_relationships":
            reasoned_relationships,

        "cross_document_reasoning_performed":
            True,

        "evidence_bound":
            True,

        "reasoning_trace_complete":
            True,

        "unsupported_fact_inference_performed":
            False,

        "conflicts_silently_resolved":
            False,

        "source_profiles_preserved":
            True,

        "retrieval_payloads_preserved":
            True,

        "reasoning_integrity_verification_performed":
            False,

        "reasoning_provenance_built":
            False,

        "read_only":
            True,

        "semantic_memory_written":
            False,

        "linking_decisions_performed":
            False,
    }

    return {
        "schema_version":
            "cross_document_reasoning_execution_result_v1",

        "version":
            CROSS_DOCUMENT_REASONING_VERSION,

        "phase":
            CROSS_DOCUMENT_REASONING_PHASE,

        "patch":
            "4.6.21G",

        "status":
            "CROSS_DOCUMENT_REASONING_EXECUTED",

        "workspace_id":
            workspace_id,

        "document_set_contract":
            deepcopy(
                dict(document_set)
            ),

        "reasoning_scope_contract":
            deepcopy(
                dict(reasoning_scope)
            ),

        "evidence_alignment_contract":
            deepcopy(
                dict(evidence_alignment)
            ),

        "relationship_construction_contract":
            deepcopy(
                dict(construction)
            ),

        "reasoning_execution_contract":
            reasoning_execution,

        "cross_document_reasoning_architecture":
            deepcopy(
                dict(architecture)
            ),

        "source_relationship_construction_result":
            deepcopy(
                dict(relationship_result)
            ),

        "processing_boundaries": {
            "document_set_scope_contract_preserved":
                True,

            "evidence_alignment_preserved":
                True,

            "relationship_construction_preserved":
                True,

            "cross_document_reasoning_architecture_preserved":
                True,

            "source_profiles_preserved":
                True,

            "retrieval_payloads_preserved":
                True,

            "cross_document_evidence_alignment_performed":
                True,

            "cross_document_relationships_constructed":
                True,

            "cross_document_reasoning_performed":
                True,

            "reasoning_trace_built":
                True,

            "reasoning_integrity_verification_performed":
                False,

            "reasoning_provenance_built":
                False,

            "final_cross_document_reasoning_result_built":
                False,

            "full_cross_document_reasoning_certification_performed":
                False,

            "source_profile_modified":
                False,

            "retrieval_payload_modified":
                False,

            "evidence_invented":
                False,

            "unsupported_fact_inference_performed":
                False,

            "conflict_silently_resolved":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,
        },

        "reasoning_policy":
            "EVIDENCE_BOUND_CROSS_DOCUMENT_REASONING_EXECUTED",

        "next_stage":
            "reasoning_integrity_conflict_guard",
    }


# =====================================================================
# PATCH 4.6.21H ? Reasoning Integrity & Conflict Guard
# =====================================================================

def guard_cross_document_reasoning_integrity_v1(
    reasoning_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Independently verify the integrity of 4.6.21G reasoning and
    explicitly register unresolved conflicts.

    H does not:
    - create new semantic facts,
    - alter G reasoning outcomes,
    - silently resolve conflicts,
    - mutate source profiles or retrieval payloads,
    - write Semantic Memory,
    - make linking decisions.
    """

    from collections.abc import Mapping
    from copy import deepcopy
    import hashlib
    import json

    if not isinstance(
        reasoning_result,
        Mapping,
    ):
        raise CrossDocumentReasoningError(
            "reasoning_result must be a mapping."
        )

    # -------------------------------------------------------------
    # Exact 4.6.21G lifecycle
    # -------------------------------------------------------------

    for field, expected in (
        (
            "schema_version",
            "cross_document_reasoning_execution_result_v1",
        ),
        (
            "version",
            CROSS_DOCUMENT_REASONING_VERSION,
        ),
        (
            "phase",
            CROSS_DOCUMENT_REASONING_PHASE,
        ),
        (
            "patch",
            "4.6.21G",
        ),
        (
            "status",
            "CROSS_DOCUMENT_REASONING_EXECUTED",
        ),
        (
            "reasoning_policy",
            "EVIDENCE_BOUND_CROSS_DOCUMENT_REASONING_EXECUTED",
        ),
        (
            "next_stage",
            "reasoning_integrity_conflict_guard",
        ),
    ):

        if reasoning_result.get(field) != expected:
            raise CrossDocumentReasoningError(
                f"Invalid 4.6.21G lifecycle field: {field}"
            )

    workspace_id = reasoning_result.get(
        "workspace_id"
    )

    document_set = reasoning_result.get(
        "document_set_contract"
    )

    reasoning_scope = reasoning_result.get(
        "reasoning_scope_contract"
    )

    evidence_alignment = reasoning_result.get(
        "evidence_alignment_contract"
    )

    construction = reasoning_result.get(
        "relationship_construction_contract"
    )

    execution = reasoning_result.get(
        "reasoning_execution_contract"
    )

    architecture = reasoning_result.get(
        "cross_document_reasoning_architecture"
    )

    boundaries = reasoning_result.get(
        "processing_boundaries"
    )

    for name, value in (
        ("document_set_contract", document_set),
        ("reasoning_scope_contract", reasoning_scope),
        ("evidence_alignment_contract", evidence_alignment),
        ("relationship_construction_contract", construction),
        ("reasoning_execution_contract", execution),
        (
            "cross_document_reasoning_architecture",
            architecture,
        ),
        ("processing_boundaries", boundaries),
    ):

        if not isinstance(
            value,
            Mapping,
        ):
            raise CrossDocumentReasoningError(
                name + " is missing."
            )

    # -------------------------------------------------------------
    # G execution authority
    # -------------------------------------------------------------

    if execution.get(
        "reasoning_execution_schema"
    ) != "cross_document_reasoning_execution_v1":
        raise CrossDocumentReasoningError(
            "Reasoning execution schema drifted."
        )

    if execution.get(
        "reasoning_execution_version"
    ) != "v1":
        raise CrossDocumentReasoningError(
            "Reasoning execution version drifted."
        )

    if execution.get(
        "document_set_id"
    ) != document_set.get(
        "document_set_id"
    ):
        raise CrossDocumentReasoningError(
            "Reasoning execution document-set identity drifted."
        )

    if execution.get(
        "reasoning_scope_id"
    ) != reasoning_scope.get(
        "reasoning_scope_id"
    ):
        raise CrossDocumentReasoningError(
            "Reasoning execution scope identity drifted."
        )

    if execution.get(
        "evidence_alignment_id"
    ) != evidence_alignment.get(
        "evidence_alignment_id"
    ):
        raise CrossDocumentReasoningError(
            "Reasoning execution alignment identity drifted."
        )

    if execution.get(
        "relationship_package_id"
    ) != construction.get(
        "relationship_package_id"
    ):
        raise CrossDocumentReasoningError(
            "Reasoning execution relationship package drifted."
        )

    for field in (
        "cross_document_reasoning_performed",
        "evidence_bound",
        "reasoning_trace_complete",
        "source_profiles_preserved",
        "retrieval_payloads_preserved",
        "read_only",
    ):

        if execution.get(field) is not True:
            raise CrossDocumentReasoningError(
                f"Required G execution field is not True: {field}"
            )

    for field in (
        "unsupported_fact_inference_performed",
        "conflicts_silently_resolved",
        "reasoning_integrity_verification_performed",
        "reasoning_provenance_built",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if execution.get(field) is not False:
            raise CrossDocumentReasoningError(
                f"Forbidden G execution field is not False: {field}"
            )

    reasoned_relationships = execution.get(
        "reasoned_relationships"
    )

    candidates = construction.get(
        "relationship_candidates"
    )

    if not isinstance(
        reasoned_relationships,
        list,
    ):
        raise CrossDocumentReasoningError(
            "Reasoned relationships are missing."
        )

    if not isinstance(
        candidates,
        list,
    ):
        raise CrossDocumentReasoningError(
            "Source relationship candidates are missing."
        )

    if len(
        reasoned_relationships
    ) != execution.get(
        "reasoned_relationship_count"
    ):
        raise CrossDocumentReasoningError(
            "Reasoned relationship count drifted."
        )

    if len(
        reasoned_relationships
    ) != len(
        candidates
    ):
        raise CrossDocumentReasoningError(
            "Reasoned relationship / candidate count mismatch."
        )

    # -------------------------------------------------------------
    # Architecture conflict-guard authority
    # -------------------------------------------------------------

    if architecture.get(
        "architecture_status"
    ) != "DEFINED":
        raise CrossDocumentReasoningError(
            "Cross-Document Reasoning architecture is not defined."
        )

    execution_contract = architecture.get(
        "execution_contract"
    )

    guard_contract = architecture.get(
        "conflict_guard_contract"
    )

    if not isinstance(
        execution_contract,
        Mapping,
    ):
        raise CrossDocumentReasoningError(
            "Execution contract is missing."
        )

    if not isinstance(
        guard_contract,
        Mapping,
    ):
        raise CrossDocumentReasoningError(
            "Conflict guard contract is missing."
        )

    if execution_contract.get(
        "4.6.21H"
    ) != "INTEGRITY_AND_CONFLICT_GUARD":
        raise CrossDocumentReasoningError(
            "4.6.21H execution contract drifted."
        )

    for field in (
        "detect_claim_conflicts",
        "detect_relation_conflicts",
        "detect_identity_conflicts",
        "detect_evidence_conflicts",
        "detect_scope_violations",
        "conflict_must_not_be_silently_resolved",
        "uncertainty_must_be_preserved",
        "conflict_evidence_trace_required",
    ):

        if guard_contract.get(field) is not True:
            raise CrossDocumentReasoningError(
                f"Required conflict-guard field is not True: {field}"
            )

    # -------------------------------------------------------------
    # G processing-boundary authority
    # -------------------------------------------------------------

    for field in (
        "document_set_scope_contract_preserved",
        "evidence_alignment_preserved",
        "relationship_construction_preserved",
        "cross_document_reasoning_architecture_preserved",
        "source_profiles_preserved",
        "retrieval_payloads_preserved",
        "cross_document_evidence_alignment_performed",
        "cross_document_relationships_constructed",
        "cross_document_reasoning_performed",
        "reasoning_trace_built",
    ):

        if boundaries.get(field) is not True:
            raise CrossDocumentReasoningError(
                f"Required 4.6.21G boundary is not True: {field}"
            )

    for field in (
        "reasoning_integrity_verification_performed",
        "reasoning_provenance_built",
        "final_cross_document_reasoning_result_built",
        "full_cross_document_reasoning_certification_performed",
        "source_profile_modified",
        "retrieval_payload_modified",
        "evidence_invented",
        "unsupported_fact_inference_performed",
        "conflict_silently_resolved",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if boundaries.get(field) is not False:
            raise CrossDocumentReasoningError(
                f"Forbidden 4.6.21G boundary is not False: {field}"
            )

    # -------------------------------------------------------------
    # Candidate index
    # -------------------------------------------------------------

    candidates_by_id = {}

    for candidate in candidates:

        if not isinstance(
            candidate,
            Mapping,
        ):
            raise CrossDocumentReasoningError(
                "Relationship candidate entry is invalid."
            )

        relationship_id = candidate.get(
            "relationship_id"
        )

        if not isinstance(
            relationship_id,
            str,
        ) or not relationship_id:
            raise CrossDocumentReasoningError(
                "Candidate relationship_id is invalid."
            )

        if relationship_id in candidates_by_id:
            raise CrossDocumentReasoningError(
                "Duplicate candidate relationship_id detected."
            )

        candidates_by_id[
            relationship_id
        ] = candidate

    # -------------------------------------------------------------
    # Independently verify each reasoned relationship
    # -------------------------------------------------------------

    guarded_relationships = []
    conflict_registry = []
    unresolved_registry = []
    rejected_registry = []

    seen_reasoning_ids = set()
    seen_source_relationship_ids = set()

    for item in reasoned_relationships:

        if not isinstance(
            item,
            Mapping,
        ):
            raise CrossDocumentReasoningError(
                "Reasoned relationship entry is invalid."
            )

        if item.get(
            "reasoned_relationship_schema"
        ) != "cross_document_reasoned_relationship_v1":
            raise CrossDocumentReasoningError(
                "Reasoned relationship schema drifted."
            )

        if item.get(
            "reasoned_relationship_version"
        ) != "v1":
            raise CrossDocumentReasoningError(
                "Reasoned relationship version drifted."
            )

        source_relationship_id = item.get(
            "source_relationship_id"
        )

        if source_relationship_id not in candidates_by_id:
            raise CrossDocumentReasoningError(
                "Reasoned relationship references unknown candidate."
            )

        if source_relationship_id in seen_source_relationship_ids:
            raise CrossDocumentReasoningError(
                "Candidate was reasoned more than once."
            )

        seen_source_relationship_ids.add(
            source_relationship_id
        )

        candidate = candidates_by_id[
            source_relationship_id
        ]

        # ---------------------------------------------------------
        # Candidate/result identity preservation
        # ---------------------------------------------------------

        for field in (
            "source_article_id",
            "target_article_id",
            "relationship_family",
            "directionality",
            "evidence_alignment_id",
        ):

            if item.get(field) != candidate.get(field):
                raise CrossDocumentReasoningError(
                    f"Reasoned relationship drifted from candidate: {field}"
                )

        if item.get(
            "evidence"
        ) != candidate.get(
            "evidence"
        ):
            raise CrossDocumentReasoningError(
                "Reasoned evidence drifted from source candidate."
            )

        # ---------------------------------------------------------
        # Required reasoning flags
        # ---------------------------------------------------------

        for field in (
            "evidence_bound",
            "reasoning_trace_present",
            "cross_document_reasoning_performed",
        ):

            if item.get(field) is not True:
                raise CrossDocumentReasoningError(
                    f"Required reasoned field is not True: {field}"
                )

        for field in (
            "conflict_silently_resolved",
            "unsupported_fact_inference",
            "source_profile_modified",
            "retrieval_payload_modified",
            "semantic_memory_written",
            "linking_decision",
        ):

            if item.get(field) is not False:
                raise CrossDocumentReasoningError(
                    f"Forbidden reasoned field is not False: {field}"
                )

        status = item.get(
            "reasoning_status"
        )

        confirmed = item.get(
            "relationship_confirmed"
        )

        rejected = item.get(
            "relationship_rejected"
        )

        basis = item.get(
            "reasoning_basis"
        )

        confidence = item.get(
            "confidence_state"
        )

        uncertainty = item.get(
            "uncertainty_state"
        )

        if status not in (
            "CONFIRMED",
            "REJECTED",
            "UNRESOLVED",
            "CONFLICT_DETECTED",
        ):
            raise CrossDocumentReasoningError(
                "Unsupported reasoning status."
            )

        if not isinstance(
            confirmed,
            bool,
        ) or not isinstance(
            rejected,
            bool,
        ):
            raise CrossDocumentReasoningError(
                "Reasoning confirmation flags must be boolean."
            )

        if confirmed and rejected:
            raise CrossDocumentReasoningError(
                "A relationship cannot be both confirmed and rejected."
            )

        if not isinstance(
            basis,
            list,
        ) or not basis:
            raise CrossDocumentReasoningError(
                "Reasoning basis is missing."
            )

        if not isinstance(
            confidence,
            str,
        ) or not confidence:
            raise CrossDocumentReasoningError(
                "Confidence state is invalid."
            )

        if not isinstance(
            uncertainty,
            str,
        ) or not uncertainty:
            raise CrossDocumentReasoningError(
                "Uncertainty state is invalid."
            )

        # ---------------------------------------------------------
        # Status consistency
        # ---------------------------------------------------------

        if status == "CONFIRMED":

            if confirmed is not True:
                raise CrossDocumentReasoningError(
                    "CONFIRMED status requires relationship_confirmed=True."
                )

            if rejected is not False:
                raise CrossDocumentReasoningError(
                    "CONFIRMED status requires relationship_rejected=False."
                )

        elif status == "REJECTED":

            if confirmed is not False:
                raise CrossDocumentReasoningError(
                    "REJECTED status cannot be confirmed."
                )

            if rejected is not True:
                raise CrossDocumentReasoningError(
                    "REJECTED status requires relationship_rejected=True."
                )

        elif status == "UNRESOLVED":

            if confirmed is not False:
                raise CrossDocumentReasoningError(
                    "UNRESOLVED status cannot be confirmed."
                )

            if rejected is not False:
                raise CrossDocumentReasoningError(
                    "UNRESOLVED status cannot be rejected."
                )

        elif status == "CONFLICT_DETECTED":

            if confirmed is not True:
                raise CrossDocumentReasoningError(
                    "CONFLICT_DETECTED must confirm the existence of a conflict signal."
                )

            if rejected is not False:
                raise CrossDocumentReasoningError(
                    "CONFLICT_DETECTED cannot be rejected."
                )

            if uncertainty not in (
                "HIGH",
                "MODERATE",
            ):
                raise CrossDocumentReasoningError(
                    "Conflict uncertainty must remain explicit."
                )

        # ---------------------------------------------------------
        # Independent deterministic reasoning digest verification
        # ---------------------------------------------------------

        reasoning_material = {
            "document_set_id":
                document_set[
                    "document_set_id"
                ],

            "reasoning_scope_id":
                reasoning_scope[
                    "reasoning_scope_id"
                ],

            "relationship_package_id":
                construction[
                    "relationship_package_id"
                ],

            "relationship_id":
                source_relationship_id,

            "relationship_family":
                item[
                    "relationship_family"
                ],

            "reasoning_status":
                status,

            "reasoning_basis":
                basis,

            "confidence_state":
                confidence,

            "uncertainty_state":
                uncertainty,
        }

        reasoning_json = json.dumps(
            reasoning_material,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )

        expected_digest = hashlib.sha256(
            reasoning_json.encode("utf-8")
        ).hexdigest()

        expected_id = (
            "cdrreason:v1:"
            + expected_digest[:32]
        )

        if item.get(
            "reasoning_digest"
        ) != expected_digest:
            raise CrossDocumentReasoningError(
                "Reasoning digest verification failed."
            )

        if item.get(
            "reasoning_id"
        ) != expected_id:
            raise CrossDocumentReasoningError(
                "Reasoning ID verification failed."
            )

        if expected_id in seen_reasoning_ids:
            raise CrossDocumentReasoningError(
                "Duplicate reasoning_id detected."
            )

        seen_reasoning_ids.add(
            expected_id
        )

        # ---------------------------------------------------------
        # Conflict and unresolved registries
        # ---------------------------------------------------------

        conflict_detected = (
            status == "CONFLICT_DETECTED"
        )

        unresolved = (
            status == "UNRESOLVED"
        )

        rejected_state = (
            status == "REJECTED"
        )

        if conflict_detected:

            conflict_registry.append(
                {
                    "conflict_id":
                        (
                            "cdrconflict:v1:"
                            + expected_digest[:32]
                        ),

                    "reasoning_id":
                        expected_id,

                    "source_relationship_id":
                        source_relationship_id,

                    "source_article_id":
                        item[
                            "source_article_id"
                        ],

                    "target_article_id":
                        item[
                            "target_article_id"
                        ],

                    "relationship_family":
                        item[
                            "relationship_family"
                        ],

                    "conflict_status":
                        "OPEN",

                    "conflict_evidence":
                        deepcopy(
                            item[
                                "evidence"
                            ]
                        ),

                    "uncertainty_state":
                        uncertainty,

                    "silently_resolved":
                        False,

                    "requires_downstream_review":
                        True,
                }
            )

        if unresolved:

            unresolved_registry.append(
                {
                    "reasoning_id":
                        expected_id,

                    "source_relationship_id":
                        source_relationship_id,

                    "relationship_family":
                        item[
                            "relationship_family"
                        ],

                    "uncertainty_state":
                        uncertainty,

                    "resolution_status":
                        "UNRESOLVED_PRESERVED",
                }
            )

        if rejected_state:

            rejected_registry.append(
                {
                    "reasoning_id":
                        expected_id,

                    "source_relationship_id":
                        source_relationship_id,

                    "relationship_family":
                        item[
                            "relationship_family"
                        ],

                    "rejection_status":
                        "REJECTED_PRESERVED",
                }
            )

        guarded_relationship = deepcopy(
            dict(item)
        )

        guarded_relationship[
            "reasoning_integrity_verified"
        ] = True

        guarded_relationship[
            "candidate_identity_verified"
        ] = True

        guarded_relationship[
            "evidence_integrity_verified"
        ] = True

        guarded_relationship[
            "status_consistency_verified"
        ] = True

        guarded_relationship[
            "uncertainty_preserved"
        ] = True

        guarded_relationship[
            "conflict_guard_applied"
        ] = True

        guarded_relationship[
            "conflict_detected"
        ] = conflict_detected

        guarded_relationship[
            "conflict_resolved"
        ] = False

        guarded_relationships.append(
            guarded_relationship
        )

    if len(
        seen_source_relationship_ids
    ) != len(
        candidates
    ):
        raise CrossDocumentReasoningError(
            "Not every source candidate was reasoned exactly once."
        )

    guarded_relationships = sorted(
        guarded_relationships,
        key=lambda item: (
            item[
                "source_article_id"
            ],
            item[
                "target_article_id"
            ],
            item[
                "relationship_family"
            ],
            item[
                "reasoning_id"
            ],
        ),
    )

    conflict_registry = sorted(
        conflict_registry,
        key=lambda item: item[
            "conflict_id"
        ],
    )

    unresolved_registry = sorted(
        unresolved_registry,
        key=lambda item: item[
            "reasoning_id"
        ],
    )

    rejected_registry = sorted(
        rejected_registry,
        key=lambda item: item[
            "reasoning_id"
        ],
    )

    # -------------------------------------------------------------
    # Independently verify G package digest
    # -------------------------------------------------------------

    package_material = {
        "document_set_id":
            document_set[
                "document_set_id"
            ],

        "reasoning_scope_id":
            reasoning_scope[
                "reasoning_scope_id"
            ],

        "relationship_package_id":
            construction[
                "relationship_package_id"
            ],

        "reasoning_ids": [
            item[
                "reasoning_id"
            ]
            for item in guarded_relationships
        ],
    }

    package_json = json.dumps(
        package_material,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    expected_package_digest = hashlib.sha256(
        package_json.encode("utf-8")
    ).hexdigest()

    expected_package_id = (
        "cdrreasoning:v1:"
        + expected_package_digest[:32]
    )

    if execution.get(
        "reasoning_package_digest"
    ) != expected_package_digest:
        raise CrossDocumentReasoningError(
            "Reasoning package digest verification failed."
        )

    if execution.get(
        "reasoning_package_id"
    ) != expected_package_id:
        raise CrossDocumentReasoningError(
            "Reasoning package ID verification failed."
        )

    # -------------------------------------------------------------
    # Build deterministic integrity package
    # -------------------------------------------------------------

    integrity_material = {
        "document_set_id":
            document_set[
                "document_set_id"
            ],

        "reasoning_scope_id":
            reasoning_scope[
                "reasoning_scope_id"
            ],

        "relationship_package_id":
            construction[
                "relationship_package_id"
            ],

        "reasoning_package_id":
            execution[
                "reasoning_package_id"
            ],

        "verified_reasoning_ids": [
            item[
                "reasoning_id"
            ]
            for item in guarded_relationships
        ],

        "conflict_ids": [
            item[
                "conflict_id"
            ]
            for item in conflict_registry
        ],

        "unresolved_reasoning_ids": [
            item[
                "reasoning_id"
            ]
            for item in unresolved_registry
        ],
    }

    integrity_json = json.dumps(
        integrity_material,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    integrity_digest = hashlib.sha256(
        integrity_json.encode("utf-8")
    ).hexdigest()

    integrity_guard_id = (
        "cdrguard:v1:"
        + integrity_digest[:32]
    )

    status_counts = {}

    for item in guarded_relationships:

        status = item[
            "reasoning_status"
        ]

        status_counts[
            status
        ] = (
            status_counts.get(
                status,
                0,
            )
            + 1
        )

    guard_result = {
        "reasoning_integrity_guard_schema":
            "cross_document_reasoning_integrity_guard_v1",

        "reasoning_integrity_guard_version":
            "v1",

        "reasoning_integrity_guard_id":
            integrity_guard_id,

        "reasoning_integrity_guard_digest":
            integrity_digest,

        "reasoning_integrity_guard_digest_algorithm":
            "SHA256",

        "document_set_id":
            document_set[
                "document_set_id"
            ],

        "reasoning_scope_id":
            reasoning_scope[
                "reasoning_scope_id"
            ],

        "relationship_package_id":
            construction[
                "relationship_package_id"
            ],

        "reasoning_package_id":
            execution[
                "reasoning_package_id"
            ],

        "workspace_id":
            workspace_id,

        "reasoned_relationship_count":
            len(
                guarded_relationships
            ),

        "reasoning_status_counts":
            status_counts,

        "conflict_count":
            len(
                conflict_registry
            ),

        "unresolved_count":
            len(
                unresolved_registry
            ),

        "rejected_count":
            len(
                rejected_registry
            ),

        "guarded_reasoned_relationships":
            guarded_relationships,

        "conflict_registry":
            conflict_registry,

        "unresolved_registry":
            unresolved_registry,

        "rejected_registry":
            rejected_registry,

        "reasoning_integrity_verification_performed":
            True,

        "all_reasoning_digests_verified":
            True,

        "all_reasoning_ids_verified":
            True,

        "all_candidate_bindings_verified":
            True,

        "all_evidence_bindings_verified":
            True,

        "status_consistency_verified":
            True,

        "uncertainty_preserved":
            True,

        "conflicts_explicit":
            True,

        "conflicts_silently_resolved":
            False,

        "source_profiles_preserved":
            True,

        "retrieval_payloads_preserved":
            True,

        "evidence_invented":
            False,

        "unsupported_fact_inference_performed":
            False,

        "reasoning_provenance_built":
            False,

        "final_result_built":
            False,

        "read_only":
            True,

        "semantic_memory_written":
            False,

        "linking_decisions_performed":
            False,
    }

    return {
        "schema_version":
            "cross_document_reasoning_integrity_guard_result_v1",

        "version":
            CROSS_DOCUMENT_REASONING_VERSION,

        "phase":
            CROSS_DOCUMENT_REASONING_PHASE,

        "patch":
            "4.6.21H",

        "status":
            "CROSS_DOCUMENT_REASONING_INTEGRITY_VERIFIED",

        "workspace_id":
            workspace_id,

        "document_set_contract":
            deepcopy(
                dict(document_set)
            ),

        "reasoning_scope_contract":
            deepcopy(
                dict(reasoning_scope)
            ),

        "evidence_alignment_contract":
            deepcopy(
                dict(evidence_alignment)
            ),

        "relationship_construction_contract":
            deepcopy(
                dict(construction)
            ),

        "reasoning_execution_contract":
            deepcopy(
                dict(execution)
            ),

        "reasoning_integrity_guard":
            guard_result,

        "cross_document_reasoning_architecture":
            deepcopy(
                dict(architecture)
            ),

        "source_reasoning_execution_result":
            deepcopy(
                dict(reasoning_result)
            ),

        "processing_boundaries": {
            "document_set_scope_contract_preserved":
                True,

            "evidence_alignment_preserved":
                True,

            "relationship_construction_preserved":
                True,

            "reasoning_execution_preserved":
                True,

            "cross_document_reasoning_architecture_preserved":
                True,

            "source_profiles_preserved":
                True,

            "retrieval_payloads_preserved":
                True,

            "cross_document_evidence_alignment_performed":
                True,

            "cross_document_relationships_constructed":
                True,

            "cross_document_reasoning_performed":
                True,

            "reasoning_trace_preserved":
                True,

            "reasoning_integrity_verification_performed":
                True,

            "conflict_guard_applied":
                True,

            "uncertainty_preserved":
                True,

            "reasoning_provenance_built":
                False,

            "final_cross_document_reasoning_result_built":
                False,

            "full_cross_document_reasoning_certification_performed":
                False,

            "source_profile_modified":
                False,

            "retrieval_payload_modified":
                False,

            "evidence_invented":
                False,

            "unsupported_fact_inference_performed":
                False,

            "conflict_silently_resolved":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,
        },

        "reasoning_policy":
            "REASONING_INTEGRITY_AND_CONFLICT_GUARD_VERIFIED",

        "next_stage":
            "reasoning_provenance_evidence_trace",
    }


# =====================================================================
# PATCH 4.6.21I ? Reasoning Provenance & Evidence Trace
# =====================================================================

def build_cross_document_reasoning_provenance_v1(
    guard_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Build the complete immutable provenance and evidence trace
    for certified cross-document reasoning.

    I does not change:
    - reasoning outcomes,
    - conflict state,
    - uncertainty,
    - source profiles,
    - retrieval payloads.

    I performs no Semantic Memory writes and no linking decisions.
    """

    from collections.abc import Mapping
    from copy import deepcopy
    import hashlib
    import json

    if not isinstance(
        guard_result,
        Mapping,
    ):
        raise CrossDocumentReasoningError(
            "guard_result must be a mapping."
        )

    # -------------------------------------------------------------
    # Exact 4.6.21H lifecycle
    # -------------------------------------------------------------

    for field, expected in (
        (
            "schema_version",
            "cross_document_reasoning_integrity_guard_result_v1",
        ),
        (
            "version",
            CROSS_DOCUMENT_REASONING_VERSION,
        ),
        (
            "phase",
            CROSS_DOCUMENT_REASONING_PHASE,
        ),
        (
            "patch",
            "4.6.21H",
        ),
        (
            "status",
            "CROSS_DOCUMENT_REASONING_INTEGRITY_VERIFIED",
        ),
        (
            "reasoning_policy",
            "REASONING_INTEGRITY_AND_CONFLICT_GUARD_VERIFIED",
        ),
        (
            "next_stage",
            "reasoning_provenance_evidence_trace",
        ),
    ):

        if guard_result.get(field) != expected:
            raise CrossDocumentReasoningError(
                f"Invalid 4.6.21H lifecycle field: {field}"
            )

    workspace_id = guard_result.get(
        "workspace_id"
    )

    document_set = guard_result.get(
        "document_set_contract"
    )

    reasoning_scope = guard_result.get(
        "reasoning_scope_contract"
    )

    evidence_alignment = guard_result.get(
        "evidence_alignment_contract"
    )

    construction = guard_result.get(
        "relationship_construction_contract"
    )

    execution = guard_result.get(
        "reasoning_execution_contract"
    )

    integrity_guard = guard_result.get(
        "reasoning_integrity_guard"
    )

    architecture = guard_result.get(
        "cross_document_reasoning_architecture"
    )

    boundaries = guard_result.get(
        "processing_boundaries"
    )

    for name, value in (
        ("document_set_contract", document_set),
        ("reasoning_scope_contract", reasoning_scope),
        ("evidence_alignment_contract", evidence_alignment),
        ("relationship_construction_contract", construction),
        ("reasoning_execution_contract", execution),
        ("reasoning_integrity_guard", integrity_guard),
        (
            "cross_document_reasoning_architecture",
            architecture,
        ),
        ("processing_boundaries", boundaries),
    ):

        if not isinstance(
            value,
            Mapping,
        ):
            raise CrossDocumentReasoningError(
                name + " is missing."
            )

    # -------------------------------------------------------------
    # H integrity authority
    # -------------------------------------------------------------

    if integrity_guard.get(
        "reasoning_integrity_guard_schema"
    ) != "cross_document_reasoning_integrity_guard_v1":
        raise CrossDocumentReasoningError(
            "Integrity guard schema drifted."
        )

    if integrity_guard.get(
        "reasoning_integrity_guard_version"
    ) != "v1":
        raise CrossDocumentReasoningError(
            "Integrity guard version drifted."
        )

    if integrity_guard.get(
        "document_set_id"
    ) != document_set.get(
        "document_set_id"
    ):
        raise CrossDocumentReasoningError(
            "Integrity guard document-set identity drifted."
        )

    if integrity_guard.get(
        "reasoning_scope_id"
    ) != reasoning_scope.get(
        "reasoning_scope_id"
    ):
        raise CrossDocumentReasoningError(
            "Integrity guard reasoning-scope identity drifted."
        )

    if integrity_guard.get(
        "relationship_package_id"
    ) != construction.get(
        "relationship_package_id"
    ):
        raise CrossDocumentReasoningError(
            "Integrity guard relationship package drifted."
        )

    if integrity_guard.get(
        "reasoning_package_id"
    ) != execution.get(
        "reasoning_package_id"
    ):
        raise CrossDocumentReasoningError(
            "Integrity guard reasoning package drifted."
        )

    for field in (
        "reasoning_integrity_verification_performed",
        "all_reasoning_digests_verified",
        "all_reasoning_ids_verified",
        "all_candidate_bindings_verified",
        "all_evidence_bindings_verified",
        "status_consistency_verified",
        "uncertainty_preserved",
        "conflicts_explicit",
        "source_profiles_preserved",
        "retrieval_payloads_preserved",
        "read_only",
    ):

        if integrity_guard.get(field) is not True:
            raise CrossDocumentReasoningError(
                f"Required H guard field is not True: {field}"
            )

    for field in (
        "conflicts_silently_resolved",
        "evidence_invented",
        "unsupported_fact_inference_performed",
        "reasoning_provenance_built",
        "final_result_built",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if integrity_guard.get(field) is not False:
            raise CrossDocumentReasoningError(
                f"Forbidden H guard field is not False: {field}"
            )

    guarded_relationships = integrity_guard.get(
        "guarded_reasoned_relationships"
    )

    conflict_registry = integrity_guard.get(
        "conflict_registry"
    )

    unresolved_registry = integrity_guard.get(
        "unresolved_registry"
    )

    rejected_registry = integrity_guard.get(
        "rejected_registry"
    )

    for name, value in (
        (
            "guarded_reasoned_relationships",
            guarded_relationships,
        ),
        (
            "conflict_registry",
            conflict_registry,
        ),
        (
            "unresolved_registry",
            unresolved_registry,
        ),
        (
            "rejected_registry",
            rejected_registry,
        ),
    ):

        if not isinstance(
            value,
            list,
        ):
            raise CrossDocumentReasoningError(
                name + " must be a list."
            )

    # -------------------------------------------------------------
    # Architecture provenance authority
    # -------------------------------------------------------------

    if architecture.get(
        "architecture_status"
    ) != "DEFINED":
        raise CrossDocumentReasoningError(
            "Cross-Document Reasoning architecture is not defined."
        )

    execution_contract = architecture.get(
        "execution_contract"
    )

    provenance_contract = architecture.get(
        "provenance_contract"
    )

    if not isinstance(
        execution_contract,
        Mapping,
    ):
        raise CrossDocumentReasoningError(
            "Execution contract is missing."
        )

    if not isinstance(
        provenance_contract,
        Mapping,
    ):
        raise CrossDocumentReasoningError(
            "Provenance contract is missing."
        )

    if execution_contract.get(
        "4.6.21I"
    ) != "PROVENANCE_AND_EVIDENCE_TRACE":
        raise CrossDocumentReasoningError(
            "4.6.21I execution contract drifted."
        )

    for field in (
        "document_lineage_required",
        "relationship_lineage_required",
        "evidence_trace_required",
        "reasoning_trace_required",
        "result_digest_required",
    ):

        if provenance_contract.get(field) is not True:
            raise CrossDocumentReasoningError(
                f"Required provenance field is not True: {field}"
            )

    # -------------------------------------------------------------
    # H boundary authority
    # -------------------------------------------------------------

    for field in (
        "document_set_scope_contract_preserved",
        "evidence_alignment_preserved",
        "relationship_construction_preserved",
        "reasoning_execution_preserved",
        "cross_document_reasoning_architecture_preserved",
        "source_profiles_preserved",
        "retrieval_payloads_preserved",
        "cross_document_evidence_alignment_performed",
        "cross_document_relationships_constructed",
        "cross_document_reasoning_performed",
        "reasoning_trace_preserved",
        "reasoning_integrity_verification_performed",
        "conflict_guard_applied",
        "uncertainty_preserved",
    ):

        if boundaries.get(field) is not True:
            raise CrossDocumentReasoningError(
                f"Required 4.6.21H boundary is not True: {field}"
            )

    for field in (
        "reasoning_provenance_built",
        "final_cross_document_reasoning_result_built",
        "full_cross_document_reasoning_certification_performed",
        "source_profile_modified",
        "retrieval_payload_modified",
        "evidence_invented",
        "unsupported_fact_inference_performed",
        "conflict_silently_resolved",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if boundaries.get(field) is not False:
            raise CrossDocumentReasoningError(
                f"Forbidden 4.6.21H boundary is not False: {field}"
            )

    # -------------------------------------------------------------
    # Build lookup indexes
    # -------------------------------------------------------------

    candidates = construction.get(
        "relationship_candidates"
    )

    pair_alignments = evidence_alignment.get(
        "pairwise_alignments"
    )

    aligned_documents = evidence_alignment.get(
        "documents"
    )

    if not isinstance(
        candidates,
        list,
    ):
        raise CrossDocumentReasoningError(
            "Relationship candidates are missing."
        )

    if not isinstance(
        pair_alignments,
        list,
    ):
        raise CrossDocumentReasoningError(
            "Pair alignments are missing."
        )

    if not isinstance(
        aligned_documents,
        list,
    ):
        raise CrossDocumentReasoningError(
            "Aligned documents are missing."
        )

    candidate_by_id = {}

    for candidate in candidates:

        if not isinstance(
            candidate,
            Mapping,
        ):
            raise CrossDocumentReasoningError(
                "Candidate entry is invalid."
            )

        relationship_id = candidate.get(
            "relationship_id"
        )

        if relationship_id in candidate_by_id:
            raise CrossDocumentReasoningError(
                "Duplicate relationship candidate ID."
            )

        candidate_by_id[
            relationship_id
        ] = candidate

    pair_by_id = {}

    for pair in pair_alignments:

        if not isinstance(
            pair,
            Mapping,
        ):
            raise CrossDocumentReasoningError(
                "Pair alignment entry is invalid."
            )

        alignment_id = pair.get(
            "alignment_id"
        )

        if alignment_id in pair_by_id:
            raise CrossDocumentReasoningError(
                "Duplicate pair alignment ID."
            )

        pair_by_id[
            alignment_id
        ] = pair

    document_by_article = {}

    for document in aligned_documents:

        if not isinstance(
            document,
            Mapping,
        ):
            raise CrossDocumentReasoningError(
                "Aligned document entry is invalid."
            )

        article_id = document.get(
            "article_id"
        )

        if article_id in document_by_article:
            raise CrossDocumentReasoningError(
                "Duplicate aligned article identity."
            )

        document_by_article[
            article_id
        ] = document

    # -------------------------------------------------------------
    # Construct relationship-level provenance traces
    # -------------------------------------------------------------

    relationship_traces = []

    for guarded in guarded_relationships:

        if not isinstance(
            guarded,
            Mapping,
        ):
            raise CrossDocumentReasoningError(
                "Guarded reasoning entry is invalid."
            )

        source_relationship_id = guarded.get(
            "source_relationship_id"
        )

        candidate = candidate_by_id.get(
            source_relationship_id
        )

        if candidate is None:
            raise CrossDocumentReasoningError(
                "Guarded reasoning references unknown candidate."
            )

        alignment_id = guarded.get(
            "evidence_alignment_id"
        )

        pair = pair_by_id.get(
            alignment_id
        )

        if pair is None:
            raise CrossDocumentReasoningError(
                "Guarded reasoning references unknown alignment."
            )

        source_article_id = guarded.get(
            "source_article_id"
        )

        target_article_id = guarded.get(
            "target_article_id"
        )

        source_document = document_by_article.get(
            source_article_id
        )

        target_document = document_by_article.get(
            target_article_id
        )

        if source_document is None:
            raise CrossDocumentReasoningError(
                "Source document lineage is missing."
            )

        if target_document is None:
            raise CrossDocumentReasoningError(
                "Target document lineage is missing."
            )

        if candidate.get(
            "evidence"
        ) != guarded.get(
            "evidence"
        ):
            raise CrossDocumentReasoningError(
                "Candidate/guarded evidence mismatch."
            )

        if pair.get(
            "source_article_id"
        ) != source_article_id:
            raise CrossDocumentReasoningError(
                "Source article / alignment lineage mismatch."
            )

        if pair.get(
            "target_article_id"
        ) != target_article_id:
            raise CrossDocumentReasoningError(
                "Target article / alignment lineage mismatch."
            )

        relationship_trace_material = {
            "document_set_id":
                document_set[
                    "document_set_id"
                ],

            "reasoning_scope_id":
                reasoning_scope[
                    "reasoning_scope_id"
                ],

            "evidence_alignment_id":
                evidence_alignment[
                    "evidence_alignment_id"
                ],

            "relationship_package_id":
                construction[
                    "relationship_package_id"
                ],

            "reasoning_package_id":
                execution[
                    "reasoning_package_id"
                ],

            "integrity_guard_id":
                integrity_guard[
                    "reasoning_integrity_guard_id"
                ],

            "source_relationship_id":
                source_relationship_id,

            "reasoning_id":
                guarded[
                    "reasoning_id"
                ],

            "pair_alignment_id":
                alignment_id,

            "source_article_id":
                source_article_id,

            "target_article_id":
                target_article_id,

            "source_evidence_digest":
                pair.get(
                    "source_evidence_digest"
                ),

            "target_evidence_digest":
                pair.get(
                    "target_evidence_digest"
                ),

            "reasoning_status":
                guarded[
                    "reasoning_status"
                ],
        }

        relationship_trace_json = json.dumps(
            relationship_trace_material,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )

        relationship_trace_digest = hashlib.sha256(
            relationship_trace_json.encode(
                "utf-8"
            )
        ).hexdigest()

        relationship_trace_id = (
            "cdrtrace:v1:"
            + relationship_trace_digest[:32]
        )

        conflict_ids = [
            item[
                "conflict_id"
            ]
            for item in conflict_registry
            if item.get(
                "reasoning_id"
            ) == guarded.get(
                "reasoning_id"
            )
        ]

        unresolved_entries = [
            deepcopy(
                dict(item)
            )
            for item in unresolved_registry
            if item.get(
                "reasoning_id"
            ) == guarded.get(
                "reasoning_id"
            )
        ]

        rejected_entries = [
            deepcopy(
                dict(item)
            )
            for item in rejected_registry
            if item.get(
                "reasoning_id"
            ) == guarded.get(
                "reasoning_id"
            )
        ]

        relationship_traces.append(
            {
                "relationship_trace_schema":
                    "cross_document_relationship_provenance_trace_v1",

                "relationship_trace_version":
                    "v1",

                "relationship_trace_id":
                    relationship_trace_id,

                "relationship_trace_digest":
                    relationship_trace_digest,

                "relationship_trace_digest_algorithm":
                    "SHA256",

                "source_article_id":
                    source_article_id,

                "target_article_id":
                    target_article_id,

                "source_storage_key":
                    source_document.get(
                        "storage_key"
                    ),

                "target_storage_key":
                    target_document.get(
                        "storage_key"
                    ),

                "source_profile_payload_hash":
                    source_document.get(
                        "profile_payload_hash"
                    ),

                "target_profile_payload_hash":
                    target_document.get(
                        "profile_payload_hash"
                    ),

                "pair_alignment_id":
                    alignment_id,

                "source_evidence_digest":
                    pair.get(
                        "source_evidence_digest"
                    ),

                "target_evidence_digest":
                    pair.get(
                        "target_evidence_digest"
                    ),

                "relationship_candidate_id":
                    source_relationship_id,

                "reasoning_id":
                    guarded[
                        "reasoning_id"
                    ],

                "reasoning_digest":
                    guarded[
                        "reasoning_digest"
                    ],

                "relationship_family":
                    guarded[
                        "relationship_family"
                    ],

                "reasoning_status":
                    guarded[
                        "reasoning_status"
                    ],

                "reasoning_basis":
                    deepcopy(
                        guarded[
                            "reasoning_basis"
                        ]
                    ),

                "confidence_state":
                    guarded[
                        "confidence_state"
                    ],

                "uncertainty_state":
                    guarded[
                        "uncertainty_state"
                    ],

                "evidence":
                    deepcopy(
                        guarded[
                            "evidence"
                        ]
                    ),

                "conflict_ids":
                    conflict_ids,

                "unresolved_entries":
                    unresolved_entries,

                "rejected_entries":
                    rejected_entries,

                "document_lineage_complete":
                    True,

                "relationship_lineage_complete":
                    True,

                "evidence_trace_complete":
                    True,

                "reasoning_trace_complete":
                    True,

                "integrity_guard_verified":
                    True,

                "uncertainty_preserved":
                    True,

                "conflict_state_preserved":
                    True,

                "source_profile_modified":
                    False,

                "retrieval_payload_modified":
                    False,

                "evidence_invented":
                    False,

                "semantic_memory_written":
                    False,

                "linking_decision":
                    False,
            }
        )

    relationship_traces = sorted(
        relationship_traces,
        key=lambda item: (
            item[
                "source_article_id"
            ],
            item[
                "target_article_id"
            ],
            item[
                "relationship_family"
            ],
            item[
                "reasoning_id"
            ],
        ),
    )

    if len(
        relationship_traces
    ) != len(
        guarded_relationships
    ):
        raise CrossDocumentReasoningError(
            "Relationship provenance trace count drifted."
        )

    # -------------------------------------------------------------
    # Document lineage
    # -------------------------------------------------------------

    document_lineage = []

    for document in sorted(
        aligned_documents,
        key=lambda item: item[
            "article_id"
        ],
    ):

        document_lineage.append(
            {
                "workspace_id":
                    document.get(
                        "workspace_id",
                        workspace_id,
                    ),

                "article_id":
                    document.get(
                        "article_id"
                    ),

                "canonical_article_identity":
                    deepcopy(
                        document.get(
                            "canonical_article_identity",
                            {},
                        )
                    ),

                "storage_key":
                    document.get(
                        "storage_key"
                    ),

                "retrieval_payload_id":
                    document.get(
                        "retrieval_payload_id"
                    ),

                "retrieval_provenance_id":
                    document.get(
                        "provenance_id"
                    ),

                "profile_payload_hash":
                    document.get(
                        "profile_payload_hash"
                    ),

                "evidence_digest":
                    document.get(
                        "evidence_digest"
                    ),

                "knowledge_retrieval_source":
                    "4.6.20K",

                "cross_document_scope_source":
                    "4.6.21D",

                "evidence_alignment_source":
                    "4.6.21E",

                "source_profile_certified":
                    document.get(
                        "source_profile_certified"
                    )
                    is True,

                "source_profile_immutable":
                    document.get(
                        "source_profile_immutable"
                    )
                    is True,
            }
        )

    # -------------------------------------------------------------
    # Full phase lineage
    # -------------------------------------------------------------

    phase_lineage = [
        {
            "phase":
                "4.6.20",

            "patch":
                "4.6.20K",

            "role":
                "CERTIFIED_KNOWLEDGE_RETRIEVAL_SOURCE",
        },
        {
            "phase":
                "4.6.21",

            "patch":
                "4.6.21A",

            "role":
                "CERTIFIED_RETRIEVAL_INPUT_INSPECTION",
        },
        {
            "phase":
                "4.6.21",

            "patch":
                "4.6.21B",

            "role":
                "ARCHITECTURE_DEFINITION",
        },
        {
            "phase":
                "4.6.21",

            "patch":
                "4.6.21C",

            "role":
                "REASONING_INTAKE_VALIDATION",
        },
        {
            "phase":
                "4.6.21",

            "patch":
                "4.6.21D",

            "role":
                "DOCUMENT_SET_AND_SCOPE",
        },
        {
            "phase":
                "4.6.21",

            "patch":
                "4.6.21E",

            "role":
                "EVIDENCE_ALIGNMENT",
        },
        {
            "phase":
                "4.6.21",

            "patch":
                "4.6.21F",

            "role":
                "RELATIONSHIP_CONSTRUCTION",
        },
        {
            "phase":
                "4.6.21",

            "patch":
                "4.6.21G",

            "role":
                "REASONING_EXECUTION",
        },
        {
            "phase":
                "4.6.21",

            "patch":
                "4.6.21H",

            "role":
                "INTEGRITY_AND_CONFLICT_GUARD",
        },
        {
            "phase":
                "4.6.21",

            "patch":
                "4.6.21I",

            "role":
                "PROVENANCE_AND_EVIDENCE_TRACE",
        },
    ]

    # -------------------------------------------------------------
    # Deterministic provenance package identity
    # -------------------------------------------------------------

    provenance_material = {
        "document_set_id":
            document_set[
                "document_set_id"
            ],

        "reasoning_scope_id":
            reasoning_scope[
                "reasoning_scope_id"
            ],

        "evidence_alignment_id":
            evidence_alignment[
                "evidence_alignment_id"
            ],

        "relationship_package_id":
            construction[
                "relationship_package_id"
            ],

        "reasoning_package_id":
            execution[
                "reasoning_package_id"
            ],

        "integrity_guard_id":
            integrity_guard[
                "reasoning_integrity_guard_id"
            ],

        "relationship_trace_ids": [
            item[
                "relationship_trace_id"
            ]
            for item in relationship_traces
        ],

        "conflict_ids": [
            item[
                "conflict_id"
            ]
            for item in conflict_registry
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
        "cdrprov:v1:"
        + provenance_digest[:32]
    )

    provenance = {
        "reasoning_provenance_schema":
            "cross_document_reasoning_provenance_v1",

        "reasoning_provenance_version":
            "v1",

        "reasoning_provenance_id":
            provenance_id,

        "reasoning_provenance_digest":
            provenance_digest,

        "reasoning_provenance_digest_algorithm":
            "SHA256",

        "workspace_id":
            workspace_id,

        "document_set_id":
            document_set[
                "document_set_id"
            ],

        "reasoning_scope_id":
            reasoning_scope[
                "reasoning_scope_id"
            ],

        "evidence_alignment_id":
            evidence_alignment[
                "evidence_alignment_id"
            ],

        "relationship_package_id":
            construction[
                "relationship_package_id"
            ],

        "reasoning_package_id":
            execution[
                "reasoning_package_id"
            ],

        "integrity_guard_id":
            integrity_guard[
                "reasoning_integrity_guard_id"
            ],

        "document_lineage":
            document_lineage,

        "relationship_traces":
            relationship_traces,

        "conflict_registry":
            deepcopy(
                conflict_registry
            ),

        "unresolved_registry":
            deepcopy(
                unresolved_registry
            ),

        "rejected_registry":
            deepcopy(
                rejected_registry
            ),

        "phase_lineage":
            phase_lineage,

        "lineage_complete_through_4.6.21I":
            True,

        "document_lineage_complete":
            True,

        "relationship_lineage_complete":
            True,

        "evidence_trace_complete":
            True,

        "reasoning_trace_complete":
            True,

        "conflict_trace_complete":
            True,

        "uncertainty_trace_complete":
            True,

        "reasoning_integrity_verified":
            True,

        "reasoning_provenance_built":
            True,

        "source_profiles_preserved":
            True,

        "retrieval_payloads_preserved":
            True,

        "reasoning_outcomes_preserved":
            True,

        "conflicts_silently_resolved":
            False,

        "evidence_invented":
            False,

        "unsupported_fact_inference_performed":
            False,

        "final_result_built":
            False,

        "read_only":
            True,

        "semantic_memory_written":
            False,

        "linking_decisions_performed":
            False,
    }

    return {
        "schema_version":
            "cross_document_reasoning_provenance_result_v1",

        "version":
            CROSS_DOCUMENT_REASONING_VERSION,

        "phase":
            CROSS_DOCUMENT_REASONING_PHASE,

        "patch":
            "4.6.21I",

        "status":
            "CROSS_DOCUMENT_REASONING_PROVENANCE_BUILT",

        "workspace_id":
            workspace_id,

        "document_set_contract":
            deepcopy(
                dict(document_set)
            ),

        "reasoning_scope_contract":
            deepcopy(
                dict(reasoning_scope)
            ),

        "evidence_alignment_contract":
            deepcopy(
                dict(evidence_alignment)
            ),

        "relationship_construction_contract":
            deepcopy(
                dict(construction)
            ),

        "reasoning_execution_contract":
            deepcopy(
                dict(execution)
            ),

        "reasoning_integrity_guard":
            deepcopy(
                dict(integrity_guard)
            ),

        "reasoning_provenance":
            provenance,

        "cross_document_reasoning_architecture":
            deepcopy(
                dict(architecture)
            ),

        "source_integrity_guard_result":
            deepcopy(
                dict(guard_result)
            ),

        "processing_boundaries": {
            "document_set_scope_contract_preserved":
                True,

            "evidence_alignment_preserved":
                True,

            "relationship_construction_preserved":
                True,

            "reasoning_execution_preserved":
                True,

            "reasoning_integrity_guard_preserved":
                True,

            "cross_document_reasoning_architecture_preserved":
                True,

            "source_profiles_preserved":
                True,

            "retrieval_payloads_preserved":
                True,

            "cross_document_evidence_alignment_performed":
                True,

            "cross_document_relationships_constructed":
                True,

            "cross_document_reasoning_performed":
                True,

            "reasoning_integrity_verification_performed":
                True,

            "conflict_guard_applied":
                True,

            "uncertainty_preserved":
                True,

            "reasoning_provenance_built":
                True,

            "document_lineage_built":
                True,

            "relationship_lineage_built":
                True,

            "evidence_trace_built":
                True,

            "reasoning_trace_built":
                True,

            "conflict_trace_built":
                True,

            "final_cross_document_reasoning_result_built":
                False,

            "full_cross_document_reasoning_certification_performed":
                False,

            "source_profile_modified":
                False,

            "retrieval_payload_modified":
                False,

            "reasoning_outcome_modified":
                False,

            "evidence_invented":
                False,

            "unsupported_fact_inference_performed":
                False,

            "conflict_silently_resolved":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,
        },

        "reasoning_policy":
            "COMPLETE_REASONING_PROVENANCE_AND_EVIDENCE_TRACE_BUILT",

        "next_stage":
            "final_cross_document_reasoning_result",
    }


# =====================================================================
# PATCH 4.6.21J ? Final Cross-Document Reasoning Result
# =====================================================================

def build_final_cross_document_reasoning_result_v1(
    provenance_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Assemble the final canonical 4.6.21 Cross-Document Reasoning result.

    J is assembly only.

    J does not:
    - perform new reasoning,
    - change relationship outcomes,
    - resolve conflicts,
    - change uncertainty,
    - mutate source profiles or retrieval payloads,
    - write Semantic Memory,
    - make linking decisions.
    """

    from collections.abc import Mapping
    from copy import deepcopy
    import hashlib
    import json

    if not isinstance(
        provenance_result,
        Mapping,
    ):
        raise CrossDocumentReasoningError(
            "provenance_result must be a mapping."
        )

    # -------------------------------------------------------------
    # Exact 4.6.21I lifecycle
    # -------------------------------------------------------------

    for field, expected in (
        (
            "schema_version",
            "cross_document_reasoning_provenance_result_v1",
        ),
        (
            "version",
            CROSS_DOCUMENT_REASONING_VERSION,
        ),
        (
            "phase",
            CROSS_DOCUMENT_REASONING_PHASE,
        ),
        (
            "patch",
            "4.6.21I",
        ),
        (
            "status",
            "CROSS_DOCUMENT_REASONING_PROVENANCE_BUILT",
        ),
        (
            "reasoning_policy",
            "COMPLETE_REASONING_PROVENANCE_AND_EVIDENCE_TRACE_BUILT",
        ),
        (
            "next_stage",
            "final_cross_document_reasoning_result",
        ),
    ):

        if provenance_result.get(field) != expected:
            raise CrossDocumentReasoningError(
                f"Invalid 4.6.21I lifecycle field: {field}"
            )

    workspace_id = provenance_result.get(
        "workspace_id"
    )

    document_set = provenance_result.get(
        "document_set_contract"
    )

    reasoning_scope = provenance_result.get(
        "reasoning_scope_contract"
    )

    evidence_alignment = provenance_result.get(
        "evidence_alignment_contract"
    )

    construction = provenance_result.get(
        "relationship_construction_contract"
    )

    execution = provenance_result.get(
        "reasoning_execution_contract"
    )

    integrity_guard = provenance_result.get(
        "reasoning_integrity_guard"
    )

    provenance = provenance_result.get(
        "reasoning_provenance"
    )

    architecture = provenance_result.get(
        "cross_document_reasoning_architecture"
    )

    boundaries = provenance_result.get(
        "processing_boundaries"
    )

    for name, value in (
        ("document_set_contract", document_set),
        ("reasoning_scope_contract", reasoning_scope),
        ("evidence_alignment_contract", evidence_alignment),
        ("relationship_construction_contract", construction),
        ("reasoning_execution_contract", execution),
        ("reasoning_integrity_guard", integrity_guard),
        ("reasoning_provenance", provenance),
        (
            "cross_document_reasoning_architecture",
            architecture,
        ),
        ("processing_boundaries", boundaries),
    ):

        if not isinstance(
            value,
            Mapping,
        ):
            raise CrossDocumentReasoningError(
                name + " is missing."
            )

    # -------------------------------------------------------------
    # I provenance authority
    # -------------------------------------------------------------

    if provenance.get(
        "reasoning_provenance_schema"
    ) != "cross_document_reasoning_provenance_v1":
        raise CrossDocumentReasoningError(
            "Reasoning provenance schema drifted."
        )

    if provenance.get(
        "reasoning_provenance_version"
    ) != "v1":
        raise CrossDocumentReasoningError(
            "Reasoning provenance version drifted."
        )

    for field in (
        "lineage_complete_through_4.6.21I",
        "document_lineage_complete",
        "relationship_lineage_complete",
        "evidence_trace_complete",
        "reasoning_trace_complete",
        "conflict_trace_complete",
        "uncertainty_trace_complete",
        "reasoning_integrity_verified",
        "reasoning_provenance_built",
        "source_profiles_preserved",
        "retrieval_payloads_preserved",
        "reasoning_outcomes_preserved",
        "read_only",
    ):

        if provenance.get(field) is not True:
            raise CrossDocumentReasoningError(
                f"Required provenance field is not True: {field}"
            )

    for field in (
        "conflicts_silently_resolved",
        "evidence_invented",
        "unsupported_fact_inference_performed",
        "final_result_built",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if provenance.get(field) is not False:
            raise CrossDocumentReasoningError(
                f"Forbidden provenance field is not False: {field}"
            )

    # -------------------------------------------------------------
    # Cross-package identity binding
    # -------------------------------------------------------------

    identity_checks = (
        (
            provenance.get("document_set_id"),
            document_set.get("document_set_id"),
            "document_set_id",
        ),
        (
            provenance.get("reasoning_scope_id"),
            reasoning_scope.get("reasoning_scope_id"),
            "reasoning_scope_id",
        ),
        (
            provenance.get("evidence_alignment_id"),
            evidence_alignment.get("evidence_alignment_id"),
            "evidence_alignment_id",
        ),
        (
            provenance.get("relationship_package_id"),
            construction.get("relationship_package_id"),
            "relationship_package_id",
        ),
        (
            provenance.get("reasoning_package_id"),
            execution.get("reasoning_package_id"),
            "reasoning_package_id",
        ),
        (
            provenance.get("integrity_guard_id"),
            integrity_guard.get("reasoning_integrity_guard_id"),
            "integrity_guard_id",
        ),
    )

    for actual, expected, name in identity_checks:

        if actual != expected:
            raise CrossDocumentReasoningError(
                f"Cross-document identity binding drifted: {name}"
            )

    if provenance.get(
        "workspace_id"
    ) != workspace_id:
        raise CrossDocumentReasoningError(
            "Workspace identity drifted."
        )

    # -------------------------------------------------------------
    # H integrity authority
    # -------------------------------------------------------------

    for field in (
        "reasoning_integrity_verification_performed",
        "all_reasoning_digests_verified",
        "all_reasoning_ids_verified",
        "all_candidate_bindings_verified",
        "all_evidence_bindings_verified",
        "status_consistency_verified",
        "uncertainty_preserved",
        "conflicts_explicit",
        "source_profiles_preserved",
        "retrieval_payloads_preserved",
        "read_only",
    ):

        if integrity_guard.get(field) is not True:
            raise CrossDocumentReasoningError(
                f"Required integrity field is not True: {field}"
            )

    for field in (
        "conflicts_silently_resolved",
        "evidence_invented",
        "unsupported_fact_inference_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if integrity_guard.get(field) is not False:
            raise CrossDocumentReasoningError(
                f"Forbidden integrity field is not False: {field}"
            )

    guarded_relationships = integrity_guard.get(
        "guarded_reasoned_relationships"
    )

    conflict_registry = integrity_guard.get(
        "conflict_registry"
    )

    unresolved_registry = integrity_guard.get(
        "unresolved_registry"
    )

    rejected_registry = integrity_guard.get(
        "rejected_registry"
    )

    for name, value in (
        ("guarded_reasoned_relationships", guarded_relationships),
        ("conflict_registry", conflict_registry),
        ("unresolved_registry", unresolved_registry),
        ("rejected_registry", rejected_registry),
    ):

        if not isinstance(
            value,
            list,
        ):
            raise CrossDocumentReasoningError(
                name + " must be a list."
            )

    # -------------------------------------------------------------
    # Architecture authority
    # -------------------------------------------------------------

    execution_contract = architecture.get(
        "execution_contract"
    )

    if not isinstance(
        execution_contract,
        Mapping,
    ):
        raise CrossDocumentReasoningError(
            "Execution contract is missing."
        )

    if execution_contract.get(
        "4.6.21J"
    ) != "FINAL_RESULT_ASSEMBLY":
        raise CrossDocumentReasoningError(
            "4.6.21J execution contract drifted."
        )

    # -------------------------------------------------------------
    # I boundary authority
    # -------------------------------------------------------------

    for field in (
        "document_set_scope_contract_preserved",
        "evidence_alignment_preserved",
        "relationship_construction_preserved",
        "reasoning_execution_preserved",
        "reasoning_integrity_guard_preserved",
        "cross_document_reasoning_architecture_preserved",
        "source_profiles_preserved",
        "retrieval_payloads_preserved",
        "cross_document_evidence_alignment_performed",
        "cross_document_relationships_constructed",
        "cross_document_reasoning_performed",
        "reasoning_integrity_verification_performed",
        "conflict_guard_applied",
        "uncertainty_preserved",
        "reasoning_provenance_built",
        "document_lineage_built",
        "relationship_lineage_built",
        "evidence_trace_built",
        "reasoning_trace_built",
        "conflict_trace_built",
    ):

        if boundaries.get(field) is not True:
            raise CrossDocumentReasoningError(
                f"Required 4.6.21I boundary is not True: {field}"
            )

    for field in (
        "final_cross_document_reasoning_result_built",
        "full_cross_document_reasoning_certification_performed",
        "source_profile_modified",
        "retrieval_payload_modified",
        "reasoning_outcome_modified",
        "evidence_invented",
        "unsupported_fact_inference_performed",
        "conflict_silently_resolved",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if boundaries.get(field) is not False:
            raise CrossDocumentReasoningError(
                f"Forbidden 4.6.21I boundary is not False: {field}"
            )

    # -------------------------------------------------------------
    # Final canonical relationship view
    # -------------------------------------------------------------

    final_relationships = []

    for item in guarded_relationships:

        if not isinstance(
            item,
            Mapping,
        ):
            raise CrossDocumentReasoningError(
                "Guarded relationship entry is invalid."
            )

        for field in (
            "reasoning_integrity_verified",
            "candidate_identity_verified",
            "evidence_integrity_verified",
            "status_consistency_verified",
            "uncertainty_preserved",
            "conflict_guard_applied",
        ):

            if item.get(field) is not True:
                raise CrossDocumentReasoningError(
                    f"Guarded relationship integrity field is not True: {field}"
                )

        if item.get(
            "conflict_resolved"
        ) is not False:
            raise CrossDocumentReasoningError(
                "J cannot consume a silently resolved conflict."
            )

        final_relationships.append(
            {
                "reasoning_id":
                    item.get(
                        "reasoning_id"
                    ),

                "reasoning_digest":
                    item.get(
                        "reasoning_digest"
                    ),

                "source_relationship_id":
                    item.get(
                        "source_relationship_id"
                    ),

                "source_article_id":
                    item.get(
                        "source_article_id"
                    ),

                "target_article_id":
                    item.get(
                        "target_article_id"
                    ),

                "relationship_family":
                    item.get(
                        "relationship_family"
                    ),

                "directionality":
                    item.get(
                        "directionality"
                    ),

                "reasoning_status":
                    item.get(
                        "reasoning_status"
                    ),

                "relationship_confirmed":
                    item.get(
                        "relationship_confirmed"
                    ),

                "relationship_rejected":
                    item.get(
                        "relationship_rejected"
                    ),

                "reasoning_basis":
                    deepcopy(
                        item.get(
                            "reasoning_basis"
                        )
                    ),

                "confidence_state":
                    item.get(
                        "confidence_state"
                    ),

                "uncertainty_state":
                    item.get(
                        "uncertainty_state"
                    ),

                "evidence":
                    deepcopy(
                        item.get(
                            "evidence"
                        )
                    ),

                "evidence_alignment_id":
                    item.get(
                        "evidence_alignment_id"
                    ),

                "reasoning_integrity_verified":
                    True,

                "provenance_trace_available":
                    True,

                "uncertainty_preserved":
                    True,

                "conflict_detected":
                    item.get(
                        "conflict_detected"
                    )
                    is True,

                "conflict_resolved":
                    False,

                "source_profile_modified":
                    False,

                "retrieval_payload_modified":
                    False,

                "semantic_memory_written":
                    False,

                "linking_decision":
                    False,
            }
        )

    final_relationships = sorted(
        final_relationships,
        key=lambda item: (
            item[
                "source_article_id"
            ],
            item[
                "target_article_id"
            ],
            item[
                "relationship_family"
            ],
            item[
                "reasoning_id"
            ],
        ),
    )

    # -------------------------------------------------------------
    # Status summary
    # -------------------------------------------------------------

    reasoning_status_counts = {}

    relationship_family_counts = {}

    for item in final_relationships:

        status = item[
            "reasoning_status"
        ]

        family = item[
            "relationship_family"
        ]

        reasoning_status_counts[
            status
        ] = (
            reasoning_status_counts.get(
                status,
                0,
            )
            + 1
        )

        relationship_family_counts[
            family
        ] = (
            relationship_family_counts.get(
                family,
                0,
            )
            + 1
        )

    # -------------------------------------------------------------
    # Deterministic final identity
    # -------------------------------------------------------------

    final_material = {
        "version":
            CROSS_DOCUMENT_REASONING_VERSION,

        "workspace_id":
            workspace_id,

        "document_set_id":
            document_set[
                "document_set_id"
            ],

        "reasoning_scope_id":
            reasoning_scope[
                "reasoning_scope_id"
            ],

        "evidence_alignment_id":
            evidence_alignment[
                "evidence_alignment_id"
            ],

        "relationship_package_id":
            construction[
                "relationship_package_id"
            ],

        "reasoning_package_id":
            execution[
                "reasoning_package_id"
            ],

        "integrity_guard_id":
            integrity_guard[
                "reasoning_integrity_guard_id"
            ],

        "reasoning_provenance_id":
            provenance[
                "reasoning_provenance_id"
            ],

        "reasoning_ids": [
            item[
                "reasoning_id"
            ]
            for item in final_relationships
        ],

        "conflict_ids": [
            item[
                "conflict_id"
            ]
            for item in conflict_registry
        ],
    }

    final_json = json.dumps(
        final_material,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    final_digest = hashlib.sha256(
        final_json.encode("utf-8")
    ).hexdigest()

    final_result_id = (
        "cdrfinal:v1:"
        + final_digest[:32]
    )

    final_result = {
        "final_result_schema":
            "final_cross_document_reasoning_result_v1",

        "final_result_version":
            "v1",

        "final_result_id":
            final_result_id,

        "final_result_digest":
            final_digest,

        "final_result_digest_algorithm":
            "SHA256",

        "workspace_id":
            workspace_id,

        "document_set_id":
            document_set[
                "document_set_id"
            ],

        "reasoning_scope_id":
            reasoning_scope[
                "reasoning_scope_id"
            ],

        "evidence_alignment_id":
            evidence_alignment[
                "evidence_alignment_id"
            ],

        "relationship_package_id":
            construction[
                "relationship_package_id"
            ],

        "reasoning_package_id":
            execution[
                "reasoning_package_id"
            ],

        "integrity_guard_id":
            integrity_guard[
                "reasoning_integrity_guard_id"
            ],

        "reasoning_provenance_id":
            provenance[
                "reasoning_provenance_id"
            ],

        "relationship_count":
            len(
                final_relationships
            ),

        "reasoning_status_counts":
            reasoning_status_counts,

        "relationship_family_counts":
            relationship_family_counts,

        "relationships":
            final_relationships,

        "conflict_registry":
            deepcopy(
                conflict_registry
            ),

        "unresolved_registry":
            deepcopy(
                unresolved_registry
            ),

        "rejected_registry":
            deepcopy(
                rejected_registry
            ),

        "reasoning_provenance":
            deepcopy(
                dict(provenance)
            ),

        "cross_document_reasoning_performed":
            True,

        "reasoning_integrity_verified":
            True,

        "reasoning_provenance_complete":
            True,

        "reasoning_outcomes_preserved":
            True,

        "conflicts_explicit":
            True,

        "uncertainty_preserved":
            True,

        "source_profiles_preserved":
            True,

        "retrieval_payloads_preserved":
            True,

        "evidence_invented":
            False,

        "unsupported_fact_inference_performed":
            False,

        "conflicts_silently_resolved":
            False,

        "source_profile_modified":
            False,

        "retrieval_payload_modified":
            False,

        "semantic_memory_written":
            False,

        "linking_decisions_performed":
            False,

        "full_cross_document_reasoning_certified":
            False,

        "certification_status":
            "PENDING_4.6.21K",

        "next_owner":
            "4.6.21K_FULL_CROSS_DOCUMENT_REASONING_HARD_CERTIFICATION",

        "post_certification_owner":
            "4.6.22_ONTOLOGY_ALIGNMENT",
    }

    summary = {
        "final_status":
            "CROSS_DOCUMENT_REASONING_RESULT_READY_FOR_CERTIFICATION",

        "workspace_id":
            workspace_id,

        "relationship_count":
            len(
                final_relationships
            ),

        "conflict_count":
            len(
                conflict_registry
            ),

        "unresolved_count":
            len(
                unresolved_registry
            ),

        "rejected_count":
            len(
                rejected_registry
            ),

        "reasoning_integrity_verified":
            True,

        "reasoning_provenance_complete":
            True,

        "full_cross_document_reasoning_certified":
            False,

        "next_owner":
            "4.6.21K_FULL_CROSS_DOCUMENT_REASONING_HARD_CERTIFICATION",

        "post_certification_owner":
            "4.6.22_ONTOLOGY_ALIGNMENT",

        "semantic_memory_owner":
            "4.6.28_SEMANTIC_MEMORY",
    }

    return {
        "schema_version":
            "final_cross_document_reasoning_result_envelope_v1",

        "version":
            CROSS_DOCUMENT_REASONING_VERSION,

        "phase":
            CROSS_DOCUMENT_REASONING_PHASE,

        "patch":
            "4.6.21J",

        "status":
            "FINAL_CROSS_DOCUMENT_REASONING_RESULT_BUILT",

        "workspace_id":
            workspace_id,

        "document_set_contract":
            deepcopy(
                dict(document_set)
            ),

        "reasoning_scope_contract":
            deepcopy(
                dict(reasoning_scope)
            ),

        "evidence_alignment_contract":
            deepcopy(
                dict(evidence_alignment)
            ),

        "relationship_construction_contract":
            deepcopy(
                dict(construction)
            ),

        "reasoning_execution_contract":
            deepcopy(
                dict(execution)
            ),

        "reasoning_integrity_guard":
            deepcopy(
                dict(integrity_guard)
            ),

        "reasoning_provenance":
            deepcopy(
                dict(provenance)
            ),

        "final_cross_document_reasoning_result":
            final_result,

        "final_result_summary":
            summary,

        "cross_document_reasoning_architecture":
            deepcopy(
                dict(architecture)
            ),

        "source_provenance_result":
            deepcopy(
                dict(provenance_result)
            ),

        "processing_boundaries": {
            "document_set_scope_contract_preserved":
                True,

            "evidence_alignment_preserved":
                True,

            "relationship_construction_preserved":
                True,

            "reasoning_execution_preserved":
                True,

            "reasoning_integrity_guard_preserved":
                True,

            "reasoning_provenance_preserved":
                True,

            "cross_document_reasoning_architecture_preserved":
                True,

            "source_profiles_preserved":
                True,

            "retrieval_payloads_preserved":
                True,

            "cross_document_evidence_alignment_performed":
                True,

            "cross_document_relationships_constructed":
                True,

            "cross_document_reasoning_performed":
                True,

            "reasoning_integrity_verification_performed":
                True,

            "conflict_guard_applied":
                True,

            "uncertainty_preserved":
                True,

            "reasoning_provenance_built":
                True,

            "final_cross_document_reasoning_result_built":
                True,

            "full_cross_document_reasoning_certification_performed":
                False,

            "source_profile_modified":
                False,

            "retrieval_payload_modified":
                False,

            "reasoning_outcome_modified":
                False,

            "evidence_invented":
                False,

            "unsupported_fact_inference_performed":
                False,

            "conflict_silently_resolved":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,
        },

        "reasoning_policy":
            "FINAL_CROSS_DOCUMENT_REASONING_RESULT_READY_FOR_CERTIFICATION",

        "next_stage":
            "full_cross_document_reasoning_hard_certification",
    }


# =====================================================================
# PATCH 4.6.21K ? Full Cross-Document Reasoning Hard Certification
# =====================================================================

def certify_full_cross_document_reasoning_v1(
    final_result_envelope: dict[str, Any],
) -> dict[str, Any]:
    """
    Perform the final hard certification of the complete
    4.6.21 Cross-Document Reasoning pipeline.

    K verifies only. It performs no new reasoning.
    """

    from collections.abc import Mapping
    from copy import deepcopy
    import hashlib
    import json

    if not isinstance(
        final_result_envelope,
        Mapping,
    ):
        raise CrossDocumentReasoningError(
            "final_result_envelope must be a mapping."
        )

    # -------------------------------------------------------------
    # Exact 4.6.21J lifecycle
    # -------------------------------------------------------------

    for field, expected in (
        (
            "schema_version",
            "final_cross_document_reasoning_result_envelope_v1",
        ),
        (
            "version",
            CROSS_DOCUMENT_REASONING_VERSION,
        ),
        (
            "phase",
            CROSS_DOCUMENT_REASONING_PHASE,
        ),
        (
            "patch",
            "4.6.21J",
        ),
        (
            "status",
            "FINAL_CROSS_DOCUMENT_REASONING_RESULT_BUILT",
        ),
        (
            "reasoning_policy",
            "FINAL_CROSS_DOCUMENT_REASONING_RESULT_READY_FOR_CERTIFICATION",
        ),
        (
            "next_stage",
            "full_cross_document_reasoning_hard_certification",
        ),
    ):

        if final_result_envelope.get(field) != expected:
            raise CrossDocumentReasoningError(
                f"Invalid 4.6.21J lifecycle field: {field}"
            )

    workspace_id = final_result_envelope.get(
        "workspace_id"
    )

    document_set = final_result_envelope.get(
        "document_set_contract"
    )

    reasoning_scope = final_result_envelope.get(
        "reasoning_scope_contract"
    )

    evidence_alignment = final_result_envelope.get(
        "evidence_alignment_contract"
    )

    construction = final_result_envelope.get(
        "relationship_construction_contract"
    )

    execution = final_result_envelope.get(
        "reasoning_execution_contract"
    )

    integrity_guard = final_result_envelope.get(
        "reasoning_integrity_guard"
    )

    provenance = final_result_envelope.get(
        "reasoning_provenance"
    )

    final_result = final_result_envelope.get(
        "final_cross_document_reasoning_result"
    )

    summary = final_result_envelope.get(
        "final_result_summary"
    )

    architecture = final_result_envelope.get(
        "cross_document_reasoning_architecture"
    )

    boundaries = final_result_envelope.get(
        "processing_boundaries"
    )

    for name, value in (
        ("document_set_contract", document_set),
        ("reasoning_scope_contract", reasoning_scope),
        ("evidence_alignment_contract", evidence_alignment),
        ("relationship_construction_contract", construction),
        ("reasoning_execution_contract", execution),
        ("reasoning_integrity_guard", integrity_guard),
        ("reasoning_provenance", provenance),
        ("final_cross_document_reasoning_result", final_result),
        ("final_result_summary", summary),
        ("cross_document_reasoning_architecture", architecture),
        ("processing_boundaries", boundaries),
    ):

        if not isinstance(
            value,
            Mapping,
        ):
            raise CrossDocumentReasoningError(
                name + " is missing."
            )

    # -------------------------------------------------------------
    # Architecture K authority
    # -------------------------------------------------------------

    execution_contract = architecture.get(
        "execution_contract"
    )

    if not isinstance(
        execution_contract,
        Mapping,
    ):
        raise CrossDocumentReasoningError(
            "Architecture execution contract is missing."
        )

    if execution_contract.get(
        "4.6.21K"
    ) != "FULL_HARD_CERTIFICATION":
        raise CrossDocumentReasoningError(
            "4.6.21K execution contract drifted."
        )

    # -------------------------------------------------------------
    # Final result lifecycle
    # -------------------------------------------------------------

    for field, expected in (
        (
            "final_result_schema",
            "final_cross_document_reasoning_result_v1",
        ),
        (
            "final_result_version",
            "v1",
        ),
        (
            "certification_status",
            "PENDING_4.6.21K",
        ),
        (
            "next_owner",
            "4.6.21K_FULL_CROSS_DOCUMENT_REASONING_HARD_CERTIFICATION",
        ),
        (
            "post_certification_owner",
            "4.6.22_ONTOLOGY_ALIGNMENT",
        ),
    ):

        if final_result.get(field) != expected:
            raise CrossDocumentReasoningError(
                f"Final result field drifted: {field}"
            )

    if final_result.get(
        "workspace_id"
    ) != workspace_id:
        raise CrossDocumentReasoningError(
            "Final result workspace drifted."
        )

    # -------------------------------------------------------------
    # Identity binding across the complete pipeline
    # -------------------------------------------------------------

    bindings = (
        (
            final_result.get("document_set_id"),
            document_set.get("document_set_id"),
            "document_set_id",
        ),
        (
            final_result.get("reasoning_scope_id"),
            reasoning_scope.get("reasoning_scope_id"),
            "reasoning_scope_id",
        ),
        (
            final_result.get("evidence_alignment_id"),
            evidence_alignment.get("evidence_alignment_id"),
            "evidence_alignment_id",
        ),
        (
            final_result.get("relationship_package_id"),
            construction.get("relationship_package_id"),
            "relationship_package_id",
        ),
        (
            final_result.get("reasoning_package_id"),
            execution.get("reasoning_package_id"),
            "reasoning_package_id",
        ),
        (
            final_result.get("integrity_guard_id"),
            integrity_guard.get("reasoning_integrity_guard_id"),
            "integrity_guard_id",
        ),
        (
            final_result.get("reasoning_provenance_id"),
            provenance.get("reasoning_provenance_id"),
            "reasoning_provenance_id",
        ),
    )

    for actual, expected, name in bindings:

        if actual != expected:
            raise CrossDocumentReasoningError(
                f"Final cross-document binding drifted: {name}"
            )

    # -------------------------------------------------------------
    # Required final-state truths
    # -------------------------------------------------------------

    for field in (
        "cross_document_reasoning_performed",
        "reasoning_integrity_verified",
        "reasoning_provenance_complete",
        "reasoning_outcomes_preserved",
        "conflicts_explicit",
        "uncertainty_preserved",
        "source_profiles_preserved",
        "retrieval_payloads_preserved",
    ):

        if final_result.get(field) is not True:
            raise CrossDocumentReasoningError(
                f"Required final result field is not True: {field}"
            )

    for field in (
        "evidence_invented",
        "unsupported_fact_inference_performed",
        "conflicts_silently_resolved",
        "source_profile_modified",
        "retrieval_payload_modified",
        "semantic_memory_written",
        "linking_decisions_performed",
        "full_cross_document_reasoning_certified",
    ):

        if final_result.get(field) is not False:
            raise CrossDocumentReasoningError(
                f"Forbidden final result field is not False: {field}"
            )

    relationships = final_result.get(
        "relationships"
    )

    conflict_registry = final_result.get(
        "conflict_registry"
    )

    unresolved_registry = final_result.get(
        "unresolved_registry"
    )

    rejected_registry = final_result.get(
        "rejected_registry"
    )

    for name, value in (
        ("relationships", relationships),
        ("conflict_registry", conflict_registry),
        ("unresolved_registry", unresolved_registry),
        ("rejected_registry", rejected_registry),
    ):

        if not isinstance(
            value,
            list,
        ):
            raise CrossDocumentReasoningError(
                name + " must be a list."
            )

    if len(
        relationships
    ) != final_result.get(
        "relationship_count"
    ):
        raise CrossDocumentReasoningError(
            "Final relationship count drifted."
        )

    # -------------------------------------------------------------
    # Reverify every final relationship
    # -------------------------------------------------------------

    reasoning_ids = []

    for item in relationships:

        if not isinstance(
            item,
            Mapping,
        ):
            raise CrossDocumentReasoningError(
                "Final relationship entry is invalid."
            )

        for field in (
            "reasoning_integrity_verified",
            "provenance_trace_available",
            "uncertainty_preserved",
        ):

            if item.get(field) is not True:
                raise CrossDocumentReasoningError(
                    f"Required final relationship field is not True: {field}"
                )

        for field in (
            "conflict_resolved",
            "source_profile_modified",
            "retrieval_payload_modified",
            "semantic_memory_written",
            "linking_decision",
        ):

            if item.get(field) is not False:
                raise CrossDocumentReasoningError(
                    f"Forbidden final relationship field is not False: {field}"
                )

        reasoning_status = item.get(
            "reasoning_status"
        )

        if reasoning_status not in (
            "CONFIRMED",
            "REJECTED",
            "UNRESOLVED",
            "CONFLICT_DETECTED",
        ):
            raise CrossDocumentReasoningError(
                "Unsupported final reasoning status."
            )

        if (
            reasoning_status == "CONFLICT_DETECTED"
            and item.get(
                "conflict_detected"
            ) is not True
        ):
            raise CrossDocumentReasoningError(
                "Conflict status lost its conflict flag."
            )

        if (
            reasoning_status == "CONFLICT_DETECTED"
            and item.get(
                "uncertainty_state"
            ) not in (
                "HIGH",
                "MODERATE",
            )
        ):
            raise CrossDocumentReasoningError(
                "Conflict uncertainty was improperly reduced."
            )

        reasoning_id = item.get(
            "reasoning_id"
        )

        if not isinstance(
            reasoning_id,
            str,
        ) or not reasoning_id.startswith(
            "cdrreason:v1:"
        ):
            raise CrossDocumentReasoningError(
                "Final reasoning ID is invalid."
            )

        reasoning_ids.append(
            reasoning_id
        )

    if len(
        reasoning_ids
    ) != len(
        set(reasoning_ids)
    ):
        raise CrossDocumentReasoningError(
            "Duplicate reasoning IDs detected."
        )

    # -------------------------------------------------------------
    # Provenance authority
    # -------------------------------------------------------------

    for field in (
        "lineage_complete_through_4.6.21I",
        "document_lineage_complete",
        "relationship_lineage_complete",
        "evidence_trace_complete",
        "reasoning_trace_complete",
        "conflict_trace_complete",
        "uncertainty_trace_complete",
        "reasoning_integrity_verified",
        "reasoning_provenance_built",
        "source_profiles_preserved",
        "retrieval_payloads_preserved",
        "reasoning_outcomes_preserved",
        "read_only",
    ):

        if provenance.get(field) is not True:
            raise CrossDocumentReasoningError(
                f"Required provenance field is not True: {field}"
            )

    for field in (
        "conflicts_silently_resolved",
        "evidence_invented",
        "unsupported_fact_inference_performed",
        "final_result_built",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if provenance.get(field) is not False:
            raise CrossDocumentReasoningError(
                f"Forbidden provenance field is not False: {field}"
            )

    # -------------------------------------------------------------
    # Integrity guard authority
    # -------------------------------------------------------------

    for field in (
        "reasoning_integrity_verification_performed",
        "all_reasoning_digests_verified",
        "all_reasoning_ids_verified",
        "all_candidate_bindings_verified",
        "all_evidence_bindings_verified",
        "status_consistency_verified",
        "uncertainty_preserved",
        "conflicts_explicit",
        "source_profiles_preserved",
        "retrieval_payloads_preserved",
        "read_only",
    ):

        if integrity_guard.get(field) is not True:
            raise CrossDocumentReasoningError(
                f"Required integrity-guard field is not True: {field}"
            )

    for field in (
        "conflicts_silently_resolved",
        "evidence_invented",
        "unsupported_fact_inference_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if integrity_guard.get(field) is not False:
            raise CrossDocumentReasoningError(
                f"Forbidden integrity-guard field is not False: {field}"
            )

    # -------------------------------------------------------------
    # Recompute J final digest and ID
    # -------------------------------------------------------------

    final_material = {
        "version":
            CROSS_DOCUMENT_REASONING_VERSION,

        "workspace_id":
            workspace_id,

        "document_set_id":
            document_set[
                "document_set_id"
            ],

        "reasoning_scope_id":
            reasoning_scope[
                "reasoning_scope_id"
            ],

        "evidence_alignment_id":
            evidence_alignment[
                "evidence_alignment_id"
            ],

        "relationship_package_id":
            construction[
                "relationship_package_id"
            ],

        "reasoning_package_id":
            execution[
                "reasoning_package_id"
            ],

        "integrity_guard_id":
            integrity_guard[
                "reasoning_integrity_guard_id"
            ],

        "reasoning_provenance_id":
            provenance[
                "reasoning_provenance_id"
            ],

        "reasoning_ids":
            reasoning_ids,

        "conflict_ids": [
            item[
                "conflict_id"
            ]
            for item in conflict_registry
        ],
    }

    final_json = json.dumps(
        final_material,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    expected_final_digest = hashlib.sha256(
        final_json.encode("utf-8")
    ).hexdigest()

    expected_final_id = (
        "cdrfinal:v1:"
        + expected_final_digest[:32]
    )

    if final_result.get(
        "final_result_digest"
    ) != expected_final_digest:
        raise CrossDocumentReasoningError(
            "Final result digest verification failed."
        )

    if final_result.get(
        "final_result_id"
    ) != expected_final_id:
        raise CrossDocumentReasoningError(
            "Final result ID verification failed."
        )

    # -------------------------------------------------------------
    # J summary authority
    # -------------------------------------------------------------

    if summary.get(
        "final_status"
    ) != "CROSS_DOCUMENT_REASONING_RESULT_READY_FOR_CERTIFICATION":
        raise CrossDocumentReasoningError(
            "Final summary status drifted."
        )

    if summary.get(
        "relationship_count"
    ) != len(
        relationships
    ):
        raise CrossDocumentReasoningError(
            "Final summary relationship count drifted."
        )

    if summary.get(
        "conflict_count"
    ) != len(
        conflict_registry
    ):
        raise CrossDocumentReasoningError(
            "Final summary conflict count drifted."
        )

    if summary.get(
        "reasoning_integrity_verified"
    ) is not True:
        raise CrossDocumentReasoningError(
            "Final summary integrity flag drifted."
        )

    if summary.get(
        "reasoning_provenance_complete"
    ) is not True:
        raise CrossDocumentReasoningError(
            "Final summary provenance flag drifted."
        )

    if summary.get(
        "full_cross_document_reasoning_certified"
    ) is not False:
        raise CrossDocumentReasoningError(
            "J must remain uncertified before K."
        )

    if summary.get(
        "next_owner"
    ) != "4.6.21K_FULL_CROSS_DOCUMENT_REASONING_HARD_CERTIFICATION":
        raise CrossDocumentReasoningError(
            "Final summary K owner drifted."
        )

    if summary.get(
        "post_certification_owner"
    ) != "4.6.22_ONTOLOGY_ALIGNMENT":
        raise CrossDocumentReasoningError(
            "Final summary post-certification owner drifted."
        )

    if summary.get(
        "semantic_memory_owner"
    ) != "4.6.28_SEMANTIC_MEMORY":
        raise CrossDocumentReasoningError(
            "Semantic Memory owner drifted."
        )

    # -------------------------------------------------------------
    # J boundary authority
    # -------------------------------------------------------------

    for field in (
        "document_set_scope_contract_preserved",
        "evidence_alignment_preserved",
        "relationship_construction_preserved",
        "reasoning_execution_preserved",
        "reasoning_integrity_guard_preserved",
        "reasoning_provenance_preserved",
        "cross_document_reasoning_architecture_preserved",
        "source_profiles_preserved",
        "retrieval_payloads_preserved",
        "cross_document_evidence_alignment_performed",
        "cross_document_relationships_constructed",
        "cross_document_reasoning_performed",
        "reasoning_integrity_verification_performed",
        "conflict_guard_applied",
        "uncertainty_preserved",
        "reasoning_provenance_built",
        "final_cross_document_reasoning_result_built",
    ):

        if boundaries.get(field) is not True:
            raise CrossDocumentReasoningError(
                f"Required 4.6.21J boundary is not True: {field}"
            )

    for field in (
        "full_cross_document_reasoning_certification_performed",
        "source_profile_modified",
        "retrieval_payload_modified",
        "reasoning_outcome_modified",
        "evidence_invented",
        "unsupported_fact_inference_performed",
        "conflict_silently_resolved",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if boundaries.get(field) is not False:
            raise CrossDocumentReasoningError(
                f"Forbidden 4.6.21J boundary is not False: {field}"
            )

    # -------------------------------------------------------------
    # Certified final result
    # -------------------------------------------------------------

    certified_final = deepcopy(
        dict(final_result)
    )

    certified_final[
        "full_cross_document_reasoning_certified"
    ] = True

    certified_final[
        "certification_status"
    ] = "CERTIFIED"

    certified_final[
        "certification_patch"
    ] = "4.6.21K"

    certified_final[
        "next_owner"
    ] = "4.6.22_ONTOLOGY_ALIGNMENT"

    certified_final[
        "post_certification_owner"
    ] = "4.6.22_ONTOLOGY_ALIGNMENT"

    certified_final[
        "semantic_memory_owner"
    ] = "4.6.28_SEMANTIC_MEMORY"

    certification = {
        "certification_schema":
            "full_cross_document_reasoning_certification_v1",

        "certification_version":
            "v1",

        "certification_status":
            "CERTIFIED",

        "certification_scope":
            "FULL_CROSS_DOCUMENT_REASONING_PIPELINE",

        "certification_phase":
            "4.6.21",

        "certification_patch":
            "4.6.21K",

        "source_patch":
            "4.6.21J",

        "source_final_result_id":
            final_result[
                "final_result_id"
            ],

        "source_final_result_digest":
            final_result[
                "final_result_digest"
            ],

        "document_set_id":
            document_set[
                "document_set_id"
            ],

        "reasoning_scope_id":
            reasoning_scope[
                "reasoning_scope_id"
            ],

        "evidence_alignment_id":
            evidence_alignment[
                "evidence_alignment_id"
            ],

        "relationship_package_id":
            construction[
                "relationship_package_id"
            ],

        "reasoning_package_id":
            execution[
                "reasoning_package_id"
            ],

        "integrity_guard_id":
            integrity_guard[
                "reasoning_integrity_guard_id"
            ],

        "reasoning_provenance_id":
            provenance[
                "reasoning_provenance_id"
            ],

        "relationship_count":
            len(
                relationships
            ),

        "conflict_count":
            len(
                conflict_registry
            ),

        "unresolved_count":
            len(
                unresolved_registry
            ),

        "rejected_count":
            len(
                rejected_registry
            ),

        "all_pipeline_identity_bindings_verified":
            True,

        "final_result_digest_verified":
            True,

        "final_result_id_verified":
            True,

        "reasoning_integrity_verified":
            True,

        "reasoning_provenance_verified":
            True,

        "reasoning_outcomes_preserved":
            True,

        "uncertainty_preserved":
            True,

        "conflicts_explicit":
            True,

        "source_profiles_preserved":
            True,

        "retrieval_payloads_preserved":
            True,

        "evidence_invented":
            False,

        "unsupported_fact_inference_performed":
            False,

        "conflicts_silently_resolved":
            False,

        "semantic_memory_written":
            False,

        "linking_decisions_performed":
            False,

        "ontology_alignment_ready":
            True,

        "next_owner":
            "4.6.22_ONTOLOGY_ALIGNMENT",
    }

    return {
        "schema_version":
            "certified_cross_document_reasoning_result_v1",

        "version":
            CROSS_DOCUMENT_REASONING_VERSION,

        "phase":
            CROSS_DOCUMENT_REASONING_PHASE,

        "patch":
            "4.6.21K",

        "status":
            "CROSS_DOCUMENT_REASONING_CERTIFIED",

        "workspace_id":
            workspace_id,

        "certified_final_cross_document_reasoning_result":
            certified_final,

        "full_cross_document_reasoning_certification":
            certification,

        "source_final_result_envelope":
            deepcopy(
                dict(final_result_envelope)
            ),

        "processing_boundaries": {
            "document_set_scope_contract_preserved":
                True,

            "evidence_alignment_preserved":
                True,

            "relationship_construction_preserved":
                True,

            "reasoning_execution_preserved":
                True,

            "reasoning_integrity_guard_preserved":
                True,

            "reasoning_provenance_preserved":
                True,

            "final_cross_document_reasoning_result_preserved":
                True,

            "cross_document_reasoning_architecture_preserved":
                True,

            "source_profiles_preserved":
                True,

            "retrieval_payloads_preserved":
                True,

            "cross_document_evidence_alignment_performed":
                True,

            "cross_document_relationships_constructed":
                True,

            "cross_document_reasoning_performed":
                True,

            "reasoning_integrity_verification_performed":
                True,

            "conflict_guard_applied":
                True,

            "uncertainty_preserved":
                True,

            "reasoning_provenance_built":
                True,

            "final_cross_document_reasoning_result_built":
                True,

            "full_cross_document_reasoning_certification_performed":
                True,

            "source_profile_modified":
                False,

            "retrieval_payload_modified":
                False,

            "reasoning_outcome_modified":
                False,

            "evidence_invented":
                False,

            "unsupported_fact_inference_performed":
                False,

            "conflict_silently_resolved":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,
        },

        "reasoning_policy":
            "FULL_CROSS_DOCUMENT_REASONING_CERTIFIED",

        "next_stage":
            "ontology_alignment",
    }

