from __future__ import annotations

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

