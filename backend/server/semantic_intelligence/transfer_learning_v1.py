from __future__ import annotations

import copy

import hashlib
import json

from copy import deepcopy
from typing import Any


TRANSFER_LEARNING_VERSION = "transfer_learning_v1"
TRANSFER_LEARNING_PHASE = "4.6.23"


class TransferLearningError(Exception):
    """Raised when Transfer Learning contract validation fails."""


# =====================================================================
# PATCH 4.6.23A ? Certified 4.6.22K Input Contract Inspection
# =====================================================================

def inspect_certified_ontology_alignment_input_v1(
    certified_ontology_result: dict[str, Any],
) -> dict[str, Any]:

    from collections.abc import Mapping

    if not isinstance(
        certified_ontology_result,
        Mapping,
    ):
        raise TransferLearningError(
            "certified_ontology_result must be a mapping."
        )

    # -------------------------------------------------------------
    # Exact 4.6.22K lifecycle
    # -------------------------------------------------------------

    for field, expected in (
        (
            "schema_version",
            "certified_ontology_alignment_result_v1",
        ),
        (
            "version",
            "ontology_alignment_v1",
        ),
        (
            "phase",
            "4.6.22",
        ),
        (
            "patch",
            "4.6.22K",
        ),
        (
            "status",
            "ONTOLOGY_ALIGNMENT_CERTIFIED",
        ),
        (
            "alignment_policy",
            "FULL_ONTOLOGY_ALIGNMENT_CERTIFIED",
        ),
        (
            "next_stage",
            "transfer_learning",
        ),
    ):

        if certified_ontology_result.get(field) != expected:
            raise TransferLearningError(
                f"Invalid certified ontology lifecycle field: {field}"
            )

    workspace_id = certified_ontology_result.get(
        "workspace_id"
    )

    final_result = certified_ontology_result.get(
        "certified_final_ontology_alignment_result"
    )

    certification = certified_ontology_result.get(
        "full_ontology_alignment_certification"
    )

    boundaries = certified_ontology_result.get(
        "processing_boundaries"
    )

    if not isinstance(
        workspace_id,
        str,
    ) or not workspace_id:
        raise TransferLearningError(
            "workspace_id is required."
        )

    for name, value in (
        (
            "certified_final_ontology_alignment_result",
            final_result,
        ),
        (
            "full_ontology_alignment_certification",
            certification,
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
            raise TransferLearningError(
                name + " is missing."
            )

    # -------------------------------------------------------------
    # Certified final result
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
            "full_ontology_alignment_certified",
            True,
        ),
        (
            "certification_status",
            "CERTIFIED",
        ),
        (
            "certification_patch",
            "4.6.22K",
        ),
        (
            "next_owner",
            "4.6.23_TRANSFER_LEARNING",
        ),
        (
            "semantic_memory_owner",
            "4.6.28_SEMANTIC_MEMORY",
        ),
    ):

        if final_result.get(field) != expected:
            raise TransferLearningError(
                f"Certified final ontology field drifted: {field}"
            )

    for field in (
        "ontology_mapping_performed",
        "ontology_alignment_performed",
        "ontology_integrity_verified",
        "ontology_provenance_complete",
        "alignment_outcomes_preserved",
        "ambiguity_preserved",
        "conflicts_preserved",
        "uncertainty_preserved",
        "source_reasoning_preserved",
        "source_profiles_preserved",
        "retrieval_payloads_preserved",
    ):

        if final_result.get(field) is not True:
            raise TransferLearningError(
                f"Required ontology field is not True: {field}"
            )

    for field in (
        "unsupported_mapping_invented",
        "silent_resolution_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if final_result.get(field) is not False:
            raise TransferLearningError(
                f"Forbidden ontology field is not False: {field}"
            )

    # -------------------------------------------------------------
    # Full ontology certification
    # -------------------------------------------------------------

    for field, expected in (
        (
            "certification_schema",
            "full_ontology_alignment_certification_v1",
        ),
        (
            "certification_version",
            "v1",
        ),
        (
            "certification_phase",
            "4.6.22",
        ),
        (
            "certification_patch",
            "4.6.22K",
        ),
        (
            "certification_status",
            "CERTIFIED",
        ),
        (
            "certification_scope",
            "FULL_ONTOLOGY_ALIGNMENT_PIPELINE",
        ),
        (
            "next_owner",
            "4.6.23_TRANSFER_LEARNING",
        ),
        (
            "semantic_memory_owner",
            "4.6.28_SEMANTIC_MEMORY",
        ),
    ):

        if certification.get(field) != expected:
            raise TransferLearningError(
                f"Ontology certification field drifted: {field}"
            )

    for field in (
        "all_pipeline_identity_bindings_verified",
        "final_result_digest_verified",
        "final_result_id_verified",
        "ontology_mapping_verified",
        "ontology_alignment_verified",
        "ontology_integrity_verified",
        "ontology_provenance_verified",
        "alignment_outcomes_preserved",
        "ambiguity_preserved",
        "conflicts_preserved",
        "uncertainty_preserved",
        "source_reasoning_preserved",
        "source_profiles_preserved",
        "retrieval_payloads_preserved",
        "transfer_learning_ready",
    ):

        if certification.get(field) is not True:
            raise TransferLearningError(
                f"Required certification field is not True: {field}"
            )

    for field in (
        "unsupported_mapping_invented",
        "silent_resolution_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if certification.get(field) is not False:
            raise TransferLearningError(
                f"Forbidden certification field is not False: {field}"
            )

    # -------------------------------------------------------------
    # Identity bindings
    # -------------------------------------------------------------

    for field in (
        "ontology_scope_id",
        "normalization_package_id",
        "alignment_package_id",
        "integrity_guard_id",
        "provenance_id",
    ):

        final_value = final_result.get(
            field
        )

        cert_value = certification.get(
            field
        )

        if not isinstance(
            final_value,
            str,
        ) or not final_value:
            raise TransferLearningError(
                f"Missing certified identity: {field}"
            )

        if final_value != cert_value:
            raise TransferLearningError(
                f"Certification binding drifted: {field}"
            )

    if certification.get(
        "source_final_result_id"
    ) != final_result.get(
        "final_result_id"
    ):
        raise TransferLearningError(
            "Final result ID binding drifted."
        )

    if certification.get(
        "source_final_result_digest"
    ) != final_result.get(
        "final_result_digest"
    ):
        raise TransferLearningError(
            "Final result digest binding drifted."
        )

    # -------------------------------------------------------------
    # Transfer payload readiness
    # -------------------------------------------------------------

    collections = {
        "canonical_concepts":
            final_result.get(
                "canonical_concepts"
            ),

        "alignments":
            final_result.get(
                "alignments"
            ),

        "confirmed_alignments":
            final_result.get(
                "confirmed_alignments"
            ),

        "unresolved_alignments":
            final_result.get(
                "unresolved_alignments"
            ),

        "conflicting_alignments":
            final_result.get(
                "conflicting_alignments"
            ),

        "ambiguity_registry":
            final_result.get(
                "ambiguity_registry"
            ),

        "ontology_conflict_registry":
            final_result.get(
                "ontology_conflict_registry"
            ),

        "multi_candidate_registry":
            final_result.get(
                "multi_candidate_registry"
            ),

        "mapping_traces":
            final_result.get(
                "mapping_traces"
            ),
    }

    for name, value in collections.items():

        if not isinstance(
            value,
            list,
        ):
            raise TransferLearningError(
                name + " must be a list."
            )

    count_bindings = (
        (
            "canonical_concept_count",
            "canonical_concepts",
        ),
        (
            "alignment_count",
            "alignments",
        ),
        (
            "confirmed_alignment_count",
            "confirmed_alignments",
        ),
        (
            "unresolved_alignment_count",
            "unresolved_alignments",
        ),
        (
            "conflict_alignment_count",
            "conflicting_alignments",
        ),
        (
            "ambiguity_count",
            "ambiguity_registry",
        ),
        (
            "ontology_conflict_count",
            "ontology_conflict_registry",
        ),
        (
            "multi_candidate_count",
            "multi_candidate_registry",
        ),
        (
            "mapping_trace_count",
            "mapping_traces",
        ),
    )

    for count_field, collection_name in count_bindings:

        if final_result.get(
            count_field
        ) != len(
            collections[
                collection_name
            ]
        ):
            raise TransferLearningError(
                f"Ontology payload count drifted: {count_field}"
            )

    if not collections[
        "canonical_concepts"
    ]:
        raise TransferLearningError(
            "At least one canonical concept is required."
        )

    if len(
        collections[
            "mapping_traces"
        ]
    ) != len(
        collections[
            "alignments"
        ]
    ):
        raise TransferLearningError(
            "Every alignment must retain a mapping trace."
        )

    # -------------------------------------------------------------
    # Ambiguity / conflict preservation
    # -------------------------------------------------------------

    for item in collections[
        "ambiguity_registry"
    ]:

        if not isinstance(
            item,
            Mapping,
        ):
            raise TransferLearningError(
                "Invalid ambiguity entry."
            )

        if item.get(
            "ambiguity_status"
        ) != "OPEN":
            raise TransferLearningError(
                "Resolved ambiguity cannot enter Transfer Learning."
            )

        if item.get(
            "auto_resolved"
        ) is not False:
            raise TransferLearningError(
                "Auto-resolved ambiguity rejected."
            )

    for item in collections[
        "ontology_conflict_registry"
    ]:

        if not isinstance(
            item,
            Mapping,
        ):
            raise TransferLearningError(
                "Invalid ontology conflict entry."
            )

        if item.get(
            "conflict_status"
        ) != "OPEN":
            raise TransferLearningError(
                "Resolved ontology conflict cannot enter Transfer Learning."
            )

        if item.get(
            "silently_resolved"
        ) is not False:
            raise TransferLearningError(
                "Silently resolved ontology conflict rejected."
            )

    # -------------------------------------------------------------
    # Certified upstream boundaries
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
        "full_ontology_alignment_certification_performed",
        "reasoning_integrity_preserved",
        "reasoning_provenance_preserved",
        "reasoning_outcomes_preserved",
        "uncertainty_preserved",
        "conflicts_preserved",
        "ambiguity_preserved",
    ):

        if boundaries.get(field) is not True:
            raise TransferLearningError(
                f"Required upstream boundary is not True: {field}"
            )

    for field in (
        "source_reasoning_modified",
        "source_profile_modified",
        "retrieval_payload_modified",
        "unsupported_mapping_invented",
        "silent_resolution_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if boundaries.get(field) is not False:
            raise TransferLearningError(
                f"Forbidden upstream boundary is not False: {field}"
            )

    inspection = {
        "inspection_schema":
            "transfer_learning_input_inspection_v1",

        "inspection_version":
            "v1",

        "inspection_status":
            "PASSED",

        "source_schema":
            "certified_ontology_alignment_result_v1",

        "source_phase":
            "4.6.22",

        "source_patch":
            "4.6.22K",

        "workspace_id":
            workspace_id,

        "ontology_scope_id":
            final_result[
                "ontology_scope_id"
            ],

        "final_result_id":
            final_result[
                "final_result_id"
            ],

        "final_result_digest":
            final_result[
                "final_result_digest"
            ],

        "canonical_concept_count":
            len(
                collections[
                    "canonical_concepts"
                ]
            ),

        "alignment_count":
            len(
                collections[
                    "alignments"
                ]
            ),

        "confirmed_alignment_count":
            len(
                collections[
                    "confirmed_alignments"
                ]
            ),

        "unresolved_alignment_count":
            len(
                collections[
                    "unresolved_alignments"
                ]
            ),

        "conflict_alignment_count":
            len(
                collections[
                    "conflicting_alignments"
                ]
            ),

        "mapping_trace_count":
            len(
                collections[
                    "mapping_traces"
                ]
            ),

        "ontology_alignment_certified":
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

        "transfer_learning_ready":
            True,

        "semantic_memory_deferred":
            True,

        "linking_deferred":
            True,

        "transfer_learning_performed":
            False,
    }

    return {
        "schema_version":
            "transfer_learning_input_inspection_result_v1",

        "version":
            TRANSFER_LEARNING_VERSION,

        "phase":
            TRANSFER_LEARNING_PHASE,

        "patch":
            "4.6.23A",

        "status":
            "CERTIFIED_ONTOLOGY_ALIGNMENT_INPUT_INSPECTED",

        "workspace_id":
            workspace_id,

        "inspection":
            inspection,

        "certified_final_ontology_alignment_result":
            deepcopy(
                dict(final_result)
            ),

        "full_ontology_alignment_certification":
            deepcopy(
                dict(certification)
            ),

        "source_certified_ontology_alignment_result":
            deepcopy(
                dict(certified_ontology_result)
            ),

        "processing_boundaries": {
            "certified_ontology_alignment_input_inspected":
                True,

            "certified_ontology_alignment_input_preserved":
                True,

            "ontology_alignment_integrity_preserved":
                True,

            "ontology_alignment_provenance_preserved":
                True,

            "alignment_outcomes_preserved":
                True,

            "ambiguity_preserved":
                True,

            "conflicts_preserved":
                True,

            "uncertainty_preserved":
                True,

            "transfer_learning_architecture_defined":
                False,

            "transfer_learning_intake_validated":
                False,

            "transfer_scope_defined":
                False,

            "transferable_knowledge_extracted":
                False,

            "knowledge_adaptation_performed":
                False,

            "transfer_learning_performed":
                False,

            "transfer_integrity_verification_performed":
                False,

            "transfer_provenance_built":
                False,

            "final_transfer_learning_result_built":
                False,

            "full_transfer_learning_certification_performed":
                False,

            "source_ontology_alignment_modified":
                False,

            "source_reasoning_modified":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,
        },

        "transfer_policy":
            "CERTIFIED_ONTOLOGY_ALIGNMENT_INPUT_ONLY",

        "next_stage":
            "transfer_learning_architecture_definition",
    }


# =====================================================================
# PATCH 4.6.23B ? Transfer Learning Architecture Definition
# =====================================================================

def define_transfer_learning_architecture_v1() -> dict[str, Any]:
    """
    Define the canonical LinkCraftor Transfer Learning architecture.

    Transfer Learning in this architecture means controlled,
    evidence-bound reuse of certified semantic knowledge.

    It does NOT:
    - retrain foundation/model weights,
    - perform neural fine-tuning,
    - write Semantic Memory,
    - alter upstream ontology results,
    - make linking decisions,
    - silently resolve ambiguity or conflicts.
    """

    transfer_knowledge_families = [
        "CANONICAL_CONCEPT_KNOWLEDGE",
        "ONTOLOGY_ALIGNMENT_KNOWLEDGE",
        "SEMANTIC_RELATIONSHIP_PATTERN",
        "TOPIC_STRUCTURE_PATTERN",
        "REASONING_PATTERN",
        "EVIDENCE_PATTERN",
        "CONTEXT_PATTERN",
        "CAUSAL_PATTERN",
        "TEMPORAL_PATTERN",
        "PROCEDURAL_PATTERN",
        "COMPARATIVE_PATTERN",
        "CONFLICT_PATTERN",
        "AMBIGUITY_PATTERN",
        "UNCERTAINTY_PATTERN",
    ]

    transfer_context_modes = [
        "SAME_DOCUMENT_FAMILY",
        "CROSS_DOCUMENT",
        "CROSS_TOPIC_CLUSTER",
        "SAME_WORKSPACE",
        "CROSS_WORKSPACE",
        "SAME_DOMAIN",
        "RELATED_DOMAIN",
        "CROSS_DOMAIN_RESTRICTED",
    ]

    transfer_eligibility_states = [
        "ELIGIBLE",
        "CONDITIONALLY_ELIGIBLE",
        "BLOCKED",
        "UNRESOLVED",
    ]

    transfer_execution_states = [
        "TRANSFERRED",
        "CONDITIONAL_TRANSFER",
        "NOT_TRANSFERRED",
        "BLOCKED_NEGATIVE_TRANSFER",
        "BLOCKED_INSUFFICIENT_EVIDENCE",
        "BLOCKED_CONFLICT",
        "BLOCKED_AMBIGUITY",
        "BLOCKED_DOMAIN_MISMATCH",
    ]

    negative_transfer_risk_levels = [
        "LOW",
        "MODERATE",
        "HIGH",
        "CRITICAL",
    ]

    adaptation_dimensions = [
        "CONCEPT_COMPATIBILITY",
        "ONTOLOGY_COMPATIBILITY",
        "DOMAIN_COMPATIBILITY",
        "TOPIC_COMPATIBILITY",
        "CONTEXT_COMPATIBILITY",
        "RELATIONSHIP_COMPATIBILITY",
        "EVIDENCE_COMPATIBILITY",
        "TEMPORAL_COMPATIBILITY",
        "UNCERTAINTY_COMPATIBILITY",
        "CONFLICT_COMPATIBILITY",
    ]

    mandatory_transfer_principles = [
        "CERTIFIED_SOURCE_ONLY",
        "TARGET_CONTEXT_REQUIRED",
        "EVIDENCE_BOUND_TRANSFER",
        "NO_BLIND_REUSE",
        "NO_FORCED_EQUIVALENCE",
        "NO_SILENT_AMBIGUITY_RESOLUTION",
        "NO_SILENT_CONFLICT_RESOLUTION",
        "UNCERTAINTY_MUST_BE_PRESERVED",
        "SOURCE_PROVENANCE_MUST_BE_PRESERVED",
        "TARGET_PROVENANCE_MUST_BE_CREATED",
        "NEGATIVE_TRANSFER_MUST_BE_GUARDED",
        "SOURCE_RESULT_IMMUTABLE",
        "TRANSFER_DECISION_EXPLAINABLE",
        "SEMANTIC_MEMORY_WRITE_DEFERRED",
        "LINKING_DECISIONS_DEFERRED",
    ]

    blocked_behaviors = [
        "MODEL_WEIGHT_TRAINING",
        "FOUNDATION_MODEL_FINE_TUNING",
        "UNSUPPORTED_KNOWLEDGE_INVENTION",
        "UNSUPPORTED_CROSS_DOMAIN_TRANSFER",
        "SOURCE_ONTOLOGY_MUTATION",
        "SOURCE_REASONING_MUTATION",
        "AUTOMATIC_AMBIGUITY_RESOLUTION",
        "AUTOMATIC_CONFLICT_RESOLUTION",
        "SEMANTIC_MEMORY_WRITE",
        "LINKING_DECISION",
        "URL_ASSIGNMENT",
        "TARGET_SELECTION",
        "HIGHLIGHT_SELECTION",
    ]

    execution_contract = {
        "4.6.23A":
            "CERTIFIED_ONTOLOGY_ALIGNMENT_INPUT_CONTRACT_INSPECTION",

        "4.6.23B":
            "TRANSFER_LEARNING_ARCHITECTURE_DEFINITION",

        "4.6.23C":
            "TRANSFER_LEARNING_INTAKE_VALIDATION",

        "4.6.23D":
            "TRANSFER_SCOPE_AND_ELIGIBILITY_CONTRACT",

        "4.6.23E":
            "TRANSFERABLE_KNOWLEDGE_EXTRACTION",

        "4.6.23F":
            "SOURCE_TO_TARGET_KNOWLEDGE_ADAPTATION",

        "4.6.23G":
            "TRANSFER_LEARNING_EXECUTION",

        "4.6.23H":
            "TRANSFER_INTEGRITY_AND_NEGATIVE_TRANSFER_GUARD",

        "4.6.23I":
            "TRANSFER_PROVENANCE_AND_EVIDENCE_TRACE",

        "4.6.23J":
            "FINAL_TRANSFER_LEARNING_RESULT",

        "4.6.23K":
            "FULL_TRANSFER_LEARNING_HARD_CERTIFICATION",
    }

    return {
        "architecture_schema":
            "transfer_learning_architecture_v1",

        "architecture_version":
            "v1",

        "engine_version":
            TRANSFER_LEARNING_VERSION,

        "phase":
            TRANSFER_LEARNING_PHASE,

        "owner":
            "4.6.23_TRANSFER_LEARNING",

        "source_owner":
            "4.6.22_ONTOLOGY_ALIGNMENT",

        "next_owner":
            "4.6.24_AUTHORITY",

        "semantic_memory_owner":
            "4.6.28_SEMANTIC_MEMORY",

        "learning_engine_owner":
            "4.6.27_LEARNING_ENGINE",

        "dynamic_semantic_graph_owner":
            "4.6.26_DYNAMIC_SEMANTIC_GRAPH",

        "transfer_engine_type":
            "CERTIFIED_SEMANTIC_KNOWLEDGE_TRANSFER",

        "model_weight_training":
            False,

        "foundation_model_fine_tuning":
            False,

        "source_contract":
            "certified_ontology_alignment_result_v1",

        "source_patch":
            "4.6.22K",

        "required_input_stage":
            "4.6.23A",

        "transfer_knowledge_families":
            transfer_knowledge_families,

        "transfer_context_modes":
            transfer_context_modes,

        "transfer_eligibility_states":
            transfer_eligibility_states,

        "transfer_execution_states":
            transfer_execution_states,

        "negative_transfer_risk_levels":
            negative_transfer_risk_levels,

        "adaptation_dimensions":
            adaptation_dimensions,

        "mandatory_transfer_principles":
            mandatory_transfer_principles,

        "blocked_behaviors":
            blocked_behaviors,

        "execution_contract":
            execution_contract,

        "requires_certified_source":
            True,

        "requires_target_context":
            True,

        "requires_transfer_scope":
            True,

        "requires_eligibility_decision":
            True,

        "requires_source_evidence":
            True,

        "requires_target_compatibility_evidence":
            True,

        "requires_negative_transfer_guard":
            True,

        "requires_transfer_provenance":
            True,

        "requires_explainable_transfer_decision":
            True,

        "allows_same_workspace_transfer":
            True,

        "allows_cross_workspace_transfer":
            True,

        "allows_same_domain_transfer":
            True,

        "allows_related_domain_transfer":
            True,

        "allows_cross_domain_transfer":
            True,

        "cross_domain_transfer_restricted":
            True,

        "confirmed_knowledge_may_transfer":
            True,

        "unresolved_knowledge_auto_transfer":
            False,

        "conflicting_knowledge_auto_transfer":
            False,

        "ambiguous_knowledge_auto_transfer":
            False,

        "unsupported_knowledge_may_transfer":
            False,

        "source_ontology_alignment_mutable":
            False,

        "source_reasoning_mutable":
            False,

        "semantic_memory_written":
            False,

        "linking_decisions_performed":
            False,

        "architecture_policy":
            "EVIDENCE_BOUND_CERTIFIED_SEMANTIC_TRANSFER_ONLY",

        "next_stage":
            "transfer_learning_intake_validation",
    }


# =====================================================================
# PATCH 4.6.23C ? Transfer Learning Intake Validation
# =====================================================================

def validate_transfer_learning_intake_v1(
    inspection_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Validate the certified Transfer Learning intake.

    C validates the exact 4.6.23A inspection result against the
    canonical 4.6.23B architecture.

    C does NOT:
    - define transfer scope,
    - extract transferable knowledge,
    - adapt knowledge,
    - execute transfer,
    - resolve ambiguity/conflicts,
    - write Semantic Memory,
    - make linking decisions.
    """

    from collections.abc import Mapping

    if not isinstance(
        inspection_result,
        Mapping,
    ):
        raise TransferLearningError(
            "inspection_result must be a mapping."
        )

    # -------------------------------------------------------------
    # Exact 4.6.23A lifecycle
    # -------------------------------------------------------------

    for field, expected in (
        (
            "schema_version",
            "transfer_learning_input_inspection_result_v1",
        ),
        (
            "version",
            TRANSFER_LEARNING_VERSION,
        ),
        (
            "phase",
            TRANSFER_LEARNING_PHASE,
        ),
        (
            "patch",
            "4.6.23A",
        ),
        (
            "status",
            "CERTIFIED_ONTOLOGY_ALIGNMENT_INPUT_INSPECTED",
        ),
        (
            "transfer_policy",
            "CERTIFIED_ONTOLOGY_ALIGNMENT_INPUT_ONLY",
        ),
        (
            "next_stage",
            "transfer_learning_architecture_definition",
        ),
    ):

        if inspection_result.get(field) != expected:
            raise TransferLearningError(
                f"Invalid 4.6.23A lifecycle field: {field}"
            )

    workspace_id = inspection_result.get(
        "workspace_id"
    )

    inspection = inspection_result.get(
        "inspection"
    )

    certified_final = inspection_result.get(
        "certified_final_ontology_alignment_result"
    )

    certification = inspection_result.get(
        "full_ontology_alignment_certification"
    )

    source_certified = inspection_result.get(
        "source_certified_ontology_alignment_result"
    )

    boundaries = inspection_result.get(
        "processing_boundaries"
    )

    for name, value in (
        (
            "inspection",
            inspection,
        ),
        (
            "certified_final_ontology_alignment_result",
            certified_final,
        ),
        (
            "full_ontology_alignment_certification",
            certification,
        ),
        (
            "source_certified_ontology_alignment_result",
            source_certified,
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
            raise TransferLearningError(
                name + " is missing."
            )

    if not isinstance(
        workspace_id,
        str,
    ) or not workspace_id:
        raise TransferLearningError(
            "workspace_id is required."
        )

    # -------------------------------------------------------------
    # Architecture authority
    # -------------------------------------------------------------

    architecture = define_transfer_learning_architecture_v1()

    if architecture.get(
        "architecture_schema"
    ) != "transfer_learning_architecture_v1":
        raise TransferLearningError(
            "Transfer Learning architecture schema drifted."
        )

    if architecture.get(
        "owner"
    ) != "4.6.23_TRANSFER_LEARNING":
        raise TransferLearningError(
            "Transfer Learning ownership drifted."
        )

    if architecture.get(
        "source_owner"
    ) != "4.6.22_ONTOLOGY_ALIGNMENT":
        raise TransferLearningError(
            "Transfer Learning source owner drifted."
        )

    if architecture.get(
        "next_owner"
    ) != "4.6.24_AUTHORITY":
        raise TransferLearningError(
            "Post-transfer owner drifted."
        )

    if architecture.get(
        "semantic_memory_owner"
    ) != "4.6.28_SEMANTIC_MEMORY":
        raise TransferLearningError(
            "Semantic Memory ownership drifted."
        )

    execution_contract = architecture.get(
        "execution_contract"
    )

    if not isinstance(
        execution_contract,
        Mapping,
    ):
        raise TransferLearningError(
            "Execution contract is missing."
        )

    if execution_contract.get(
        "4.6.23C"
    ) != "TRANSFER_LEARNING_INTAKE_VALIDATION":
        raise TransferLearningError(
            "4.6.23C execution contract drifted."
        )

    # -------------------------------------------------------------
    # Inspection authority
    # -------------------------------------------------------------

    for field, expected in (
        (
            "inspection_schema",
            "transfer_learning_input_inspection_v1",
        ),
        (
            "inspection_version",
            "v1",
        ),
        (
            "inspection_status",
            "PASSED",
        ),
        (
            "source_schema",
            "certified_ontology_alignment_result_v1",
        ),
        (
            "source_phase",
            "4.6.22",
        ),
        (
            "source_patch",
            "4.6.22K",
        ),
        (
            "workspace_id",
            workspace_id,
        ),
        (
            "ontology_alignment_certified",
            True,
        ),
        (
            "ontology_integrity_verified",
            True,
        ),
        (
            "ontology_provenance_verified",
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
            "transfer_learning_ready",
            True,
        ),
        (
            "semantic_memory_deferred",
            True,
        ),
        (
            "linking_deferred",
            True,
        ),
        (
            "transfer_learning_performed",
            False,
        ),
    ):

        if inspection.get(field) != expected:
            raise TransferLearningError(
                f"Transfer Learning inspection drifted: {field}"
            )

    # -------------------------------------------------------------
    # Cross-object identity bindings
    # -------------------------------------------------------------

    if certified_final.get(
        "workspace_id"
    ) != workspace_id:
        raise TransferLearningError(
            "Certified final workspace binding drifted."
        )

    if inspection.get(
        "ontology_scope_id"
    ) != certified_final.get(
        "ontology_scope_id"
    ):
        raise TransferLearningError(
            "Inspection ontology scope binding drifted."
        )

    if inspection.get(
        "final_result_id"
    ) != certified_final.get(
        "final_result_id"
    ):
        raise TransferLearningError(
            "Inspection final result ID binding drifted."
        )

    if inspection.get(
        "final_result_digest"
    ) != certified_final.get(
        "final_result_digest"
    ):
        raise TransferLearningError(
            "Inspection final digest binding drifted."
        )

    if certification.get(
        "source_final_result_id"
    ) != certified_final.get(
        "final_result_id"
    ):
        raise TransferLearningError(
            "Certification/final result ID binding drifted."
        )

    if certification.get(
        "source_final_result_digest"
    ) != certified_final.get(
        "final_result_digest"
    ):
        raise TransferLearningError(
            "Certification/final digest binding drifted."
        )

    # -------------------------------------------------------------
    # Count / payload authority
    # -------------------------------------------------------------

    count_pairs = (
        (
            "canonical_concept_count",
            "canonical_concepts",
        ),
        (
            "alignment_count",
            "alignments",
        ),
        (
            "confirmed_alignment_count",
            "confirmed_alignments",
        ),
        (
            "unresolved_alignment_count",
            "unresolved_alignments",
        ),
        (
            "conflict_alignment_count",
            "conflicting_alignments",
        ),
        (
            "mapping_trace_count",
            "mapping_traces",
        ),
    )

    for count_field, collection_field in count_pairs:

        collection = certified_final.get(
            collection_field
        )

        if not isinstance(
            collection,
            list,
        ):
            raise TransferLearningError(
                collection_field + " must be a list."
            )

        expected_count = len(
            collection
        )

        if certified_final.get(
            count_field
        ) != expected_count:
            raise TransferLearningError(
                f"Certified final count drifted: {count_field}"
            )

        if inspection.get(
            count_field
        ) != expected_count:
            raise TransferLearningError(
                f"Inspection count drifted: {count_field}"
            )

    if certified_final.get(
        "canonical_concept_count"
    ) < 1:
        raise TransferLearningError(
            "Transfer Learning intake requires canonical concepts."
        )

    if certified_final.get(
        "mapping_trace_count"
    ) != certified_final.get(
        "alignment_count"
    ):
        raise TransferLearningError(
            "Every alignment must retain provenance."
        )

    # -------------------------------------------------------------
    # Certified source readiness
    # -------------------------------------------------------------

    for field in (
        "ontology_mapping_performed",
        "ontology_alignment_performed",
        "ontology_integrity_verified",
        "ontology_provenance_complete",
        "alignment_outcomes_preserved",
        "ambiguity_preserved",
        "conflicts_preserved",
        "uncertainty_preserved",
        "full_ontology_alignment_certified",
    ):

        if certified_final.get(field) is not True:
            raise TransferLearningError(
                f"Required source field is not True: {field}"
            )

    if certified_final.get(
        "certification_status"
    ) != "CERTIFIED":
        raise TransferLearningError(
            "Source ontology alignment is not certified."
        )

    if certified_final.get(
        "next_owner"
    ) != "4.6.23_TRANSFER_LEARNING":
        raise TransferLearningError(
            "Source handoff owner drifted."
        )

    for field in (
        "unsupported_mapping_invented",
        "silent_resolution_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if certified_final.get(field) is not False:
            raise TransferLearningError(
                f"Forbidden source field is not False: {field}"
            )

    # -------------------------------------------------------------
    # A boundary authority
    # -------------------------------------------------------------

    for field in (
        "certified_ontology_alignment_input_inspected",
        "certified_ontology_alignment_input_preserved",
        "ontology_alignment_integrity_preserved",
        "ontology_alignment_provenance_preserved",
        "alignment_outcomes_preserved",
        "ambiguity_preserved",
        "conflicts_preserved",
        "uncertainty_preserved",
    ):

        if boundaries.get(field) is not True:
            raise TransferLearningError(
                f"Required 4.6.23A boundary is not True: {field}"
            )

    for field in (
        "transfer_learning_architecture_defined",
        "transfer_learning_intake_validated",
        "transfer_scope_defined",
        "transferable_knowledge_extracted",
        "knowledge_adaptation_performed",
        "transfer_learning_performed",
        "transfer_integrity_verification_performed",
        "transfer_provenance_built",
        "final_transfer_learning_result_built",
        "full_transfer_learning_certification_performed",
        "source_ontology_alignment_modified",
        "source_reasoning_modified",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if boundaries.get(field) is not False:
            raise TransferLearningError(
                f"Forbidden 4.6.23A boundary is not False: {field}"
            )

    # -------------------------------------------------------------
    # Intake validation result
    # -------------------------------------------------------------

    intake = {
        "intake_schema":
            "transfer_learning_intake_v1",

        "intake_version":
            "v1",

        "intake_status":
            "VALIDATED",

        "workspace_id":
            workspace_id,

        "ontology_scope_id":
            certified_final[
                "ontology_scope_id"
            ],

        "source_final_result_id":
            certified_final[
                "final_result_id"
            ],

        "source_final_result_digest":
            certified_final[
                "final_result_digest"
            ],

        "source_certification_id":
            certification[
                "certification_id"
            ],

        "canonical_concept_count":
            certified_final[
                "canonical_concept_count"
            ],

        "alignment_count":
            certified_final[
                "alignment_count"
            ],

        "confirmed_alignment_count":
            certified_final[
                "confirmed_alignment_count"
            ],

        "unresolved_alignment_count":
            certified_final[
                "unresolved_alignment_count"
            ],

        "conflict_alignment_count":
            certified_final[
                "conflict_alignment_count"
            ],

        "mapping_trace_count":
            certified_final[
                "mapping_trace_count"
            ],

        "certified_source_verified":
            True,

        "source_identity_bindings_verified":
            True,

        "source_counts_verified":
            True,

        "source_provenance_verified":
            True,

        "source_integrity_verified":
            True,

        "ambiguity_preserved":
            True,

        "conflicts_preserved":
            True,

        "uncertainty_preserved":
            True,

        "target_context_required":
            True,

        "transfer_scope_required":
            True,

        "eligibility_decision_required":
            True,

        "negative_transfer_guard_required":
            True,

        "transfer_learning_performed":
            False,

        "semantic_memory_written":
            False,

        "linking_decisions_performed":
            False,
    }

    return {
        "schema_version":
            "transfer_learning_intake_validation_result_v1",

        "version":
            TRANSFER_LEARNING_VERSION,

        "phase":
            TRANSFER_LEARNING_PHASE,

        "patch":
            "4.6.23C",

        "status":
            "TRANSFER_LEARNING_INTAKE_VALIDATED",

        "workspace_id":
            workspace_id,

        "transfer_learning_architecture":
            deepcopy(
                architecture
            ),

        "validated_intake":
            intake,

        "certified_final_ontology_alignment_result":
            deepcopy(
                dict(certified_final)
            ),

        "full_ontology_alignment_certification":
            deepcopy(
                dict(certification)
            ),

        "source_inspection_result":
            deepcopy(
                dict(inspection_result)
            ),

        "processing_boundaries": {
            "certified_ontology_alignment_input_inspected":
                True,

            "certified_ontology_alignment_input_preserved":
                True,

            "ontology_alignment_integrity_preserved":
                True,

            "ontology_alignment_provenance_preserved":
                True,

            "alignment_outcomes_preserved":
                True,

            "ambiguity_preserved":
                True,

            "conflicts_preserved":
                True,

            "uncertainty_preserved":
                True,

            "transfer_learning_architecture_defined":
                True,

            "transfer_learning_intake_validated":
                True,

            "transfer_scope_defined":
                False,

            "transferable_knowledge_extracted":
                False,

            "knowledge_adaptation_performed":
                False,

            "transfer_learning_performed":
                False,

            "transfer_integrity_verification_performed":
                False,

            "transfer_provenance_built":
                False,

            "final_transfer_learning_result_built":
                False,

            "full_transfer_learning_certification_performed":
                False,

            "source_ontology_alignment_modified":
                False,

            "source_reasoning_modified":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,
        },

        "transfer_policy":
            "CERTIFIED_TRANSFER_LEARNING_INTAKE_VALIDATED",

        "next_stage":
            "transfer_scope_and_eligibility_contract",
    }


# =====================================================================
# PATCH 4.6.23D ? Transfer Scope & Eligibility Contract
# =====================================================================

def define_transfer_scope_and_eligibility_v1(
    intake_result: dict[str, Any],
    target_context: dict[str, Any],
) -> dict[str, Any]:
    """
    Define the Transfer Learning scope and eligibility contract.

    D determines:
    - source/target scope,
    - requested knowledge families,
    - transfer context mode,
    - eligibility state,
    - blocking/conditional reasons.

    D does NOT:
    - extract knowledge,
    - adapt knowledge,
    - execute transfer,
    - resolve ambiguity/conflict,
    - write Semantic Memory,
    - make linking decisions.
    """

    from collections.abc import Mapping

    if not isinstance(
        intake_result,
        Mapping,
    ):
        raise TransferLearningError(
            "intake_result must be a mapping."
        )

    if not isinstance(
        target_context,
        Mapping,
    ):
        raise TransferLearningError(
            "target_context must be a mapping."
        )

    # -------------------------------------------------------------
    # Exact 4.6.23C lifecycle
    # -------------------------------------------------------------

    for field, expected in (
        (
            "schema_version",
            "transfer_learning_intake_validation_result_v1",
        ),
        (
            "version",
            TRANSFER_LEARNING_VERSION,
        ),
        (
            "phase",
            TRANSFER_LEARNING_PHASE,
        ),
        (
            "patch",
            "4.6.23C",
        ),
        (
            "status",
            "TRANSFER_LEARNING_INTAKE_VALIDATED",
        ),
        (
            "transfer_policy",
            "CERTIFIED_TRANSFER_LEARNING_INTAKE_VALIDATED",
        ),
        (
            "next_stage",
            "transfer_scope_and_eligibility_contract",
        ),
    ):

        if intake_result.get(field) != expected:
            raise TransferLearningError(
                f"Invalid 4.6.23C lifecycle field: {field}"
            )

    workspace_id = intake_result.get(
        "workspace_id"
    )

    intake = intake_result.get(
        "validated_intake"
    )

    architecture = intake_result.get(
        "transfer_learning_architecture"
    )

    certified_final = intake_result.get(
        "certified_final_ontology_alignment_result"
    )

    boundaries = intake_result.get(
        "processing_boundaries"
    )

    for name, value in (
        (
            "validated_intake",
            intake,
        ),
        (
            "transfer_learning_architecture",
            architecture,
        ),
        (
            "certified_final_ontology_alignment_result",
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
            raise TransferLearningError(
                name + " is missing."
            )

    if not isinstance(
        workspace_id,
        str,
    ) or not workspace_id:
        raise TransferLearningError(
            "workspace_id is required."
        )

    # -------------------------------------------------------------
    # Intake readiness
    # -------------------------------------------------------------

    if intake.get(
        "intake_status"
    ) != "VALIDATED":
        raise TransferLearningError(
            "Transfer Learning intake is not validated."
        )

    for field in (
        "certified_source_verified",
        "source_identity_bindings_verified",
        "source_counts_verified",
        "source_provenance_verified",
        "source_integrity_verified",
        "ambiguity_preserved",
        "conflicts_preserved",
        "uncertainty_preserved",
        "target_context_required",
        "transfer_scope_required",
        "eligibility_decision_required",
        "negative_transfer_guard_required",
    ):

        if intake.get(field) is not True:
            raise TransferLearningError(
                f"Required intake field is not True: {field}"
            )

    for field in (
        "transfer_learning_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if intake.get(field) is not False:
            raise TransferLearningError(
                f"Forbidden intake field is not False: {field}"
            )

    # -------------------------------------------------------------
    # C boundary authority
    # -------------------------------------------------------------

    for field in (
        "certified_ontology_alignment_input_inspected",
        "certified_ontology_alignment_input_preserved",
        "ontology_alignment_integrity_preserved",
        "ontology_alignment_provenance_preserved",
        "alignment_outcomes_preserved",
        "ambiguity_preserved",
        "conflicts_preserved",
        "uncertainty_preserved",
        "transfer_learning_architecture_defined",
        "transfer_learning_intake_validated",
    ):

        if boundaries.get(field) is not True:
            raise TransferLearningError(
                f"Required 4.6.23C boundary is not True: {field}"
            )

    for field in (
        "transfer_scope_defined",
        "transferable_knowledge_extracted",
        "knowledge_adaptation_performed",
        "transfer_learning_performed",
        "transfer_integrity_verification_performed",
        "transfer_provenance_built",
        "final_transfer_learning_result_built",
        "full_transfer_learning_certification_performed",
        "source_ontology_alignment_modified",
        "source_reasoning_modified",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if boundaries.get(field) is not False:
            raise TransferLearningError(
                f"Forbidden 4.6.23C boundary is not False: {field}"
            )

    # -------------------------------------------------------------
    # Architecture authority
    # -------------------------------------------------------------

    if architecture.get(
        "architecture_schema"
    ) != "transfer_learning_architecture_v1":
        raise TransferLearningError(
            "Transfer Learning architecture drifted."
        )

    if architecture.get(
        "owner"
    ) != "4.6.23_TRANSFER_LEARNING":
        raise TransferLearningError(
            "Transfer Learning owner drifted."
        )

    allowed_context_modes = set(
        architecture.get(
            "transfer_context_modes"
        ) or []
    )

    allowed_families = set(
        architecture.get(
            "transfer_knowledge_families"
        ) or []
    )

    if not allowed_context_modes:
        raise TransferLearningError(
            "No transfer context modes are registered."
        )

    if not allowed_families:
        raise TransferLearningError(
            "No transfer knowledge families are registered."
        )

    # -------------------------------------------------------------
    # Target context contract
    # -------------------------------------------------------------

    target_workspace_id = target_context.get(
        "target_workspace_id"
    )

    target_domain = target_context.get(
        "target_domain"
    )

    target_topic = target_context.get(
        "target_topic"
    )

    transfer_context_mode = target_context.get(
        "transfer_context_mode"
    )

    requested_families = target_context.get(
        "requested_knowledge_families"
    )

    target_context_id = target_context.get(
        "target_context_id"
    )

    for field_name, value in (
        (
            "target_workspace_id",
            target_workspace_id,
        ),
        (
            "target_domain",
            target_domain,
        ),
        (
            "target_topic",
            target_topic,
        ),
        (
            "transfer_context_mode",
            transfer_context_mode,
        ),
        (
            "target_context_id",
            target_context_id,
        ),
    ):

        if not isinstance(
            value,
            str,
        ) or not value.strip():
            raise TransferLearningError(
                field_name + " must be a non-empty string."
            )

    if transfer_context_mode not in allowed_context_modes:
        raise TransferLearningError(
            "Unsupported transfer_context_mode."
        )

    if not isinstance(
        requested_families,
        list,
    ) or not requested_families:
        raise TransferLearningError(
            "requested_knowledge_families must be a non-empty list."
        )

    if any(
        not isinstance(item, str)
        or not item
        for item in requested_families
    ):
        raise TransferLearningError(
            "Each requested knowledge family must be a non-empty string."
        )

    if len(
        requested_families
    ) != len(
        set(requested_families)
    ):
        raise TransferLearningError(
            "requested_knowledge_families contains duplicates."
        )

    unsupported_families = sorted(
        set(requested_families)
        - allowed_families
    )

    if unsupported_families:
        raise TransferLearningError(
            "Unsupported knowledge families requested: "
            + ", ".join(
                unsupported_families
            )
        )

    # -------------------------------------------------------------
    # Context consistency rules
    # -------------------------------------------------------------

    source_workspace_id = workspace_id

    source_domain = target_context.get(
        "source_domain"
    )

    if not isinstance(
        source_domain,
        str,
    ) or not source_domain.strip():
        raise TransferLearningError(
            "source_domain must be supplied for transfer-scope evaluation."
        )

    if (
        transfer_context_mode == "SAME_WORKSPACE"
        and target_workspace_id != source_workspace_id
    ):
        raise TransferLearningError(
            "SAME_WORKSPACE requires identical workspace IDs."
        )

    if (
        transfer_context_mode == "CROSS_WORKSPACE"
        and target_workspace_id == source_workspace_id
    ):
        raise TransferLearningError(
            "CROSS_WORKSPACE requires different workspace IDs."
        )

    if (
        transfer_context_mode == "SAME_DOMAIN"
        and target_domain != source_domain
    ):
        raise TransferLearningError(
            "SAME_DOMAIN requires identical source and target domains."
        )

    if (
        transfer_context_mode
        in {
            "RELATED_DOMAIN",
            "CROSS_DOMAIN_RESTRICTED",
        }
        and target_domain == source_domain
    ):
        raise TransferLearningError(
            "Cross/related-domain modes require different domains."
        )

    # -------------------------------------------------------------
    # Eligibility evaluation
    # -------------------------------------------------------------

    blocking_reasons = []
    conditional_reasons = []

    canonical_concept_count = int(
        intake.get(
            "canonical_concept_count"
        ) or 0
    )

    confirmed_alignment_count = int(
        intake.get(
            "confirmed_alignment_count"
        ) or 0
    )

    unresolved_alignment_count = int(
        intake.get(
            "unresolved_alignment_count"
        ) or 0
    )

    conflict_alignment_count = int(
        intake.get(
            "conflict_alignment_count"
        ) or 0
    )

    if canonical_concept_count < 1:
        blocking_reasons.append(
            "NO_CANONICAL_CONCEPTS"
        )

    if (
        "ONTOLOGY_ALIGNMENT_KNOWLEDGE"
        in requested_families
        and confirmed_alignment_count < 1
    ):
        blocking_reasons.append(
            "NO_CONFIRMED_ONTOLOGY_ALIGNMENT"
        )

    if unresolved_alignment_count > 0:
        conditional_reasons.append(
            "UNRESOLVED_ALIGNMENT_PRESENT"
        )

    if conflict_alignment_count > 0:
        conditional_reasons.append(
            "CONFLICTING_ALIGNMENT_PRESENT"
        )

    if transfer_context_mode == "CROSS_DOMAIN_RESTRICTED":
        conditional_reasons.append(
            "CROSS_DOMAIN_REQUIRES_COMPATIBILITY_ASSESSMENT"
        )

    if transfer_context_mode == "RELATED_DOMAIN":
        conditional_reasons.append(
            "RELATED_DOMAIN_REQUIRES_COMPATIBILITY_ASSESSMENT"
        )

    if blocking_reasons:
        eligibility_state = "BLOCKED"

    elif conditional_reasons:
        eligibility_state = "CONDITIONALLY_ELIGIBLE"

    else:
        eligibility_state = "ELIGIBLE"

    # -------------------------------------------------------------
    # Deterministic scope identity
    # -------------------------------------------------------------

    scope_material = {
        "source_workspace_id":
            source_workspace_id,

        "target_workspace_id":
            target_workspace_id,

        "source_domain":
            source_domain,

        "target_domain":
            target_domain,

        "target_topic":
            target_topic,

        "target_context_id":
            target_context_id,

        "transfer_context_mode":
            transfer_context_mode,

        "requested_knowledge_families":
            sorted(
                requested_families
            ),

        "source_final_result_id":
            intake.get(
                "source_final_result_id"
            ),

        "source_final_result_digest":
            intake.get(
                "source_final_result_digest"
            ),
    }

    scope_digest = hashlib.sha256(
        json.dumps(
            scope_material,
            sort_keys=True,
            separators=(
                ",",
                ":",
            ),
        ).encode(
            "utf-8"
        )
    ).hexdigest()

    transfer_scope_id = (
        "transcope:v1:"
        + scope_digest
    )

    scope = {
        "scope_schema":
            "transfer_scope_eligibility_v1",

        "scope_version":
            "v1",

        "transfer_scope_id":
            transfer_scope_id,

        "transfer_scope_digest":
            scope_digest,

        "source_workspace_id":
            source_workspace_id,

        "target_workspace_id":
            target_workspace_id,

        "source_domain":
            source_domain,

        "target_domain":
            target_domain,

        "target_topic":
            target_topic,

        "target_context_id":
            target_context_id,

        "transfer_context_mode":
            transfer_context_mode,

        "requested_knowledge_families":
            sorted(
                requested_families
            ),

        "requested_knowledge_family_count":
            len(
                requested_families
            ),

        "canonical_concept_count":
            canonical_concept_count,

        "confirmed_alignment_count":
            confirmed_alignment_count,

        "unresolved_alignment_count":
            unresolved_alignment_count,

        "conflict_alignment_count":
            conflict_alignment_count,

        "eligibility_state":
            eligibility_state,

        "blocking_reasons":
            sorted(
                blocking_reasons
            ),

        "conditional_reasons":
            sorted(
                conditional_reasons
            ),

        "scope_defined":
            True,

        "eligibility_evaluated":
            True,

        "target_context_validated":
            True,

        "source_certification_preserved":
            True,

        "ambiguity_preserved":
            True,

        "conflicts_preserved":
            True,

        "uncertainty_preserved":
            True,

        "transferable_knowledge_extracted":
            False,

        "knowledge_adaptation_performed":
            False,

        "transfer_learning_performed":
            False,

        "semantic_memory_written":
            False,

        "linking_decisions_performed":
            False,
    }

    return {
        "schema_version":
            "transfer_scope_eligibility_result_v1",

        "version":
            TRANSFER_LEARNING_VERSION,

        "phase":
            TRANSFER_LEARNING_PHASE,

        "patch":
            "4.6.23D",

        "status":
            "TRANSFER_SCOPE_AND_ELIGIBILITY_DEFINED",

        "workspace_id":
            workspace_id,

        "transfer_scope":
            scope,

        "target_context":
            deepcopy(
                dict(target_context)
            ),

        "source_intake_result":
            deepcopy(
                dict(intake_result)
            ),

        "processing_boundaries": {
            "certified_ontology_alignment_input_inspected":
                True,

            "certified_ontology_alignment_input_preserved":
                True,

            "ontology_alignment_integrity_preserved":
                True,

            "ontology_alignment_provenance_preserved":
                True,

            "alignment_outcomes_preserved":
                True,

            "ambiguity_preserved":
                True,

            "conflicts_preserved":
                True,

            "uncertainty_preserved":
                True,

            "transfer_learning_architecture_defined":
                True,

            "transfer_learning_intake_validated":
                True,

            "transfer_scope_defined":
                True,

            "transfer_eligibility_evaluated":
                True,

            "transferable_knowledge_extracted":
                False,

            "knowledge_adaptation_performed":
                False,

            "transfer_learning_performed":
                False,

            "transfer_integrity_verification_performed":
                False,

            "transfer_provenance_built":
                False,

            "final_transfer_learning_result_built":
                False,

            "full_transfer_learning_certification_performed":
                False,

            "source_ontology_alignment_modified":
                False,

            "source_reasoning_modified":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,
        },

        "transfer_policy":
            "TRANSFER_SCOPE_AND_ELIGIBILITY_CONTRACT_DEFINED",

        "next_stage":
            "transferable_knowledge_extraction",
    }


# =====================================================================
# PATCH 4.6.23E ? Transferable Knowledge Extraction
# =====================================================================

def extract_transferable_knowledge_v1(
    scope_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Extract admissible source knowledge for Transfer Learning.

    E performs source-side extraction only.

    E does NOT:
    - adapt knowledge to the target,
    - execute transfer,
    - resolve ambiguity,
    - resolve conflicts,
    - invent unsupported knowledge,
    - write Semantic Memory,
    - make linking decisions.
    """

    from collections.abc import Mapping

    if not isinstance(
        scope_result,
        Mapping,
    ):
        raise TransferLearningError(
            "scope_result must be a mapping."
        )

    # -------------------------------------------------------------
    # Exact 4.6.23D lifecycle
    # -------------------------------------------------------------

    for field, expected in (
        (
            "schema_version",
            "transfer_scope_eligibility_result_v1",
        ),
        (
            "version",
            TRANSFER_LEARNING_VERSION,
        ),
        (
            "phase",
            TRANSFER_LEARNING_PHASE,
        ),
        (
            "patch",
            "4.6.23D",
        ),
        (
            "status",
            "TRANSFER_SCOPE_AND_ELIGIBILITY_DEFINED",
        ),
        (
            "transfer_policy",
            "TRANSFER_SCOPE_AND_ELIGIBILITY_CONTRACT_DEFINED",
        ),
        (
            "next_stage",
            "transferable_knowledge_extraction",
        ),
    ):

        if scope_result.get(field) != expected:
            raise TransferLearningError(
                f"Invalid 4.6.23D lifecycle field: {field}"
            )

    scope = scope_result.get(
        "transfer_scope"
    )

    source_intake = scope_result.get(
        "source_intake_result"
    )

    boundaries = scope_result.get(
        "processing_boundaries"
    )

    if not isinstance(
        scope,
        Mapping,
    ):
        raise TransferLearningError(
            "transfer_scope is missing."
        )

    if not isinstance(
        source_intake,
        Mapping,
    ):
        raise TransferLearningError(
            "source_intake_result is missing."
        )

    if not isinstance(
        boundaries,
        Mapping,
    ):
        raise TransferLearningError(
            "processing_boundaries are missing."
        )

    # -------------------------------------------------------------
    # Scope authority
    # -------------------------------------------------------------

    if scope.get(
        "scope_schema"
    ) != "transfer_scope_eligibility_v1":
        raise TransferLearningError(
            "Transfer scope schema drifted."
        )

    if scope.get(
        "scope_version"
    ) != "v1":
        raise TransferLearningError(
            "Transfer scope version drifted."
        )

    if scope.get(
        "scope_defined"
    ) is not True:
        raise TransferLearningError(
            "Transfer scope was not defined."
        )

    if scope.get(
        "eligibility_evaluated"
    ) is not True:
        raise TransferLearningError(
            "Transfer eligibility was not evaluated."
        )

    eligibility_state = scope.get(
        "eligibility_state"
    )

    if eligibility_state not in {
        "ELIGIBLE",
        "CONDITIONALLY_ELIGIBLE",
        "BLOCKED",
    }:
        raise TransferLearningError(
            "Invalid transfer eligibility state."
        )

    if eligibility_state == "BLOCKED":
        raise TransferLearningError(
            "Blocked transfer scope cannot enter knowledge extraction."
        )

    requested_families = scope.get(
        "requested_knowledge_families"
    )

    if not isinstance(
        requested_families,
        list,
    ) or not requested_families:
        raise TransferLearningError(
            "Requested knowledge families are missing."
        )

    # -------------------------------------------------------------
    # D boundary authority
    # -------------------------------------------------------------

    for field in (
        "certified_ontology_alignment_input_inspected",
        "certified_ontology_alignment_input_preserved",
        "ontology_alignment_integrity_preserved",
        "ontology_alignment_provenance_preserved",
        "alignment_outcomes_preserved",
        "ambiguity_preserved",
        "conflicts_preserved",
        "uncertainty_preserved",
        "transfer_learning_architecture_defined",
        "transfer_learning_intake_validated",
        "transfer_scope_defined",
        "transfer_eligibility_evaluated",
    ):

        if boundaries.get(field) is not True:
            raise TransferLearningError(
                f"Required 4.6.23D boundary is not True: {field}"
            )

    for field in (
        "transferable_knowledge_extracted",
        "knowledge_adaptation_performed",
        "transfer_learning_performed",
        "transfer_integrity_verification_performed",
        "transfer_provenance_built",
        "final_transfer_learning_result_built",
        "full_transfer_learning_certification_performed",
        "source_ontology_alignment_modified",
        "source_reasoning_modified",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if boundaries.get(field) is not False:
            raise TransferLearningError(
                f"Forbidden 4.6.23D boundary is not False: {field}"
            )

    # -------------------------------------------------------------
    # Recover certified ontology payload
    # -------------------------------------------------------------

    certified_final = source_intake.get(
        "certified_final_ontology_alignment_result"
    )

    if not isinstance(
        certified_final,
        Mapping,
    ):
        raise TransferLearningError(
            "Certified final ontology alignment result is missing."
        )

    canonical_concepts = certified_final.get(
        "canonical_concepts"
    )

    confirmed_alignments = certified_final.get(
        "confirmed_alignments"
    )

    unresolved_alignments = certified_final.get(
        "unresolved_alignments"
    )

    conflicting_alignments = certified_final.get(
        "conflicting_alignments"
    )

    ambiguity_registry = certified_final.get(
        "ambiguity_registry"
    )

    ontology_conflict_registry = certified_final.get(
        "ontology_conflict_registry"
    )

    mapping_traces = certified_final.get(
        "mapping_traces"
    )

    for name, value in (
        (
            "canonical_concepts",
            canonical_concepts,
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
        (
            "ambiguity_registry",
            ambiguity_registry,
        ),
        (
            "ontology_conflict_registry",
            ontology_conflict_registry,
        ),
        (
            "mapping_traces",
            mapping_traces,
        ),
    ):

        if not isinstance(
            value,
            list,
        ):
            raise TransferLearningError(
                name + " must be a list."
            )

    # -------------------------------------------------------------
    # Knowledge family extraction
    # -------------------------------------------------------------

    transferable_items = []
    restricted_items = []

    def add_transferable(
        family,
        source_kind,
        item,
        source_id,
        evidence_state,
    ):

        material = {
            "family":
                family,

            "source_kind":
                source_kind,

            "source_id":
                source_id,

            "source_item":
                copy.deepcopy(
                    item
                ),

            "evidence_state":
                evidence_state,

            "transferability":
                "TRANSFERABLE",

            "requires_target_adaptation":
                True,

            "source_preserved":
                True,
        }

        digest = hashlib.sha256(
            json.dumps(
                material,
                sort_keys=True,
                separators=(",", ":"),
                default=str,
            ).encode("utf-8")
        ).hexdigest()

        material[
            "transferable_knowledge_id"
        ] = (
            "transknow:v1:"
            + digest
        )

        material[
            "transferable_knowledge_digest"
        ] = digest

        transferable_items.append(
            material
        )

    def add_restricted(
        family,
        source_kind,
        item,
        source_id,
        restriction_reason,
    ):

        material = {
            "family":
                family,

            "source_kind":
                source_kind,

            "source_id":
                source_id,

            "source_item":
                copy.deepcopy(
                    item
                ),

            "transferability":
                "RESTRICTED",

            "restriction_reason":
                restriction_reason,

            "requires_target_adaptation":
                True,

            "source_preserved":
                True,
        }

        digest = hashlib.sha256(
            json.dumps(
                material,
                sort_keys=True,
                separators=(",", ":"),
                default=str,
            ).encode("utf-8")
        ).hexdigest()

        material[
            "restricted_knowledge_id"
        ] = (
            "transrestrict:v1:"
            + digest
        )

        material[
            "restricted_knowledge_digest"
        ] = digest

        restricted_items.append(
            material
        )

    # CANONICAL CONCEPTS
    if (
        "CANONICAL_CONCEPT_KNOWLEDGE"
        in requested_families
    ):

        for item in canonical_concepts:

            if not isinstance(
                item,
                Mapping,
            ):
                raise TransferLearningError(
                    "Invalid canonical concept entry."
                )

            concept_id = item.get(
                "canonical_concept_id"
            )

            if not isinstance(
                concept_id,
                str,
            ) or not concept_id:
                raise TransferLearningError(
                    "Canonical concept ID is required."
                )

            add_transferable(
                "CANONICAL_CONCEPT_KNOWLEDGE",
                "CANONICAL_CONCEPT",
                item,
                concept_id,
                "CERTIFIED_CANONICAL_CONCEPT",
            )

    # CONFIRMED ONTOLOGY ALIGNMENTS
    if (
        "ONTOLOGY_ALIGNMENT_KNOWLEDGE"
        in requested_families
    ):

        for item in confirmed_alignments:

            if not isinstance(
                item,
                Mapping,
            ):
                raise TransferLearningError(
                    "Invalid confirmed alignment entry."
                )

            alignment_id = item.get(
                "ontology_alignment_id"
            )

            if not isinstance(
                alignment_id,
                str,
            ) or not alignment_id:
                raise TransferLearningError(
                    "Confirmed alignment ID is required."
                )

            add_transferable(
                "ONTOLOGY_ALIGNMENT_KNOWLEDGE",
                "CONFIRMED_ONTOLOGY_ALIGNMENT",
                item,
                alignment_id,
                "CERTIFIED_CONFIRMED_ALIGNMENT",
            )

    # RELATIONSHIP KNOWLEDGE
    if (
        "SEMANTIC_RELATIONSHIP_PATTERN"
        in requested_families
    ):

        for item in confirmed_alignments:

            if not isinstance(
                item,
                Mapping,
            ):
                raise TransferLearningError(
                    "Invalid relationship source alignment."
                )

            alignment_id = item.get(
                "ontology_alignment_id"
            )

            if not isinstance(
                alignment_id,
                str,
            ) or not alignment_id:
                raise TransferLearningError(
                    "Relationship alignment ID is required."
                )

            add_transferable(
                "SEMANTIC_RELATIONSHIP_PATTERN",
                "ONTOLOGY_RELATIONSHIP",
                item,
                alignment_id,
                "CERTIFIED_RELATIONSHIP_EVIDENCE",
            )

    # -------------------------------------------------------------
    # Preserve unresolved / conflict / ambiguity as restricted
    # -------------------------------------------------------------

    for item in unresolved_alignments:

        if not isinstance(
            item,
            Mapping,
        ):
            raise TransferLearningError(
                "Invalid unresolved alignment."
            )

        add_restricted(
            "ONTOLOGY_ALIGNMENT_KNOWLEDGE",
            "UNRESOLVED_ONTOLOGY_ALIGNMENT",
            item,
            str(
                item.get(
                    "ontology_alignment_id"
                )
                or "UNRESOLVED"
            ),
            "UNRESOLVED_SOURCE_KNOWLEDGE",
        )

    for item in conflicting_alignments:

        if not isinstance(
            item,
            Mapping,
        ):
            raise TransferLearningError(
                "Invalid conflicting alignment."
            )

        add_restricted(
            "CONFLICT_PATTERN",
            "CONFLICTING_ONTOLOGY_ALIGNMENT",
            item,
            str(
                item.get(
                    "ontology_alignment_id"
                )
                or "CONFLICT"
            ),
            "CONFLICTING_SOURCE_KNOWLEDGE",
        )

    for item in ambiguity_registry:

        if not isinstance(
            item,
            Mapping,
        ):
            raise TransferLearningError(
                "Invalid ambiguity registry entry."
            )

        add_restricted(
            "AMBIGUITY_PATTERN",
            "ONTOLOGY_AMBIGUITY",
            item,
            str(
                item.get(
                    "ambiguity_id"
                )
                or item.get(
                    "ontology_alignment_id"
                )
                or "AMBIGUITY"
            ),
            "AMBIGUOUS_SOURCE_KNOWLEDGE",
        )

    for item in ontology_conflict_registry:

        if not isinstance(
            item,
            Mapping,
        ):
            raise TransferLearningError(
                "Invalid ontology conflict registry entry."
            )

        add_restricted(
            "CONFLICT_PATTERN",
            "ONTOLOGY_CONFLICT",
            item,
            str(
                item.get(
                    "conflict_id"
                )
                or item.get(
                    "ontology_alignment_id"
                )
                or "ONTOLOGY_CONFLICT"
            ),
            "ONTOLOGY_CONFLICT_REQUIRES_PRESERVATION",
        )

    # -------------------------------------------------------------
    # Provenance binding
    # -------------------------------------------------------------

    alignment_trace_ids = {}

    for trace in mapping_traces:

        if not isinstance(
            trace,
            Mapping,
        ):
            raise TransferLearningError(
                "Invalid mapping trace."
            )

        alignment_id = trace.get(
            "ontology_alignment_id"
        )

        trace_id = (
            trace.get(
                "ontology_trace_id"
            )
            or trace.get(
                "mapping_trace_id"
            )
        )

        if (
            isinstance(
                alignment_id,
                str,
            )
            and alignment_id
            and isinstance(
                trace_id,
                str,
            )
            and trace_id
        ):
            alignment_trace_ids[
                alignment_id
            ] = trace_id

    for item in transferable_items:

        source_id = item.get(
            "source_id"
        )

        if source_id in alignment_trace_ids:
            item[
                "source_mapping_trace_id"
            ] = alignment_trace_ids[
                source_id
            ]

    # -------------------------------------------------------------
    # Deterministic extraction package
    # -------------------------------------------------------------

    transferable_items.sort(
        key=lambda x: (
            x[
                "family"
            ],
            x[
                "source_kind"
            ],
            x[
                "source_id"
            ],
            x[
                "transferable_knowledge_id"
            ],
        )
    )

    restricted_items.sort(
        key=lambda x: (
            x[
                "family"
            ],
            x[
                "source_kind"
            ],
            x[
                "source_id"
            ],
            x[
                "restricted_knowledge_id"
            ],
        )
    )

    package_material = {
        "transfer_scope_id":
            scope.get(
                "transfer_scope_id"
            ),

        "transfer_scope_digest":
            scope.get(
                "transfer_scope_digest"
            ),

        "eligibility_state":
            eligibility_state,

        "requested_knowledge_families":
            sorted(
                requested_families
            ),

        "transferable_items":
            transferable_items,

        "restricted_items":
            restricted_items,
    }

    package_digest = hashlib.sha256(
        json.dumps(
            package_material,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        ).encode("utf-8")
    ).hexdigest()

    extraction_package = {
        "extraction_schema":
            "transferable_knowledge_extraction_v1",

        "extraction_version":
            "v1",

        "extraction_package_id":
            "transextract:v1:"
            + package_digest,

        "extraction_package_digest":
            package_digest,

        "transfer_scope_id":
            scope[
                "transfer_scope_id"
            ],

        "transfer_scope_digest":
            scope[
                "transfer_scope_digest"
            ],

        "eligibility_state":
            eligibility_state,

        "requested_knowledge_families":
            sorted(
                requested_families
            ),

        "transferable_knowledge_count":
            len(
                transferable_items
            ),

        "restricted_knowledge_count":
            len(
                restricted_items
            ),

        "transferable_knowledge":
            transferable_items,

        "restricted_knowledge":
            restricted_items,

        "canonical_concept_knowledge_count":
            sum(
                1
                for item
                in transferable_items
                if item[
                    "family"
                ]
                == "CANONICAL_CONCEPT_KNOWLEDGE"
            ),

        "ontology_alignment_knowledge_count":
            sum(
                1
                for item
                in transferable_items
                if item[
                    "family"
                ]
                == "ONTOLOGY_ALIGNMENT_KNOWLEDGE"
            ),

        "semantic_relationship_pattern_count":
            sum(
                1
                for item
                in transferable_items
                if item[
                    "family"
                ]
                == "SEMANTIC_RELATIONSHIP_PATTERN"
            ),

        "source_scope_preserved":
            True,

        "source_ontology_preserved":
            True,

        "source_provenance_preserved":
            True,

        "ambiguity_preserved":
            True,

        "conflicts_preserved":
            True,

        "uncertainty_preserved":
            True,

        "unsupported_knowledge_invented":
            False,

        "silent_resolution_performed":
            False,

        "knowledge_adaptation_performed":
            False,

        "transfer_learning_performed":
            False,

        "semantic_memory_written":
            False,

        "linking_decisions_performed":
            False,
    }

    return {
        "schema_version":
            "transferable_knowledge_extraction_result_v1",

        "version":
            TRANSFER_LEARNING_VERSION,

        "phase":
            TRANSFER_LEARNING_PHASE,

        "patch":
            "4.6.23E",

        "status":
            "TRANSFERABLE_KNOWLEDGE_EXTRACTED",

        "workspace_id":
            scope_result.get(
                "workspace_id"
            ),

        "transferable_knowledge_extraction":
            extraction_package,

        "source_scope_result":
            deepcopy(
                dict(scope_result)
            ),

        "processing_boundaries": {
            "certified_ontology_alignment_input_inspected":
                True,

            "certified_ontology_alignment_input_preserved":
                True,

            "ontology_alignment_integrity_preserved":
                True,

            "ontology_alignment_provenance_preserved":
                True,

            "alignment_outcomes_preserved":
                True,

            "ambiguity_preserved":
                True,

            "conflicts_preserved":
                True,

            "uncertainty_preserved":
                True,

            "transfer_learning_architecture_defined":
                True,

            "transfer_learning_intake_validated":
                True,

            "transfer_scope_defined":
                True,

            "transfer_eligibility_evaluated":
                True,

            "transferable_knowledge_extracted":
                True,

            "knowledge_adaptation_performed":
                False,

            "transfer_learning_performed":
                False,

            "transfer_integrity_verification_performed":
                False,

            "transfer_provenance_built":
                False,

            "final_transfer_learning_result_built":
                False,

            "full_transfer_learning_certification_performed":
                False,

            "source_ontology_alignment_modified":
                False,

            "source_reasoning_modified":
                False,

            "unsupported_knowledge_invented":
                False,

            "silent_resolution_performed":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,
        },

        "transfer_policy":
            "CERTIFIED_TRANSFERABLE_KNOWLEDGE_EXTRACTED",

        "next_stage":
            "source_to_target_knowledge_adaptation",
    }


# =====================================================================
# PATCH 4.6.23F ? Source-to-Target Knowledge Adaptation
# =====================================================================

def adapt_source_to_target_knowledge_v1(
    extraction_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Adapt certified transferable source knowledge into target-context
    candidates.

    F performs target adaptation only.

    It does NOT:
    - execute final transfer,
    - approve negative-transfer risk,
    - resolve source ambiguity/conflicts,
    - invent unsupported knowledge,
    - write Semantic Memory,
    - make linking decisions.
    """

    from collections.abc import Mapping

    if not isinstance(
        extraction_result,
        Mapping,
    ):
        raise TransferLearningError(
            "extraction_result must be a mapping."
        )

    # -------------------------------------------------------------
    # Exact 4.6.23E lifecycle
    # -------------------------------------------------------------

    for field, expected in (
        (
            "schema_version",
            "transferable_knowledge_extraction_result_v1",
        ),
        (
            "version",
            TRANSFER_LEARNING_VERSION,
        ),
        (
            "phase",
            TRANSFER_LEARNING_PHASE,
        ),
        (
            "patch",
            "4.6.23E",
        ),
        (
            "status",
            "TRANSFERABLE_KNOWLEDGE_EXTRACTED",
        ),
        (
            "transfer_policy",
            "CERTIFIED_TRANSFERABLE_KNOWLEDGE_EXTRACTED",
        ),
        (
            "next_stage",
            "source_to_target_knowledge_adaptation",
        ),
    ):

        if extraction_result.get(field) != expected:
            raise TransferLearningError(
                f"Invalid 4.6.23E lifecycle field: {field}"
            )

    extraction = extraction_result.get(
        "transferable_knowledge_extraction"
    )

    source_scope_result = extraction_result.get(
        "source_scope_result"
    )

    boundaries = extraction_result.get(
        "processing_boundaries"
    )

    for name, value in (
        (
            "transferable_knowledge_extraction",
            extraction,
        ),
        (
            "source_scope_result",
            source_scope_result,
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
            raise TransferLearningError(
                name + " is missing."
            )

    # -------------------------------------------------------------
    # E boundary authority
    # -------------------------------------------------------------

    for field in (
        "certified_ontology_alignment_input_inspected",
        "certified_ontology_alignment_input_preserved",
        "ontology_alignment_integrity_preserved",
        "ontology_alignment_provenance_preserved",
        "alignment_outcomes_preserved",
        "ambiguity_preserved",
        "conflicts_preserved",
        "uncertainty_preserved",
        "transfer_learning_architecture_defined",
        "transfer_learning_intake_validated",
        "transfer_scope_defined",
        "transfer_eligibility_evaluated",
        "transferable_knowledge_extracted",
    ):

        if boundaries.get(field) is not True:
            raise TransferLearningError(
                f"Required 4.6.23E boundary is not True: {field}"
            )

    for field in (
        "knowledge_adaptation_performed",
        "transfer_learning_performed",
        "transfer_integrity_verification_performed",
        "transfer_provenance_built",
        "final_transfer_learning_result_built",
        "full_transfer_learning_certification_performed",
        "source_ontology_alignment_modified",
        "source_reasoning_modified",
        "unsupported_knowledge_invented",
        "silent_resolution_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if boundaries.get(field) is not False:
            raise TransferLearningError(
                f"Forbidden 4.6.23E boundary is not False: {field}"
            )

    # -------------------------------------------------------------
    # Extraction package authority
    # -------------------------------------------------------------

    for field, expected in (
        (
            "extraction_schema",
            "transferable_knowledge_extraction_v1",
        ),
        (
            "extraction_version",
            "v1",
        ),
    ):

        if extraction.get(field) != expected:
            raise TransferLearningError(
                f"Extraction package drifted: {field}"
            )

    if extraction.get(
        "source_scope_preserved"
    ) is not True:
        raise TransferLearningError(
            "Source scope preservation is required."
        )

    if extraction.get(
        "source_ontology_preserved"
    ) is not True:
        raise TransferLearningError(
            "Source ontology preservation is required."
        )

    if extraction.get(
        "source_provenance_preserved"
    ) is not True:
        raise TransferLearningError(
            "Source provenance preservation is required."
        )

    for field in (
        "unsupported_knowledge_invented",
        "silent_resolution_performed",
        "knowledge_adaptation_performed",
        "transfer_learning_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if extraction.get(field) is not False:
            raise TransferLearningError(
                f"Forbidden extraction state is not False: {field}"
            )

    transferable_items = extraction.get(
        "transferable_knowledge"
    )

    restricted_items = extraction.get(
        "restricted_knowledge"
    )

    if not isinstance(
        transferable_items,
        list,
    ):
        raise TransferLearningError(
            "transferable_knowledge must be a list."
        )

    if not isinstance(
        restricted_items,
        list,
    ):
        raise TransferLearningError(
            "restricted_knowledge must be a list."
        )

    if extraction.get(
        "transferable_knowledge_count"
    ) != len(
        transferable_items
    ):
        raise TransferLearningError(
            "Transferable knowledge count drifted."
        )

    if extraction.get(
        "restricted_knowledge_count"
    ) != len(
        restricted_items
    ):
        raise TransferLearningError(
            "Restricted knowledge count drifted."
        )

    # -------------------------------------------------------------
    # Recover target scope/context
    # -------------------------------------------------------------

    transfer_scope = source_scope_result.get(
        "transfer_scope"
    )

    target_context = source_scope_result.get(
        "target_context"
    )

    if not isinstance(
        transfer_scope,
        Mapping,
    ):
        raise TransferLearningError(
            "Transfer scope is missing."
        )

    if not isinstance(
        target_context,
        Mapping,
    ):
        raise TransferLearningError(
            "Target context is missing."
        )

    if transfer_scope.get(
        "scope_defined"
    ) is not True:
        raise TransferLearningError(
            "Transfer scope must be defined."
        )

    eligibility_state = transfer_scope.get(
        "eligibility_state"
    )

    if eligibility_state not in {
        "ELIGIBLE",
        "CONDITIONALLY_ELIGIBLE",
    }:
        raise TransferLearningError(
            "Only eligible or conditionally eligible scope may adapt."
        )

    transfer_context_mode = transfer_scope.get(
        "transfer_context_mode"
    )

    source_domain = transfer_scope.get(
        "source_domain"
    )

    target_domain = transfer_scope.get(
        "target_domain"
    )

    target_topic = transfer_scope.get(
        "target_topic"
    )

    target_context_id = transfer_scope.get(
        "target_context_id"
    )

    target_workspace_id = transfer_scope.get(
        "target_workspace_id"
    )

    for field_name, value in (
        (
            "transfer_context_mode",
            transfer_context_mode,
        ),
        (
            "source_domain",
            source_domain,
        ),
        (
            "target_domain",
            target_domain,
        ),
        (
            "target_topic",
            target_topic,
        ),
        (
            "target_context_id",
            target_context_id,
        ),
        (
            "target_workspace_id",
            target_workspace_id,
        ),
    ):

        if not isinstance(
            value,
            str,
        ) or not value:
            raise TransferLearningError(
                field_name + " is required."
            )

    # -------------------------------------------------------------
    # Compatibility framework
    # -------------------------------------------------------------

    dimensions = (
        "CONCEPT_COMPATIBILITY",
        "ONTOLOGY_COMPATIBILITY",
        "DOMAIN_COMPATIBILITY",
        "TOPIC_COMPATIBILITY",
        "CONTEXT_COMPATIBILITY",
        "RELATIONSHIP_COMPATIBILITY",
        "EVIDENCE_COMPATIBILITY",
        "TEMPORAL_COMPATIBILITY",
        "UNCERTAINTY_COMPATIBILITY",
        "CONFLICT_COMPATIBILITY",
    )

    def domain_score():

        if source_domain == target_domain:
            return 1.0

        if transfer_context_mode == "RELATED_DOMAIN":
            return 0.80

        if transfer_context_mode == "CROSS_DOMAIN_RESTRICTED":
            return 0.60

        return 0.90

    def base_scores(item):

        family = item.get(
            "family"
        )

        scores = {
            "CONCEPT_COMPATIBILITY":
                0.90,

            "ONTOLOGY_COMPATIBILITY":
                0.90,

            "DOMAIN_COMPATIBILITY":
                domain_score(),

            "TOPIC_COMPATIBILITY":
                0.85,

            "CONTEXT_COMPATIBILITY":
                0.85,

            "RELATIONSHIP_COMPATIBILITY":
                0.80,

            "EVIDENCE_COMPATIBILITY":
                0.95,

            "TEMPORAL_COMPATIBILITY":
                0.80,

            "UNCERTAINTY_COMPATIBILITY":
                0.90,

            "CONFLICT_COMPATIBILITY":
                0.90,
        }

        if family == "CANONICAL_CONCEPT_KNOWLEDGE":
            scores[
                "CONCEPT_COMPATIBILITY"
            ] = 1.0

        elif family == "ONTOLOGY_ALIGNMENT_KNOWLEDGE":
            scores[
                "ONTOLOGY_COMPATIBILITY"
            ] = 1.0

        elif family == "SEMANTIC_RELATIONSHIP_PATTERN":
            scores[
                "RELATIONSHIP_COMPATIBILITY"
            ] = 1.0

        return scores

    # -------------------------------------------------------------
    # Adapt transferable knowledge
    # -------------------------------------------------------------

    adapted_candidates = []

    for item in transferable_items:

        if not isinstance(
            item,
            Mapping,
        ):
            raise TransferLearningError(
                "Invalid transferable knowledge item."
            )

        if item.get(
            "transferability"
        ) != "TRANSFERABLE":
            raise TransferLearningError(
                "Only transferable items may enter adaptation."
            )

        source_knowledge_id = item.get(
            "transferable_knowledge_id"
        )

        source_knowledge_digest = item.get(
            "transferable_knowledge_digest"
        )

        if not isinstance(
            source_knowledge_id,
            str,
        ) or not source_knowledge_id.startswith(
            "transknow:v1:"
        ):
            raise TransferLearningError(
                "Invalid transferable knowledge ID."
            )

        if not isinstance(
            source_knowledge_digest,
            str,
        ) or len(
            source_knowledge_digest
        ) != 64:
            raise TransferLearningError(
                "Invalid transferable knowledge digest."
            )

        scores = base_scores(
            item
        )

        if set(
            scores
        ) != set(
            dimensions
        ):
            raise TransferLearningError(
                "Adaptation compatibility dimensions drifted."
            )

        compatibility_score = round(
            sum(
                scores.values()
            )
            / len(
                scores
            ),
            6,
        )

        if compatibility_score >= 0.90:
            adaptation_state = "HIGH_COMPATIBILITY"

        elif compatibility_score >= 0.75:
            adaptation_state = "MODERATE_COMPATIBILITY"

        elif compatibility_score >= 0.60:
            adaptation_state = "LOW_COMPATIBILITY"

        else:
            adaptation_state = "INCOMPATIBLE"

        candidate_material = {
            "source_transferable_knowledge_id":
                source_knowledge_id,

            "source_transferable_knowledge_digest":
                source_knowledge_digest,

            "family":
                item[
                    "family"
                ],

            "source_kind":
                item[
                    "source_kind"
                ],

            "source_id":
                item[
                    "source_id"
                ],

            "target_workspace_id":
                target_workspace_id,

            "target_context_id":
                target_context_id,

            "target_domain":
                target_domain,

            "target_topic":
                target_topic,

            "transfer_context_mode":
                transfer_context_mode,

            "compatibility_dimensions":
                scores,

            "compatibility_score":
                compatibility_score,

            "adaptation_state":
                adaptation_state,

            "source_item":
                copy.deepcopy(
                    item[
                        "source_item"
                    ]
                ),

            "source_mapping_trace_id":
                item.get(
                    "source_mapping_trace_id"
                ),

            "source_preserved":
                True,

            "target_context_bound":
                True,

            "requires_transfer_execution":
                True,

            "negative_transfer_guard_pending":
                True,
        }

        digest = hashlib.sha256(
            json.dumps(
                candidate_material,
                sort_keys=True,
                separators=(",", ":"),
                default=str,
            ).encode("utf-8")
        ).hexdigest()

        candidate_material[
            "adapted_knowledge_id"
        ] = (
            "transadapt:v1:"
            + digest
        )

        candidate_material[
            "adapted_knowledge_digest"
        ] = digest

        adapted_candidates.append(
            candidate_material
        )

    # -------------------------------------------------------------
    # Restricted knowledge stays restricted
    # -------------------------------------------------------------

    preserved_restricted = []

    for item in restricted_items:

        if not isinstance(
            item,
            Mapping,
        ):
            raise TransferLearningError(
                "Invalid restricted knowledge item."
            )

        if item.get(
            "transferability"
        ) != "RESTRICTED":
            raise TransferLearningError(
                "Restricted knowledge status drifted."
            )

        preserved = copy.deepcopy(
            dict(item)
        )

        preserved[
            "target_adaptation_performed"
        ] = False

        preserved[
            "negative_transfer_guard_required"
        ] = True

        preserved[
            "transfer_execution_allowed"
        ] = False

        preserved_restricted.append(
            preserved
        )

    adapted_candidates.sort(
        key=lambda x: (
            x[
                "family"
            ],
            x[
                "source_kind"
            ],
            x[
                "source_id"
            ],
            x[
                "adapted_knowledge_id"
            ],
        )
    )

    preserved_restricted.sort(
        key=lambda x: (
            x[
                "family"
            ],
            x[
                "source_kind"
            ],
            x[
                "source_id"
            ],
            x[
                "restricted_knowledge_id"
            ],
        )
    )

    # -------------------------------------------------------------
    # Deterministic adaptation package
    # -------------------------------------------------------------

    package_material = {
        "source_extraction_package_id":
            extraction[
                "extraction_package_id"
            ],

        "source_extraction_package_digest":
            extraction[
                "extraction_package_digest"
            ],

        "transfer_scope_id":
            extraction[
                "transfer_scope_id"
            ],

        "target_workspace_id":
            target_workspace_id,

        "target_context_id":
            target_context_id,

        "target_domain":
            target_domain,

        "target_topic":
            target_topic,

        "transfer_context_mode":
            transfer_context_mode,

        "adapted_candidates":
            adapted_candidates,

        "preserved_restricted_knowledge":
            preserved_restricted,
    }

    package_digest = hashlib.sha256(
        json.dumps(
            package_material,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        ).encode("utf-8")
    ).hexdigest()

    adaptation_package = {
        "adaptation_schema":
            "source_to_target_knowledge_adaptation_v1",

        "adaptation_version":
            "v1",

        "adaptation_package_id":
            "transadaptpkg:v1:"
            + package_digest,

        "adaptation_package_digest":
            package_digest,

        "source_extraction_package_id":
            extraction[
                "extraction_package_id"
            ],

        "source_extraction_package_digest":
            extraction[
                "extraction_package_digest"
            ],

        "transfer_scope_id":
            extraction[
                "transfer_scope_id"
            ],

        "target_workspace_id":
            target_workspace_id,

        "target_context_id":
            target_context_id,

        "target_domain":
            target_domain,

        "target_topic":
            target_topic,

        "transfer_context_mode":
            transfer_context_mode,

        "adapted_candidate_count":
            len(
                adapted_candidates
            ),

        "restricted_knowledge_count":
            len(
                preserved_restricted
            ),

        "adapted_candidates":
            adapted_candidates,

        "preserved_restricted_knowledge":
            preserved_restricted,

        "compatibility_dimensions":
            list(
                dimensions
            ),

        "source_extraction_preserved":
            True,

        "source_scope_preserved":
            True,

        "source_ontology_preserved":
            True,

        "source_provenance_preserved":
            True,

        "ambiguity_preserved":
            True,

        "conflicts_preserved":
            True,

        "uncertainty_preserved":
            True,

        "restricted_knowledge_not_adapted":
            True,

        "unsupported_knowledge_invented":
            False,

        "silent_resolution_performed":
            False,

        "knowledge_adaptation_performed":
            True,

        "transfer_learning_performed":
            False,

        "negative_transfer_guard_performed":
            False,

        "semantic_memory_written":
            False,

        "linking_decisions_performed":
            False,
    }

    return {
        "schema_version":
            "source_to_target_knowledge_adaptation_result_v1",

        "version":
            TRANSFER_LEARNING_VERSION,

        "phase":
            TRANSFER_LEARNING_PHASE,

        "patch":
            "4.6.23F",

        "status":
            "SOURCE_TO_TARGET_KNOWLEDGE_ADAPTED",

        "workspace_id":
            extraction_result.get(
                "workspace_id"
            ),

        "knowledge_adaptation":
            adaptation_package,

        "source_extraction_result":
            deepcopy(
                dict(extraction_result)
            ),

        "processing_boundaries": {
            "certified_ontology_alignment_input_inspected":
                True,

            "certified_ontology_alignment_input_preserved":
                True,

            "ontology_alignment_integrity_preserved":
                True,

            "ontology_alignment_provenance_preserved":
                True,

            "alignment_outcomes_preserved":
                True,

            "ambiguity_preserved":
                True,

            "conflicts_preserved":
                True,

            "uncertainty_preserved":
                True,

            "transfer_learning_architecture_defined":
                True,

            "transfer_learning_intake_validated":
                True,

            "transfer_scope_defined":
                True,

            "transfer_eligibility_evaluated":
                True,

            "transferable_knowledge_extracted":
                True,

            "knowledge_adaptation_performed":
                True,

            "transfer_learning_performed":
                False,

            "transfer_integrity_verification_performed":
                False,

            "transfer_provenance_built":
                False,

            "final_transfer_learning_result_built":
                False,

            "full_transfer_learning_certification_performed":
                False,

            "source_ontology_alignment_modified":
                False,

            "source_reasoning_modified":
                False,

            "unsupported_knowledge_invented":
                False,

            "silent_resolution_performed":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,
        },

        "transfer_policy":
            "SOURCE_TO_TARGET_KNOWLEDGE_ADAPTATION_COMPLETE",

        "next_stage":
            "transfer_learning_execution",
    }


# =====================================================================
# PATCH 4.6.23G ? Transfer Learning Execution
# =====================================================================

def execute_transfer_learning_v1(
    adaptation_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Execute provisional Transfer Learning decisions.

    G performs the semantic transfer operation over certified,
    target-adapted candidates.

    The execution is still subject to 4.6.23H negative-transfer and
    integrity certification.

    G does NOT:
    - finalize a transfer,
    - bypass the negative-transfer guard,
    - transfer restricted knowledge,
    - resolve ambiguity/conflict,
    - invent unsupported knowledge,
    - write Semantic Memory,
    - make linking decisions.
    """

    from collections.abc import Mapping

    if not isinstance(
        adaptation_result,
        Mapping,
    ):
        raise TransferLearningError(
            "adaptation_result must be a mapping."
        )

    # -------------------------------------------------------------
    # Exact 4.6.23F lifecycle
    # -------------------------------------------------------------

    for field, expected in (
        (
            "schema_version",
            "source_to_target_knowledge_adaptation_result_v1",
        ),
        (
            "version",
            TRANSFER_LEARNING_VERSION,
        ),
        (
            "phase",
            TRANSFER_LEARNING_PHASE,
        ),
        (
            "patch",
            "4.6.23F",
        ),
        (
            "status",
            "SOURCE_TO_TARGET_KNOWLEDGE_ADAPTED",
        ),
        (
            "transfer_policy",
            "SOURCE_TO_TARGET_KNOWLEDGE_ADAPTATION_COMPLETE",
        ),
        (
            "next_stage",
            "transfer_learning_execution",
        ),
    ):

        if adaptation_result.get(field) != expected:
            raise TransferLearningError(
                f"Invalid 4.6.23F lifecycle field: {field}"
            )

    adaptation = adaptation_result.get(
        "knowledge_adaptation"
    )

    boundaries = adaptation_result.get(
        "processing_boundaries"
    )

    if not isinstance(
        adaptation,
        Mapping,
    ):
        raise TransferLearningError(
            "knowledge_adaptation is missing."
        )

    if not isinstance(
        boundaries,
        Mapping,
    ):
        raise TransferLearningError(
            "processing_boundaries are missing."
        )

    # -------------------------------------------------------------
    # F boundary authority
    # -------------------------------------------------------------

    for field in (
        "certified_ontology_alignment_input_inspected",
        "certified_ontology_alignment_input_preserved",
        "ontology_alignment_integrity_preserved",
        "ontology_alignment_provenance_preserved",
        "alignment_outcomes_preserved",
        "ambiguity_preserved",
        "conflicts_preserved",
        "uncertainty_preserved",
        "transfer_learning_architecture_defined",
        "transfer_learning_intake_validated",
        "transfer_scope_defined",
        "transfer_eligibility_evaluated",
        "transferable_knowledge_extracted",
        "knowledge_adaptation_performed",
    ):

        if boundaries.get(field) is not True:
            raise TransferLearningError(
                f"Required 4.6.23F boundary is not True: {field}"
            )

    for field in (
        "transfer_learning_performed",
        "transfer_integrity_verification_performed",
        "transfer_provenance_built",
        "final_transfer_learning_result_built",
        "full_transfer_learning_certification_performed",
        "source_ontology_alignment_modified",
        "source_reasoning_modified",
        "unsupported_knowledge_invented",
        "silent_resolution_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if boundaries.get(field) is not False:
            raise TransferLearningError(
                f"Forbidden 4.6.23F boundary is not False: {field}"
            )

    # -------------------------------------------------------------
    # Adaptation package authority
    # -------------------------------------------------------------

    for field, expected in (
        (
            "adaptation_schema",
            "source_to_target_knowledge_adaptation_v1",
        ),
        (
            "adaptation_version",
            "v1",
        ),
    ):

        if adaptation.get(field) != expected:
            raise TransferLearningError(
                f"Adaptation package drifted: {field}"
            )

    for field in (
        "source_extraction_preserved",
        "source_scope_preserved",
        "source_ontology_preserved",
        "source_provenance_preserved",
        "ambiguity_preserved",
        "conflicts_preserved",
        "uncertainty_preserved",
        "restricted_knowledge_not_adapted",
        "knowledge_adaptation_performed",
    ):

        if adaptation.get(field) is not True:
            raise TransferLearningError(
                f"Required adaptation field is not True: {field}"
            )

    for field in (
        "unsupported_knowledge_invented",
        "silent_resolution_performed",
        "transfer_learning_performed",
        "negative_transfer_guard_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if adaptation.get(field) is not False:
            raise TransferLearningError(
                f"Forbidden adaptation field is not False: {field}"
            )

    adapted_candidates = adaptation.get(
        "adapted_candidates"
    )

    restricted_knowledge = adaptation.get(
        "preserved_restricted_knowledge"
    )

    if not isinstance(
        adapted_candidates,
        list,
    ):
        raise TransferLearningError(
            "adapted_candidates must be a list."
        )

    if not isinstance(
        restricted_knowledge,
        list,
    ):
        raise TransferLearningError(
            "preserved_restricted_knowledge must be a list."
        )

    if adaptation.get(
        "adapted_candidate_count"
    ) != len(
        adapted_candidates
    ):
        raise TransferLearningError(
            "Adapted candidate count drifted."
        )

    if adaptation.get(
        "restricted_knowledge_count"
    ) != len(
        restricted_knowledge
    ):
        raise TransferLearningError(
            "Restricted knowledge count drifted."
        )

    # -------------------------------------------------------------
    # Execute provisional transfers
    # -------------------------------------------------------------

    execution_records = []

    for candidate in adapted_candidates:

        if not isinstance(
            candidate,
            Mapping,
        ):
            raise TransferLearningError(
                "Invalid adapted candidate."
            )

        adapted_id = candidate.get(
            "adapted_knowledge_id"
        )

        adapted_digest = candidate.get(
            "adapted_knowledge_digest"
        )

        compatibility_score = candidate.get(
            "compatibility_score"
        )

        adaptation_state = candidate.get(
            "adaptation_state"
        )

        if not isinstance(
            adapted_id,
            str,
        ) or not adapted_id.startswith(
            "transadapt:v1:"
        ):
            raise TransferLearningError(
                "Invalid adapted knowledge ID."
            )

        if not isinstance(
            adapted_digest,
            str,
        ) or len(
            adapted_digest
        ) != 64:
            raise TransferLearningError(
                "Invalid adapted knowledge digest."
            )

        if not isinstance(
            compatibility_score,
            (int, float),
        ):
            raise TransferLearningError(
                "Compatibility score is invalid."
            )

        compatibility_score = float(
            compatibility_score
        )

        if not (
            0.0
            <= compatibility_score
            <= 1.0
        ):
            raise TransferLearningError(
                "Compatibility score is outside 0..1."
            )

        if candidate.get(
            "target_context_bound"
        ) is not True:
            raise TransferLearningError(
                "Candidate is not bound to a target context."
            )

        if candidate.get(
            "requires_transfer_execution"
        ) is not True:
            raise TransferLearningError(
                "Candidate does not authorize transfer execution."
            )

        if candidate.get(
            "negative_transfer_guard_pending"
        ) is not True:
            raise TransferLearningError(
                "Negative-transfer guard must remain pending."
            )

        # ---------------------------------------------------------
        # Provisional execution policy
        # ---------------------------------------------------------

        if (
            adaptation_state
            == "HIGH_COMPATIBILITY"
            and compatibility_score >= 0.90
        ):
            execution_state = "TRANSFERRED"

            execution_reason = (
                "HIGH_COMPATIBILITY_TRANSFER"
            )

        elif (
            adaptation_state
            in {
                "HIGH_COMPATIBILITY",
                "MODERATE_COMPATIBILITY",
            }
            and compatibility_score >= 0.75
        ):
            execution_state = "CONDITIONAL_TRANSFER"

            execution_reason = (
                "COMPATIBLE_TRANSFER_REQUIRES_GUARD"
            )

        elif compatibility_score >= 0.60:
            execution_state = "NOT_TRANSFERRED"

            execution_reason = (
                "LOW_COMPATIBILITY_REQUIRES_REVIEW"
            )

        else:
            execution_state = "NOT_TRANSFERRED"

            execution_reason = (
                "INSUFFICIENT_TARGET_COMPATIBILITY"
            )

        execution_material = {
            "source_adapted_knowledge_id":
                adapted_id,

            "source_adapted_knowledge_digest":
                adapted_digest,

            "family":
                candidate.get(
                    "family"
                ),

            "source_kind":
                candidate.get(
                    "source_kind"
                ),

            "source_id":
                candidate.get(
                    "source_id"
                ),

            "target_workspace_id":
                candidate.get(
                    "target_workspace_id"
                ),

            "target_context_id":
                candidate.get(
                    "target_context_id"
                ),

            "target_domain":
                candidate.get(
                    "target_domain"
                ),

            "target_topic":
                candidate.get(
                    "target_topic"
                ),

            "transfer_context_mode":
                candidate.get(
                    "transfer_context_mode"
                ),

            "compatibility_score":
                compatibility_score,

            "adaptation_state":
                adaptation_state,

            "execution_state":
                execution_state,

            "execution_reason":
                execution_reason,

            "transferred_payload":
                copy.deepcopy(
                    candidate.get(
                        "source_item"
                    )
                )
                if execution_state
                in {
                    "TRANSFERRED",
                    "CONDITIONAL_TRANSFER",
                }
                else None,

            "source_mapping_trace_id":
                candidate.get(
                    "source_mapping_trace_id"
                ),

            "source_preserved":
                True,

            "target_context_preserved":
                True,

            "provisional_execution":
                True,

            "negative_transfer_guard_pending":
                True,

            "final_transfer_approved":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,
        }

        digest = hashlib.sha256(
            json.dumps(
                execution_material,
                sort_keys=True,
                separators=(",", ":"),
                default=str,
            ).encode("utf-8")
        ).hexdigest()

        execution_material[
            "transfer_execution_id"
        ] = (
            "transexec:v1:"
            + digest
        )

        execution_material[
            "transfer_execution_digest"
        ] = digest

        execution_records.append(
            execution_material
        )

    # -------------------------------------------------------------
    # Restricted knowledge remains blocked
    # -------------------------------------------------------------

    restricted_execution_records = []

    for item in restricted_knowledge:

        if not isinstance(
            item,
            Mapping,
        ):
            raise TransferLearningError(
                "Invalid restricted knowledge entry."
            )

        if item.get(
            "transferability"
        ) != "RESTRICTED":
            raise TransferLearningError(
                "Restricted knowledge state drifted."
            )

        if item.get(
            "transfer_execution_allowed"
        ) is not False:
            raise TransferLearningError(
                "Restricted knowledge cannot execute."
            )

        restricted_record = {
            "restricted_knowledge_id":
                item.get(
                    "restricted_knowledge_id"
                ),

            "family":
                item.get(
                    "family"
                ),

            "source_kind":
                item.get(
                    "source_kind"
                ),

            "source_id":
                item.get(
                    "source_id"
                ),

            "restriction_reason":
                item.get(
                    "restriction_reason"
                ),

            "execution_state":
                "NOT_TRANSFERRED",

            "execution_reason":
                "RESTRICTED_SOURCE_KNOWLEDGE",

            "provisional_execution":
                False,

            "negative_transfer_guard_required":
                True,

            "final_transfer_approved":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,
        }

        restricted_execution_records.append(
            restricted_record
        )

    execution_records.sort(
        key=lambda x: (
            str(
                x.get(
                    "family"
                )
            ),
            str(
                x.get(
                    "source_id"
                )
            ),
            x[
                "transfer_execution_id"
            ],
        )
    )

    restricted_execution_records.sort(
        key=lambda x: (
            str(
                x.get(
                    "family"
                )
            ),
            str(
                x.get(
                    "source_id"
                )
            ),
            str(
                x.get(
                    "restricted_knowledge_id"
                )
            ),
        )
    )

    transferred_count = sum(
        1
        for item in execution_records
        if item[
            "execution_state"
        ] == "TRANSFERRED"
    )

    conditional_transfer_count = sum(
        1
        for item in execution_records
        if item[
            "execution_state"
        ] == "CONDITIONAL_TRANSFER"
    )

    not_transferred_count = sum(
        1
        for item in execution_records
        if item[
            "execution_state"
        ] == "NOT_TRANSFERRED"
    )

    # -------------------------------------------------------------
    # Deterministic execution package
    # -------------------------------------------------------------

    package_material = {
        "source_adaptation_package_id":
            adaptation[
                "adaptation_package_id"
            ],

        "source_adaptation_package_digest":
            adaptation[
                "adaptation_package_digest"
            ],

        "transfer_scope_id":
            adaptation[
                "transfer_scope_id"
            ],

        "target_workspace_id":
            adaptation[
                "target_workspace_id"
            ],

        "target_context_id":
            adaptation[
                "target_context_id"
            ],

        "execution_records":
            execution_records,

        "restricted_execution_records":
            restricted_execution_records,
    }

    package_digest = hashlib.sha256(
        json.dumps(
            package_material,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        ).encode("utf-8")
    ).hexdigest()

    execution_package = {
        "execution_schema":
            "transfer_learning_execution_v1",

        "execution_version":
            "v1",

        "execution_package_id":
            "transexecpkg:v1:"
            + package_digest,

        "execution_package_digest":
            package_digest,

        "source_adaptation_package_id":
            adaptation[
                "adaptation_package_id"
            ],

        "source_adaptation_package_digest":
            adaptation[
                "adaptation_package_digest"
            ],

        "transfer_scope_id":
            adaptation[
                "transfer_scope_id"
            ],

        "target_workspace_id":
            adaptation[
                "target_workspace_id"
            ],

        "target_context_id":
            adaptation[
                "target_context_id"
            ],

        "target_domain":
            adaptation[
                "target_domain"
            ],

        "target_topic":
            adaptation[
                "target_topic"
            ],

        "transfer_context_mode":
            adaptation[
                "transfer_context_mode"
            ],

        "execution_record_count":
            len(
                execution_records
            ),

        "transferred_count":
            transferred_count,

        "conditional_transfer_count":
            conditional_transfer_count,

        "not_transferred_count":
            not_transferred_count,

        "restricted_execution_count":
            len(
                restricted_execution_records
            ),

        "execution_records":
            execution_records,

        "restricted_execution_records":
            restricted_execution_records,

        "source_adaptation_preserved":
            True,

        "source_extraction_preserved":
            True,

        "source_scope_preserved":
            True,

        "source_ontology_preserved":
            True,

        "source_provenance_preserved":
            True,

        "ambiguity_preserved":
            True,

        "conflicts_preserved":
            True,

        "uncertainty_preserved":
            True,

        "restricted_knowledge_not_transferred":
            True,

        "unsupported_knowledge_invented":
            False,

        "silent_resolution_performed":
            False,

        "transfer_learning_performed":
            True,

        "provisional_execution_only":
            True,

        "negative_transfer_guard_performed":
            False,

        "negative_transfer_guard_pending":
            True,

        "final_transfer_approved":
            False,

        "semantic_memory_written":
            False,

        "linking_decisions_performed":
            False,
    }

    return {
        "schema_version":
            "transfer_learning_execution_result_v1",

        "version":
            TRANSFER_LEARNING_VERSION,

        "phase":
            TRANSFER_LEARNING_PHASE,

        "patch":
            "4.6.23G",

        "status":
            "TRANSFER_LEARNING_EXECUTED_PROVISIONALLY",

        "workspace_id":
            adaptation_result.get(
                "workspace_id"
            ),

        "transfer_learning_execution":
            execution_package,

        "source_adaptation_result":
            deepcopy(
                dict(adaptation_result)
            ),

        "processing_boundaries": {
            "certified_ontology_alignment_input_inspected":
                True,

            "certified_ontology_alignment_input_preserved":
                True,

            "ontology_alignment_integrity_preserved":
                True,

            "ontology_alignment_provenance_preserved":
                True,

            "alignment_outcomes_preserved":
                True,

            "ambiguity_preserved":
                True,

            "conflicts_preserved":
                True,

            "uncertainty_preserved":
                True,

            "transfer_learning_architecture_defined":
                True,

            "transfer_learning_intake_validated":
                True,

            "transfer_scope_defined":
                True,

            "transfer_eligibility_evaluated":
                True,

            "transferable_knowledge_extracted":
                True,

            "knowledge_adaptation_performed":
                True,

            "transfer_learning_performed":
                True,

            "transfer_execution_provisional":
                True,

            "transfer_integrity_verification_performed":
                False,

            "negative_transfer_guard_performed":
                False,

            "transfer_provenance_built":
                False,

            "final_transfer_learning_result_built":
                False,

            "full_transfer_learning_certification_performed":
                False,

            "source_ontology_alignment_modified":
                False,

            "source_reasoning_modified":
                False,

            "unsupported_knowledge_invented":
                False,

            "silent_resolution_performed":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,
        },

        "transfer_policy":
            "PROVISIONAL_TRANSFER_EXECUTION_PENDING_INTEGRITY_GUARD",

        "next_stage":
            "transfer_integrity_and_negative_transfer_guard",
    }


# =====================================================================
# PATCH 4.6.23H ? Transfer Integrity & Negative-Transfer Guard
# =====================================================================

def guard_transfer_integrity_and_negative_transfer_v1(
    execution_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Verify provisional transfer integrity and apply the
    negative-transfer guard.

    H may approve, conditionally approve, or block provisional
    transfers.

    H does NOT:
    - invent source knowledge,
    - silently resolve ambiguity/conflict,
    - alter upstream ontology/reasoning,
    - write Semantic Memory,
    - make linking decisions.
    """

    from collections.abc import Mapping

    if not isinstance(execution_result, Mapping):
        raise TransferLearningError(
            "execution_result must be a mapping."
        )

    # -------------------------------------------------------------
    # Exact 4.6.23G lifecycle
    # -------------------------------------------------------------

    for field, expected in (
        (
            "schema_version",
            "transfer_learning_execution_result_v1",
        ),
        (
            "version",
            TRANSFER_LEARNING_VERSION,
        ),
        (
            "phase",
            TRANSFER_LEARNING_PHASE,
        ),
        (
            "patch",
            "4.6.23G",
        ),
        (
            "status",
            "TRANSFER_LEARNING_EXECUTED_PROVISIONALLY",
        ),
        (
            "transfer_policy",
            "PROVISIONAL_TRANSFER_EXECUTION_PENDING_INTEGRITY_GUARD",
        ),
        (
            "next_stage",
            "transfer_integrity_and_negative_transfer_guard",
        ),
    ):
        if execution_result.get(field) != expected:
            raise TransferLearningError(
                f"Invalid 4.6.23G lifecycle field: {field}"
            )

    execution = execution_result.get(
        "transfer_learning_execution"
    )

    boundaries = execution_result.get(
        "processing_boundaries"
    )

    if not isinstance(execution, Mapping):
        raise TransferLearningError(
            "transfer_learning_execution is missing."
        )

    if not isinstance(boundaries, Mapping):
        raise TransferLearningError(
            "processing_boundaries are missing."
        )

    # -------------------------------------------------------------
    # G boundary authority
    # -------------------------------------------------------------

    for field in (
        "certified_ontology_alignment_input_inspected",
        "certified_ontology_alignment_input_preserved",
        "ontology_alignment_integrity_preserved",
        "ontology_alignment_provenance_preserved",
        "alignment_outcomes_preserved",
        "ambiguity_preserved",
        "conflicts_preserved",
        "uncertainty_preserved",
        "transfer_learning_architecture_defined",
        "transfer_learning_intake_validated",
        "transfer_scope_defined",
        "transfer_eligibility_evaluated",
        "transferable_knowledge_extracted",
        "knowledge_adaptation_performed",
        "transfer_learning_performed",
        "transfer_execution_provisional",
    ):
        if boundaries.get(field) is not True:
            raise TransferLearningError(
                f"Required 4.6.23G boundary is not True: {field}"
            )

    for field in (
        "transfer_integrity_verification_performed",
        "negative_transfer_guard_performed",
        "transfer_provenance_built",
        "final_transfer_learning_result_built",
        "full_transfer_learning_certification_performed",
        "source_ontology_alignment_modified",
        "source_reasoning_modified",
        "unsupported_knowledge_invented",
        "silent_resolution_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):
        if boundaries.get(field) is not False:
            raise TransferLearningError(
                f"Forbidden 4.6.23G boundary is not False: {field}"
            )

    # -------------------------------------------------------------
    # Execution package authority
    # -------------------------------------------------------------

    for field, expected in (
        (
            "execution_schema",
            "transfer_learning_execution_v1",
        ),
        (
            "execution_version",
            "v1",
        ),
    ):
        if execution.get(field) != expected:
            raise TransferLearningError(
                f"Execution package drifted: {field}"
            )

    for field in (
        "source_adaptation_preserved",
        "source_extraction_preserved",
        "source_scope_preserved",
        "source_ontology_preserved",
        "source_provenance_preserved",
        "ambiguity_preserved",
        "conflicts_preserved",
        "uncertainty_preserved",
        "restricted_knowledge_not_transferred",
        "transfer_learning_performed",
        "provisional_execution_only",
        "negative_transfer_guard_pending",
    ):
        if execution.get(field) is not True:
            raise TransferLearningError(
                f"Required execution field is not True: {field}"
            )

    for field in (
        "unsupported_knowledge_invented",
        "silent_resolution_performed",
        "negative_transfer_guard_performed",
        "final_transfer_approved",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):
        if execution.get(field) is not False:
            raise TransferLearningError(
                f"Forbidden execution field is not False: {field}"
            )

    records = execution.get("execution_records")
    restricted_records = execution.get(
        "restricted_execution_records"
    )

    if not isinstance(records, list):
        raise TransferLearningError(
            "execution_records must be a list."
        )

    if not isinstance(restricted_records, list):
        raise TransferLearningError(
            "restricted_execution_records must be a list."
        )

    if execution.get(
        "execution_record_count"
    ) != len(records):
        raise TransferLearningError(
            "Execution record count drifted."
        )

    if execution.get(
        "restricted_execution_count"
    ) != len(restricted_records):
        raise TransferLearningError(
            "Restricted execution count drifted."
        )

    # -------------------------------------------------------------
    # Verify record-level cryptographic identity
    # -------------------------------------------------------------

    guarded_records = []

    for record in records:

        if not isinstance(record, Mapping):
            raise TransferLearningError(
                "Invalid transfer execution record."
            )

        execution_id = record.get(
            "transfer_execution_id"
        )

        execution_digest = record.get(
            "transfer_execution_digest"
        )

        if not isinstance(
            execution_id,
            str,
        ) or not execution_id.startswith(
            "transexec:v1:"
        ):
            raise TransferLearningError(
                "Invalid transfer execution ID."
            )

        if not isinstance(
            execution_digest,
            str,
        ) or len(execution_digest) != 64:
            raise TransferLearningError(
                "Invalid transfer execution digest."
            )

        digest_material = copy.deepcopy(
            dict(record)
        )

        digest_material.pop(
            "transfer_execution_id",
            None,
        )

        digest_material.pop(
            "transfer_execution_digest",
            None,
        )

        recomputed_digest = hashlib.sha256(
            json.dumps(
                digest_material,
                sort_keys=True,
                separators=(",", ":"),
                default=str,
            ).encode("utf-8")
        ).hexdigest()

        if recomputed_digest != execution_digest:
            raise TransferLearningError(
                "Transfer execution record digest mismatch."
            )

        if execution_id != (
            "transexec:v1:"
            + execution_digest
        ):
            raise TransferLearningError(
                "Transfer execution ID/digest binding mismatch."
            )

        if record.get(
            "provisional_execution"
        ) is not True:
            raise TransferLearningError(
                "Execution record must remain provisional before H."
            )

        if record.get(
            "negative_transfer_guard_pending"
        ) is not True:
            raise TransferLearningError(
                "Negative-transfer guard was not pending."
            )

        if record.get(
            "final_transfer_approved"
        ) is not False:
            raise TransferLearningError(
                "Transfer was prematurely approved."
            )

        if record.get(
            "semantic_memory_written"
        ) is not False:
            raise TransferLearningError(
                "Semantic Memory write occurred prematurely."
            )

        if record.get(
            "linking_decisions_performed"
        ) is not False:
            raise TransferLearningError(
                "Linking occurred prematurely."
            )

        score = record.get(
            "compatibility_score"
        )

        state = record.get(
            "execution_state"
        )

        if not isinstance(
            score,
            (int, float),
        ):
            raise TransferLearningError(
                "Compatibility score is invalid."
            )

        score = float(score)

        if not 0.0 <= score <= 1.0:
            raise TransferLearningError(
                "Compatibility score is outside 0..1."
            )

        # ---------------------------------------------------------
        # Negative-transfer risk policy
        # ---------------------------------------------------------

        if (
            state == "TRANSFERRED"
            and score >= 0.90
        ):
            risk_level = "LOW"
            guard_decision = "APPROVED"
            guard_reason = (
                "HIGH_COMPATIBILITY_AND_INTEGRITY_VERIFIED"
            )
            final_approved = True

        elif (
            state == "CONDITIONAL_TRANSFER"
            and score >= 0.75
        ):
            risk_level = "MODERATE"
            guard_decision = "CONDITIONALLY_APPROVED"
            guard_reason = (
                "MODERATE_NEGATIVE_TRANSFER_RISK"
            )
            final_approved = False

        elif (
            state == "NOT_TRANSFERRED"
            and score >= 0.60
        ):
            risk_level = "HIGH"
            guard_decision = "BLOCKED"
            guard_reason = (
                "LOW_COMPATIBILITY_NEGATIVE_TRANSFER_RISK"
            )
            final_approved = False

        else:
            risk_level = "CRITICAL"
            guard_decision = "BLOCKED"
            guard_reason = (
                "UNACCEPTABLE_NEGATIVE_TRANSFER_RISK"
            )
            final_approved = False

        guarded = copy.deepcopy(
            dict(record)
        )

        guarded[
            "execution_integrity_verified"
        ] = True

        guarded[
            "negative_transfer_risk_level"
        ] = risk_level

        guarded[
            "negative_transfer_guard_decision"
        ] = guard_decision

        guarded[
            "negative_transfer_guard_reason"
        ] = guard_reason

        guarded[
            "negative_transfer_guard_pending"
        ] = False

        guarded[
            "negative_transfer_guard_performed"
        ] = True

        guarded[
            "final_transfer_approved"
        ] = final_approved

        guarded[
            "semantic_memory_written"
        ] = False

        guarded[
            "linking_decisions_performed"
        ] = False

        guarded_records.append(
            guarded
        )

    # -------------------------------------------------------------
    # Restricted records remain hard blocked
    # -------------------------------------------------------------

    guarded_restricted = []

    for record in restricted_records:

        if not isinstance(record, Mapping):
            raise TransferLearningError(
                "Invalid restricted execution record."
            )

        if record.get(
            "execution_state"
        ) != "NOT_TRANSFERRED":
            raise TransferLearningError(
                "Restricted knowledge must remain NOT_TRANSFERRED."
            )

        if record.get(
            "final_transfer_approved"
        ) is not False:
            raise TransferLearningError(
                "Restricted knowledge cannot be approved."
            )

        guarded = copy.deepcopy(
            dict(record)
        )

        guarded[
            "execution_integrity_verified"
        ] = True

        guarded[
            "negative_transfer_risk_level"
        ] = "CRITICAL"

        guarded[
            "negative_transfer_guard_decision"
        ] = "BLOCKED"

        guarded[
            "negative_transfer_guard_reason"
        ] = "RESTRICTED_SOURCE_KNOWLEDGE"

        guarded[
            "negative_transfer_guard_performed"
        ] = True

        guarded[
            "final_transfer_approved"
        ] = False

        guarded[
            "semantic_memory_written"
        ] = False

        guarded[
            "linking_decisions_performed"
        ] = False

        guarded_restricted.append(
            guarded
        )

    guarded_records.sort(
        key=lambda x: (
            str(x.get("family")),
            str(x.get("source_id")),
            str(x.get("transfer_execution_id")),
        )
    )

    guarded_restricted.sort(
        key=lambda x: (
            str(x.get("family")),
            str(x.get("source_id")),
            str(x.get("restricted_knowledge_id")),
        )
    )

    approved_count = sum(
        1
        for item in guarded_records
        if item[
            "negative_transfer_guard_decision"
        ] == "APPROVED"
    )

    conditional_count = sum(
        1
        for item in guarded_records
        if item[
            "negative_transfer_guard_decision"
        ] == "CONDITIONALLY_APPROVED"
    )

    blocked_count = sum(
        1
        for item in guarded_records
        if item[
            "negative_transfer_guard_decision"
        ] == "BLOCKED"
    )

    risk_counts = {
        "LOW": 0,
        "MODERATE": 0,
        "HIGH": 0,
        "CRITICAL": 0,
    }

    for item in guarded_records:
        risk_counts[
            item[
                "negative_transfer_risk_level"
            ]
        ] += 1

    for item in guarded_restricted:
        risk_counts[
            item[
                "negative_transfer_risk_level"
            ]
        ] += 1

    # -------------------------------------------------------------
    # Deterministic guard package
    # -------------------------------------------------------------

    package_material = {
        "source_execution_package_id":
            execution[
                "execution_package_id"
            ],

        "source_execution_package_digest":
            execution[
                "execution_package_digest"
            ],

        "transfer_scope_id":
            execution[
                "transfer_scope_id"
            ],

        "target_workspace_id":
            execution[
                "target_workspace_id"
            ],

        "target_context_id":
            execution[
                "target_context_id"
            ],

        "guarded_execution_records":
            guarded_records,

        "guarded_restricted_records":
            guarded_restricted,

        "risk_counts":
            risk_counts,
    }

    package_digest = hashlib.sha256(
        json.dumps(
            package_material,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        ).encode("utf-8")
    ).hexdigest()

    guard_package = {
        "guard_schema":
            "transfer_integrity_negative_transfer_guard_v1",

        "guard_version":
            "v1",

        "guard_id":
            "transguard:v1:"
            + package_digest,

        "guard_digest":
            package_digest,

        "source_execution_package_id":
            execution[
                "execution_package_id"
            ],

        "source_execution_package_digest":
            execution[
                "execution_package_digest"
            ],

        "transfer_scope_id":
            execution[
                "transfer_scope_id"
            ],

        "target_workspace_id":
            execution[
                "target_workspace_id"
            ],

        "target_context_id":
            execution[
                "target_context_id"
            ],

        "guarded_execution_record_count":
            len(guarded_records),

        "guarded_restricted_record_count":
            len(guarded_restricted),

        "approved_count":
            approved_count,

        "conditionally_approved_count":
            conditional_count,

        "blocked_count":
            blocked_count,

        "risk_counts":
            risk_counts,

        "guarded_execution_records":
            guarded_records,

        "guarded_restricted_records":
            guarded_restricted,

        "execution_integrity_verified":
            True,

        "negative_transfer_guard_performed":
            True,

        "restricted_knowledge_blocked":
            True,

        "source_execution_preserved":
            True,

        "source_adaptation_preserved":
            True,

        "source_extraction_preserved":
            True,

        "source_scope_preserved":
            True,

        "source_ontology_preserved":
            True,

        "source_provenance_preserved":
            True,

        "ambiguity_preserved":
            True,

        "conflicts_preserved":
            True,

        "uncertainty_preserved":
            True,

        "unsupported_knowledge_invented":
            False,

        "silent_resolution_performed":
            False,

        "semantic_memory_written":
            False,

        "linking_decisions_performed":
            False,
    }

    return {
        "schema_version":
            "transfer_integrity_negative_transfer_guard_result_v1",

        "version":
            TRANSFER_LEARNING_VERSION,

        "phase":
            TRANSFER_LEARNING_PHASE,

        "patch":
            "4.6.23H",

        "status":
            "TRANSFER_INTEGRITY_AND_NEGATIVE_TRANSFER_VERIFIED",

        "workspace_id":
            execution_result.get(
                "workspace_id"
            ),

        "transfer_integrity_guard":
            guard_package,

        "source_execution_result":
            deepcopy(
                dict(execution_result)
            ),

        "processing_boundaries": {
            "certified_ontology_alignment_input_inspected":
                True,

            "certified_ontology_alignment_input_preserved":
                True,

            "ontology_alignment_integrity_preserved":
                True,

            "ontology_alignment_provenance_preserved":
                True,

            "alignment_outcomes_preserved":
                True,

            "ambiguity_preserved":
                True,

            "conflicts_preserved":
                True,

            "uncertainty_preserved":
                True,

            "transfer_learning_architecture_defined":
                True,

            "transfer_learning_intake_validated":
                True,

            "transfer_scope_defined":
                True,

            "transfer_eligibility_evaluated":
                True,

            "transferable_knowledge_extracted":
                True,

            "knowledge_adaptation_performed":
                True,

            "transfer_learning_performed":
                True,

            "transfer_execution_provisional":
                True,

            "transfer_integrity_verification_performed":
                True,

            "negative_transfer_guard_performed":
                True,

            "transfer_provenance_built":
                False,

            "final_transfer_learning_result_built":
                False,

            "full_transfer_learning_certification_performed":
                False,

            "source_ontology_alignment_modified":
                False,

            "source_reasoning_modified":
                False,

            "unsupported_knowledge_invented":
                False,

            "silent_resolution_performed":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,
        },

        "transfer_policy":
            "TRANSFER_INTEGRITY_AND_NEGATIVE_TRANSFER_GUARD_VERIFIED",

        "next_stage":
            "transfer_provenance_and_evidence_trace",
    }


# =====================================================================
# PATCH 4.6.23I ? Transfer Provenance & Evidence Trace
# =====================================================================

def build_transfer_provenance_and_evidence_trace_v1(
    guard_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Build the complete provenance and evidence trace for Transfer Learning.

    I records how each transfer outcome was derived across:
    source knowledge -> adaptation -> execution -> negative-transfer guard.

    I does NOT:
    - alter a guard decision,
    - invent evidence,
    - resolve ambiguity/conflict,
    - write Semantic Memory,
    - make linking decisions.
    """

    from collections.abc import Mapping

    if not isinstance(
        guard_result,
        Mapping,
    ):
        raise TransferLearningError(
            "guard_result must be a mapping."
        )

    # -------------------------------------------------------------
    # Exact 4.6.23H lifecycle
    # -------------------------------------------------------------

    for field, expected in (
        (
            "schema_version",
            "transfer_integrity_negative_transfer_guard_result_v1",
        ),
        (
            "version",
            TRANSFER_LEARNING_VERSION,
        ),
        (
            "phase",
            TRANSFER_LEARNING_PHASE,
        ),
        (
            "patch",
            "4.6.23H",
        ),
        (
            "status",
            "TRANSFER_INTEGRITY_AND_NEGATIVE_TRANSFER_VERIFIED",
        ),
        (
            "transfer_policy",
            "TRANSFER_INTEGRITY_AND_NEGATIVE_TRANSFER_GUARD_VERIFIED",
        ),
        (
            "next_stage",
            "transfer_provenance_and_evidence_trace",
        ),
    ):

        if guard_result.get(field) != expected:
            raise TransferLearningError(
                f"Invalid 4.6.23H lifecycle field: {field}"
            )

    guard = guard_result.get(
        "transfer_integrity_guard"
    )

    source_execution_result = guard_result.get(
        "source_execution_result"
    )

    boundaries = guard_result.get(
        "processing_boundaries"
    )

    for name, value in (
        (
            "transfer_integrity_guard",
            guard,
        ),
        (
            "source_execution_result",
            source_execution_result,
        ),
        (
            "processing_boundaries",
            boundaries,
        ),
    ):
        if not isinstance(value, Mapping):
            raise TransferLearningError(
                name + " is missing."
            )

    # -------------------------------------------------------------
    # H boundary authority
    # -------------------------------------------------------------

    for field in (
        "certified_ontology_alignment_input_inspected",
        "certified_ontology_alignment_input_preserved",
        "ontology_alignment_integrity_preserved",
        "ontology_alignment_provenance_preserved",
        "alignment_outcomes_preserved",
        "ambiguity_preserved",
        "conflicts_preserved",
        "uncertainty_preserved",
        "transfer_learning_architecture_defined",
        "transfer_learning_intake_validated",
        "transfer_scope_defined",
        "transfer_eligibility_evaluated",
        "transferable_knowledge_extracted",
        "knowledge_adaptation_performed",
        "transfer_learning_performed",
        "transfer_execution_provisional",
        "transfer_integrity_verification_performed",
        "negative_transfer_guard_performed",
    ):

        if boundaries.get(field) is not True:
            raise TransferLearningError(
                f"Required 4.6.23H boundary is not True: {field}"
            )

    for field in (
        "transfer_provenance_built",
        "final_transfer_learning_result_built",
        "full_transfer_learning_certification_performed",
        "source_ontology_alignment_modified",
        "source_reasoning_modified",
        "unsupported_knowledge_invented",
        "silent_resolution_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if boundaries.get(field) is not False:
            raise TransferLearningError(
                f"Forbidden 4.6.23H boundary is not False: {field}"
            )

    # -------------------------------------------------------------
    # Guard package authority
    # -------------------------------------------------------------

    for field, expected in (
        (
            "guard_schema",
            "transfer_integrity_negative_transfer_guard_v1",
        ),
        (
            "guard_version",
            "v1",
        ),
    ):

        if guard.get(field) != expected:
            raise TransferLearningError(
                f"Guard package drifted: {field}"
            )

    for field in (
        "execution_integrity_verified",
        "negative_transfer_guard_performed",
        "restricted_knowledge_blocked",
        "source_execution_preserved",
        "source_adaptation_preserved",
        "source_extraction_preserved",
        "source_scope_preserved",
        "source_ontology_preserved",
        "source_provenance_preserved",
        "ambiguity_preserved",
        "conflicts_preserved",
        "uncertainty_preserved",
    ):

        if guard.get(field) is not True:
            raise TransferLearningError(
                f"Required guard field is not True: {field}"
            )

    for field in (
        "unsupported_knowledge_invented",
        "silent_resolution_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if guard.get(field) is not False:
            raise TransferLearningError(
                f"Forbidden guard field is not False: {field}"
            )

    guarded_records = guard.get(
        "guarded_execution_records"
    )

    guarded_restricted = guard.get(
        "guarded_restricted_records"
    )

    if not isinstance(
        guarded_records,
        list,
    ):
        raise TransferLearningError(
            "guarded_execution_records must be a list."
        )

    if not isinstance(
        guarded_restricted,
        list,
    ):
        raise TransferLearningError(
            "guarded_restricted_records must be a list."
        )

    if guard.get(
        "guarded_execution_record_count"
    ) != len(guarded_records):
        raise TransferLearningError(
            "Guarded execution record count drifted."
        )

    if guard.get(
        "guarded_restricted_record_count"
    ) != len(guarded_restricted):
        raise TransferLearningError(
            "Guarded restricted record count drifted."
        )

    # -------------------------------------------------------------
    # Recover upstream adaptation and extraction evidence
    # -------------------------------------------------------------

    execution_package = source_execution_result.get(
        "transfer_learning_execution"
    )

    source_adaptation_result = source_execution_result.get(
        "source_adaptation_result"
    )

    if not isinstance(
        execution_package,
        Mapping,
    ):
        raise TransferLearningError(
            "Source execution package is missing."
        )

    if not isinstance(
        source_adaptation_result,
        Mapping,
    ):
        raise TransferLearningError(
            "Source adaptation result is missing."
        )

    adaptation_package = source_adaptation_result.get(
        "knowledge_adaptation"
    )

    source_extraction_result = source_adaptation_result.get(
        "source_extraction_result"
    )

    if not isinstance(
        adaptation_package,
        Mapping,
    ):
        raise TransferLearningError(
            "Source adaptation package is missing."
        )

    if not isinstance(
        source_extraction_result,
        Mapping,
    ):
        raise TransferLearningError(
            "Source extraction result is missing."
        )

    extraction_package = source_extraction_result.get(
        "transferable_knowledge_extraction"
    )

    if not isinstance(
        extraction_package,
        Mapping,
    ):
        raise TransferLearningError(
            "Source extraction package is missing."
        )

    transferable_knowledge = extraction_package.get(
        "transferable_knowledge"
    )

    restricted_knowledge = extraction_package.get(
        "restricted_knowledge"
    )

    adapted_candidates = adaptation_package.get(
        "adapted_candidates"
    )

    execution_records = execution_package.get(
        "execution_records"
    )

    restricted_execution_records = execution_package.get(
        "restricted_execution_records"
    )

    for name, value in (
        (
            "transferable_knowledge",
            transferable_knowledge,
        ),
        (
            "restricted_knowledge",
            restricted_knowledge,
        ),
        (
            "adapted_candidates",
            adapted_candidates,
        ),
        (
            "execution_records",
            execution_records,
        ),
        (
            "restricted_execution_records",
            restricted_execution_records,
        ),
    ):

        if not isinstance(
            value,
            list,
        ):
            raise TransferLearningError(
                name + " must be a list."
            )

    # -------------------------------------------------------------
    # Index upstream evidence
    # -------------------------------------------------------------

    transferable_by_id = {
        item.get(
            "transferable_knowledge_id"
        ): item
        for item in transferable_knowledge
        if isinstance(item, Mapping)
    }

    adapted_by_id = {
        item.get(
            "adapted_knowledge_id"
        ): item
        for item in adapted_candidates
        if isinstance(item, Mapping)
    }

    execution_by_id = {
        item.get(
            "transfer_execution_id"
        ): item
        for item in execution_records
        if isinstance(item, Mapping)
    }

    restricted_by_id = {
        item.get(
            "restricted_knowledge_id"
        ): item
        for item in restricted_knowledge
        if isinstance(item, Mapping)
    }

    restricted_execution_by_id = {
        item.get(
            "restricted_knowledge_id"
        ): item
        for item in restricted_execution_records
        if isinstance(item, Mapping)
    }

    # -------------------------------------------------------------
    # Build successful/conditional/blocked provenance traces
    # -------------------------------------------------------------

    traces = []

    for guarded in guarded_records:

        if not isinstance(
            guarded,
            Mapping,
        ):
            raise TransferLearningError(
                "Invalid guarded execution record."
            )

        execution_id = guarded.get(
            "transfer_execution_id"
        )

        if execution_id not in execution_by_id:
            raise TransferLearningError(
                "Guarded record cannot bind to source execution."
            )

        execution_record = execution_by_id[
            execution_id
        ]

        adapted_id = execution_record.get(
            "source_adapted_knowledge_id"
        )

        if adapted_id not in adapted_by_id:
            raise TransferLearningError(
                "Execution record cannot bind to adapted knowledge."
            )

        adapted = adapted_by_id[
            adapted_id
        ]

        source_transferable_id = adapted.get(
            "source_transferable_knowledge_id"
        )

        if source_transferable_id not in transferable_by_id:
            raise TransferLearningError(
                "Adapted knowledge cannot bind to transferable source."
            )

        transferable = transferable_by_id[
            source_transferable_id
        ]

        if guarded.get(
            "execution_integrity_verified"
        ) is not True:
            raise TransferLearningError(
                "Guarded execution integrity is not verified."
            )

        decision = guarded.get(
            "negative_transfer_guard_decision"
        )

        if decision not in {
            "APPROVED",
            "CONDITIONALLY_APPROVED",
            "BLOCKED",
        }:
            raise TransferLearningError(
                "Invalid negative-transfer guard decision."
            )

        trace_material = {
            "source_transferable_knowledge_id":
                source_transferable_id,

            "source_transferable_knowledge_digest":
                transferable.get(
                    "transferable_knowledge_digest"
                ),

            "source_mapping_trace_id":
                transferable.get(
                    "source_mapping_trace_id"
                ),

            "adapted_knowledge_id":
                adapted_id,

            "adapted_knowledge_digest":
                adapted.get(
                    "adapted_knowledge_digest"
                ),

            "transfer_execution_id":
                execution_id,

            "transfer_execution_digest":
                execution_record.get(
                    "transfer_execution_digest"
                ),

            "family":
                guarded.get(
                    "family"
                ),

            "source_kind":
                guarded.get(
                    "source_kind"
                ),

            "source_id":
                guarded.get(
                    "source_id"
                ),

            "target_workspace_id":
                guarded.get(
                    "target_workspace_id"
                ),

            "target_context_id":
                guarded.get(
                    "target_context_id"
                ),

            "target_domain":
                guarded.get(
                    "target_domain"
                ),

            "target_topic":
                guarded.get(
                    "target_topic"
                ),

            "transfer_context_mode":
                guarded.get(
                    "transfer_context_mode"
                ),

            "compatibility_score":
                guarded.get(
                    "compatibility_score"
                ),

            "adaptation_state":
                guarded.get(
                    "adaptation_state"
                ),

            "execution_state":
                guarded.get(
                    "execution_state"
                ),

            "execution_reason":
                guarded.get(
                    "execution_reason"
                ),

            "execution_integrity_verified":
                True,

            "negative_transfer_risk_level":
                guarded.get(
                    "negative_transfer_risk_level"
                ),

            "negative_transfer_guard_decision":
                decision,

            "negative_transfer_guard_reason":
                guarded.get(
                    "negative_transfer_guard_reason"
                ),

            "final_transfer_approved":
                guarded.get(
                    "final_transfer_approved"
                ),

            "source_evidence_state":
                transferable.get(
                    "evidence_state"
                ),

            "source_preserved":
                True,

            "provenance_complete":
                True,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,
        }

        trace_digest = hashlib.sha256(
            json.dumps(
                trace_material,
                sort_keys=True,
                separators=(",", ":"),
                default=str,
            ).encode("utf-8")
        ).hexdigest()

        trace_material[
            "transfer_trace_id"
        ] = (
            "transtrace:v1:"
            + trace_digest
        )

        trace_material[
            "transfer_trace_digest"
        ] = trace_digest

        traces.append(
            trace_material
        )

    # -------------------------------------------------------------
    # Restricted evidence traces
    # -------------------------------------------------------------

    restricted_traces = []

    for guarded in guarded_restricted:

        if not isinstance(
            guarded,
            Mapping,
        ):
            raise TransferLearningError(
                "Invalid guarded restricted record."
            )

        restricted_id = guarded.get(
            "restricted_knowledge_id"
        )

        if restricted_id not in restricted_by_id:
            raise TransferLearningError(
                "Restricted guard cannot bind to source restricted knowledge."
            )

        if restricted_id not in restricted_execution_by_id:
            raise TransferLearningError(
                "Restricted guard cannot bind to source execution record."
            )

        source_item = restricted_by_id[
            restricted_id
        ]

        source_execution = restricted_execution_by_id[
            restricted_id
        ]

        if guarded.get(
            "negative_transfer_guard_decision"
        ) != "BLOCKED":
            raise TransferLearningError(
                "Restricted knowledge must remain blocked."
            )

        trace_material = {
            "restricted_knowledge_id":
                restricted_id,

            "restricted_knowledge_digest":
                source_item.get(
                    "restricted_knowledge_digest"
                ),

            "family":
                guarded.get(
                    "family"
                ),

            "source_kind":
                guarded.get(
                    "source_kind"
                ),

            "source_id":
                guarded.get(
                    "source_id"
                ),

            "restriction_reason":
                guarded.get(
                    "restriction_reason"
                ),

            "execution_state":
                source_execution.get(
                    "execution_state"
                ),

            "execution_reason":
                source_execution.get(
                    "execution_reason"
                ),

            "execution_integrity_verified":
                guarded.get(
                    "execution_integrity_verified"
                ),

            "negative_transfer_risk_level":
                guarded.get(
                    "negative_transfer_risk_level"
                ),

            "negative_transfer_guard_decision":
                guarded.get(
                    "negative_transfer_guard_decision"
                ),

            "negative_transfer_guard_reason":
                guarded.get(
                    "negative_transfer_guard_reason"
                ),

            "final_transfer_approved":
                False,

            "restricted_source_preserved":
                True,

            "provenance_complete":
                True,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,
        }

        trace_digest = hashlib.sha256(
            json.dumps(
                trace_material,
                sort_keys=True,
                separators=(",", ":"),
                default=str,
            ).encode("utf-8")
        ).hexdigest()

        trace_material[
            "transfer_trace_id"
        ] = (
            "transtrace:v1:"
            + trace_digest
        )

        trace_material[
            "transfer_trace_digest"
        ] = trace_digest

        restricted_traces.append(
            trace_material
        )

    traces.sort(
        key=lambda x: (
            str(
                x.get(
                    "family"
                )
            ),
            str(
                x.get(
                    "source_id"
                )
            ),
            x[
                "transfer_trace_id"
            ],
        )
    )

    restricted_traces.sort(
        key=lambda x: (
            str(
                x.get(
                    "family"
                )
            ),
            str(
                x.get(
                    "source_id"
                )
            ),
            x[
                "transfer_trace_id"
            ],
        )
    )

    approved_trace_count = sum(
        1
        for item in traces
        if item[
            "negative_transfer_guard_decision"
        ] == "APPROVED"
    )

    conditional_trace_count = sum(
        1
        for item in traces
        if item[
            "negative_transfer_guard_decision"
        ] == "CONDITIONALLY_APPROVED"
    )

    blocked_trace_count = sum(
        1
        for item in traces
        if item[
            "negative_transfer_guard_decision"
        ] == "BLOCKED"
    )

    # -------------------------------------------------------------
    # Deterministic provenance package
    # -------------------------------------------------------------

    package_material = {
        "guard_id":
            guard[
                "guard_id"
            ],

        "guard_digest":
            guard[
                "guard_digest"
            ],

        "source_execution_package_id":
            guard[
                "source_execution_package_id"
            ],

        "source_execution_package_digest":
            guard[
                "source_execution_package_digest"
            ],

        "transfer_scope_id":
            guard[
                "transfer_scope_id"
            ],

        "target_workspace_id":
            guard[
                "target_workspace_id"
            ],

        "target_context_id":
            guard[
                "target_context_id"
            ],

        "transfer_traces":
            traces,

        "restricted_transfer_traces":
            restricted_traces,
    }

    package_digest = hashlib.sha256(
        json.dumps(
            package_material,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        ).encode("utf-8")
    ).hexdigest()

    provenance_package = {
        "provenance_schema":
            "transfer_provenance_evidence_trace_v1",

        "provenance_version":
            "v1",

        "provenance_id":
            "transprov:v1:"
            + package_digest,

        "provenance_digest":
            package_digest,

        "guard_id":
            guard[
                "guard_id"
            ],

        "guard_digest":
            guard[
                "guard_digest"
            ],

        "source_execution_package_id":
            guard[
                "source_execution_package_id"
            ],

        "source_execution_package_digest":
            guard[
                "source_execution_package_digest"
            ],

        "transfer_scope_id":
            guard[
                "transfer_scope_id"
            ],

        "target_workspace_id":
            guard[
                "target_workspace_id"
            ],

        "target_context_id":
            guard[
                "target_context_id"
            ],

        "transfer_trace_count":
            len(
                traces
            ),

        "restricted_transfer_trace_count":
            len(
                restricted_traces
            ),

        "approved_trace_count":
            approved_trace_count,

        "conditionally_approved_trace_count":
            conditional_trace_count,

        "blocked_trace_count":
            blocked_trace_count,

        "transfer_traces":
            traces,

        "restricted_transfer_traces":
            restricted_traces,

        "complete_source_to_guard_trace":
            True,

        "source_transferable_knowledge_bound":
            True,

        "source_adaptation_bound":
            True,

        "source_execution_bound":
            True,

        "guard_decisions_bound":
            True,

        "restricted_knowledge_trace_complete":
            True,

        "source_ontology_preserved":
            True,

        "source_provenance_preserved":
            True,

        "ambiguity_preserved":
            True,

        "conflicts_preserved":
            True,

        "uncertainty_preserved":
            True,

        "unsupported_knowledge_invented":
            False,

        "silent_resolution_performed":
            False,

        "semantic_memory_written":
            False,

        "linking_decisions_performed":
            False,
    }

    return {
        "schema_version":
            "transfer_provenance_evidence_trace_result_v1",

        "version":
            TRANSFER_LEARNING_VERSION,

        "phase":
            TRANSFER_LEARNING_PHASE,

        "patch":
            "4.6.23I",

        "status":
            "TRANSFER_PROVENANCE_AND_EVIDENCE_TRACE_BUILT",

        "workspace_id":
            guard_result.get(
                "workspace_id"
            ),

        "transfer_provenance":
            provenance_package,

        "source_guard_result":
            deepcopy(
                dict(guard_result)
            ),

        "processing_boundaries": {
            "certified_ontology_alignment_input_inspected":
                True,

            "certified_ontology_alignment_input_preserved":
                True,

            "ontology_alignment_integrity_preserved":
                True,

            "ontology_alignment_provenance_preserved":
                True,

            "alignment_outcomes_preserved":
                True,

            "ambiguity_preserved":
                True,

            "conflicts_preserved":
                True,

            "uncertainty_preserved":
                True,

            "transfer_learning_architecture_defined":
                True,

            "transfer_learning_intake_validated":
                True,

            "transfer_scope_defined":
                True,

            "transfer_eligibility_evaluated":
                True,

            "transferable_knowledge_extracted":
                True,

            "knowledge_adaptation_performed":
                True,

            "transfer_learning_performed":
                True,

            "transfer_execution_provisional":
                True,

            "transfer_integrity_verification_performed":
                True,

            "negative_transfer_guard_performed":
                True,

            "transfer_provenance_built":
                True,

            "final_transfer_learning_result_built":
                False,

            "full_transfer_learning_certification_performed":
                False,

            "source_ontology_alignment_modified":
                False,

            "source_reasoning_modified":
                False,

            "unsupported_knowledge_invented":
                False,

            "silent_resolution_performed":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,
        },

        "transfer_policy":
            "COMPLETE_TRANSFER_PROVENANCE_AND_EVIDENCE_TRACE_BUILT",

        "next_stage":
            "final_transfer_learning_result",
    }


# =====================================================================
# PATCH 4.6.23J ? Final Transfer Learning Result
# =====================================================================

def build_final_transfer_learning_result_v1(
    provenance_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Build the canonical final Transfer Learning result.

    J consolidates the complete A->I pipeline output while preserving
    all guard decisions and provenance.

    J does NOT:
    - recalculate transfer decisions,
    - override negative-transfer guard outcomes,
    - write Semantic Memory,
    - perform linking decisions,
    - certify the full phase. Certification belongs to 4.6.23K.
    """

    from collections.abc import Mapping

    if not isinstance(
        provenance_result,
        Mapping,
    ):
        raise TransferLearningError(
            "provenance_result must be a mapping."
        )

    # -------------------------------------------------------------
    # Exact 4.6.23I lifecycle
    # -------------------------------------------------------------

    for field, expected in (
        (
            "schema_version",
            "transfer_provenance_evidence_trace_result_v1",
        ),
        (
            "version",
            TRANSFER_LEARNING_VERSION,
        ),
        (
            "phase",
            TRANSFER_LEARNING_PHASE,
        ),
        (
            "patch",
            "4.6.23I",
        ),
        (
            "status",
            "TRANSFER_PROVENANCE_AND_EVIDENCE_TRACE_BUILT",
        ),
        (
            "transfer_policy",
            "COMPLETE_TRANSFER_PROVENANCE_AND_EVIDENCE_TRACE_BUILT",
        ),
        (
            "next_stage",
            "final_transfer_learning_result",
        ),
    ):

        if provenance_result.get(field) != expected:
            raise TransferLearningError(
                f"Invalid 4.6.23I lifecycle field: {field}"
            )

    workspace_id = provenance_result.get(
        "workspace_id"
    )

    provenance = provenance_result.get(
        "transfer_provenance"
    )

    source_guard_result = provenance_result.get(
        "source_guard_result"
    )

    boundaries = provenance_result.get(
        "processing_boundaries"
    )

    for name, value in (
        (
            "transfer_provenance",
            provenance,
        ),
        (
            "source_guard_result",
            source_guard_result,
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
            raise TransferLearningError(
                name + " is missing."
            )

    if not isinstance(
        workspace_id,
        str,
    ) or not workspace_id:
        raise TransferLearningError(
            "workspace_id is required."
        )

    # -------------------------------------------------------------
    # I boundary authority
    # -------------------------------------------------------------

    for field in (
        "certified_ontology_alignment_input_inspected",
        "certified_ontology_alignment_input_preserved",
        "ontology_alignment_integrity_preserved",
        "ontology_alignment_provenance_preserved",
        "alignment_outcomes_preserved",
        "ambiguity_preserved",
        "conflicts_preserved",
        "uncertainty_preserved",
        "transfer_learning_architecture_defined",
        "transfer_learning_intake_validated",
        "transfer_scope_defined",
        "transfer_eligibility_evaluated",
        "transferable_knowledge_extracted",
        "knowledge_adaptation_performed",
        "transfer_learning_performed",
        "transfer_execution_provisional",
        "transfer_integrity_verification_performed",
        "negative_transfer_guard_performed",
        "transfer_provenance_built",
    ):

        if boundaries.get(field) is not True:
            raise TransferLearningError(
                f"Required 4.6.23I boundary is not True: {field}"
            )

    for field in (
        "final_transfer_learning_result_built",
        "full_transfer_learning_certification_performed",
        "source_ontology_alignment_modified",
        "source_reasoning_modified",
        "unsupported_knowledge_invented",
        "silent_resolution_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if boundaries.get(field) is not False:
            raise TransferLearningError(
                f"Forbidden 4.6.23I boundary is not False: {field}"
            )

    # -------------------------------------------------------------
    # Provenance authority
    # -------------------------------------------------------------

    for field, expected in (
        (
            "provenance_schema",
            "transfer_provenance_evidence_trace_v1",
        ),
        (
            "provenance_version",
            "v1",
        ),
    ):

        if provenance.get(field) != expected:
            raise TransferLearningError(
                f"Transfer provenance drifted: {field}"
            )

    for field in (
        "complete_source_to_guard_trace",
        "source_transferable_knowledge_bound",
        "source_adaptation_bound",
        "source_execution_bound",
        "guard_decisions_bound",
        "restricted_knowledge_trace_complete",
        "source_ontology_preserved",
        "source_provenance_preserved",
        "ambiguity_preserved",
        "conflicts_preserved",
        "uncertainty_preserved",
    ):

        if provenance.get(field) is not True:
            raise TransferLearningError(
                f"Required provenance field is not True: {field}"
            )

    for field in (
        "unsupported_knowledge_invented",
        "silent_resolution_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if provenance.get(field) is not False:
            raise TransferLearningError(
                f"Forbidden provenance field is not False: {field}"
            )

    traces = provenance.get(
        "transfer_traces"
    )

    restricted_traces = provenance.get(
        "restricted_transfer_traces"
    )

    if not isinstance(
        traces,
        list,
    ):
        raise TransferLearningError(
            "transfer_traces must be a list."
        )

    if not isinstance(
        restricted_traces,
        list,
    ):
        raise TransferLearningError(
            "restricted_transfer_traces must be a list."
        )

    if provenance.get(
        "transfer_trace_count"
    ) != len(traces):
        raise TransferLearningError(
            "Transfer trace count drifted."
        )

    if provenance.get(
        "restricted_transfer_trace_count"
    ) != len(
        restricted_traces
    ):
        raise TransferLearningError(
            "Restricted transfer trace count drifted."
        )

    # -------------------------------------------------------------
    # Verify trace identities and derive canonical outcome sets
    # -------------------------------------------------------------

    approved = []
    conditional = []
    blocked = []

    for trace in traces:

        if not isinstance(
            trace,
            Mapping,
        ):
            raise TransferLearningError(
                "Invalid transfer trace."
            )

        trace_id = trace.get(
            "transfer_trace_id"
        )

        trace_digest = trace.get(
            "transfer_trace_digest"
        )

        if not isinstance(
            trace_id,
            str,
        ) or not trace_id.startswith(
            "transtrace:v1:"
        ):
            raise TransferLearningError(
                "Invalid transfer trace ID."
            )

        if not isinstance(
            trace_digest,
            str,
        ) or len(trace_digest) != 64:
            raise TransferLearningError(
                "Invalid transfer trace digest."
            )

        material = copy.deepcopy(
            dict(trace)
        )

        material.pop(
            "transfer_trace_id",
            None,
        )

        material.pop(
            "transfer_trace_digest",
            None,
        )

        recomputed = hashlib.sha256(
            json.dumps(
                material,
                sort_keys=True,
                separators=(",", ":"),
                default=str,
            ).encode("utf-8")
        ).hexdigest()

        if recomputed != trace_digest:
            raise TransferLearningError(
                "Transfer trace digest mismatch."
            )

        if trace_id != (
            "transtrace:v1:"
            + trace_digest
        ):
            raise TransferLearningError(
                "Transfer trace ID/digest binding mismatch."
            )

        if trace.get(
            "provenance_complete"
        ) is not True:
            raise TransferLearningError(
                "Transfer trace provenance is incomplete."
            )

        decision = trace.get(
            "negative_transfer_guard_decision"
        )

        if decision == "APPROVED":

            if trace.get(
                "final_transfer_approved"
            ) is not True:
                raise TransferLearningError(
                    "Approved trace must be finally approved."
                )

            approved.append(
                copy.deepcopy(
                    dict(trace)
                )
            )

        elif decision == "CONDITIONALLY_APPROVED":

            if trace.get(
                "final_transfer_approved"
            ) is not False:
                raise TransferLearningError(
                    "Conditional trace cannot be finally approved."
                )

            conditional.append(
                copy.deepcopy(
                    dict(trace)
                )
            )

        elif decision == "BLOCKED":

            if trace.get(
                "final_transfer_approved"
            ) is not False:
                raise TransferLearningError(
                    "Blocked trace cannot be approved."
                )

            blocked.append(
                copy.deepcopy(
                    dict(trace)
                )
            )

        else:
            raise TransferLearningError(
                "Invalid final transfer guard decision."
            )

    canonical_restricted = []

    for trace in restricted_traces:

        if not isinstance(
            trace,
            Mapping,
        ):
            raise TransferLearningError(
                "Invalid restricted transfer trace."
            )

        if trace.get(
            "negative_transfer_guard_decision"
        ) != "BLOCKED":
            raise TransferLearningError(
                "Restricted trace must remain blocked."
            )

        if trace.get(
            "final_transfer_approved"
        ) is not False:
            raise TransferLearningError(
                "Restricted trace cannot be approved."
            )

        if trace.get(
            "provenance_complete"
        ) is not True:
            raise TransferLearningError(
                "Restricted trace provenance is incomplete."
            )

        canonical_restricted.append(
            copy.deepcopy(
                dict(trace)
            )
        )

    # -------------------------------------------------------------
    # Count integrity
    # -------------------------------------------------------------

    if provenance.get(
        "approved_trace_count"
    ) != len(approved):
        raise TransferLearningError(
            "Approved transfer count drifted."
        )

    if provenance.get(
        "conditionally_approved_trace_count"
    ) != len(conditional):
        raise TransferLearningError(
            "Conditional transfer count drifted."
        )

    if provenance.get(
        "blocked_trace_count"
    ) != len(blocked):
        raise TransferLearningError(
            "Blocked transfer count drifted."
        )

    # -------------------------------------------------------------
    # Deterministic final result
    # -------------------------------------------------------------

    final_material = {
        "workspace_id":
            workspace_id,

        "provenance_id":
            provenance[
                "provenance_id"
            ],

        "provenance_digest":
            provenance[
                "provenance_digest"
            ],

        "guard_id":
            provenance[
                "guard_id"
            ],

        "guard_digest":
            provenance[
                "guard_digest"
            ],

        "source_execution_package_id":
            provenance[
                "source_execution_package_id"
            ],

        "source_execution_package_digest":
            provenance[
                "source_execution_package_digest"
            ],

        "transfer_scope_id":
            provenance[
                "transfer_scope_id"
            ],

        "target_workspace_id":
            provenance[
                "target_workspace_id"
            ],

        "target_context_id":
            provenance[
                "target_context_id"
            ],

        "approved_transfers":
            approved,

        "conditionally_approved_transfers":
            conditional,

        "blocked_transfers":
            blocked,

        "restricted_transfers":
            canonical_restricted,
    }

    final_digest = hashlib.sha256(
        json.dumps(
            final_material,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        ).encode("utf-8")
    ).hexdigest()

    final_result = {
        "final_result_schema":
            "final_transfer_learning_result_v1",

        "final_result_version":
            "v1",

        "final_result_id":
            "transfinal:v1:"
            + final_digest,

        "final_result_digest":
            final_digest,

        "workspace_id":
            workspace_id,

        "provenance_id":
            provenance[
                "provenance_id"
            ],

        "provenance_digest":
            provenance[
                "provenance_digest"
            ],

        "guard_id":
            provenance[
                "guard_id"
            ],

        "guard_digest":
            provenance[
                "guard_digest"
            ],

        "source_execution_package_id":
            provenance[
                "source_execution_package_id"
            ],

        "source_execution_package_digest":
            provenance[
                "source_execution_package_digest"
            ],

        "transfer_scope_id":
            provenance[
                "transfer_scope_id"
            ],

        "target_workspace_id":
            provenance[
                "target_workspace_id"
            ],

        "target_context_id":
            provenance[
                "target_context_id"
            ],

        "transfer_trace_count":
            len(traces),

        "restricted_transfer_trace_count":
            len(
                canonical_restricted
            ),

        "approved_transfer_count":
            len(
                approved
            ),

        "conditionally_approved_transfer_count":
            len(
                conditional
            ),

        "blocked_transfer_count":
            len(
                blocked
            ),

        "approved_transfers":
            approved,

        "conditionally_approved_transfers":
            conditional,

        "blocked_transfers":
            blocked,

        "restricted_transfers":
            canonical_restricted,

        "transfer_learning_performed":
            True,

        "transfer_integrity_verified":
            True,

        "negative_transfer_guard_performed":
            True,

        "transfer_provenance_complete":
            True,

        "source_ontology_preserved":
            True,

        "source_provenance_preserved":
            True,

        "ambiguity_preserved":
            True,

        "conflicts_preserved":
            True,

        "uncertainty_preserved":
            True,

        "restricted_knowledge_blocked":
            True,

        "unsupported_knowledge_invented":
            False,

        "silent_resolution_performed":
            False,

        "source_ontology_alignment_modified":
            False,

        "source_reasoning_modified":
            False,

        "semantic_memory_written":
            False,

        "linking_decisions_performed":
            False,

        "full_transfer_learning_certified":
            False,

        "certification_status":
            "PENDING_4.6.23K",

        "next_owner":
            "4.6.24_AUTHORITY",

        "dynamic_semantic_graph_owner":
            "4.6.26_DYNAMIC_SEMANTIC_GRAPH",

        "learning_engine_owner":
            "4.6.27_LEARNING_ENGINE",

        "semantic_memory_owner":
            "4.6.28_SEMANTIC_MEMORY",
    }

    return {
        "schema_version":
            "final_transfer_learning_result_envelope_v1",

        "version":
            TRANSFER_LEARNING_VERSION,

        "phase":
            TRANSFER_LEARNING_PHASE,

        "patch":
            "4.6.23J",

        "status":
            "FINAL_TRANSFER_LEARNING_RESULT_BUILT",

        "workspace_id":
            workspace_id,

        "final_transfer_learning_result":
            final_result,

        "source_provenance_result":
            deepcopy(
                dict(provenance_result)
            ),

        "processing_boundaries": {
            "certified_ontology_alignment_input_inspected":
                True,

            "certified_ontology_alignment_input_preserved":
                True,

            "ontology_alignment_integrity_preserved":
                True,

            "ontology_alignment_provenance_preserved":
                True,

            "alignment_outcomes_preserved":
                True,

            "ambiguity_preserved":
                True,

            "conflicts_preserved":
                True,

            "uncertainty_preserved":
                True,

            "transfer_learning_architecture_defined":
                True,

            "transfer_learning_intake_validated":
                True,

            "transfer_scope_defined":
                True,

            "transfer_eligibility_evaluated":
                True,

            "transferable_knowledge_extracted":
                True,

            "knowledge_adaptation_performed":
                True,

            "transfer_learning_performed":
                True,

            "transfer_execution_provisional":
                True,

            "transfer_integrity_verification_performed":
                True,

            "negative_transfer_guard_performed":
                True,

            "transfer_provenance_built":
                True,

            "final_transfer_learning_result_built":
                True,

            "full_transfer_learning_certification_performed":
                False,

            "source_ontology_alignment_modified":
                False,

            "source_reasoning_modified":
                False,

            "unsupported_knowledge_invented":
                False,

            "silent_resolution_performed":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,
        },

        "transfer_policy":
            "FINAL_TRANSFER_LEARNING_RESULT_READY_FOR_CERTIFICATION",

        "next_stage":
            "full_transfer_learning_hard_certification",
    }


# =====================================================================
# PATCH 4.6.23K ? Full Transfer Learning Hard Certification
# =====================================================================

def certify_full_transfer_learning_v1(
    final_envelope: dict[str, Any],
) -> dict[str, Any]:
    """
    Perform full hard certification of Transfer Learning 4.6.23.

    K certifies the complete A->J pipeline and emits the canonical
    certified transfer-learning result.

    K does NOT:
    - write Semantic Memory,
    - perform linking decisions,
    - mutate upstream ontology/reasoning,
    - create new transfer outcomes.
    """

    from collections.abc import Mapping

    if not isinstance(
        final_envelope,
        Mapping,
    ):
        raise TransferLearningError(
            "final_envelope must be a mapping."
        )

    # -------------------------------------------------------------
    # Exact 4.6.23J lifecycle
    # -------------------------------------------------------------

    for field, expected in (
        (
            "schema_version",
            "final_transfer_learning_result_envelope_v1",
        ),
        (
            "version",
            TRANSFER_LEARNING_VERSION,
        ),
        (
            "phase",
            TRANSFER_LEARNING_PHASE,
        ),
        (
            "patch",
            "4.6.23J",
        ),
        (
            "status",
            "FINAL_TRANSFER_LEARNING_RESULT_BUILT",
        ),
        (
            "transfer_policy",
            "FINAL_TRANSFER_LEARNING_RESULT_READY_FOR_CERTIFICATION",
        ),
        (
            "next_stage",
            "full_transfer_learning_hard_certification",
        ),
    ):

        if final_envelope.get(field) != expected:
            raise TransferLearningError(
                f"Invalid 4.6.23J lifecycle field: {field}"
            )

    workspace_id = final_envelope.get(
        "workspace_id"
    )

    final = final_envelope.get(
        "final_transfer_learning_result"
    )

    source_provenance_result = final_envelope.get(
        "source_provenance_result"
    )

    boundaries = final_envelope.get(
        "processing_boundaries"
    )

    for name, value in (
        (
            "final_transfer_learning_result",
            final,
        ),
        (
            "source_provenance_result",
            source_provenance_result,
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
            raise TransferLearningError(
                name + " is missing."
            )

    if not isinstance(
        workspace_id,
        str,
    ) or not workspace_id:
        raise TransferLearningError(
            "workspace_id is required."
        )

    if final.get(
        "workspace_id"
    ) != workspace_id:
        raise TransferLearningError(
            "Workspace binding drifted."
        )

    # -------------------------------------------------------------
    # J boundary authority
    # -------------------------------------------------------------

    for field in (
        "certified_ontology_alignment_input_inspected",
        "certified_ontology_alignment_input_preserved",
        "ontology_alignment_integrity_preserved",
        "ontology_alignment_provenance_preserved",
        "alignment_outcomes_preserved",
        "ambiguity_preserved",
        "conflicts_preserved",
        "uncertainty_preserved",
        "transfer_learning_architecture_defined",
        "transfer_learning_intake_validated",
        "transfer_scope_defined",
        "transfer_eligibility_evaluated",
        "transferable_knowledge_extracted",
        "knowledge_adaptation_performed",
        "transfer_learning_performed",
        "transfer_execution_provisional",
        "transfer_integrity_verification_performed",
        "negative_transfer_guard_performed",
        "transfer_provenance_built",
        "final_transfer_learning_result_built",
    ):

        if boundaries.get(field) is not True:
            raise TransferLearningError(
                f"Required 4.6.23J boundary is not True: {field}"
            )

    for field in (
        "full_transfer_learning_certification_performed",
        "source_ontology_alignment_modified",
        "source_reasoning_modified",
        "unsupported_knowledge_invented",
        "silent_resolution_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if boundaries.get(field) is not False:
            raise TransferLearningError(
                f"Forbidden 4.6.23J boundary is not False: {field}"
            )

    # -------------------------------------------------------------
    # Final result contract
    # -------------------------------------------------------------

    for field, expected in (
        (
            "final_result_schema",
            "final_transfer_learning_result_v1",
        ),
        (
            "final_result_version",
            "v1",
        ),
        (
            "certification_status",
            "PENDING_4.6.23K",
        ),
        (
            "next_owner",
            "4.6.24_AUTHORITY",
        ),
        (
            "dynamic_semantic_graph_owner",
            "4.6.26_DYNAMIC_SEMANTIC_GRAPH",
        ),
        (
            "learning_engine_owner",
            "4.6.27_LEARNING_ENGINE",
        ),
        (
            "semantic_memory_owner",
            "4.6.28_SEMANTIC_MEMORY",
        ),
    ):

        if final.get(field) != expected:
            raise TransferLearningError(
                f"Final result contract drifted: {field}"
            )

    if final.get(
        "full_transfer_learning_certified"
    ) is not False:
        raise TransferLearningError(
            "Transfer Learning was prematurely certified."
        )

    for field in (
        "transfer_learning_performed",
        "transfer_integrity_verified",
        "negative_transfer_guard_performed",
        "transfer_provenance_complete",
        "source_ontology_preserved",
        "source_provenance_preserved",
        "ambiguity_preserved",
        "conflicts_preserved",
        "uncertainty_preserved",
        "restricted_knowledge_blocked",
    ):

        if final.get(field) is not True:
            raise TransferLearningError(
                f"Required final result field is not True: {field}"
            )

    for field in (
        "unsupported_knowledge_invented",
        "silent_resolution_performed",
        "source_ontology_alignment_modified",
        "source_reasoning_modified",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if final.get(field) is not False:
            raise TransferLearningError(
                f"Forbidden final result field is not False: {field}"
            )

    # -------------------------------------------------------------
    # Outcome arrays and counts
    # -------------------------------------------------------------

    approved = final.get(
        "approved_transfers"
    )

    conditional = final.get(
        "conditionally_approved_transfers"
    )

    blocked = final.get(
        "blocked_transfers"
    )

    restricted = final.get(
        "restricted_transfers"
    )

    for name, value in (
        (
            "approved_transfers",
            approved,
        ),
        (
            "conditionally_approved_transfers",
            conditional,
        ),
        (
            "blocked_transfers",
            blocked,
        ),
        (
            "restricted_transfers",
            restricted,
        ),
    ):

        if not isinstance(
            value,
            list,
        ):
            raise TransferLearningError(
                name + " must be a list."
            )

    if final.get(
        "approved_transfer_count"
    ) != len(approved):
        raise TransferLearningError(
            "Approved transfer count drifted."
        )

    if final.get(
        "conditionally_approved_transfer_count"
    ) != len(conditional):
        raise TransferLearningError(
            "Conditional transfer count drifted."
        )

    if final.get(
        "blocked_transfer_count"
    ) != len(blocked):
        raise TransferLearningError(
            "Blocked transfer count drifted."
        )

    if final.get(
        "restricted_transfer_trace_count"
    ) != len(restricted):
        raise TransferLearningError(
            "Restricted transfer count drifted."
        )

    if final.get(
        "transfer_trace_count"
    ) != (
        len(approved)
        + len(conditional)
        + len(blocked)
    ):
        raise TransferLearningError(
            "Total transfer trace count drifted."
        )

    # -------------------------------------------------------------
    # Outcome semantics
    # -------------------------------------------------------------

    for item in approved:

        if not isinstance(
            item,
            Mapping,
        ):
            raise TransferLearningError(
                "Invalid approved transfer."
            )

        if item.get(
            "negative_transfer_guard_decision"
        ) != "APPROVED":
            raise TransferLearningError(
                "Approved transfer guard decision drifted."
            )

        if item.get(
            "final_transfer_approved"
        ) is not True:
            raise TransferLearningError(
                "Approved transfer is not finally approved."
            )

        if item.get(
            "provenance_complete"
        ) is not True:
            raise TransferLearningError(
                "Approved transfer lacks complete provenance."
            )

    for item in conditional:

        if not isinstance(
            item,
            Mapping,
        ):
            raise TransferLearningError(
                "Invalid conditional transfer."
            )

        if item.get(
            "negative_transfer_guard_decision"
        ) != "CONDITIONALLY_APPROVED":
            raise TransferLearningError(
                "Conditional transfer decision drifted."
            )

        if item.get(
            "final_transfer_approved"
        ) is not False:
            raise TransferLearningError(
                "Conditional transfer cannot be finally approved."
            )

    for item in blocked:

        if not isinstance(
            item,
            Mapping,
        ):
            raise TransferLearningError(
                "Invalid blocked transfer."
            )

        if item.get(
            "negative_transfer_guard_decision"
        ) != "BLOCKED":
            raise TransferLearningError(
                "Blocked transfer decision drifted."
            )

        if item.get(
            "final_transfer_approved"
        ) is not False:
            raise TransferLearningError(
                "Blocked transfer cannot be approved."
            )

    for item in restricted:

        if not isinstance(
            item,
            Mapping,
        ):
            raise TransferLearningError(
                "Invalid restricted transfer."
            )

        if item.get(
            "negative_transfer_guard_decision"
        ) != "BLOCKED":
            raise TransferLearningError(
                "Restricted transfer must remain blocked."
            )

        if item.get(
            "final_transfer_approved"
        ) is not False:
            raise TransferLearningError(
                "Restricted transfer cannot be approved."
            )

        if item.get(
            "provenance_complete"
        ) is not True:
            raise TransferLearningError(
                "Restricted transfer provenance is incomplete."
            )

    # -------------------------------------------------------------
    # Verify final result cryptographic identity
    # -------------------------------------------------------------

    final_result_id = final.get(
        "final_result_id"
    )

    final_result_digest = final.get(
        "final_result_digest"
    )

    if not isinstance(
        final_result_id,
        str,
    ) or not final_result_id.startswith(
        "transfinal:v1:"
    ):
        raise TransferLearningError(
            "Invalid final result ID."
        )

    if not isinstance(
        final_result_digest,
        str,
    ) or len(
        final_result_digest
    ) != 64:
        raise TransferLearningError(
            "Invalid final result digest."
        )

    final_material = {
        "workspace_id":
            final[
                "workspace_id"
            ],

        "provenance_id":
            final[
                "provenance_id"
            ],

        "provenance_digest":
            final[
                "provenance_digest"
            ],

        "guard_id":
            final[
                "guard_id"
            ],

        "guard_digest":
            final[
                "guard_digest"
            ],

        "source_execution_package_id":
            final[
                "source_execution_package_id"
            ],

        "source_execution_package_digest":
            final[
                "source_execution_package_digest"
            ],

        "transfer_scope_id":
            final[
                "transfer_scope_id"
            ],

        "target_workspace_id":
            final[
                "target_workspace_id"
            ],

        "target_context_id":
            final[
                "target_context_id"
            ],

        "approved_transfers":
            approved,

        "conditionally_approved_transfers":
            conditional,

        "blocked_transfers":
            blocked,

        "restricted_transfers":
            restricted,
    }

    recomputed_final_digest = hashlib.sha256(
        json.dumps(
            final_material,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        ).encode("utf-8")
    ).hexdigest()

    if recomputed_final_digest != final_result_digest:
        raise TransferLearningError(
            "Final transfer result digest mismatch."
        )

    if final_result_id != (
        "transfinal:v1:"
        + final_result_digest
    ):
        raise TransferLearningError(
            "Final result ID/digest binding mismatch."
        )

    # -------------------------------------------------------------
    # Verify provenance bindings
    # -------------------------------------------------------------

    provenance = source_provenance_result.get(
        "transfer_provenance"
    )

    if not isinstance(
        provenance,
        Mapping,
    ):
        raise TransferLearningError(
            "Source provenance package is missing."
        )

    for final_field, provenance_field in (
        (
            "provenance_id",
            "provenance_id",
        ),
        (
            "provenance_digest",
            "provenance_digest",
        ),
        (
            "guard_id",
            "guard_id",
        ),
        (
            "guard_digest",
            "guard_digest",
        ),
        (
            "source_execution_package_id",
            "source_execution_package_id",
        ),
        (
            "source_execution_package_digest",
            "source_execution_package_digest",
        ),
        (
            "transfer_scope_id",
            "transfer_scope_id",
        ),
        (
            "target_workspace_id",
            "target_workspace_id",
        ),
        (
            "target_context_id",
            "target_context_id",
        ),
    ):

        if final.get(
            final_field
        ) != provenance.get(
            provenance_field
        ):
            raise TransferLearningError(
                f"Final/provenance binding drifted: {final_field}"
            )

    # -------------------------------------------------------------
    # Build certification package
    # -------------------------------------------------------------

    certification_material = {
        "source_final_result_id":
            final_result_id,

        "source_final_result_digest":
            final_result_digest,

        "workspace_id":
            workspace_id,

        "provenance_id":
            final[
                "provenance_id"
            ],

        "guard_id":
            final[
                "guard_id"
            ],

        "transfer_scope_id":
            final[
                "transfer_scope_id"
            ],

        "approved_transfer_count":
            len(
                approved
            ),

        "conditionally_approved_transfer_count":
            len(
                conditional
            ),

        "blocked_transfer_count":
            len(
                blocked
            ),

        "restricted_transfer_count":
            len(
                restricted
            ),
    }

    certification_digest = hashlib.sha256(
        json.dumps(
            certification_material,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        ).encode("utf-8")
    ).hexdigest()

    certification = {
        "certification_schema":
            "full_transfer_learning_certification_v1",

        "certification_version":
            "v1",

        "certification_phase":
            "4.6.23",

        "certification_patch":
            "4.6.23K",

        "certification_id":
            "transcert:v1:"
            + certification_digest,

        "certification_digest":
            certification_digest,

        "certification_status":
            "CERTIFIED",

        "certification_scope":
            "FULL_TRANSFER_LEARNING_PIPELINE",

        "source_final_result_id":
            final_result_id,

        "source_final_result_digest":
            final_result_digest,

        "workspace_id":
            workspace_id,

        "provenance_id":
            final[
                "provenance_id"
            ],

        "provenance_digest":
            final[
                "provenance_digest"
            ],

        "guard_id":
            final[
                "guard_id"
            ],

        "guard_digest":
            final[
                "guard_digest"
            ],

        "transfer_scope_id":
            final[
                "transfer_scope_id"
            ],

        "approved_transfer_count":
            len(
                approved
            ),

        "conditionally_approved_transfer_count":
            len(
                conditional
            ),

        "blocked_transfer_count":
            len(
                blocked
            ),

        "restricted_transfer_count":
            len(
                restricted
            ),

        "final_result_identity_verified":
            True,

        "final_result_digest_verified":
            True,

        "provenance_identity_verified":
            True,

        "guard_identity_verified":
            True,

        "transfer_scope_identity_verified":
            True,

        "outcome_counts_verified":
            True,

        "approved_transfer_integrity_verified":
            True,

        "conditional_transfer_integrity_verified":
            True,

        "blocked_transfer_integrity_verified":
            True,

        "restricted_transfer_integrity_verified":
            True,

        "transfer_integrity_verified":
            True,

        "negative_transfer_guard_verified":
            True,

        "transfer_provenance_verified":
            True,

        "source_ontology_preserved":
            True,

        "source_reasoning_preserved":
            True,

        "ambiguity_preserved":
            True,

        "conflicts_preserved":
            True,

        "uncertainty_preserved":
            True,

        "unsupported_knowledge_invented":
            False,

        "silent_resolution_performed":
            False,

        "semantic_memory_written":
            False,

        "linking_decisions_performed":
            False,

        "authority_ready":
            True,

        "next_owner":
            "4.6.24_AUTHORITY",

        "dynamic_semantic_graph_owner":
            "4.6.26_DYNAMIC_SEMANTIC_GRAPH",

        "learning_engine_owner":
            "4.6.27_LEARNING_ENGINE",

        "semantic_memory_owner":
            "4.6.28_SEMANTIC_MEMORY",
    }

    certified_final = deepcopy(
        dict(final)
    )

    certified_final[
        "full_transfer_learning_certified"
    ] = True

    certified_final[
        "certification_status"
    ] = "CERTIFIED"

    certified_final[
        "certification_patch"
    ] = "4.6.23K"

    certified_final[
        "certification_id"
    ] = certification[
        "certification_id"
    ]

    certified_final[
        "certification_digest"
    ] = certification[
        "certification_digest"
    ]

    return {
        "schema_version":
            "certified_transfer_learning_result_v1",

        "version":
            TRANSFER_LEARNING_VERSION,

        "phase":
            TRANSFER_LEARNING_PHASE,

        "patch":
            "4.6.23K",

        "status":
            "TRANSFER_LEARNING_CERTIFIED",

        "workspace_id":
            workspace_id,

        "certified_final_transfer_learning_result":
            certified_final,

        "full_transfer_learning_certification":
            certification,

        "source_final_result_envelope":
            deepcopy(
                dict(final_envelope)
            ),

        "processing_boundaries": {
            "certified_ontology_alignment_input_inspected":
                True,

            "certified_ontology_alignment_input_preserved":
                True,

            "ontology_alignment_integrity_preserved":
                True,

            "ontology_alignment_provenance_preserved":
                True,

            "alignment_outcomes_preserved":
                True,

            "ambiguity_preserved":
                True,

            "conflicts_preserved":
                True,

            "uncertainty_preserved":
                True,

            "transfer_learning_architecture_defined":
                True,

            "transfer_learning_intake_validated":
                True,

            "transfer_scope_defined":
                True,

            "transfer_eligibility_evaluated":
                True,

            "transferable_knowledge_extracted":
                True,

            "knowledge_adaptation_performed":
                True,

            "transfer_learning_performed":
                True,

            "transfer_execution_provisional":
                True,

            "transfer_integrity_verification_performed":
                True,

            "negative_transfer_guard_performed":
                True,

            "transfer_provenance_built":
                True,

            "final_transfer_learning_result_built":
                True,

            "full_transfer_learning_certification_performed":
                True,

            "source_ontology_alignment_modified":
                False,

            "source_reasoning_modified":
                False,

            "unsupported_knowledge_invented":
                False,

            "silent_resolution_performed":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,
        },

        "transfer_policy":
            "FULL_TRANSFER_LEARNING_CERTIFIED",

        "next_stage":
            "authority",
    }

