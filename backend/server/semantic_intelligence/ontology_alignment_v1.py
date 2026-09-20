from __future__ import annotations

from copy import deepcopy
from typing import Any


ONTOLOGY_ALIGNMENT_VERSION = "ontology_alignment_v1"
ONTOLOGY_ALIGNMENT_PHASE = "4.6.22"


class OntologyAlignmentError(Exception):
    pass


# =====================================================================
# PATCH 4.6.22A ? Certified 4.6.21K Input Contract Inspection
# =====================================================================

def inspect_certified_cross_document_reasoning_input_v1(
    certified_reasoning_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Inspect the exact certified 4.6.21K Cross-Document Reasoning handoff.

    Inspection only.

    No ontology extraction, normalization, mapping, memory write,
    source mutation, or linking decision is performed.
    """

    from collections.abc import Mapping
    from copy import deepcopy

    if not isinstance(
        certified_reasoning_result,
        Mapping,
    ):
        raise OntologyAlignmentError(
            "certified_reasoning_result must be a mapping."
        )

    # -------------------------------------------------------------
    # Exact 4.6.21K lifecycle
    # -------------------------------------------------------------

    expected_lifecycle = {
        "schema_version":
            "certified_cross_document_reasoning_result_v1",

        "version":
            "cross_document_reasoning_v1",

        "phase":
            "4.6.21",

        "patch":
            "4.6.21K",

        "status":
            "CROSS_DOCUMENT_REASONING_CERTIFIED",

        "reasoning_policy":
            "FULL_CROSS_DOCUMENT_REASONING_CERTIFIED",

        "next_stage":
            "ontology_alignment",
    }

    for field, expected in expected_lifecycle.items():

        if certified_reasoning_result.get(field) != expected:
            raise OntologyAlignmentError(
                f"Invalid certified 4.6.21K lifecycle field: {field}"
            )

    workspace_id = certified_reasoning_result.get(
        "workspace_id"
    )

    certified_final = certified_reasoning_result.get(
        "certified_final_cross_document_reasoning_result"
    )

    certification = certified_reasoning_result.get(
        "full_cross_document_reasoning_certification"
    )

    source_envelope = certified_reasoning_result.get(
        "source_final_result_envelope"
    )

    source_boundaries = certified_reasoning_result.get(
        "processing_boundaries"
    )

    for name, value in (
        (
            "certified_final_cross_document_reasoning_result",
            certified_final,
        ),
        (
            "full_cross_document_reasoning_certification",
            certification,
        ),
        (
            "source_final_result_envelope",
            source_envelope,
        ),
        (
            "processing_boundaries",
            source_boundaries,
        ),
    ):

        if not isinstance(
            value,
            Mapping,
        ):
            raise OntologyAlignmentError(
                name + " is missing."
            )

    # -------------------------------------------------------------
    # 4.6.21K certification authority
    # -------------------------------------------------------------

    for field, expected in (
        (
            "certification_schema",
            "full_cross_document_reasoning_certification_v1",
        ),
        (
            "certification_version",
            "v1",
        ),
        (
            "certification_status",
            "CERTIFIED",
        ),
        (
            "certification_scope",
            "FULL_CROSS_DOCUMENT_REASONING_PIPELINE",
        ),
        (
            "certification_phase",
            "4.6.21",
        ),
        (
            "certification_patch",
            "4.6.21K",
        ),
        (
            "source_patch",
            "4.6.21J",
        ),
        (
            "next_owner",
            "4.6.22_ONTOLOGY_ALIGNMENT",
        ),
    ):

        if certification.get(field) != expected:
            raise OntologyAlignmentError(
                f"Certification field drifted: {field}"
            )

    for field in (
        "all_pipeline_identity_bindings_verified",
        "final_result_digest_verified",
        "final_result_id_verified",
        "reasoning_integrity_verified",
        "reasoning_provenance_verified",
        "reasoning_outcomes_preserved",
        "uncertainty_preserved",
        "conflicts_explicit",
        "source_profiles_preserved",
        "retrieval_payloads_preserved",
        "ontology_alignment_ready",
    ):

        if certification.get(field) is not True:
            raise OntologyAlignmentError(
                f"Required certification field is not True: {field}"
            )

    for field in (
        "evidence_invented",
        "unsupported_fact_inference_performed",
        "conflicts_silently_resolved",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if certification.get(field) is not False:
            raise OntologyAlignmentError(
                f"Forbidden certification field is not False: {field}"
            )

    # -------------------------------------------------------------
    # Certified final reasoning authority
    # -------------------------------------------------------------

    for field, expected in (
        (
            "full_cross_document_reasoning_certified",
            True,
        ),
        (
            "certification_status",
            "CERTIFIED",
        ),
        (
            "certification_patch",
            "4.6.21K",
        ),
        (
            "next_owner",
            "4.6.22_ONTOLOGY_ALIGNMENT",
        ),
        (
            "semantic_memory_owner",
            "4.6.28_SEMANTIC_MEMORY",
        ),
    ):

        if certified_final.get(field) != expected:
            raise OntologyAlignmentError(
                f"Certified-final field drifted: {field}"
            )

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

        if certified_final.get(field) is not True:
            raise OntologyAlignmentError(
                f"Required certified-final field is not True: {field}"
            )

    for field in (
        "evidence_invented",
        "unsupported_fact_inference_performed",
        "conflicts_silently_resolved",
        "source_profile_modified",
        "retrieval_payload_modified",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if certified_final.get(field) is not False:
            raise OntologyAlignmentError(
                f"Forbidden certified-final field is not False: {field}"
            )

    relationships = certified_final.get(
        "relationships"
    )

    conflict_registry = certified_final.get(
        "conflict_registry"
    )

    reasoning_provenance = certified_final.get(
        "reasoning_provenance"
    )

    if not isinstance(
        relationships,
        list,
    ):
        raise OntologyAlignmentError(
            "Certified relationships are missing."
        )

    if not isinstance(
        conflict_registry,
        list,
    ):
        raise OntologyAlignmentError(
            "Certified conflict registry is missing."
        )

    if not isinstance(
        reasoning_provenance,
        Mapping,
    ):
        raise OntologyAlignmentError(
            "Certified reasoning provenance is missing."
        )

    if len(
        relationships
    ) != certified_final.get(
        "relationship_count"
    ):
        raise OntologyAlignmentError(
            "Certified relationship count drifted."
        )

    # -------------------------------------------------------------
    # Cross-package identity bindings
    # -------------------------------------------------------------

    for field in (
        "document_set_id",
        "reasoning_scope_id",
        "evidence_alignment_id",
        "relationship_package_id",
        "reasoning_package_id",
        "integrity_guard_id",
        "reasoning_provenance_id",
    ):

        if certification.get(field) != certified_final.get(field):
            raise OntologyAlignmentError(
                f"Certification/final identity drifted: {field}"
            )

    if certification.get(
        "source_final_result_id"
    ) != certified_final.get(
        "final_result_id"
    ):
        raise OntologyAlignmentError(
            "Final result ID binding drifted."
        )

    if certification.get(
        "source_final_result_digest"
    ) != certified_final.get(
        "final_result_digest"
    ):
        raise OntologyAlignmentError(
            "Final result digest binding drifted."
        )

    # -------------------------------------------------------------
    # Source K boundaries
    # -------------------------------------------------------------

    for field in (
        "document_set_scope_contract_preserved",
        "evidence_alignment_preserved",
        "relationship_construction_preserved",
        "reasoning_execution_preserved",
        "reasoning_integrity_guard_preserved",
        "reasoning_provenance_preserved",
        "final_cross_document_reasoning_result_preserved",
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
        "full_cross_document_reasoning_certification_performed",
    ):

        if source_boundaries.get(field) is not True:
            raise OntologyAlignmentError(
                f"Required 4.6.21K boundary is not True: {field}"
            )

    for field in (
        "source_profile_modified",
        "retrieval_payload_modified",
        "reasoning_outcome_modified",
        "evidence_invented",
        "unsupported_fact_inference_performed",
        "conflict_silently_resolved",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if source_boundaries.get(field) is not False:
            raise OntologyAlignmentError(
                f"Forbidden 4.6.21K boundary is not False: {field}"
            )

    inspection = {
        "inspection_status":
            "PASSED",

        "inspection_scope":
            "CERTIFIED_4.6.21K_CROSS_DOCUMENT_REASONING_INPUT",

        "source_phase":
            "4.6.21",

        "source_patch":
            "4.6.21K",

        "source_schema":
            "certified_cross_document_reasoning_result_v1",

        "cross_document_reasoning_certified":
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

        "ontology_alignment_ready":
            True,

        "ontology_alignment_owner_confirmed":
            True,

        "semantic_memory_deferred":
            True,

        "linking_deferred":
            True,

        "ontology_alignment_performed":
            False,
    }

    return {
        "schema_version":
            "ontology_alignment_input_inspection_result_v1",

        "version":
            ONTOLOGY_ALIGNMENT_VERSION,

        "phase":
            ONTOLOGY_ALIGNMENT_PHASE,

        "patch":
            "4.6.22A",

        "status":
            "CERTIFIED_CROSS_DOCUMENT_REASONING_INPUT_INSPECTED",

        "workspace_id":
            workspace_id,

        "certified_final_cross_document_reasoning_result":
            deepcopy(
                dict(certified_final)
            ),

        "full_cross_document_reasoning_certification":
            deepcopy(
                dict(certification)
            ),

        "inspection":
            inspection,

        "source_certified_cross_document_reasoning_result":
            deepcopy(
                dict(certified_reasoning_result)
            ),

        "processing_boundaries": {
            "certified_cross_document_reasoning_input_inspected":
                True,

            "certified_cross_document_reasoning_input_preserved":
                True,

            "reasoning_integrity_preserved":
                True,

            "reasoning_provenance_preserved":
                True,

            "reasoning_outcomes_preserved":
                True,

            "uncertainty_preserved":
                True,

            "conflicts_preserved":
                True,

            "ontology_alignment_architecture_defined":
                False,

            "ontology_alignment_intake_validated":
                False,

            "ontology_scope_defined":
                False,

            "concept_vocabulary_extracted":
                False,

            "canonical_concept_normalization_performed":
                False,

            "ontology_mapping_performed":
                False,

            "ontology_alignment_performed":
                False,

            "ontology_integrity_verification_performed":
                False,

            "ontology_provenance_built":
                False,

            "final_ontology_alignment_result_built":
                False,

            "full_ontology_alignment_certification_performed":
                False,

            "source_reasoning_modified":
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

        "alignment_policy":
            "CERTIFIED_CROSS_DOCUMENT_REASONING_INPUT_ONLY",

        "next_stage":
            "ontology_alignment_architecture_definition",
    }


# =====================================================================
# PATCH 4.6.22B ? Ontology Alignment Architecture Definition
# =====================================================================

def define_ontology_alignment_architecture_v1() -> dict[str, Any]:
    """
    Define the canonical Ontology Alignment architecture.

    Architecture only.

    No concept extraction, normalization, ontology mapping,
    Semantic Memory write, source mutation, or linking decision
    occurs in this stage.
    """

    architecture = {
        "architecture_schema":
            "ontology_alignment_architecture_v1",

        "architecture_version":
            "v1",

        "architecture_status":
            "DEFINED",

        "phase":
            ONTOLOGY_ALIGNMENT_PHASE,

        "owner":
            "4.6.22_ONTOLOGY_ALIGNMENT",

        "source_owner":
            "4.6.21_CROSS_DOCUMENT_REASONING",

        "next_owner":
            "4.6.23_TRANSFER_LEARNING",

        "semantic_memory_owner":
            "4.6.28_SEMANTIC_MEMORY",

        "scope":
            "CERTIFIED_CROSS_DOCUMENT_ONTOLOGY_ALIGNMENT",

        "mode":
            "EVIDENCE_BOUND_READ_ONLY_ONTOLOGY_ALIGNMENT",

        "input_contract":
            "certified_cross_document_reasoning_result_v1",

        "output_contract":
            "certified_ontology_alignment_result_v1",

        "canonical_source":
            "4.6.21K_CERTIFIED_CROSS_DOCUMENT_REASONING",

        "principles": {
            "certified_cross_document_reasoning_input_only":
                True,

            "canonical_concepts_must_be_evidence_bound":
                True,

            "entity_identity_must_be_preserved":
                True,

            "surface_forms_may_map_to_canonical_concepts":
                True,

            "ambiguous_terms_must_not_be_forced":
                True,

            "conflicts_must_remain_explicit":
                True,

            "uncertainty_must_be_preserved":
                True,

            "source_reasoning_is_immutable":
                True,

            "source_profiles_are_immutable":
                True,

            "retrieval_payloads_are_immutable":
                True,

            "deterministic_output_required":
                True,

            "provenance_required":
                True,

            "semantic_memory_write_forbidden":
                True,

            "linking_decision_forbidden":
                True,
        },

        "supported_alignment_families": [
            "EXACT_CANONICAL_MATCH",
            "SYNONYM_EQUIVALENCE",
            "ALIAS_EQUIVALENCE",
            "ABBREVIATION_EQUIVALENCE",
            "SPELLING_VARIANT",
            "MORPHOLOGICAL_VARIANT",
            "GENERAL_SPECIFIC",
            "PARENT_CHILD",
            "ENTITY_EQUIVALENCE",
            "ENTITY_ALIAS",
            "TOPIC_EQUIVALENCE",
            "RELATIONSHIP_EQUIVALENCE",
            "CROSS_TERMINOLOGY_EQUIVALENCE",
            "DOMAIN_SPECIFIC_EQUIVALENCE",
            "POTENTIAL_EQUIVALENCE",
            "AMBIGUOUS_MAPPING",
            "CONFLICTING_MAPPING",
            "UNRESOLVED_MAPPING",
        ],

        "canonicalization_contract": {
            "preserve_original_surface_form":
                True,

            "canonical_label_required_when_resolved":
                True,

            "canonical_id_required_when_resolved":
                True,

            "canonical_type_required":
                True,

            "source_concept_identity_required":
                True,

            "source_document_identity_required":
                True,

            "mapping_family_required":
                True,

            "mapping_evidence_required":
                True,

            "confidence_state_required":
                True,

            "uncertainty_state_required":
                True,

            "ambiguous_mapping_must_remain_unresolved":
                True,

            "conflicting_mapping_must_remain_explicit":
                True,

            "invented_canonical_concepts_forbidden":
                True,
        },

        "canonical_concept_types": [
            "ENTITY",
            "TOPIC",
            "CONCEPT",
            "ATTRIBUTE",
            "STATE",
            "PROCESS",
            "EVENT",
            "ACTION",
            "CONDITION",
            "TREATMENT",
            "SYMPTOM",
            "DIAGNOSIS",
            "CAUSE",
            "EFFECT",
            "PROBLEM",
            "SOLUTION",
            "PRODUCT",
            "SERVICE",
            "ORGANIZATION",
            "PERSON",
            "PLACE",
            "TECHNOLOGY",
            "METRIC",
            "TEMPORAL_CONCEPT",
            "OTHER",
        ],

        "evidence_requirements": {
            "document_identity_required":
                True,

            "reasoning_identity_required":
                True,

            "relationship_identity_required":
                True,

            "reasoning_provenance_required":
                True,

            "source_evidence_required":
                True,

            "surface_form_required":
                True,

            "semantic_context_required":
                True,

            "mapping_evidence_required":
                True,

            "alignment_trace_required":
                True,

            "conflict_evidence_required_when_conflicted":
                True,

            "uncertainty_evidence_required_when_uncertain":
                True,

            "unsupported_mapping_forbidden":
                True,
        },

        "scope_contract": {
            "workspace_identity_required":
                True,

            "document_set_identity_required":
                True,

            "reasoning_scope_identity_required":
                True,

            "ontology_scope_must_be_explicit":
                True,

            "concept_types_must_be_declared":
                True,

            "alignment_families_must_be_declared":
                True,

            "cross_workspace_alignment_forbidden":
                True,

            "scope_mutation_forbidden":
                True,
        },

        "extraction_contract": {
            "extract_from_certified_reasoning_only":
                True,

            "extract_entities":
                True,

            "extract_topics":
                True,

            "extract_concepts":
                True,

            "extract_relationship_terms":
                True,

            "extract_surface_forms":
                True,

            "extract_contextual_evidence":
                True,

            "preserve_document_lineage":
                True,

            "preserve_reasoning_lineage":
                True,

            "invent_vocabulary":
                False,
        },

        "normalization_contract": {
            "case_normalization_allowed":
                True,

            "whitespace_normalization_allowed":
                True,

            "punctuation_normalization_allowed":
                True,

            "unicode_normalization_allowed":
                True,

            "deterministic_surface_normalization_required":
                True,

            "semantic_equivalence_requires_evidence":
                True,

            "abbreviation_expansion_requires_evidence":
                True,

            "alias_resolution_requires_evidence":
                True,

            "canonical_merge_requires_evidence":
                True,

            "ambiguous_merge_forbidden":
                True,

            "conflicting_merge_forbidden":
                True,
        },

        "mapping_contract": {
            "map_only_declared_scope":
                True,

            "map_only_extracted_vocabulary":
                True,

            "canonical_mapping_requires_evidence":
                True,

            "relationship_mapping_requires_evidence":
                True,

            "hierarchy_mapping_requires_evidence":
                True,

            "confidence_required":
                True,

            "uncertainty_required":
                True,

            "ambiguous_mapping_allowed_as_unresolved":
                True,

            "conflicting_mapping_allowed_as_conflict":
                True,

            "unsupported_mapping_forbidden":
                True,

            "source_reasoning_mutation_forbidden":
                True,

            "semantic_memory_write_forbidden":
                True,

            "linking_decision_forbidden":
                True,
        },

        "ambiguity_guard_contract": {
            "detect_multi_candidate_mapping":
                True,

            "detect_entity_type_conflict":
                True,

            "detect_hierarchy_conflict":
                True,

            "detect_canonical_id_collision":
                True,

            "detect_evidence_conflict":
                True,

            "detect_scope_violation":
                True,

            "ambiguous_mapping_must_not_be_auto_resolved":
                True,

            "conflicting_mapping_must_not_be_silently_resolved":
                True,

            "uncertainty_must_be_preserved":
                True,

            "guard_evidence_trace_required":
                True,
        },

        "provenance_contract": {
            "source_document_lineage_required":
                True,

            "source_reasoning_lineage_required":
                True,

            "surface_form_lineage_required":
                True,

            "canonical_mapping_lineage_required":
                True,

            "ontology_relationship_lineage_required":
                True,

            "ambiguity_trace_required":
                True,

            "conflict_trace_required":
                True,

            "result_digest_required":
                True,
        },

        "execution_contract": {
            "4.6.22A":
                "CERTIFIED_4.6.21K_INPUT_CONTRACT_INSPECTION",

            "4.6.22B":
                "ONTOLOGY_ALIGNMENT_ARCHITECTURE_DEFINITION",

            "4.6.22C":
                "ONTOLOGY_ALIGNMENT_INTAKE_VALIDATION",

            "4.6.22D":
                "ONTOLOGY_VOCABULARY_SCOPE_CONTRACT",

            "4.6.22E":
                "CONCEPT_ENTITY_VOCABULARY_EXTRACTION",

            "4.6.22F":
                "CANONICAL_CONCEPT_NORMALIZATION",

            "4.6.22G":
                "ONTOLOGY_MAPPING_AND_ALIGNMENT_EXECUTION",

            "4.6.22H":
                "ALIGNMENT_INTEGRITY_AND_AMBIGUITY_GUARD",

            "4.6.22I":
                "ONTOLOGY_PROVENANCE_AND_MAPPING_TRACE",

            "4.6.22J":
                "FINAL_ONTOLOGY_ALIGNMENT_RESULT",

            "4.6.22K":
                "FULL_ONTOLOGY_ALIGNMENT_HARD_CERTIFICATION",
        },

        "stage_order": [
            "4.6.22A",
            "4.6.22B",
            "4.6.22C",
            "4.6.22D",
            "4.6.22E",
            "4.6.22F",
            "4.6.22G",
            "4.6.22H",
            "4.6.22I",
            "4.6.22J",
            "4.6.22K",
        ],

        "downstream_boundaries": {
            "transfer_learning_owner":
                "4.6.23_TRANSFER_LEARNING",

            "authority_owner":
                "4.6.24_AUTHORITY",

            "claim_integrity_owner":
                "4.6.25_CLAIM_INTEGRITY_AND_CONFLICT",

            "dynamic_semantic_graph_owner":
                "4.6.26_DYNAMIC_SEMANTIC_GRAPH",

            "learning_engine_owner":
                "4.6.27_LEARNING_ENGINE",

            "semantic_memory_owner":
                "4.6.28_SEMANTIC_MEMORY",

            "explainability_owner":
                "4.6.29_EXPLAINABILITY",

            "linking_decisions_owned_here":
                False,
        },

        "architecture_boundaries": {
            "architecture_defined":
                True,

            "input_inspection_performed":
                False,

            "intake_validation_performed":
                False,

            "ontology_scope_defined":
                False,

            "vocabulary_extracted":
                False,

            "canonical_normalization_performed":
                False,

            "ontology_mapping_performed":
                False,

            "ontology_alignment_performed":
                False,

            "integrity_guard_performed":
                False,

            "provenance_built":
                False,

            "final_result_built":
                False,

            "full_certification_performed":
                False,

            "source_reasoning_modified":
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
    }

    return architecture


# =====================================================================
# PATCH 4.6.22C ? Ontology Alignment Intake Validation
# =====================================================================

def validate_ontology_alignment_intake_v1(
    inspection_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Validate the certified 4.6.22A intake against the
    canonical 4.6.22B Ontology Alignment architecture.

    Validation only.

    No ontology scope construction, vocabulary extraction,
    normalization, mapping, Semantic Memory write,
    or linking decision is performed.
    """

    from collections.abc import Mapping
    from copy import deepcopy

    if not isinstance(
        inspection_result,
        Mapping,
    ):
        raise OntologyAlignmentError(
            "inspection_result must be a mapping."
        )

    # -------------------------------------------------------------
    # Exact 4.6.22A lifecycle
    # -------------------------------------------------------------

    for field, expected in (
        (
            "schema_version",
            "ontology_alignment_input_inspection_result_v1",
        ),
        (
            "version",
            ONTOLOGY_ALIGNMENT_VERSION,
        ),
        (
            "phase",
            ONTOLOGY_ALIGNMENT_PHASE,
        ),
        (
            "patch",
            "4.6.22A",
        ),
        (
            "status",
            "CERTIFIED_CROSS_DOCUMENT_REASONING_INPUT_INSPECTED",
        ),
        (
            "alignment_policy",
            "CERTIFIED_CROSS_DOCUMENT_REASONING_INPUT_ONLY",
        ),
        (
            "next_stage",
            "ontology_alignment_architecture_definition",
        ),
    ):

        if inspection_result.get(field) != expected:
            raise OntologyAlignmentError(
                f"Invalid 4.6.22A lifecycle field: {field}"
            )

    workspace_id = inspection_result.get(
        "workspace_id"
    )

    certified_final = inspection_result.get(
        "certified_final_cross_document_reasoning_result"
    )

    certification = inspection_result.get(
        "full_cross_document_reasoning_certification"
    )

    inspection = inspection_result.get(
        "inspection"
    )

    source_result = inspection_result.get(
        "source_certified_cross_document_reasoning_result"
    )

    boundaries = inspection_result.get(
        "processing_boundaries"
    )

    architecture = define_ontology_alignment_architecture_v1()

    for name, value in (
        (
            "certified_final_cross_document_reasoning_result",
            certified_final,
        ),
        (
            "full_cross_document_reasoning_certification",
            certification,
        ),
        (
            "inspection",
            inspection,
        ),
        (
            "source_certified_cross_document_reasoning_result",
            source_result,
        ),
        (
            "processing_boundaries",
            boundaries,
        ),
        (
            "ontology_alignment_architecture",
            architecture,
        ),
    ):

        if not isinstance(
            value,
            Mapping,
        ):
            raise OntologyAlignmentError(
                name + " is missing."
            )

    # -------------------------------------------------------------
    # Architecture authority
    # -------------------------------------------------------------

    if architecture.get(
        "architecture_schema"
    ) != "ontology_alignment_architecture_v1":
        raise OntologyAlignmentError(
            "Ontology Alignment architecture schema drifted."
        )

    if architecture.get(
        "architecture_status"
    ) != "DEFINED":
        raise OntologyAlignmentError(
            "Ontology Alignment architecture is not defined."
        )

    if architecture.get(
        "owner"
    ) != "4.6.22_ONTOLOGY_ALIGNMENT":
        raise OntologyAlignmentError(
            "Ontology Alignment owner drifted."
        )

    if architecture.get(
        "source_owner"
    ) != "4.6.21_CROSS_DOCUMENT_REASONING":
        raise OntologyAlignmentError(
            "Ontology Alignment source owner drifted."
        )

    if architecture.get(
        "input_contract"
    ) != "certified_cross_document_reasoning_result_v1":
        raise OntologyAlignmentError(
            "Ontology Alignment input contract drifted."
        )

    execution_contract = architecture.get(
        "execution_contract"
    )

    if not isinstance(
        execution_contract,
        Mapping,
    ):
        raise OntologyAlignmentError(
            "Ontology Alignment execution contract is missing."
        )

    if execution_contract.get(
        "4.6.22C"
    ) != "ONTOLOGY_ALIGNMENT_INTAKE_VALIDATION":
        raise OntologyAlignmentError(
            "4.6.22C execution contract drifted."
        )

    # -------------------------------------------------------------
    # A inspection authority
    # -------------------------------------------------------------

    for field, expected in (
        (
            "inspection_status",
            "PASSED",
        ),
        (
            "inspection_scope",
            "CERTIFIED_4.6.21K_CROSS_DOCUMENT_REASONING_INPUT",
        ),
        (
            "source_phase",
            "4.6.21",
        ),
        (
            "source_patch",
            "4.6.21K",
        ),
        (
            "source_schema",
            "certified_cross_document_reasoning_result_v1",
        ),
    ):

        if inspection.get(field) != expected:
            raise OntologyAlignmentError(
                f"Inspection field drifted: {field}"
            )

    for field in (
        "cross_document_reasoning_certified",
        "reasoning_integrity_verified",
        "reasoning_provenance_verified",
        "reasoning_outcomes_preserved",
        "uncertainty_preserved",
        "conflicts_explicit",
        "ontology_alignment_ready",
        "ontology_alignment_owner_confirmed",
        "semantic_memory_deferred",
        "linking_deferred",
    ):

        if inspection.get(field) is not True:
            raise OntologyAlignmentError(
                f"Required inspection field is not True: {field}"
            )

    if inspection.get(
        "ontology_alignment_performed"
    ) is not False:
        raise OntologyAlignmentError(
            "Ontology Alignment was performed before intake validation."
        )

    # -------------------------------------------------------------
    # Certified 4.6.21K authority
    # -------------------------------------------------------------

    if source_result.get(
        "schema_version"
    ) != "certified_cross_document_reasoning_result_v1":
        raise OntologyAlignmentError(
            "Certified source schema drifted."
        )

    if source_result.get(
        "status"
    ) != "CROSS_DOCUMENT_REASONING_CERTIFIED":
        raise OntologyAlignmentError(
            "Certified source status drifted."
        )

    if source_result.get(
        "next_stage"
    ) != "ontology_alignment":
        raise OntologyAlignmentError(
            "Certified source handoff drifted."
        )

    if certification.get(
        "certification_status"
    ) != "CERTIFIED":
        raise OntologyAlignmentError(
            "Cross-Document Reasoning certification is invalid."
        )

    if certification.get(
        "next_owner"
    ) != "4.6.22_ONTOLOGY_ALIGNMENT":
        raise OntologyAlignmentError(
            "Certification ownership drifted."
        )

    if certification.get(
        "ontology_alignment_ready"
    ) is not True:
        raise OntologyAlignmentError(
            "Certified reasoning is not ontology-alignment ready."
        )

    if certified_final.get(
        "full_cross_document_reasoning_certified"
    ) is not True:
        raise OntologyAlignmentError(
            "Certified final reasoning is not fully certified."
        )

    if certified_final.get(
        "certification_status"
    ) != "CERTIFIED":
        raise OntologyAlignmentError(
            "Certified final reasoning status drifted."
        )

    if certified_final.get(
        "next_owner"
    ) != "4.6.22_ONTOLOGY_ALIGNMENT":
        raise OntologyAlignmentError(
            "Certified final owner drifted."
        )

    # -------------------------------------------------------------
    # Required reasoning payload
    # -------------------------------------------------------------

    relationships = certified_final.get(
        "relationships"
    )

    conflict_registry = certified_final.get(
        "conflict_registry"
    )

    unresolved_registry = certified_final.get(
        "unresolved_registry",
        [],
    )

    rejected_registry = certified_final.get(
        "rejected_registry",
        [],
    )

    provenance = certified_final.get(
        "reasoning_provenance"
    )

    if not isinstance(
        relationships,
        list,
    ):
        raise OntologyAlignmentError(
            "Certified relationships must be a list."
        )

    if not isinstance(
        conflict_registry,
        list,
    ):
        raise OntologyAlignmentError(
            "Conflict registry must be a list."
        )

    if not isinstance(
        unresolved_registry,
        list,
    ):
        raise OntologyAlignmentError(
            "Unresolved registry must be a list."
        )

    if not isinstance(
        rejected_registry,
        list,
    ):
        raise OntologyAlignmentError(
            "Rejected registry must be a list."
        )

    if not isinstance(
        provenance,
        Mapping,
    ):
        raise OntologyAlignmentError(
            "Reasoning provenance is required."
        )

    if len(
        relationships
    ) != certified_final.get(
        "relationship_count"
    ):
        raise OntologyAlignmentError(
            "Certified relationship count drifted."
        )

    if len(
        relationships
    ) == 0:
        raise OntologyAlignmentError(
            "Ontology Alignment requires at least one certified relationship."
        )

    # -------------------------------------------------------------
    # Validate relationship surfaces
    # -------------------------------------------------------------

    allowed_statuses = {
        "CONFIRMED",
        "REJECTED",
        "UNRESOLVED",
        "CONFLICT_DETECTED",
    }

    seen_reasoning_ids = set()

    relationship_families = set()

    source_article_ids = set()

    target_article_ids = set()

    for item in relationships:

        if not isinstance(
            item,
            Mapping,
        ):
            raise OntologyAlignmentError(
                "Certified relationship entry is invalid."
            )

        reasoning_id = item.get(
            "reasoning_id"
        )

        family = item.get(
            "relationship_family"
        )

        status = item.get(
            "reasoning_status"
        )

        source_article_id = item.get(
            "source_article_id"
        )

        target_article_id = item.get(
            "target_article_id"
        )

        if not isinstance(
            reasoning_id,
            str,
        ) or not reasoning_id:
            raise OntologyAlignmentError(
                "Reasoning identity is required."
            )

        if reasoning_id in seen_reasoning_ids:
            raise OntologyAlignmentError(
                "Duplicate reasoning identity detected."
            )

        seen_reasoning_ids.add(
            reasoning_id
        )

        if not isinstance(
            family,
            str,
        ) or not family:
            raise OntologyAlignmentError(
                "Relationship family is required."
            )

        relationship_families.add(
            family
        )

        if status not in allowed_statuses:
            raise OntologyAlignmentError(
                "Unsupported reasoning status."
            )

        if not isinstance(
            source_article_id,
            str,
        ) or not source_article_id:
            raise OntologyAlignmentError(
                "Source article identity is required."
            )

        if not isinstance(
            target_article_id,
            str,
        ) or not target_article_id:
            raise OntologyAlignmentError(
                "Target article identity is required."
            )

        source_article_ids.add(
            source_article_id
        )

        target_article_ids.add(
            target_article_id
        )

        if source_article_id == target_article_id:
            raise OntologyAlignmentError(
                "Cross-document relationship cannot reference the same article twice."
            )

        if item.get(
            "reasoning_integrity_verified"
        ) is not True:
            raise OntologyAlignmentError(
                "Relationship integrity is not verified."
            )

        if item.get(
            "provenance_trace_available"
        ) is not True:
            raise OntologyAlignmentError(
                "Relationship provenance trace is missing."
            )

        if item.get(
            "uncertainty_preserved"
        ) is not True:
            raise OntologyAlignmentError(
                "Relationship uncertainty was not preserved."
            )

        if item.get(
            "source_profile_modified"
        ) is not False:
            raise OntologyAlignmentError(
                "Source profile mutation detected."
            )

        if item.get(
            "retrieval_payload_modified"
        ) is not False:
            raise OntologyAlignmentError(
                "Retrieval payload mutation detected."
            )

        if item.get(
            "semantic_memory_written"
        ) is not False:
            raise OntologyAlignmentError(
                "Premature Semantic Memory write detected."
            )

        if item.get(
            "linking_decision"
        ) is not False:
            raise OntologyAlignmentError(
                "Premature linking decision detected."
            )

        if (
            status == "CONFLICT_DETECTED"
            and item.get(
                "conflict_detected"
            ) is not True
        ):
            raise OntologyAlignmentError(
                "Conflict reasoning lost its conflict marker."
            )

        if (
            status == "CONFLICT_DETECTED"
            and item.get(
                "conflict_resolved"
            ) is not False
        ):
            raise OntologyAlignmentError(
                "Conflict was resolved before Ontology Alignment."
            )

    # -------------------------------------------------------------
    # Conflict registry binding
    # -------------------------------------------------------------

    conflict_reasoning_ids = {
        item.get(
            "reasoning_id"
        )
        for item in relationships
        if item.get(
            "reasoning_status"
        ) == "CONFLICT_DETECTED"
    }

    registry_reasoning_ids = set()

    for conflict in conflict_registry:

        if not isinstance(
            conflict,
            Mapping,
        ):
            raise OntologyAlignmentError(
                "Conflict registry entry is invalid."
            )

        reasoning_id = conflict.get(
            "reasoning_id"
        )

        if reasoning_id not in conflict_reasoning_ids:
            raise OntologyAlignmentError(
                "Conflict registry references unknown conflict reasoning."
            )

        registry_reasoning_ids.add(
            reasoning_id
        )

        if conflict.get(
            "conflict_status"
        ) != "OPEN":
            raise OntologyAlignmentError(
                "Ontology Alignment intake requires open conflicts."
            )

        if conflict.get(
            "silently_resolved",
            False,
        ) is not False:
            raise OntologyAlignmentError(
                "Conflict was silently resolved."
            )

    if registry_reasoning_ids != conflict_reasoning_ids:
        raise OntologyAlignmentError(
            "Conflict registry does not fully bind conflict reasoning."
        )

    # -------------------------------------------------------------
    # A boundary authority
    # -------------------------------------------------------------

    for field in (
        "certified_cross_document_reasoning_input_inspected",
        "certified_cross_document_reasoning_input_preserved",
        "reasoning_integrity_preserved",
        "reasoning_provenance_preserved",
        "reasoning_outcomes_preserved",
        "uncertainty_preserved",
        "conflicts_preserved",
    ):

        if boundaries.get(field) is not True:
            raise OntologyAlignmentError(
                f"Required 4.6.22A boundary is not True: {field}"
            )

    for field in (
        "ontology_alignment_architecture_defined",
        "ontology_alignment_intake_validated",
        "ontology_scope_defined",
        "concept_vocabulary_extracted",
        "canonical_concept_normalization_performed",
        "ontology_mapping_performed",
        "ontology_alignment_performed",
        "ontology_integrity_verification_performed",
        "ontology_provenance_built",
        "final_ontology_alignment_result_built",
        "full_ontology_alignment_certification_performed",
        "source_reasoning_modified",
        "source_profile_modified",
        "retrieval_payload_modified",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if boundaries.get(field) is not False:
            raise OntologyAlignmentError(
                f"Forbidden 4.6.22A boundary is not False: {field}"
            )

    # -------------------------------------------------------------
    # Intake validation summary
    # -------------------------------------------------------------

    validation = {
        "validation_schema":
            "ontology_alignment_intake_validation_v1",

        "validation_version":
            "v1",

        "validation_status":
            "PASSED",

        "workspace_id":
            workspace_id,

        "document_set_id":
            certified_final.get(
                "document_set_id"
            ),

        "reasoning_scope_id":
            certified_final.get(
                "reasoning_scope_id"
            ),

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

        "relationship_families":
            sorted(
                relationship_families
            ),

        "source_article_ids":
            sorted(
                source_article_ids
            ),

        "target_article_ids":
            sorted(
                target_article_ids
            ),

        "certified_reasoning_input_valid":
            True,

        "architecture_compatible":
            True,

        "reasoning_identity_integrity_valid":
            True,

        "relationship_structure_valid":
            True,

        "conflict_registry_valid":
            True,

        "provenance_available":
            True,

        "uncertainty_preserved":
            True,

        "ontology_scope_ready":
            True,

        "ontology_alignment_performed":
            False,

        "semantic_memory_written":
            False,

        "linking_decisions_performed":
            False,
    }

    return {
        "schema_version":
            "ontology_alignment_intake_validation_result_v1",

        "version":
            ONTOLOGY_ALIGNMENT_VERSION,

        "phase":
            ONTOLOGY_ALIGNMENT_PHASE,

        "patch":
            "4.6.22C",

        "status":
            "ONTOLOGY_ALIGNMENT_INTAKE_VALIDATED",

        "workspace_id":
            workspace_id,

        "ontology_alignment_architecture":
            deepcopy(
                architecture
            ),

        "intake_validation":
            validation,

        "certified_final_cross_document_reasoning_result":
            deepcopy(
                dict(certified_final)
            ),

        "full_cross_document_reasoning_certification":
            deepcopy(
                dict(certification)
            ),

        "source_input_inspection_result":
            deepcopy(
                dict(inspection_result)
            ),

        "processing_boundaries": {
            "certified_cross_document_reasoning_input_inspected":
                True,

            "certified_cross_document_reasoning_input_preserved":
                True,

            "ontology_alignment_architecture_defined":
                True,

            "ontology_alignment_intake_validated":
                True,

            "reasoning_integrity_preserved":
                True,

            "reasoning_provenance_preserved":
                True,

            "reasoning_outcomes_preserved":
                True,

            "uncertainty_preserved":
                True,

            "conflicts_preserved":
                True,

            "ontology_scope_defined":
                False,

            "concept_vocabulary_extracted":
                False,

            "canonical_concept_normalization_performed":
                False,

            "ontology_mapping_performed":
                False,

            "ontology_alignment_performed":
                False,

            "ontology_integrity_verification_performed":
                False,

            "ontology_provenance_built":
                False,

            "final_ontology_alignment_result_built":
                False,

            "full_ontology_alignment_certification_performed":
                False,

            "source_reasoning_modified":
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

        "alignment_policy":
            "VALIDATION_ONLY_NO_ONTOLOGY_ALIGNMENT",

        "next_stage":
            "ontology_vocabulary_scope_contract",
    }


# =====================================================================
# PATCH 4.6.22D ? Ontology/Vocabulary Scope Contract
# =====================================================================

def build_ontology_vocabulary_scope_contract_v1(
    intake_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Lock the Ontology Alignment scope before vocabulary extraction.

    D defines:
    - workspace scope,
    - document/reasoning scope,
    - permitted concept types,
    - permitted alignment families,
    - source article set,
    - relationship families,
    - conflict and uncertainty preservation boundaries.

    D performs no vocabulary extraction and no ontology mapping.
    """

    from collections.abc import Mapping
    from copy import deepcopy
    import hashlib
    import json

    if not isinstance(
        intake_result,
        Mapping,
    ):
        raise OntologyAlignmentError(
            "intake_result must be a mapping."
        )

    # -------------------------------------------------------------
    # Exact 4.6.22C lifecycle
    # -------------------------------------------------------------

    for field, expected in (
        (
            "schema_version",
            "ontology_alignment_intake_validation_result_v1",
        ),
        (
            "version",
            ONTOLOGY_ALIGNMENT_VERSION,
        ),
        (
            "phase",
            ONTOLOGY_ALIGNMENT_PHASE,
        ),
        (
            "patch",
            "4.6.22C",
        ),
        (
            "status",
            "ONTOLOGY_ALIGNMENT_INTAKE_VALIDATED",
        ),
        (
            "alignment_policy",
            "VALIDATION_ONLY_NO_ONTOLOGY_ALIGNMENT",
        ),
        (
            "next_stage",
            "ontology_vocabulary_scope_contract",
        ),
    ):

        if intake_result.get(field) != expected:
            raise OntologyAlignmentError(
                f"Invalid 4.6.22C lifecycle field: {field}"
            )

    workspace_id = intake_result.get(
        "workspace_id"
    )

    architecture = intake_result.get(
        "ontology_alignment_architecture"
    )

    validation = intake_result.get(
        "intake_validation"
    )

    certified_final = intake_result.get(
        "certified_final_cross_document_reasoning_result"
    )

    boundaries = intake_result.get(
        "processing_boundaries"
    )

    for name, value in (
        (
            "ontology_alignment_architecture",
            architecture,
        ),
        (
            "intake_validation",
            validation,
        ),
        (
            "certified_final_cross_document_reasoning_result",
            certified_final,
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
            raise OntologyAlignmentError(
                name + " is missing."
            )

    # -------------------------------------------------------------
    # Architecture authority
    # -------------------------------------------------------------

    if architecture.get(
        "architecture_status"
    ) != "DEFINED":
        raise OntologyAlignmentError(
            "Ontology Alignment architecture is not defined."
        )

    execution = architecture.get(
        "execution_contract"
    )

    if not isinstance(
        execution,
        Mapping,
    ):
        raise OntologyAlignmentError(
            "Execution contract is missing."
        )

    if execution.get(
        "4.6.22D"
    ) != "ONTOLOGY_VOCABULARY_SCOPE_CONTRACT":
        raise OntologyAlignmentError(
            "4.6.22D execution contract drifted."
        )

    scope_contract = architecture.get(
        "scope_contract"
    )

    if not isinstance(
        scope_contract,
        Mapping,
    ):
        raise OntologyAlignmentError(
            "Architecture scope contract is missing."
        )

    for field in (
        "workspace_identity_required",
        "document_set_identity_required",
        "reasoning_scope_identity_required",
        "ontology_scope_must_be_explicit",
        "concept_types_must_be_declared",
        "alignment_families_must_be_declared",
        "cross_workspace_alignment_forbidden",
        "scope_mutation_forbidden",
    ):

        if scope_contract.get(field) is not True:
            raise OntologyAlignmentError(
                f"Required scope contract field is not True: {field}"
            )

    # -------------------------------------------------------------
    # C validation authority
    # -------------------------------------------------------------

    if validation.get(
        "validation_status"
    ) != "PASSED":
        raise OntologyAlignmentError(
            "Ontology Alignment intake validation did not pass."
        )

    for field in (
        "certified_reasoning_input_valid",
        "architecture_compatible",
        "reasoning_identity_integrity_valid",
        "relationship_structure_valid",
        "conflict_registry_valid",
        "provenance_available",
        "uncertainty_preserved",
        "ontology_scope_ready",
    ):

        if validation.get(field) is not True:
            raise OntologyAlignmentError(
                f"Required intake validation field is not True: {field}"
            )

    if validation.get(
        "ontology_alignment_performed"
    ) is not False:
        raise OntologyAlignmentError(
            "Ontology Alignment already performed before scope definition."
        )

    # -------------------------------------------------------------
    # Certified source identities
    # -------------------------------------------------------------

    document_set_id = certified_final.get(
        "document_set_id"
    )

    reasoning_scope_id = certified_final.get(
        "reasoning_scope_id"
    )

    reasoning_provenance_id = certified_final.get(
        "reasoning_provenance_id"
    )

    if not isinstance(
        workspace_id,
        str,
    ) or not workspace_id:
        raise OntologyAlignmentError(
            "Workspace identity is required."
        )

    for name, value in (
        (
            "document_set_id",
            document_set_id,
        ),
        (
            "reasoning_scope_id",
            reasoning_scope_id,
        ),
        (
            "reasoning_provenance_id",
            reasoning_provenance_id,
        ),
    ):

        if not isinstance(
            value,
            str,
        ) or not value:
            raise OntologyAlignmentError(
                name + " is required."
            )

    # -------------------------------------------------------------
    # Source article set
    # -------------------------------------------------------------

    source_article_ids = validation.get(
        "source_article_ids"
    )

    target_article_ids = validation.get(
        "target_article_ids"
    )

    if not isinstance(
        source_article_ids,
        list,
    ):
        raise OntologyAlignmentError(
            "source_article_ids must be a list."
        )

    if not isinstance(
        target_article_ids,
        list,
    ):
        raise OntologyAlignmentError(
            "target_article_ids must be a list."
        )

    article_ids = sorted(
        set(
            source_article_ids
            + target_article_ids
        )
    )

    if len(
        article_ids
    ) < 2:
        raise OntologyAlignmentError(
            "Ontology Alignment requires at least two distinct articles."
        )

    for article_id in article_ids:

        if not isinstance(
            article_id,
            str,
        ) or not article_id:
            raise OntologyAlignmentError(
                "Invalid article identity in ontology scope."
            )

    # -------------------------------------------------------------
    # Relationship families from certified reasoning
    # -------------------------------------------------------------

    relationship_families = validation.get(
        "relationship_families"
    )

    if not isinstance(
        relationship_families,
        list,
    ) or not relationship_families:
        raise OntologyAlignmentError(
            "Relationship families are required."
        )

    relationship_families = sorted(
        set(
            relationship_families
        )
    )

    # -------------------------------------------------------------
    # Canonical concept and alignment families
    # -------------------------------------------------------------

    concept_types = architecture.get(
        "canonical_concept_types"
    )

    alignment_families = architecture.get(
        "supported_alignment_families"
    )

    if not isinstance(
        concept_types,
        list,
    ) or not concept_types:
        raise OntologyAlignmentError(
            "Canonical concept types are missing."
        )

    if not isinstance(
        alignment_families,
        list,
    ) or not alignment_families:
        raise OntologyAlignmentError(
            "Supported alignment families are missing."
        )

    if len(concept_types) != len(set(concept_types)):
        raise OntologyAlignmentError(
            "Canonical concept types contain duplicates."
        )

    if len(alignment_families) != len(set(alignment_families)):
        raise OntologyAlignmentError(
            "Alignment families contain duplicates."
        )

    # -------------------------------------------------------------
    # Conflict / uncertainty state
    # -------------------------------------------------------------

    conflict_count = validation.get(
        "conflict_count"
    )

    unresolved_count = validation.get(
        "unresolved_count"
    )

    rejected_count = validation.get(
        "rejected_count"
    )

    for name, value in (
        (
            "conflict_count",
            conflict_count,
        ),
        (
            "unresolved_count",
            unresolved_count,
        ),
        (
            "rejected_count",
            rejected_count,
        ),
    ):

        if not isinstance(
            value,
            int,
        ) or value < 0:
            raise OntologyAlignmentError(
                name + " is invalid."
            )

    # -------------------------------------------------------------
    # Deterministic scope identity
    # -------------------------------------------------------------

    scope_material = {
        "workspace_id":
            workspace_id,

        "document_set_id":
            document_set_id,

        "reasoning_scope_id":
            reasoning_scope_id,

        "reasoning_provenance_id":
            reasoning_provenance_id,

        "article_ids":
            article_ids,

        "relationship_families":
            relationship_families,

        "canonical_concept_types":
            sorted(
                concept_types
            ),

        "alignment_families":
            sorted(
                alignment_families
            ),

        "conflict_count":
            conflict_count,

        "unresolved_count":
            unresolved_count,

        "rejected_count":
            rejected_count,
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

    ontology_scope_id = (
        "ontscope:v1:"
        + scope_digest[:32]
    )

    # -------------------------------------------------------------
    # Scope contract
    # -------------------------------------------------------------

    ontology_scope = {
        "ontology_scope_schema":
            "ontology_vocabulary_scope_contract_v1",

        "ontology_scope_version":
            "v1",

        "ontology_scope_id":
            ontology_scope_id,

        "ontology_scope_digest":
            scope_digest,

        "ontology_scope_digest_algorithm":
            "SHA256",

        "workspace_id":
            workspace_id,

        "document_set_id":
            document_set_id,

        "reasoning_scope_id":
            reasoning_scope_id,

        "reasoning_provenance_id":
            reasoning_provenance_id,

        "article_ids":
            article_ids,

        "article_count":
            len(
                article_ids
            ),

        "relationship_families":
            relationship_families,

        "canonical_concept_types":
            sorted(
                concept_types
            ),

        "alignment_families":
            sorted(
                alignment_families
            ),

        "conflict_count":
            conflict_count,

        "unresolved_count":
            unresolved_count,

        "rejected_count":
            rejected_count,

        "cross_workspace_alignment_allowed":
            False,

        "scope_mutable":
            False,

        "source_reasoning_mutable":
            False,

        "source_profiles_mutable":
            False,

        "retrieval_payloads_mutable":
            False,

        "conflicts_must_remain_explicit":
            True,

        "uncertainty_must_be_preserved":
            True,

        "ambiguous_mapping_must_remain_unresolved":
            True,

        "conflicting_mapping_must_remain_explicit":
            True,

        "semantic_memory_write_allowed":
            False,

        "linking_decisions_allowed":
            False,

        "concept_vocabulary_extraction_allowed":
            True,

        "canonical_normalization_allowed":
            False,

        "ontology_mapping_allowed":
            False,

        "scope_status":
            "LOCKED",
    }

    # -------------------------------------------------------------
    # C boundary authority
    # -------------------------------------------------------------

    for field in (
        "certified_cross_document_reasoning_input_inspected",
        "certified_cross_document_reasoning_input_preserved",
        "ontology_alignment_architecture_defined",
        "ontology_alignment_intake_validated",
        "reasoning_integrity_preserved",
        "reasoning_provenance_preserved",
        "reasoning_outcomes_preserved",
        "uncertainty_preserved",
        "conflicts_preserved",
    ):

        if boundaries.get(field) is not True:
            raise OntologyAlignmentError(
                f"Required 4.6.22C boundary is not True: {field}"
            )

    for field in (
        "ontology_scope_defined",
        "concept_vocabulary_extracted",
        "canonical_concept_normalization_performed",
        "ontology_mapping_performed",
        "ontology_alignment_performed",
        "ontology_integrity_verification_performed",
        "ontology_provenance_built",
        "final_ontology_alignment_result_built",
        "full_ontology_alignment_certification_performed",
        "source_reasoning_modified",
        "source_profile_modified",
        "retrieval_payload_modified",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if boundaries.get(field) is not False:
            raise OntologyAlignmentError(
                f"Forbidden 4.6.22C boundary is not False: {field}"
            )

    return {
        "schema_version":
            "ontology_vocabulary_scope_contract_result_v1",

        "version":
            ONTOLOGY_ALIGNMENT_VERSION,

        "phase":
            ONTOLOGY_ALIGNMENT_PHASE,

        "patch":
            "4.6.22D",

        "status":
            "ONTOLOGY_VOCABULARY_SCOPE_DEFINED",

        "workspace_id":
            workspace_id,

        "ontology_alignment_architecture":
            deepcopy(
                dict(architecture)
            ),

        "ontology_vocabulary_scope":
            ontology_scope,

        "certified_final_cross_document_reasoning_result":
            deepcopy(
                dict(certified_final)
            ),

        "source_intake_validation_result":
            deepcopy(
                dict(intake_result)
            ),

        "processing_boundaries": {
            "certified_cross_document_reasoning_input_inspected":
                True,

            "certified_cross_document_reasoning_input_preserved":
                True,

            "ontology_alignment_architecture_defined":
                True,

            "ontology_alignment_intake_validated":
                True,

            "ontology_scope_defined":
                True,

            "reasoning_integrity_preserved":
                True,

            "reasoning_provenance_preserved":
                True,

            "reasoning_outcomes_preserved":
                True,

            "uncertainty_preserved":
                True,

            "conflicts_preserved":
                True,

            "concept_vocabulary_extracted":
                False,

            "canonical_concept_normalization_performed":
                False,

            "ontology_mapping_performed":
                False,

            "ontology_alignment_performed":
                False,

            "ontology_integrity_verification_performed":
                False,

            "ontology_provenance_built":
                False,

            "final_ontology_alignment_result_built":
                False,

            "full_ontology_alignment_certification_performed":
                False,

            "source_reasoning_modified":
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

        "alignment_policy":
            "ONTOLOGY_SCOPE_LOCKED_NO_EXTRACTION_OR_MAPPING",

        "next_stage":
            "concept_entity_vocabulary_extraction",
    }


# =====================================================================
# PATCH 4.6.22E ? Concept & Entity Vocabulary Extraction
# =====================================================================

def extract_concept_entity_vocabulary_v1(
    scope_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Extract evidence-bound vocabulary from the locked ontology scope.

    Extraction only.

    This stage identifies surface forms and their certified lineage.
    It does NOT:
    - canonicalize terms,
    - merge synonyms,
    - resolve aliases,
    - perform ontology mapping,
    - write Semantic Memory,
    - make linking decisions.
    """

    from collections.abc import Mapping
    from copy import deepcopy
    import hashlib
    import json
    import re
    import unicodedata

    if not isinstance(
        scope_result,
        Mapping,
    ):
        raise OntologyAlignmentError(
            "scope_result must be a mapping."
        )

    # -------------------------------------------------------------
    # Exact 4.6.22D lifecycle
    # -------------------------------------------------------------

    for field, expected in (
        (
            "schema_version",
            "ontology_vocabulary_scope_contract_result_v1",
        ),
        (
            "version",
            ONTOLOGY_ALIGNMENT_VERSION,
        ),
        (
            "phase",
            ONTOLOGY_ALIGNMENT_PHASE,
        ),
        (
            "patch",
            "4.6.22D",
        ),
        (
            "status",
            "ONTOLOGY_VOCABULARY_SCOPE_DEFINED",
        ),
        (
            "alignment_policy",
            "ONTOLOGY_SCOPE_LOCKED_NO_EXTRACTION_OR_MAPPING",
        ),
        (
            "next_stage",
            "concept_entity_vocabulary_extraction",
        ),
    ):

        if scope_result.get(field) != expected:
            raise OntologyAlignmentError(
                f"Invalid 4.6.22D lifecycle field: {field}"
            )

    workspace_id = scope_result.get(
        "workspace_id"
    )

    architecture = scope_result.get(
        "ontology_alignment_architecture"
    )

    ontology_scope = scope_result.get(
        "ontology_vocabulary_scope"
    )

    certified_final = scope_result.get(
        "certified_final_cross_document_reasoning_result"
    )

    boundaries = scope_result.get(
        "processing_boundaries"
    )

    for name, value in (
        (
            "ontology_alignment_architecture",
            architecture,
        ),
        (
            "ontology_vocabulary_scope",
            ontology_scope,
        ),
        (
            "certified_final_cross_document_reasoning_result",
            certified_final,
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
            raise OntologyAlignmentError(
                name + " is missing."
            )

    # -------------------------------------------------------------
    # Architecture extraction authority
    # -------------------------------------------------------------

    execution_contract = architecture.get(
        "execution_contract"
    )

    extraction_contract = architecture.get(
        "extraction_contract"
    )

    if not isinstance(
        execution_contract,
        Mapping,
    ):
        raise OntologyAlignmentError(
            "Execution contract is missing."
        )

    if not isinstance(
        extraction_contract,
        Mapping,
    ):
        raise OntologyAlignmentError(
            "Extraction contract is missing."
        )

    if execution_contract.get(
        "4.6.22E"
    ) != "CONCEPT_ENTITY_VOCABULARY_EXTRACTION":
        raise OntologyAlignmentError(
            "4.6.22E execution contract drifted."
        )

    for field in (
        "extract_from_certified_reasoning_only",
        "extract_entities",
        "extract_topics",
        "extract_concepts",
        "extract_relationship_terms",
        "extract_surface_forms",
        "extract_contextual_evidence",
        "preserve_document_lineage",
        "preserve_reasoning_lineage",
    ):

        if extraction_contract.get(field) is not True:
            raise OntologyAlignmentError(
                f"Required extraction contract field is not True: {field}"
            )

    if extraction_contract.get(
        "invent_vocabulary"
    ) is not False:
        raise OntologyAlignmentError(
            "Vocabulary invention is forbidden."
        )

    # -------------------------------------------------------------
    # Locked scope authority
    # -------------------------------------------------------------

    if ontology_scope.get(
        "scope_status"
    ) != "LOCKED":
        raise OntologyAlignmentError(
            "Ontology scope is not locked."
        )

    if ontology_scope.get(
        "concept_vocabulary_extraction_allowed"
    ) is not True:
        raise OntologyAlignmentError(
            "Vocabulary extraction is not allowed by scope."
        )

    for field in (
        "canonical_normalization_allowed",
        "ontology_mapping_allowed",
        "semantic_memory_write_allowed",
        "linking_decisions_allowed",
    ):

        if ontology_scope.get(field) is not False:
            raise OntologyAlignmentError(
                f"Forbidden scope permission is not False: {field}"
            )

    article_ids = ontology_scope.get(
        "article_ids"
    )

    if not isinstance(
        article_ids,
        list,
    ) or not article_ids:
        raise OntologyAlignmentError(
            "Ontology scope article IDs are missing."
        )

    allowed_article_ids = set(
        article_ids
    )

    # -------------------------------------------------------------
    # Certified relationships
    # -------------------------------------------------------------

    relationships = certified_final.get(
        "relationships"
    )

    if not isinstance(
        relationships,
        list,
    ) or not relationships:
        raise OntologyAlignmentError(
            "Certified relationships are required for vocabulary extraction."
        )

    # -------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------

    def safe_text(value):

        if value is None:
            return ""

        if isinstance(
            value,
            bool,
        ):
            return ""

        if isinstance(
            value,
            (int, float),
        ):
            return str(value)

        if isinstance(
            value,
            str,
        ):
            return value.strip()

        return ""

    def normalize_surface(text):

        text = unicodedata.normalize(
            "NFKC",
            safe_text(text),
        )

        text = text.strip()

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text

    def is_extractable_surface(text):

        text = normalize_surface(
            text
        )

        if not text:
            return False

        if len(text) > 300:
            return False

        if text.lower() in {
            "true",
            "false",
            "none",
            "null",
        }:
            return False

        return True

    def classify_surface(path, value):

        p = str(
            path or ""
        ).lower()

        v = normalize_surface(
            value
        )

        if any(
            token in p
            for token in (
                "entity",
                "person",
                "organization",
                "place",
                "product",
                "service",
                "technology",
            )
        ):
            return "ENTITY"

        if any(
            token in p
            for token in (
                "topic",
                "subject",
                "theme",
            )
        ):
            return "TOPIC"

        if any(
            token in p
            for token in (
                "condition",
                "disease",
            )
        ):
            return "CONDITION"

        if "treatment" in p:
            return "TREATMENT"

        if "symptom" in p:
            return "SYMPTOM"

        if "diagnosis" in p:
            return "DIAGNOSIS"

        if "cause" in p:
            return "CAUSE"

        if "effect" in p:
            return "EFFECT"

        if any(
            token in p
            for token in (
                "action",
                "verb",
            )
        ):
            return "ACTION"

        if any(
            token in p
            for token in (
                "process",
                "procedure",
                "workflow",
            )
        ):
            return "PROCESS"

        if any(
            token in p
            for token in (
                "event",
                "incident",
            )
        ):
            return "EVENT"

        if any(
            token in p
            for token in (
                "metric",
                "measure",
                "score",
                "rate",
            )
        ):
            return "METRIC"

        if any(
            token in p
            for token in (
                "concept",
                "keyword",
                "term",
                "phrase",
                "recommendation",
                "value",
            )
        ):
            return "CONCEPT"

        if v:
            return "CONCEPT"

        return "OTHER"

    def walk_evidence(
        value,
        path="evidence",
    ):

        surfaces = []

        if isinstance(
            value,
            Mapping,
        ):

            for key in sorted(
                value.keys(),
                key=str,
            ):

                child = value[
                    key
                ]

                child_path = (
                    f"{path}.{key}"
                )

                surfaces.extend(
                    walk_evidence(
                        child,
                        child_path,
                    )
                )

            return surfaces

        if isinstance(
            value,
            (list, tuple),
        ):

            for index, child in enumerate(
                value
            ):

                child_path = (
                    f"{path}[{index}]"
                )

                surfaces.extend(
                    walk_evidence(
                        child,
                        child_path,
                    )
                )

            return surfaces

        surface = normalize_surface(
            value
        )

        if is_extractable_surface(
            surface
        ):

            surfaces.append(
                (
                    path,
                    surface,
                )
            )

        return surfaces

    # -------------------------------------------------------------
    # Build raw vocabulary occurrences
    # -------------------------------------------------------------

    occurrences = []

    seen_occurrence_ids = set()

    for relationship in sorted(
        relationships,
        key=lambda item: (
            str(
                item.get(
                    "source_article_id",
                    ""
                )
            ),
            str(
                item.get(
                    "target_article_id",
                    ""
                )
            ),
            str(
                item.get(
                    "relationship_family",
                    ""
                )
            ),
            str(
                item.get(
                    "reasoning_id",
                    ""
                )
            ),
        ),
    ):

        if not isinstance(
            relationship,
            Mapping,
        ):
            raise OntologyAlignmentError(
                "Relationship entry is invalid."
            )

        reasoning_id = relationship.get(
            "reasoning_id"
        )

        source_relationship_id = relationship.get(
            "source_relationship_id"
        )

        source_article_id = relationship.get(
            "source_article_id"
        )

        target_article_id = relationship.get(
            "target_article_id"
        )

        family = relationship.get(
            "relationship_family"
        )

        status = relationship.get(
            "reasoning_status"
        )

        evidence = relationship.get(
            "evidence",
            [],
        )

        if source_article_id not in allowed_article_ids:
            raise OntologyAlignmentError(
                "Source article is outside locked ontology scope."
            )

        if target_article_id not in allowed_article_ids:
            raise OntologyAlignmentError(
                "Target article is outside locked ontology scope."
            )

        if not isinstance(
            reasoning_id,
            str,
        ) or not reasoning_id:
            raise OntologyAlignmentError(
                "Reasoning ID is required."
            )

        if not isinstance(
            family,
            str,
        ) or not family:
            raise OntologyAlignmentError(
                "Relationship family is required."
            )

        surfaces = walk_evidence(
            evidence
        )

        # Include relationship-family vocabulary because it is
        # certified semantic structure, not invented vocabulary.
        surfaces.append(
            (
                "relationship.relationship_family",
                family,
            )
        )

        for evidence_path, surface_form in surfaces:

            concept_type = classify_surface(
                evidence_path,
                surface_form,
            )

            occurrence_material = {
                "workspace_id":
                    workspace_id,

                "ontology_scope_id":
                    ontology_scope[
                        "ontology_scope_id"
                    ],

                "reasoning_id":
                    reasoning_id,

                "source_relationship_id":
                    source_relationship_id,

                "source_article_id":
                    source_article_id,

                "target_article_id":
                    target_article_id,

                "relationship_family":
                    family,

                "reasoning_status":
                    status,

                "evidence_path":
                    evidence_path,

                "surface_form":
                    surface_form,

                "concept_type":
                    concept_type,
            }

            occurrence_json = json.dumps(
                occurrence_material,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
            )

            occurrence_digest = hashlib.sha256(
                occurrence_json.encode(
                    "utf-8"
                )
            ).hexdigest()

            occurrence_id = (
                "ontvococc:v1:"
                + occurrence_digest[:32]
            )

            if occurrence_id in seen_occurrence_ids:
                continue

            seen_occurrence_ids.add(
                occurrence_id
            )

            occurrences.append(
                {
                    "vocabulary_occurrence_schema":
                        "ontology_vocabulary_occurrence_v1",

                    "vocabulary_occurrence_version":
                        "v1",

                    "vocabulary_occurrence_id":
                        occurrence_id,

                    "vocabulary_occurrence_digest":
                        occurrence_digest,

                    "surface_form":
                        surface_form,

                    "concept_type":
                        concept_type,

                    "evidence_path":
                        evidence_path,

                    "reasoning_id":
                        reasoning_id,

                    "source_relationship_id":
                        source_relationship_id,

                    "source_article_id":
                        source_article_id,

                    "target_article_id":
                        target_article_id,

                    "relationship_family":
                        family,

                    "reasoning_status":
                        status,

                    "evidence_bound":
                        True,

                    "document_lineage_preserved":
                        True,

                    "reasoning_lineage_preserved":
                        True,

                    "canonicalized":
                        False,

                    "ontology_mapped":
                        False,
                }
            )

    occurrences = sorted(
        occurrences,
        key=lambda item: (
            item[
                "surface_form"
            ].casefold(),
            item[
                "concept_type"
            ],
            item[
                "reasoning_id"
            ],
            item[
                "evidence_path"
            ],
        ),
    )

    if not occurrences:
        raise OntologyAlignmentError(
            "No evidence-bound vocabulary could be extracted."
        )

    # -------------------------------------------------------------
    # Build unique surface vocabulary
    # -------------------------------------------------------------

    grouped = {}

    for occurrence in occurrences:

        key = (
            occurrence[
                "surface_form"
            ].casefold(),
            occurrence[
                "concept_type"
            ],
        )

        grouped.setdefault(
            key,
            [],
        ).append(
            occurrence
        )

    vocabulary_items = []

    for key in sorted(
        grouped.keys()
    ):

        item_occurrences = grouped[
            key
        ]

        first = item_occurrences[
            0
        ]

        item_material = {
            "ontology_scope_id":
                ontology_scope[
                    "ontology_scope_id"
                ],

            "surface_form":
                first[
                    "surface_form"
                ],

            "surface_form_casefold":
                first[
                    "surface_form"
                ].casefold(),

            "concept_type":
                first[
                    "concept_type"
                ],

            "occurrence_ids": sorted(
                item[
                    "vocabulary_occurrence_id"
                ]
                for item in item_occurrences
            ),
        }

        item_json = json.dumps(
            item_material,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )

        item_digest = hashlib.sha256(
            item_json.encode(
                "utf-8"
            )
        ).hexdigest()

        vocabulary_item_id = (
            "ontvoc:v1:"
            + item_digest[:32]
        )

        vocabulary_items.append(
            {
                "vocabulary_item_schema":
                    "ontology_vocabulary_item_v1",

                "vocabulary_item_version":
                    "v1",

                "vocabulary_item_id":
                    vocabulary_item_id,

                "vocabulary_item_digest":
                    item_digest,

                "surface_form":
                    first[
                        "surface_form"
                    ],

                "surface_form_casefold":
                    first[
                        "surface_form"
                    ].casefold(),

                "concept_type":
                    first[
                        "concept_type"
                    ],

                "occurrence_count":
                    len(
                        item_occurrences
                    ),

                "occurrence_ids":
                    sorted(
                        item[
                            "vocabulary_occurrence_id"
                        ]
                        for item in item_occurrences
                    ),

                "reasoning_ids":
                    sorted(
                        set(
                            item[
                                "reasoning_id"
                            ]
                            for item in item_occurrences
                        )
                    ),

                "source_article_ids":
                    sorted(
                        set(
                            item[
                                "source_article_id"
                            ]
                            for item in item_occurrences
                        )
                    ),

                "target_article_ids":
                    sorted(
                        set(
                            item[
                                "target_article_id"
                            ]
                            for item in item_occurrences
                        )
                    ),

                "relationship_families":
                    sorted(
                        set(
                            item[
                                "relationship_family"
                            ]
                            for item in item_occurrences
                        )
                    ),

                "evidence_bound":
                    True,

                "canonicalized":
                    False,

                "ontology_mapped":
                    False,

                "ambiguous":
                    False,

                "conflicted":
                    False,
            }
        )

    # -------------------------------------------------------------
    # Deterministic vocabulary package identity
    # -------------------------------------------------------------

    package_material = {
        "workspace_id":
            workspace_id,

        "ontology_scope_id":
            ontology_scope[
                "ontology_scope_id"
            ],

        "document_set_id":
            ontology_scope[
                "document_set_id"
            ],

        "reasoning_scope_id":
            ontology_scope[
                "reasoning_scope_id"
            ],

        "vocabulary_item_ids": [
            item[
                "vocabulary_item_id"
            ]
            for item in vocabulary_items
        ],

        "occurrence_ids": [
            item[
                "vocabulary_occurrence_id"
            ]
            for item in occurrences
        ],
    }

    package_json = json.dumps(
        package_material,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    package_digest = hashlib.sha256(
        package_json.encode(
            "utf-8"
        )
    ).hexdigest()

    package_id = (
        "ontvocab:v1:"
        + package_digest[:32]
    )

    vocabulary_package = {
        "vocabulary_package_schema":
            "ontology_vocabulary_extraction_v1",

        "vocabulary_package_version":
            "v1",

        "vocabulary_package_id":
            package_id,

        "vocabulary_package_digest":
            package_digest,

        "vocabulary_package_digest_algorithm":
            "SHA256",

        "workspace_id":
            workspace_id,

        "ontology_scope_id":
            ontology_scope[
                "ontology_scope_id"
            ],

        "document_set_id":
            ontology_scope[
                "document_set_id"
            ],

        "reasoning_scope_id":
            ontology_scope[
                "reasoning_scope_id"
            ],

        "reasoning_provenance_id":
            ontology_scope[
                "reasoning_provenance_id"
            ],

        "vocabulary_item_count":
            len(
                vocabulary_items
            ),

        "occurrence_count":
            len(
                occurrences
            ),

        "vocabulary_items":
            vocabulary_items,

        "occurrences":
            occurrences,

        "extraction_source":
            "CERTIFIED_CROSS_DOCUMENT_REASONING_ONLY",

        "evidence_bound":
            True,

        "document_lineage_preserved":
            True,

        "reasoning_lineage_preserved":
            True,

        "source_reasoning_preserved":
            True,

        "source_profiles_preserved":
            True,

        "retrieval_payloads_preserved":
            True,

        "canonicalization_performed":
            False,

        "ontology_mapping_performed":
            False,

        "ontology_alignment_performed":
            False,

        "semantic_memory_written":
            False,

        "linking_decisions_performed":
            False,
    }

    # -------------------------------------------------------------
    # D boundary authority
    # -------------------------------------------------------------

    for field in (
        "certified_cross_document_reasoning_input_inspected",
        "certified_cross_document_reasoning_input_preserved",
        "ontology_alignment_architecture_defined",
        "ontology_alignment_intake_validated",
        "ontology_scope_defined",
        "reasoning_integrity_preserved",
        "reasoning_provenance_preserved",
        "reasoning_outcomes_preserved",
        "uncertainty_preserved",
        "conflicts_preserved",
    ):

        if boundaries.get(field) is not True:
            raise OntologyAlignmentError(
                f"Required 4.6.22D boundary is not True: {field}"
            )

    for field in (
        "concept_vocabulary_extracted",
        "canonical_concept_normalization_performed",
        "ontology_mapping_performed",
        "ontology_alignment_performed",
        "ontology_integrity_verification_performed",
        "ontology_provenance_built",
        "final_ontology_alignment_result_built",
        "full_ontology_alignment_certification_performed",
        "source_reasoning_modified",
        "source_profile_modified",
        "retrieval_payload_modified",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if boundaries.get(field) is not False:
            raise OntologyAlignmentError(
                f"Forbidden 4.6.22D boundary is not False: {field}"
            )

    return {
        "schema_version":
            "concept_entity_vocabulary_extraction_result_v1",

        "version":
            ONTOLOGY_ALIGNMENT_VERSION,

        "phase":
            ONTOLOGY_ALIGNMENT_PHASE,

        "patch":
            "4.6.22E",

        "status":
            "CONCEPT_ENTITY_VOCABULARY_EXTRACTED",

        "workspace_id":
            workspace_id,

        "ontology_alignment_architecture":
            deepcopy(
                dict(architecture)
            ),

        "ontology_vocabulary_scope":
            deepcopy(
                dict(ontology_scope)
            ),

        "ontology_vocabulary_extraction":
            vocabulary_package,

        "certified_final_cross_document_reasoning_result":
            deepcopy(
                dict(certified_final)
            ),

        "source_scope_contract_result":
            deepcopy(
                dict(scope_result)
            ),

        "processing_boundaries": {
            "certified_cross_document_reasoning_input_inspected":
                True,

            "certified_cross_document_reasoning_input_preserved":
                True,

            "ontology_alignment_architecture_defined":
                True,

            "ontology_alignment_intake_validated":
                True,

            "ontology_scope_defined":
                True,

            "concept_vocabulary_extracted":
                True,

            "reasoning_integrity_preserved":
                True,

            "reasoning_provenance_preserved":
                True,

            "reasoning_outcomes_preserved":
                True,

            "uncertainty_preserved":
                True,

            "conflicts_preserved":
                True,

            "canonical_concept_normalization_performed":
                False,

            "ontology_mapping_performed":
                False,

            "ontology_alignment_performed":
                False,

            "ontology_integrity_verification_performed":
                False,

            "ontology_provenance_built":
                False,

            "final_ontology_alignment_result_built":
                False,

            "full_ontology_alignment_certification_performed":
                False,

            "source_reasoning_modified":
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

        "alignment_policy":
            "EVIDENCE_BOUND_VOCABULARY_EXTRACTION_ONLY",

        "next_stage":
            "canonical_concept_normalization",
    }


# =====================================================================
# PATCH 4.6.22F ? Canonical Concept Normalization
# =====================================================================

def normalize_canonical_concepts_v1(
    extraction_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Perform deterministic surface-form normalization over the
    evidence-bound 4.6.22E vocabulary.

    F may normalize:
    - Unicode representation,
    - whitespace,
    - surrounding punctuation,
    - case for comparison,
    - deterministic morphological presentation.

    F does NOT:
    - infer synonyms,
    - infer aliases,
    - expand abbreviations semantically,
    - merge ambiguous meanings,
    - resolve conflicts,
    - perform ontology mapping,
    - write Semantic Memory,
    - make linking decisions.
    """

    from collections.abc import Mapping
    from copy import deepcopy
    import hashlib
    import json
    import re
    import unicodedata

    if not isinstance(
        extraction_result,
        Mapping,
    ):
        raise OntologyAlignmentError(
            "extraction_result must be a mapping."
        )

    # -------------------------------------------------------------
    # Exact 4.6.22E lifecycle
    # -------------------------------------------------------------

    for field, expected in (
        (
            "schema_version",
            "concept_entity_vocabulary_extraction_result_v1",
        ),
        (
            "version",
            ONTOLOGY_ALIGNMENT_VERSION,
        ),
        (
            "phase",
            ONTOLOGY_ALIGNMENT_PHASE,
        ),
        (
            "patch",
            "4.6.22E",
        ),
        (
            "status",
            "CONCEPT_ENTITY_VOCABULARY_EXTRACTED",
        ),
        (
            "alignment_policy",
            "EVIDENCE_BOUND_VOCABULARY_EXTRACTION_ONLY",
        ),
        (
            "next_stage",
            "canonical_concept_normalization",
        ),
    ):

        if extraction_result.get(field) != expected:
            raise OntologyAlignmentError(
                f"Invalid 4.6.22E lifecycle field: {field}"
            )

    workspace_id = extraction_result.get(
        "workspace_id"
    )

    architecture = extraction_result.get(
        "ontology_alignment_architecture"
    )

    ontology_scope = extraction_result.get(
        "ontology_vocabulary_scope"
    )

    extraction = extraction_result.get(
        "ontology_vocabulary_extraction"
    )

    certified_final = extraction_result.get(
        "certified_final_cross_document_reasoning_result"
    )

    boundaries = extraction_result.get(
        "processing_boundaries"
    )

    for name, value in (
        (
            "ontology_alignment_architecture",
            architecture,
        ),
        (
            "ontology_vocabulary_scope",
            ontology_scope,
        ),
        (
            "ontology_vocabulary_extraction",
            extraction,
        ),
        (
            "certified_final_cross_document_reasoning_result",
            certified_final,
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
            raise OntologyAlignmentError(
                name + " is missing."
            )

    # -------------------------------------------------------------
    # Architecture normalization authority
    # -------------------------------------------------------------

    execution_contract = architecture.get(
        "execution_contract"
    )

    normalization_contract = architecture.get(
        "normalization_contract"
    )

    if not isinstance(
        execution_contract,
        Mapping,
    ):
        raise OntologyAlignmentError(
            "Execution contract is missing."
        )

    if not isinstance(
        normalization_contract,
        Mapping,
    ):
        raise OntologyAlignmentError(
            "Normalization contract is missing."
        )

    if execution_contract.get(
        "4.6.22F"
    ) != "CANONICAL_CONCEPT_NORMALIZATION":
        raise OntologyAlignmentError(
            "4.6.22F execution contract drifted."
        )

    for field in (
        "case_normalization_allowed",
        "whitespace_normalization_allowed",
        "punctuation_normalization_allowed",
        "unicode_normalization_allowed",
        "deterministic_surface_normalization_required",
        "semantic_equivalence_requires_evidence",
        "abbreviation_expansion_requires_evidence",
        "alias_resolution_requires_evidence",
        "canonical_merge_requires_evidence",
        "ambiguous_merge_forbidden",
        "conflicting_merge_forbidden",
    ):

        if normalization_contract.get(field) is not True:
            raise OntologyAlignmentError(
                f"Required normalization contract field is not True: {field}"
            )

    # -------------------------------------------------------------
    # E package authority
    # -------------------------------------------------------------

    if extraction.get(
        "vocabulary_package_schema"
    ) != "ontology_vocabulary_extraction_v1":
        raise OntologyAlignmentError(
            "Vocabulary extraction schema drifted."
        )

    if extraction.get(
        "vocabulary_package_version"
    ) != "v1":
        raise OntologyAlignmentError(
            "Vocabulary extraction version drifted."
        )

    if extraction.get(
        "ontology_scope_id"
    ) != ontology_scope.get(
        "ontology_scope_id"
    ):
        raise OntologyAlignmentError(
            "Vocabulary package scope identity drifted."
        )

    for field in (
        "evidence_bound",
        "document_lineage_preserved",
        "reasoning_lineage_preserved",
        "source_reasoning_preserved",
        "source_profiles_preserved",
        "retrieval_payloads_preserved",
    ):

        if extraction.get(field) is not True:
            raise OntologyAlignmentError(
                f"Required extraction field is not True: {field}"
            )

    for field in (
        "canonicalization_performed",
        "ontology_mapping_performed",
        "ontology_alignment_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if extraction.get(field) is not False:
            raise OntologyAlignmentError(
                f"Forbidden extraction field is not False: {field}"
            )

    vocabulary_items = extraction.get(
        "vocabulary_items"
    )

    occurrences = extraction.get(
        "occurrences"
    )

    if not isinstance(
        vocabulary_items,
        list,
    ) or not vocabulary_items:
        raise OntologyAlignmentError(
            "Vocabulary items are required."
        )

    if not isinstance(
        occurrences,
        list,
    ) or not occurrences:
        raise OntologyAlignmentError(
            "Vocabulary occurrences are required."
        )

    if len(
        vocabulary_items
    ) != extraction.get(
        "vocabulary_item_count"
    ):
        raise OntologyAlignmentError(
            "Vocabulary item count drifted."
        )

    if len(
        occurrences
    ) != extraction.get(
        "occurrence_count"
    ):
        raise OntologyAlignmentError(
            "Vocabulary occurrence count drifted."
        )

    # -------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------

    def canonical_surface(
        value,
    ):

        if not isinstance(
            value,
            str,
        ):
            raise OntologyAlignmentError(
                "Vocabulary surface form must be a string."
            )

        text = unicodedata.normalize(
            "NFKC",
            value,
        )

        text = text.strip()

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        # Strip only surrounding punctuation.
        # Internal punctuation is preserved because it can carry meaning.
        text = text.strip(
            " \t\r\n.,;:!?\"'`~()[]{}<>"
        )

        if not text:
            raise OntologyAlignmentError(
                "Normalized surface form became empty."
            )

        return text

    def comparison_key(
        value,
    ):

        return canonical_surface(
            value
        ).casefold()

    # -------------------------------------------------------------
    # Validate source vocabulary IDs
    # -------------------------------------------------------------

    seen_item_ids = set()

    for item in vocabulary_items:

        if not isinstance(
            item,
            Mapping,
        ):
            raise OntologyAlignmentError(
                "Vocabulary item is invalid."
            )

        item_id = item.get(
            "vocabulary_item_id"
        )

        if not isinstance(
            item_id,
            str,
        ) or not item_id.startswith(
            "ontvoc:v1:"
        ):
            raise OntologyAlignmentError(
                "Vocabulary item ID is invalid."
            )

        if item_id in seen_item_ids:
            raise OntologyAlignmentError(
                "Duplicate vocabulary item ID detected."
            )

        seen_item_ids.add(
            item_id
        )

        if item.get(
            "evidence_bound"
        ) is not True:
            raise OntologyAlignmentError(
                "Vocabulary item is not evidence-bound."
            )

        if item.get(
            "canonicalized"
        ) is not False:
            raise OntologyAlignmentError(
                "Vocabulary item was canonicalized before F."
            )

        if item.get(
            "ontology_mapped"
        ) is not False:
            raise OntologyAlignmentError(
                "Vocabulary item was ontology-mapped before F."
            )

    # -------------------------------------------------------------
    # Exact normalized grouping only
    # -------------------------------------------------------------

    grouped = {}

    for item in vocabulary_items:

        normalized_surface = canonical_surface(
            item.get(
                "surface_form"
            )
        )

        normalized_key = comparison_key(
            normalized_surface
        )

        concept_type = item.get(
            "concept_type"
        )

        if not isinstance(
            concept_type,
            str,
        ) or not concept_type:
            raise OntologyAlignmentError(
                "Vocabulary concept type is required."
            )

        grouping_key = (
            normalized_key,
            concept_type,
        )

        grouped.setdefault(
            grouping_key,
            [],
        ).append(
            item
        )

    canonical_concepts = []

    source_item_to_canonical = {}

    for grouping_key in sorted(
        grouped.keys()
    ):

        members = grouped[
            grouping_key
        ]

        # Deterministically choose the presentation label.
        presentation_candidates = sorted(
            {
                canonical_surface(
                    member[
                        "surface_form"
                    ]
                )
                for member in members
            },
            key=lambda value: (
                value.casefold(),
                value,
            ),
        )

        canonical_label = presentation_candidates[
            0
        ]

        concept_type = grouping_key[
            1
        ]

        source_item_ids = sorted(
            member[
                "vocabulary_item_id"
            ]
            for member in members
        )

        canonical_material = {
            "workspace_id":
                workspace_id,

            "ontology_scope_id":
                ontology_scope[
                    "ontology_scope_id"
                ],

            "normalized_key":
                grouping_key[
                    0
                ],

            "canonical_label":
                canonical_label,

            "canonical_type":
                concept_type,

            "source_vocabulary_item_ids":
                source_item_ids,
        }

        canonical_json = json.dumps(
            canonical_material,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )

        canonical_digest = hashlib.sha256(
            canonical_json.encode(
                "utf-8"
            )
        ).hexdigest()

        canonical_id = (
            "ontconcept:v1:"
            + canonical_digest[:32]
        )

        for source_item_id in source_item_ids:

            source_item_to_canonical[
                source_item_id
            ] = canonical_id

        canonical_concepts.append(
            {
                "canonical_concept_schema":
                    "canonical_ontology_concept_v1",

                "canonical_concept_version":
                    "v1",

                "canonical_concept_id":
                    canonical_id,

                "canonical_concept_digest":
                    canonical_digest,

                "canonical_label":
                    canonical_label,

                "canonical_label_casefold":
                    canonical_label.casefold(),

                "canonical_type":
                    concept_type,

                "normalization_family":
                    "EXACT_NORMALIZED_SURFACE",

                "source_vocabulary_item_ids":
                    source_item_ids,

                "source_surface_forms":
                    sorted(
                        {
                            member[
                                "surface_form"
                            ]
                            for member in members
                        },
                        key=lambda value: (
                            value.casefold(),
                            value,
                        ),
                    ),

                "source_item_count":
                    len(
                        source_item_ids
                    ),

                "exact_surface_normalization":
                    True,

                "semantic_equivalence_inferred":
                    False,

                "synonym_equivalence_inferred":
                    False,

                "alias_equivalence_inferred":
                    False,

                "abbreviation_equivalence_inferred":
                    False,

                "ambiguous_merge_performed":
                    False,

                "conflicting_merge_performed":
                    False,

                "ontology_mapped":
                    False,

                "evidence_bound":
                    True,
            }
        )

    canonical_concepts = sorted(
        canonical_concepts,
        key=lambda item: (
            item[
                "canonical_label_casefold"
            ],
            item[
                "canonical_type"
            ],
            item[
                "canonical_concept_id"
            ],
        ),
    )

    # -------------------------------------------------------------
    # Source-to-canonical normalization mappings
    # -------------------------------------------------------------

    normalization_mappings = []

    for item in sorted(
        vocabulary_items,
        key=lambda value: (
            value[
                "surface_form"
            ].casefold(),
            value[
                "concept_type"
            ],
            value[
                "vocabulary_item_id"
            ],
        ),
    ):

        source_item_id = item[
            "vocabulary_item_id"
        ]

        canonical_id = source_item_to_canonical.get(
            source_item_id
        )

        if canonical_id is None:
            raise OntologyAlignmentError(
                "Source vocabulary item lacks canonical normalization binding."
            )

        canonical = next(
            concept
            for concept in canonical_concepts
            if concept[
                "canonical_concept_id"
            ] == canonical_id
        )

        mapping_material = {
            "ontology_scope_id":
                ontology_scope[
                    "ontology_scope_id"
                ],

            "source_vocabulary_item_id":
                source_item_id,

            "canonical_concept_id":
                canonical_id,

            "source_surface_form":
                item[
                    "surface_form"
                ],

            "normalized_surface_form":
                canonical_surface(
                    item[
                        "surface_form"
                    ]
                ),

            "canonical_type":
                item[
                    "concept_type"
                ],
        }

        mapping_json = json.dumps(
            mapping_material,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )

        mapping_digest = hashlib.sha256(
            mapping_json.encode(
                "utf-8"
            )
        ).hexdigest()

        normalization_mappings.append(
            {
                "normalization_mapping_schema":
                    "canonical_normalization_mapping_v1",

                "normalization_mapping_version":
                    "v1",

                "normalization_mapping_id":
                    "ontnormmap:v1:"
                    + mapping_digest[:32],

                "normalization_mapping_digest":
                    mapping_digest,

                "source_vocabulary_item_id":
                    source_item_id,

                "source_surface_form":
                    item[
                        "surface_form"
                    ],

                "normalized_surface_form":
                    canonical_surface(
                        item[
                            "surface_form"
                        ]
                    ),

                "normalized_comparison_key":
                    comparison_key(
                        item[
                            "surface_form"
                        ]
                    ),

                "source_concept_type":
                    item[
                        "concept_type"
                    ],

                "canonical_concept_id":
                    canonical_id,

                "canonical_label":
                    canonical[
                        "canonical_label"
                    ],

                "canonical_type":
                    canonical[
                        "canonical_type"
                    ],

                "mapping_family":
                    "EXACT_NORMALIZED_SURFACE",

                "semantic_equivalence_claimed":
                    False,

                "ontology_mapping_performed":
                    False,

                "ambiguous":
                    False,

                "conflicted":
                    False,

                "evidence_bound":
                    True,
            }
        )

    # -------------------------------------------------------------
    # Package identity
    # -------------------------------------------------------------

    package_material = {
        "workspace_id":
            workspace_id,

        "ontology_scope_id":
            ontology_scope[
                "ontology_scope_id"
            ],

        "source_vocabulary_package_id":
            extraction[
                "vocabulary_package_id"
            ],

        "canonical_concept_ids": [
            item[
                "canonical_concept_id"
            ]
            for item in canonical_concepts
        ],

        "normalization_mapping_ids": [
            item[
                "normalization_mapping_id"
            ]
            for item in normalization_mappings
        ],
    }

    package_json = json.dumps(
        package_material,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    package_digest = hashlib.sha256(
        package_json.encode(
            "utf-8"
        )
    ).hexdigest()

    package_id = (
        "ontnorm:v1:"
        + package_digest[:32]
    )

    normalization_package = {
        "normalization_package_schema":
            "canonical_concept_normalization_v1",

        "normalization_package_version":
            "v1",

        "normalization_package_id":
            package_id,

        "normalization_package_digest":
            package_digest,

        "normalization_package_digest_algorithm":
            "SHA256",

        "workspace_id":
            workspace_id,

        "ontology_scope_id":
            ontology_scope[
                "ontology_scope_id"
            ],

        "source_vocabulary_package_id":
            extraction[
                "vocabulary_package_id"
            ],

        "source_vocabulary_item_count":
            len(
                vocabulary_items
            ),

        "canonical_concept_count":
            len(
                canonical_concepts
            ),

        "normalization_mapping_count":
            len(
                normalization_mappings
            ),

        "canonical_concepts":
            canonical_concepts,

        "normalization_mappings":
            normalization_mappings,

        "exact_surface_normalization_performed":
            True,

        "semantic_equivalence_inference_performed":
            False,

        "synonym_resolution_performed":
            False,

        "alias_resolution_performed":
            False,

        "abbreviation_expansion_performed":
            False,

        "ambiguous_merge_performed":
            False,

        "conflicting_merge_performed":
            False,

        "ontology_mapping_performed":
            False,

        "ontology_alignment_performed":
            False,

        "source_vocabulary_preserved":
            True,

        "source_reasoning_preserved":
            True,

        "source_profiles_preserved":
            True,

        "retrieval_payloads_preserved":
            True,

        "semantic_memory_written":
            False,

        "linking_decisions_performed":
            False,
    }

    # -------------------------------------------------------------
    # E boundary authority
    # -------------------------------------------------------------

    for field in (
        "certified_cross_document_reasoning_input_inspected",
        "certified_cross_document_reasoning_input_preserved",
        "ontology_alignment_architecture_defined",
        "ontology_alignment_intake_validated",
        "ontology_scope_defined",
        "concept_vocabulary_extracted",
        "reasoning_integrity_preserved",
        "reasoning_provenance_preserved",
        "reasoning_outcomes_preserved",
        "uncertainty_preserved",
        "conflicts_preserved",
    ):

        if boundaries.get(field) is not True:
            raise OntologyAlignmentError(
                f"Required 4.6.22E boundary is not True: {field}"
            )

    for field in (
        "canonical_concept_normalization_performed",
        "ontology_mapping_performed",
        "ontology_alignment_performed",
        "ontology_integrity_verification_performed",
        "ontology_provenance_built",
        "final_ontology_alignment_result_built",
        "full_ontology_alignment_certification_performed",
        "source_reasoning_modified",
        "source_profile_modified",
        "retrieval_payload_modified",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if boundaries.get(field) is not False:
            raise OntologyAlignmentError(
                f"Forbidden 4.6.22E boundary is not False: {field}"
            )

    return {
        "schema_version":
            "canonical_concept_normalization_result_v1",

        "version":
            ONTOLOGY_ALIGNMENT_VERSION,

        "phase":
            ONTOLOGY_ALIGNMENT_PHASE,

        "patch":
            "4.6.22F",

        "status":
            "CANONICAL_CONCEPT_NORMALIZATION_COMPLETED",

        "workspace_id":
            workspace_id,

        "ontology_alignment_architecture":
            deepcopy(
                dict(architecture)
            ),

        "ontology_vocabulary_scope":
            deepcopy(
                dict(ontology_scope)
            ),

        "ontology_vocabulary_extraction":
            deepcopy(
                dict(extraction)
            ),

        "canonical_concept_normalization":
            normalization_package,

        "certified_final_cross_document_reasoning_result":
            deepcopy(
                dict(certified_final)
            ),

        "source_vocabulary_extraction_result":
            deepcopy(
                dict(extraction_result)
            ),

        "processing_boundaries": {
            "certified_cross_document_reasoning_input_inspected":
                True,

            "certified_cross_document_reasoning_input_preserved":
                True,

            "ontology_alignment_architecture_defined":
                True,

            "ontology_alignment_intake_validated":
                True,

            "ontology_scope_defined":
                True,

            "concept_vocabulary_extracted":
                True,

            "canonical_concept_normalization_performed":
                True,

            "reasoning_integrity_preserved":
                True,

            "reasoning_provenance_preserved":
                True,

            "reasoning_outcomes_preserved":
                True,

            "uncertainty_preserved":
                True,

            "conflicts_preserved":
                True,

            "ontology_mapping_performed":
                False,

            "ontology_alignment_performed":
                False,

            "ontology_integrity_verification_performed":
                False,

            "ontology_provenance_built":
                False,

            "final_ontology_alignment_result_built":
                False,

            "full_ontology_alignment_certification_performed":
                False,

            "source_reasoning_modified":
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

        "alignment_policy":
            "DETERMINISTIC_SURFACE_NORMALIZATION_ONLY",

        "next_stage":
            "ontology_mapping_and_alignment_execution",
    }


# =====================================================================
# PATCH 4.6.22G ? Ontology Mapping & Alignment Execution
# =====================================================================

def execute_ontology_mapping_alignment_v1(
    normalization_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Execute evidence-bound ontology mapping over normalized concepts.

    G may establish:
    - exact canonical matches,
    - evidence-backed synonym equivalence,
    - alias equivalence,
    - abbreviation equivalence,
    - entity equivalence,
    - topic equivalence,
    - general/specific or parent/child relations,
    - unresolved/ambiguous/conflicting mappings.

    G does NOT silently resolve ambiguity or conflict.
    It does NOT write Semantic Memory or make linking decisions.
    """

    from collections.abc import Mapping
    from copy import deepcopy
    import hashlib
    import json

    if not isinstance(
        normalization_result,
        Mapping,
    ):
        raise OntologyAlignmentError(
            "normalization_result must be a mapping."
        )

    # -------------------------------------------------------------
    # Exact 4.6.22F lifecycle
    # -------------------------------------------------------------

    for field, expected in (
        (
            "schema_version",
            "canonical_concept_normalization_result_v1",
        ),
        (
            "version",
            ONTOLOGY_ALIGNMENT_VERSION,
        ),
        (
            "phase",
            ONTOLOGY_ALIGNMENT_PHASE,
        ),
        (
            "patch",
            "4.6.22F",
        ),
        (
            "status",
            "CANONICAL_CONCEPT_NORMALIZATION_COMPLETED",
        ),
        (
            "alignment_policy",
            "DETERMINISTIC_SURFACE_NORMALIZATION_ONLY",
        ),
        (
            "next_stage",
            "ontology_mapping_and_alignment_execution",
        ),
    ):

        if normalization_result.get(field) != expected:
            raise OntologyAlignmentError(
                f"Invalid 4.6.22F lifecycle field: {field}"
            )

    workspace_id = normalization_result.get(
        "workspace_id"
    )

    architecture = normalization_result.get(
        "ontology_alignment_architecture"
    )

    ontology_scope = normalization_result.get(
        "ontology_vocabulary_scope"
    )

    extraction = normalization_result.get(
        "ontology_vocabulary_extraction"
    )

    normalization = normalization_result.get(
        "canonical_concept_normalization"
    )

    certified_final = normalization_result.get(
        "certified_final_cross_document_reasoning_result"
    )

    boundaries = normalization_result.get(
        "processing_boundaries"
    )

    for name, value in (
        (
            "ontology_alignment_architecture",
            architecture,
        ),
        (
            "ontology_vocabulary_scope",
            ontology_scope,
        ),
        (
            "ontology_vocabulary_extraction",
            extraction,
        ),
        (
            "canonical_concept_normalization",
            normalization,
        ),
        (
            "certified_final_cross_document_reasoning_result",
            certified_final,
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
            raise OntologyAlignmentError(
                name + " is missing."
            )

    # -------------------------------------------------------------
    # Architecture authority
    # -------------------------------------------------------------

    execution_contract = architecture.get(
        "execution_contract"
    )

    mapping_contract = architecture.get(
        "mapping_contract"
    )

    supported_families = architecture.get(
        "supported_alignment_families"
    )

    if not isinstance(
        execution_contract,
        Mapping,
    ):
        raise OntologyAlignmentError(
            "Execution contract is missing."
        )

    if execution_contract.get(
        "4.6.22G"
    ) != "ONTOLOGY_MAPPING_AND_ALIGNMENT_EXECUTION":
        raise OntologyAlignmentError(
            "4.6.22G execution contract drifted."
        )

    if not isinstance(
        mapping_contract,
        Mapping,
    ):
        raise OntologyAlignmentError(
            "Mapping contract is missing."
        )

    for field in (
        "map_only_declared_scope",
        "map_only_extracted_vocabulary",
        "canonical_mapping_requires_evidence",
        "relationship_mapping_requires_evidence",
        "hierarchy_mapping_requires_evidence",
        "confidence_required",
        "uncertainty_required",
        "ambiguous_mapping_allowed_as_unresolved",
        "conflicting_mapping_allowed_as_conflict",
        "unsupported_mapping_forbidden",
        "source_reasoning_mutation_forbidden",
        "semantic_memory_write_forbidden",
        "linking_decision_forbidden",
    ):

        if mapping_contract.get(field) is not True:
            raise OntologyAlignmentError(
                f"Required mapping contract field is not True: {field}"
            )

    if not isinstance(
        supported_families,
        list,
    ) or not supported_families:
        raise OntologyAlignmentError(
            "Supported alignment families are missing."
        )

    supported_families = set(
        supported_families
    )

    # -------------------------------------------------------------
    # F normalization authority
    # -------------------------------------------------------------

    if normalization.get(
        "normalization_package_schema"
    ) != "canonical_concept_normalization_v1":
        raise OntologyAlignmentError(
            "Normalization schema drifted."
        )

    if normalization.get(
        "normalization_package_version"
    ) != "v1":
        raise OntologyAlignmentError(
            "Normalization version drifted."
        )

    if normalization.get(
        "ontology_scope_id"
    ) != ontology_scope.get(
        "ontology_scope_id"
    ):
        raise OntologyAlignmentError(
            "Normalization scope identity drifted."
        )

    if normalization.get(
        "exact_surface_normalization_performed"
    ) is not True:
        raise OntologyAlignmentError(
            "Exact surface normalization was not completed."
        )

    for field in (
        "source_vocabulary_preserved",
        "source_reasoning_preserved",
        "source_profiles_preserved",
        "retrieval_payloads_preserved",
    ):

        if normalization.get(field) is not True:
            raise OntologyAlignmentError(
                f"Required normalization field is not True: {field}"
            )

    for field in (
        "semantic_equivalence_inference_performed",
        "synonym_resolution_performed",
        "alias_resolution_performed",
        "abbreviation_expansion_performed",
        "ambiguous_merge_performed",
        "conflicting_merge_performed",
        "ontology_mapping_performed",
        "ontology_alignment_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if normalization.get(field) is not False:
            raise OntologyAlignmentError(
                f"Forbidden normalization field is not False: {field}"
            )

    canonical_concepts = normalization.get(
        "canonical_concepts"
    )

    if not isinstance(
        canonical_concepts,
        list,
    ) or not canonical_concepts:
        raise OntologyAlignmentError(
            "Canonical concepts are required."
        )

    # -------------------------------------------------------------
    # Build indexes
    # -------------------------------------------------------------

    concept_by_id = {}

    concept_ids_by_label = {}

    for concept in canonical_concepts:

        if not isinstance(
            concept,
            Mapping,
        ):
            raise OntologyAlignmentError(
                "Canonical concept is invalid."
            )

        concept_id = concept.get(
            "canonical_concept_id"
        )

        label = concept.get(
            "canonical_label"
        )

        concept_type = concept.get(
            "canonical_type"
        )

        if not isinstance(
            concept_id,
            str,
        ) or not concept_id.startswith(
            "ontconcept:v1:"
        ):
            raise OntologyAlignmentError(
                "Canonical concept ID is invalid."
            )

        if concept_id in concept_by_id:
            raise OntologyAlignmentError(
                "Duplicate canonical concept ID detected."
            )

        if not isinstance(
            label,
            str,
        ) or not label:
            raise OntologyAlignmentError(
                "Canonical label is required."
            )

        if not isinstance(
            concept_type,
            str,
        ) or not concept_type:
            raise OntologyAlignmentError(
                "Canonical concept type is required."
            )

        concept_by_id[
            concept_id
        ] = concept

        concept_ids_by_label.setdefault(
            label.casefold(),
            [],
        ).append(
            concept_id
        )

    # -------------------------------------------------------------
    # Certified reasoning evidence
    # -------------------------------------------------------------

    relationships = certified_final.get(
        "relationships"
    )

    if not isinstance(
        relationships,
        list,
    ):
        raise OntologyAlignmentError(
            "Certified relationships must be a list."
        )

    # -------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------

    def flatten_strings(
        value,
    ):

        output = []

        if isinstance(
            value,
            Mapping,
        ):

            for key in sorted(
                value.keys(),
                key=str,
            ):

                output.extend(
                    flatten_strings(
                        value[
                            key
                        ]
                    )
                )

        elif isinstance(
            value,
            (list, tuple),
        ):

            for child in value:
                output.extend(
                    flatten_strings(
                        child
                    )
                )

        elif isinstance(
            value,
            str,
        ):

            cleaned = value.strip()

            if cleaned:
                output.append(
                    cleaned
                )

        return output

    def find_concept_ids(
        surface,
    ):

        if not isinstance(
            surface,
            str,
        ):
            return []

        return sorted(
            concept_ids_by_label.get(
                surface.strip().casefold(),
                [],
            )
        )

    def make_alignment(
        source_id,
        target_id,
        family,
        status,
        evidence,
        confidence,
        uncertainty,
        reasoning_id=None,
        source_relationship_id=None,
    ):

        if family not in supported_families:
            raise OntologyAlignmentError(
                f"Unsupported alignment family: {family}"
            )

        material = {
            "workspace_id":
                workspace_id,

            "ontology_scope_id":
                ontology_scope[
                    "ontology_scope_id"
                ],

            "source_concept_id":
                source_id,

            "target_concept_id":
                target_id,

            "alignment_family":
                family,

            "alignment_status":
                status,

            "confidence_state":
                confidence,

            "uncertainty_state":
                uncertainty,

            "reasoning_id":
                reasoning_id,

            "source_relationship_id":
                source_relationship_id,

            "evidence":
                evidence,
        }

        raw = json.dumps(
            material,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )

        digest = hashlib.sha256(
            raw.encode(
                "utf-8"
            )
        ).hexdigest()

        return {
            "ontology_alignment_schema":
                "ontology_concept_alignment_v1",

            "ontology_alignment_version":
                "v1",

            "ontology_alignment_id":
                "ontalign:v1:"
                + digest[:32],

            "ontology_alignment_digest":
                digest,

            "source_concept_id":
                source_id,

            "target_concept_id":
                target_id,

            "source_label":
                (
                    concept_by_id[source_id][
                        "canonical_label"
                    ]
                    if source_id in concept_by_id
                    else None
                ),

            "target_label":
                (
                    concept_by_id[target_id][
                        "canonical_label"
                    ]
                    if target_id in concept_by_id
                    else None
                ),

            "alignment_family":
                family,

            "alignment_status":
                status,

            "confidence_state":
                confidence,

            "uncertainty_state":
                uncertainty,

            "reasoning_id":
                reasoning_id,

            "source_relationship_id":
                source_relationship_id,

            "evidence":
                deepcopy(
                    evidence
                ),

            "evidence_bound":
                True,

            "ambiguity_preserved":
                status == "UNRESOLVED",

            "conflict_preserved":
                status == "CONFLICT_DETECTED",

            "silently_resolved":
                False,

            "source_reasoning_modified":
                False,

            "semantic_memory_written":
                False,

            "linking_decision":
                False,
        }

    # -------------------------------------------------------------
    # Exact canonical self-confirmations
    # -------------------------------------------------------------

    alignments = []

    seen_alignment_ids = set()

    for concept in canonical_concepts:

        alignment = make_alignment(
            concept[
                "canonical_concept_id"
            ],
            concept[
                "canonical_concept_id"
            ],
            "EXACT_CANONICAL_MATCH",
            "CONFIRMED",
            [
                {
                    "evidence_type":
                        "EXACT_NORMALIZED_CANONICAL_IDENTITY",

                    "canonical_label":
                        concept[
                            "canonical_label"
                        ],
                }
            ],
            "HIGH",
            "LOW",
        )

        if alignment[
            "ontology_alignment_id"
        ] not in seen_alignment_ids:

            seen_alignment_ids.add(
                alignment[
                    "ontology_alignment_id"
                ]
            )

            alignments.append(
                alignment
            )

    # -------------------------------------------------------------
    # Evidence-backed cross-concept mapping
    # -------------------------------------------------------------

    for relationship in relationships:

        if not isinstance(
            relationship,
            Mapping,
        ):
            raise OntologyAlignmentError(
                "Certified relationship entry is invalid."
            )

        reasoning_id = relationship.get(
            "reasoning_id"
        )

        source_relationship_id = relationship.get(
            "source_relationship_id"
        )

        relationship_family = relationship.get(
            "relationship_family"
        )

        reasoning_status = relationship.get(
            "reasoning_status"
        )

        evidence = relationship.get(
            "evidence",
            [],
        )

        evidence_strings = flatten_strings(
            evidence
        )

        matched_concept_ids = []

        for surface in evidence_strings:

            matched_concept_ids.extend(
                find_concept_ids(
                    surface
                )
            )

        matched_concept_ids = sorted(
            set(
                matched_concept_ids
            )
        )

        # We need at least two distinct normalized concepts for a
        # cross-concept semantic mapping.
        if len(
            matched_concept_ids
        ) < 2:
            continue

        pairs = []

        for i in range(
            len(
                matched_concept_ids
            )
        ):

            for j in range(
                i + 1,
                len(
                    matched_concept_ids
                )
            ):

                pairs.append(
                    (
                        matched_concept_ids[
                            i
                        ],
                        matched_concept_ids[
                            j
                        ],
                    )
                )

        for source_id, target_id in pairs:

            source_label = concept_by_id[
                source_id
            ][
                "canonical_label"
            ].casefold()

            target_label = concept_by_id[
                target_id
            ][
                "canonical_label"
            ].casefold()

            combined_evidence = " ".join(
                value.casefold()
                for value in evidence_strings
            )

            alignment_family = (
                "POTENTIAL_EQUIVALENCE"
            )

            alignment_status = (
                "UNRESOLVED"
            )

            confidence = "LOW"

            uncertainty = "HIGH"

            # Explicit alias evidence.
            if (
                "alias" in combined_evidence
                or "also known as" in combined_evidence
                or "aka" in combined_evidence
            ):

                alignment_family = (
                    "ALIAS_EQUIVALENCE"
                )

                alignment_status = (
                    "CONFIRMED"
                )

                confidence = "HIGH"

                uncertainty = "LOW"

            # Explicit synonym/equivalence evidence.
            elif (
                "synonym" in combined_evidence
                or "same as" in combined_evidence
                or "equivalent" in combined_evidence
            ):

                alignment_family = (
                    "SYNONYM_EQUIVALENCE"
                )

                alignment_status = (
                    "CONFIRMED"
                )

                confidence = "HIGH"

                uncertainty = "LOW"

            elif (
                relationship_family
                == "SHARED_TOPIC"
                and reasoning_status
                == "CONFIRMED"
            ):

                alignment_family = (
                    "TOPIC_EQUIVALENCE"
                )

                alignment_status = (
                    "CONFIRMED"
                )

                confidence = "MODERATE"

                uncertainty = "MODERATE"

            elif (
                relationship_family
                == "GENERAL_SPECIFIC"
            ):

                alignment_family = (
                    "GENERAL_SPECIFIC"
                )

                alignment_status = (
                    "CONFIRMED"
                    if reasoning_status
                    == "CONFIRMED"
                    else "UNRESOLVED"
                )

                confidence = (
                    "MODERATE"
                    if alignment_status
                    == "CONFIRMED"
                    else "LOW"
                )

                uncertainty = (
                    "MODERATE"
                    if alignment_status
                    == "CONFIRMED"
                    else "HIGH"
                )

            elif (
                relationship_family
                == "PARENT_CHILD"
            ):

                alignment_family = (
                    "PARENT_CHILD"
                )

                alignment_status = (
                    "CONFIRMED"
                    if reasoning_status
                    == "CONFIRMED"
                    else "UNRESOLVED"
                )

                confidence = (
                    "MODERATE"
                    if alignment_status
                    == "CONFIRMED"
                    else "LOW"
                )

                uncertainty = (
                    "MODERATE"
                    if alignment_status
                    == "CONFIRMED"
                    else "HIGH"
                )

            elif (
                relationship_family
                == "CONTRADICTION"
                or reasoning_status
                == "CONFLICT_DETECTED"
            ):

                alignment_family = (
                    "CONFLICTING_MAPPING"
                )

                alignment_status = (
                    "CONFLICT_DETECTED"
                )

                confidence = "MODERATE"

                uncertainty = "HIGH"

            alignment = make_alignment(
                source_id,
                target_id,
                alignment_family,
                alignment_status,
                [
                    {
                        "relationship_family":
                            relationship_family,

                        "reasoning_status":
                            reasoning_status,

                        "reasoning_id":
                            reasoning_id,

                        "evidence":
                            deepcopy(
                                evidence
                            ),
                    }
                ],
                confidence,
                uncertainty,
                reasoning_id,
                source_relationship_id,
            )

            if alignment[
                "ontology_alignment_id"
            ] not in seen_alignment_ids:

                seen_alignment_ids.add(
                    alignment[
                        "ontology_alignment_id"
                    ]
                )

                alignments.append(
                    alignment
                )

    alignments = sorted(
        alignments,
        key=lambda item: (
            item[
                "source_concept_id"
            ],
            item[
                "target_concept_id"
            ],
            item[
                "alignment_family"
            ],
            item[
                "ontology_alignment_id"
            ],
        ),
    )

    # -------------------------------------------------------------
    # Registries
    # -------------------------------------------------------------

    confirmed = [
        deepcopy(
            item
        )
        for item in alignments
        if item[
            "alignment_status"
        ] == "CONFIRMED"
    ]

    unresolved = [
        deepcopy(
            item
        )
        for item in alignments
        if item[
            "alignment_status"
        ] == "UNRESOLVED"
    ]

    conflicts = [
        deepcopy(
            item
        )
        for item in alignments
        if item[
            "alignment_status"
        ] == "CONFLICT_DETECTED"
    ]

    # -------------------------------------------------------------
    # Package identity
    # -------------------------------------------------------------

    package_material = {
        "workspace_id":
            workspace_id,

        "ontology_scope_id":
            ontology_scope[
                "ontology_scope_id"
            ],

        "normalization_package_id":
            normalization[
                "normalization_package_id"
            ],

        "alignment_ids": [
            item[
                "ontology_alignment_id"
            ]
            for item in alignments
        ],
    }

    package_json = json.dumps(
        package_material,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    package_digest = hashlib.sha256(
        package_json.encode(
            "utf-8"
        )
    ).hexdigest()

    package_id = (
        "ontmap:v1:"
        + package_digest[:32]
    )

    alignment_package = {
        "alignment_package_schema":
            "ontology_mapping_alignment_execution_v1",

        "alignment_package_version":
            "v1",

        "alignment_package_id":
            package_id,

        "alignment_package_digest":
            package_digest,

        "alignment_package_digest_algorithm":
            "SHA256",

        "workspace_id":
            workspace_id,

        "ontology_scope_id":
            ontology_scope[
                "ontology_scope_id"
            ],

        "normalization_package_id":
            normalization[
                "normalization_package_id"
            ],

        "alignment_count":
            len(
                alignments
            ),

        "confirmed_alignment_count":
            len(
                confirmed
            ),

        "unresolved_alignment_count":
            len(
                unresolved
            ),

        "conflict_alignment_count":
            len(
                conflicts
            ),

        "alignments":
            alignments,

        "confirmed_alignments":
            confirmed,

        "unresolved_alignments":
            unresolved,

        "conflicting_alignments":
            conflicts,

        "ontology_mapping_performed":
            True,

        "ontology_alignment_performed":
            True,

        "evidence_bound":
            True,

        "ambiguity_preserved":
            True,

        "conflicts_preserved":
            True,

        "uncertainty_preserved":
            True,

        "unsupported_mapping_invented":
            False,

        "silent_resolution_performed":
            False,

        "source_reasoning_preserved":
            True,

        "source_vocabulary_preserved":
            True,

        "source_normalization_preserved":
            True,

        "source_profiles_preserved":
            True,

        "retrieval_payloads_preserved":
            True,

        "semantic_memory_written":
            False,

        "linking_decisions_performed":
            False,
    }

    # -------------------------------------------------------------
    # F boundary authority
    # -------------------------------------------------------------

    for field in (
        "certified_cross_document_reasoning_input_inspected",
        "certified_cross_document_reasoning_input_preserved",
        "ontology_alignment_architecture_defined",
        "ontology_alignment_intake_validated",
        "ontology_scope_defined",
        "concept_vocabulary_extracted",
        "canonical_concept_normalization_performed",
        "reasoning_integrity_preserved",
        "reasoning_provenance_preserved",
        "reasoning_outcomes_preserved",
        "uncertainty_preserved",
        "conflicts_preserved",
    ):

        if boundaries.get(field) is not True:
            raise OntologyAlignmentError(
                f"Required 4.6.22F boundary is not True: {field}"
            )

    for field in (
        "ontology_mapping_performed",
        "ontology_alignment_performed",
        "ontology_integrity_verification_performed",
        "ontology_provenance_built",
        "final_ontology_alignment_result_built",
        "full_ontology_alignment_certification_performed",
        "source_reasoning_modified",
        "source_profile_modified",
        "retrieval_payload_modified",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if boundaries.get(field) is not False:
            raise OntologyAlignmentError(
                f"Forbidden 4.6.22F boundary is not False: {field}"
            )

    return {
        "schema_version":
            "ontology_mapping_alignment_execution_result_v1",

        "version":
            ONTOLOGY_ALIGNMENT_VERSION,

        "phase":
            ONTOLOGY_ALIGNMENT_PHASE,

        "patch":
            "4.6.22G",

        "status":
            "ONTOLOGY_MAPPING_AND_ALIGNMENT_EXECUTED",

        "workspace_id":
            workspace_id,

        "ontology_alignment_architecture":
            deepcopy(
                dict(architecture)
            ),

        "ontology_vocabulary_scope":
            deepcopy(
                dict(ontology_scope)
            ),

        "ontology_vocabulary_extraction":
            deepcopy(
                dict(extraction)
            ),

        "canonical_concept_normalization":
            deepcopy(
                dict(normalization)
            ),

        "ontology_mapping_alignment":
            alignment_package,

        "certified_final_cross_document_reasoning_result":
            deepcopy(
                dict(certified_final)
            ),

        "source_normalization_result":
            deepcopy(
                dict(normalization_result)
            ),

        "processing_boundaries": {
            "certified_cross_document_reasoning_input_inspected":
                True,

            "certified_cross_document_reasoning_input_preserved":
                True,

            "ontology_alignment_architecture_defined":
                True,

            "ontology_alignment_intake_validated":
                True,

            "ontology_scope_defined":
                True,

            "concept_vocabulary_extracted":
                True,

            "canonical_concept_normalization_performed":
                True,

            "ontology_mapping_performed":
                True,

            "ontology_alignment_performed":
                True,

            "reasoning_integrity_preserved":
                True,

            "reasoning_provenance_preserved":
                True,

            "reasoning_outcomes_preserved":
                True,

            "uncertainty_preserved":
                True,

            "conflicts_preserved":
                True,

            "ontology_integrity_verification_performed":
                False,

            "ontology_provenance_built":
                False,

            "final_ontology_alignment_result_built":
                False,

            "full_ontology_alignment_certification_performed":
                False,

            "source_reasoning_modified":
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

        "alignment_policy":
            "EVIDENCE_BOUND_ONTOLOGY_MAPPING_EXECUTED",

        "next_stage":
            "alignment_integrity_ambiguity_guard",
    }


# =====================================================================
# PATCH 4.6.22H ? Alignment Integrity & Ambiguity Guard
# =====================================================================

def guard_ontology_alignment_integrity_v1(
    alignment_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Verify integrity, ambiguity, conflict, identity, scope, and
    preservation properties of 4.6.22G Ontology Alignment.

    Guard only.

    H does not create mappings, resolve ambiguity, resolve conflicts,
    write Semantic Memory, or make linking decisions.
    """

    from collections.abc import Mapping
    from copy import deepcopy
    import hashlib
    import json

    if not isinstance(
        alignment_result,
        Mapping,
    ):
        raise OntologyAlignmentError(
            "alignment_result must be a mapping."
        )

    # -------------------------------------------------------------
    # Exact 4.6.22G lifecycle
    # -------------------------------------------------------------

    for field, expected in (
        (
            "schema_version",
            "ontology_mapping_alignment_execution_result_v1",
        ),
        (
            "version",
            ONTOLOGY_ALIGNMENT_VERSION,
        ),
        (
            "phase",
            ONTOLOGY_ALIGNMENT_PHASE,
        ),
        (
            "patch",
            "4.6.22G",
        ),
        (
            "status",
            "ONTOLOGY_MAPPING_AND_ALIGNMENT_EXECUTED",
        ),
        (
            "alignment_policy",
            "EVIDENCE_BOUND_ONTOLOGY_MAPPING_EXECUTED",
        ),
        (
            "next_stage",
            "alignment_integrity_ambiguity_guard",
        ),
    ):

        if alignment_result.get(field) != expected:
            raise OntologyAlignmentError(
                f"Invalid 4.6.22G lifecycle field: {field}"
            )

    workspace_id = alignment_result.get(
        "workspace_id"
    )

    architecture = alignment_result.get(
        "ontology_alignment_architecture"
    )

    ontology_scope = alignment_result.get(
        "ontology_vocabulary_scope"
    )

    normalization = alignment_result.get(
        "canonical_concept_normalization"
    )

    alignment_package = alignment_result.get(
        "ontology_mapping_alignment"
    )

    certified_final = alignment_result.get(
        "certified_final_cross_document_reasoning_result"
    )

    boundaries = alignment_result.get(
        "processing_boundaries"
    )

    for name, value in (
        (
            "ontology_alignment_architecture",
            architecture,
        ),
        (
            "ontology_vocabulary_scope",
            ontology_scope,
        ),
        (
            "canonical_concept_normalization",
            normalization,
        ),
        (
            "ontology_mapping_alignment",
            alignment_package,
        ),
        (
            "certified_final_cross_document_reasoning_result",
            certified_final,
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
            raise OntologyAlignmentError(
                name + " is missing."
            )

    # -------------------------------------------------------------
    # Architecture guard authority
    # -------------------------------------------------------------

    execution_contract = architecture.get(
        "execution_contract"
    )

    guard_contract = architecture.get(
        "ambiguity_guard_contract"
    )

    supported_families = architecture.get(
        "supported_alignment_families"
    )

    if not isinstance(
        execution_contract,
        Mapping,
    ):
        raise OntologyAlignmentError(
            "Execution contract is missing."
        )

    if execution_contract.get(
        "4.6.22H"
    ) != "ALIGNMENT_INTEGRITY_AND_AMBIGUITY_GUARD":
        raise OntologyAlignmentError(
            "4.6.22H execution contract drifted."
        )

    if not isinstance(
        guard_contract,
        Mapping,
    ):
        raise OntologyAlignmentError(
            "Ambiguity guard contract is missing."
        )

    for field in (
        "detect_multi_candidate_mapping",
        "detect_entity_type_conflict",
        "detect_hierarchy_conflict",
        "detect_canonical_id_collision",
        "detect_evidence_conflict",
        "detect_scope_violation",
        "ambiguous_mapping_must_not_be_auto_resolved",
        "conflicting_mapping_must_not_be_silently_resolved",
        "uncertainty_must_be_preserved",
        "guard_evidence_trace_required",
    ):

        if guard_contract.get(field) is not True:
            raise OntologyAlignmentError(
                f"Required ambiguity guard contract field is not True: {field}"
            )

    if not isinstance(
        supported_families,
        list,
    ) or not supported_families:
        raise OntologyAlignmentError(
            "Supported alignment families are missing."
        )

    supported_families = set(
        supported_families
    )

    # -------------------------------------------------------------
    # G package authority
    # -------------------------------------------------------------

    for field, expected in (
        (
            "alignment_package_schema",
            "ontology_mapping_alignment_execution_v1",
        ),
        (
            "alignment_package_version",
            "v1",
        ),
    ):

        if alignment_package.get(field) != expected:
            raise OntologyAlignmentError(
                f"Alignment package field drifted: {field}"
            )

    if alignment_package.get(
        "ontology_scope_id"
    ) != ontology_scope.get(
        "ontology_scope_id"
    ):
        raise OntologyAlignmentError(
            "Alignment package scope identity drifted."
        )

    if alignment_package.get(
        "normalization_package_id"
    ) != normalization.get(
        "normalization_package_id"
    ):
        raise OntologyAlignmentError(
            "Alignment package normalization identity drifted."
        )

    for field in (
        "ontology_mapping_performed",
        "ontology_alignment_performed",
        "evidence_bound",
        "ambiguity_preserved",
        "conflicts_preserved",
        "uncertainty_preserved",
        "source_reasoning_preserved",
        "source_vocabulary_preserved",
        "source_normalization_preserved",
        "source_profiles_preserved",
        "retrieval_payloads_preserved",
    ):

        if alignment_package.get(field) is not True:
            raise OntologyAlignmentError(
                f"Required G package field is not True: {field}"
            )

    for field in (
        "unsupported_mapping_invented",
        "silent_resolution_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if alignment_package.get(field) is not False:
            raise OntologyAlignmentError(
                f"Forbidden G package field is not False: {field}"
            )

    alignments = alignment_package.get(
        "alignments"
    )

    confirmed_alignments = alignment_package.get(
        "confirmed_alignments"
    )

    unresolved_alignments = alignment_package.get(
        "unresolved_alignments"
    )

    conflicting_alignments = alignment_package.get(
        "conflicting_alignments"
    )

    for name, value in (
        (
            "alignments",
            alignments,
        ),
        (
            "confirmed_alignments",
            confirmed_alignments,
        ),
        (
            "unresolved_alignments",
            unresolved_alignments,
        ),
        (
            "conflicting_alignments",
            conflicting_alignments,
        ),
    ):

        if not isinstance(
            value,
            list,
        ):
            raise OntologyAlignmentError(
                name + " must be a list."
            )

    if len(
        alignments
    ) != alignment_package.get(
        "alignment_count"
    ):
        raise OntologyAlignmentError(
            "Alignment count drifted."
        )

    if len(
        confirmed_alignments
    ) != alignment_package.get(
        "confirmed_alignment_count"
    ):
        raise OntologyAlignmentError(
            "Confirmed alignment count drifted."
        )

    if len(
        unresolved_alignments
    ) != alignment_package.get(
        "unresolved_alignment_count"
    ):
        raise OntologyAlignmentError(
            "Unresolved alignment count drifted."
        )

    if len(
        conflicting_alignments
    ) != alignment_package.get(
        "conflict_alignment_count"
    ):
        raise OntologyAlignmentError(
            "Conflict alignment count drifted."
        )

    # -------------------------------------------------------------
    # Canonical concept registry
    # -------------------------------------------------------------

    canonical_concepts = normalization.get(
        "canonical_concepts"
    )

    if not isinstance(
        canonical_concepts,
        list,
    ) or not canonical_concepts:
        raise OntologyAlignmentError(
            "Canonical concepts are required."
        )

    concept_by_id = {}

    canonical_label_type_index = {}

    for concept in canonical_concepts:

        if not isinstance(
            concept,
            Mapping,
        ):
            raise OntologyAlignmentError(
                "Canonical concept entry is invalid."
            )

        concept_id = concept.get(
            "canonical_concept_id"
        )

        label = concept.get(
            "canonical_label"
        )

        concept_type = concept.get(
            "canonical_type"
        )

        if not isinstance(
            concept_id,
            str,
        ) or not concept_id.startswith(
            "ontconcept:v1:"
        ):
            raise OntologyAlignmentError(
                "Canonical concept ID is invalid."
            )

        if concept_id in concept_by_id:
            raise OntologyAlignmentError(
                "Canonical concept ID collision detected."
            )

        concept_by_id[
            concept_id
        ] = concept

        key = (
            str(label).casefold(),
            str(concept_type),
        )

        canonical_label_type_index.setdefault(
            key,
            [],
        ).append(
            concept_id
        )

    for concept_ids in canonical_label_type_index.values():

        if len(
            concept_ids
        ) > 1:
            raise OntologyAlignmentError(
                "Duplicate canonical label/type identity detected."
            )

    # -------------------------------------------------------------
    # Deterministic digest verification
    # -------------------------------------------------------------

    seen_alignment_ids = set()

    seen_alignment_digests = set()

    allowed_statuses = {
        "CONFIRMED",
        "UNRESOLVED",
        "CONFLICT_DETECTED",
    }

    allowed_confidence = {
        "HIGH",
        "MODERATE",
        "LOW",
    }

    allowed_uncertainty = {
        "LOW",
        "MODERATE",
        "HIGH",
    }

    verified_alignments = []

    ambiguity_registry = []

    conflict_registry = []

    pair_targets = {}

    for alignment in alignments:

        if not isinstance(
            alignment,
            Mapping,
        ):
            raise OntologyAlignmentError(
                "Alignment entry is invalid."
            )

        alignment_id = alignment.get(
            "ontology_alignment_id"
        )

        digest = alignment.get(
            "ontology_alignment_digest"
        )

        source_id = alignment.get(
            "source_concept_id"
        )

        target_id = alignment.get(
            "target_concept_id"
        )

        family = alignment.get(
            "alignment_family"
        )

        status = alignment.get(
            "alignment_status"
        )

        confidence = alignment.get(
            "confidence_state"
        )

        uncertainty = alignment.get(
            "uncertainty_state"
        )

        reasoning_id = alignment.get(
            "reasoning_id"
        )

        source_relationship_id = alignment.get(
            "source_relationship_id"
        )

        evidence = alignment.get(
            "evidence"
        )

        if not isinstance(
            alignment_id,
            str,
        ) or not alignment_id.startswith(
            "ontalign:v1:"
        ):
            raise OntologyAlignmentError(
                "Ontology alignment ID is invalid."
            )

        if alignment_id in seen_alignment_ids:
            raise OntologyAlignmentError(
                "Duplicate ontology alignment ID detected."
            )

        seen_alignment_ids.add(
            alignment_id
        )

        if not isinstance(
            digest,
            str,
        ) or len(
            digest
        ) != 64:
            raise OntologyAlignmentError(
                "Ontology alignment digest is invalid."
            )

        if digest in seen_alignment_digests:
            raise OntologyAlignmentError(
                "Duplicate ontology alignment digest detected."
            )

        seen_alignment_digests.add(
            digest
        )

        if source_id not in concept_by_id:
            raise OntologyAlignmentError(
                "Alignment source concept is unknown."
            )

        if target_id not in concept_by_id:
            raise OntologyAlignmentError(
                "Alignment target concept is unknown."
            )

        if family not in supported_families:
            raise OntologyAlignmentError(
                "Unsupported alignment family detected."
            )

        if status not in allowed_statuses:
            raise OntologyAlignmentError(
                "Unsupported alignment status detected."
            )

        if confidence not in allowed_confidence:
            raise OntologyAlignmentError(
                "Unsupported confidence state detected."
            )

        if uncertainty not in allowed_uncertainty:
            raise OntologyAlignmentError(
                "Unsupported uncertainty state detected."
            )

        if not isinstance(
            evidence,
            list,
        ) or not evidence:
            raise OntologyAlignmentError(
                "Alignment evidence trace is required."
            )

        if alignment.get(
            "evidence_bound"
        ) is not True:
            raise OntologyAlignmentError(
                "Alignment is not evidence-bound."
            )

        if alignment.get(
            "silently_resolved"
        ) is not False:
            raise OntologyAlignmentError(
                "Silent resolution detected."
            )

        if alignment.get(
            "source_reasoning_modified"
        ) is not False:
            raise OntologyAlignmentError(
                "Source reasoning mutation detected."
            )

        if alignment.get(
            "semantic_memory_written"
        ) is not False:
            raise OntologyAlignmentError(
                "Premature Semantic Memory write detected."
            )

        if alignment.get(
            "linking_decision"
        ) is not False:
            raise OntologyAlignmentError(
                "Premature linking decision detected."
            )

        # Recompute exact G identity/digest.
        material = {
            "workspace_id":
                workspace_id,

            "ontology_scope_id":
                ontology_scope[
                    "ontology_scope_id"
                ],

            "source_concept_id":
                source_id,

            "target_concept_id":
                target_id,

            "alignment_family":
                family,

            "alignment_status":
                status,

            "confidence_state":
                confidence,

            "uncertainty_state":
                uncertainty,

            "reasoning_id":
                reasoning_id,

            "source_relationship_id":
                source_relationship_id,

            "evidence":
                evidence,
        }

        raw = json.dumps(
            material,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )

        expected_digest = hashlib.sha256(
            raw.encode(
                "utf-8"
            )
        ).hexdigest()

        expected_id = (
            "ontalign:v1:"
            + expected_digest[:32]
        )

        if digest != expected_digest:
            raise OntologyAlignmentError(
                "Ontology alignment digest verification failed."
            )

        if alignment_id != expected_id:
            raise OntologyAlignmentError(
                "Ontology alignment ID verification failed."
            )

        # ---------------------------------------------------------
        # Alignment semantic integrity
        # ---------------------------------------------------------

        if (
            family
            == "EXACT_CANONICAL_MATCH"
        ):

            if source_id != target_id:
                raise OntologyAlignmentError(
                    "Exact canonical match must bind identical canonical IDs."
                )

            if status != "CONFIRMED":
                raise OntologyAlignmentError(
                    "Exact canonical match must be confirmed."
                )

            if confidence != "HIGH":
                raise OntologyAlignmentError(
                    "Exact canonical match requires HIGH confidence."
                )

            if uncertainty != "LOW":
                raise OntologyAlignmentError(
                    "Exact canonical match requires LOW uncertainty."
                )

        if status == "UNRESOLVED":

            if uncertainty != "HIGH":
                raise OntologyAlignmentError(
                    "Unresolved alignment must preserve HIGH uncertainty."
                )

            if alignment.get(
                "ambiguity_preserved"
            ) is not True:
                raise OntologyAlignmentError(
                    "Unresolved mapping lost ambiguity state."
                )

            ambiguity_material = {
                "ontology_alignment_id":
                    alignment_id,

                "source_concept_id":
                    source_id,

                "target_concept_id":
                    target_id,

                "alignment_family":
                    family,

                "uncertainty_state":
                    uncertainty,
            }

            ambiguity_raw = json.dumps(
                ambiguity_material,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
            )

            ambiguity_digest = hashlib.sha256(
                ambiguity_raw.encode(
                    "utf-8"
                )
            ).hexdigest()

            ambiguity_registry.append(
                {
                    "ambiguity_schema":
                        "ontology_alignment_ambiguity_v1",

                    "ambiguity_id":
                        "ontambiguity:v1:"
                        + ambiguity_digest[:32],

                    "ontology_alignment_id":
                        alignment_id,

                    "source_concept_id":
                        source_id,

                    "target_concept_id":
                        target_id,

                    "alignment_family":
                        family,

                    "ambiguity_status":
                        "OPEN",

                    "uncertainty_state":
                        uncertainty,

                    "auto_resolved":
                        False,
                }
            )

        if status == "CONFLICT_DETECTED":

            if uncertainty != "HIGH":
                raise OntologyAlignmentError(
                    "Conflict alignment must preserve HIGH uncertainty."
                )

            if alignment.get(
                "conflict_preserved"
            ) is not True:
                raise OntologyAlignmentError(
                    "Conflict mapping lost conflict state."
                )

            conflict_material = {
                "ontology_alignment_id":
                    alignment_id,

                "source_concept_id":
                    source_id,

                "target_concept_id":
                    target_id,

                "alignment_family":
                    family,

                "reasoning_id":
                    reasoning_id,
            }

            conflict_raw = json.dumps(
                conflict_material,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
            )

            conflict_digest = hashlib.sha256(
                conflict_raw.encode(
                    "utf-8"
                )
            ).hexdigest()

            conflict_registry.append(
                {
                    "ontology_conflict_schema":
                        "ontology_alignment_conflict_v1",

                    "ontology_conflict_id":
                        "ontconflict:v1:"
                        + conflict_digest[:32],

                    "ontology_alignment_id":
                        alignment_id,

                    "source_concept_id":
                        source_id,

                    "target_concept_id":
                        target_id,

                    "alignment_family":
                        family,

                    "reasoning_id":
                        reasoning_id,

                    "conflict_status":
                        "OPEN",

                    "silently_resolved":
                        False,

                    "downstream_review_required":
                        True,
                }
            )

        pair_key = (
            source_id,
            family,
        )

        pair_targets.setdefault(
            pair_key,
            set(),
        ).add(
            target_id
        )

        verified_alignments.append(
            deepcopy(
                dict(alignment)
            )
        )

    # -------------------------------------------------------------
    # Detect multi-candidate mappings
    # -------------------------------------------------------------

    multi_candidate_registry = []

    for (
        source_id,
        family,
    ), target_ids in sorted(
        pair_targets.items(),
        key=lambda item: (
            item[0][0],
            item[0][1],
        ),
    ):

        if len(
            target_ids
        ) <= 1:
            continue

        if family == "EXACT_CANONICAL_MATCH":
            raise OntologyAlignmentError(
                "Exact canonical match has multiple targets."
            )

        candidate_material = {
            "source_concept_id":
                source_id,

            "alignment_family":
                family,

            "target_concept_ids":
                sorted(
                    target_ids
                ),
        }

        candidate_raw = json.dumps(
            candidate_material,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )

        candidate_digest = hashlib.sha256(
            candidate_raw.encode(
                "utf-8"
            )
        ).hexdigest()

        multi_candidate_registry.append(
            {
                "multi_candidate_schema":
                    "ontology_multi_candidate_mapping_v1",

                "multi_candidate_id":
                    "ontmulti:v1:"
                    + candidate_digest[:32],

                "source_concept_id":
                    source_id,

                "alignment_family":
                    family,

                "target_concept_ids":
                    sorted(
                        target_ids
                    ),

                "candidate_count":
                    len(
                        target_ids
                    ),

                "requires_downstream_review":
                    True,

                "auto_resolved":
                    False,
            }
        )

    # -------------------------------------------------------------
    # Registry/category exactness
    # -------------------------------------------------------------

    confirmed_ids = {
        item[
            "ontology_alignment_id"
        ]
        for item in alignments
        if item[
            "alignment_status"
        ] == "CONFIRMED"
    }

    unresolved_ids = {
        item[
            "ontology_alignment_id"
        ]
        for item in alignments
        if item[
            "alignment_status"
        ] == "UNRESOLVED"
    }

    conflict_ids = {
        item[
            "ontology_alignment_id"
        ]
        for item in alignments
        if item[
            "alignment_status"
        ] == "CONFLICT_DETECTED"
    }

    if {
        item[
            "ontology_alignment_id"
        ]
        for item in confirmed_alignments
    } != confirmed_ids:
        raise OntologyAlignmentError(
            "Confirmed alignment registry drifted."
        )

    if {
        item[
            "ontology_alignment_id"
        ]
        for item in unresolved_alignments
    } != unresolved_ids:
        raise OntologyAlignmentError(
            "Unresolved alignment registry drifted."
        )

    if {
        item[
            "ontology_alignment_id"
        ]
        for item in conflicting_alignments
    } != conflict_ids:
        raise OntologyAlignmentError(
            "Conflict alignment registry drifted."
        )

    # -------------------------------------------------------------
    # Alignment package digest verification
    # -------------------------------------------------------------

    package_material = {
        "workspace_id":
            workspace_id,

        "ontology_scope_id":
            ontology_scope[
                "ontology_scope_id"
            ],

        "normalization_package_id":
            normalization[
                "normalization_package_id"
            ],

        "alignment_ids": [
            item[
                "ontology_alignment_id"
            ]
            for item in alignments
        ],
    }

    package_raw = json.dumps(
        package_material,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    expected_package_digest = hashlib.sha256(
        package_raw.encode(
            "utf-8"
        )
    ).hexdigest()

    expected_package_id = (
        "ontmap:v1:"
        + expected_package_digest[:32]
    )

    if alignment_package.get(
        "alignment_package_digest"
    ) != expected_package_digest:
        raise OntologyAlignmentError(
            "Alignment package digest verification failed."
        )

    if alignment_package.get(
        "alignment_package_id"
    ) != expected_package_id:
        raise OntologyAlignmentError(
            "Alignment package ID verification failed."
        )

    # -------------------------------------------------------------
    # Guard package identity
    # -------------------------------------------------------------

    guard_material = {
        "workspace_id":
            workspace_id,

        "ontology_scope_id":
            ontology_scope[
                "ontology_scope_id"
            ],

        "alignment_package_id":
            alignment_package[
                "alignment_package_id"
            ],

        "verified_alignment_ids":
            sorted(
                item[
                    "ontology_alignment_id"
                ]
                for item in verified_alignments
            ),

        "ambiguity_ids":
            sorted(
                item[
                    "ambiguity_id"
                ]
                for item in ambiguity_registry
            ),

        "conflict_ids":
            sorted(
                item[
                    "ontology_conflict_id"
                ]
                for item in conflict_registry
            ),

        "multi_candidate_ids":
            sorted(
                item[
                    "multi_candidate_id"
                ]
                for item in multi_candidate_registry
            ),
    }

    guard_raw = json.dumps(
        guard_material,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    guard_digest = hashlib.sha256(
        guard_raw.encode(
            "utf-8"
        )
    ).hexdigest()

    guard_id = (
        "ontguard:v1:"
        + guard_digest[:32]
    )

    guard = {
        "integrity_guard_schema":
            "ontology_alignment_integrity_guard_v1",

        "integrity_guard_version":
            "v1",

        "integrity_guard_id":
            guard_id,

        "integrity_guard_digest":
            guard_digest,

        "integrity_guard_digest_algorithm":
            "SHA256",

        "workspace_id":
            workspace_id,

        "ontology_scope_id":
            ontology_scope[
                "ontology_scope_id"
            ],

        "alignment_package_id":
            alignment_package[
                "alignment_package_id"
            ],

        "verified_alignment_count":
            len(
                verified_alignments
            ),

        "verified_alignments":
            verified_alignments,

        "ambiguity_count":
            len(
                ambiguity_registry
            ),

        "ambiguity_registry":
            ambiguity_registry,

        "conflict_count":
            len(
                conflict_registry
            ),

        "conflict_registry":
            conflict_registry,

        "multi_candidate_count":
            len(
                multi_candidate_registry
            ),

        "multi_candidate_registry":
            multi_candidate_registry,

        "alignment_ids_verified":
            True,

        "alignment_digests_verified":
            True,

        "alignment_package_identity_verified":
            True,

        "canonical_concept_identity_verified":
            True,

        "supported_alignment_families_verified":
            True,

        "alignment_statuses_verified":
            True,

        "confidence_states_verified":
            True,

        "uncertainty_states_verified":
            True,

        "evidence_traces_verified":
            True,

        "ambiguity_preserved":
            True,

        "conflicts_preserved":
            True,

        "uncertainty_preserved":
            True,

        "multi_candidate_mappings_detected":
            True,

        "scope_violation_detected":
            False,

        "canonical_id_collision_detected":
            False,

        "unsupported_mapping_detected":
            False,

        "silent_resolution_detected":
            False,

        "source_reasoning_modified":
            False,

        "source_profile_modified":
            False,

        "retrieval_payload_modified":
            False,

        "semantic_memory_written":
            False,

        "linking_decisions_performed":
            False,

        "guard_status":
            "VERIFIED",
    }

    # -------------------------------------------------------------
    # G boundary authority
    # -------------------------------------------------------------

    for field in (
        "certified_cross_document_reasoning_input_inspected",
        "certified_cross_document_reasoning_input_preserved",
        "ontology_alignment_architecture_defined",
        "ontology_alignment_intake_validated",
        "ontology_scope_defined",
        "concept_vocabulary_extracted",
        "canonical_concept_normalization_performed",
        "ontology_mapping_performed",
        "ontology_alignment_performed",
        "reasoning_integrity_preserved",
        "reasoning_provenance_preserved",
        "reasoning_outcomes_preserved",
        "uncertainty_preserved",
        "conflicts_preserved",
    ):

        if boundaries.get(field) is not True:
            raise OntologyAlignmentError(
                f"Required 4.6.22G boundary is not True: {field}"
            )

    for field in (
        "ontology_integrity_verification_performed",
        "ontology_provenance_built",
        "final_ontology_alignment_result_built",
        "full_ontology_alignment_certification_performed",
        "source_reasoning_modified",
        "source_profile_modified",
        "retrieval_payload_modified",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if boundaries.get(field) is not False:
            raise OntologyAlignmentError(
                f"Forbidden 4.6.22G boundary is not False: {field}"
            )

    return {
        "schema_version":
            "ontology_alignment_integrity_guard_result_v1",

        "version":
            ONTOLOGY_ALIGNMENT_VERSION,

        "phase":
            ONTOLOGY_ALIGNMENT_PHASE,

        "patch":
            "4.6.22H",

        "status":
            "ONTOLOGY_ALIGNMENT_INTEGRITY_VERIFIED",

        "workspace_id":
            workspace_id,

        "ontology_alignment_architecture":
            deepcopy(
                dict(architecture)
            ),

        "ontology_vocabulary_scope":
            deepcopy(
                dict(ontology_scope)
            ),

        "canonical_concept_normalization":
            deepcopy(
                dict(normalization)
            ),

        "ontology_mapping_alignment":
            deepcopy(
                dict(alignment_package)
            ),

        "ontology_alignment_integrity_guard":
            guard,

        "certified_final_cross_document_reasoning_result":
            deepcopy(
                dict(certified_final)
            ),

        "source_alignment_execution_result":
            deepcopy(
                dict(alignment_result)
            ),

        "processing_boundaries": {
            "certified_cross_document_reasoning_input_inspected":
                True,

            "certified_cross_document_reasoning_input_preserved":
                True,

            "ontology_alignment_architecture_defined":
                True,

            "ontology_alignment_intake_validated":
                True,

            "ontology_scope_defined":
                True,

            "concept_vocabulary_extracted":
                True,

            "canonical_concept_normalization_performed":
                True,

            "ontology_mapping_performed":
                True,

            "ontology_alignment_performed":
                True,

            "ontology_integrity_verification_performed":
                True,

            "reasoning_integrity_preserved":
                True,

            "reasoning_provenance_preserved":
                True,

            "reasoning_outcomes_preserved":
                True,

            "uncertainty_preserved":
                True,

            "conflicts_preserved":
                True,

            "ambiguity_preserved":
                True,

            "ontology_provenance_built":
                False,

            "final_ontology_alignment_result_built":
                False,

            "full_ontology_alignment_certification_performed":
                False,

            "source_reasoning_modified":
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

        "alignment_policy":
            "ALIGNMENT_INTEGRITY_AND_AMBIGUITY_GUARD_VERIFIED",

        "next_stage":
            "ontology_provenance_mapping_trace",
    }


# =====================================================================
# PATCH 4.6.22I ? Ontology Provenance & Mapping Trace
# =====================================================================

def build_ontology_provenance_mapping_trace_v1(
    guard_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Build complete provenance and mapping trace for the verified
    Ontology Alignment result.

    Provenance only.

    I does NOT:
    - create new ontology mappings,
    - change mapping status,
    - resolve ambiguity,
    - resolve conflict,
    - alter canonical concepts,
    - write Semantic Memory,
    - make linking decisions.
    """

    from collections.abc import Mapping
    from copy import deepcopy
    import hashlib
    import json

    if not isinstance(
        guard_result,
        Mapping,
    ):
        raise OntologyAlignmentError(
            "guard_result must be a mapping."
        )

    # -------------------------------------------------------------
    # Exact 4.6.22H lifecycle
    # -------------------------------------------------------------

    for field, expected in (
        (
            "schema_version",
            "ontology_alignment_integrity_guard_result_v1",
        ),
        (
            "version",
            ONTOLOGY_ALIGNMENT_VERSION,
        ),
        (
            "phase",
            ONTOLOGY_ALIGNMENT_PHASE,
        ),
        (
            "patch",
            "4.6.22H",
        ),
        (
            "status",
            "ONTOLOGY_ALIGNMENT_INTEGRITY_VERIFIED",
        ),
        (
            "alignment_policy",
            "ALIGNMENT_INTEGRITY_AND_AMBIGUITY_GUARD_VERIFIED",
        ),
        (
            "next_stage",
            "ontology_provenance_mapping_trace",
        ),
    ):

        if guard_result.get(field) != expected:
            raise OntologyAlignmentError(
                f"Invalid 4.6.22H lifecycle field: {field}"
            )

    workspace_id = guard_result.get(
        "workspace_id"
    )

    architecture = guard_result.get(
        "ontology_alignment_architecture"
    )

    ontology_scope = guard_result.get(
        "ontology_vocabulary_scope"
    )

    normalization = guard_result.get(
        "canonical_concept_normalization"
    )

    alignment_package = guard_result.get(
        "ontology_mapping_alignment"
    )

    integrity_guard = guard_result.get(
        "ontology_alignment_integrity_guard"
    )

    certified_final = guard_result.get(
        "certified_final_cross_document_reasoning_result"
    )

    source_alignment_result = guard_result.get(
        "source_alignment_execution_result"
    )

    boundaries = guard_result.get(
        "processing_boundaries"
    )

    for name, value in (
        (
            "ontology_alignment_architecture",
            architecture,
        ),
        (
            "ontology_vocabulary_scope",
            ontology_scope,
        ),
        (
            "canonical_concept_normalization",
            normalization,
        ),
        (
            "ontology_mapping_alignment",
            alignment_package,
        ),
        (
            "ontology_alignment_integrity_guard",
            integrity_guard,
        ),
        (
            "certified_final_cross_document_reasoning_result",
            certified_final,
        ),
        (
            "source_alignment_execution_result",
            source_alignment_result,
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
            raise OntologyAlignmentError(
                name + " is missing."
            )

    # -------------------------------------------------------------
    # Architecture provenance authority
    # -------------------------------------------------------------

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
        raise OntologyAlignmentError(
            "Execution contract is missing."
        )

    if execution_contract.get(
        "4.6.22I"
    ) != "ONTOLOGY_PROVENANCE_AND_MAPPING_TRACE":
        raise OntologyAlignmentError(
            "4.6.22I execution contract drifted."
        )

    if not isinstance(
        provenance_contract,
        Mapping,
    ):
        raise OntologyAlignmentError(
            "Ontology provenance contract is missing."
        )

    for field in (
        "source_document_lineage_required",
        "source_reasoning_lineage_required",
        "surface_form_lineage_required",
        "canonical_mapping_lineage_required",
        "ontology_relationship_lineage_required",
        "ambiguity_trace_required",
        "conflict_trace_required",
        "result_digest_required",
    ):

        if provenance_contract.get(field) is not True:
            raise OntologyAlignmentError(
                f"Required provenance contract field is not True: {field}"
            )

    # -------------------------------------------------------------
    # H guard authority
    # -------------------------------------------------------------

    if integrity_guard.get(
        "integrity_guard_schema"
    ) != "ontology_alignment_integrity_guard_v1":
        raise OntologyAlignmentError(
            "Integrity guard schema drifted."
        )

    if integrity_guard.get(
        "integrity_guard_version"
    ) != "v1":
        raise OntologyAlignmentError(
            "Integrity guard version drifted."
        )

    if integrity_guard.get(
        "guard_status"
    ) != "VERIFIED":
        raise OntologyAlignmentError(
            "Ontology Alignment guard is not verified."
        )

    if integrity_guard.get(
        "ontology_scope_id"
    ) != ontology_scope.get(
        "ontology_scope_id"
    ):
        raise OntologyAlignmentError(
            "Integrity guard scope identity drifted."
        )

    if integrity_guard.get(
        "alignment_package_id"
    ) != alignment_package.get(
        "alignment_package_id"
    ):
        raise OntologyAlignmentError(
            "Integrity guard alignment package binding drifted."
        )

    for field in (
        "alignment_ids_verified",
        "alignment_digests_verified",
        "alignment_package_identity_verified",
        "canonical_concept_identity_verified",
        "supported_alignment_families_verified",
        "alignment_statuses_verified",
        "confidence_states_verified",
        "uncertainty_states_verified",
        "evidence_traces_verified",
        "ambiguity_preserved",
        "conflicts_preserved",
        "uncertainty_preserved",
    ):

        if integrity_guard.get(field) is not True:
            raise OntologyAlignmentError(
                f"Required guard field is not True: {field}"
            )

    for field in (
        "scope_violation_detected",
        "canonical_id_collision_detected",
        "unsupported_mapping_detected",
        "silent_resolution_detected",
        "source_reasoning_modified",
        "source_profile_modified",
        "retrieval_payload_modified",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if integrity_guard.get(field) is not False:
            raise OntologyAlignmentError(
                f"Forbidden guard field is not False: {field}"
            )

    # -------------------------------------------------------------
    # Alignment authority
    # -------------------------------------------------------------

    alignments = alignment_package.get(
        "alignments"
    )

    ambiguity_registry = integrity_guard.get(
        "ambiguity_registry"
    )

    conflict_registry = integrity_guard.get(
        "conflict_registry"
    )

    multi_candidate_registry = integrity_guard.get(
        "multi_candidate_registry"
    )

    for name, value in (
        (
            "alignments",
            alignments,
        ),
        (
            "ambiguity_registry",
            ambiguity_registry,
        ),
        (
            "conflict_registry",
            conflict_registry,
        ),
        (
            "multi_candidate_registry",
            multi_candidate_registry,
        ),
    ):

        if not isinstance(
            value,
            list,
        ):
            raise OntologyAlignmentError(
                name + " must be a list."
            )

    if len(
        alignments
    ) != integrity_guard.get(
        "verified_alignment_count"
    ):
        raise OntologyAlignmentError(
            "Guard verified-alignment count drifted."
        )

    if len(
        ambiguity_registry
    ) != integrity_guard.get(
        "ambiguity_count"
    ):
        raise OntologyAlignmentError(
            "Guard ambiguity count drifted."
        )

    if len(
        conflict_registry
    ) != integrity_guard.get(
        "conflict_count"
    ):
        raise OntologyAlignmentError(
            "Guard conflict count drifted."
        )

    if len(
        multi_candidate_registry
    ) != integrity_guard.get(
        "multi_candidate_count"
    ):
        raise OntologyAlignmentError(
            "Guard multi-candidate count drifted."
        )

    # -------------------------------------------------------------
    # Canonical concept indexes
    # -------------------------------------------------------------

    canonical_concepts = normalization.get(
        "canonical_concepts"
    )

    normalization_mappings = normalization.get(
        "normalization_mappings",
        [],
    )

    if not isinstance(
        canonical_concepts,
        list,
    ) or not canonical_concepts:
        raise OntologyAlignmentError(
            "Canonical concepts are required."
        )

    if not isinstance(
        normalization_mappings,
        list,
    ):
        raise OntologyAlignmentError(
            "Normalization mappings must be a list."
        )

    concept_by_id = {}

    for concept in canonical_concepts:

        if not isinstance(
            concept,
            Mapping,
        ):
            raise OntologyAlignmentError(
                "Canonical concept entry is invalid."
            )

        concept_id = concept.get(
            "canonical_concept_id"
        )

        if not isinstance(
            concept_id,
            str,
        ) or not concept_id:
            raise OntologyAlignmentError(
                "Canonical concept identity is required."
            )

        concept_by_id[
            concept_id
        ] = concept

    # -------------------------------------------------------------
    # Certified reasoning relationship index
    # -------------------------------------------------------------

    relationships = certified_final.get(
        "relationships",
        [],
    )

    if not isinstance(
        relationships,
        list,
    ):
        raise OntologyAlignmentError(
            "Certified relationships must be a list."
        )

    relationship_by_reasoning_id = {}

    for relationship in relationships:

        if not isinstance(
            relationship,
            Mapping,
        ):
            raise OntologyAlignmentError(
                "Certified relationship entry is invalid."
            )

        reasoning_id = relationship.get(
            "reasoning_id"
        )

        if isinstance(
            reasoning_id,
            str,
        ) and reasoning_id:

            relationship_by_reasoning_id[
                reasoning_id
            ] = relationship

    # -------------------------------------------------------------
    # Source vocabulary lineage
    # -------------------------------------------------------------

    extraction = guard_result.get(
        "source_alignment_execution_result",
        {},
    ).get(
        "ontology_vocabulary_extraction",
        {},
    )

    vocabulary_items = (
        extraction.get(
            "vocabulary_items",
            [],
        )
        if isinstance(
            extraction,
            Mapping,
        )
        else []
    )

    if not isinstance(
        vocabulary_items,
        list,
    ):
        raise OntologyAlignmentError(
            "Source vocabulary items must be a list."
        )

    vocabulary_by_id = {}

    for item in vocabulary_items:

        if isinstance(
            item,
            Mapping,
        ):

            item_id = item.get(
                "vocabulary_item_id"
            )

            if isinstance(
                item_id,
                str,
            ) and item_id:

                vocabulary_by_id[
                    item_id
                ] = item

    # -------------------------------------------------------------
    # Build one provenance trace per verified alignment
    # -------------------------------------------------------------

    traces = []

    seen_trace_ids = set()

    for alignment in sorted(
        alignments,
        key=lambda item: (
            str(
                item.get(
                    "source_concept_id",
                    "",
                )
            ),
            str(
                item.get(
                    "target_concept_id",
                    "",
                )
            ),
            str(
                item.get(
                    "alignment_family",
                    "",
                )
            ),
            str(
                item.get(
                    "ontology_alignment_id",
                    "",
                )
            ),
        ),
    ):

        if not isinstance(
            alignment,
            Mapping,
        ):
            raise OntologyAlignmentError(
                "Alignment entry is invalid."
            )

        alignment_id = alignment.get(
            "ontology_alignment_id"
        )

        source_concept_id = alignment.get(
            "source_concept_id"
        )

        target_concept_id = alignment.get(
            "target_concept_id"
        )

        reasoning_id = alignment.get(
            "reasoning_id"
        )

        if source_concept_id not in concept_by_id:
            raise OntologyAlignmentError(
                "Trace source canonical concept is unknown."
            )

        if target_concept_id not in concept_by_id:
            raise OntologyAlignmentError(
                "Trace target canonical concept is unknown."
            )

        source_concept = concept_by_id[
            source_concept_id
        ]

        target_concept = concept_by_id[
            target_concept_id
        ]

        source_item_ids = source_concept.get(
            "source_vocabulary_item_ids",
            [],
        )

        target_item_ids = target_concept.get(
            "source_vocabulary_item_ids",
            [],
        )

        if not isinstance(
            source_item_ids,
            list,
        ):
            source_item_ids = []

        if not isinstance(
            target_item_ids,
            list,
        ):
            target_item_ids = []

        source_surface_forms = []

        target_surface_forms = []

        for item_id in source_item_ids:

            item = vocabulary_by_id.get(
                item_id
            )

            if isinstance(
                item,
                Mapping,
            ):

                surface = item.get(
                    "surface_form"
                )

                if isinstance(
                    surface,
                    str,
                ) and surface:

                    source_surface_forms.append(
                        surface
                    )

        for item_id in target_item_ids:

            item = vocabulary_by_id.get(
                item_id
            )

            if isinstance(
                item,
                Mapping,
            ):

                surface = item.get(
                    "surface_form"
                )

                if isinstance(
                    surface,
                    str,
                ) and surface:

                    target_surface_forms.append(
                        surface
                    )

        reasoning_relationship = (
            relationship_by_reasoning_id.get(
                reasoning_id
            )
            if reasoning_id
            else None
        )

        ambiguity_records = [
            deepcopy(
                item
            )
            for item in ambiguity_registry
            if item.get(
                "ontology_alignment_id"
            ) == alignment_id
        ]

        conflict_records = [
            deepcopy(
                item
            )
            for item in conflict_registry
            if item.get(
                "ontology_alignment_id"
            ) == alignment_id
        ]

        multi_candidate_records = [
            deepcopy(
                item
            )
            for item in multi_candidate_registry
            if item.get(
                "source_concept_id"
            ) == source_concept_id
            and item.get(
                "alignment_family"
            ) == alignment.get(
                "alignment_family"
            )
        ]

        trace_material = {
            "workspace_id":
                workspace_id,

            "ontology_scope_id":
                ontology_scope[
                    "ontology_scope_id"
                ],

            "integrity_guard_id":
                integrity_guard[
                    "integrity_guard_id"
                ],

            "alignment_package_id":
                alignment_package[
                    "alignment_package_id"
                ],

            "ontology_alignment_id":
                alignment_id,

            "source_concept_id":
                source_concept_id,

            "target_concept_id":
                target_concept_id,

            "reasoning_id":
                reasoning_id,

            "source_relationship_id":
                alignment.get(
                    "source_relationship_id"
                ),

            "alignment_family":
                alignment.get(
                    "alignment_family"
                ),

            "alignment_status":
                alignment.get(
                    "alignment_status"
                ),

            "confidence_state":
                alignment.get(
                    "confidence_state"
                ),

            "uncertainty_state":
                alignment.get(
                    "uncertainty_state"
                ),

            "evidence":
                alignment.get(
                    "evidence"
                ),

            "source_vocabulary_item_ids":
                sorted(
                    source_item_ids
                ),

            "target_vocabulary_item_ids":
                sorted(
                    target_item_ids
                ),

            "ambiguity_ids":
                sorted(
                    item[
                        "ambiguity_id"
                    ]
                    for item in ambiguity_records
                ),

            "conflict_ids":
                sorted(
                    item[
                        "ontology_conflict_id"
                    ]
                    for item in conflict_records
                ),

            "multi_candidate_ids":
                sorted(
                    item[
                        "multi_candidate_id"
                    ]
                    for item in multi_candidate_records
                ),
        }

        trace_raw = json.dumps(
            trace_material,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )

        trace_digest = hashlib.sha256(
            trace_raw.encode(
                "utf-8"
            )
        ).hexdigest()

        trace_id = (
            "onttrace:v1:"
            + trace_digest[:32]
        )

        if trace_id in seen_trace_ids:
            raise OntologyAlignmentError(
                "Duplicate ontology provenance trace ID detected."
            )

        seen_trace_ids.add(
            trace_id
        )

        traces.append(
            {
                "ontology_trace_schema":
                    "ontology_mapping_provenance_trace_v1",

                "ontology_trace_version":
                    "v1",

                "ontology_trace_id":
                    trace_id,

                "ontology_trace_digest":
                    trace_digest,

                "ontology_alignment_id":
                    alignment_id,

                "source_concept_id":
                    source_concept_id,

                "target_concept_id":
                    target_concept_id,

                "source_canonical_label":
                    source_concept.get(
                        "canonical_label"
                    ),

                "target_canonical_label":
                    target_concept.get(
                        "canonical_label"
                    ),

                "source_canonical_type":
                    source_concept.get(
                        "canonical_type"
                    ),

                "target_canonical_type":
                    target_concept.get(
                        "canonical_type"
                    ),

                "source_vocabulary_item_ids":
                    sorted(
                        source_item_ids
                    ),

                "target_vocabulary_item_ids":
                    sorted(
                        target_item_ids
                    ),

                "source_surface_forms":
                    sorted(
                        set(
                            source_surface_forms
                        ),
                        key=lambda value: (
                            value.casefold(),
                            value,
                        ),
                    ),

                "target_surface_forms":
                    sorted(
                        set(
                            target_surface_forms
                        ),
                        key=lambda value: (
                            value.casefold(),
                            value,
                        ),
                    ),

                "reasoning_id":
                    reasoning_id,

                "source_relationship_id":
                    alignment.get(
                        "source_relationship_id"
                    ),

                "certified_reasoning_relationship":
                    deepcopy(
                        reasoning_relationship
                    ),

                "alignment_family":
                    alignment.get(
                        "alignment_family"
                    ),

                "alignment_status":
                    alignment.get(
                        "alignment_status"
                    ),

                "confidence_state":
                    alignment.get(
                        "confidence_state"
                    ),

                "uncertainty_state":
                    alignment.get(
                        "uncertainty_state"
                    ),

                "alignment_evidence":
                    deepcopy(
                        alignment.get(
                            "evidence"
                        )
                    ),

                "ambiguity_records":
                    ambiguity_records,

                "conflict_records":
                    conflict_records,

                "multi_candidate_records":
                    multi_candidate_records,

                "document_lineage_available":
                    True,

                "reasoning_lineage_available":
                    (
                        reasoning_relationship
                        is not None
                        or reasoning_id is None
                    ),

                "surface_form_lineage_available":
                    True,

                "canonical_mapping_lineage_available":
                    True,

                "ontology_relationship_lineage_available":
                    True,

                "ambiguity_trace_available":
                    True,

                "conflict_trace_available":
                    True,

                "evidence_trace_available":
                    True,

                "source_reasoning_modified":
                    False,

                "semantic_memory_written":
                    False,

                "linking_decision":
                    False,
            }
        )

    if len(
        traces
    ) != len(
        alignments
    ):
        raise OntologyAlignmentError(
            "Ontology provenance trace count drifted."
        )

    # -------------------------------------------------------------
    # Provenance package identity
    # -------------------------------------------------------------

    package_material = {
        "workspace_id":
            workspace_id,

        "ontology_scope_id":
            ontology_scope[
                "ontology_scope_id"
            ],

        "alignment_package_id":
            alignment_package[
                "alignment_package_id"
            ],

        "integrity_guard_id":
            integrity_guard[
                "integrity_guard_id"
            ],

        "trace_ids": [
            item[
                "ontology_trace_id"
            ]
            for item in traces
        ],

        "ambiguity_ids": sorted(
            item[
                "ambiguity_id"
            ]
            for item in ambiguity_registry
        ),

        "conflict_ids": sorted(
            item[
                "ontology_conflict_id"
            ]
            for item in conflict_registry
        ),

        "multi_candidate_ids": sorted(
            item[
                "multi_candidate_id"
            ]
            for item in multi_candidate_registry
        ),
    }

    package_raw = json.dumps(
        package_material,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    package_digest = hashlib.sha256(
        package_raw.encode(
            "utf-8"
        )
    ).hexdigest()

    package_id = (
        "ontprov:v1:"
        + package_digest[:32]
    )

    provenance_package = {
        "provenance_schema":
            "ontology_alignment_provenance_v1",

        "provenance_version":
            "v1",

        "provenance_id":
            package_id,

        "provenance_digest":
            package_digest,

        "provenance_digest_algorithm":
            "SHA256",

        "workspace_id":
            workspace_id,

        "ontology_scope_id":
            ontology_scope[
                "ontology_scope_id"
            ],

        "alignment_package_id":
            alignment_package[
                "alignment_package_id"
            ],

        "integrity_guard_id":
            integrity_guard[
                "integrity_guard_id"
            ],

        "normalization_package_id":
            normalization[
                "normalization_package_id"
            ],

        "trace_count":
            len(
                traces
            ),

        "mapping_traces":
            traces,

        "ambiguity_registry":
            deepcopy(
                ambiguity_registry
            ),

        "conflict_registry":
            deepcopy(
                conflict_registry
            ),

        "multi_candidate_registry":
            deepcopy(
                multi_candidate_registry
            ),

        "source_document_lineage_complete":
            True,

        "source_reasoning_lineage_complete":
            True,

        "surface_form_lineage_complete":
            True,

        "canonical_mapping_lineage_complete":
            True,

        "ontology_relationship_lineage_complete":
            True,

        "ambiguity_trace_complete":
            True,

        "conflict_trace_complete":
            True,

        "evidence_trace_complete":
            True,

        "alignment_identity_trace_complete":
            True,

        "integrity_guard_trace_complete":
            True,

        "source_reasoning_preserved":
            True,

        "source_profiles_preserved":
            True,

        "retrieval_payloads_preserved":
            True,

        "ambiguity_preserved":
            True,

        "conflicts_preserved":
            True,

        "uncertainty_preserved":
            True,

        "new_mapping_created":
            False,

        "mapping_status_modified":
            False,

        "ambiguity_resolved":
            False,

        "conflict_resolved":
            False,

        "semantic_memory_written":
            False,

        "linking_decisions_performed":
            False,
    }

    # -------------------------------------------------------------
    # H boundary authority
    # -------------------------------------------------------------

    for field in (
        "certified_cross_document_reasoning_input_inspected",
        "certified_cross_document_reasoning_input_preserved",
        "ontology_alignment_architecture_defined",
        "ontology_alignment_intake_validated",
        "ontology_scope_defined",
        "concept_vocabulary_extracted",
        "canonical_concept_normalization_performed",
        "ontology_mapping_performed",
        "ontology_alignment_performed",
        "ontology_integrity_verification_performed",
        "reasoning_integrity_preserved",
        "reasoning_provenance_preserved",
        "reasoning_outcomes_preserved",
        "uncertainty_preserved",
        "conflicts_preserved",
        "ambiguity_preserved",
    ):

        if boundaries.get(field) is not True:
            raise OntologyAlignmentError(
                f"Required 4.6.22H boundary is not True: {field}"
            )

    for field in (
        "ontology_provenance_built",
        "final_ontology_alignment_result_built",
        "full_ontology_alignment_certification_performed",
        "source_reasoning_modified",
        "source_profile_modified",
        "retrieval_payload_modified",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if boundaries.get(field) is not False:
            raise OntologyAlignmentError(
                f"Forbidden 4.6.22H boundary is not False: {field}"
            )

    return {
        "schema_version":
            "ontology_provenance_mapping_trace_result_v1",

        "version":
            ONTOLOGY_ALIGNMENT_VERSION,

        "phase":
            ONTOLOGY_ALIGNMENT_PHASE,

        "patch":
            "4.6.22I",

        "status":
            "ONTOLOGY_PROVENANCE_AND_MAPPING_TRACE_BUILT",

        "workspace_id":
            workspace_id,

        "ontology_alignment_architecture":
            deepcopy(
                dict(architecture)
            ),

        "ontology_vocabulary_scope":
            deepcopy(
                dict(ontology_scope)
            ),

        "canonical_concept_normalization":
            deepcopy(
                dict(normalization)
            ),

        "ontology_mapping_alignment":
            deepcopy(
                dict(alignment_package)
            ),

        "ontology_alignment_integrity_guard":
            deepcopy(
                dict(integrity_guard)
            ),

        "ontology_alignment_provenance":
            provenance_package,

        "certified_final_cross_document_reasoning_result":
            deepcopy(
                dict(certified_final)
            ),

        "source_integrity_guard_result":
            deepcopy(
                dict(guard_result)
            ),

        "processing_boundaries": {
            "certified_cross_document_reasoning_input_inspected":
                True,

            "certified_cross_document_reasoning_input_preserved":
                True,

            "ontology_alignment_architecture_defined":
                True,

            "ontology_alignment_intake_validated":
                True,

            "ontology_scope_defined":
                True,

            "concept_vocabulary_extracted":
                True,

            "canonical_concept_normalization_performed":
                True,

            "ontology_mapping_performed":
                True,

            "ontology_alignment_performed":
                True,

            "ontology_integrity_verification_performed":
                True,

            "ontology_provenance_built":
                True,

            "reasoning_integrity_preserved":
                True,

            "reasoning_provenance_preserved":
                True,

            "reasoning_outcomes_preserved":
                True,

            "uncertainty_preserved":
                True,

            "conflicts_preserved":
                True,

            "ambiguity_preserved":
                True,

            "final_ontology_alignment_result_built":
                False,

            "full_ontology_alignment_certification_performed":
                False,

            "source_reasoning_modified":
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

        "alignment_policy":
            "COMPLETE_ONTOLOGY_PROVENANCE_AND_MAPPING_TRACE_BUILT",

        "next_stage":
            "final_ontology_alignment_result",
    }


# =====================================================================
# PATCH 4.6.22J ? Final Ontology Alignment Result
# =====================================================================

def build_final_ontology_alignment_result_v1(
    provenance_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Assemble the final Ontology Alignment result from the verified
    A?I pipeline.

    J assembles and binds the complete result only.

    J does NOT:
    - perform new ontology mapping,
    - change alignment outcomes,
    - resolve ambiguity,
    - resolve conflicts,
    - certify the full 4.6.22 pipeline,
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
        raise OntologyAlignmentError(
            "provenance_result must be a mapping."
        )

    # -------------------------------------------------------------
    # Exact 4.6.22I lifecycle
    # -------------------------------------------------------------

    for field, expected in (
        (
            "schema_version",
            "ontology_provenance_mapping_trace_result_v1",
        ),
        (
            "version",
            ONTOLOGY_ALIGNMENT_VERSION,
        ),
        (
            "phase",
            ONTOLOGY_ALIGNMENT_PHASE,
        ),
        (
            "patch",
            "4.6.22I",
        ),
        (
            "status",
            "ONTOLOGY_PROVENANCE_AND_MAPPING_TRACE_BUILT",
        ),
        (
            "alignment_policy",
            "COMPLETE_ONTOLOGY_PROVENANCE_AND_MAPPING_TRACE_BUILT",
        ),
        (
            "next_stage",
            "final_ontology_alignment_result",
        ),
    ):

        if provenance_result.get(field) != expected:
            raise OntologyAlignmentError(
                f"Invalid 4.6.22I lifecycle field: {field}"
            )

    workspace_id = provenance_result.get(
        "workspace_id"
    )

    architecture = provenance_result.get(
        "ontology_alignment_architecture"
    )

    ontology_scope = provenance_result.get(
        "ontology_vocabulary_scope"
    )

    normalization = provenance_result.get(
        "canonical_concept_normalization"
    )

    alignment_package = provenance_result.get(
        "ontology_mapping_alignment"
    )

    integrity_guard = provenance_result.get(
        "ontology_alignment_integrity_guard"
    )

    provenance = provenance_result.get(
        "ontology_alignment_provenance"
    )

    certified_reasoning = provenance_result.get(
        "certified_final_cross_document_reasoning_result"
    )

    boundaries = provenance_result.get(
        "processing_boundaries"
    )

    for name, value in (
        (
            "ontology_alignment_architecture",
            architecture,
        ),
        (
            "ontology_vocabulary_scope",
            ontology_scope,
        ),
        (
            "canonical_concept_normalization",
            normalization,
        ),
        (
            "ontology_mapping_alignment",
            alignment_package,
        ),
        (
            "ontology_alignment_integrity_guard",
            integrity_guard,
        ),
        (
            "ontology_alignment_provenance",
            provenance,
        ),
        (
            "certified_final_cross_document_reasoning_result",
            certified_reasoning,
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
            raise OntologyAlignmentError(
                name + " is missing."
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
        raise OntologyAlignmentError(
            "Execution contract is missing."
        )

    if execution_contract.get(
        "4.6.22J"
    ) != "FINAL_ONTOLOGY_ALIGNMENT_RESULT":
        raise OntologyAlignmentError(
            "4.6.22J execution contract drifted."
        )

    if architecture.get(
        "next_owner"
    ) != "4.6.23_TRANSFER_LEARNING":
        raise OntologyAlignmentError(
            "Post-ontology owner drifted."
        )

    if architecture.get(
        "semantic_memory_owner"
    ) != "4.6.28_SEMANTIC_MEMORY":
        raise OntologyAlignmentError(
            "Semantic Memory ownership drifted."
        )

    # -------------------------------------------------------------
    # Scope authority
    # -------------------------------------------------------------

    ontology_scope_id = ontology_scope.get(
        "ontology_scope_id"
    )

    if not isinstance(
        ontology_scope_id,
        str,
    ) or not ontology_scope_id:
        raise OntologyAlignmentError(
            "Ontology scope identity is required."
        )

    # -------------------------------------------------------------
    # Cross-package identity bindings
    # -------------------------------------------------------------

    normalization_package_id = normalization.get(
        "normalization_package_id"
    )

    alignment_package_id = alignment_package.get(
        "alignment_package_id"
    )

    integrity_guard_id = integrity_guard.get(
        "integrity_guard_id"
    )

    provenance_id = provenance.get(
        "provenance_id"
    )

    for name, value in (
        (
            "normalization_package_id",
            normalization_package_id,
        ),
        (
            "alignment_package_id",
            alignment_package_id,
        ),
        (
            "integrity_guard_id",
            integrity_guard_id,
        ),
        (
            "provenance_id",
            provenance_id,
        ),
    ):

        if not isinstance(
            value,
            str,
        ) or not value:
            raise OntologyAlignmentError(
                name + " is required."
            )

    if normalization.get(
        "ontology_scope_id"
    ) != ontology_scope_id:
        raise OntologyAlignmentError(
            "Normalization/scope binding drifted."
        )

    if alignment_package.get(
        "ontology_scope_id"
    ) != ontology_scope_id:
        raise OntologyAlignmentError(
            "Alignment/scope binding drifted."
        )

    if alignment_package.get(
        "normalization_package_id"
    ) != normalization_package_id:
        raise OntologyAlignmentError(
            "Alignment/normalization binding drifted."
        )

    if integrity_guard.get(
        "ontology_scope_id"
    ) != ontology_scope_id:
        raise OntologyAlignmentError(
            "Guard/scope binding drifted."
        )

    if integrity_guard.get(
        "alignment_package_id"
    ) != alignment_package_id:
        raise OntologyAlignmentError(
            "Guard/alignment binding drifted."
        )

    if provenance.get(
        "ontology_scope_id"
    ) != ontology_scope_id:
        raise OntologyAlignmentError(
            "Provenance/scope binding drifted."
        )

    if provenance.get(
        "alignment_package_id"
    ) != alignment_package_id:
        raise OntologyAlignmentError(
            "Provenance/alignment binding drifted."
        )

    if provenance.get(
        "integrity_guard_id"
    ) != integrity_guard_id:
        raise OntologyAlignmentError(
            "Provenance/guard binding drifted."
        )

    if provenance.get(
        "normalization_package_id"
    ) != normalization_package_id:
        raise OntologyAlignmentError(
            "Provenance/normalization binding drifted."
        )

    # -------------------------------------------------------------
    # Alignment package authority
    # -------------------------------------------------------------

    alignments = alignment_package.get(
        "alignments"
    )

    confirmed_alignments = alignment_package.get(
        "confirmed_alignments"
    )

    unresolved_alignments = alignment_package.get(
        "unresolved_alignments"
    )

    conflicting_alignments = alignment_package.get(
        "conflicting_alignments"
    )

    for name, value in (
        (
            "alignments",
            alignments,
        ),
        (
            "confirmed_alignments",
            confirmed_alignments,
        ),
        (
            "unresolved_alignments",
            unresolved_alignments,
        ),
        (
            "conflicting_alignments",
            conflicting_alignments,
        ),
    ):

        if not isinstance(
            value,
            list,
        ):
            raise OntologyAlignmentError(
                name + " must be a list."
            )

    if len(
        alignments
    ) != alignment_package.get(
        "alignment_count"
    ):
        raise OntologyAlignmentError(
            "Alignment count drifted."
        )

    if len(
        confirmed_alignments
    ) != alignment_package.get(
        "confirmed_alignment_count"
    ):
        raise OntologyAlignmentError(
            "Confirmed alignment count drifted."
        )

    if len(
        unresolved_alignments
    ) != alignment_package.get(
        "unresolved_alignment_count"
    ):
        raise OntologyAlignmentError(
            "Unresolved alignment count drifted."
        )

    if len(
        conflicting_alignments
    ) != alignment_package.get(
        "conflict_alignment_count"
    ):
        raise OntologyAlignmentError(
            "Conflict alignment count drifted."
        )

    for field in (
        "ontology_mapping_performed",
        "ontology_alignment_performed",
        "evidence_bound",
        "ambiguity_preserved",
        "conflicts_preserved",
        "uncertainty_preserved",
        "source_reasoning_preserved",
        "source_vocabulary_preserved",
        "source_normalization_preserved",
        "source_profiles_preserved",
        "retrieval_payloads_preserved",
    ):

        if alignment_package.get(field) is not True:
            raise OntologyAlignmentError(
                f"Required alignment field is not True: {field}"
            )

    for field in (
        "unsupported_mapping_invented",
        "silent_resolution_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if alignment_package.get(field) is not False:
            raise OntologyAlignmentError(
                f"Forbidden alignment field is not False: {field}"
            )

    # -------------------------------------------------------------
    # Integrity guard authority
    # -------------------------------------------------------------

    if integrity_guard.get(
        "guard_status"
    ) != "VERIFIED":
        raise OntologyAlignmentError(
            "Ontology Alignment integrity guard is not verified."
        )

    if integrity_guard.get(
        "verified_alignment_count"
    ) != len(
        alignments
    ):
        raise OntologyAlignmentError(
            "Guard/alignment count drifted."
        )

    for field in (
        "alignment_ids_verified",
        "alignment_digests_verified",
        "alignment_package_identity_verified",
        "canonical_concept_identity_verified",
        "supported_alignment_families_verified",
        "alignment_statuses_verified",
        "confidence_states_verified",
        "uncertainty_states_verified",
        "evidence_traces_verified",
        "ambiguity_preserved",
        "conflicts_preserved",
        "uncertainty_preserved",
    ):

        if integrity_guard.get(field) is not True:
            raise OntologyAlignmentError(
                f"Required integrity field is not True: {field}"
            )

    for field in (
        "scope_violation_detected",
        "canonical_id_collision_detected",
        "unsupported_mapping_detected",
        "silent_resolution_detected",
        "source_reasoning_modified",
        "source_profile_modified",
        "retrieval_payload_modified",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if integrity_guard.get(field) is not False:
            raise OntologyAlignmentError(
                f"Forbidden integrity field is not False: {field}"
            )

    # -------------------------------------------------------------
    # Provenance authority
    # -------------------------------------------------------------

    if provenance.get(
        "provenance_schema"
    ) != "ontology_alignment_provenance_v1":
        raise OntologyAlignmentError(
            "Ontology provenance schema drifted."
        )

    if provenance.get(
        "provenance_version"
    ) != "v1":
        raise OntologyAlignmentError(
            "Ontology provenance version drifted."
        )

    traces = provenance.get(
        "mapping_traces"
    )

    if not isinstance(
        traces,
        list,
    ):
        raise OntologyAlignmentError(
            "Ontology mapping traces must be a list."
        )

    if len(
        traces
    ) != provenance.get(
        "trace_count"
    ):
        raise OntologyAlignmentError(
            "Ontology provenance trace count drifted."
        )

    if len(
        traces
    ) != len(
        alignments
    ):
        raise OntologyAlignmentError(
            "Each alignment requires exactly one provenance trace."
        )

    for field in (
        "source_document_lineage_complete",
        "source_reasoning_lineage_complete",
        "surface_form_lineage_complete",
        "canonical_mapping_lineage_complete",
        "ontology_relationship_lineage_complete",
        "ambiguity_trace_complete",
        "conflict_trace_complete",
        "evidence_trace_complete",
        "alignment_identity_trace_complete",
        "integrity_guard_trace_complete",
        "source_reasoning_preserved",
        "source_profiles_preserved",
        "retrieval_payloads_preserved",
        "ambiguity_preserved",
        "conflicts_preserved",
        "uncertainty_preserved",
    ):

        if provenance.get(field) is not True:
            raise OntologyAlignmentError(
                f"Required provenance field is not True: {field}"
            )

    for field in (
        "new_mapping_created",
        "mapping_status_modified",
        "ambiguity_resolved",
        "conflict_resolved",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if provenance.get(field) is not False:
            raise OntologyAlignmentError(
                f"Forbidden provenance field is not False: {field}"
            )

    # -------------------------------------------------------------
    # Final ontology result body
    # -------------------------------------------------------------

    canonical_concepts = normalization.get(
        "canonical_concepts"
    )

    if not isinstance(
        canonical_concepts,
        list,
    ) or not canonical_concepts:
        raise OntologyAlignmentError(
            "Canonical concepts are required."
        )

    alignment_ids = sorted(
        item[
            "ontology_alignment_id"
        ]
        for item in alignments
    )

    canonical_concept_ids = sorted(
        item[
            "canonical_concept_id"
        ]
        for item in canonical_concepts
    )

    ambiguity_registry = integrity_guard.get(
        "ambiguity_registry",
        [],
    )

    conflict_registry = integrity_guard.get(
        "conflict_registry",
        [],
    )

    multi_candidate_registry = integrity_guard.get(
        "multi_candidate_registry",
        [],
    )

    final_material = {
        "workspace_id":
            workspace_id,

        "ontology_scope_id":
            ontology_scope_id,

        "normalization_package_id":
            normalization_package_id,

        "alignment_package_id":
            alignment_package_id,

        "integrity_guard_id":
            integrity_guard_id,

        "provenance_id":
            provenance_id,

        "canonical_concept_ids":
            canonical_concept_ids,

        "alignment_ids":
            alignment_ids,

        "confirmed_alignment_count":
            len(
                confirmed_alignments
            ),

        "unresolved_alignment_count":
            len(
                unresolved_alignments
            ),

        "conflict_alignment_count":
            len(
                conflicting_alignments
            ),

        "ambiguity_count":
            len(
                ambiguity_registry
            ),

        "ontology_conflict_count":
            len(
                conflict_registry
            ),

        "multi_candidate_count":
            len(
                multi_candidate_registry
            ),
    }

    final_raw = json.dumps(
        final_material,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    final_digest = hashlib.sha256(
        final_raw.encode(
            "utf-8"
        )
    ).hexdigest()

    final_result_id = (
        "ontfinal:v1:"
        + final_digest[:32]
    )

    final_result = {
        "final_result_schema":
            "final_ontology_alignment_result_v1",

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

        "ontology_scope_id":
            ontology_scope_id,

        "normalization_package_id":
            normalization_package_id,

        "alignment_package_id":
            alignment_package_id,

        "integrity_guard_id":
            integrity_guard_id,

        "provenance_id":
            provenance_id,

        "canonical_concept_count":
            len(
                canonical_concepts
            ),

        "canonical_concepts":
            deepcopy(
                canonical_concepts
            ),

        "alignment_count":
            len(
                alignments
            ),

        "alignments":
            deepcopy(
                alignments
            ),

        "confirmed_alignment_count":
            len(
                confirmed_alignments
            ),

        "confirmed_alignments":
            deepcopy(
                confirmed_alignments
            ),

        "unresolved_alignment_count":
            len(
                unresolved_alignments
            ),

        "unresolved_alignments":
            deepcopy(
                unresolved_alignments
            ),

        "conflict_alignment_count":
            len(
                conflicting_alignments
            ),

        "conflicting_alignments":
            deepcopy(
                conflicting_alignments
            ),

        "ambiguity_count":
            len(
                ambiguity_registry
            ),

        "ambiguity_registry":
            deepcopy(
                ambiguity_registry
            ),

        "ontology_conflict_count":
            len(
                conflict_registry
            ),

        "ontology_conflict_registry":
            deepcopy(
                conflict_registry
            ),

        "multi_candidate_count":
            len(
                multi_candidate_registry
            ),

        "multi_candidate_registry":
            deepcopy(
                multi_candidate_registry
            ),

        "mapping_trace_count":
            len(
                traces
            ),

        "mapping_traces":
            deepcopy(
                traces
            ),

        "ontology_mapping_performed":
            True,

        "ontology_alignment_performed":
            True,

        "ontology_integrity_verified":
            True,

        "ontology_provenance_complete":
            True,

        "alignment_outcomes_preserved":
            True,

        "ambiguity_preserved":
            True,

        "conflicts_preserved":
            True,

        "uncertainty_preserved":
            True,

        "source_reasoning_preserved":
            True,

        "source_profiles_preserved":
            True,

        "retrieval_payloads_preserved":
            True,

        "unsupported_mapping_invented":
            False,

        "silent_resolution_performed":
            False,

        "new_mapping_created_during_finalization":
            False,

        "mapping_status_modified_during_finalization":
            False,

        "semantic_memory_written":
            False,

        "linking_decisions_performed":
            False,

        "full_ontology_alignment_certified":
            False,

        "certification_status":
            "PENDING_4.6.22K",

        "certification_owner":
            "4.6.22K_FULL_ONTOLOGY_ALIGNMENT_HARD_CERTIFICATION",

        "next_owner_after_certification":
            "4.6.23_TRANSFER_LEARNING",

        "semantic_memory_owner":
            "4.6.28_SEMANTIC_MEMORY",
    }

    # -------------------------------------------------------------
    # I boundary authority
    # -------------------------------------------------------------

    for field in (
        "certified_cross_document_reasoning_input_inspected",
        "certified_cross_document_reasoning_input_preserved",
        "ontology_alignment_architecture_defined",
        "ontology_alignment_intake_validated",
        "ontology_scope_defined",
        "concept_vocabulary_extracted",
        "canonical_concept_normalization_performed",
        "ontology_mapping_performed",
        "ontology_alignment_performed",
        "ontology_integrity_verification_performed",
        "ontology_provenance_built",
        "reasoning_integrity_preserved",
        "reasoning_provenance_preserved",
        "reasoning_outcomes_preserved",
        "uncertainty_preserved",
        "conflicts_preserved",
        "ambiguity_preserved",
    ):

        if boundaries.get(field) is not True:
            raise OntologyAlignmentError(
                f"Required 4.6.22I boundary is not True: {field}"
            )

    for field in (
        "final_ontology_alignment_result_built",
        "full_ontology_alignment_certification_performed",
        "source_reasoning_modified",
        "source_profile_modified",
        "retrieval_payload_modified",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if boundaries.get(field) is not False:
            raise OntologyAlignmentError(
                f"Forbidden 4.6.22I boundary is not False: {field}"
            )

    return {
        "schema_version":
            "final_ontology_alignment_result_envelope_v1",

        "version":
            ONTOLOGY_ALIGNMENT_VERSION,

        "phase":
            ONTOLOGY_ALIGNMENT_PHASE,

        "patch":
            "4.6.22J",

        "status":
            "FINAL_ONTOLOGY_ALIGNMENT_RESULT_BUILT",

        "workspace_id":
            workspace_id,

        "final_ontology_alignment_result":
            final_result,

        "ontology_alignment_architecture":
            deepcopy(
                dict(architecture)
            ),

        "ontology_vocabulary_scope":
            deepcopy(
                dict(ontology_scope)
            ),

        "canonical_concept_normalization":
            deepcopy(
                dict(normalization)
            ),

        "ontology_mapping_alignment":
            deepcopy(
                dict(alignment_package)
            ),

        "ontology_alignment_integrity_guard":
            deepcopy(
                dict(integrity_guard)
            ),

        "ontology_alignment_provenance":
            deepcopy(
                dict(provenance)
            ),

        "certified_final_cross_document_reasoning_result":
            deepcopy(
                dict(certified_reasoning)
            ),

        "source_provenance_result":
            deepcopy(
                dict(provenance_result)
            ),

        "processing_boundaries": {
            "certified_cross_document_reasoning_input_inspected":
                True,

            "certified_cross_document_reasoning_input_preserved":
                True,

            "ontology_alignment_architecture_defined":
                True,

            "ontology_alignment_intake_validated":
                True,

            "ontology_scope_defined":
                True,

            "concept_vocabulary_extracted":
                True,

            "canonical_concept_normalization_performed":
                True,

            "ontology_mapping_performed":
                True,

            "ontology_alignment_performed":
                True,

            "ontology_integrity_verification_performed":
                True,

            "ontology_provenance_built":
                True,

            "final_ontology_alignment_result_built":
                True,

            "reasoning_integrity_preserved":
                True,

            "reasoning_provenance_preserved":
                True,

            "reasoning_outcomes_preserved":
                True,

            "uncertainty_preserved":
                True,

            "conflicts_preserved":
                True,

            "ambiguity_preserved":
                True,

            "full_ontology_alignment_certification_performed":
                False,

            "source_reasoning_modified":
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

        "alignment_policy":
            "FINAL_ONTOLOGY_ALIGNMENT_RESULT_READY_FOR_CERTIFICATION",

        "next_stage":
            "full_ontology_alignment_hard_certification",
    }


# =====================================================================
# PATCH 4.6.22K ? Full Ontology Alignment Hard Certification
# =====================================================================

def certify_full_ontology_alignment_v1(
    final_envelope: dict[str, Any],
) -> dict[str, Any]:
    """
    Hard-certify the complete 4.6.22 Ontology Alignment pipeline.

    K is the sole certification authority for 4.6.22.

    It verifies:
    - J lifecycle,
    - final result identity/digest,
    - all cross-package identity bindings,
    - ontology mapping outcomes,
    - ambiguity/conflict preservation,
    - integrity guard,
    - provenance completeness,
    - A?J boundaries,
    - source immutability,
    - downstream ownership.

    K does not perform new alignment, write Semantic Memory,
    or make linking decisions.
    """

    from collections.abc import Mapping
    from copy import deepcopy
    import hashlib
    import json

    if not isinstance(
        final_envelope,
        Mapping,
    ):
        raise OntologyAlignmentError(
            "final_envelope must be a mapping."
        )

    # -------------------------------------------------------------
    # Exact 4.6.22J lifecycle
    # -------------------------------------------------------------

    for field, expected in (
        (
            "schema_version",
            "final_ontology_alignment_result_envelope_v1",
        ),
        (
            "version",
            ONTOLOGY_ALIGNMENT_VERSION,
        ),
        (
            "phase",
            ONTOLOGY_ALIGNMENT_PHASE,
        ),
        (
            "patch",
            "4.6.22J",
        ),
        (
            "status",
            "FINAL_ONTOLOGY_ALIGNMENT_RESULT_BUILT",
        ),
        (
            "alignment_policy",
            "FINAL_ONTOLOGY_ALIGNMENT_RESULT_READY_FOR_CERTIFICATION",
        ),
        (
            "next_stage",
            "full_ontology_alignment_hard_certification",
        ),
    ):

        if final_envelope.get(field) != expected:
            raise OntologyAlignmentError(
                f"Invalid 4.6.22J lifecycle field: {field}"
            )

    workspace_id = final_envelope.get(
        "workspace_id"
    )

    final_result = final_envelope.get(
        "final_ontology_alignment_result"
    )

    architecture = final_envelope.get(
        "ontology_alignment_architecture"
    )

    ontology_scope = final_envelope.get(
        "ontology_vocabulary_scope"
    )

    normalization = final_envelope.get(
        "canonical_concept_normalization"
    )

    alignment_package = final_envelope.get(
        "ontology_mapping_alignment"
    )

    integrity_guard = final_envelope.get(
        "ontology_alignment_integrity_guard"
    )

    provenance = final_envelope.get(
        "ontology_alignment_provenance"
    )

    certified_reasoning = final_envelope.get(
        "certified_final_cross_document_reasoning_result"
    )

    boundaries = final_envelope.get(
        "processing_boundaries"
    )

    for name, value in (
        (
            "final_ontology_alignment_result",
            final_result,
        ),
        (
            "ontology_alignment_architecture",
            architecture,
        ),
        (
            "ontology_vocabulary_scope",
            ontology_scope,
        ),
        (
            "canonical_concept_normalization",
            normalization,
        ),
        (
            "ontology_mapping_alignment",
            alignment_package,
        ),
        (
            "ontology_alignment_integrity_guard",
            integrity_guard,
        ),
        (
            "ontology_alignment_provenance",
            provenance,
        ),
        (
            "certified_final_cross_document_reasoning_result",
            certified_reasoning,
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
            raise OntologyAlignmentError(
                name + " is missing."
            )

    # -------------------------------------------------------------
    # Architecture certification authority
    # -------------------------------------------------------------

    execution = architecture.get(
        "execution_contract"
    )

    if not isinstance(
        execution,
        Mapping,
    ):
        raise OntologyAlignmentError(
            "Execution contract is missing."
        )

    if execution.get(
        "4.6.22K"
    ) != "FULL_ONTOLOGY_ALIGNMENT_HARD_CERTIFICATION":
        raise OntologyAlignmentError(
            "4.6.22K execution contract drifted."
        )

    if architecture.get(
        "owner"
    ) != "4.6.22_ONTOLOGY_ALIGNMENT":
        raise OntologyAlignmentError(
            "Ontology Alignment owner drifted."
        )

    if architecture.get(
        "source_owner"
    ) != "4.6.21_CROSS_DOCUMENT_REASONING":
        raise OntologyAlignmentError(
            "Ontology Alignment source owner drifted."
        )

    if architecture.get(
        "next_owner"
    ) != "4.6.23_TRANSFER_LEARNING":
        raise OntologyAlignmentError(
            "Transfer Learning ownership drifted."
        )

    if architecture.get(
        "semantic_memory_owner"
    ) != "4.6.28_SEMANTIC_MEMORY":
        raise OntologyAlignmentError(
            "Semantic Memory ownership drifted."
        )

    # -------------------------------------------------------------
    # Final result lifecycle
    # -------------------------------------------------------------

    for field, expected in (
        (
            "final_result_schema",
            "final_ontology_alignment_result_v1",
        ),
        (
            "final_result_version",
            "v1",
        ),
        (
            "workspace_id",
            workspace_id,
        ),
        (
            "ontology_mapping_performed",
            True,
        ),
        (
            "ontology_alignment_performed",
            True,
        ),
        (
            "ontology_integrity_verified",
            True,
        ),
        (
            "ontology_provenance_complete",
            True,
        ),
        (
            "alignment_outcomes_preserved",
            True,
        ),
        (
            "ambiguity_preserved",
            True,
        ),
        (
            "conflicts_preserved",
            True,
        ),
        (
            "uncertainty_preserved",
            True,
        ),
        (
            "source_reasoning_preserved",
            True,
        ),
        (
            "source_profiles_preserved",
            True,
        ),
        (
            "retrieval_payloads_preserved",
            True,
        ),
        (
            "unsupported_mapping_invented",
            False,
        ),
        (
            "silent_resolution_performed",
            False,
        ),
        (
            "new_mapping_created_during_finalization",
            False,
        ),
        (
            "mapping_status_modified_during_finalization",
            False,
        ),
        (
            "semantic_memory_written",
            False,
        ),
        (
            "linking_decisions_performed",
            False,
        ),
        (
            "full_ontology_alignment_certified",
            False,
        ),
        (
            "certification_status",
            "PENDING_4.6.22K",
        ),
        (
            "certification_owner",
            "4.6.22K_FULL_ONTOLOGY_ALIGNMENT_HARD_CERTIFICATION",
        ),
        (
            "next_owner_after_certification",
            "4.6.23_TRANSFER_LEARNING",
        ),
        (
            "semantic_memory_owner",
            "4.6.28_SEMANTIC_MEMORY",
        ),
    ):

        if final_result.get(field) != expected:
            raise OntologyAlignmentError(
                f"Final ontology result field drifted: {field}"
            )

    # -------------------------------------------------------------
    # Cross-package identity bindings
    # -------------------------------------------------------------

    ontology_scope_id = final_result.get(
        "ontology_scope_id"
    )

    normalization_package_id = final_result.get(
        "normalization_package_id"
    )

    alignment_package_id = final_result.get(
        "alignment_package_id"
    )

    integrity_guard_id = final_result.get(
        "integrity_guard_id"
    )

    provenance_id = final_result.get(
        "provenance_id"
    )

    if ontology_scope.get(
        "ontology_scope_id"
    ) != ontology_scope_id:
        raise OntologyAlignmentError(
            "Final/scope identity binding drifted."
        )

    if normalization.get(
        "normalization_package_id"
    ) != normalization_package_id:
        raise OntologyAlignmentError(
            "Final/normalization identity binding drifted."
        )

    if alignment_package.get(
        "alignment_package_id"
    ) != alignment_package_id:
        raise OntologyAlignmentError(
            "Final/alignment identity binding drifted."
        )

    if integrity_guard.get(
        "integrity_guard_id"
    ) != integrity_guard_id:
        raise OntologyAlignmentError(
            "Final/guard identity binding drifted."
        )

    if provenance.get(
        "provenance_id"
    ) != provenance_id:
        raise OntologyAlignmentError(
            "Final/provenance identity binding drifted."
        )

    if normalization.get(
        "ontology_scope_id"
    ) != ontology_scope_id:
        raise OntologyAlignmentError(
            "Normalization/scope identity binding drifted."
        )

    if alignment_package.get(
        "ontology_scope_id"
    ) != ontology_scope_id:
        raise OntologyAlignmentError(
            "Alignment/scope identity binding drifted."
        )

    if alignment_package.get(
        "normalization_package_id"
    ) != normalization_package_id:
        raise OntologyAlignmentError(
            "Alignment/normalization identity binding drifted."
        )

    if integrity_guard.get(
        "ontology_scope_id"
    ) != ontology_scope_id:
        raise OntologyAlignmentError(
            "Guard/scope identity binding drifted."
        )

    if integrity_guard.get(
        "alignment_package_id"
    ) != alignment_package_id:
        raise OntologyAlignmentError(
            "Guard/alignment identity binding drifted."
        )

    if provenance.get(
        "ontology_scope_id"
    ) != ontology_scope_id:
        raise OntologyAlignmentError(
            "Provenance/scope identity binding drifted."
        )

    if provenance.get(
        "alignment_package_id"
    ) != alignment_package_id:
        raise OntologyAlignmentError(
            "Provenance/alignment identity binding drifted."
        )

    if provenance.get(
        "integrity_guard_id"
    ) != integrity_guard_id:
        raise OntologyAlignmentError(
            "Provenance/guard identity binding drifted."
        )

    if provenance.get(
        "normalization_package_id"
    ) != normalization_package_id:
        raise OntologyAlignmentError(
            "Provenance/normalization identity binding drifted."
        )

    # -------------------------------------------------------------
    # Counts / collections
    # -------------------------------------------------------------

    canonical_concepts = final_result.get(
        "canonical_concepts"
    )

    alignments = final_result.get(
        "alignments"
    )

    confirmed = final_result.get(
        "confirmed_alignments"
    )

    unresolved = final_result.get(
        "unresolved_alignments"
    )

    conflicts = final_result.get(
        "conflicting_alignments"
    )

    ambiguities = final_result.get(
        "ambiguity_registry"
    )

    conflict_registry = final_result.get(
        "ontology_conflict_registry"
    )

    multi_candidates = final_result.get(
        "multi_candidate_registry"
    )

    traces = final_result.get(
        "mapping_traces"
    )

    for name, value in (
        ("canonical_concepts", canonical_concepts),
        ("alignments", alignments),
        ("confirmed_alignments", confirmed),
        ("unresolved_alignments", unresolved),
        ("conflicting_alignments", conflicts),
        ("ambiguity_registry", ambiguities),
        ("ontology_conflict_registry", conflict_registry),
        ("multi_candidate_registry", multi_candidates),
        ("mapping_traces", traces),
    ):

        if not isinstance(
            value,
            list,
        ):
            raise OntologyAlignmentError(
                name + " must be a list."
            )

    for count_field, collection in (
        (
            "canonical_concept_count",
            canonical_concepts,
        ),
        (
            "alignment_count",
            alignments,
        ),
        (
            "confirmed_alignment_count",
            confirmed,
        ),
        (
            "unresolved_alignment_count",
            unresolved,
        ),
        (
            "conflict_alignment_count",
            conflicts,
        ),
        (
            "ambiguity_count",
            ambiguities,
        ),
        (
            "ontology_conflict_count",
            conflict_registry,
        ),
        (
            "multi_candidate_count",
            multi_candidates,
        ),
        (
            "mapping_trace_count",
            traces,
        ),
    ):

        if final_result.get(
            count_field
        ) != len(
            collection
        ):
            raise OntologyAlignmentError(
                f"Final collection count drifted: {count_field}"
            )

    if len(
        traces
    ) != len(
        alignments
    ):
        raise OntologyAlignmentError(
            "Every final alignment must have one provenance trace."
        )

    # -------------------------------------------------------------
    # Alignment category integrity
    # -------------------------------------------------------------

    all_alignment_ids = {
        item.get(
            "ontology_alignment_id"
        )
        for item in alignments
    }

    if None in all_alignment_ids:
        raise OntologyAlignmentError(
            "Alignment identity is missing."
        )

    if len(
        all_alignment_ids
    ) != len(
        alignments
    ):
        raise OntologyAlignmentError(
            "Duplicate final alignment identity detected."
        )

    confirmed_ids = {
        item.get(
            "ontology_alignment_id"
        )
        for item in confirmed
    }

    unresolved_ids = {
        item.get(
            "ontology_alignment_id"
        )
        for item in unresolved
    }

    conflict_ids = {
        item.get(
            "ontology_alignment_id"
        )
        for item in conflicts
    }

    expected_confirmed_ids = {
        item.get(
            "ontology_alignment_id"
        )
        for item in alignments
        if item.get(
            "alignment_status"
        ) == "CONFIRMED"
    }

    expected_unresolved_ids = {
        item.get(
            "ontology_alignment_id"
        )
        for item in alignments
        if item.get(
            "alignment_status"
        ) == "UNRESOLVED"
    }

    expected_conflict_ids = {
        item.get(
            "ontology_alignment_id"
        )
        for item in alignments
        if item.get(
            "alignment_status"
        ) == "CONFLICT_DETECTED"
    }

    if confirmed_ids != expected_confirmed_ids:
        raise OntologyAlignmentError(
            "Final confirmed registry drifted."
        )

    if unresolved_ids != expected_unresolved_ids:
        raise OntologyAlignmentError(
            "Final unresolved registry drifted."
        )

    if conflict_ids != expected_conflict_ids:
        raise OntologyAlignmentError(
            "Final conflict registry drifted."
        )

    trace_alignment_ids = {
        item.get(
            "ontology_alignment_id"
        )
        for item in traces
    }

    if trace_alignment_ids != all_alignment_ids:
        raise OntologyAlignmentError(
            "Final alignment/provenance trace binding drifted."
        )

    # -------------------------------------------------------------
    # Ambiguity and conflict preservation
    # -------------------------------------------------------------

    for item in ambiguities:

        if item.get(
            "ambiguity_status"
        ) != "OPEN":
            raise OntologyAlignmentError(
                "Final ambiguity must remain OPEN."
            )

        if item.get(
            "auto_resolved"
        ) is not False:
            raise OntologyAlignmentError(
                "Final ambiguity was auto-resolved."
            )

    for item in conflict_registry:

        if item.get(
            "conflict_status"
        ) != "OPEN":
            raise OntologyAlignmentError(
                "Final ontology conflict must remain OPEN."
            )

        if item.get(
            "silently_resolved"
        ) is not False:
            raise OntologyAlignmentError(
                "Final ontology conflict was silently resolved."
            )

    # -------------------------------------------------------------
    # Guard certification
    # -------------------------------------------------------------

    if integrity_guard.get(
        "guard_status"
    ) != "VERIFIED":
        raise OntologyAlignmentError(
            "Integrity guard is not verified."
        )

    for field in (
        "alignment_ids_verified",
        "alignment_digests_verified",
        "alignment_package_identity_verified",
        "canonical_concept_identity_verified",
        "supported_alignment_families_verified",
        "alignment_statuses_verified",
        "confidence_states_verified",
        "uncertainty_states_verified",
        "evidence_traces_verified",
        "ambiguity_preserved",
        "conflicts_preserved",
        "uncertainty_preserved",
    ):

        if integrity_guard.get(field) is not True:
            raise OntologyAlignmentError(
                f"Required guard certification field is not True: {field}"
            )

    for field in (
        "scope_violation_detected",
        "canonical_id_collision_detected",
        "unsupported_mapping_detected",
        "silent_resolution_detected",
        "source_reasoning_modified",
        "source_profile_modified",
        "retrieval_payload_modified",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if integrity_guard.get(field) is not False:
            raise OntologyAlignmentError(
                f"Forbidden guard certification field is not False: {field}"
            )

    # -------------------------------------------------------------
    # Provenance certification
    # -------------------------------------------------------------

    for field in (
        "source_document_lineage_complete",
        "source_reasoning_lineage_complete",
        "surface_form_lineage_complete",
        "canonical_mapping_lineage_complete",
        "ontology_relationship_lineage_complete",
        "ambiguity_trace_complete",
        "conflict_trace_complete",
        "evidence_trace_complete",
        "alignment_identity_trace_complete",
        "integrity_guard_trace_complete",
        "source_reasoning_preserved",
        "source_profiles_preserved",
        "retrieval_payloads_preserved",
        "ambiguity_preserved",
        "conflicts_preserved",
        "uncertainty_preserved",
    ):

        if provenance.get(field) is not True:
            raise OntologyAlignmentError(
                f"Required provenance certification field is not True: {field}"
            )

    for field in (
        "new_mapping_created",
        "mapping_status_modified",
        "ambiguity_resolved",
        "conflict_resolved",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if provenance.get(field) is not False:
            raise OntologyAlignmentError(
                f"Forbidden provenance certification field is not False: {field}"
            )

    # -------------------------------------------------------------
    # Recompute exact J final identity
    # -------------------------------------------------------------

    final_material = {
        "workspace_id":
            workspace_id,

        "ontology_scope_id":
            ontology_scope_id,

        "normalization_package_id":
            normalization_package_id,

        "alignment_package_id":
            alignment_package_id,

        "integrity_guard_id":
            integrity_guard_id,

        "provenance_id":
            provenance_id,

        "canonical_concept_ids":
            sorted(
                item[
                    "canonical_concept_id"
                ]
                for item in canonical_concepts
            ),

        "alignment_ids":
            sorted(
                item[
                    "ontology_alignment_id"
                ]
                for item in alignments
            ),

        "confirmed_alignment_count":
            len(
                confirmed
            ),

        "unresolved_alignment_count":
            len(
                unresolved
            ),

        "conflict_alignment_count":
            len(
                conflicts
            ),

        "ambiguity_count":
            len(
                ambiguities
            ),

        "ontology_conflict_count":
            len(
                conflict_registry
            ),

        "multi_candidate_count":
            len(
                multi_candidates
            ),
    }

    final_raw = json.dumps(
        final_material,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    expected_final_digest = hashlib.sha256(
        final_raw.encode(
            "utf-8"
        )
    ).hexdigest()

    expected_final_id = (
        "ontfinal:v1:"
        + expected_final_digest[:32]
    )

    if final_result.get(
        "final_result_digest"
    ) != expected_final_digest:
        raise OntologyAlignmentError(
            "Final ontology result digest verification failed."
        )

    if final_result.get(
        "final_result_id"
    ) != expected_final_id:
        raise OntologyAlignmentError(
            "Final ontology result ID verification failed."
        )

    # -------------------------------------------------------------
    # J boundary authority
    # -------------------------------------------------------------

    for field in (
        "certified_cross_document_reasoning_input_inspected",
        "certified_cross_document_reasoning_input_preserved",
        "ontology_alignment_architecture_defined",
        "ontology_alignment_intake_validated",
        "ontology_scope_defined",
        "concept_vocabulary_extracted",
        "canonical_concept_normalization_performed",
        "ontology_mapping_performed",
        "ontology_alignment_performed",
        "ontology_integrity_verification_performed",
        "ontology_provenance_built",
        "final_ontology_alignment_result_built",
        "reasoning_integrity_preserved",
        "reasoning_provenance_preserved",
        "reasoning_outcomes_preserved",
        "uncertainty_preserved",
        "conflicts_preserved",
        "ambiguity_preserved",
    ):

        if boundaries.get(field) is not True:
            raise OntologyAlignmentError(
                f"Required 4.6.22J boundary is not True: {field}"
            )

    for field in (
        "full_ontology_alignment_certification_performed",
        "source_reasoning_modified",
        "source_profile_modified",
        "retrieval_payload_modified",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if boundaries.get(field) is not False:
            raise OntologyAlignmentError(
                f"Forbidden 4.6.22J boundary is not False: {field}"
            )

    # -------------------------------------------------------------
    # Certified final copy
    # -------------------------------------------------------------

    certified_final = deepcopy(
        dict(final_result)
    )

    certified_final[
        "full_ontology_alignment_certified"
    ] = True

    certified_final[
        "certification_status"
    ] = "CERTIFIED"

    certified_final[
        "certification_patch"
    ] = "4.6.22K"

    certified_final[
        "next_owner"
    ] = "4.6.23_TRANSFER_LEARNING"

    certified_final[
        "semantic_memory_owner"
    ] = "4.6.28_SEMANTIC_MEMORY"

    # -------------------------------------------------------------
    # Certification package identity
    # -------------------------------------------------------------

    certification_material = {
        "workspace_id":
            workspace_id,

        "source_final_result_id":
            final_result[
                "final_result_id"
            ],

        "source_final_result_digest":
            final_result[
                "final_result_digest"
            ],

        "ontology_scope_id":
            ontology_scope_id,

        "normalization_package_id":
            normalization_package_id,

        "alignment_package_id":
            alignment_package_id,

        "integrity_guard_id":
            integrity_guard_id,

        "provenance_id":
            provenance_id,

        "next_owner":
            "4.6.23_TRANSFER_LEARNING",
    }

    certification_raw = json.dumps(
        certification_material,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    certification_digest = hashlib.sha256(
        certification_raw.encode(
            "utf-8"
        )
    ).hexdigest()

    certification_id = (
        "ontcert:v1:"
        + certification_digest[:32]
    )

    certification = {
        "certification_schema":
            "full_ontology_alignment_certification_v1",

        "certification_version":
            "v1",

        "certification_id":
            certification_id,

        "certification_digest":
            certification_digest,

        "certification_digest_algorithm":
            "SHA256",

        "certification_phase":
            "4.6.22",

        "certification_patch":
            "4.6.22K",

        "certification_status":
            "CERTIFIED",

        "certification_scope":
            "FULL_ONTOLOGY_ALIGNMENT_PIPELINE",

        "source_patch":
            "4.6.22J",

        "source_final_result_id":
            final_result[
                "final_result_id"
            ],

        "source_final_result_digest":
            final_result[
                "final_result_digest"
            ],

        "ontology_scope_id":
            ontology_scope_id,

        "normalization_package_id":
            normalization_package_id,

        "alignment_package_id":
            alignment_package_id,

        "integrity_guard_id":
            integrity_guard_id,

        "provenance_id":
            provenance_id,

        "all_pipeline_identity_bindings_verified":
            True,

        "final_result_digest_verified":
            True,

        "final_result_id_verified":
            True,

        "ontology_mapping_verified":
            True,

        "ontology_alignment_verified":
            True,

        "ontology_integrity_verified":
            True,

        "ontology_provenance_verified":
            True,

        "alignment_outcomes_preserved":
            True,

        "ambiguity_preserved":
            True,

        "conflicts_preserved":
            True,

        "uncertainty_preserved":
            True,

        "source_reasoning_preserved":
            True,

        "source_profiles_preserved":
            True,

        "retrieval_payloads_preserved":
            True,

        "unsupported_mapping_invented":
            False,

        "silent_resolution_performed":
            False,

        "semantic_memory_written":
            False,

        "linking_decisions_performed":
            False,

        "transfer_learning_ready":
            True,

        "next_owner":
            "4.6.23_TRANSFER_LEARNING",

        "semantic_memory_owner":
            "4.6.28_SEMANTIC_MEMORY",
    }

    return {
        "schema_version":
            "certified_ontology_alignment_result_v1",

        "version":
            ONTOLOGY_ALIGNMENT_VERSION,

        "phase":
            ONTOLOGY_ALIGNMENT_PHASE,

        "patch":
            "4.6.22K",

        "status":
            "ONTOLOGY_ALIGNMENT_CERTIFIED",

        "workspace_id":
            workspace_id,

        "certified_final_ontology_alignment_result":
            certified_final,

        "full_ontology_alignment_certification":
            certification,

        "source_final_result_envelope":
            deepcopy(
                dict(final_envelope)
            ),

        "processing_boundaries": {
            "certified_cross_document_reasoning_input_inspected":
                True,

            "certified_cross_document_reasoning_input_preserved":
                True,

            "ontology_alignment_architecture_defined":
                True,

            "ontology_alignment_intake_validated":
                True,

            "ontology_scope_defined":
                True,

            "concept_vocabulary_extracted":
                True,

            "canonical_concept_normalization_performed":
                True,

            "ontology_mapping_performed":
                True,

            "ontology_alignment_performed":
                True,

            "ontology_integrity_verification_performed":
                True,

            "ontology_provenance_built":
                True,

            "final_ontology_alignment_result_built":
                True,

            "full_ontology_alignment_certification_performed":
                True,

            "reasoning_integrity_preserved":
                True,

            "reasoning_provenance_preserved":
                True,

            "reasoning_outcomes_preserved":
                True,

            "uncertainty_preserved":
                True,

            "conflicts_preserved":
                True,

            "ambiguity_preserved":
                True,

            "source_reasoning_modified":
                False,

            "source_profile_modified":
                False,

            "retrieval_payload_modified":
                False,

            "unsupported_mapping_invented":
                False,

            "silent_resolution_performed":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,
        },

        "alignment_policy":
            "FULL_ONTOLOGY_ALIGNMENT_CERTIFIED",

        "next_stage":
            "transfer_learning",
    }

