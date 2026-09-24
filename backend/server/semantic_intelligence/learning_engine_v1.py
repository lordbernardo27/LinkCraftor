from __future__ import annotations

import json
from typing import Any

import copy


import hashlib
LEARNING_ENGINE_VERSION = "learning_engine_v1"
LEARNING_ENGINE_PHASE = "4.6.27"


class LearningEngineError(ValueError):
    """Raised when Learning Engine contracts are violated."""

def inspect_certified_dynamic_semantic_graph_input_v1(
    final_graph_result: dict[str, Any],
    graph_certification_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.27A ? Certified Dynamic Semantic Graph Input Inspection.

    Accepts only:
    1. the certified 4.6.26L Final Dynamic Semantic Graph Result; and
    2. the matching 4.6.26M Full Dynamic Semantic Graph certification.

    Inspection only.

    This stage does not:
    - learn patterns,
    - modify graph objects,
    - create graph nodes or edges,
    - change Authority,
    - change Claim Integrity,
    - change conflicts,
    - override guard state,
    - write Semantic Memory,
    - execute reasoning,
    - create/select targets,
    - make linking decisions,
    - create editor highlights.
    """

    if not isinstance(
        final_graph_result,
        dict,
    ):
        raise LearningEngineError(
            "final_graph_result must be a dictionary."
        )

    if not isinstance(
        graph_certification_result,
        dict,
    ):
        raise LearningEngineError(
            "graph_certification_result must be a dictionary."
        )

    expected_final_lifecycle = {
        "schema":
            "final_dynamic_semantic_graph_result_v1",

        "dynamic_semantic_graph_version":
            "dynamic_semantic_graph_v1",

        "phase":
            "4.6.26",

        "patch":
            "4.6.26L",

        "status":
            "FINAL_DYNAMIC_SEMANTIC_GRAPH_RESULT_BUILT",

        "policy":
            "CERTIFIED_FINAL_DYNAMIC_SEMANTIC_GRAPH_RESULT",

        "next":
            "full_dynamic_semantic_graph_hard_certification",
    }

    for key, expected in expected_final_lifecycle.items():

        if final_graph_result.get(key) != expected:

            raise LearningEngineError(
                "Invalid certified Dynamic Semantic Graph final result: "
                f"{key}"
            )

    expected_certification_lifecycle = {
        "schema":
            "full_dynamic_semantic_graph_hard_certification_result_v1",

        "dynamic_semantic_graph_version":
            "dynamic_semantic_graph_v1",

        "phase":
            "4.6.26",

        "patch":
            "4.6.26M",

        "status":
            "DYNAMIC_SEMANTIC_GRAPH_FULL_HARD_CERTIFIED",

        "policy":
            "CERTIFIED_FULL_DYNAMIC_SEMANTIC_GRAPH_V1",

        "next":
            "learning_engine",
    }

    for key, expected in expected_certification_lifecycle.items():

        if graph_certification_result.get(key) != expected:

            raise LearningEngineError(
                "Invalid Dynamic Semantic Graph hard certification: "
                f"{key}"
            )

    package = final_graph_result.get(
        "final_dynamic_semantic_graph_package"
    )

    downstream = final_graph_result.get(
        "downstream_contract"
    )

    preservation = final_graph_result.get(
        "preservation_contract"
    )

    if not isinstance(package, dict):

        raise LearningEngineError(
            "Final Dynamic Semantic Graph package is missing."
        )

    if (
        package.get("schema")
        != "final_dynamic_semantic_graph_package_v1"
    ):

        raise LearningEngineError(
            "Invalid final Dynamic Semantic Graph package schema."
        )

    if (
        package.get("final_policy")
        != "CERTIFIED_DYNAMIC_SEMANTIC_GRAPH_FOR_DOWNSTREAM_CONSUMPTION"
    ):

        raise LearningEngineError(
            "Dynamic Semantic Graph is not certified for downstream consumption."
        )

    if not isinstance(
        downstream,
        dict,
    ):

        raise LearningEngineError(
            "Dynamic Semantic Graph downstream contract is missing."
        )

    if (
        downstream.get("schema")
        != "dynamic_semantic_graph_downstream_contract_v1"
    ):

        raise LearningEngineError(
            "Invalid Dynamic Semantic Graph downstream contract."
        )

    required_downstream_true = (
        "graph_represents_certified_semantic_state",
        "graph_is_dynamic_and_versioned",
        "graph_is_provenance_bound",
        "graph_is_lineage_traceable",
        "graph_preserves_historical_versions",
        "graph_preserves_claim_integrity",
        "graph_preserves_authority",
        "graph_preserves_conflict",
        "graph_preserves_guard_state",
        "graph_preserves_active_target_set_ownership",
        "graph_target_references_are_reference_only",
        "graph_does_not_select_final_external_target",
        "graph_does_not_write_semantic_memory",
        "graph_does_not_execute_learning",
        "graph_does_not_execute_reasoning",
        "graph_does_not_make_linking_decisions",
        "graph_does_not_create_editor_highlights",
        "downstream_consumption_authorized",
    )

    for flag in required_downstream_true:

        if downstream.get(flag) is not True:

            raise LearningEngineError(
                "Dynamic Semantic Graph downstream contract drift: "
                f"{flag}"
            )

    if (
        downstream.get(
            "next_semantic_intelligence_component"
        )
        != "LEARNING_ENGINE"
    ):

        raise LearningEngineError(
            "Dynamic Semantic Graph is not handed off to Learning Engine."
        )

    if downstream.get(
        "upstream_truth_rewritten"
    ) is not False:

        raise LearningEngineError(
            "Dynamic Semantic Graph indicates upstream truth rewrite."
        )

    if not isinstance(
        preservation,
        dict,
    ):

        raise LearningEngineError(
            "Dynamic Semantic Graph preservation contract is missing."
        )

    required_preservation_true = (
        "claim_integrity_preserved",
        "authority_preserved",
        "support_preserved",
        "conflict_preserved",
        "guard_preserved",
        "provenance_preserved",
        "active_target_set_ownership_preserved",
        "external_authority_partition_preserved",
        "external_route_eligibility_preserved",
        "external_resolver_ownership_preserved",
    )

    for flag in required_preservation_true:

        if preservation.get(flag) is not True:

            raise LearningEngineError(
                "Dynamic Semantic Graph preservation drift: "
                f"{flag}"
            )

    identity_fields = (
        "final_graph_id",
        "final_graph_digest",
        "graph_snapshot_id",
        "graph_snapshot_digest",
        "lineage_root_id",
        "lineage_root_digest",
    )

    for field in identity_fields:

        final_value = final_graph_result.get(
            field
        )

        certified_value = graph_certification_result.get(
            field
        )

        if final_value != certified_value:

            raise LearningEngineError(
                "Dynamic Semantic Graph certification identity mismatch: "
                f"{field}"
            )

    if (
        package.get("final_graph_id")
        != final_graph_result.get(
            "final_graph_id"
        )
    ):

        raise LearningEngineError(
            "Final graph package ID mismatch."
        )

    if (
        package.get("final_graph_digest")
        != final_graph_result.get(
            "final_graph_digest"
        )
    ):

        raise LearningEngineError(
            "Final graph package digest mismatch."
        )

    required_certifications = (
        "preservation_certified",
        "referential_integrity_certified",
        "dynamic_versioning_certified",
        "historical_trace_certified",
        "provenance_lineage_certified",
        "target_ownership_certified",
        "no_truth_rewrite_certified",
        "no_semantic_memory_write_certified",
        "no_learning_execution_certified",
        "no_reasoning_execution_certified",
        "no_target_selection_certified",
        "no_linking_decision_certified",
    )

    for flag in required_certifications:

        if graph_certification_result.get(
            flag
        ) is not True:

            raise LearningEngineError(
                "Dynamic Semantic Graph certification flag missing: "
                f"{flag}"
            )

    if (
        graph_certification_result.get(
            "downstream_handoff"
        )
        != "LEARNING_ENGINE"
    ):

        raise LearningEngineError(
            "Certified graph downstream handoff mismatch."
        )

    stage_chain = graph_certification_result.get(
        "certified_stage_chain"
    )

    expected_stage_chain = (
        "4.6.26A",
        "4.6.26B",
        "4.6.26C",
        "4.6.26D",
        "4.6.26E",
        "4.6.26F",
        "4.6.26G",
        "4.6.26H",
        "4.6.26I",
        "4.6.26J",
        "4.6.26K",
        "4.6.26L",
    )

    if stage_chain != expected_stage_chain:

        raise LearningEngineError(
            "Dynamic Semantic Graph certified stage chain mismatch."
        )

    if (
        graph_certification_result.get(
            "certified_stage_count"
        )
        != 12
    ):

        raise LearningEngineError(
            "Dynamic Semantic Graph certified stage count mismatch."
        )

    nodes = package.get(
        "canonical_graph_nodes"
    )

    edges = package.get(
        "canonical_graph_edges"
    )

    active_lineage = package.get(
        "active_object_lineage"
    )

    historical_lineage = package.get(
        "historical_lineage"
    )

    history = package.get(
        "historical_object_versions"
    )

    if not isinstance(nodes, list):

        raise LearningEngineError(
            "Certified graph nodes must be a list."
        )

    if not isinstance(edges, list):

        raise LearningEngineError(
            "Certified graph edges must be a list."
        )

    if not isinstance(
        active_lineage,
        list,
    ):

        raise LearningEngineError(
            "Certified graph active lineage must be a list."
        )

    if not isinstance(
        historical_lineage,
        list,
    ):

        raise LearningEngineError(
            "Certified graph historical lineage must be a list."
        )

    if not isinstance(
        history,
        list,
    ):

        raise LearningEngineError(
            "Certified graph history must be a list."
        )

    if package.get(
        "node_count"
    ) != len(nodes):

        raise LearningEngineError(
            "Certified graph node count mismatch."
        )

    if package.get(
        "edge_count"
    ) != len(edges):

        raise LearningEngineError(
            "Certified graph edge count mismatch."
        )

    if package.get(
        "historical_version_count"
    ) != len(history):

        raise LearningEngineError(
            "Certified graph historical version count mismatch."
        )

    if len(
        active_lineage
    ) != (
        len(nodes)
        + len(edges)
    ):

        raise LearningEngineError(
            "Certified graph active lineage coverage mismatch."
        )

    if len(
        historical_lineage
    ) != len(history):

        raise LearningEngineError(
            "Certified graph historical lineage coverage mismatch."
        )

    return {
        "schema":
            "learning_engine_dynamic_graph_input_inspection_result_v1",

        "learning_engine_version":
            LEARNING_ENGINE_VERSION,

        "phase":
            LEARNING_ENGINE_PHASE,

        "patch":
            "4.6.27A",

        "status":
            "CERTIFIED_DYNAMIC_SEMANTIC_GRAPH_INPUT_INSPECTED",

        "source_dynamic_semantic_graph_version":
            "dynamic_semantic_graph_v1",

        "source_dynamic_semantic_graph_phase":
            "4.6.26",

        "source_final_graph_id":
            final_graph_result.get(
                "final_graph_id"
            ),

        "source_final_graph_digest":
            final_graph_result.get(
                "final_graph_digest"
            ),

        "source_graph_snapshot_id":
            final_graph_result.get(
                "graph_snapshot_id"
            ),

        "source_graph_snapshot_digest":
            final_graph_result.get(
                "graph_snapshot_digest"
            ),

        "source_lineage_root_id":
            final_graph_result.get(
                "lineage_root_id"
            ),

        "source_lineage_root_digest":
            final_graph_result.get(
                "lineage_root_digest"
            ),

        "node_count":
            len(nodes),

        "edge_count":
            len(edges),

        "historical_version_count":
            len(history),

        "active_lineage_count":
            len(
                active_lineage
            ),

        "historical_lineage_count":
            len(
                historical_lineage
            ),

        "certified_dynamic_semantic_graph_package":
            copy.deepcopy(
                package
            ),

        "dynamic_semantic_graph_certification":
            copy.deepcopy(
                graph_certification_result
            ),

        "preservation_contract":
            copy.deepcopy(
                preservation
            ),

        "inspection_boundaries": {
            "certified_graph_inspection_performed":
                True,

            "graph_mutation_performed":
                False,

            "learning_performed":
                False,

            "pattern_learning_performed":
                False,

            "relationship_learning_performed":
                False,

            "authority_changed":
                False,

            "claim_integrity_changed":
                False,

            "conflict_changed":
                False,

            "guard_state_changed":
                False,

            "semantic_memory_written":
                False,

            "reasoning_performed":
                False,

            "external_target_created":
                False,

            "external_target_selected":
                False,

            "linking_decisions_performed":
                False,

            "highlights_created":
                False,

            "upstream_truth_rewritten":
                False,
        },

        "policy":
            "CERTIFIED_DYNAMIC_SEMANTIC_GRAPH_INPUT_ONLY",

        "next":
            "learning_engine_architecture_definition",
    }

def define_learning_engine_architecture_v1(
    inspection_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.27B ? Learning Engine Architecture Definition.

    Defines the canonical Learning Engine architecture only.

    No learning is executed at this stage.
    """

    if not isinstance(
        inspection_result,
        dict,
    ):
        raise LearningEngineError(
            "inspection_result must be a dictionary."
        )

    expected_lifecycle = {
        "schema":
            "learning_engine_dynamic_graph_input_inspection_result_v1",

        "learning_engine_version":
            LEARNING_ENGINE_VERSION,

        "phase":
            LEARNING_ENGINE_PHASE,

        "patch":
            "4.6.27A",

        "status":
            "CERTIFIED_DYNAMIC_SEMANTIC_GRAPH_INPUT_INSPECTED",

        "policy":
            "CERTIFIED_DYNAMIC_SEMANTIC_GRAPH_INPUT_ONLY",

        "next":
            "learning_engine_architecture_definition",
    }

    for key, expected in expected_lifecycle.items():

        if inspection_result.get(key) != expected:
            raise LearningEngineError(
                "Invalid 4.6.27A lifecycle field: "
                f"{key}"
            )

    package = inspection_result.get(
        "certified_dynamic_semantic_graph_package"
    )

    certification = inspection_result.get(
        "dynamic_semantic_graph_certification"
    )

    preservation = inspection_result.get(
        "preservation_contract"
    )

    if not isinstance(package, dict):
        raise LearningEngineError(
            "Certified Dynamic Semantic Graph package is missing."
        )

    if not isinstance(certification, dict):
        raise LearningEngineError(
            "Dynamic Semantic Graph certification is missing."
        )

    if not isinstance(preservation, dict):
        raise LearningEngineError(
            "preservation_contract must be a dictionary."
        )

    learning_question = (
        "WHAT_REPEATABLE_SEMANTIC_PATTERNS_RELATIONSHIPS_AND_"
        "EXCEPTIONS_CAN_BE_LEARNED_FROM_CERTIFIED_GRAPH_EVIDENCE_"
        "WITHOUT_REWRITING_THE_CERTIFIED_FACTS_THAT_PRODUCED_THEM"
    )

    learning_policy = (
        "EVIDENCE_BOUND_NON_DESTRUCTIVE_SEMANTIC_LEARNING_ONLY"
    )

    learning_object_types = (
        "SEMANTIC_PATTERN",
        "RELATIONSHIP_PATTERN",
        "EVIDENCE_PATTERN",
        "AUTHORITY_PATTERN",
        "CONFLICT_PATTERN",
        "EXCEPTION_PATTERN",
        "CONTEXT_PATTERN",
        "TEMPORAL_PATTERN",
        "CO_OCCURRENCE_PATTERN",
        "GRAPH_TRANSITION_PATTERN",
    )

    observation_units = (
        "NODE_OBSERVATION",
        "EDGE_OBSERVATION",
        "SUBGRAPH_OBSERVATION",
        "SNAPSHOT_OBSERVATION",
        "HISTORICAL_TRANSITION_OBSERVATION",
        "PROVENANCE_OBSERVATION",
        "CONFLICT_OBSERVATION",
        "AUTHORITY_OBSERVATION",
        "INTEGRITY_OBSERVATION",
        "GUARD_OBSERVATION",
    )

    learning_states = (
        "OBSERVED",
        "CANDIDATE",
        "SUPPORTED",
        "STABLE",
        "CONTESTED",
        "WEAKENED",
        "SUPERSEDED",
        "RETIRED",
        "BLOCKED",
    )

    evidence_states = (
        "INSUFFICIENT",
        "EMERGING",
        "SUPPORTED",
        "STRONGLY_SUPPORTED",
        "CONFLICTING",
        "UNRESOLVED",
    )

    confidence_states = (
        "VERY_LOW",
        "LOW",
        "MODERATE",
        "HIGH",
        "VERY_HIGH",
    )

    learning_layers = (
        "OBSERVATION_LAYER",
        "PATTERN_LAYER",
        "RELATIONSHIP_LAYER",
        "AUTHORITY_EVIDENCE_LAYER",
        "CONFLICT_EXCEPTION_LAYER",
        "STABILITY_GUARD_LAYER",
        "PROVENANCE_LINEAGE_LAYER",
        "FINAL_LEARNING_RESULT_LAYER",
    )

    identity_rules = (
        "EVERY_LEARNED_OBJECT_MUST_HAVE_STABLE_CANONICAL_ID",
        "LEARNED_OBJECT_IDENTITY_MUST_BE_TYPE_SCOPED",
        "CANONICAL_LEARNING_IDS_MUST_BE_DETERMINISTIC",
        "LEARNING_MUST_PRESERVE_SOURCE_GRAPH_IDS",
        "LEARNING_MUST_PRESERVE_SOURCE_LINEAGE_IDS",
        "EQUIVALENT_LEARNED_OBJECTS_MUST_NOT_BE_DUPLICATED",
        "LEARNED_OBJECT_IDENTITY_MUST_NOT_REDEFINE_GRAPH_IDENTITY",
    )

    learning_rules = (
        "LEARNING_REQUIRES_CERTIFIED_GRAPH_EVIDENCE",
        "LEARNING_MUST_BE_PROVENANCE_BOUND",
        "LEARNING_MUST_BE_VERSION_AWARE",
        "LEARNING_MUST_PRESERVE_CONTRADICTORY_EVIDENCE",
        "LEARNING_MUST_PRESERVE_EXCEPTIONS",
        "LEARNING_MUST_DISTINGUISH_OBSERVATION_FROM_INFERENCE",
        "LEARNING_MUST_DISTINGUISH_PATTERN_FROM_FACT",
        "LEARNING_MUST_NOT_PROMOTE_FREQUENCY_TO_TRUTH",
        "LEARNING_MUST_NOT_PROMOTE_AUTHORITY_TO_TRUTH",
        "LEARNING_MUST_NOT_ERASE_MINOR_OR_DISSENTING_PATTERNS",
        "LEARNING_MUST_SUPPORT_SUPERSESSION_WITH_HISTORY",
        "LEARNING_MUST_BE_IDEMPOTENT_FOR_EQUIVALENT_INPUT",
    )

    invariants = (
        "CERTIFIED_DYNAMIC_GRAPH_REMAINS_IMMUTABLE",
        "CLAIM_INTEGRITY_REMAINS_UPSTREAM_OWNED",
        "AUTHORITY_REMAINS_UPSTREAM_OWNED",
        "CONFLICT_CLASSIFICATION_REMAINS_UPSTREAM_OWNED",
        "GUARD_DISPOSITION_REMAINS_UPSTREAM_OWNED",
        "ACTIVE_TARGET_SET_REMAINS_TARGET_OWNER",
        "EXTERNAL_AUTHORITY_REMAINS_EXTERNAL_PARTITION",
        "EXTERNAL_ROUTE_REMAINS_EXTERNAL_ELIGIBILITY_ROUTE",
        "EXTERNAL_TARGET_RESOLVER_REMAINS_FINAL_EXTERNAL_SELECTOR",
        "SEMANTIC_MEMORY_IS_NOT_WRITTEN_BY_ARCHITECTURE_DEFINITION",
        "LEARNING_RESULT_IS_NOT_A_LINKING_DECISION",
        "LEARNING_RESULT_IS_NOT_AN_EDITOR_HIGHLIGHT",
        "LEARNING_RESULT_IS_NOT_AUTOMATIC_TRUTH",
        "LEARNING_RESULT_IS_NOT_AUTOMATIC_REASONING_OUTPUT",
    )

    ownership_contract = {
        "certified_semantic_state_owner":
            "DYNAMIC_SEMANTIC_GRAPH",

        "learning_pattern_owner":
            "LEARNING_ENGINE",

        "persistent_learned_memory_owner":
            "SEMANTIC_MEMORY",

        "target_owner":
            "ACTIVE_TARGET_SET",

        "external_partition":
            "EXTERNAL_AUTHORITY",

        "external_route":
            "EXTERNAL",

        "final_external_selection_owner":
            "EXTERNAL_TARGET_RESOLVER",

        "learning_engine_may_rewrite_dynamic_graph":
            False,

        "learning_engine_may_write_semantic_memory_in_architecture_stage":
            False,

        "learning_engine_may_select_final_target":
            False,

        "learning_engine_may_make_linking_decision":
            False,
    }

    boundaries = {
        "architecture_definition_performed":
            True,

        "learning_performed":
            False,

        "pattern_learning_performed":
            False,

        "relationship_learning_performed":
            False,

        "graph_mutation_performed":
            False,

        "authority_changed":
            False,

        "claim_integrity_changed":
            False,

        "conflict_changed":
            False,

        "guard_state_changed":
            False,

        "semantic_memory_written":
            False,

        "reasoning_performed":
            False,

        "external_target_created":
            False,

        "external_target_selected":
            False,

        "linking_decisions_performed":
            False,

        "highlights_created":
            False,

        "upstream_truth_rewritten":
            False,
    }

    architecture = {
        "schema":
            "learning_engine_architecture_v1",

        "learning_engine_version":
            LEARNING_ENGINE_VERSION,

        "learning_question":
            learning_question,

        "learning_policy":
            learning_policy,

        "learning_object_types":
            learning_object_types,

        "observation_units":
            observation_units,

        "learning_states":
            learning_states,

        "evidence_states":
            evidence_states,

        "confidence_states":
            confidence_states,

        "learning_layers":
            learning_layers,

        "identity_rules":
            identity_rules,

        "learning_rules":
            learning_rules,

        "invariants":
            invariants,

        "ownership_contract":
            ownership_contract,
    }

    return {
        "schema":
            "learning_engine_architecture_result_v1",

        "learning_engine_version":
            LEARNING_ENGINE_VERSION,

        "phase":
            LEARNING_ENGINE_PHASE,

        "patch":
            "4.6.27B",

        "status":
            "LEARNING_ENGINE_ARCHITECTURE_DEFINED",

        "source_final_graph_id":
            inspection_result.get(
                "source_final_graph_id"
            ),

        "source_final_graph_digest":
            inspection_result.get(
                "source_final_graph_digest"
            ),

        "source_graph_snapshot_id":
            inspection_result.get(
                "source_graph_snapshot_id"
            ),

        "source_lineage_root_id":
            inspection_result.get(
                "source_lineage_root_id"
            ),

        "architecture":
            architecture,

        "certified_dynamic_semantic_graph_package":
            copy.deepcopy(
                package
            ),

        "dynamic_semantic_graph_certification":
            copy.deepcopy(
                certification
            ),

        "preservation_contract":
            copy.deepcopy(
                preservation
            ),

        "processing_boundaries":
            boundaries,

        "policy":
            "CERTIFIED_LEARNING_ENGINE_ARCHITECTURE",

        "next":
            "learning_intake_validation",
    }

def validate_learning_intake_v1(
    architecture_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.27C ? Learning Intake Validation.

    Validates that the certified Dynamic Semantic Graph-backed
    Learning Engine architecture is structurally suitable for
    downstream learning stages.

    Validation only.

    No semantic learning, graph mutation, memory write,
    reasoning, target selection, linking decision, or
    editor highlight is performed.
    """

    if not isinstance(
        architecture_result,
        dict,
    ):
        raise LearningEngineError(
            "architecture_result must be a dictionary."
        )

    expected_lifecycle = {
        "schema":
            "learning_engine_architecture_result_v1",

        "learning_engine_version":
            LEARNING_ENGINE_VERSION,

        "phase":
            LEARNING_ENGINE_PHASE,

        "patch":
            "4.6.27B",

        "status":
            "LEARNING_ENGINE_ARCHITECTURE_DEFINED",

        "policy":
            "CERTIFIED_LEARNING_ENGINE_ARCHITECTURE",

        "next":
            "learning_intake_validation",
    }

    for key, expected in expected_lifecycle.items():

        if architecture_result.get(key) != expected:
            raise LearningEngineError(
                "Invalid 4.6.27B lifecycle field: "
                f"{key}"
            )

    architecture = architecture_result.get(
        "architecture"
    )

    package = architecture_result.get(
        "certified_dynamic_semantic_graph_package"
    )

    certification = architecture_result.get(
        "dynamic_semantic_graph_certification"
    )

    preservation = architecture_result.get(
        "preservation_contract"
    )

    boundaries = architecture_result.get(
        "processing_boundaries"
    )

    if not isinstance(
        architecture,
        dict,
    ):
        raise LearningEngineError(
            "Learning Engine architecture is missing."
        )

    if (
        architecture.get("schema")
        != "learning_engine_architecture_v1"
    ):
        raise LearningEngineError(
            "Invalid Learning Engine architecture schema."
        )

    if (
        architecture.get(
            "learning_policy"
        )
        != "EVIDENCE_BOUND_NON_DESTRUCTIVE_SEMANTIC_LEARNING_ONLY"
    ):
        raise LearningEngineError(
            "Invalid Learning Engine policy."
        )

    if not isinstance(
        package,
        dict,
    ):
        raise LearningEngineError(
            "Certified Dynamic Semantic Graph package is missing."
        )

    if not isinstance(
        certification,
        dict,
    ):
        raise LearningEngineError(
            "Dynamic Semantic Graph certification is missing."
        )

    if not isinstance(
        preservation,
        dict,
    ):
        raise LearningEngineError(
            "preservation_contract must be a dictionary."
        )

    if not isinstance(
        boundaries,
        dict,
    ):
        raise LearningEngineError(
            "processing_boundaries must be a dictionary."
        )

    required_object_types = (
        "SEMANTIC_PATTERN",
        "RELATIONSHIP_PATTERN",
        "EVIDENCE_PATTERN",
        "AUTHORITY_PATTERN",
        "CONFLICT_PATTERN",
        "EXCEPTION_PATTERN",
        "CONTEXT_PATTERN",
        "TEMPORAL_PATTERN",
        "CO_OCCURRENCE_PATTERN",
        "GRAPH_TRANSITION_PATTERN",
    )

    object_types = architecture.get(
        "learning_object_types"
    )

    if not isinstance(
        object_types,
        tuple,
    ):
        raise LearningEngineError(
            "learning_object_types must be a tuple."
        )

    for item in required_object_types:

        if item not in object_types:
            raise LearningEngineError(
                "Required learning object type missing: "
                f"{item}"
            )

    required_observation_units = (
        "NODE_OBSERVATION",
        "EDGE_OBSERVATION",
        "SUBGRAPH_OBSERVATION",
        "SNAPSHOT_OBSERVATION",
        "HISTORICAL_TRANSITION_OBSERVATION",
        "PROVENANCE_OBSERVATION",
        "CONFLICT_OBSERVATION",
        "AUTHORITY_OBSERVATION",
        "INTEGRITY_OBSERVATION",
        "GUARD_OBSERVATION",
    )

    observation_units = architecture.get(
        "observation_units"
    )

    if not isinstance(
        observation_units,
        tuple,
    ):
        raise LearningEngineError(
            "observation_units must be a tuple."
        )

    for item in required_observation_units:

        if item not in observation_units:
            raise LearningEngineError(
                "Required learning observation unit missing: "
                f"{item}"
            )

    required_learning_states = (
        "OBSERVED",
        "CANDIDATE",
        "SUPPORTED",
        "STABLE",
        "CONTESTED",
        "WEAKENED",
        "SUPERSEDED",
        "RETIRED",
        "BLOCKED",
    )

    learning_states = architecture.get(
        "learning_states"
    )

    if not isinstance(
        learning_states,
        tuple,
    ):
        raise LearningEngineError(
            "learning_states must be a tuple."
        )

    for state in required_learning_states:

        if state not in learning_states:
            raise LearningEngineError(
                "Required learning state missing: "
                f"{state}"
            )

    required_evidence_states = (
        "INSUFFICIENT",
        "EMERGING",
        "SUPPORTED",
        "STRONGLY_SUPPORTED",
        "CONFLICTING",
        "UNRESOLVED",
    )

    evidence_states = architecture.get(
        "evidence_states"
    )

    if not isinstance(
        evidence_states,
        tuple,
    ):
        raise LearningEngineError(
            "evidence_states must be a tuple."
        )

    for state in required_evidence_states:

        if state not in evidence_states:
            raise LearningEngineError(
                "Required evidence state missing: "
                f"{state}"
            )

    required_confidence_states = (
        "VERY_LOW",
        "LOW",
        "MODERATE",
        "HIGH",
        "VERY_HIGH",
    )

    confidence_states = architecture.get(
        "confidence_states"
    )

    if not isinstance(
        confidence_states,
        tuple,
    ):
        raise LearningEngineError(
            "confidence_states must be a tuple."
        )

    for state in required_confidence_states:

        if state not in confidence_states:
            raise LearningEngineError(
                "Required confidence state missing: "
                f"{state}"
            )

    required_rules = (
        "LEARNING_REQUIRES_CERTIFIED_GRAPH_EVIDENCE",
        "LEARNING_MUST_BE_PROVENANCE_BOUND",
        "LEARNING_MUST_BE_VERSION_AWARE",
        "LEARNING_MUST_PRESERVE_CONTRADICTORY_EVIDENCE",
        "LEARNING_MUST_PRESERVE_EXCEPTIONS",
        "LEARNING_MUST_DISTINGUISH_OBSERVATION_FROM_INFERENCE",
        "LEARNING_MUST_DISTINGUISH_PATTERN_FROM_FACT",
        "LEARNING_MUST_NOT_PROMOTE_FREQUENCY_TO_TRUTH",
        "LEARNING_MUST_NOT_PROMOTE_AUTHORITY_TO_TRUTH",
        "LEARNING_MUST_NOT_ERASE_MINOR_OR_DISSENTING_PATTERNS",
        "LEARNING_MUST_SUPPORT_SUPERSESSION_WITH_HISTORY",
        "LEARNING_MUST_BE_IDEMPOTENT_FOR_EQUIVALENT_INPUT",
    )

    learning_rules = architecture.get(
        "learning_rules"
    )

    if not isinstance(
        learning_rules,
        tuple,
    ):
        raise LearningEngineError(
            "learning_rules must be a tuple."
        )

    for rule in required_rules:

        if rule not in learning_rules:
            raise LearningEngineError(
                "Required learning rule missing: "
                f"{rule}"
            )

    required_invariants = (
        "CERTIFIED_DYNAMIC_GRAPH_REMAINS_IMMUTABLE",
        "CLAIM_INTEGRITY_REMAINS_UPSTREAM_OWNED",
        "AUTHORITY_REMAINS_UPSTREAM_OWNED",
        "CONFLICT_CLASSIFICATION_REMAINS_UPSTREAM_OWNED",
        "GUARD_DISPOSITION_REMAINS_UPSTREAM_OWNED",
        "ACTIVE_TARGET_SET_REMAINS_TARGET_OWNER",
        "EXTERNAL_AUTHORITY_REMAINS_EXTERNAL_PARTITION",
        "EXTERNAL_ROUTE_REMAINS_EXTERNAL_ELIGIBILITY_ROUTE",
        "EXTERNAL_TARGET_RESOLVER_REMAINS_FINAL_EXTERNAL_SELECTOR",
        "SEMANTIC_MEMORY_IS_NOT_WRITTEN_BY_ARCHITECTURE_DEFINITION",
        "LEARNING_RESULT_IS_NOT_A_LINKING_DECISION",
        "LEARNING_RESULT_IS_NOT_AN_EDITOR_HIGHLIGHT",
        "LEARNING_RESULT_IS_NOT_AUTOMATIC_TRUTH",
        "LEARNING_RESULT_IS_NOT_AUTOMATIC_REASONING_OUTPUT",
    )

    invariants = architecture.get(
        "invariants"
    )

    if not isinstance(
        invariants,
        tuple,
    ):
        raise LearningEngineError(
            "invariants must be a tuple."
        )

    for invariant in required_invariants:

        if invariant not in invariants:
            raise LearningEngineError(
                "Required invariant missing: "
                f"{invariant}"
            )

    ownership = architecture.get(
        "ownership_contract"
    )

    if not isinstance(
        ownership,
        dict,
    ):
        raise LearningEngineError(
            "ownership_contract is missing."
        )

    expected_ownership = {
        "certified_semantic_state_owner":
            "DYNAMIC_SEMANTIC_GRAPH",

        "learning_pattern_owner":
            "LEARNING_ENGINE",

        "persistent_learned_memory_owner":
            "SEMANTIC_MEMORY",

        "target_owner":
            "ACTIVE_TARGET_SET",

        "external_partition":
            "EXTERNAL_AUTHORITY",

        "external_route":
            "EXTERNAL",

        "final_external_selection_owner":
            "EXTERNAL_TARGET_RESOLVER",

        "learning_engine_may_rewrite_dynamic_graph":
            False,

        "learning_engine_may_write_semantic_memory_in_architecture_stage":
            False,

        "learning_engine_may_select_final_target":
            False,

        "learning_engine_may_make_linking_decision":
            False,
    }

    for key, expected in expected_ownership.items():

        if ownership.get(key) != expected:
            raise LearningEngineError(
                "Learning ownership contract drift: "
                f"{key}"
            )

    required_preservation = (
        "claim_integrity_preserved",
        "authority_preserved",
        "support_preserved",
        "conflict_preserved",
        "guard_preserved",
        "provenance_preserved",
        "active_target_set_ownership_preserved",
        "external_authority_partition_preserved",
        "external_route_eligibility_preserved",
        "external_resolver_ownership_preserved",
    )

    for flag in required_preservation:

        if preservation.get(flag) is not True:
            raise LearningEngineError(
                "Learning intake preservation drift: "
                f"{flag}"
            )

    if boundaries.get(
        "architecture_definition_performed"
    ) is not True:
        raise LearningEngineError(
            "Learning architecture definition was not certified."
        )

    forbidden_true_boundaries = (
        "learning_performed",
        "pattern_learning_performed",
        "relationship_learning_performed",
        "graph_mutation_performed",
        "authority_changed",
        "claim_integrity_changed",
        "conflict_changed",
        "guard_state_changed",
        "semantic_memory_written",
        "reasoning_performed",
        "external_target_created",
        "external_target_selected",
        "linking_decisions_performed",
        "highlights_created",
        "upstream_truth_rewritten",
    )

    for flag in forbidden_true_boundaries:

        if boundaries.get(flag) is not False:
            raise LearningEngineError(
                "Learning architecture boundary drift: "
                f"{flag}"
            )

    intake_contract = {
        "schema":
            "learning_engine_intake_contract_v1",

        "accepts_certified_dynamic_semantic_graph":
            True,

        "accepts_certified_graph_nodes":
            True,

        "accepts_certified_graph_edges":
            True,

        "accepts_graph_history":
            True,

        "accepts_graph_lineage":
            True,

        "accepts_authority_context":
            True,

        "accepts_claim_integrity_context":
            True,

        "accepts_conflict_context":
            True,

        "accepts_guard_context":
            True,

        "requires_provenance":
            True,

        "requires_version_awareness":
            True,

        "requires_non_destructive_learning":
            True,

        "requires_pattern_fact_separation":
            True,

        "requires_observation_inference_separation":
            True,

        "allows_uncertified_graph_input":
            False,

        "allows_graph_truth_rewrite":
            False,

        "allows_semantic_memory_write_at_intake":
            False,

        "allows_target_selection_at_intake":
            False,

        "allows_linking_decision_at_intake":
            False,
    }

    validation_report = {
        "schema":
            "learning_engine_intake_validation_report_v1",

        "architecture_valid":
            True,

        "learning_object_contract_valid":
            True,

        "observation_contract_valid":
            True,

        "learning_state_contract_valid":
            True,

        "evidence_state_contract_valid":
            True,

        "confidence_state_contract_valid":
            True,

        "learning_rules_valid":
            True,

        "invariants_valid":
            True,

        "ownership_contract_valid":
            True,

        "preservation_contract_valid":
            True,

        "processing_boundaries_valid":
            True,

        "intake_authorized":
            True,
    }

    return {
        "schema":
            "learning_engine_intake_validation_result_v1",

        "learning_engine_version":
            LEARNING_ENGINE_VERSION,

        "phase":
            LEARNING_ENGINE_PHASE,

        "patch":
            "4.6.27C",

        "status":
            "LEARNING_INTAKE_VALIDATED",

        "source_final_graph_id":
            architecture_result.get(
                "source_final_graph_id"
            ),

        "source_final_graph_digest":
            architecture_result.get(
                "source_final_graph_digest"
            ),

        "source_graph_snapshot_id":
            architecture_result.get(
                "source_graph_snapshot_id"
            ),

        "source_lineage_root_id":
            architecture_result.get(
                "source_lineage_root_id"
            ),

        "architecture":
            copy.deepcopy(
                architecture
            ),

        "learning_intake_contract":
            intake_contract,

        "validation_report":
            validation_report,

        "certified_dynamic_semantic_graph_package":
            copy.deepcopy(
                package
            ),

        "dynamic_semantic_graph_certification":
            copy.deepcopy(
                certification
            ),

        "preservation_contract":
            copy.deepcopy(
                preservation
            ),

        "processing_boundaries": {
            "learning_intake_validation_performed":
                True,

            "learning_performed":
                False,

            "pattern_learning_performed":
                False,

            "relationship_learning_performed":
                False,

            "graph_mutation_performed":
                False,

            "authority_changed":
                False,

            "claim_integrity_changed":
                False,

            "conflict_changed":
                False,

            "guard_state_changed":
                False,

            "semantic_memory_written":
                False,

            "reasoning_performed":
                False,

            "external_target_created":
                False,

            "external_target_selected":
                False,

            "linking_decisions_performed":
                False,

            "highlights_created":
                False,

            "upstream_truth_rewritten":
                False,
        },

        "policy":
            "CERTIFIED_LEARNING_INTAKE_VALIDATION",

        "next":
            "learning_scope_and_mutation_contract",
    }

def define_learning_scope_and_mutation_contract_v1(
    intake_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.27D ? Learning Scope & Mutation Contract.

    Defines what the Learning Engine may create, version,
    supersede, retire, and preserve.

    This stage defines permissions only.
    It does not perform learning.
    """

    if not isinstance(
        intake_result,
        dict,
    ):
        raise LearningEngineError(
            "intake_result must be a dictionary."
        )

    expected_lifecycle = {
        "schema":
            "learning_engine_intake_validation_result_v1",

        "learning_engine_version":
            LEARNING_ENGINE_VERSION,

        "phase":
            LEARNING_ENGINE_PHASE,

        "patch":
            "4.6.27C",

        "status":
            "LEARNING_INTAKE_VALIDATED",

        "policy":
            "CERTIFIED_LEARNING_INTAKE_VALIDATION",

        "next":
            "learning_scope_and_mutation_contract",
    }

    for key, expected in expected_lifecycle.items():

        if intake_result.get(key) != expected:
            raise LearningEngineError(
                "Invalid 4.6.27C lifecycle field: "
                f"{key}"
            )

    architecture = intake_result.get(
        "architecture"
    )

    intake_contract = intake_result.get(
        "learning_intake_contract"
    )

    validation_report = intake_result.get(
        "validation_report"
    )

    package = intake_result.get(
        "certified_dynamic_semantic_graph_package"
    )

    certification = intake_result.get(
        "dynamic_semantic_graph_certification"
    )

    preservation = intake_result.get(
        "preservation_contract"
    )

    if not isinstance(
        architecture,
        dict,
    ):
        raise LearningEngineError(
            "Learning Engine architecture is missing."
        )

    if not isinstance(
        intake_contract,
        dict,
    ):
        raise LearningEngineError(
            "Learning intake contract is missing."
        )

    if not isinstance(
        validation_report,
        dict,
    ):
        raise LearningEngineError(
            "Learning validation report is missing."
        )

    if validation_report.get(
        "intake_authorized"
    ) is not True:
        raise LearningEngineError(
            "Learning intake is not authorized."
        )

    if (
        architecture.get("schema")
        != "learning_engine_architecture_v1"
    ):
        raise LearningEngineError(
            "Invalid Learning Engine architecture."
        )

    if (
        intake_contract.get("schema")
        != "learning_engine_intake_contract_v1"
    ):
        raise LearningEngineError(
            "Invalid Learning Engine intake contract."
        )

    if not isinstance(
        package,
        dict,
    ):
        raise LearningEngineError(
            "Certified graph package is missing."
        )

    if not isinstance(
        certification,
        dict,
    ):
        raise LearningEngineError(
            "Dynamic graph certification is missing."
        )

    if not isinstance(
        preservation,
        dict,
    ):
        raise LearningEngineError(
            "Preservation contract is missing."
        )

    allowed_learning_mutations = (
        "CREATE_LEARNED_OBJECT",
        "CREATE_LEARNING_OBSERVATION",
        "ATTACH_LEARNING_EVIDENCE_REFERENCE",
        "ATTACH_LEARNING_PROVENANCE_REFERENCE",
        "ATTACH_SOURCE_GRAPH_REFERENCE",
        "ATTACH_SOURCE_LINEAGE_REFERENCE",
        "UPDATE_LEARNED_OBJECT_SUPPORT_STATE",
        "UPDATE_LEARNED_OBJECT_CONFIDENCE_STATE",
        "UPDATE_LEARNED_OBJECT_STABILITY_STATE",
        "VERSION_LEARNED_OBJECT",
        "SUPERSEDE_LEARNED_OBJECT",
        "RETIRE_LEARNED_OBJECT",
        "PRESERVE_LEARNED_OBJECT_HISTORY",
        "REGISTER_CONFLICTING_PATTERN",
        "REGISTER_EXCEPTION_PATTERN",
    )

    forbidden_mutations = (
        "REWRITE_CERTIFIED_GRAPH_NODE",
        "REWRITE_CERTIFIED_GRAPH_EDGE",
        "DELETE_CERTIFIED_GRAPH_HISTORY",
        "ALTER_GRAPH_LINEAGE",
        "REWRITE_CLAIM",
        "REDECIDE_CLAIM_INTEGRITY",
        "RESCORE_AUTHORITY",
        "RECLASSIFY_AUTHORITY",
        "REDETECT_CONFLICT",
        "RECLASSIFY_CONFLICT",
        "OVERRIDE_GUARD_DISPOSITION",
        "PROMOTE_PATTERN_TO_CERTIFIED_FACT",
        "PROMOTE_FREQUENCY_TO_TRUTH",
        "PROMOTE_AUTHORITY_TO_TRUTH",
        "WRITE_SEMANTIC_MEMORY_DIRECTLY",
        "CREATE_ACTIVE_TARGET",
        "CHANGE_ACTIVE_TARGET_SET_OWNERSHIP",
        "CHANGE_EXTERNAL_AUTHORITY_PARTITION",
        "CHANGE_EXTERNAL_ROUTE_OWNERSHIP",
        "SELECT_FINAL_EXTERNAL_TARGET",
        "MAKE_LINKING_DECISION",
        "CREATE_EDITOR_HIGHLIGHT",
        "EXECUTE_RUNTIME_REASONING",
        "DISCOVER_EXTERNAL_URL",
    )

    learned_object_lifecycle = (
        "OBSERVED",
        "CANDIDATE",
        "SUPPORTED",
        "STABLE",
        "CONTESTED",
        "WEAKENED",
        "SUPERSEDED",
        "RETIRED",
        "BLOCKED",
    )

    mutation_principles = (
        "LEARNING_MUTATES_ONLY_LEARNING_ENGINE_OWNED_OBJECTS",
        "UPSTREAM_CERTIFIED_GRAPH_IS_READ_ONLY",
        "EVERY_MUTATION_REQUIRES_PROVENANCE",
        "EVERY_MUTATION_REQUIRES_SOURCE_GRAPH_REFERENCE",
        "EVERY_MUTATION_MUST_BE_VERSION_AWARE",
        "MUTATION_MUST_PRESERVE_CONFLICTS_AND_EXCEPTIONS",
        "MUTATION_MUST_PRESERVE_SUPERSEDED_HISTORY",
        "EQUIVALENT_INPUT_MUST_BE_IDEMPOTENT",
        "LEARNED_STATE_MUST_NOT_BE_REPRESENTED_AS_CERTIFIED_FACT",
        "SEMANTIC_MEMORY_PERSISTENCE_IS_DOWNSTREAM_OWNED",
    )

    ownership_contract = architecture.get(
        "ownership_contract"
    )

    if not isinstance(
        ownership_contract,
        dict,
    ):
        raise LearningEngineError(
            "Learning ownership contract is missing."
        )

    expected_ownership = {
        "certified_semantic_state_owner":
            "DYNAMIC_SEMANTIC_GRAPH",

        "learning_pattern_owner":
            "LEARNING_ENGINE",

        "persistent_learned_memory_owner":
            "SEMANTIC_MEMORY",

        "target_owner":
            "ACTIVE_TARGET_SET",

        "external_partition":
            "EXTERNAL_AUTHORITY",

        "external_route":
            "EXTERNAL",

        "final_external_selection_owner":
            "EXTERNAL_TARGET_RESOLVER",
    }

    for key, expected in expected_ownership.items():

        if ownership_contract.get(key) != expected:
            raise LearningEngineError(
                "Learning ownership drift: "
                f"{key}"
            )

    scope_contract = {
        "schema":
            "learning_engine_scope_mutation_contract_v1",

        "learning_engine_owns_learned_objects":
            True,

        "dynamic_semantic_graph_is_read_only":
            True,

        "claim_integrity_is_read_only":
            True,

        "authority_is_read_only":
            True,

        "conflict_classification_is_read_only":
            True,

        "guard_disposition_is_read_only":
            True,

        "active_target_set_is_read_only":
            True,

        "semantic_memory_is_downstream":
            True,

        "allowed_learning_mutations":
            allowed_learning_mutations,

        "forbidden_mutations":
            forbidden_mutations,

        "learned_object_lifecycle":
            learned_object_lifecycle,

        "mutation_principles":
            mutation_principles,

        "ownership_contract":
            copy.deepcopy(
                ownership_contract
            ),
    }

    processing_boundaries = {
        "scope_mutation_contract_defined":
            True,

        "learning_performed":
            False,

        "pattern_learning_performed":
            False,

        "relationship_learning_performed":
            False,

        "learned_object_created":
            False,

        "learned_object_mutated":
            False,

        "graph_mutation_performed":
            False,

        "authority_changed":
            False,

        "claim_integrity_changed":
            False,

        "conflict_changed":
            False,

        "guard_state_changed":
            False,

        "semantic_memory_written":
            False,

        "reasoning_performed":
            False,

        "external_target_created":
            False,

        "external_target_selected":
            False,

        "linking_decisions_performed":
            False,

        "highlights_created":
            False,

        "upstream_truth_rewritten":
            False,
    }

    return {
        "schema":
            "learning_engine_scope_mutation_contract_result_v1",

        "learning_engine_version":
            LEARNING_ENGINE_VERSION,

        "phase":
            LEARNING_ENGINE_PHASE,

        "patch":
            "4.6.27D",

        "status":
            "LEARNING_SCOPE_AND_MUTATION_CONTRACT_DEFINED",

        "source_final_graph_id":
            intake_result.get(
                "source_final_graph_id"
            ),

        "source_final_graph_digest":
            intake_result.get(
                "source_final_graph_digest"
            ),

        "source_graph_snapshot_id":
            intake_result.get(
                "source_graph_snapshot_id"
            ),

        "source_lineage_root_id":
            intake_result.get(
                "source_lineage_root_id"
            ),

        "architecture":
            copy.deepcopy(
                architecture
            ),

        "learning_intake_contract":
            copy.deepcopy(
                intake_contract
            ),

        "validation_report":
            copy.deepcopy(
                validation_report
            ),

        "learning_scope_mutation_contract":
            scope_contract,

        "certified_dynamic_semantic_graph_package":
            copy.deepcopy(
                package
            ),

        "dynamic_semantic_graph_certification":
            copy.deepcopy(
                certification
            ),

        "preservation_contract":
            copy.deepcopy(
                preservation
            ),

        "processing_boundaries":
            processing_boundaries,

        "policy":
            "CERTIFIED_LEARNING_SCOPE_AND_MUTATION_CONTRACT",

        "next":
            "semantic_pattern_observation",
    }

def observe_semantic_patterns_v1(
    scope_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.27E ? Semantic Pattern Observation.

    Observes repeatable semantic structures from the certified
    Dynamic Semantic Graph and creates Learning Engine-owned
    observation objects only.

    This stage does not promote observations to learned truth,
    mutate the certified graph, write Semantic Memory, select
    targets, make linking decisions, or create highlights.
    """

    if not isinstance(
        scope_result,
        dict,
    ):
        raise LearningEngineError(
            "scope_result must be a dictionary."
        )

    expected_lifecycle = {
        "schema":
            "learning_engine_scope_mutation_contract_result_v1",

        "learning_engine_version":
            LEARNING_ENGINE_VERSION,

        "phase":
            LEARNING_ENGINE_PHASE,

        "patch":
            "4.6.27D",

        "status":
            "LEARNING_SCOPE_AND_MUTATION_CONTRACT_DEFINED",

        "policy":
            "CERTIFIED_LEARNING_SCOPE_AND_MUTATION_CONTRACT",

        "next":
            "semantic_pattern_observation",
    }

    for key, expected in expected_lifecycle.items():

        if scope_result.get(key) != expected:
            raise LearningEngineError(
                "Invalid 4.6.27D lifecycle field: "
                f"{key}"
            )

    architecture = scope_result.get(
        "architecture"
    )

    intake_contract = scope_result.get(
        "learning_intake_contract"
    )

    validation_report = scope_result.get(
        "validation_report"
    )

    mutation_contract = scope_result.get(
        "learning_scope_mutation_contract"
    )

    graph_package = scope_result.get(
        "certified_dynamic_semantic_graph_package"
    )

    certification = scope_result.get(
        "dynamic_semantic_graph_certification"
    )

    preservation = scope_result.get(
        "preservation_contract"
    )

    if not isinstance(
        architecture,
        dict,
    ):
        raise LearningEngineError(
            "Learning architecture is missing."
        )

    if not isinstance(
        intake_contract,
        dict,
    ):
        raise LearningEngineError(
            "Learning intake contract is missing."
        )

    if not isinstance(
        validation_report,
        dict,
    ):
        raise LearningEngineError(
            "Learning validation report is missing."
        )

    if not isinstance(
        mutation_contract,
        dict,
    ):
        raise LearningEngineError(
            "Learning scope mutation contract is missing."
        )

    if (
        mutation_contract.get("schema")
        != "learning_engine_scope_mutation_contract_v1"
    ):
        raise LearningEngineError(
            "Invalid learning scope mutation contract schema."
        )

    if mutation_contract.get(
        "learning_engine_owns_learned_objects"
    ) is not True:
        raise LearningEngineError(
            "Learning Engine object ownership is not authorized."
        )

    if mutation_contract.get(
        "dynamic_semantic_graph_is_read_only"
    ) is not True:
        raise LearningEngineError(
            "Certified Dynamic Semantic Graph must remain read-only."
        )

    if mutation_contract.get(
        "semantic_memory_is_downstream"
    ) is not True:
        raise LearningEngineError(
            "Semantic Memory ownership drift."
        )

    allowed_mutations = mutation_contract.get(
        "allowed_learning_mutations"
    )

    if not isinstance(
        allowed_mutations,
        tuple,
    ):
        raise LearningEngineError(
            "allowed_learning_mutations must be a tuple."
        )

    for permission in (
        "CREATE_LEARNED_OBJECT",
        "CREATE_LEARNING_OBSERVATION",
        "ATTACH_LEARNING_EVIDENCE_REFERENCE",
        "ATTACH_LEARNING_PROVENANCE_REFERENCE",
        "ATTACH_SOURCE_GRAPH_REFERENCE",
        "ATTACH_SOURCE_LINEAGE_REFERENCE",
    ):

        if permission not in allowed_mutations:
            raise LearningEngineError(
                "Required observation permission missing: "
                f"{permission}"
            )

    if not isinstance(
        graph_package,
        dict,
    ):
        raise LearningEngineError(
            "Certified Dynamic Semantic Graph package is missing."
        )

    if (
        graph_package.get("schema")
        != "final_dynamic_semantic_graph_package_v1"
    ):
        raise LearningEngineError(
            "Invalid certified graph package schema."
        )

    if not isinstance(
        certification,
        dict,
    ):
        raise LearningEngineError(
            "Dynamic Semantic Graph certification is missing."
        )

    if not isinstance(
        preservation,
        dict,
    ):
        raise LearningEngineError(
            "Preservation contract is missing."
        )

    nodes = graph_package.get(
        "canonical_graph_nodes",
        [],
    )

    edges = graph_package.get(
        "canonical_graph_edges",
        [],
    )

    history = graph_package.get(
        "historical_object_versions",
        [],
    )

    active_lineage = graph_package.get(
        "active_object_lineage",
        [],
    )

    historical_lineage = graph_package.get(
        "historical_lineage",
        [],
    )

    for name, value in (
        ("canonical_graph_nodes", nodes),
        ("canonical_graph_edges", edges),
        ("historical_object_versions", history),
        ("active_object_lineage", active_lineage),
        ("historical_lineage", historical_lineage),
    ):

        if not isinstance(
            value,
            list,
        ):
            raise LearningEngineError(
                f"{name} must be a list."
            )

    source_final_graph_id = scope_result.get(
        "source_final_graph_id"
    )

    source_final_graph_digest = scope_result.get(
        "source_final_graph_digest"
    )

    source_graph_snapshot_id = scope_result.get(
        "source_graph_snapshot_id"
    )

    source_lineage_root_id = scope_result.get(
        "source_lineage_root_id"
    )

    if not isinstance(
        source_final_graph_id,
        str,
    ) or not source_final_graph_id:
        raise LearningEngineError(
            "source_final_graph_id is required."
        )

    if not isinstance(
        source_final_graph_digest,
        str,
    ) or not source_final_graph_digest:
        raise LearningEngineError(
            "source_final_graph_digest is required."
        )

    def canonical_digest(payload: Any) -> str:
        serialized = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )

        return hashlib.sha256(
            serialized.encode("utf-8")
        ).hexdigest()

    def make_observation(
        observation_type: str,
        pattern_type: str,
        signature: dict[str, Any],
        source_object_ids: list[str],
        occurrence_count: int,
    ) -> dict[str, Any]:

        canonical_payload = {
            "observation_type":
                observation_type,

            "pattern_type":
                pattern_type,

            "signature":
                signature,

            "source_object_ids":
                sorted(
                    source_object_ids
                ),

            "source_final_graph_id":
                source_final_graph_id,
        }

        digest = canonical_digest(
            canonical_payload
        )

        return {
            "schema":
                "learning_engine_semantic_pattern_observation_v1",

            "observation_id":
                "learningobservation:v1:"
                + digest,

            "observation_digest":
                digest,

            "observation_type":
                observation_type,

            "pattern_type":
                pattern_type,

            "learning_state":
                "OBSERVED",

            "evidence_state":
                (
                    "SUPPORTED"
                    if occurrence_count >= 2
                    else "EMERGING"
                ),

            "confidence_state":
                (
                    "MODERATE"
                    if occurrence_count >= 2
                    else "LOW"
                ),

            "occurrence_count":
                occurrence_count,

            "signature":
                copy.deepcopy(
                    signature
                ),

            "source_object_ids":
                tuple(
                    sorted(
                        source_object_ids
                    )
                ),

            "source_final_graph_id":
                source_final_graph_id,

            "source_final_graph_digest":
                source_final_graph_digest,

            "source_graph_snapshot_id":
                source_graph_snapshot_id,

            "source_lineage_root_id":
                source_lineage_root_id,

            "is_certified_fact":
                False,

            "is_learned_truth":
                False,

            "is_learning_engine_owned":
                True,

            "graph_mutation_performed":
                False,

            "semantic_memory_written":
                False,
        }

    observations = []

    node_type_groups = {}

    for node in nodes:

        if not isinstance(
            node,
            dict,
        ):
            raise LearningEngineError(
                "Graph nodes must be dictionaries."
            )

        node_id = node.get(
            "node_id"
        )

        node_type = node.get(
            "node_type"
        )

        if not isinstance(
            node_id,
            str,
        ) or not node_id:
            raise LearningEngineError(
                "Graph node_id is required."
            )

        if not isinstance(
            node_type,
            str,
        ) or not node_type:
            raise LearningEngineError(
                "Graph node_type is required."
            )

        node_type_groups.setdefault(
            node_type,
            [],
        ).append(
            node_id
        )

    for node_type in sorted(
        node_type_groups
    ):

        ids = node_type_groups[
            node_type
        ]

        observations.append(
            make_observation(
                "NODE_OBSERVATION",
                "SEMANTIC_PATTERN",
                {
                    "node_type":
                        node_type,
                },
                ids,
                len(ids),
            )
        )

    edge_type_groups = {}

    for edge in edges:

        if not isinstance(
            edge,
            dict,
        ):
            raise LearningEngineError(
                "Graph edges must be dictionaries."
            )

        edge_id = edge.get(
            "edge_id"
        )

        edge_type = edge.get(
            "edge_type"
        )

        from_node_id = edge.get(
            "from_node_id"
        )

        to_node_id = edge.get(
            "to_node_id"
        )

        if not isinstance(
            edge_id,
            str,
        ) or not edge_id:
            raise LearningEngineError(
                "Graph edge_id is required."
            )

        if not isinstance(
            edge_type,
            str,
        ) or not edge_type:
            raise LearningEngineError(
                "Graph edge_type is required."
            )

        if not isinstance(
            from_node_id,
            str,
        ) or not from_node_id:
            raise LearningEngineError(
                "Graph from_node_id is required."
            )

        if not isinstance(
            to_node_id,
            str,
        ) or not to_node_id:
            raise LearningEngineError(
                "Graph to_node_id is required."
            )

        signature = (
            edge_type,
            from_node_id.split(
                ":",
                1,
            )[0],
            to_node_id.split(
                ":",
                1,
            )[0],
        )

        edge_type_groups.setdefault(
            signature,
            [],
        ).append(
            edge_id
        )

    for signature in sorted(
        edge_type_groups
    ):

        ids = edge_type_groups[
            signature
        ]

        edge_type, from_family, to_family = signature

        observations.append(
            make_observation(
                "EDGE_OBSERVATION",
                "RELATIONSHIP_PATTERN",
                {
                    "edge_type":
                        edge_type,

                    "from_id_family":
                        from_family,

                    "to_id_family":
                        to_family,
                },
                ids,
                len(ids),
            )
        )

    if history:

        historical_ids = []

        for index, item in enumerate(
            history
        ):

            if not isinstance(
                item,
                dict,
            ):
                raise LearningEngineError(
                    "Historical graph objects must be dictionaries."
                )

            historical_ids.append(
                str(
                    item.get(
                        "historical_version_id",
                        f"history:{index}",
                    )
                )
            )

        observations.append(
            make_observation(
                "HISTORICAL_TRANSITION_OBSERVATION",
                "GRAPH_TRANSITION_PATTERN",
                {
                    "historical_version_count":
                        len(history),
                },
                historical_ids,
                len(history),
            )
        )

    observation_ids = [
        item["observation_id"]
        for item in observations
    ]

    if len(
        observation_ids
    ) != len(
        set(
            observation_ids
        )
    ):
        raise LearningEngineError(
            "Duplicate semantic pattern observation IDs detected."
        )

    observation_bundle_payload = {
        "source_final_graph_id":
            source_final_graph_id,

        "observation_ids":
            sorted(
                observation_ids
            ),
    }

    bundle_digest = canonical_digest(
        observation_bundle_payload
    )

    observation_bundle = {
        "schema":
            "learning_engine_semantic_pattern_observation_bundle_v1",

        "observation_bundle_id":
            "learningobservationbundle:v1:"
            + bundle_digest,

        "observation_bundle_digest":
            bundle_digest,

        "observation_count":
            len(
                observations
            ),

        "observations":
            observations,

        "source_node_count":
            len(
                nodes
            ),

        "source_edge_count":
            len(
                edges
            ),

        "source_historical_version_count":
            len(
                history
            ),

        "source_active_lineage_count":
            len(
                active_lineage
            ),

        "source_historical_lineage_count":
            len(
                historical_lineage
            ),

        "observation_policy":
            "EVIDENCE_BOUND_PATTERN_OBSERVATION_ONLY",
    }

    processing_boundaries = {
        "semantic_pattern_observation_performed":
            True,

        "learning_performed":
            True,

        "pattern_observation_performed":
            True,

        "relationship_learning_performed":
            False,

        "learned_truth_created":
            False,

        "certified_fact_created":
            False,

        "graph_mutation_performed":
            False,

        "authority_changed":
            False,

        "claim_integrity_changed":
            False,

        "conflict_changed":
            False,

        "guard_state_changed":
            False,

        "semantic_memory_written":
            False,

        "reasoning_performed":
            False,

        "external_target_created":
            False,

        "external_target_selected":
            False,

        "linking_decisions_performed":
            False,

        "highlights_created":
            False,

        "upstream_truth_rewritten":
            False,
    }

    return {
        "schema":
            "learning_engine_semantic_pattern_observation_result_v1",

        "learning_engine_version":
            LEARNING_ENGINE_VERSION,

        "phase":
            LEARNING_ENGINE_PHASE,

        "patch":
            "4.6.27E",

        "status":
            "SEMANTIC_PATTERN_OBSERVATION_COMPLETED",

        "source_final_graph_id":
            source_final_graph_id,

        "source_final_graph_digest":
            source_final_graph_digest,

        "source_graph_snapshot_id":
            source_graph_snapshot_id,

        "source_lineage_root_id":
            source_lineage_root_id,

        "learning_scope_mutation_contract":
            copy.deepcopy(
                mutation_contract
            ),

        "semantic_pattern_observation_bundle":
            observation_bundle,

        "certified_dynamic_semantic_graph_package":
            copy.deepcopy(
                graph_package
            ),

        "dynamic_semantic_graph_certification":
            copy.deepcopy(
                certification
            ),

        "preservation_contract":
            copy.deepcopy(
                preservation
            ),

        "processing_boundaries":
            processing_boundaries,

        "policy":
            "CERTIFIED_SEMANTIC_PATTERN_OBSERVATION",

        "next":
            "relationship_learning",
    }

def learn_semantic_relationships_v1(
    observation_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.27F ? Relationship Learning.

    Converts eligible certified semantic relationship observations
    into Learning Engine-owned learned relationship objects.

    Learned relationships remain evidence-bound hypotheses/patterns.
    They are not certified graph facts and do not mutate upstream truth.
    """

    if not isinstance(observation_result, dict):
        raise LearningEngineError(
            "observation_result must be a dictionary."
        )

    expected_lifecycle = {
        "schema":
            "learning_engine_semantic_pattern_observation_result_v1",
        "learning_engine_version":
            LEARNING_ENGINE_VERSION,
        "phase":
            LEARNING_ENGINE_PHASE,
        "patch":
            "4.6.27E",
        "status":
            "SEMANTIC_PATTERN_OBSERVATION_COMPLETED",
        "policy":
            "CERTIFIED_SEMANTIC_PATTERN_OBSERVATION",
        "next":
            "relationship_learning",
    }

    for key, expected in expected_lifecycle.items():
        if observation_result.get(key) != expected:
            raise LearningEngineError(
                "Invalid 4.6.27E lifecycle field: "
                f"{key}"
            )

    bundle = observation_result.get(
        "semantic_pattern_observation_bundle"
    )

    mutation_contract = observation_result.get(
        "learning_scope_mutation_contract"
    )

    graph_package = observation_result.get(
        "certified_dynamic_semantic_graph_package"
    )

    certification = observation_result.get(
        "dynamic_semantic_graph_certification"
    )

    preservation = observation_result.get(
        "preservation_contract"
    )

    if not isinstance(bundle, dict):
        raise LearningEngineError(
            "Semantic pattern observation bundle is missing."
        )

    if (
        bundle.get("schema")
        != "learning_engine_semantic_pattern_observation_bundle_v1"
    ):
        raise LearningEngineError(
            "Invalid semantic pattern observation bundle schema."
        )

    if (
        bundle.get("observation_policy")
        != "EVIDENCE_BOUND_PATTERN_OBSERVATION_ONLY"
    ):
        raise LearningEngineError(
            "Invalid observation policy."
        )

    if not isinstance(mutation_contract, dict):
        raise LearningEngineError(
            "Learning mutation contract is missing."
        )

    if (
        mutation_contract.get("schema")
        != "learning_engine_scope_mutation_contract_v1"
    ):
        raise LearningEngineError(
            "Invalid mutation contract schema."
        )

    if mutation_contract.get(
        "learning_engine_owns_learned_objects"
    ) is not True:
        raise LearningEngineError(
            "Learning Engine object ownership is not authorized."
        )

    if mutation_contract.get(
        "dynamic_semantic_graph_is_read_only"
    ) is not True:
        raise LearningEngineError(
            "Dynamic Semantic Graph must remain read-only."
        )

    if mutation_contract.get(
        "semantic_memory_is_downstream"
    ) is not True:
        raise LearningEngineError(
            "Semantic Memory ownership drift."
        )

    allowed = mutation_contract.get(
        "allowed_learning_mutations"
    )

    if not isinstance(allowed, tuple):
        raise LearningEngineError(
            "allowed_learning_mutations must be a tuple."
        )

    for permission in (
        "CREATE_LEARNED_OBJECT",
        "UPDATE_LEARNED_OBJECT_SUPPORT_STATE",
        "UPDATE_LEARNED_OBJECT_CONFIDENCE_STATE",
        "ATTACH_LEARNING_EVIDENCE_REFERENCE",
        "ATTACH_SOURCE_GRAPH_REFERENCE",
        "ATTACH_SOURCE_LINEAGE_REFERENCE",
    ):
        if permission not in allowed:
            raise LearningEngineError(
                "Required relationship-learning permission missing: "
                f"{permission}"
            )

    observations = bundle.get(
        "observations"
    )

    if not isinstance(observations, list):
        raise LearningEngineError(
            "Observation collection must be a list."
        )

    source_final_graph_id = observation_result.get(
        "source_final_graph_id"
    )

    source_final_graph_digest = observation_result.get(
        "source_final_graph_digest"
    )

    source_graph_snapshot_id = observation_result.get(
        "source_graph_snapshot_id"
    )

    source_lineage_root_id = observation_result.get(
        "source_lineage_root_id"
    )

    learned_relationships = []

    for observation in observations:

        if not isinstance(observation, dict):
            raise LearningEngineError(
                "Observation objects must be dictionaries."
            )

        if (
            observation.get("schema")
            != "learning_engine_semantic_pattern_observation_v1"
        ):
            raise LearningEngineError(
                "Invalid observation schema."
            )

        if observation.get(
            "is_learning_engine_owned"
        ) is not True:
            raise LearningEngineError(
                "Observation ownership drift."
            )

        if observation.get(
            "is_certified_fact"
        ) is not False:
            raise LearningEngineError(
                "Observation must not be a certified fact."
            )

        if observation.get(
            "is_learned_truth"
        ) is not False:
            raise LearningEngineError(
                "Observation must not be represented as learned truth."
            )

        if (
            observation.get("observation_type")
            != "EDGE_OBSERVATION"
        ):
            continue

        if (
            observation.get("pattern_type")
            != "RELATIONSHIP_PATTERN"
        ):
            continue

        occurrence_count = observation.get(
            "occurrence_count"
        )

        if not isinstance(occurrence_count, int):
            raise LearningEngineError(
                "Relationship occurrence_count must be an integer."
            )

        if occurrence_count < 1:
            raise LearningEngineError(
                "Relationship occurrence_count must be positive."
            )

        signature = observation.get(
            "signature"
        )

        if not isinstance(signature, dict):
            raise LearningEngineError(
                "Relationship signature is missing."
            )

        observation_id = observation.get(
            "observation_id"
        )

        observation_digest = observation.get(
            "observation_digest"
        )

        if not isinstance(observation_id, str) or not observation_id:
            raise LearningEngineError(
                "Relationship observation_id is required."
            )

        if (
            not isinstance(observation_digest, str)
            or not observation_digest
        ):
            raise LearningEngineError(
                "Relationship observation_digest is required."
            )

        relationship_payload = {
            "source_observation_id":
                observation_id,
            "relationship_signature":
                signature,
            "source_final_graph_id":
                source_final_graph_id,
        }

        serialized = json.dumps(
            relationship_payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )

        digest = hashlib.sha256(
            serialized.encode("utf-8")
        ).hexdigest()

        evidence_state = (
            "SUPPORTED"
            if occurrence_count >= 2
            else "EMERGING"
        )

        confidence_state = (
            "MODERATE"
            if occurrence_count >= 2
            else "LOW"
        )

        learning_state = (
            "SUPPORTED"
            if occurrence_count >= 2
            else "CANDIDATE"
        )

        learned_relationships.append(
            {
                "schema":
                    "learning_engine_learned_relationship_v1",

                "learned_relationship_id":
                    "learnedrelationship:v1:"
                    + digest,

                "learned_relationship_digest":
                    digest,

                "relationship_type":
                    signature.get(
                        "edge_type"
                    ),

                "relationship_signature":
                    copy.deepcopy(
                        signature
                    ),

                "learning_state":
                    learning_state,

                "evidence_state":
                    evidence_state,

                "confidence_state":
                    confidence_state,

                "occurrence_count":
                    occurrence_count,

                "source_observation_id":
                    observation_id,

                "source_observation_digest":
                    observation_digest,

                "source_object_ids":
                    tuple(
                        observation.get(
                            "source_object_ids",
                            (),
                        )
                    ),

                "source_final_graph_id":
                    source_final_graph_id,

                "source_final_graph_digest":
                    source_final_graph_digest,

                "source_graph_snapshot_id":
                    source_graph_snapshot_id,

                "source_lineage_root_id":
                    source_lineage_root_id,

                "is_learning_engine_owned":
                    True,

                "is_certified_graph_fact":
                    False,

                "is_learned_truth":
                    False,

                "graph_mutation_performed":
                    False,

                "semantic_memory_written":
                    False,

                "linking_decision_performed":
                    False,
            }
        )

    learned_relationships.sort(
        key=lambda x:
            x["learned_relationship_id"]
    )

    ids = [
        item["learned_relationship_id"]
        for item in learned_relationships
    ]

    if len(ids) != len(set(ids)):
        raise LearningEngineError(
            "Duplicate learned relationship IDs detected."
        )

    bundle_payload = {
        "source_final_graph_id":
            source_final_graph_id,
        "learned_relationship_ids":
            ids,
    }

    serialized_bundle = json.dumps(
        bundle_payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    bundle_digest = hashlib.sha256(
        serialized_bundle.encode("utf-8")
    ).hexdigest()

    relationship_bundle = {
        "schema":
            "learning_engine_relationship_learning_bundle_v1",

        "relationship_learning_bundle_id":
            "relationshiplearningbundle:v1:"
            + bundle_digest,

        "relationship_learning_bundle_digest":
            bundle_digest,

        "learned_relationship_count":
            len(learned_relationships),

        "learned_relationships":
            learned_relationships,

        "source_observation_count":
            len(observations),

        "relationship_learning_policy":
            "EVIDENCE_BOUND_NON_TRUTH_RELATIONSHIP_LEARNING_ONLY",
    }

    return {
        "schema":
            "learning_engine_relationship_learning_result_v1",

        "learning_engine_version":
            LEARNING_ENGINE_VERSION,

        "phase":
            LEARNING_ENGINE_PHASE,

        "patch":
            "4.6.27F",

        "status":
            "RELATIONSHIP_LEARNING_COMPLETED",

        "source_final_graph_id":
            source_final_graph_id,

        "source_final_graph_digest":
            source_final_graph_digest,

        "source_graph_snapshot_id":
            source_graph_snapshot_id,

        "source_lineage_root_id":
            source_lineage_root_id,

        "semantic_pattern_observation_bundle":
            copy.deepcopy(bundle),

        "relationship_learning_bundle":
            relationship_bundle,

        "learning_scope_mutation_contract":
            copy.deepcopy(mutation_contract),

        "certified_dynamic_semantic_graph_package":
            copy.deepcopy(graph_package),

        "dynamic_semantic_graph_certification":
            copy.deepcopy(certification),

        "preservation_contract":
            copy.deepcopy(preservation),

        "processing_boundaries": {
            "relationship_learning_performed":
                True,

            "learning_performed":
                True,

            "learned_relationship_objects_created":
                True,

            "learned_truth_created":
                False,

            "certified_fact_created":
                False,

            "graph_mutation_performed":
                False,

            "authority_changed":
                False,

            "claim_integrity_changed":
                False,

            "conflict_changed":
                False,

            "guard_state_changed":
                False,

            "semantic_memory_written":
                False,

            "reasoning_performed":
                False,

            "external_target_created":
                False,

            "external_target_selected":
                False,

            "linking_decisions_performed":
                False,

            "highlights_created":
                False,

            "upstream_truth_rewritten":
                False,
        },

        "policy":
            "CERTIFIED_RELATIONSHIP_LEARNING",

        "next":
            "evidence_authority_learning_integration",
    }

def integrate_evidence_authority_learning_v1(
    relationship_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.27G ? Evidence / Authority Learning Integration.

    Integrates certified evidence and authority context into
    Learning Engine-owned learned objects without rescoring
    Authority, re-deciding Claim Integrity, promoting authority
    to truth, mutating the Dynamic Semantic Graph, or writing
    Semantic Memory.
    """

    if not isinstance(
        relationship_result,
        dict,
    ):
        raise LearningEngineError(
            "relationship_result must be a dictionary."
        )

    expected_lifecycle = {
        "schema":
            "learning_engine_relationship_learning_result_v1",

        "learning_engine_version":
            LEARNING_ENGINE_VERSION,

        "phase":
            LEARNING_ENGINE_PHASE,

        "patch":
            "4.6.27F",

        "status":
            "RELATIONSHIP_LEARNING_COMPLETED",

        "policy":
            "CERTIFIED_RELATIONSHIP_LEARNING",

        "next":
            "evidence_authority_learning_integration",
    }

    for key, expected in expected_lifecycle.items():

        if relationship_result.get(key) != expected:
            raise LearningEngineError(
                "Invalid 4.6.27F lifecycle field: "
                f"{key}"
            )

    observation_bundle = relationship_result.get(
        "semantic_pattern_observation_bundle"
    )

    relationship_bundle = relationship_result.get(
        "relationship_learning_bundle"
    )

    mutation_contract = relationship_result.get(
        "learning_scope_mutation_contract"
    )

    graph_package = relationship_result.get(
        "certified_dynamic_semantic_graph_package"
    )

    certification = relationship_result.get(
        "dynamic_semantic_graph_certification"
    )

    preservation = relationship_result.get(
        "preservation_contract"
    )

    if not isinstance(
        observation_bundle,
        dict,
    ):
        raise LearningEngineError(
            "Semantic pattern observation bundle is missing."
        )

    if (
        observation_bundle.get("schema")
        != "learning_engine_semantic_pattern_observation_bundle_v1"
    ):
        raise LearningEngineError(
            "Invalid observation bundle schema."
        )

    if not isinstance(
        relationship_bundle,
        dict,
    ):
        raise LearningEngineError(
            "Relationship learning bundle is missing."
        )

    if (
        relationship_bundle.get("schema")
        != "learning_engine_relationship_learning_bundle_v1"
    ):
        raise LearningEngineError(
            "Invalid relationship learning bundle schema."
        )

    if not isinstance(
        mutation_contract,
        dict,
    ):
        raise LearningEngineError(
            "Learning mutation contract is missing."
        )

    if (
        mutation_contract.get("schema")
        != "learning_engine_scope_mutation_contract_v1"
    ):
        raise LearningEngineError(
            "Invalid mutation contract schema."
        )

    if mutation_contract.get(
        "dynamic_semantic_graph_is_read_only"
    ) is not True:
        raise LearningEngineError(
            "Dynamic Semantic Graph must remain read-only."
        )

    if mutation_contract.get(
        "authority_is_read_only"
    ) is not True:
        raise LearningEngineError(
            "Authority must remain read-only."
        )

    if mutation_contract.get(
        "claim_integrity_is_read_only"
    ) is not True:
        raise LearningEngineError(
            "Claim Integrity must remain read-only."
        )

    if mutation_contract.get(
        "semantic_memory_is_downstream"
    ) is not True:
        raise LearningEngineError(
            "Semantic Memory ownership drift."
        )

    allowed = mutation_contract.get(
        "allowed_learning_mutations"
    )

    if not isinstance(
        allowed,
        tuple,
    ):
        raise LearningEngineError(
            "allowed_learning_mutations must be a tuple."
        )

    for permission in (
        "CREATE_LEARNED_OBJECT",
        "ATTACH_LEARNING_EVIDENCE_REFERENCE",
        "ATTACH_LEARNING_PROVENANCE_REFERENCE",
        "ATTACH_SOURCE_GRAPH_REFERENCE",
        "UPDATE_LEARNED_OBJECT_SUPPORT_STATE",
        "UPDATE_LEARNED_OBJECT_CONFIDENCE_STATE",
    ):
        if permission not in allowed:
            raise LearningEngineError(
                "Required evidence/authority integration "
                f"permission missing: {permission}"
            )

    observations = observation_bundle.get(
        "observations"
    )

    relationships = relationship_bundle.get(
        "learned_relationships"
    )

    if not isinstance(
        observations,
        list,
    ):
        raise LearningEngineError(
            "observations must be a list."
        )

    if not isinstance(
        relationships,
        list,
    ):
        raise LearningEngineError(
            "learned_relationships must be a list."
        )

    source_final_graph_id = relationship_result.get(
        "source_final_graph_id"
    )

    source_final_graph_digest = relationship_result.get(
        "source_final_graph_digest"
    )

    source_graph_snapshot_id = relationship_result.get(
        "source_graph_snapshot_id"
    )

    source_lineage_root_id = relationship_result.get(
        "source_lineage_root_id"
    )

    authority_observation_ids = []
    evidence_observation_ids = []
    authority_relationship_observation_ids = []
    evidence_relationship_observation_ids = []

    for observation in observations:

        if not isinstance(
            observation,
            dict,
        ):
            raise LearningEngineError(
                "Observation objects must be dictionaries."
            )

        if (
            observation.get("schema")
            != "learning_engine_semantic_pattern_observation_v1"
        ):
            raise LearningEngineError(
                "Invalid observation schema."
            )

        if observation.get(
            "is_learning_engine_owned"
        ) is not True:
            raise LearningEngineError(
                "Observation ownership drift."
            )

        if observation.get(
            "is_certified_fact"
        ) is not False:
            raise LearningEngineError(
                "Observation must not be a certified fact."
            )

        observation_id = observation.get(
            "observation_id"
        )

        if not isinstance(
            observation_id,
            str,
        ) or not observation_id:
            raise LearningEngineError(
                "observation_id is required."
            )

        signature = observation.get(
            "signature"
        )

        if not isinstance(
            signature,
            dict,
        ):
            raise LearningEngineError(
                "Observation signature is required."
            )

        node_type = signature.get(
            "node_type"
        )

        edge_type = signature.get(
            "edge_type"
        )

        if node_type == "AUTHORITY_NODE":
            authority_observation_ids.append(
                observation_id
            )

        if node_type == "EVIDENCE_NODE":
            evidence_observation_ids.append(
                observation_id
            )

        if isinstance(
            edge_type,
            str,
        ):
            upper_edge = edge_type.upper()

            if "AUTHORITY" in upper_edge:
                authority_relationship_observation_ids.append(
                    observation_id
                )

            if (
                "EVIDENCE" in upper_edge
                or "SUPPORT" in upper_edge
                or "CHALLENGE" in upper_edge
                or "CONTRADICT" in upper_edge
            ):
                evidence_relationship_observation_ids.append(
                    observation_id
                )

    integration_objects = []

    for relationship in relationships:

        if not isinstance(
            relationship,
            dict,
        ):
            raise LearningEngineError(
                "Learned relationships must be dictionaries."
            )

        if (
            relationship.get("schema")
            != "learning_engine_learned_relationship_v1"
        ):
            raise LearningEngineError(
                "Invalid learned relationship schema."
            )

        if relationship.get(
            "is_learning_engine_owned"
        ) is not True:
            raise LearningEngineError(
                "Learned relationship ownership drift."
            )

        if relationship.get(
            "is_certified_graph_fact"
        ) is not False:
            raise LearningEngineError(
                "Learned relationship must not be a certified fact."
            )

        if relationship.get(
            "is_learned_truth"
        ) is not False:
            raise LearningEngineError(
                "Learned relationship must not be learned truth."
            )

        learned_relationship_id = relationship.get(
            "learned_relationship_id"
        )

        if not isinstance(
            learned_relationship_id,
            str,
        ) or not learned_relationship_id:
            raise LearningEngineError(
                "learned_relationship_id is required."
            )

        source_observation_id = relationship.get(
            "source_observation_id"
        )

        related_authority = sorted(
            set(
                authority_observation_ids
                + authority_relationship_observation_ids
            )
        )

        related_evidence = sorted(
            set(
                evidence_observation_ids
                + evidence_relationship_observation_ids
            )
        )

        evidence_signal_count = len(
            related_evidence
        )

        authority_signal_count = len(
            related_authority
        )

        if (
            evidence_signal_count > 0
            and authority_signal_count > 0
        ):
            integration_state = (
                "EVIDENCE_AND_AUTHORITY_CONTEXT_AVAILABLE"
            )

            support_state = (
                "CONTEXTUALLY_SUPPORTED"
            )

            confidence_state = (
                "MODERATE"
            )

        elif evidence_signal_count > 0:
            integration_state = (
                "EVIDENCE_CONTEXT_AVAILABLE"
            )

            support_state = (
                "EVIDENCE_SUPPORTED"
            )

            confidence_state = (
                "MODERATE"
            )

        elif authority_signal_count > 0:
            integration_state = (
                "AUTHORITY_CONTEXT_AVAILABLE"
            )

            support_state = (
                "AUTHORITY_CONTEXT_ONLY"
            )

            confidence_state = (
                "LOW"
            )

        else:
            integration_state = (
                "NO_ADDITIONAL_CONTEXT"
            )

            support_state = (
                "UNCHANGED"
            )

            confidence_state = relationship.get(
                "confidence_state",
                "LOW",
            )

        payload = {
            "learned_relationship_id":
                learned_relationship_id,

            "source_observation_id":
                source_observation_id,

            "authority_observation_ids":
                related_authority,

            "evidence_observation_ids":
                related_evidence,

            "source_final_graph_id":
                source_final_graph_id,
        }

        serialized = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )

        digest = hashlib.sha256(
            serialized.encode("utf-8")
        ).hexdigest()

        integration_objects.append(
            {
                "schema":
                    "learning_engine_evidence_authority_integration_v1",

                "integration_id":
                    "evidenceauthoritylearning:v1:"
                    + digest,

                "integration_digest":
                    digest,

                "learned_relationship_id":
                    learned_relationship_id,

                "source_observation_id":
                    source_observation_id,

                "integration_state":
                    integration_state,

                "support_state":
                    support_state,

                "confidence_state":
                    confidence_state,

                "authority_signal_count":
                    authority_signal_count,

                "evidence_signal_count":
                    evidence_signal_count,

                "authority_observation_ids":
                    tuple(
                        related_authority
                    ),

                "evidence_observation_ids":
                    tuple(
                        related_evidence
                    ),

                "authority_used_as_context_only":
                    True,

                "authority_used_as_truth":
                    False,

                "evidence_used_as_context_only":
                    True,

                "claim_integrity_redecided":
                    False,

                "authority_rescored":
                    False,

                "authority_reclassified":
                    False,

                "graph_mutation_performed":
                    False,

                "semantic_memory_written":
                    False,

                "linking_decision_performed":
                    False,

                "source_final_graph_id":
                    source_final_graph_id,

                "source_final_graph_digest":
                    source_final_graph_digest,

                "source_graph_snapshot_id":
                    source_graph_snapshot_id,

                "source_lineage_root_id":
                    source_lineage_root_id,

                "is_learning_engine_owned":
                    True,

                "is_certified_fact":
                    False,

                "is_learned_truth":
                    False,
            }
        )

    integration_objects.sort(
        key=lambda x:
            x["integration_id"]
    )

    ids = [
        item["integration_id"]
        for item in integration_objects
    ]

    if len(ids) != len(set(ids)):
        raise LearningEngineError(
            "Duplicate evidence/authority integration IDs detected."
        )

    bundle_payload = {
        "source_final_graph_id":
            source_final_graph_id,

        "integration_ids":
            ids,
    }

    serialized_bundle = json.dumps(
        bundle_payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    bundle_digest = hashlib.sha256(
        serialized_bundle.encode("utf-8")
    ).hexdigest()

    integration_bundle = {
        "schema":
            "learning_engine_evidence_authority_learning_bundle_v1",

        "integration_bundle_id":
            "evidenceauthoritybundle:v1:"
            + bundle_digest,

        "integration_bundle_digest":
            bundle_digest,

        "integration_count":
            len(
                integration_objects
            ),

        "integrations":
            integration_objects,

        "authority_observation_count":
            len(
                set(
                    authority_observation_ids
                    + authority_relationship_observation_ids
                )
            ),

        "evidence_observation_count":
            len(
                set(
                    evidence_observation_ids
                    + evidence_relationship_observation_ids
                )
            ),

        "integration_policy":
            "EVIDENCE_AND_AUTHORITY_CONTEXT_WITHOUT_TRUTH_PROMOTION",
    }

    return {
        "schema":
            "learning_engine_evidence_authority_learning_result_v1",

        "learning_engine_version":
            LEARNING_ENGINE_VERSION,

        "phase":
            LEARNING_ENGINE_PHASE,

        "patch":
            "4.6.27G",

        "status":
            "EVIDENCE_AUTHORITY_LEARNING_INTEGRATION_COMPLETED",

        "source_final_graph_id":
            source_final_graph_id,

        "source_final_graph_digest":
            source_final_graph_digest,

        "source_graph_snapshot_id":
            source_graph_snapshot_id,

        "source_lineage_root_id":
            source_lineage_root_id,

        "semantic_pattern_observation_bundle":
            copy.deepcopy(
                observation_bundle
            ),

        "relationship_learning_bundle":
            copy.deepcopy(
                relationship_bundle
            ),

        "evidence_authority_learning_bundle":
            integration_bundle,

        "learning_scope_mutation_contract":
            copy.deepcopy(
                mutation_contract
            ),

        "certified_dynamic_semantic_graph_package":
            copy.deepcopy(
                graph_package
            ),

        "dynamic_semantic_graph_certification":
            copy.deepcopy(
                certification
            ),

        "preservation_contract":
            copy.deepcopy(
                preservation
            ),

        "processing_boundaries": {
            "evidence_authority_learning_integration_performed":
                True,

            "learning_performed":
                True,

            "authority_context_integrated":
                True,

            "evidence_context_integrated":
                True,

            "authority_rescored":
                False,

            "authority_reclassified":
                False,

            "claim_integrity_redecided":
                False,

            "learned_truth_created":
                False,

            "certified_fact_created":
                False,

            "graph_mutation_performed":
                False,

            "conflict_changed":
                False,

            "guard_state_changed":
                False,

            "semantic_memory_written":
                False,

            "reasoning_performed":
                False,

            "external_target_created":
                False,

            "external_target_selected":
                False,

            "linking_decisions_performed":
                False,

            "highlights_created":
                False,

            "upstream_truth_rewritten":
                False,
        },

        "policy":
            "CERTIFIED_EVIDENCE_AUTHORITY_LEARNING_INTEGRATION",

        "next":
            "conflict_exception_learning",
    }

def learn_conflicts_and_exceptions_v1(
    integration_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.27H ? Conflict / Exception Learning.

    Learns from certified conflict, contradiction, disagreement,
    exception, contested, and unresolved signals while preserving
    upstream conflict classification and certified semantic truth.
    """

    if not isinstance(
        integration_result,
        dict,
    ):
        raise LearningEngineError(
            "integration_result must be a dictionary."
        )

    expected_lifecycle = {
        "schema":
            "learning_engine_evidence_authority_learning_result_v1",

        "learning_engine_version":
            LEARNING_ENGINE_VERSION,

        "phase":
            LEARNING_ENGINE_PHASE,

        "patch":
            "4.6.27G",

        "status":
            "EVIDENCE_AUTHORITY_LEARNING_INTEGRATION_COMPLETED",

        "policy":
            "CERTIFIED_EVIDENCE_AUTHORITY_LEARNING_INTEGRATION",

        "next":
            "conflict_exception_learning",
    }

    for key, expected in expected_lifecycle.items():

        if integration_result.get(key) != expected:
            raise LearningEngineError(
                "Invalid 4.6.27G lifecycle field: "
                f"{key}"
            )

    observation_bundle = integration_result.get(
        "semantic_pattern_observation_bundle"
    )

    relationship_bundle = integration_result.get(
        "relationship_learning_bundle"
    )

    evidence_authority_bundle = integration_result.get(
        "evidence_authority_learning_bundle"
    )

    mutation_contract = integration_result.get(
        "learning_scope_mutation_contract"
    )

    graph_package = integration_result.get(
        "certified_dynamic_semantic_graph_package"
    )

    certification = integration_result.get(
        "dynamic_semantic_graph_certification"
    )

    preservation = integration_result.get(
        "preservation_contract"
    )

    if not isinstance(
        observation_bundle,
        dict,
    ):
        raise LearningEngineError(
            "Observation bundle is missing."
        )

    if (
        observation_bundle.get("schema")
        != "learning_engine_semantic_pattern_observation_bundle_v1"
    ):
        raise LearningEngineError(
            "Invalid observation bundle schema."
        )

    if not isinstance(
        relationship_bundle,
        dict,
    ):
        raise LearningEngineError(
            "Relationship bundle is missing."
        )

    if (
        relationship_bundle.get("schema")
        != "learning_engine_relationship_learning_bundle_v1"
    ):
        raise LearningEngineError(
            "Invalid relationship bundle schema."
        )

    if not isinstance(
        evidence_authority_bundle,
        dict,
    ):
        raise LearningEngineError(
            "Evidence/Authority learning bundle is missing."
        )

    if (
        evidence_authority_bundle.get("schema")
        != "learning_engine_evidence_authority_learning_bundle_v1"
    ):
        raise LearningEngineError(
            "Invalid evidence/authority bundle schema."
        )

    if not isinstance(
        mutation_contract,
        dict,
    ):
        raise LearningEngineError(
            "Learning mutation contract is missing."
        )

    if (
        mutation_contract.get("schema")
        != "learning_engine_scope_mutation_contract_v1"
    ):
        raise LearningEngineError(
            "Invalid mutation contract schema."
        )

    for flag in (
        "dynamic_semantic_graph_is_read_only",
        "claim_integrity_is_read_only",
        "authority_is_read_only",
        "conflict_classification_is_read_only",
        "guard_disposition_is_read_only",
        "semantic_memory_is_downstream",
    ):
        if mutation_contract.get(flag) is not True:
            raise LearningEngineError(
                "Required immutable learning boundary missing: "
                f"{flag}"
            )

    allowed = mutation_contract.get(
        "allowed_learning_mutations"
    )

    if not isinstance(
        allowed,
        tuple,
    ):
        raise LearningEngineError(
            "allowed_learning_mutations must be a tuple."
        )

    for permission in (
        "CREATE_LEARNED_OBJECT",
        "REGISTER_CONFLICTING_PATTERN",
        "REGISTER_EXCEPTION_PATTERN",
        "ATTACH_LEARNING_EVIDENCE_REFERENCE",
        "ATTACH_LEARNING_PROVENANCE_REFERENCE",
        "ATTACH_SOURCE_GRAPH_REFERENCE",
    ):
        if permission not in allowed:
            raise LearningEngineError(
                "Required conflict/exception learning "
                f"permission missing: {permission}"
            )

    observations = observation_bundle.get(
        "observations"
    )

    relationships = relationship_bundle.get(
        "learned_relationships"
    )

    integrations = evidence_authority_bundle.get(
        "integrations"
    )

    if not isinstance(observations, list):
        raise LearningEngineError(
            "observations must be a list."
        )

    if not isinstance(relationships, list):
        raise LearningEngineError(
            "learned_relationships must be a list."
        )

    if not isinstance(integrations, list):
        raise LearningEngineError(
            "integrations must be a list."
        )

    source_final_graph_id = integration_result.get(
        "source_final_graph_id"
    )

    source_final_graph_digest = integration_result.get(
        "source_final_graph_digest"
    )

    source_graph_snapshot_id = integration_result.get(
        "source_graph_snapshot_id"
    )

    source_lineage_root_id = integration_result.get(
        "source_lineage_root_id"
    )

    conflict_tokens = (
        "CONFLICT",
        "CONTRADICT",
        "DISAGREE",
        "CHALLENGE",
        "DISPUT",
        "CONTEST",
        "UNRESOLVED",
    )

    exception_tokens = (
        "EXCEPTION",
        "QUALIF",
        "MINORITY",
        "OUTLIER",
        "CONTEXT_DEPENDENT",
        "TEMPORAL",
        "SCOPE",
    )

    conflict_source_ids = []
    exception_source_ids = []

    for observation in observations:

        if not isinstance(observation, dict):
            raise LearningEngineError(
                "Observation objects must be dictionaries."
            )

        if (
            observation.get("schema")
            != "learning_engine_semantic_pattern_observation_v1"
        ):
            raise LearningEngineError(
                "Invalid observation schema."
            )

        if observation.get(
            "is_learning_engine_owned"
        ) is not True:
            raise LearningEngineError(
                "Observation ownership drift."
            )

        if observation.get(
            "is_certified_fact"
        ) is not False:
            raise LearningEngineError(
                "Observation cannot be a certified fact."
            )

        observation_id = observation.get(
            "observation_id"
        )

        if not isinstance(
            observation_id,
            str,
        ) or not observation_id:
            raise LearningEngineError(
                "observation_id is required."
            )

        signature = observation.get(
            "signature"
        )

        if not isinstance(signature, dict):
            raise LearningEngineError(
                "Observation signature is required."
            )

        semantic_tokens = [
            str(v).upper()
            for v in signature.values()
            if isinstance(v, str)
        ]

        combined = " ".join(
            semantic_tokens
        )

        if any(
            token in combined
            for token in conflict_tokens
        ):
            conflict_source_ids.append(
                observation_id
            )

        if any(
            token in combined
            for token in exception_tokens
        ):
            exception_source_ids.append(
                observation_id
            )

    for relationship in relationships:

        if not isinstance(
            relationship,
            dict,
        ):
            raise LearningEngineError(
                "Learned relationships must be dictionaries."
            )

        if (
            relationship.get("schema")
            != "learning_engine_learned_relationship_v1"
        ):
            raise LearningEngineError(
                "Invalid learned relationship schema."
            )

        if relationship.get(
            "is_learning_engine_owned"
        ) is not True:
            raise LearningEngineError(
                "Learned relationship ownership drift."
            )

        if relationship.get(
            "is_certified_graph_fact"
        ) is not False:
            raise LearningEngineError(
                "Learned relationship cannot be a certified graph fact."
            )

        if relationship.get(
            "is_learned_truth"
        ) is not False:
            raise LearningEngineError(
                "Learned relationship cannot be learned truth."
            )

    for integration in integrations:

        if not isinstance(
            integration,
            dict,
        ):
            raise LearningEngineError(
                "Integration objects must be dictionaries."
            )

        if (
            integration.get("schema")
            != "learning_engine_evidence_authority_integration_v1"
        ):
            raise LearningEngineError(
                "Invalid evidence/authority integration schema."
            )

        if integration.get(
            "authority_used_as_truth"
        ) is not False:
            raise LearningEngineError(
                "Authority must not be promoted to truth."
            )

    learned_objects = []

    def build_learning_object(
        learning_type: str,
        source_ids: list[str],
        learning_state: str,
    ) -> dict[str, Any]:

        canonical_ids = sorted(
            set(source_ids)
        )

        payload = {
            "learning_type":
                learning_type,

            "source_ids":
                canonical_ids,

            "source_final_graph_id":
                source_final_graph_id,
        }

        serialized = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )

        digest = hashlib.sha256(
            serialized.encode("utf-8")
        ).hexdigest()

        return {
            "schema":
                "learning_engine_conflict_exception_learning_object_v1",

            "learning_object_id":
                "conflictexceptionlearning:v1:"
                + digest,

            "learning_object_digest":
                digest,

            "learning_type":
                learning_type,

            "learning_state":
                learning_state,

            "evidence_state":
                (
                    "SUPPORTED"
                    if canonical_ids
                    else "INSUFFICIENT"
                ),

            "confidence_state":
                (
                    "MODERATE"
                    if canonical_ids
                    else "VERY_LOW"
                ),

            "source_observation_ids":
                tuple(
                    canonical_ids
                ),

            "source_observation_count":
                len(
                    canonical_ids
                ),

            "preserves_conflicting_evidence":
                True,

            "preserves_exceptions":
                True,

            "minority_patterns_preserved":
                True,

            "upstream_conflict_classification_preserved":
                True,

            "claim_integrity_redecided":
                False,

            "conflict_reclassified":
                False,

            "certified_truth_rewritten":
                False,

            "is_learning_engine_owned":
                True,

            "is_certified_fact":
                False,

            "is_learned_truth":
                False,

            "graph_mutation_performed":
                False,

            "semantic_memory_written":
                False,

            "linking_decision_performed":
                False,

            "source_final_graph_id":
                source_final_graph_id,

            "source_final_graph_digest":
                source_final_graph_digest,

            "source_graph_snapshot_id":
                source_graph_snapshot_id,

            "source_lineage_root_id":
                source_lineage_root_id,
        }

    if conflict_source_ids:
        learned_objects.append(
            build_learning_object(
                "CONFLICT_PATTERN",
                conflict_source_ids,
                "CONTESTED",
            )
        )

    if exception_source_ids:
        learned_objects.append(
            build_learning_object(
                "EXCEPTION_PATTERN",
                exception_source_ids,
                "OBSERVED",
            )
        )

    learned_objects.sort(
        key=lambda item:
            item["learning_object_id"]
    )

    object_ids = [
        item["learning_object_id"]
        for item in learned_objects
    ]

    if len(object_ids) != len(set(object_ids)):
        raise LearningEngineError(
            "Duplicate conflict/exception learning IDs detected."
        )

    bundle_payload = {
        "source_final_graph_id":
            source_final_graph_id,

        "learning_object_ids":
            object_ids,
    }

    serialized_bundle = json.dumps(
        bundle_payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    bundle_digest = hashlib.sha256(
        serialized_bundle.encode("utf-8")
    ).hexdigest()

    conflict_exception_bundle = {
        "schema":
            "learning_engine_conflict_exception_learning_bundle_v1",

        "conflict_exception_learning_bundle_id":
            "conflictexceptionbundle:v1:"
            + bundle_digest,

        "conflict_exception_learning_bundle_digest":
            bundle_digest,

        "learning_object_count":
            len(
                learned_objects
            ),

        "learning_objects":
            learned_objects,

        "conflict_source_count":
            len(
                set(
                    conflict_source_ids
                )
            ),

        "exception_source_count":
            len(
                set(
                    exception_source_ids
                )
            ),

        "conflict_exception_policy":
            "PRESERVE_CONFLICTS_EXCEPTIONS_AND_MINORITY_PATTERNS_WITHOUT_UPSTREAM_RECLASSIFICATION",
    }

    return {
        "schema":
            "learning_engine_conflict_exception_learning_result_v1",

        "learning_engine_version":
            LEARNING_ENGINE_VERSION,

        "phase":
            LEARNING_ENGINE_PHASE,

        "patch":
            "4.6.27H",

        "status":
            "CONFLICT_EXCEPTION_LEARNING_COMPLETED",

        "source_final_graph_id":
            source_final_graph_id,

        "source_final_graph_digest":
            source_final_graph_digest,

        "source_graph_snapshot_id":
            source_graph_snapshot_id,

        "source_lineage_root_id":
            source_lineage_root_id,

        "semantic_pattern_observation_bundle":
            copy.deepcopy(
                observation_bundle
            ),

        "relationship_learning_bundle":
            copy.deepcopy(
                relationship_bundle
            ),

        "evidence_authority_learning_bundle":
            copy.deepcopy(
                evidence_authority_bundle
            ),

        "conflict_exception_learning_bundle":
            conflict_exception_bundle,

        "learning_scope_mutation_contract":
            copy.deepcopy(
                mutation_contract
            ),

        "certified_dynamic_semantic_graph_package":
            copy.deepcopy(
                graph_package
            ),

        "dynamic_semantic_graph_certification":
            copy.deepcopy(
                certification
            ),

        "preservation_contract":
            copy.deepcopy(
                preservation
            ),

        "processing_boundaries": {
            "conflict_exception_learning_performed":
                True,

            "learning_performed":
                True,

            "conflicting_patterns_preserved":
                True,

            "exceptions_preserved":
                True,

            "minority_patterns_preserved":
                True,

            "conflict_reclassified":
                False,

            "claim_integrity_redecided":
                False,

            "authority_rescored":
                False,

            "learned_truth_created":
                False,

            "certified_fact_created":
                False,

            "graph_mutation_performed":
                False,

            "guard_state_changed":
                False,

            "semantic_memory_written":
                False,

            "reasoning_performed":
                False,

            "external_target_created":
                False,

            "external_target_selected":
                False,

            "linking_decisions_performed":
                False,

            "highlights_created":
                False,

            "upstream_truth_rewritten":
                False,
        },

        "policy":
            "CERTIFIED_CONFLICT_EXCEPTION_LEARNING",

        "next":
            "learning_stability_and_guard",
    }

def apply_learning_stability_and_guard_v1(
    conflict_exception_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.27I ? Learning Stability & Guard.

    Evaluates stability and downstream eligibility of Learning
    Engine-owned learned objects without changing certified upstream
    guard dispositions, graph truth, Claim Integrity, Authority,
    conflict classification, or Semantic Memory.
    """

    if not isinstance(
        conflict_exception_result,
        dict,
    ):
        raise LearningEngineError(
            "conflict_exception_result must be a dictionary."
        )

    expected_lifecycle = {
        "schema":
            "learning_engine_conflict_exception_learning_result_v1",

        "learning_engine_version":
            LEARNING_ENGINE_VERSION,

        "phase":
            LEARNING_ENGINE_PHASE,

        "patch":
            "4.6.27H",

        "status":
            "CONFLICT_EXCEPTION_LEARNING_COMPLETED",

        "policy":
            "CERTIFIED_CONFLICT_EXCEPTION_LEARNING",

        "next":
            "learning_stability_and_guard",
    }

    for key, expected in expected_lifecycle.items():

        if conflict_exception_result.get(key) != expected:
            raise LearningEngineError(
                "Invalid 4.6.27H lifecycle field: "
                f"{key}"
            )

    observation_bundle = conflict_exception_result.get(
        "semantic_pattern_observation_bundle"
    )

    relationship_bundle = conflict_exception_result.get(
        "relationship_learning_bundle"
    )

    evidence_authority_bundle = conflict_exception_result.get(
        "evidence_authority_learning_bundle"
    )

    conflict_exception_bundle = conflict_exception_result.get(
        "conflict_exception_learning_bundle"
    )

    mutation_contract = conflict_exception_result.get(
        "learning_scope_mutation_contract"
    )

    graph_package = conflict_exception_result.get(
        "certified_dynamic_semantic_graph_package"
    )

    certification = conflict_exception_result.get(
        "dynamic_semantic_graph_certification"
    )

    preservation = conflict_exception_result.get(
        "preservation_contract"
    )

    for name, value, schema in (
        (
            "observation_bundle",
            observation_bundle,
            "learning_engine_semantic_pattern_observation_bundle_v1",
        ),
        (
            "relationship_bundle",
            relationship_bundle,
            "learning_engine_relationship_learning_bundle_v1",
        ),
        (
            "evidence_authority_bundle",
            evidence_authority_bundle,
            "learning_engine_evidence_authority_learning_bundle_v1",
        ),
        (
            "conflict_exception_bundle",
            conflict_exception_bundle,
            "learning_engine_conflict_exception_learning_bundle_v1",
        ),
    ):

        if not isinstance(
            value,
            dict,
        ):
            raise LearningEngineError(
                f"{name} is missing."
            )

        if value.get("schema") != schema:
            raise LearningEngineError(
                f"Invalid {name} schema."
            )

    if not isinstance(
        mutation_contract,
        dict,
    ):
        raise LearningEngineError(
            "Learning mutation contract is missing."
        )

    if (
        mutation_contract.get("schema")
        != "learning_engine_scope_mutation_contract_v1"
    ):
        raise LearningEngineError(
            "Invalid mutation contract schema."
        )

    for flag in (
        "dynamic_semantic_graph_is_read_only",
        "claim_integrity_is_read_only",
        "authority_is_read_only",
        "conflict_classification_is_read_only",
        "guard_disposition_is_read_only",
        "semantic_memory_is_downstream",
    ):

        if mutation_contract.get(flag) is not True:
            raise LearningEngineError(
                "Required stability boundary missing: "
                f"{flag}"
            )

    allowed = mutation_contract.get(
        "allowed_learning_mutations"
    )

    if not isinstance(
        allowed,
        tuple,
    ):
        raise LearningEngineError(
            "allowed_learning_mutations must be a tuple."
        )

    for permission in (
        "UPDATE_LEARNED_OBJECT_SUPPORT_STATE",
        "UPDATE_LEARNED_OBJECT_CONFIDENCE_STATE",
        "UPDATE_LEARNED_OBJECT_STABILITY_STATE",
        "VERSION_LEARNED_OBJECT",
        "SUPERSEDE_LEARNED_OBJECT",
        "RETIRE_LEARNED_OBJECT",
        "PRESERVE_LEARNED_OBJECT_HISTORY",
    ):

        if permission not in allowed:
            raise LearningEngineError(
                "Required stability/guard permission missing: "
                f"{permission}"
            )

    relationships = relationship_bundle.get(
        "learned_relationships"
    )

    integrations = evidence_authority_bundle.get(
        "integrations"
    )

    conflict_objects = conflict_exception_bundle.get(
        "learning_objects"
    )

    if not isinstance(
        relationships,
        list,
    ):
        raise LearningEngineError(
            "learned_relationships must be a list."
        )

    if not isinstance(
        integrations,
        list,
    ):
        raise LearningEngineError(
            "integrations must be a list."
        )

    if not isinstance(
        conflict_objects,
        list,
    ):
        raise LearningEngineError(
            "learning_objects must be a list."
        )

    source_final_graph_id = conflict_exception_result.get(
        "source_final_graph_id"
    )

    source_final_graph_digest = conflict_exception_result.get(
        "source_final_graph_digest"
    )

    source_graph_snapshot_id = conflict_exception_result.get(
        "source_graph_snapshot_id"
    )

    source_lineage_root_id = conflict_exception_result.get(
        "source_lineage_root_id"
    )

    integration_by_relationship = {}

    for integration in integrations:

        if not isinstance(
            integration,
            dict,
        ):
            raise LearningEngineError(
                "Integration objects must be dictionaries."
            )

        if (
            integration.get("schema")
            != "learning_engine_evidence_authority_integration_v1"
        ):
            raise LearningEngineError(
                "Invalid integration schema."
            )

        if integration.get(
            "authority_used_as_truth"
        ) is not False:
            raise LearningEngineError(
                "Authority must not be promoted to truth."
            )

        relationship_id = integration.get(
            "learned_relationship_id"
        )

        if isinstance(
            relationship_id,
            str,
        ) and relationship_id:
            integration_by_relationship[
                relationship_id
            ] = integration

    conflict_source_ids = set()
    exception_source_ids = set()

    for obj in conflict_objects:

        if not isinstance(
            obj,
            dict,
        ):
            raise LearningEngineError(
                "Conflict/exception learning objects "
                "must be dictionaries."
            )

        if (
            obj.get("schema")
            != "learning_engine_conflict_exception_learning_object_v1"
        ):
            raise LearningEngineError(
                "Invalid conflict/exception object schema."
            )

        if obj.get(
            "is_learning_engine_owned"
        ) is not True:
            raise LearningEngineError(
                "Conflict/exception object ownership drift."
            )

        if obj.get(
            "is_certified_fact"
        ) is not False:
            raise LearningEngineError(
                "Conflict/exception object cannot be certified fact."
            )

        learning_type = obj.get(
            "learning_type"
        )

        source_ids = obj.get(
            "source_observation_ids",
            (),
        )

        if not isinstance(
            source_ids,
            tuple,
        ):
            raise LearningEngineError(
                "source_observation_ids must be a tuple."
            )

        if learning_type == "CONFLICT_PATTERN":
            conflict_source_ids.update(
                source_ids
            )

        if learning_type == "EXCEPTION_PATTERN":
            exception_source_ids.update(
                source_ids
            )

    guarded_relationships = []

    for relationship in relationships:

        if not isinstance(
            relationship,
            dict,
        ):
            raise LearningEngineError(
                "Learned relationships must be dictionaries."
            )

        if (
            relationship.get("schema")
            != "learning_engine_learned_relationship_v1"
        ):
            raise LearningEngineError(
                "Invalid learned relationship schema."
            )

        if relationship.get(
            "is_learning_engine_owned"
        ) is not True:
            raise LearningEngineError(
                "Learned relationship ownership drift."
            )

        if relationship.get(
            "is_certified_graph_fact"
        ) is not False:
            raise LearningEngineError(
                "Learned relationship cannot be certified fact."
            )

        if relationship.get(
            "is_learned_truth"
        ) is not False:
            raise LearningEngineError(
                "Learned relationship cannot be learned truth."
            )

        relationship_id = relationship.get(
            "learned_relationship_id"
        )

        source_observation_id = relationship.get(
            "source_observation_id"
        )

        occurrence_count = relationship.get(
            "occurrence_count"
        )

        evidence_state = relationship.get(
            "evidence_state"
        )

        confidence_state = relationship.get(
            "confidence_state"
        )

        if not isinstance(
            relationship_id,
            str,
        ) or not relationship_id:
            raise LearningEngineError(
                "learned_relationship_id is required."
            )

        if not isinstance(
            occurrence_count,
            int,
        ) or occurrence_count < 1:
            raise LearningEngineError(
                "occurrence_count must be a positive integer."
            )

        integration = integration_by_relationship.get(
            relationship_id
        )

        has_conflict = (
            source_observation_id
            in conflict_source_ids
        )

        has_exception = (
            source_observation_id
            in exception_source_ids
        )

        if has_conflict:
            stability_state = "CONTESTED"
            guard_disposition = "HOLD"
            downstream_eligible = False

        elif (
            evidence_state == "SUPPORTED"
            and confidence_state
            in ("HIGH", "VERY_HIGH")
            and occurrence_count >= 3
        ):
            stability_state = "STABLE"
            guard_disposition = "PASS"
            downstream_eligible = True

        elif (
            evidence_state == "SUPPORTED"
            and occurrence_count >= 2
        ):
            stability_state = "SUPPORTED"
            guard_disposition = (
                "CAUTION"
                if has_exception
                else "PASS"
            )
            downstream_eligible = True

        elif evidence_state == "CONFLICTING":
            stability_state = "CONTESTED"
            guard_disposition = "HOLD"
            downstream_eligible = False

        elif evidence_state in (
            "INSUFFICIENT",
            "UNRESOLVED",
        ):
            stability_state = "WEAKENED"
            guard_disposition = "HOLD"
            downstream_eligible = False

        else:
            stability_state = "CANDIDATE"
            guard_disposition = "CAUTION"
            downstream_eligible = True

        integration_state = (
            integration.get(
                "integration_state"
            )
            if integration
            else "NO_ADDITIONAL_CONTEXT"
        )

        payload = {
            "learned_relationship_id":
                relationship_id,

            "stability_state":
                stability_state,

            "guard_disposition":
                guard_disposition,

            "source_final_graph_id":
                source_final_graph_id,
        }

        serialized = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )

        digest = hashlib.sha256(
            serialized.encode("utf-8")
        ).hexdigest()

        guarded_relationships.append(
            {
                "schema":
                    "learning_engine_stability_guard_record_v1",

                "stability_guard_id":
                    "learningstabilityguard:v1:"
                    + digest,

                "stability_guard_digest":
                    digest,

                "learned_relationship_id":
                    relationship_id,

                "source_observation_id":
                    source_observation_id,

                "stability_state":
                    stability_state,

                "guard_disposition":
                    guard_disposition,

                "downstream_eligible":
                    downstream_eligible,

                "has_conflict_signal":
                    has_conflict,

                "has_exception_signal":
                    has_exception,

                "integration_state":
                    integration_state,

                "evidence_state":
                    evidence_state,

                "confidence_state":
                    confidence_state,

                "occurrence_count":
                    occurrence_count,

                "guard_applies_to_learning_object_only":
                    True,

                "upstream_guard_disposition_preserved":
                    True,

                "upstream_conflict_classification_preserved":
                    True,

                "claim_integrity_redecided":
                    False,

                "authority_rescored":
                    False,

                "is_learning_engine_owned":
                    True,

                "is_certified_fact":
                    False,

                "is_learned_truth":
                    False,

                "graph_mutation_performed":
                    False,

                "semantic_memory_written":
                    False,

                "linking_decision_performed":
                    False,

                "source_final_graph_id":
                    source_final_graph_id,

                "source_final_graph_digest":
                    source_final_graph_digest,

                "source_graph_snapshot_id":
                    source_graph_snapshot_id,

                "source_lineage_root_id":
                    source_lineage_root_id,
            }
        )

    guarded_relationships.sort(
        key=lambda item:
            item["stability_guard_id"]
    )

    record_ids = [
        item["stability_guard_id"]
        for item in guarded_relationships
    ]

    if len(record_ids) != len(set(record_ids)):
        raise LearningEngineError(
            "Duplicate Learning Stability & Guard IDs detected."
        )

    guard_counts = {
        "PASS":
            0,

        "CAUTION":
            0,

        "HOLD":
            0,

        "BLOCK":
            0,
    }

    stability_counts = {
        "CANDIDATE":
            0,

        "SUPPORTED":
            0,

        "STABLE":
            0,

        "CONTESTED":
            0,

        "WEAKENED":
            0,

        "SUPERSEDED":
            0,

        "RETIRED":
            0,

        "BLOCKED":
            0,
    }

    for item in guarded_relationships:

        guard_counts[
            item["guard_disposition"]
        ] = (
            guard_counts.get(
                item["guard_disposition"],
                0,
            )
            + 1
        )

        stability_counts[
            item["stability_state"]
        ] = (
            stability_counts.get(
                item["stability_state"],
                0,
            )
            + 1
        )

    bundle_payload = {
        "source_final_graph_id":
            source_final_graph_id,

        "stability_guard_ids":
            record_ids,
    }

    serialized_bundle = json.dumps(
        bundle_payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    bundle_digest = hashlib.sha256(
        serialized_bundle.encode("utf-8")
    ).hexdigest()

    stability_guard_bundle = {
        "schema":
            "learning_engine_stability_guard_bundle_v1",

        "stability_guard_bundle_id":
            "learningstabilityguardbundle:v1:"
            + bundle_digest,

        "stability_guard_bundle_digest":
            bundle_digest,

        "record_count":
            len(
                guarded_relationships
            ),

        "records":
            guarded_relationships,

        "guard_counts":
            guard_counts,

        "stability_counts":
            stability_counts,

        "stability_guard_policy":
            "LEARNING_OBJECT_STABILITY_AND_GUARD_WITHOUT_UPSTREAM_GUARD_MUTATION",
    }

    return {
        "schema":
            "learning_engine_stability_guard_result_v1",

        "learning_engine_version":
            LEARNING_ENGINE_VERSION,

        "phase":
            LEARNING_ENGINE_PHASE,

        "patch":
            "4.6.27I",

        "status":
            "LEARNING_STABILITY_AND_GUARD_COMPLETED",

        "source_final_graph_id":
            source_final_graph_id,

        "source_final_graph_digest":
            source_final_graph_digest,

        "source_graph_snapshot_id":
            source_graph_snapshot_id,

        "source_lineage_root_id":
            source_lineage_root_id,

        "semantic_pattern_observation_bundle":
            copy.deepcopy(
                observation_bundle
            ),

        "relationship_learning_bundle":
            copy.deepcopy(
                relationship_bundle
            ),

        "evidence_authority_learning_bundle":
            copy.deepcopy(
                evidence_authority_bundle
            ),

        "conflict_exception_learning_bundle":
            copy.deepcopy(
                conflict_exception_bundle
            ),

        "learning_stability_guard_bundle":
            stability_guard_bundle,

        "learning_scope_mutation_contract":
            copy.deepcopy(
                mutation_contract
            ),

        "certified_dynamic_semantic_graph_package":
            copy.deepcopy(
                graph_package
            ),

        "dynamic_semantic_graph_certification":
            copy.deepcopy(
                certification
            ),

        "preservation_contract":
            copy.deepcopy(
                preservation
            ),

        "processing_boundaries": {
            "learning_stability_guard_performed":
                True,

            "learning_performed":
                True,

            "learning_object_guard_created":
                True,

            "upstream_guard_disposition_changed":
                False,

            "conflict_reclassified":
                False,

            "claim_integrity_redecided":
                False,

            "authority_rescored":
                False,

            "learned_truth_created":
                False,

            "certified_fact_created":
                False,

            "graph_mutation_performed":
                False,

            "semantic_memory_written":
                False,

            "reasoning_performed":
                False,

            "external_target_created":
                False,

            "external_target_selected":
                False,

            "linking_decisions_performed":
                False,

            "highlights_created":
                False,

            "upstream_truth_rewritten":
                False,
        },

        "policy":
            "CERTIFIED_LEARNING_STABILITY_AND_GUARD",

        "next":
            "learning_provenance_and_lineage",
    }

def build_learning_provenance_and_lineage_v1(
    stability_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.27J ? Learning Provenance & Lineage.

    Builds deterministic provenance and lineage records for
    Learning Engine-owned learned objects while preserving
    certified upstream graph provenance and lineage as read-only.
    """

    if not isinstance(
        stability_result,
        dict,
    ):
        raise LearningEngineError(
            "stability_result must be a dictionary."
        )

    expected_lifecycle = {
        "schema":
            "learning_engine_stability_guard_result_v1",

        "learning_engine_version":
            LEARNING_ENGINE_VERSION,

        "phase":
            LEARNING_ENGINE_PHASE,

        "patch":
            "4.6.27I",

        "status":
            "LEARNING_STABILITY_AND_GUARD_COMPLETED",

        "policy":
            "CERTIFIED_LEARNING_STABILITY_AND_GUARD",

        "next":
            "learning_provenance_and_lineage",
    }

    for key, expected in expected_lifecycle.items():

        if stability_result.get(key) != expected:
            raise LearningEngineError(
                "Invalid 4.6.27I lifecycle field: "
                f"{key}"
            )

    observation_bundle = stability_result.get(
        "semantic_pattern_observation_bundle"
    )

    relationship_bundle = stability_result.get(
        "relationship_learning_bundle"
    )

    evidence_authority_bundle = stability_result.get(
        "evidence_authority_learning_bundle"
    )

    conflict_exception_bundle = stability_result.get(
        "conflict_exception_learning_bundle"
    )

    stability_guard_bundle = stability_result.get(
        "learning_stability_guard_bundle"
    )

    mutation_contract = stability_result.get(
        "learning_scope_mutation_contract"
    )

    graph_package = stability_result.get(
        "certified_dynamic_semantic_graph_package"
    )

    certification = stability_result.get(
        "dynamic_semantic_graph_certification"
    )

    preservation = stability_result.get(
        "preservation_contract"
    )

    required_bundles = (
        (
            observation_bundle,
            "learning_engine_semantic_pattern_observation_bundle_v1",
        ),
        (
            relationship_bundle,
            "learning_engine_relationship_learning_bundle_v1",
        ),
        (
            evidence_authority_bundle,
            "learning_engine_evidence_authority_learning_bundle_v1",
        ),
        (
            conflict_exception_bundle,
            "learning_engine_conflict_exception_learning_bundle_v1",
        ),
        (
            stability_guard_bundle,
            "learning_engine_stability_guard_bundle_v1",
        ),
    )

    for bundle, schema in required_bundles:

        if not isinstance(bundle, dict):
            raise LearningEngineError(
                "Required Learning Engine bundle is missing."
            )

        if bundle.get("schema") != schema:
            raise LearningEngineError(
                "Invalid Learning Engine bundle schema: "
                f"{schema}"
            )

    if not isinstance(
        mutation_contract,
        dict,
    ):
        raise LearningEngineError(
            "Learning mutation contract is missing."
        )

    if (
        mutation_contract.get("schema")
        != "learning_engine_scope_mutation_contract_v1"
    ):
        raise LearningEngineError(
            "Invalid mutation contract schema."
        )

    for flag in (
        "dynamic_semantic_graph_is_read_only",
        "claim_integrity_is_read_only",
        "authority_is_read_only",
        "conflict_classification_is_read_only",
        "guard_disposition_is_read_only",
        "semantic_memory_is_downstream",
    ):
        if mutation_contract.get(flag) is not True:
            raise LearningEngineError(
                "Required provenance boundary missing: "
                f"{flag}"
            )

    allowed = mutation_contract.get(
        "allowed_learning_mutations"
    )

    if not isinstance(
        allowed,
        tuple,
    ):
        raise LearningEngineError(
            "allowed_learning_mutations must be a tuple."
        )

    for permission in (
        "ATTACH_LEARNING_PROVENANCE_REFERENCE",
        "ATTACH_SOURCE_GRAPH_REFERENCE",
        "ATTACH_SOURCE_LINEAGE_REFERENCE",
        "PRESERVE_LEARNED_OBJECT_HISTORY",
    ):
        if permission not in allowed:
            raise LearningEngineError(
                "Required provenance/lineage permission missing: "
                f"{permission}"
            )

    source_final_graph_id = stability_result.get(
        "source_final_graph_id"
    )

    source_final_graph_digest = stability_result.get(
        "source_final_graph_digest"
    )

    source_graph_snapshot_id = stability_result.get(
        "source_graph_snapshot_id"
    )

    source_lineage_root_id = stability_result.get(
        "source_lineage_root_id"
    )

    for name, value in (
        (
            "source_final_graph_id",
            source_final_graph_id,
        ),
        (
            "source_final_graph_digest",
            source_final_graph_digest,
        ),
        (
            "source_graph_snapshot_id",
            source_graph_snapshot_id,
        ),
        (
            "source_lineage_root_id",
            source_lineage_root_id,
        ),
    ):
        if not isinstance(value, str) or not value:
            raise LearningEngineError(
                f"{name} is required."
            )

    observations = observation_bundle.get(
        "observations"
    )

    relationships = relationship_bundle.get(
        "learned_relationships"
    )

    integrations = evidence_authority_bundle.get(
        "integrations"
    )

    conflict_objects = conflict_exception_bundle.get(
        "learning_objects"
    )

    guard_records = stability_guard_bundle.get(
        "records"
    )

    for name, value in (
        ("observations", observations),
        ("relationships", relationships),
        ("integrations", integrations),
        ("conflict_objects", conflict_objects),
        ("guard_records", guard_records),
    ):
        if not isinstance(value, list):
            raise LearningEngineError(
                f"{name} must be a list."
            )

    observation_ids = set()

    for observation in observations:

        if not isinstance(observation, dict):
            raise LearningEngineError(
                "Observation objects must be dictionaries."
            )

        if (
            observation.get("schema")
            != "learning_engine_semantic_pattern_observation_v1"
        ):
            raise LearningEngineError(
                "Invalid observation schema."
            )

        observation_id = observation.get(
            "observation_id"
        )

        if not isinstance(
            observation_id,
            str,
        ) or not observation_id:
            raise LearningEngineError(
                "observation_id is required."
            )

        observation_ids.add(
            observation_id
        )

    relationship_ids = set()

    for relationship in relationships:

        if not isinstance(relationship, dict):
            raise LearningEngineError(
                "Learned relationships must be dictionaries."
            )

        if (
            relationship.get("schema")
            != "learning_engine_learned_relationship_v1"
        ):
            raise LearningEngineError(
                "Invalid learned relationship schema."
            )

        if relationship.get(
            "is_learning_engine_owned"
        ) is not True:
            raise LearningEngineError(
                "Learned relationship ownership drift."
            )

        if relationship.get(
            "is_certified_graph_fact"
        ) is not False:
            raise LearningEngineError(
                "Learned relationship cannot be certified graph fact."
            )

        if relationship.get(
            "is_learned_truth"
        ) is not False:
            raise LearningEngineError(
                "Learned relationship cannot be learned truth."
            )

        relationship_id = relationship.get(
            "learned_relationship_id"
        )

        source_observation_id = relationship.get(
            "source_observation_id"
        )

        if not isinstance(
            relationship_id,
            str,
        ) or not relationship_id:
            raise LearningEngineError(
                "learned_relationship_id is required."
            )

        if (
            source_observation_id
            not in observation_ids
        ):
            raise LearningEngineError(
                "Learned relationship references "
                "unknown observation."
            )

        relationship_ids.add(
            relationship_id
        )

    integration_ids = set()

    for integration in integrations:

        if not isinstance(integration, dict):
            raise LearningEngineError(
                "Integration objects must be dictionaries."
            )

        if (
            integration.get("schema")
            != "learning_engine_evidence_authority_integration_v1"
        ):
            raise LearningEngineError(
                "Invalid integration schema."
            )

        integration_id = integration.get(
            "integration_id"
        )

        relationship_id = integration.get(
            "learned_relationship_id"
        )

        if not isinstance(
            integration_id,
            str,
        ) or not integration_id:
            raise LearningEngineError(
                "integration_id is required."
            )

        if relationship_id not in relationship_ids:
            raise LearningEngineError(
                "Integration references unknown "
                "learned relationship."
            )

        integration_ids.add(
            integration_id
        )

    conflict_object_ids = set()

    for obj in conflict_objects:

        if not isinstance(obj, dict):
            raise LearningEngineError(
                "Conflict/exception objects must be dictionaries."
            )

        if (
            obj.get("schema")
            != "learning_engine_conflict_exception_learning_object_v1"
        ):
            raise LearningEngineError(
                "Invalid conflict/exception object schema."
            )

        object_id = obj.get(
            "learning_object_id"
        )

        source_ids = obj.get(
            "source_observation_ids",
            (),
        )

        if not isinstance(
            object_id,
            str,
        ) or not object_id:
            raise LearningEngineError(
                "learning_object_id is required."
            )

        if not isinstance(
            source_ids,
            tuple,
        ):
            raise LearningEngineError(
                "source_observation_ids must be a tuple."
            )

        for source_id in source_ids:

            if source_id not in observation_ids:
                raise LearningEngineError(
                    "Conflict/exception object references "
                    "unknown observation."
                )

        conflict_object_ids.add(
            object_id
        )

    guard_record_ids = set()

    for record in guard_records:

        if not isinstance(record, dict):
            raise LearningEngineError(
                "Guard records must be dictionaries."
            )

        if (
            record.get("schema")
            != "learning_engine_stability_guard_record_v1"
        ):
            raise LearningEngineError(
                "Invalid stability guard record schema."
            )

        guard_id = record.get(
            "stability_guard_id"
        )

        relationship_id = record.get(
            "learned_relationship_id"
        )

        if not isinstance(
            guard_id,
            str,
        ) or not guard_id:
            raise LearningEngineError(
                "stability_guard_id is required."
            )

        if relationship_id not in relationship_ids:
            raise LearningEngineError(
                "Guard record references unknown "
                "learned relationship."
            )

        guard_record_ids.add(
            guard_id
        )

    lineage_records = []

    integration_by_relationship = {
        item.get("learned_relationship_id"):
            item
        for item in integrations
    }

    guard_by_relationship = {
        item.get("learned_relationship_id"):
            item
        for item in guard_records
    }

    conflict_by_observation = {}

    for obj in conflict_objects:

        for source_id in obj.get(
            "source_observation_ids",
            (),
        ):
            conflict_by_observation.setdefault(
                source_id,
                [],
            ).append(
                obj["learning_object_id"]
            )

    for relationship in relationships:

        relationship_id = relationship[
            "learned_relationship_id"
        ]

        observation_id = relationship[
            "source_observation_id"
        ]

        integration = integration_by_relationship.get(
            relationship_id
        )

        guard_record = guard_by_relationship.get(
            relationship_id
        )

        conflict_ids = sorted(
            conflict_by_observation.get(
                observation_id,
                [],
            )
        )

        payload = {
            "learned_relationship_id":
                relationship_id,

            "source_observation_id":
                observation_id,

            "integration_id":
                (
                    integration.get("integration_id")
                    if integration
                    else None
                ),

            "stability_guard_id":
                (
                    guard_record.get(
                        "stability_guard_id"
                    )
                    if guard_record
                    else None
                ),

            "conflict_exception_object_ids":
                conflict_ids,

            "source_final_graph_id":
                source_final_graph_id,

            "source_graph_snapshot_id":
                source_graph_snapshot_id,

            "source_lineage_root_id":
                source_lineage_root_id,
        }

        serialized = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )

        digest = hashlib.sha256(
            serialized.encode("utf-8")
        ).hexdigest()

        lineage_records.append(
            {
                "schema":
                    "learning_engine_provenance_lineage_record_v1",

                "learning_lineage_id":
                    "learninglineage:v1:"
                    + digest,

                "learning_lineage_digest":
                    digest,

                "learned_relationship_id":
                    relationship_id,

                "source_observation_id":
                    observation_id,

                "integration_id":
                    (
                        integration.get(
                            "integration_id"
                        )
                        if integration
                        else None
                    ),

                "stability_guard_id":
                    (
                        guard_record.get(
                            "stability_guard_id"
                        )
                        if guard_record
                        else None
                    ),

                "conflict_exception_object_ids":
                    tuple(
                        conflict_ids
                    ),

                "source_final_graph_id":
                    source_final_graph_id,

                "source_final_graph_digest":
                    source_final_graph_digest,

                "source_graph_snapshot_id":
                    source_graph_snapshot_id,

                "source_lineage_root_id":
                    source_lineage_root_id,

                "graph_provenance_preserved":
                    True,

                "graph_lineage_preserved":
                    True,

                "learning_provenance_complete":
                    True,

                "learning_lineage_complete":
                    True,

                "upstream_provenance_rewritten":
                    False,

                "upstream_lineage_rewritten":
                    False,

                "is_learning_engine_owned":
                    True,

                "is_certified_fact":
                    False,

                "is_learned_truth":
                    False,

                "semantic_memory_written":
                    False,

                "graph_mutation_performed":
                    False,

                "linking_decision_performed":
                    False,
            }
        )

    lineage_records.sort(
        key=lambda item:
            item["learning_lineage_id"]
    )

    lineage_ids = [
        item["learning_lineage_id"]
        for item in lineage_records
    ]

    if len(lineage_ids) != len(set(lineage_ids)):
        raise LearningEngineError(
            "Duplicate Learning Provenance & Lineage IDs detected."
        )

    root_payload = {
        "source_final_graph_id":
            source_final_graph_id,

        "source_graph_snapshot_id":
            source_graph_snapshot_id,

        "source_lineage_root_id":
            source_lineage_root_id,

        "learning_lineage_ids":
            lineage_ids,
    }

    root_serialized = json.dumps(
        root_payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    root_digest = hashlib.sha256(
        root_serialized.encode("utf-8")
    ).hexdigest()

    learning_lineage_root_id = (
        "learninglineageroot:v1:"
        + root_digest
    )

    provenance_bundle = {
        "schema":
            "learning_engine_provenance_lineage_bundle_v1",

        "learning_lineage_root_id":
            learning_lineage_root_id,

        "learning_lineage_root_digest":
            root_digest,

        "record_count":
            len(
                lineage_records
            ),

        "records":
            lineage_records,

        "source_observation_count":
            len(
                observation_ids
            ),

        "source_relationship_count":
            len(
                relationship_ids
            ),

        "source_integration_count":
            len(
                integration_ids
            ),

        "source_conflict_exception_count":
            len(
                conflict_object_ids
            ),

        "source_guard_record_count":
            len(
                guard_record_ids
            ),

        "provenance_lineage_policy":
            "DETERMINISTIC_END_TO_END_LEARNING_LINEAGE_WITH_READ_ONLY_UPSTREAM_PROVENANCE",
    }

    return {
        "schema":
            "learning_engine_provenance_lineage_result_v1",

        "learning_engine_version":
            LEARNING_ENGINE_VERSION,

        "phase":
            LEARNING_ENGINE_PHASE,

        "patch":
            "4.6.27J",

        "status":
            "LEARNING_PROVENANCE_AND_LINEAGE_COMPLETED",

        "source_final_graph_id":
            source_final_graph_id,

        "source_final_graph_digest":
            source_final_graph_digest,

        "source_graph_snapshot_id":
            source_graph_snapshot_id,

        "source_lineage_root_id":
            source_lineage_root_id,

        "learning_lineage_root_id":
            learning_lineage_root_id,

        "semantic_pattern_observation_bundle":
            copy.deepcopy(
                observation_bundle
            ),

        "relationship_learning_bundle":
            copy.deepcopy(
                relationship_bundle
            ),

        "evidence_authority_learning_bundle":
            copy.deepcopy(
                evidence_authority_bundle
            ),

        "conflict_exception_learning_bundle":
            copy.deepcopy(
                conflict_exception_bundle
            ),

        "learning_stability_guard_bundle":
            copy.deepcopy(
                stability_guard_bundle
            ),

        "learning_provenance_lineage_bundle":
            provenance_bundle,

        "learning_scope_mutation_contract":
            copy.deepcopy(
                mutation_contract
            ),

        "certified_dynamic_semantic_graph_package":
            copy.deepcopy(
                graph_package
            ),

        "dynamic_semantic_graph_certification":
            copy.deepcopy(
                certification
            ),

        "preservation_contract":
            copy.deepcopy(
                preservation
            ),

        "processing_boundaries": {
            "learning_provenance_lineage_performed":
                True,

            "learning_performed":
                True,

            "learning_lineage_created":
                True,

            "graph_provenance_preserved":
                True,

            "graph_lineage_preserved":
                True,

            "upstream_provenance_rewritten":
                False,

            "upstream_lineage_rewritten":
                False,

            "claim_integrity_redecided":
                False,

            "authority_rescored":
                False,

            "conflict_reclassified":
                False,

            "upstream_guard_disposition_changed":
                False,

            "learned_truth_created":
                False,

            "certified_fact_created":
                False,

            "graph_mutation_performed":
                False,

            "semantic_memory_written":
                False,

            "reasoning_performed":
                False,

            "external_target_created":
                False,

            "external_target_selected":
                False,

            "linking_decisions_performed":
                False,

            "highlights_created":
                False,

            "upstream_truth_rewritten":
                False,
        },

        "policy":
            "CERTIFIED_LEARNING_PROVENANCE_AND_LINEAGE",

        "next":
            "final_learning_engine_result",
    }

def build_final_learning_engine_result_v1(
    provenance_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.27K ? Final Learning Engine Result.

    Packages all certified Learning Engine outputs into the final
    deterministic learned-knowledge artifact for downstream
    Semantic Memory consumption without writing Semantic Memory.
    """

    if not isinstance(
        provenance_result,
        dict,
    ):
        raise LearningEngineError(
            "provenance_result must be a dictionary."
        )

    expected_lifecycle = {
        "schema":
            "learning_engine_provenance_lineage_result_v1",

        "learning_engine_version":
            LEARNING_ENGINE_VERSION,

        "phase":
            LEARNING_ENGINE_PHASE,

        "patch":
            "4.6.27J",

        "status":
            "LEARNING_PROVENANCE_AND_LINEAGE_COMPLETED",

        "policy":
            "CERTIFIED_LEARNING_PROVENANCE_AND_LINEAGE",

        "next":
            "final_learning_engine_result",
    }

    for key, expected in expected_lifecycle.items():

        if provenance_result.get(key) != expected:
            raise LearningEngineError(
                "Invalid 4.6.27J lifecycle field: "
                f"{key}"
            )

    observation_bundle = provenance_result.get(
        "semantic_pattern_observation_bundle"
    )

    relationship_bundle = provenance_result.get(
        "relationship_learning_bundle"
    )

    evidence_authority_bundle = provenance_result.get(
        "evidence_authority_learning_bundle"
    )

    conflict_exception_bundle = provenance_result.get(
        "conflict_exception_learning_bundle"
    )

    stability_guard_bundle = provenance_result.get(
        "learning_stability_guard_bundle"
    )

    provenance_lineage_bundle = provenance_result.get(
        "learning_provenance_lineage_bundle"
    )

    mutation_contract = provenance_result.get(
        "learning_scope_mutation_contract"
    )

    graph_package = provenance_result.get(
        "certified_dynamic_semantic_graph_package"
    )

    graph_certification = provenance_result.get(
        "dynamic_semantic_graph_certification"
    )

    preservation = provenance_result.get(
        "preservation_contract"
    )

    required = (
        (
            observation_bundle,
            "learning_engine_semantic_pattern_observation_bundle_v1",
        ),
        (
            relationship_bundle,
            "learning_engine_relationship_learning_bundle_v1",
        ),
        (
            evidence_authority_bundle,
            "learning_engine_evidence_authority_learning_bundle_v1",
        ),
        (
            conflict_exception_bundle,
            "learning_engine_conflict_exception_learning_bundle_v1",
        ),
        (
            stability_guard_bundle,
            "learning_engine_stability_guard_bundle_v1",
        ),
        (
            provenance_lineage_bundle,
            "learning_engine_provenance_lineage_bundle_v1",
        ),
    )

    for bundle, expected_schema in required:

        if not isinstance(bundle, dict):
            raise LearningEngineError(
                "Required Learning Engine bundle is missing."
            )

        if bundle.get("schema") != expected_schema:
            raise LearningEngineError(
                "Invalid bundle schema: "
                f"{expected_schema}"
            )

    if not isinstance(
        mutation_contract,
        dict,
    ):
        raise LearningEngineError(
            "Learning mutation contract is missing."
        )

    if (
        mutation_contract.get("schema")
        != "learning_engine_scope_mutation_contract_v1"
    ):
        raise LearningEngineError(
            "Invalid mutation contract schema."
        )

    for flag in (
        "dynamic_semantic_graph_is_read_only",
        "claim_integrity_is_read_only",
        "authority_is_read_only",
        "conflict_classification_is_read_only",
        "guard_disposition_is_read_only",
        "semantic_memory_is_downstream",
    ):
        if mutation_contract.get(flag) is not True:
            raise LearningEngineError(
                "Required final-result boundary missing: "
                f"{flag}"
            )

    source_final_graph_id = provenance_result.get(
        "source_final_graph_id"
    )

    source_final_graph_digest = provenance_result.get(
        "source_final_graph_digest"
    )

    source_graph_snapshot_id = provenance_result.get(
        "source_graph_snapshot_id"
    )

    source_lineage_root_id = provenance_result.get(
        "source_lineage_root_id"
    )

    learning_lineage_root_id = provenance_result.get(
        "learning_lineage_root_id"
    )

    for name, value in (
        (
            "source_final_graph_id",
            source_final_graph_id,
        ),
        (
            "source_final_graph_digest",
            source_final_graph_digest,
        ),
        (
            "source_graph_snapshot_id",
            source_graph_snapshot_id,
        ),
        (
            "source_lineage_root_id",
            source_lineage_root_id,
        ),
        (
            "learning_lineage_root_id",
            learning_lineage_root_id,
        ),
    ):
        if not isinstance(value, str) or not value:
            raise LearningEngineError(
                f"{name} is required."
            )

    observations = observation_bundle.get(
        "observations",
        [],
    )

    relationships = relationship_bundle.get(
        "learned_relationships",
        [],
    )

    integrations = evidence_authority_bundle.get(
        "integrations",
        [],
    )

    conflict_objects = conflict_exception_bundle.get(
        "learning_objects",
        [],
    )

    guard_records = stability_guard_bundle.get(
        "records",
        [],
    )

    lineage_records = provenance_lineage_bundle.get(
        "records",
        [],
    )

    for name, value in (
        ("observations", observations),
        ("relationships", relationships),
        ("integrations", integrations),
        ("conflict_objects", conflict_objects),
        ("guard_records", guard_records),
        ("lineage_records", lineage_records),
    ):
        if not isinstance(value, list):
            raise LearningEngineError(
                f"{name} must be a list."
            )

    downstream_eligible_ids = sorted(
        {
            record.get(
                "learned_relationship_id"
            )
            for record in guard_records
            if (
                isinstance(record, dict)
                and record.get(
                    "downstream_eligible"
                )
                is True
                and isinstance(
                    record.get(
                        "learned_relationship_id"
                    ),
                    str,
                )
            )
        }
    )

    held_ids = sorted(
        {
            record.get(
                "learned_relationship_id"
            )
            for record in guard_records
            if (
                isinstance(record, dict)
                and record.get(
                    "guard_disposition"
                )
                == "HOLD"
                and isinstance(
                    record.get(
                        "learned_relationship_id"
                    ),
                    str,
                )
            )
        }
    )

    blocked_ids = sorted(
        {
            record.get(
                "learned_relationship_id"
            )
            for record in guard_records
            if (
                isinstance(record, dict)
                and record.get(
                    "guard_disposition"
                )
                == "BLOCK"
                and isinstance(
                    record.get(
                        "learned_relationship_id"
                    ),
                    str,
                )
            )
        }
    )

    final_payload = {
        "source_final_graph_id":
            source_final_graph_id,

        "source_final_graph_digest":
            source_final_graph_digest,

        "learning_lineage_root_id":
            learning_lineage_root_id,

        "observation_count":
            len(observations),

        "relationship_count":
            len(relationships),

        "integration_count":
            len(integrations),

        "conflict_exception_count":
            len(conflict_objects),

        "guard_record_count":
            len(guard_records),

        "lineage_record_count":
            len(lineage_records),

        "downstream_eligible_relationship_ids":
            downstream_eligible_ids,

        "held_relationship_ids":
            held_ids,

        "blocked_relationship_ids":
            blocked_ids,
    }

    serialized = json.dumps(
        final_payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    digest = hashlib.sha256(
        serialized.encode("utf-8")
    ).hexdigest()

    final_package = {
        "schema":
            "final_learning_engine_package_v1",

        "final_learning_engine_package_id":
            "finallearningengine:v1:"
            + digest,

        "final_learning_engine_package_digest":
            digest,

        "source_final_graph_id":
            source_final_graph_id,

        "source_final_graph_digest":
            source_final_graph_digest,

        "source_graph_snapshot_id":
            source_graph_snapshot_id,

        "source_lineage_root_id":
            source_lineage_root_id,

        "learning_lineage_root_id":
            learning_lineage_root_id,

        "semantic_pattern_observation_bundle":
            copy.deepcopy(
                observation_bundle
            ),

        "relationship_learning_bundle":
            copy.deepcopy(
                relationship_bundle
            ),

        "evidence_authority_learning_bundle":
            copy.deepcopy(
                evidence_authority_bundle
            ),

        "conflict_exception_learning_bundle":
            copy.deepcopy(
                conflict_exception_bundle
            ),

        "learning_stability_guard_bundle":
            copy.deepcopy(
                stability_guard_bundle
            ),

        "learning_provenance_lineage_bundle":
            copy.deepcopy(
                provenance_lineage_bundle
            ),

        "downstream_eligible_relationship_ids":
            tuple(
                downstream_eligible_ids
            ),

        "held_relationship_ids":
            tuple(
                held_ids
            ),

        "blocked_relationship_ids":
            tuple(
                blocked_ids
            ),

        "learning_engine_output_is_certified_fact":
            False,

        "learning_engine_output_is_learned_truth":
            False,

        "semantic_memory_write_performed":
            False,

        "graph_mutation_performed":
            False,

        "linking_decision_performed":
            False,

        "final_policy":
            "CERTIFIED_LEARNING_ENGINE_OUTPUT_FOR_SEMANTIC_MEMORY_HANDOFF",
    }

    return {
        "schema":
            "final_learning_engine_result_v1",

        "learning_engine_version":
            LEARNING_ENGINE_VERSION,

        "phase":
            LEARNING_ENGINE_PHASE,

        "patch":
            "4.6.27K",

        "status":
            "FINAL_LEARNING_ENGINE_RESULT_BUILT",

        "source_final_graph_id":
            source_final_graph_id,

        "source_final_graph_digest":
            source_final_graph_digest,

        "source_graph_snapshot_id":
            source_graph_snapshot_id,

        "source_lineage_root_id":
            source_lineage_root_id,

        "learning_lineage_root_id":
            learning_lineage_root_id,

        "final_learning_engine_package":
            final_package,

        "learning_scope_mutation_contract":
            copy.deepcopy(
                mutation_contract
            ),

        "certified_dynamic_semantic_graph_package":
            copy.deepcopy(
                graph_package
            ),

        "dynamic_semantic_graph_certification":
            copy.deepcopy(
                graph_certification
            ),

        "preservation_contract":
            copy.deepcopy(
                preservation
            ),

        "processing_boundaries": {
            "final_learning_engine_result_built":
                True,

            "learning_performed":
                True,

            "learning_output_packaged":
                True,

            "semantic_memory_handoff_ready":
                True,

            "semantic_memory_written":
                False,

            "graph_mutation_performed":
                False,

            "claim_integrity_redecided":
                False,

            "authority_rescored":
                False,

            "conflict_reclassified":
                False,

            "upstream_guard_disposition_changed":
                False,

            "learned_truth_created":
                False,

            "certified_fact_created":
                False,

            "reasoning_performed":
                False,

            "external_target_created":
                False,

            "external_target_selected":
                False,

            "linking_decisions_performed":
                False,

            "highlights_created":
                False,

            "upstream_truth_rewritten":
                False,
        },

        "policy":
            "CERTIFIED_FINAL_LEARNING_ENGINE_RESULT",

        "next":
            "full_learning_engine_hard_certification",
    }

def certify_full_learning_engine_v1(
    scope_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.27L ? Full Learning Engine Hard Certification.

    Executes and certifies the complete operational Learning Engine
    chain from the certified 4.6.27D scope/mutation contract through
    the final 4.6.27K learned-knowledge package.

    Certification proves:
    - deterministic E -> K execution,
    - exact lifecycle handoffs,
    - preservation of upstream certified semantic state,
    - no graph mutation,
    - no Semantic Memory write,
    - no target ownership/selection drift,
    - no linking/highlighting side effects,
    - learned output is not promoted to certified truth,
    - final package is ready only for downstream Semantic Memory
      handoff.
    """

    if not isinstance(
        scope_result,
        dict,
    ):
        raise LearningEngineError(
            "scope_result must be a dictionary."
        )

    expected_d = {
        "schema":
            "learning_engine_scope_mutation_contract_result_v1",

        "learning_engine_version":
            LEARNING_ENGINE_VERSION,

        "phase":
            LEARNING_ENGINE_PHASE,

        "patch":
            "4.6.27D",

        "status":
            "LEARNING_SCOPE_AND_MUTATION_CONTRACT_DEFINED",

        "policy":
            "CERTIFIED_LEARNING_SCOPE_AND_MUTATION_CONTRACT",

        "next":
            "semantic_pattern_observation",
    }

    for key, expected in expected_d.items():

        if scope_result.get(key) != expected:
            raise LearningEngineError(
                "Invalid 4.6.27D certification input field: "
                f"{key}"
            )

    before = copy.deepcopy(
        scope_result
    )

    result_e = observe_semantic_patterns_v1(
        scope_result
    )

    result_f = learn_semantic_relationships_v1(
        result_e
    )

    result_g = integrate_evidence_authority_learning_v1(
        result_f
    )

    result_h = learn_conflicts_and_exceptions_v1(
        result_g
    )

    result_i = apply_learning_stability_and_guard_v1(
        result_h
    )

    result_j = build_learning_provenance_and_lineage_v1(
        result_i
    )

    result_k = build_final_learning_engine_result_v1(
        result_j
    )

    final_package = result_k.get(
        "final_learning_engine_package"
    )

    if not isinstance(
        final_package,
        dict,
    ):
        raise LearningEngineError(
            "Final Learning Engine package is missing."
        )

    required_stage_lifecycle = (
        (
            result_e,
            "learning_engine_semantic_pattern_observation_result_v1",
            "4.6.27E",
            "SEMANTIC_PATTERN_OBSERVATION_COMPLETED",
            "CERTIFIED_SEMANTIC_PATTERN_OBSERVATION",
            "relationship_learning",
        ),
        (
            result_f,
            "learning_engine_relationship_learning_result_v1",
            "4.6.27F",
            "RELATIONSHIP_LEARNING_COMPLETED",
            "CERTIFIED_RELATIONSHIP_LEARNING",
            "evidence_authority_learning_integration",
        ),
        (
            result_g,
            "learning_engine_evidence_authority_learning_result_v1",
            "4.6.27G",
            "EVIDENCE_AUTHORITY_LEARNING_INTEGRATION_COMPLETED",
            "CERTIFIED_EVIDENCE_AUTHORITY_LEARNING_INTEGRATION",
            "conflict_exception_learning",
        ),
        (
            result_h,
            "learning_engine_conflict_exception_learning_result_v1",
            "4.6.27H",
            "CONFLICT_EXCEPTION_LEARNING_COMPLETED",
            "CERTIFIED_CONFLICT_EXCEPTION_LEARNING",
            "learning_stability_and_guard",
        ),
        (
            result_i,
            "learning_engine_stability_guard_result_v1",
            "4.6.27I",
            "LEARNING_STABILITY_AND_GUARD_COMPLETED",
            "CERTIFIED_LEARNING_STABILITY_AND_GUARD",
            "learning_provenance_and_lineage",
        ),
        (
            result_j,
            "learning_engine_provenance_lineage_result_v1",
            "4.6.27J",
            "LEARNING_PROVENANCE_AND_LINEAGE_COMPLETED",
            "CERTIFIED_LEARNING_PROVENANCE_AND_LINEAGE",
            "final_learning_engine_result",
        ),
        (
            result_k,
            "final_learning_engine_result_v1",
            "4.6.27K",
            "FINAL_LEARNING_ENGINE_RESULT_BUILT",
            "CERTIFIED_FINAL_LEARNING_ENGINE_RESULT",
            "full_learning_engine_hard_certification",
        ),
    )

    for (
        result,
        schema,
        patch,
        status,
        policy,
        next_stage,
    ) in required_stage_lifecycle:

        if result.get("schema") != schema:
            raise LearningEngineError(
                "Full certification schema drift at "
                f"{patch}."
            )

        if result.get("patch") != patch:
            raise LearningEngineError(
                "Full certification patch drift at "
                f"{patch}."
            )

        if result.get("status") != status:
            raise LearningEngineError(
                "Full certification status drift at "
                f"{patch}."
            )

        if result.get("policy") != policy:
            raise LearningEngineError(
                "Full certification policy drift at "
                f"{patch}."
            )

        if result.get("next") != next_stage:
            raise LearningEngineError(
                "Full certification handoff drift at "
                f"{patch}."
            )

    mutation_contract = scope_result.get(
        "learning_scope_mutation_contract"
    )

    if not isinstance(
        mutation_contract,
        dict,
    ):
        raise LearningEngineError(
            "Mutation contract is missing."
        )

    required_immutable_boundaries = (
        "dynamic_semantic_graph_is_read_only",
        "claim_integrity_is_read_only",
        "authority_is_read_only",
        "conflict_classification_is_read_only",
        "guard_disposition_is_read_only",
        "active_target_set_is_read_only",
        "semantic_memory_is_downstream",
    )

    for flag in required_immutable_boundaries:

        if mutation_contract.get(flag) is not True:
            raise LearningEngineError(
                "Certification boundary drift: "
                f"{flag}"
            )

    final_boundaries = result_k.get(
        "processing_boundaries"
    )

    if not isinstance(
        final_boundaries,
        dict,
    ):
        raise LearningEngineError(
            "Final processing boundaries are missing."
        )

    if final_boundaries.get(
        "semantic_memory_handoff_ready"
    ) is not True:
        raise LearningEngineError(
            "Semantic Memory handoff is not ready."
        )

    forbidden_true_flags = (
        "semantic_memory_written",
        "graph_mutation_performed",
        "claim_integrity_redecided",
        "authority_rescored",
        "conflict_reclassified",
        "upstream_guard_disposition_changed",
        "learned_truth_created",
        "certified_fact_created",
        "reasoning_performed",
        "external_target_created",
        "external_target_selected",
        "linking_decisions_performed",
        "highlights_created",
        "upstream_truth_rewritten",
    )

    for flag in forbidden_true_flags:

        if final_boundaries.get(flag) is not False:
            raise LearningEngineError(
                "Forbidden final side effect detected: "
                f"{flag}"
            )

    if (
        final_package.get("schema")
        != "final_learning_engine_package_v1"
    ):
        raise LearningEngineError(
            "Invalid final Learning Engine package schema."
        )

    if (
        final_package.get("final_policy")
        != "CERTIFIED_LEARNING_ENGINE_OUTPUT_FOR_SEMANTIC_MEMORY_HANDOFF"
    ):
        raise LearningEngineError(
            "Invalid final Learning Engine package policy."
        )

    if final_package.get(
        "learning_engine_output_is_certified_fact"
    ) is not False:
        raise LearningEngineError(
            "Learning Engine output was promoted "
            "to certified fact."
        )

    if final_package.get(
        "learning_engine_output_is_learned_truth"
    ) is not False:
        raise LearningEngineError(
            "Learning Engine output was promoted "
            "to learned truth."
        )

    if final_package.get(
        "semantic_memory_write_performed"
    ) is not False:
        raise LearningEngineError(
            "Semantic Memory was written during "
            "Learning Engine execution."
        )

    if final_package.get(
        "graph_mutation_performed"
    ) is not False:
        raise LearningEngineError(
            "Dynamic Semantic Graph mutation detected."
        )

    if final_package.get(
        "linking_decision_performed"
    ) is not False:
        raise LearningEngineError(
            "Linking decision detected during learning."
        )

    if scope_result != before:
        raise LearningEngineError(
            "4.6.27D certification input was mutated."
        )

    source_final_graph_id = result_k.get(
        "source_final_graph_id"
    )

    source_final_graph_digest = result_k.get(
        "source_final_graph_digest"
    )

    learning_lineage_root_id = result_k.get(
        "learning_lineage_root_id"
    )

    package_id = final_package.get(
        "final_learning_engine_package_id"
    )

    package_digest = final_package.get(
        "final_learning_engine_package_digest"
    )

    for name, value in (
        (
            "source_final_graph_id",
            source_final_graph_id,
        ),
        (
            "source_final_graph_digest",
            source_final_graph_digest,
        ),
        (
            "learning_lineage_root_id",
            learning_lineage_root_id,
        ),
        (
            "final_learning_engine_package_id",
            package_id,
        ),
        (
            "final_learning_engine_package_digest",
            package_digest,
        ),
    ):

        if not isinstance(
            value,
            str,
        ) or not value:
            raise LearningEngineError(
                "Missing final certification identifier: "
                f"{name}"
            )

    stage_summary = {
        "4.6.27E":
            result_e["status"],

        "4.6.27F":
            result_f["status"],

        "4.6.27G":
            result_g["status"],

        "4.6.27H":
            result_h["status"],

        "4.6.27I":
            result_i["status"],

        "4.6.27J":
            result_j["status"],

        "4.6.27K":
            result_k["status"],
    }

    return {
        "schema":
            "full_learning_engine_hard_certification_result_v1",

        "learning_engine_version":
            LEARNING_ENGINE_VERSION,

        "phase":
            LEARNING_ENGINE_PHASE,

        "patch":
            "4.6.27L",

        "status":
            "FULL_LEARNING_ENGINE_HARD_CERTIFIED",

        "certified":
            True,

        "source_final_graph_id":
            source_final_graph_id,

        "source_final_graph_digest":
            source_final_graph_digest,

        "learning_lineage_root_id":
            learning_lineage_root_id,

        "final_learning_engine_package_id":
            package_id,

        "final_learning_engine_package_digest":
            package_digest,

        "stage_summary":
            stage_summary,

        "stage_count":
            len(
                stage_summary
            ),

        "semantic_memory_handoff_ready":
            True,

        "semantic_memory_written":
            False,

        "dynamic_semantic_graph_mutated":
            False,

        "upstream_truth_rewritten":
            False,

        "authority_rescored":
            False,

        "claim_integrity_redecided":
            False,

        "conflict_reclassified":
            False,

        "upstream_guard_disposition_changed":
            False,

        "target_ownership_changed":
            False,

        "final_target_selected":
            False,

        "linking_decision_performed":
            False,

        "highlight_created":
            False,

        "learning_output_promoted_to_truth":
            False,

        "input_immutable":
            True,

        "certification_policy":
            "FULL_END_TO_END_LEARNING_ENGINE_HARD_CERTIFICATION",

        "final_learning_engine_result":
            copy.deepcopy(
                result_k
            ),

        "next":
            "semantic_memory",
    }
