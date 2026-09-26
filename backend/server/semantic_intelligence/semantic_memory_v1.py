from __future__ import annotations

from typing import Any
import copy
import hashlib
import json


SEMANTIC_MEMORY_VERSION = "semantic_memory_v1"
SEMANTIC_MEMORY_PHASE = "4.6.28"


class SemanticMemoryError(ValueError):
    pass

def inspect_certified_learning_engine_input_v1(
    learning_engine_certification: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.28A ? Certified Learning Engine Input Inspection.

    Inspects the fully hard-certified Learning Engine handoff before
    Semantic Memory admission.

    This stage performs inspection only. It does not persist memory,
    promote learned output to truth, mutate the Dynamic Semantic Graph,
    change Authority / Claim Integrity / conflict / guard state,
    create targets, select targets, or make linking decisions.
    """

    if not isinstance(
        learning_engine_certification,
        dict,
    ):
        raise SemanticMemoryError(
            "learning_engine_certification must be a dictionary."
        )

    expected = {
        "schema":
            "full_learning_engine_hard_certification_result_v1",

        "learning_engine_version":
            "learning_engine_v1",

        "phase":
            "4.6.27",

        "patch":
            "4.6.27L",

        "status":
            "FULL_LEARNING_ENGINE_HARD_CERTIFIED",

        "certified":
            True,

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

        "next":
            "semantic_memory",
    }

    for key, expected_value in expected.items():

        if (
            learning_engine_certification.get(key)
            != expected_value
        ):
            raise SemanticMemoryError(
                "Invalid certified Learning Engine "
                f"handoff field: {key}"
            )

    final_result = learning_engine_certification.get(
        "final_learning_engine_result"
    )

    if not isinstance(
        final_result,
        dict,
    ):
        raise SemanticMemoryError(
            "Final Learning Engine result is missing."
        )

    final_expected = {
        "schema":
            "final_learning_engine_result_v1",

        "learning_engine_version":
            "learning_engine_v1",

        "phase":
            "4.6.27",

        "patch":
            "4.6.27K",

        "status":
            "FINAL_LEARNING_ENGINE_RESULT_BUILT",

        "policy":
            "CERTIFIED_FINAL_LEARNING_ENGINE_RESULT",

        "next":
            "full_learning_engine_hard_certification",
    }

    for key, expected_value in final_expected.items():

        if final_result.get(key) != expected_value:
            raise SemanticMemoryError(
                "Invalid final Learning Engine "
                f"result field: {key}"
            )

    final_package = final_result.get(
        "final_learning_engine_package"
    )

    if not isinstance(
        final_package,
        dict,
    ):
        raise SemanticMemoryError(
            "Final Learning Engine package is missing."
        )

    if (
        final_package.get("schema")
        != "final_learning_engine_package_v1"
    ):
        raise SemanticMemoryError(
            "Invalid final Learning Engine package schema."
        )

    if (
        final_package.get("final_policy")
        != "CERTIFIED_LEARNING_ENGINE_OUTPUT_FOR_SEMANTIC_MEMORY_HANDOFF"
    ):
        raise SemanticMemoryError(
            "Invalid Semantic Memory handoff policy."
        )

    for flag in (
        "learning_engine_output_is_certified_fact",
        "learning_engine_output_is_learned_truth",
        "semantic_memory_write_performed",
        "graph_mutation_performed",
        "linking_decision_performed",
    ):

        if final_package.get(flag) is not False:
            raise SemanticMemoryError(
                "Unsafe Learning Engine package flag: "
                f"{flag}"
            )

    package_id = final_package.get(
        "final_learning_engine_package_id"
    )

    package_digest = final_package.get(
        "final_learning_engine_package_digest"
    )

    graph_id = final_package.get(
        "source_final_graph_id"
    )

    graph_digest = final_package.get(
        "source_final_graph_digest"
    )

    graph_snapshot_id = final_package.get(
        "source_graph_snapshot_id"
    )

    graph_lineage_root_id = final_package.get(
        "source_lineage_root_id"
    )

    learning_lineage_root_id = final_package.get(
        "learning_lineage_root_id"
    )

    for name, value in (
        (
            "final_learning_engine_package_id",
            package_id,
        ),
        (
            "final_learning_engine_package_digest",
            package_digest,
        ),
        (
            "source_final_graph_id",
            graph_id,
        ),
        (
            "source_final_graph_digest",
            graph_digest,
        ),
        (
            "source_graph_snapshot_id",
            graph_snapshot_id,
        ),
        (
            "source_lineage_root_id",
            graph_lineage_root_id,
        ),
        (
            "learning_lineage_root_id",
            learning_lineage_root_id,
        ),
    ):

        if not isinstance(
            value,
            str,
        ) or not value:
            raise SemanticMemoryError(
                "Missing certified handoff identifier: "
                f"{name}"
            )

    required_bundles = (
        (
            "semantic_pattern_observation_bundle",
            "learning_engine_semantic_pattern_observation_bundle_v1",
        ),
        (
            "relationship_learning_bundle",
            "learning_engine_relationship_learning_bundle_v1",
        ),
        (
            "evidence_authority_learning_bundle",
            "learning_engine_evidence_authority_learning_bundle_v1",
        ),
        (
            "conflict_exception_learning_bundle",
            "learning_engine_conflict_exception_learning_bundle_v1",
        ),
        (
            "learning_stability_guard_bundle",
            "learning_engine_stability_guard_bundle_v1",
        ),
        (
            "learning_provenance_lineage_bundle",
            "learning_engine_provenance_lineage_bundle_v1",
        ),
    )

    bundle_inventory = {}

    for key, expected_schema in required_bundles:

        bundle = final_package.get(
            key
        )

        if not isinstance(
            bundle,
            dict,
        ):
            raise SemanticMemoryError(
                "Missing Learning Engine bundle: "
                f"{key}"
            )

        if bundle.get("schema") != expected_schema:
            raise SemanticMemoryError(
                "Invalid Learning Engine bundle schema: "
                f"{key}"
            )

        bundle_inventory[
            key
        ] = expected_schema

    eligible_relationship_ids = final_package.get(
        "downstream_eligible_relationship_ids"
    )

    held_relationship_ids = final_package.get(
        "held_relationship_ids"
    )

    blocked_relationship_ids = final_package.get(
        "blocked_relationship_ids"
    )

    for name, value in (
        (
            "downstream_eligible_relationship_ids",
            eligible_relationship_ids,
        ),
        (
            "held_relationship_ids",
            held_relationship_ids,
        ),
        (
            "blocked_relationship_ids",
            blocked_relationship_ids,
        ),
    ):

        if not isinstance(
            value,
            tuple,
        ):
            raise SemanticMemoryError(
                f"{name} must be a tuple."
            )

    inspection_payload = {
        "package_id":
            package_id,

        "package_digest":
            package_digest,

        "source_final_graph_id":
            graph_id,

        "source_final_graph_digest":
            graph_digest,

        "source_graph_snapshot_id":
            graph_snapshot_id,

        "source_lineage_root_id":
            graph_lineage_root_id,

        "learning_lineage_root_id":
            learning_lineage_root_id,

        "bundle_inventory":
            bundle_inventory,

        "eligible_relationship_ids":
            list(
                eligible_relationship_ids
            ),

        "held_relationship_ids":
            list(
                held_relationship_ids
            ),

        "blocked_relationship_ids":
            list(
                blocked_relationship_ids
            ),
    }

    serialized = json.dumps(
        inspection_payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    inspection_digest = hashlib.sha256(
        serialized.encode("utf-8")
    ).hexdigest()

    return {
        "schema":
            "semantic_memory_learning_engine_input_inspection_result_v1",

        "semantic_memory_version":
            SEMANTIC_MEMORY_VERSION,

        "phase":
            SEMANTIC_MEMORY_PHASE,

        "patch":
            "4.6.28A",

        "status":
            "CERTIFIED_LEARNING_ENGINE_INPUT_INSPECTED",

        "inspection_id":
            "semanticmemoryinputinspection:v1:"
            + inspection_digest,

        "inspection_digest":
            inspection_digest,

        "source_learning_engine_version":
            learning_engine_certification.get(
                "learning_engine_version"
            ),

        "source_learning_engine_phase":
            learning_engine_certification.get(
                "phase"
            ),

        "source_learning_engine_certification_patch":
            learning_engine_certification.get(
                "patch"
            ),

        "source_final_learning_engine_package_id":
            package_id,

        "source_final_learning_engine_package_digest":
            package_digest,

        "source_final_graph_id":
            graph_id,

        "source_final_graph_digest":
            graph_digest,

        "source_graph_snapshot_id":
            graph_snapshot_id,

        "source_lineage_root_id":
            graph_lineage_root_id,

        "source_learning_lineage_root_id":
            learning_lineage_root_id,

        "bundle_inventory":
            copy.deepcopy(
                bundle_inventory
            ),

        "downstream_eligible_relationship_ids":
            tuple(
                eligible_relationship_ids
            ),

        "held_relationship_ids":
            tuple(
                held_relationship_ids
            ),

        "blocked_relationship_ids":
            tuple(
                blocked_relationship_ids
            ),

        "certified_learning_engine_input":
            copy.deepcopy(
                learning_engine_certification
            ),

        "processing_boundaries": {
            "learning_engine_input_inspected":
                True,

            "semantic_memory_admission_performed":
                False,

            "semantic_memory_object_created":
                False,

            "semantic_memory_written":
                False,

            "memory_persistence_performed":
                False,

            "memory_retrieval_performed":
                False,

            "learning_output_promoted_to_truth":
                False,

            "graph_mutation_performed":
                False,

            "authority_rescored":
                False,

            "claim_integrity_redecided":
                False,

            "conflict_reclassified":
                False,

            "upstream_guard_disposition_changed":
                False,

            "target_created":
                False,

            "target_selected":
                False,

            "linking_decision_performed":
                False,

            "highlight_created":
                False,
        },

        "policy":
            "CERTIFIED_LEARNING_ENGINE_INPUT_ONLY",

        "next":
            "semantic_memory_architecture_definition",
    }

def define_semantic_memory_architecture_v1(
    inspection_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.28B ? Semantic Memory Architecture Definition.

    Defines the canonical Semantic Memory architecture from the
    certified Learning Engine handoff without admitting, constructing,
    persisting, retrieving, or promoting any learned object.

    Semantic Memory stores durable learned knowledge with provenance,
    versioning, stability, conflict/exception preservation, and strict
    separation from certified upstream truth and target ownership.
    """

    if not isinstance(
        inspection_result,
        dict,
    ):
        raise SemanticMemoryError(
            "inspection_result must be a dictionary."
        )

    expected = {
        "schema":
            "semantic_memory_learning_engine_input_inspection_result_v1",

        "semantic_memory_version":
            SEMANTIC_MEMORY_VERSION,

        "phase":
            SEMANTIC_MEMORY_PHASE,

        "patch":
            "4.6.28A",

        "status":
            "CERTIFIED_LEARNING_ENGINE_INPUT_INSPECTED",

        "policy":
            "CERTIFIED_LEARNING_ENGINE_INPUT_ONLY",

        "next":
            "semantic_memory_architecture_definition",
    }

    for key, expected_value in expected.items():

        if inspection_result.get(key) != expected_value:
            raise SemanticMemoryError(
                "Invalid 4.6.28A lifecycle field: "
                f"{key}"
            )

    source_input = inspection_result.get(
        "certified_learning_engine_input"
    )

    if not isinstance(
        source_input,
        dict,
    ):
        raise SemanticMemoryError(
            "Certified Learning Engine input is missing."
        )

    boundaries = inspection_result.get(
        "processing_boundaries"
    )

    if not isinstance(
        boundaries,
        dict,
    ):
        raise SemanticMemoryError(
            "4.6.28A processing boundaries are missing."
        )

    if boundaries.get(
        "learning_engine_input_inspected"
    ) is not True:
        raise SemanticMemoryError(
            "Learning Engine input inspection is not certified."
        )

    for flag in (
        "semantic_memory_admission_performed",
        "semantic_memory_object_created",
        "semantic_memory_written",
        "memory_persistence_performed",
        "memory_retrieval_performed",
        "learning_output_promoted_to_truth",
        "graph_mutation_performed",
        "authority_rescored",
        "claim_integrity_redecided",
        "conflict_reclassified",
        "upstream_guard_disposition_changed",
        "target_created",
        "target_selected",
        "linking_decision_performed",
        "highlight_created",
    ):
        if boundaries.get(flag) is not False:
            raise SemanticMemoryError(
                "Unsafe 4.6.28A boundary state: "
                f"{flag}"
            )

    question = (
        "HOW_SHOULD_CERTIFIED_LEARNED_KNOWLEDGE_BE_STORED_VERSIONED_"
        "PRESERVED_AND_RETRIEVED_WITHOUT_PROMOTING_LEARNING_TO_TRUTH_"
        "OR_REWRITING_UPSTREAM_SEMANTIC_STATE"
    )

    memory_object_types = (
        "LEARNED_RELATIONSHIP_MEMORY",
        "SEMANTIC_PATTERN_MEMORY",
        "EVIDENCE_CONTEXT_MEMORY",
        "AUTHORITY_CONTEXT_MEMORY",
        "CONFLICT_PATTERN_MEMORY",
        "EXCEPTION_PATTERN_MEMORY",
        "STABILITY_STATE_MEMORY",
        "PROVENANCE_MEMORY",
        "LINEAGE_MEMORY",
        "HISTORICAL_MEMORY_VERSION",
        "SUPERSESSION_MEMORY",
        "RETENTION_STATE_MEMORY",
    )

    memory_states = (
        "CANDIDATE",
        "ACTIVE",
        "STABLE",
        "CONTESTED",
        "HELD",
        "BLOCKED",
        "WEAKENED",
        "SUPERSEDED",
        "RETIRED",
        "EXPIRED",
    )

    admission_states = (
        "NOT_EVALUATED",
        "ADMISSIBLE",
        "HELD",
        "BLOCKED",
        "REJECTED",
    )

    retention_states = (
        "RETAIN",
        "RETAIN_WITH_CAUTION",
        "HOLD",
        "SUPERSEDE",
        "RETIRE",
        "EXPIRE",
    )

    retrieval_classes = (
        "ACTIVE_MEMORY",
        "CONTESTED_MEMORY",
        "HISTORICAL_MEMORY",
        "HELD_MEMORY",
        "BLOCKED_MEMORY",
    )

    architecture_layers = (
        "CERTIFIED_LEARNING_ENGINE_INPUT",
        "MEMORY_INTAKE_VALIDATION",
        "OWNERSHIP_AND_MUTATION_CONTRACT",
        "LEARNED_KNOWLEDGE_ADMISSION",
        "MEMORY_OBJECT_CONSTRUCTION",
        "VERSIONING_AND_SUPERSESSION",
        "CONFLICT_EXCEPTION_PRESERVATION",
        "STABILITY_AND_RETENTION",
        "PROVENANCE_AND_LINEAGE",
        "RETRIEVAL_READ_CONTRACT",
        "FINAL_MEMORY_PACKAGE",
    )

    ownership = {
        "certified_upstream_truth":
            "DYNAMIC_SEMANTIC_GRAPH_AND_UPSTREAM_ENGINES",

        "learned_relationships":
            "LEARNING_ENGINE",

        "persistent_semantic_memory":
            "SEMANTIC_MEMORY",

        "memory_versions":
            "SEMANTIC_MEMORY",

        "memory_retention_state":
            "SEMANTIC_MEMORY",

        "memory_retrieval_contract":
            "SEMANTIC_MEMORY",

        "targets":
            "ACTIVE_TARGET_SET",

        "external_authority_partition":
            "ACTIVE_TARGET_SET",

        "external_route":
            "ACTIVE_TARGET_SET",

        "final_external_selection":
            "EXTERNAL_TARGET_RESOLVER",
    }

    truth_separation = {
        "memory_is_certified_truth":
            False,

        "memory_is_upstream_graph_truth":
            False,

        "learned_frequency_is_truth":
            False,

        "learned_stability_is_truth":
            False,

        "authority_is_truth":
            False,

        "memory_can_rewrite_claim_integrity":
            False,

        "memory_can_rewrite_authority":
            False,

        "memory_can_reclassify_conflict":
            False,

        "memory_can_change_upstream_guard":
            False,
    }

    persistence_principles = (
        "PERSIST_ONLY_AFTER_CERTIFIED_ADMISSION",
        "PRESERVE_ORIGINAL_LEARNING_PROVENANCE",
        "PRESERVE_GRAPH_PROVENANCE",
        "PRESERVE_CONFLICTS_AND_EXCEPTIONS",
        "PRESERVE_HELD_AND_BLOCKED_STATES",
        "VERSION_INSTEAD_OF_SILENT_OVERWRITE",
        "SUPERSEDE_WITH_HISTORY",
        "RETAIN_DETERMINISTIC_IDENTIFIERS",
        "SEPARATE_ACTIVE_FROM_HISTORICAL_MEMORY",
        "NO_TRUTH_PROMOTION",
    )

    retrieval_principles = (
        "READ_ONLY_CONSUMPTION_BY_DEFAULT",
        "FILTER_BY_MEMORY_STATE",
        "FILTER_BY_STABILITY",
        "FILTER_BY_GUARD_DISPOSITION",
        "FILTER_BY_PROVENANCE",
        "FILTER_BY_VERSION",
        "RETURN_CONFLICT_AND_EXCEPTION_CONTEXT",
        "DO_NOT_HIDE_HELD_OR_CONTESTED_HISTORY",
        "NO_TARGET_SELECTION_DURING_RETRIEVAL",
        "NO_LINKING_DECISION_DURING_RETRIEVAL",
    )

    prohibited_capabilities = (
        "REWRITE_DYNAMIC_SEMANTIC_GRAPH",
        "REWRITE_CLAIM_INTEGRITY",
        "RESCORE_AUTHORITY",
        "RECLASSIFY_UPSTREAM_CONFLICT",
        "CHANGE_UPSTREAM_GUARD_DISPOSITION",
        "PROMOTE_MEMORY_TO_CERTIFIED_TRUTH",
        "CREATE_ACTIVE_TARGETS",
        "CHANGE_TARGET_PARTITIONS",
        "CHANGE_ROUTE_ELIGIBILITY",
        "DISCOVER_EXTERNAL_URLS",
        "SELECT_FINAL_TARGETS",
        "MAKE_LINKING_DECISIONS",
        "CREATE_EDITOR_HIGHLIGHTS",
        "PERFORM_RUNTIME_REASONING",
    )

    required_memory_fields = (
        "memory_object_id",
        "memory_object_type",
        "memory_state",
        "admission_state",
        "retention_state",
        "source_learning_object_id",
        "source_learning_engine_package_id",
        "source_learning_lineage_root_id",
        "source_final_graph_id",
        "source_graph_snapshot_id",
        "source_graph_lineage_root_id",
        "provenance_references",
        "version",
        "created_from_certified_learning",
        "is_certified_fact",
        "is_learned_truth",
    )

    architecture = {
        "schema":
            "semantic_memory_architecture_v1",

        "question":
            question,

        "architecture_policy":
            "DURABLE_VERSIONED_PROVENANCE_PRESERVING_NON_TRUTH_SEMANTIC_MEMORY",

        "memory_object_types":
            memory_object_types,

        "memory_states":
            memory_states,

        "admission_states":
            admission_states,

        "retention_states":
            retention_states,

        "retrieval_classes":
            retrieval_classes,

        "architecture_layers":
            architecture_layers,

        "ownership":
            ownership,

        "truth_separation":
            truth_separation,

        "persistence_principles":
            persistence_principles,

        "retrieval_principles":
            retrieval_principles,

        "prohibited_capabilities":
            prohibited_capabilities,

        "required_memory_fields":
            required_memory_fields,

        "memory_is_durable":
            True,

        "memory_is_versioned":
            True,

        "memory_preserves_history":
            True,

        "memory_preserves_conflicts":
            True,

        "memory_preserves_exceptions":
            True,

        "memory_preserves_provenance":
            True,

        "memory_preserves_lineage":
            True,

        "memory_preserves_held_state":
            True,

        "memory_preserves_blocked_state":
            True,

        "memory_is_readable_downstream":
            True,

        "memory_is_not_reasoning_engine":
            True,

        "memory_is_not_target_store":
            True,

        "memory_is_not_linking_engine":
            True,
    }

    return {
        "schema":
            "semantic_memory_architecture_definition_result_v1",

        "semantic_memory_version":
            SEMANTIC_MEMORY_VERSION,

        "phase":
            SEMANTIC_MEMORY_PHASE,

        "patch":
            "4.6.28B",

        "status":
            "SEMANTIC_MEMORY_ARCHITECTURE_DEFINED",

        "source_inspection_id":
            inspection_result.get(
                "inspection_id"
            ),

        "source_inspection_digest":
            inspection_result.get(
                "inspection_digest"
            ),

        "source_final_learning_engine_package_id":
            inspection_result.get(
                "source_final_learning_engine_package_id"
            ),

        "source_final_learning_engine_package_digest":
            inspection_result.get(
                "source_final_learning_engine_package_digest"
            ),

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

        "source_learning_lineage_root_id":
            inspection_result.get(
                "source_learning_lineage_root_id"
            ),

        "semantic_memory_architecture":
            architecture,

        "certified_learning_engine_input_inspection":
            copy.deepcopy(
                inspection_result
            ),

        "processing_boundaries": {
            "architecture_definition_performed":
                True,

            "semantic_memory_admission_performed":
                False,

            "semantic_memory_object_created":
                False,

            "semantic_memory_written":
                False,

            "memory_persistence_performed":
                False,

            "memory_version_created":
                False,

            "memory_supersession_performed":
                False,

            "memory_retention_decision_performed":
                False,

            "memory_retrieval_performed":
                False,

            "learning_output_promoted_to_truth":
                False,

            "graph_mutation_performed":
                False,

            "authority_rescored":
                False,

            "claim_integrity_redecided":
                False,

            "conflict_reclassified":
                False,

            "upstream_guard_disposition_changed":
                False,

            "target_created":
                False,

            "target_selected":
                False,

            "linking_decision_performed":
                False,

            "highlight_created":
                False,
        },

        "policy":
            "CERTIFIED_SEMANTIC_MEMORY_ARCHITECTURE",

        "next":
            "memory_intake_validation",
    }

def validate_semantic_memory_intake_v1(
    architecture_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.28C ? Memory Intake Validation.

    Validates the certified Learning Engine handoff against the
    canonical Semantic Memory architecture before any learned
    knowledge admission or memory persistence occurs.
    """

    if not isinstance(
        architecture_result,
        dict,
    ):
        raise SemanticMemoryError(
            "architecture_result must be a dictionary."
        )

    expected = {
        "schema":
            "semantic_memory_architecture_definition_result_v1",

        "semantic_memory_version":
            SEMANTIC_MEMORY_VERSION,

        "phase":
            SEMANTIC_MEMORY_PHASE,

        "patch":
            "4.6.28B",

        "status":
            "SEMANTIC_MEMORY_ARCHITECTURE_DEFINED",

        "policy":
            "CERTIFIED_SEMANTIC_MEMORY_ARCHITECTURE",

        "next":
            "memory_intake_validation",
    }

    for key, expected_value in expected.items():

        if architecture_result.get(key) != expected_value:
            raise SemanticMemoryError(
                "Invalid 4.6.28B lifecycle field: "
                f"{key}"
            )

    architecture = architecture_result.get(
        "semantic_memory_architecture"
    )

    inspection = architecture_result.get(
        "certified_learning_engine_input_inspection"
    )

    boundaries = architecture_result.get(
        "processing_boundaries"
    )

    if not isinstance(
        architecture,
        dict,
    ):
        raise SemanticMemoryError(
            "Semantic Memory architecture is missing."
        )

    if (
        architecture.get("schema")
        != "semantic_memory_architecture_v1"
    ):
        raise SemanticMemoryError(
            "Invalid Semantic Memory architecture schema."
        )

    if (
        architecture.get("architecture_policy")
        != "DURABLE_VERSIONED_PROVENANCE_PRESERVING_NON_TRUTH_SEMANTIC_MEMORY"
    ):
        raise SemanticMemoryError(
            "Invalid Semantic Memory architecture policy."
        )

    if not isinstance(
        inspection,
        dict,
    ):
        raise SemanticMemoryError(
            "Certified Learning Engine inspection is missing."
        )

    if (
        inspection.get("schema")
        != "semantic_memory_learning_engine_input_inspection_result_v1"
    ):
        raise SemanticMemoryError(
            "Invalid certified Learning Engine inspection schema."
        )

    if inspection.get(
        "status"
    ) != "CERTIFIED_LEARNING_ENGINE_INPUT_INSPECTED":
        raise SemanticMemoryError(
            "Learning Engine input has not been certified."
        )

    if inspection.get(
        "policy"
    ) != "CERTIFIED_LEARNING_ENGINE_INPUT_ONLY":
        raise SemanticMemoryError(
            "Invalid Learning Engine inspection policy."
        )

    if not isinstance(
        boundaries,
        dict,
    ):
        raise SemanticMemoryError(
            "4.6.28B processing boundaries are missing."
        )

    if boundaries.get(
        "architecture_definition_performed"
    ) is not True:
        raise SemanticMemoryError(
            "Semantic Memory architecture was not defined."
        )

    for flag in (
        "semantic_memory_admission_performed",
        "semantic_memory_object_created",
        "semantic_memory_written",
        "memory_persistence_performed",
        "memory_version_created",
        "memory_supersession_performed",
        "memory_retention_decision_performed",
        "memory_retrieval_performed",
        "learning_output_promoted_to_truth",
        "graph_mutation_performed",
        "authority_rescored",
        "claim_integrity_redecided",
        "conflict_reclassified",
        "upstream_guard_disposition_changed",
        "target_created",
        "target_selected",
        "linking_decision_performed",
        "highlight_created",
    ):
        if boundaries.get(flag) is not False:
            raise SemanticMemoryError(
                "Unsafe pre-intake boundary state: "
                f"{flag}"
            )

    truth_separation = architecture.get(
        "truth_separation"
    )

    ownership = architecture.get(
        "ownership"
    )

    persistence_principles = architecture.get(
        "persistence_principles"
    )

    prohibited_capabilities = architecture.get(
        "prohibited_capabilities"
    )

    memory_object_types = architecture.get(
        "memory_object_types"
    )

    memory_states = architecture.get(
        "memory_states"
    )

    admission_states = architecture.get(
        "admission_states"
    )

    retention_states = architecture.get(
        "retention_states"
    )

    retrieval_classes = architecture.get(
        "retrieval_classes"
    )

    required_memory_fields = architecture.get(
        "required_memory_fields"
    )

    tuple_fields = (
        (
            "memory_object_types",
            memory_object_types,
        ),
        (
            "memory_states",
            memory_states,
        ),
        (
            "admission_states",
            admission_states,
        ),
        (
            "retention_states",
            retention_states,
        ),
        (
            "retrieval_classes",
            retrieval_classes,
        ),
        (
            "persistence_principles",
            persistence_principles,
        ),
        (
            "prohibited_capabilities",
            prohibited_capabilities,
        ),
        (
            "required_memory_fields",
            required_memory_fields,
        ),
    )

    for name, value in tuple_fields:

        if not isinstance(
            value,
            tuple,
        ):
            raise SemanticMemoryError(
                f"{name} must be a tuple."
            )

    if not isinstance(
        truth_separation,
        dict,
    ):
        raise SemanticMemoryError(
            "truth_separation is missing."
        )

    for key in (
        "memory_is_certified_truth",
        "memory_is_upstream_graph_truth",
        "learned_frequency_is_truth",
        "learned_stability_is_truth",
        "authority_is_truth",
        "memory_can_rewrite_claim_integrity",
        "memory_can_rewrite_authority",
        "memory_can_reclassify_conflict",
        "memory_can_change_upstream_guard",
    ):
        if truth_separation.get(key) is not False:
            raise SemanticMemoryError(
                "Unsafe truth-separation contract: "
                f"{key}"
            )

    if not isinstance(
        ownership,
        dict,
    ):
        raise SemanticMemoryError(
            "Semantic Memory ownership contract is missing."
        )

    expected_ownership = {
        "persistent_semantic_memory":
            "SEMANTIC_MEMORY",

        "memory_versions":
            "SEMANTIC_MEMORY",

        "memory_retention_state":
            "SEMANTIC_MEMORY",

        "memory_retrieval_contract":
            "SEMANTIC_MEMORY",

        "targets":
            "ACTIVE_TARGET_SET",

        "external_authority_partition":
            "ACTIVE_TARGET_SET",

        "external_route":
            "ACTIVE_TARGET_SET",

        "final_external_selection":
            "EXTERNAL_TARGET_RESOLVER",
    }

    for key, expected_owner in expected_ownership.items():

        if ownership.get(key) != expected_owner:
            raise SemanticMemoryError(
                "Semantic Memory ownership drift: "
                f"{key}"
            )

    for principle in (
        "PERSIST_ONLY_AFTER_CERTIFIED_ADMISSION",
        "PRESERVE_ORIGINAL_LEARNING_PROVENANCE",
        "PRESERVE_GRAPH_PROVENANCE",
        "PRESERVE_CONFLICTS_AND_EXCEPTIONS",
        "PRESERVE_HELD_AND_BLOCKED_STATES",
        "VERSION_INSTEAD_OF_SILENT_OVERWRITE",
        "SUPERSEDE_WITH_HISTORY",
        "RETAIN_DETERMINISTIC_IDENTIFIERS",
        "SEPARATE_ACTIVE_FROM_HISTORICAL_MEMORY",
        "NO_TRUTH_PROMOTION",
    ):
        if principle not in persistence_principles:
            raise SemanticMemoryError(
                "Required persistence principle missing: "
                f"{principle}"
            )

    for prohibition in (
        "REWRITE_DYNAMIC_SEMANTIC_GRAPH",
        "REWRITE_CLAIM_INTEGRITY",
        "RESCORE_AUTHORITY",
        "RECLASSIFY_UPSTREAM_CONFLICT",
        "CHANGE_UPSTREAM_GUARD_DISPOSITION",
        "PROMOTE_MEMORY_TO_CERTIFIED_TRUTH",
        "CREATE_ACTIVE_TARGETS",
        "CHANGE_TARGET_PARTITIONS",
        "CHANGE_ROUTE_ELIGIBILITY",
        "DISCOVER_EXTERNAL_URLS",
        "SELECT_FINAL_TARGETS",
        "MAKE_LINKING_DECISIONS",
        "CREATE_EDITOR_HIGHLIGHTS",
        "PERFORM_RUNTIME_REASONING",
    ):
        if prohibition not in prohibited_capabilities:
            raise SemanticMemoryError(
                "Required prohibition missing: "
                f"{prohibition}"
            )

    for required_type in (
        "LEARNED_RELATIONSHIP_MEMORY",
        "SEMANTIC_PATTERN_MEMORY",
        "CONFLICT_PATTERN_MEMORY",
        "EXCEPTION_PATTERN_MEMORY",
        "PROVENANCE_MEMORY",
        "LINEAGE_MEMORY",
        "HISTORICAL_MEMORY_VERSION",
        "SUPERSESSION_MEMORY",
        "RETENTION_STATE_MEMORY",
    ):
        if required_type not in memory_object_types:
            raise SemanticMemoryError(
                "Required memory object type missing: "
                f"{required_type}"
            )

    for required_state in (
        "ACTIVE",
        "STABLE",
        "CONTESTED",
        "HELD",
        "BLOCKED",
        "SUPERSEDED",
        "RETIRED",
    ):
        if required_state not in memory_states:
            raise SemanticMemoryError(
                "Required memory state missing: "
                f"{required_state}"
            )

    for required_state in (
        "NOT_EVALUATED",
        "ADMISSIBLE",
        "HELD",
        "BLOCKED",
        "REJECTED",
    ):
        if required_state not in admission_states:
            raise SemanticMemoryError(
                "Required admission state missing: "
                f"{required_state}"
            )

    required_fields = (
        "memory_object_id",
        "memory_object_type",
        "memory_state",
        "admission_state",
        "retention_state",
        "source_learning_object_id",
        "source_learning_engine_package_id",
        "source_learning_lineage_root_id",
        "source_final_graph_id",
        "source_graph_snapshot_id",
        "source_graph_lineage_root_id",
        "provenance_references",
        "version",
        "created_from_certified_learning",
        "is_certified_fact",
        "is_learned_truth",
    )

    for field in required_fields:

        if field not in required_memory_fields:
            raise SemanticMemoryError(
                "Required memory field missing: "
                f"{field}"
            )

    certified_input = inspection.get(
        "certified_learning_engine_input"
    )

    if not isinstance(
        certified_input,
        dict,
    ):
        raise SemanticMemoryError(
            "Certified Learning Engine input is missing."
        )

    if (
        certified_input.get("schema")
        != "full_learning_engine_hard_certification_result_v1"
    ):
        raise SemanticMemoryError(
            "Invalid Learning Engine certification schema."
        )

    if certified_input.get(
        "certified"
    ) is not True:
        raise SemanticMemoryError(
            "Learning Engine input is not hard-certified."
        )

    if certified_input.get(
        "semantic_memory_handoff_ready"
    ) is not True:
        raise SemanticMemoryError(
            "Learning Engine is not ready for Semantic Memory."
        )

    if certified_input.get(
        "semantic_memory_written"
    ) is not False:
        raise SemanticMemoryError(
            "Semantic Memory was already written upstream."
        )

    if certified_input.get(
        "learning_output_promoted_to_truth"
    ) is not False:
        raise SemanticMemoryError(
            "Learning Engine output was promoted to truth."
        )

    final_result = certified_input.get(
        "final_learning_engine_result"
    )

    if not isinstance(
        final_result,
        dict,
    ):
        raise SemanticMemoryError(
            "Final Learning Engine result is missing."
        )

    final_package = final_result.get(
        "final_learning_engine_package"
    )

    if not isinstance(
        final_package,
        dict,
    ):
        raise SemanticMemoryError(
            "Final Learning Engine package is missing."
        )

    if (
        final_package.get("schema")
        != "final_learning_engine_package_v1"
    ):
        raise SemanticMemoryError(
            "Invalid final Learning Engine package schema."
        )

    if (
        final_package.get("final_policy")
        != "CERTIFIED_LEARNING_ENGINE_OUTPUT_FOR_SEMANTIC_MEMORY_HANDOFF"
    ):
        raise SemanticMemoryError(
            "Invalid final Learning Engine handoff policy."
        )

    for flag in (
        "learning_engine_output_is_certified_fact",
        "learning_engine_output_is_learned_truth",
        "semantic_memory_write_performed",
        "graph_mutation_performed",
        "linking_decision_performed",
    ):
        if final_package.get(flag) is not False:
            raise SemanticMemoryError(
                "Unsafe final Learning Engine package flag: "
                f"{flag}"
            )

    eligible_ids = inspection.get(
        "downstream_eligible_relationship_ids"
    )

    held_ids = inspection.get(
        "held_relationship_ids"
    )

    blocked_ids = inspection.get(
        "blocked_relationship_ids"
    )

    for name, value in (
        (
            "downstream_eligible_relationship_ids",
            eligible_ids,
        ),
        (
            "held_relationship_ids",
            held_ids,
        ),
        (
            "blocked_relationship_ids",
            blocked_ids,
        ),
    ):
        if not isinstance(
            value,
            tuple,
        ):
            raise SemanticMemoryError(
                f"{name} must be a tuple."
            )

    eligible_set = set(
        eligible_ids
    )

    held_set = set(
        held_ids
    )

    blocked_set = set(
        blocked_ids
    )

    if eligible_set & held_set:
        raise SemanticMemoryError(
            "Eligible and held relationship sets overlap."
        )

    if eligible_set & blocked_set:
        raise SemanticMemoryError(
            "Eligible and blocked relationship sets overlap."
        )

    if held_set & blocked_set:
        raise SemanticMemoryError(
            "Held and blocked relationship sets overlap."
        )

    intake_contract = {
        "schema":
            "semantic_memory_intake_contract_v1",

        "accepted_source":
            "FULLY_CERTIFIED_LEARNING_ENGINE_ONLY",

        "required_learning_engine_schema":
            "full_learning_engine_hard_certification_result_v1",

        "required_final_package_schema":
            "final_learning_engine_package_v1",

        "required_final_package_policy":
            "CERTIFIED_LEARNING_ENGINE_OUTPUT_FOR_SEMANTIC_MEMORY_HANDOFF",

        "eligible_relationships_may_be_considered_for_admission":
            True,

        "held_relationships_must_remain_held":
            True,

        "blocked_relationships_must_remain_blocked":
            True,

        "conflicts_must_be_preserved":
            True,

        "exceptions_must_be_preserved":
            True,

        "provenance_must_be_preserved":
            True,

        "lineage_must_be_preserved":
            True,

        "graph_state_is_read_only":
            True,

        "learning_engine_output_is_read_only":
            True,

        "semantic_memory_admission_not_yet_performed":
            True,

        "semantic_memory_persistence_not_yet_performed":
            True,

        "truth_promotion_forbidden":
            True,

        "target_creation_forbidden":
            True,

        "target_selection_forbidden":
            True,

        "linking_decision_forbidden":
            True,
    }

    validation_report = {
        "schema":
            "semantic_memory_intake_validation_report_v1",

        "intake_valid":
            True,

        "architecture_valid":
            True,

        "learning_engine_certification_valid":
            True,

        "learning_engine_package_valid":
            True,

        "truth_separation_valid":
            True,

        "ownership_valid":
            True,

        "relationship_state_partitions_valid":
            True,

        "provenance_requirement_valid":
            True,

        "conflict_exception_preservation_valid":
            True,

        "safe_for_admission_stage":
            True,

        "admission_performed":
            False,

        "persistence_performed":
            False,
    }

    return {
        "schema":
            "semantic_memory_intake_validation_result_v1",

        "semantic_memory_version":
            SEMANTIC_MEMORY_VERSION,

        "phase":
            SEMANTIC_MEMORY_PHASE,

        "patch":
            "4.6.28C",

        "status":
            "SEMANTIC_MEMORY_INTAKE_VALIDATED",

        "source_final_learning_engine_package_id":
            architecture_result.get(
                "source_final_learning_engine_package_id"
            ),

        "source_final_learning_engine_package_digest":
            architecture_result.get(
                "source_final_learning_engine_package_digest"
            ),

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

        "source_learning_lineage_root_id":
            architecture_result.get(
                "source_learning_lineage_root_id"
            ),

        "semantic_memory_architecture":
            copy.deepcopy(
                architecture
            ),

        "semantic_memory_intake_contract":
            intake_contract,

        "validation_report":
            validation_report,

        "certified_learning_engine_input_inspection":
            copy.deepcopy(
                inspection
            ),

        "processing_boundaries": {
            "memory_intake_validation_performed":
                True,

            "semantic_memory_admission_performed":
                False,

            "semantic_memory_object_created":
                False,

            "semantic_memory_written":
                False,

            "memory_persistence_performed":
                False,

            "memory_version_created":
                False,

            "memory_supersession_performed":
                False,

            "memory_retention_decision_performed":
                False,

            "memory_retrieval_performed":
                False,

            "learning_output_promoted_to_truth":
                False,

            "graph_mutation_performed":
                False,

            "authority_rescored":
                False,

            "claim_integrity_redecided":
                False,

            "conflict_reclassified":
                False,

            "upstream_guard_disposition_changed":
                False,

            "target_created":
                False,

            "target_selected":
                False,

            "linking_decision_performed":
                False,

            "highlight_created":
                False,
        },

        "policy":
            "CERTIFIED_SEMANTIC_MEMORY_INTAKE_VALIDATION",

        "next":
            "memory_ownership_and_mutation_contract",
    }

def define_semantic_memory_ownership_mutation_contract_v1(
    intake_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.28D ? Memory Ownership & Mutation Contract.

    Defines the exact ownership and mutation boundary for Semantic
    Memory before learned knowledge admission.

    Semantic Memory may mutate only Semantic Memory-owned state.
    Certified Learning Engine output and all upstream semantic truth
    remain read-only.
    """

    if not isinstance(
        intake_result,
        dict,
    ):
        raise SemanticMemoryError(
            "intake_result must be a dictionary."
        )

    expected = {
        "schema":
            "semantic_memory_intake_validation_result_v1",

        "semantic_memory_version":
            SEMANTIC_MEMORY_VERSION,

        "phase":
            SEMANTIC_MEMORY_PHASE,

        "patch":
            "4.6.28C",

        "status":
            "SEMANTIC_MEMORY_INTAKE_VALIDATED",

        "policy":
            "CERTIFIED_SEMANTIC_MEMORY_INTAKE_VALIDATION",

        "next":
            "memory_ownership_and_mutation_contract",
    }

    for key, expected_value in expected.items():

        if intake_result.get(key) != expected_value:
            raise SemanticMemoryError(
                "Invalid 4.6.28C lifecycle field: "
                f"{key}"
            )

    architecture = intake_result.get(
        "semantic_memory_architecture"
    )

    intake_contract = intake_result.get(
        "semantic_memory_intake_contract"
    )

    validation_report = intake_result.get(
        "validation_report"
    )

    inspection = intake_result.get(
        "certified_learning_engine_input_inspection"
    )

    boundaries = intake_result.get(
        "processing_boundaries"
    )

    if not isinstance(
        architecture,
        dict,
    ):
        raise SemanticMemoryError(
            "Semantic Memory architecture is missing."
        )

    if (
        architecture.get("schema")
        != "semantic_memory_architecture_v1"
    ):
        raise SemanticMemoryError(
            "Invalid Semantic Memory architecture schema."
        )

    if not isinstance(
        intake_contract,
        dict,
    ):
        raise SemanticMemoryError(
            "Semantic Memory intake contract is missing."
        )

    if (
        intake_contract.get("schema")
        != "semantic_memory_intake_contract_v1"
    ):
        raise SemanticMemoryError(
            "Invalid Semantic Memory intake contract schema."
        )

    if not isinstance(
        validation_report,
        dict,
    ):
        raise SemanticMemoryError(
            "Semantic Memory validation report is missing."
        )

    if (
        validation_report.get("schema")
        != "semantic_memory_intake_validation_report_v1"
    ):
        raise SemanticMemoryError(
            "Invalid Semantic Memory validation report schema."
        )

    if validation_report.get(
        "intake_valid"
    ) is not True:
        raise SemanticMemoryError(
            "Semantic Memory intake is not valid."
        )

    if validation_report.get(
        "safe_for_admission_stage"
    ) is not True:
        raise SemanticMemoryError(
            "Semantic Memory intake is not safe for admission."
        )

    if not isinstance(
        inspection,
        dict,
    ):
        raise SemanticMemoryError(
            "Certified Learning Engine inspection is missing."
        )

    if not isinstance(
        boundaries,
        dict,
    ):
        raise SemanticMemoryError(
            "4.6.28C processing boundaries are missing."
        )

    if boundaries.get(
        "memory_intake_validation_performed"
    ) is not True:
        raise SemanticMemoryError(
            "Memory intake validation has not completed."
        )

    for flag in (
        "semantic_memory_admission_performed",
        "semantic_memory_object_created",
        "semantic_memory_written",
        "memory_persistence_performed",
        "memory_version_created",
        "memory_supersession_performed",
        "memory_retention_decision_performed",
        "memory_retrieval_performed",
        "learning_output_promoted_to_truth",
        "graph_mutation_performed",
        "authority_rescored",
        "claim_integrity_redecided",
        "conflict_reclassified",
        "upstream_guard_disposition_changed",
        "target_created",
        "target_selected",
        "linking_decision_performed",
        "highlight_created",
    ):
        if boundaries.get(flag) is not False:
            raise SemanticMemoryError(
                "Unsafe 4.6.28C boundary state: "
                f"{flag}"
            )

    ownership = architecture.get(
        "ownership"
    )

    truth_separation = architecture.get(
        "truth_separation"
    )

    if not isinstance(
        ownership,
        dict,
    ):
        raise SemanticMemoryError(
            "Architecture ownership contract is missing."
        )

    if not isinstance(
        truth_separation,
        dict,
    ):
        raise SemanticMemoryError(
            "Architecture truth separation is missing."
        )

    expected_ownership = {
        "persistent_semantic_memory":
            "SEMANTIC_MEMORY",

        "memory_versions":
            "SEMANTIC_MEMORY",

        "memory_retention_state":
            "SEMANTIC_MEMORY",

        "memory_retrieval_contract":
            "SEMANTIC_MEMORY",

        "targets":
            "ACTIVE_TARGET_SET",

        "external_authority_partition":
            "ACTIVE_TARGET_SET",

        "external_route":
            "ACTIVE_TARGET_SET",

        "final_external_selection":
            "EXTERNAL_TARGET_RESOLVER",
    }

    for key, expected_owner in expected_ownership.items():

        if ownership.get(key) != expected_owner:
            raise SemanticMemoryError(
                "Ownership drift detected: "
                f"{key}"
            )

    for key in (
        "memory_is_certified_truth",
        "memory_is_upstream_graph_truth",
        "learned_frequency_is_truth",
        "learned_stability_is_truth",
        "authority_is_truth",
        "memory_can_rewrite_claim_integrity",
        "memory_can_rewrite_authority",
        "memory_can_reclassify_conflict",
        "memory_can_change_upstream_guard",
    ):
        if truth_separation.get(key) is not False:
            raise SemanticMemoryError(
                "Truth-separation drift detected: "
                f"{key}"
            )

    allowed_memory_mutations = (
        "CREATE_MEMORY_OBJECT",
        "ADMIT_CERTIFIED_LEARNED_KNOWLEDGE",
        "ATTACH_SOURCE_LEARNING_REFERENCE",
        "ATTACH_LEARNING_PROVENANCE_REFERENCE",
        "ATTACH_GRAPH_PROVENANCE_REFERENCE",
        "ATTACH_LINEAGE_REFERENCE",
        "SET_MEMORY_STATE",
        "SET_ADMISSION_STATE",
        "SET_RETENTION_STATE",
        "CREATE_MEMORY_VERSION",
        "PRESERVE_MEMORY_HISTORY",
        "SUPERSEDE_MEMORY_OBJECT",
        "RETIRE_MEMORY_OBJECT",
        "EXPIRE_MEMORY_OBJECT",
        "REGISTER_CONFLICT_MEMORY",
        "REGISTER_EXCEPTION_MEMORY",
        "REGISTER_HELD_MEMORY",
        "REGISTER_BLOCKED_MEMORY",
        "CREATE_RETRIEVAL_METADATA",
    )

    forbidden_memory_mutations = (
        "MUTATE_LEARNING_ENGINE_OUTPUT",
        "REWRITE_DYNAMIC_SEMANTIC_GRAPH",
        "REWRITE_CLAIM_INTEGRITY",
        "RESCORE_AUTHORITY",
        "RECLASSIFY_UPSTREAM_CONFLICT",
        "CHANGE_UPSTREAM_GUARD_DISPOSITION",
        "PROMOTE_MEMORY_TO_CERTIFIED_TRUTH",
        "PROMOTE_MEMORY_TO_LEARNED_TRUTH",
        "CREATE_ACTIVE_TARGET",
        "CHANGE_ACTIVE_TARGET_SET_OWNERSHIP",
        "CHANGE_TARGET_PARTITION",
        "CHANGE_ROUTE_ELIGIBILITY",
        "DISCOVER_EXTERNAL_URL",
        "SELECT_FINAL_TARGET",
        "MAKE_LINKING_DECISION",
        "CREATE_EDITOR_HIGHLIGHT",
        "PERFORM_RUNTIME_REASONING",
    )

    ownership_contract = {
        "schema":
            "semantic_memory_ownership_mutation_contract_v1",

        "semantic_memory_owns_persistent_memory":
            True,

        "semantic_memory_owns_memory_versions":
            True,

        "semantic_memory_owns_memory_history":
            True,

        "semantic_memory_owns_retention_state":
            True,

        "semantic_memory_owns_retrieval_metadata":
            True,

        "learning_engine_output_is_read_only":
            True,

        "dynamic_semantic_graph_is_read_only":
            True,

        "claim_integrity_is_read_only":
            True,

        "authority_is_read_only":
            True,

        "conflict_classification_is_read_only":
            True,

        "upstream_guard_disposition_is_read_only":
            True,

        "active_target_set_is_read_only":
            True,

        "external_authority_partition_is_read_only":
            True,

        "external_route_eligibility_is_read_only":
            True,

        "external_target_resolver_ownership_is_preserved":
            True,

        "semantic_memory_may_not_promote_truth":
            True,

        "semantic_memory_may_not_reason":
            True,

        "semantic_memory_may_not_select_targets":
            True,

        "semantic_memory_may_not_make_linking_decisions":
            True,

        "allowed_memory_mutations":
            allowed_memory_mutations,

        "forbidden_memory_mutations":
            forbidden_memory_mutations,
    }

    return {
        "schema":
            "semantic_memory_ownership_mutation_contract_result_v1",

        "semantic_memory_version":
            SEMANTIC_MEMORY_VERSION,

        "phase":
            SEMANTIC_MEMORY_PHASE,

        "patch":
            "4.6.28D",

        "status":
            "SEMANTIC_MEMORY_OWNERSHIP_MUTATION_CONTRACT_DEFINED",

        "source_final_learning_engine_package_id":
            intake_result.get(
                "source_final_learning_engine_package_id"
            ),

        "source_final_learning_engine_package_digest":
            intake_result.get(
                "source_final_learning_engine_package_digest"
            ),

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

        "source_learning_lineage_root_id":
            intake_result.get(
                "source_learning_lineage_root_id"
            ),

        "semantic_memory_architecture":
            copy.deepcopy(
                architecture
            ),

        "semantic_memory_intake_contract":
            copy.deepcopy(
                intake_contract
            ),

        "validation_report":
            copy.deepcopy(
                validation_report
            ),

        "semantic_memory_ownership_mutation_contract":
            ownership_contract,

        "certified_learning_engine_input_inspection":
            copy.deepcopy(
                inspection
            ),

        "processing_boundaries": {
            "memory_ownership_mutation_contract_defined":
                True,

            "semantic_memory_admission_performed":
                False,

            "semantic_memory_object_created":
                False,

            "semantic_memory_written":
                False,

            "memory_persistence_performed":
                False,

            "memory_version_created":
                False,

            "memory_supersession_performed":
                False,

            "memory_retention_decision_performed":
                False,

            "memory_retrieval_performed":
                False,

            "learning_output_promoted_to_truth":
                False,

            "graph_mutation_performed":
                False,

            "authority_rescored":
                False,

            "claim_integrity_redecided":
                False,

            "conflict_reclassified":
                False,

            "upstream_guard_disposition_changed":
                False,

            "target_created":
                False,

            "target_selected":
                False,

            "linking_decision_performed":
                False,

            "highlight_created":
                False,
        },

        "policy":
            "CERTIFIED_SEMANTIC_MEMORY_OWNERSHIP_MUTATION_CONTRACT",

        "next":
            "learned_knowledge_admission",
    }

def admit_learned_knowledge_v1(
    ownership_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.28E ? Learned Knowledge Admission.

    Classifies certified Learning Engine relationships for Semantic
    Memory admission without constructing or persisting memory objects.

    Eligible relationships become ADMISSIBLE.
    Held relationships remain HELD.
    Blocked relationships remain BLOCKED.

    No Learning Engine state or upstream semantic state is mutated.
    """

    if not isinstance(
        ownership_result,
        dict,
    ):
        raise SemanticMemoryError(
            "ownership_result must be a dictionary."
        )

    expected = {
        "schema":
            "semantic_memory_ownership_mutation_contract_result_v1",

        "semantic_memory_version":
            SEMANTIC_MEMORY_VERSION,

        "phase":
            SEMANTIC_MEMORY_PHASE,

        "patch":
            "4.6.28D",

        "status":
            "SEMANTIC_MEMORY_OWNERSHIP_MUTATION_CONTRACT_DEFINED",

        "policy":
            "CERTIFIED_SEMANTIC_MEMORY_OWNERSHIP_MUTATION_CONTRACT",

        "next":
            "learned_knowledge_admission",
    }

    for key, expected_value in expected.items():

        if ownership_result.get(key) != expected_value:
            raise SemanticMemoryError(
                "Invalid 4.6.28D lifecycle field: "
                f"{key}"
            )

    ownership_contract = ownership_result.get(
        "semantic_memory_ownership_mutation_contract"
    )

    inspection = ownership_result.get(
        "certified_learning_engine_input_inspection"
    )

    boundaries = ownership_result.get(
        "processing_boundaries"
    )

    if not isinstance(
        ownership_contract,
        dict,
    ):
        raise SemanticMemoryError(
            "Semantic Memory ownership contract is missing."
        )

    if (
        ownership_contract.get("schema")
        != "semantic_memory_ownership_mutation_contract_v1"
    ):
        raise SemanticMemoryError(
            "Invalid Semantic Memory ownership contract schema."
        )

    allowed_mutations = ownership_contract.get(
        "allowed_memory_mutations"
    )

    forbidden_mutations = ownership_contract.get(
        "forbidden_memory_mutations"
    )

    if not isinstance(
        allowed_mutations,
        tuple,
    ):
        raise SemanticMemoryError(
            "Allowed mutation contract must be a tuple."
        )

    if not isinstance(
        forbidden_mutations,
        tuple,
    ):
        raise SemanticMemoryError(
            "Forbidden mutation contract must be a tuple."
        )

    for permission in (
        "ADMIT_CERTIFIED_LEARNED_KNOWLEDGE",
        "REGISTER_HELD_MEMORY",
        "REGISTER_BLOCKED_MEMORY",
    ):
        if permission not in allowed_mutations:
            raise SemanticMemoryError(
                "Required admission permission missing: "
                f"{permission}"
            )

    for prohibition in (
        "MUTATE_LEARNING_ENGINE_OUTPUT",
        "PROMOTE_MEMORY_TO_CERTIFIED_TRUTH",
        "PROMOTE_MEMORY_TO_LEARNED_TRUTH",
        "SELECT_FINAL_TARGET",
        "MAKE_LINKING_DECISION",
        "PERFORM_RUNTIME_REASONING",
    ):
        if prohibition not in forbidden_mutations:
            raise SemanticMemoryError(
                "Required admission prohibition missing: "
                f"{prohibition}"
            )

    for flag in (
        "learning_engine_output_is_read_only",
        "dynamic_semantic_graph_is_read_only",
        "claim_integrity_is_read_only",
        "authority_is_read_only",
        "conflict_classification_is_read_only",
        "upstream_guard_disposition_is_read_only",
        "active_target_set_is_read_only",
        "semantic_memory_may_not_promote_truth",
        "semantic_memory_may_not_reason",
        "semantic_memory_may_not_select_targets",
        "semantic_memory_may_not_make_linking_decisions",
    ):
        if ownership_contract.get(flag) is not True:
            raise SemanticMemoryError(
                "Unsafe ownership contract state: "
                f"{flag}"
            )

    if not isinstance(
        inspection,
        dict,
    ):
        raise SemanticMemoryError(
            "Certified Learning Engine inspection is missing."
        )

    if (
        inspection.get("schema")
        != "semantic_memory_learning_engine_input_inspection_result_v1"
    ):
        raise SemanticMemoryError(
            "Invalid Learning Engine inspection schema."
        )

    eligible_ids = inspection.get(
        "downstream_eligible_relationship_ids"
    )

    held_ids = inspection.get(
        "held_relationship_ids"
    )

    blocked_ids = inspection.get(
        "blocked_relationship_ids"
    )

    for name, value in (
        (
            "downstream_eligible_relationship_ids",
            eligible_ids,
        ),
        (
            "held_relationship_ids",
            held_ids,
        ),
        (
            "blocked_relationship_ids",
            blocked_ids,
        ),
    ):
        if not isinstance(
            value,
            tuple,
        ):
            raise SemanticMemoryError(
                f"{name} must be a tuple."
            )

    eligible_set = set(
        eligible_ids
    )

    held_set = set(
        held_ids
    )

    blocked_set = set(
        blocked_ids
    )

    if eligible_set & held_set:
        raise SemanticMemoryError(
            "Eligible and held relationship sets overlap."
        )

    if eligible_set & blocked_set:
        raise SemanticMemoryError(
            "Eligible and blocked relationship sets overlap."
        )

    if held_set & blocked_set:
        raise SemanticMemoryError(
            "Held and blocked relationship sets overlap."
        )

    if not isinstance(
        boundaries,
        dict,
    ):
        raise SemanticMemoryError(
            "4.6.28D processing boundaries are missing."
        )

    if boundaries.get(
        "memory_ownership_mutation_contract_defined"
    ) is not True:
        raise SemanticMemoryError(
            "Memory ownership mutation contract was not defined."
        )

    for flag in (
        "semantic_memory_admission_performed",
        "semantic_memory_object_created",
        "semantic_memory_written",
        "memory_persistence_performed",
        "memory_version_created",
        "memory_supersession_performed",
        "memory_retention_decision_performed",
        "memory_retrieval_performed",
        "learning_output_promoted_to_truth",
        "graph_mutation_performed",
        "authority_rescored",
        "claim_integrity_redecided",
        "conflict_reclassified",
        "upstream_guard_disposition_changed",
        "target_created",
        "target_selected",
        "linking_decision_performed",
        "highlight_created",
    ):
        if boundaries.get(flag) is not False:
            raise SemanticMemoryError(
                "Unsafe pre-admission boundary state: "
                f"{flag}"
            )

    package_id = ownership_result.get(
        "source_final_learning_engine_package_id"
    )

    package_digest = ownership_result.get(
        "source_final_learning_engine_package_digest"
    )

    graph_id = ownership_result.get(
        "source_final_graph_id"
    )

    graph_digest = ownership_result.get(
        "source_final_graph_digest"
    )

    graph_snapshot_id = ownership_result.get(
        "source_graph_snapshot_id"
    )

    graph_lineage_root_id = ownership_result.get(
        "source_lineage_root_id"
    )

    learning_lineage_root_id = ownership_result.get(
        "source_learning_lineage_root_id"
    )

    for name, value in (
        (
            "source_final_learning_engine_package_id",
            package_id,
        ),
        (
            "source_final_learning_engine_package_digest",
            package_digest,
        ),
        (
            "source_final_graph_id",
            graph_id,
        ),
        (
            "source_final_graph_digest",
            graph_digest,
        ),
        (
            "source_graph_snapshot_id",
            graph_snapshot_id,
        ),
        (
            "source_lineage_root_id",
            graph_lineage_root_id,
        ),
        (
            "source_learning_lineage_root_id",
            learning_lineage_root_id,
        ),
    ):
        if not isinstance(
            value,
            str,
        ) or not value:
            raise SemanticMemoryError(
                "Missing admission provenance field: "
                f"{name}"
            )

    def build_admission_record(
        relationship_id: str,
        admission_state: str,
        source_partition: str,
    ) -> dict[str, Any]:

        if not isinstance(
            relationship_id,
            str,
        ) or not relationship_id:
            raise SemanticMemoryError(
                "Relationship ID must be a non-empty string."
            )

        payload = {
            "relationship_id":
                relationship_id,

            "admission_state":
                admission_state,

            "source_partition":
                source_partition,

            "source_learning_engine_package_id":
                package_id,

            "source_learning_lineage_root_id":
                learning_lineage_root_id,

            "source_final_graph_id":
                graph_id,

            "source_graph_snapshot_id":
                graph_snapshot_id,
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
                "semantic_memory_admission_record_v1",

            "admission_record_id":
                "semanticmemoryadmission:v1:"
                + digest,

            "admission_record_digest":
                digest,

            "source_learning_object_id":
                relationship_id,

            "source_partition":
                source_partition,

            "admission_state":
                admission_state,

            "source_learning_engine_package_id":
                package_id,

            "source_learning_engine_package_digest":
                package_digest,

            "source_learning_lineage_root_id":
                learning_lineage_root_id,

            "source_final_graph_id":
                graph_id,

            "source_final_graph_digest":
                graph_digest,

            "source_graph_snapshot_id":
                graph_snapshot_id,

            "source_graph_lineage_root_id":
                graph_lineage_root_id,

            "created_from_certified_learning":
                True,

            "is_certified_fact":
                False,

            "is_learned_truth":
                False,

            "memory_object_created":
                False,

            "memory_persisted":
                False,

            "learning_engine_output_mutated":
                False,

            "graph_mutated":
                False,

            "target_selected":
                False,

            "linking_decision_performed":
                False,
        }

    admissible_records = tuple(
        build_admission_record(
            relationship_id,
            "ADMISSIBLE",
            "DOWNSTREAM_ELIGIBLE",
        )
        for relationship_id in eligible_ids
    )

    held_records = tuple(
        build_admission_record(
            relationship_id,
            "HELD",
            "HELD",
        )
        for relationship_id in held_ids
    )

    blocked_records = tuple(
        build_admission_record(
            relationship_id,
            "BLOCKED",
            "BLOCKED",
        )
        for relationship_id in blocked_ids
    )

    all_records = (
        admissible_records
        + held_records
        + blocked_records
    )

    record_ids = tuple(
        record[
            "admission_record_id"
        ]
        for record in all_records
    )

    if len(
        record_ids
    ) != len(
        set(record_ids)
    ):
        raise SemanticMemoryError(
            "Duplicate Semantic Memory admission record IDs."
        )

    bundle_payload = {
        "admissible_record_ids":
            [
                item[
                    "admission_record_id"
                ]
                for item in admissible_records
            ],

        "held_record_ids":
            [
                item[
                    "admission_record_id"
                ]
                for item in held_records
            ],

        "blocked_record_ids":
            [
                item[
                    "admission_record_id"
                ]
                for item in blocked_records
            ],

        "source_learning_engine_package_id":
            package_id,

        "source_final_graph_id":
            graph_id,
    }

    bundle_serialized = json.dumps(
        bundle_payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    bundle_digest = hashlib.sha256(
        bundle_serialized.encode("utf-8")
    ).hexdigest()

    admission_bundle = {
        "schema":
            "semantic_memory_learned_knowledge_admission_bundle_v1",

        "admission_bundle_id":
            "semanticmemoryadmissionbundle:v1:"
            + bundle_digest,

        "admission_bundle_digest":
            bundle_digest,

        "admissible_records":
            admissible_records,

        "held_records":
            held_records,

        "blocked_records":
            blocked_records,

        "admissible_relationship_ids":
            tuple(
                eligible_ids
            ),

        "held_relationship_ids":
            tuple(
                held_ids
            ),

        "blocked_relationship_ids":
            tuple(
                blocked_ids
            ),

        "admissible_count":
            len(
                admissible_records
            ),

        "held_count":
            len(
                held_records
            ),

        "blocked_count":
            len(
                blocked_records
            ),

        "total_admission_record_count":
            len(
                all_records
            ),

        "admission_policy":
            "CERTIFIED_LEARNED_KNOWLEDGE_STATE_PRESERVING_ADMISSION_ONLY",

        "memory_objects_constructed":
            False,

        "memory_persisted":
            False,

        "truth_promotion_performed":
            False,

        "learning_engine_output_mutated":
            False,

        "graph_mutated":
            False,

        "target_selected":
            False,

        "linking_decision_performed":
            False,
    }

    return {
        "schema":
            "semantic_memory_learned_knowledge_admission_result_v1",

        "semantic_memory_version":
            SEMANTIC_MEMORY_VERSION,

        "phase":
            SEMANTIC_MEMORY_PHASE,

        "patch":
            "4.6.28E",

        "status":
            "LEARNED_KNOWLEDGE_ADMISSION_COMPLETED",

        "source_final_learning_engine_package_id":
            package_id,

        "source_final_learning_engine_package_digest":
            package_digest,

        "source_final_graph_id":
            graph_id,

        "source_final_graph_digest":
            graph_digest,

        "source_graph_snapshot_id":
            graph_snapshot_id,

        "source_lineage_root_id":
            graph_lineage_root_id,

        "source_learning_lineage_root_id":
            learning_lineage_root_id,

        "semantic_memory_ownership_mutation_contract":
            copy.deepcopy(
                ownership_contract
            ),

        "learned_knowledge_admission_bundle":
            admission_bundle,

        "certified_learning_engine_input_inspection":
            copy.deepcopy(
                inspection
            ),

        "processing_boundaries": {
            "semantic_memory_admission_performed":
                True,

            "semantic_memory_object_created":
                False,

            "semantic_memory_written":
                False,

            "memory_persistence_performed":
                False,

            "memory_version_created":
                False,

            "memory_supersession_performed":
                False,

            "memory_retention_decision_performed":
                False,

            "memory_retrieval_performed":
                False,

            "learning_output_promoted_to_truth":
                False,

            "learning_engine_output_mutated":
                False,

            "graph_mutation_performed":
                False,

            "authority_rescored":
                False,

            "claim_integrity_redecided":
                False,

            "conflict_reclassified":
                False,

            "upstream_guard_disposition_changed":
                False,

            "target_created":
                False,

            "target_selected":
                False,

            "linking_decision_performed":
                False,

            "highlight_created":
                False,
        },

        "policy":
            "CERTIFIED_LEARNED_KNOWLEDGE_ADMISSION",

        "next":
            "memory_object_construction",
    }

def construct_semantic_memory_objects_v1(
    admission_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.28F ? Memory Object Construction.

    Constructs Semantic Memory-owned memory objects from certified
    admission records without persisting them.

    ADMISSIBLE -> ACTIVE memory
    HELD       -> HELD memory
    BLOCKED    -> BLOCKED memory

    No persistence, versioning, supersession, retention decision,
    retrieval, truth promotion, target selection, or linking decision
    is performed here.
    """

    if not isinstance(
        admission_result,
        dict,
    ):
        raise SemanticMemoryError(
            "admission_result must be a dictionary."
        )

    expected = {
        "schema":
            "semantic_memory_learned_knowledge_admission_result_v1",

        "semantic_memory_version":
            SEMANTIC_MEMORY_VERSION,

        "phase":
            SEMANTIC_MEMORY_PHASE,

        "patch":
            "4.6.28E",

        "status":
            "LEARNED_KNOWLEDGE_ADMISSION_COMPLETED",

        "policy":
            "CERTIFIED_LEARNED_KNOWLEDGE_ADMISSION",

        "next":
            "memory_object_construction",
    }

    for key, expected_value in expected.items():

        if admission_result.get(key) != expected_value:
            raise SemanticMemoryError(
                "Invalid 4.6.28E lifecycle field: "
                f"{key}"
            )

    ownership_contract = admission_result.get(
        "semantic_memory_ownership_mutation_contract"
    )

    admission_bundle = admission_result.get(
        "learned_knowledge_admission_bundle"
    )

    inspection = admission_result.get(
        "certified_learning_engine_input_inspection"
    )

    boundaries = admission_result.get(
        "processing_boundaries"
    )

    if not isinstance(
        ownership_contract,
        dict,
    ):
        raise SemanticMemoryError(
            "Semantic Memory ownership contract is missing."
        )

    if (
        ownership_contract.get("schema")
        != "semantic_memory_ownership_mutation_contract_v1"
    ):
        raise SemanticMemoryError(
            "Invalid ownership contract schema."
        )

    allowed_mutations = ownership_contract.get(
        "allowed_memory_mutations"
    )

    if not isinstance(
        allowed_mutations,
        tuple,
    ):
        raise SemanticMemoryError(
            "Allowed memory mutations must be a tuple."
        )

    for permission in (
        "CREATE_MEMORY_OBJECT",
        "ATTACH_SOURCE_LEARNING_REFERENCE",
        "ATTACH_GRAPH_PROVENANCE_REFERENCE",
        "ATTACH_LINEAGE_REFERENCE",
        "SET_MEMORY_STATE",
        "SET_ADMISSION_STATE",
    ):
        if permission not in allowed_mutations:
            raise SemanticMemoryError(
                "Required memory construction permission missing: "
                f"{permission}"
            )

    forbidden_mutations = ownership_contract.get(
        "forbidden_memory_mutations"
    )

    if not isinstance(
        forbidden_mutations,
        tuple,
    ):
        raise SemanticMemoryError(
            "Forbidden memory mutations must be a tuple."
        )

    for prohibition in (
        "MUTATE_LEARNING_ENGINE_OUTPUT",
        "REWRITE_DYNAMIC_SEMANTIC_GRAPH",
        "PROMOTE_MEMORY_TO_CERTIFIED_TRUTH",
        "PROMOTE_MEMORY_TO_LEARNED_TRUTH",
        "SELECT_FINAL_TARGET",
        "MAKE_LINKING_DECISION",
        "PERFORM_RUNTIME_REASONING",
    ):
        if prohibition not in forbidden_mutations:
            raise SemanticMemoryError(
                "Required construction prohibition missing: "
                f"{prohibition}"
            )

    if not isinstance(
        admission_bundle,
        dict,
    ):
        raise SemanticMemoryError(
            "Learned knowledge admission bundle is missing."
        )

    if (
        admission_bundle.get("schema")
        != "semantic_memory_learned_knowledge_admission_bundle_v1"
    ):
        raise SemanticMemoryError(
            "Invalid learned knowledge admission bundle schema."
        )

    if (
        admission_bundle.get("admission_policy")
        != "CERTIFIED_LEARNED_KNOWLEDGE_STATE_PRESERVING_ADMISSION_ONLY"
    ):
        raise SemanticMemoryError(
            "Invalid learned knowledge admission policy."
        )

    for flag in (
        "memory_objects_constructed",
        "memory_persisted",
        "truth_promotion_performed",
        "learning_engine_output_mutated",
        "graph_mutated",
        "target_selected",
        "linking_decision_performed",
    ):
        if admission_bundle.get(flag) is not False:
            raise SemanticMemoryError(
                "Unsafe admission bundle state: "
                f"{flag}"
            )

    if not isinstance(
        boundaries,
        dict,
    ):
        raise SemanticMemoryError(
            "4.6.28E processing boundaries are missing."
        )

    if boundaries.get(
        "semantic_memory_admission_performed"
    ) is not True:
        raise SemanticMemoryError(
            "Semantic Memory admission has not completed."
        )

    for flag in (
        "semantic_memory_object_created",
        "semantic_memory_written",
        "memory_persistence_performed",
        "memory_version_created",
        "memory_supersession_performed",
        "memory_retention_decision_performed",
        "memory_retrieval_performed",
        "learning_output_promoted_to_truth",
        "learning_engine_output_mutated",
        "graph_mutation_performed",
        "authority_rescored",
        "claim_integrity_redecided",
        "conflict_reclassified",
        "upstream_guard_disposition_changed",
        "target_created",
        "target_selected",
        "linking_decision_performed",
        "highlight_created",
    ):
        if boundaries.get(flag) is not False:
            raise SemanticMemoryError(
                "Unsafe pre-construction boundary state: "
                f"{flag}"
            )

    if not isinstance(
        inspection,
        dict,
    ):
        raise SemanticMemoryError(
            "Certified Learning Engine inspection is missing."
        )

    package_id = admission_result.get(
        "source_final_learning_engine_package_id"
    )

    package_digest = admission_result.get(
        "source_final_learning_engine_package_digest"
    )

    graph_id = admission_result.get(
        "source_final_graph_id"
    )

    graph_digest = admission_result.get(
        "source_final_graph_digest"
    )

    graph_snapshot_id = admission_result.get(
        "source_graph_snapshot_id"
    )

    graph_lineage_root_id = admission_result.get(
        "source_lineage_root_id"
    )

    learning_lineage_root_id = admission_result.get(
        "source_learning_lineage_root_id"
    )

    for name, value in (
        (
            "source_final_learning_engine_package_id",
            package_id,
        ),
        (
            "source_final_learning_engine_package_digest",
            package_digest,
        ),
        (
            "source_final_graph_id",
            graph_id,
        ),
        (
            "source_final_graph_digest",
            graph_digest,
        ),
        (
            "source_graph_snapshot_id",
            graph_snapshot_id,
        ),
        (
            "source_lineage_root_id",
            graph_lineage_root_id,
        ),
        (
            "source_learning_lineage_root_id",
            learning_lineage_root_id,
        ),
    ):
        if not isinstance(
            value,
            str,
        ) or not value:
            raise SemanticMemoryError(
                "Missing memory construction provenance: "
                f"{name}"
            )

    admissible_records = admission_bundle.get(
        "admissible_records"
    )

    held_records = admission_bundle.get(
        "held_records"
    )

    blocked_records = admission_bundle.get(
        "blocked_records"
    )

    for name, value in (
        (
            "admissible_records",
            admissible_records,
        ),
        (
            "held_records",
            held_records,
        ),
        (
            "blocked_records",
            blocked_records,
        ),
    ):
        if not isinstance(
            value,
            tuple,
        ):
            raise SemanticMemoryError(
                f"{name} must be a tuple."
            )

    def validate_admission_record(
        record: dict[str, Any],
        expected_state: str,
    ) -> None:

        if not isinstance(
            record,
            dict,
        ):
            raise SemanticMemoryError(
                "Admission record must be a dictionary."
            )

        if (
            record.get("schema")
            != "semantic_memory_admission_record_v1"
        ):
            raise SemanticMemoryError(
                "Invalid admission record schema."
            )

        if record.get(
            "admission_state"
        ) != expected_state:
            raise SemanticMemoryError(
                "Admission record state mismatch."
            )

        if record.get(
            "created_from_certified_learning"
        ) is not True:
            raise SemanticMemoryError(
                "Admission record is not from certified learning."
            )

        for flag in (
            "is_certified_fact",
            "is_learned_truth",
            "memory_object_created",
            "memory_persisted",
            "learning_engine_output_mutated",
            "graph_mutated",
            "target_selected",
            "linking_decision_performed",
        ):
            if record.get(flag) is not False:
                raise SemanticMemoryError(
                    "Unsafe admission record state: "
                    f"{flag}"
                )

    for record in admissible_records:
        validate_admission_record(
            record,
            "ADMISSIBLE",
        )

    for record in held_records:
        validate_admission_record(
            record,
            "HELD",
        )

    for record in blocked_records:
        validate_admission_record(
            record,
            "BLOCKED",
        )

    def construct_memory_object(
        record: dict[str, Any],
        memory_state: str,
        retention_state: str,
    ) -> dict[str, Any]:

        source_learning_object_id = record.get(
            "source_learning_object_id"
        )

        admission_record_id = record.get(
            "admission_record_id"
        )

        if not isinstance(
            source_learning_object_id,
            str,
        ) or not source_learning_object_id:
            raise SemanticMemoryError(
                "Source learning object ID is missing."
            )

        if not isinstance(
            admission_record_id,
            str,
        ) or not admission_record_id:
            raise SemanticMemoryError(
                "Admission record ID is missing."
            )

        payload = {
            "source_learning_object_id":
                source_learning_object_id,

            "admission_record_id":
                admission_record_id,

            "memory_state":
                memory_state,

            "admission_state":
                record.get(
                    "admission_state"
                ),

            "source_learning_engine_package_id":
                package_id,

            "source_learning_lineage_root_id":
                learning_lineage_root_id,

            "source_final_graph_id":
                graph_id,

            "source_graph_snapshot_id":
                graph_snapshot_id,

            "version":
                1,
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
                "semantic_memory_object_v1",

            "memory_object_id":
                "semanticmemoryobject:v1:"
                + digest,

            "memory_object_digest":
                digest,

            "memory_object_type":
                "LEARNED_RELATIONSHIP_MEMORY",

            "memory_state":
                memory_state,

            "admission_state":
                record.get(
                    "admission_state"
                ),

            "retention_state":
                retention_state,

            "source_learning_object_id":
                source_learning_object_id,

            "source_admission_record_id":
                admission_record_id,

            "source_learning_engine_package_id":
                package_id,

            "source_learning_engine_package_digest":
                package_digest,

            "source_learning_lineage_root_id":
                learning_lineage_root_id,

            "source_final_graph_id":
                graph_id,

            "source_final_graph_digest":
                graph_digest,

            "source_graph_snapshot_id":
                graph_snapshot_id,

            "source_graph_lineage_root_id":
                graph_lineage_root_id,

            "provenance_references":
                (
                    admission_record_id,
                    package_id,
                    learning_lineage_root_id,
                    graph_id,
                    graph_snapshot_id,
                    graph_lineage_root_id,
                ),

            "version":
                1,

            "created_from_certified_learning":
                True,

            "is_certified_fact":
                False,

            "is_learned_truth":
                False,

            "semantic_memory_owned":
                True,

            "memory_persisted":
                False,

            "version_persisted":
                False,

            "supersession_performed":
                False,

            "retention_decision_finalized":
                False,

            "retrieval_metadata_created":
                False,

            "learning_engine_output_mutated":
                False,

            "graph_mutated":
                False,

            "target_selected":
                False,

            "linking_decision_performed":
                False,
        }

    active_memory_objects = tuple(
        construct_memory_object(
            record,
            "ACTIVE",
            "RETAIN",
        )
        for record in admissible_records
    )

    held_memory_objects = tuple(
        construct_memory_object(
            record,
            "HELD",
            "HOLD",
        )
        for record in held_records
    )

    blocked_memory_objects = tuple(
        construct_memory_object(
            record,
            "BLOCKED",
            "HOLD",
        )
        for record in blocked_records
    )

    all_memory_objects = (
        active_memory_objects
        + held_memory_objects
        + blocked_memory_objects
    )

    memory_object_ids = tuple(
        item[
            "memory_object_id"
        ]
        for item in all_memory_objects
    )

    if len(
        memory_object_ids
    ) != len(
        set(memory_object_ids)
    ):
        raise SemanticMemoryError(
            "Duplicate Semantic Memory object IDs."
        )

    bundle_payload = {
        "active_memory_object_ids":
            [
                item[
                    "memory_object_id"
                ]
                for item in active_memory_objects
            ],

        "held_memory_object_ids":
            [
                item[
                    "memory_object_id"
                ]
                for item in held_memory_objects
            ],

        "blocked_memory_object_ids":
            [
                item[
                    "memory_object_id"
                ]
                for item in blocked_memory_objects
            ],

        "source_admission_bundle_id":
            admission_bundle.get(
                "admission_bundle_id"
            ),

        "source_learning_engine_package_id":
            package_id,
    }

    bundle_serialized = json.dumps(
        bundle_payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    bundle_digest = hashlib.sha256(
        bundle_serialized.encode("utf-8")
    ).hexdigest()

    memory_object_bundle = {
        "schema":
            "semantic_memory_object_construction_bundle_v1",

        "memory_object_bundle_id":
            "semanticmemoryobjectbundle:v1:"
            + bundle_digest,

        "memory_object_bundle_digest":
            bundle_digest,

        "source_admission_bundle_id":
            admission_bundle.get(
                "admission_bundle_id"
            ),

        "active_memory_objects":
            active_memory_objects,

        "held_memory_objects":
            held_memory_objects,

        "blocked_memory_objects":
            blocked_memory_objects,

        "all_memory_objects":
            all_memory_objects,

        "active_count":
            len(
                active_memory_objects
            ),

        "held_count":
            len(
                held_memory_objects
            ),

        "blocked_count":
            len(
                blocked_memory_objects
            ),

        "total_memory_object_count":
            len(
                all_memory_objects
            ),

        "construction_policy":
            "CERTIFIED_ADMISSION_TO_NON_PERSISTED_SEMANTIC_MEMORY_OBJECTS",

        "memory_objects_constructed":
            True,

        "memory_persisted":
            False,

        "versioning_performed":
            False,

        "supersession_performed":
            False,

        "retention_decision_finalized":
            False,

        "retrieval_performed":
            False,

        "truth_promotion_performed":
            False,

        "learning_engine_output_mutated":
            False,

        "graph_mutated":
            False,

        "target_selected":
            False,

        "linking_decision_performed":
            False,
    }

    return {
        "schema":
            "semantic_memory_object_construction_result_v1",

        "semantic_memory_version":
            SEMANTIC_MEMORY_VERSION,

        "phase":
            SEMANTIC_MEMORY_PHASE,

        "patch":
            "4.6.28F",

        "status":
            "SEMANTIC_MEMORY_OBJECT_CONSTRUCTION_COMPLETED",

        "source_final_learning_engine_package_id":
            package_id,

        "source_final_learning_engine_package_digest":
            package_digest,

        "source_final_graph_id":
            graph_id,

        "source_final_graph_digest":
            graph_digest,

        "source_graph_snapshot_id":
            graph_snapshot_id,

        "source_lineage_root_id":
            graph_lineage_root_id,

        "source_learning_lineage_root_id":
            learning_lineage_root_id,

        "semantic_memory_ownership_mutation_contract":
            copy.deepcopy(
                ownership_contract
            ),

        "learned_knowledge_admission_bundle":
            copy.deepcopy(
                admission_bundle
            ),

        "semantic_memory_object_bundle":
            memory_object_bundle,

        "certified_learning_engine_input_inspection":
            copy.deepcopy(
                inspection
            ),

        "processing_boundaries": {
            "semantic_memory_admission_performed":
                True,

            "semantic_memory_object_created":
                True,

            "semantic_memory_written":
                False,

            "memory_persistence_performed":
                False,

            "memory_version_created":
                False,

            "memory_supersession_performed":
                False,

            "memory_retention_decision_performed":
                False,

            "memory_retrieval_performed":
                False,

            "learning_output_promoted_to_truth":
                False,

            "learning_engine_output_mutated":
                False,

            "graph_mutation_performed":
                False,

            "authority_rescored":
                False,

            "claim_integrity_redecided":
                False,

            "conflict_reclassified":
                False,

            "upstream_guard_disposition_changed":
                False,

            "target_created":
                False,

            "target_selected":
                False,

            "linking_decision_performed":
                False,

            "highlight_created":
                False,
        },

        "policy":
            "CERTIFIED_SEMANTIC_MEMORY_OBJECT_CONSTRUCTION",

        "next":
            "memory_versioning_and_supersession",
    }

def version_and_supersede_semantic_memory_v1(
    construction_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.28G ? Memory Versioning & Supersession.

    Creates deterministic initial version records for constructed
    Semantic Memory objects and establishes the canonical supersession
    contract.

    Newly constructed objects begin at version 1 and therefore do not
    supersede a previous version. No silent overwrite is permitted.

    This stage does not persist memory to durable storage.
    """

    if not isinstance(
        construction_result,
        dict,
    ):
        raise SemanticMemoryError(
            "construction_result must be a dictionary."
        )

    expected = {
        "schema":
            "semantic_memory_object_construction_result_v1",

        "semantic_memory_version":
            SEMANTIC_MEMORY_VERSION,

        "phase":
            SEMANTIC_MEMORY_PHASE,

        "patch":
            "4.6.28F",

        "status":
            "SEMANTIC_MEMORY_OBJECT_CONSTRUCTION_COMPLETED",

        "policy":
            "CERTIFIED_SEMANTIC_MEMORY_OBJECT_CONSTRUCTION",

        "next":
            "memory_versioning_and_supersession",
    }

    for key, expected_value in expected.items():

        if construction_result.get(key) != expected_value:
            raise SemanticMemoryError(
                "Invalid 4.6.28F lifecycle field: "
                f"{key}"
            )

    ownership_contract = construction_result.get(
        "semantic_memory_ownership_mutation_contract"
    )

    memory_bundle = construction_result.get(
        "semantic_memory_object_bundle"
    )

    admission_bundle = construction_result.get(
        "learned_knowledge_admission_bundle"
    )

    inspection = construction_result.get(
        "certified_learning_engine_input_inspection"
    )

    boundaries = construction_result.get(
        "processing_boundaries"
    )

    if not isinstance(
        ownership_contract,
        dict,
    ):
        raise SemanticMemoryError(
            "Semantic Memory ownership contract is missing."
        )

    if (
        ownership_contract.get("schema")
        != "semantic_memory_ownership_mutation_contract_v1"
    ):
        raise SemanticMemoryError(
            "Invalid ownership contract schema."
        )

    allowed_mutations = ownership_contract.get(
        "allowed_memory_mutations"
    )

    forbidden_mutations = ownership_contract.get(
        "forbidden_memory_mutations"
    )

    if not isinstance(
        allowed_mutations,
        tuple,
    ):
        raise SemanticMemoryError(
            "Allowed memory mutations must be a tuple."
        )

    if not isinstance(
        forbidden_mutations,
        tuple,
    ):
        raise SemanticMemoryError(
            "Forbidden memory mutations must be a tuple."
        )

    for permission in (
        "CREATE_MEMORY_VERSION",
        "PRESERVE_MEMORY_HISTORY",
        "SUPERSEDE_MEMORY_OBJECT",
        "SET_MEMORY_STATE",
    ):
        if permission not in allowed_mutations:
            raise SemanticMemoryError(
                "Required versioning permission missing: "
                f"{permission}"
            )

    for prohibition in (
        "MUTATE_LEARNING_ENGINE_OUTPUT",
        "REWRITE_DYNAMIC_SEMANTIC_GRAPH",
        "PROMOTE_MEMORY_TO_CERTIFIED_TRUTH",
        "PROMOTE_MEMORY_TO_LEARNED_TRUTH",
        "SELECT_FINAL_TARGET",
        "MAKE_LINKING_DECISION",
        "PERFORM_RUNTIME_REASONING",
    ):
        if prohibition not in forbidden_mutations:
            raise SemanticMemoryError(
                "Required versioning prohibition missing: "
                f"{prohibition}"
            )

    if not isinstance(
        memory_bundle,
        dict,
    ):
        raise SemanticMemoryError(
            "Semantic Memory object bundle is missing."
        )

    if (
        memory_bundle.get("schema")
        != "semantic_memory_object_construction_bundle_v1"
    ):
        raise SemanticMemoryError(
            "Invalid Semantic Memory object bundle schema."
        )

    if (
        memory_bundle.get("construction_policy")
        != "CERTIFIED_ADMISSION_TO_NON_PERSISTED_SEMANTIC_MEMORY_OBJECTS"
    ):
        raise SemanticMemoryError(
            "Invalid memory construction policy."
        )

    if memory_bundle.get(
        "memory_objects_constructed"
    ) is not True:
        raise SemanticMemoryError(
            "Memory objects have not been constructed."
        )

    for flag in (
        "memory_persisted",
        "versioning_performed",
        "supersession_performed",
        "retention_decision_finalized",
        "retrieval_performed",
        "truth_promotion_performed",
        "learning_engine_output_mutated",
        "graph_mutated",
        "target_selected",
        "linking_decision_performed",
    ):
        if memory_bundle.get(flag) is not False:
            raise SemanticMemoryError(
                "Unsafe pre-versioning bundle state: "
                f"{flag}"
            )

    if not isinstance(
        boundaries,
        dict,
    ):
        raise SemanticMemoryError(
            "4.6.28F processing boundaries are missing."
        )

    if boundaries.get(
        "semantic_memory_admission_performed"
    ) is not True:
        raise SemanticMemoryError(
            "Semantic Memory admission was not completed."
        )

    if boundaries.get(
        "semantic_memory_object_created"
    ) is not True:
        raise SemanticMemoryError(
            "Semantic Memory objects were not created."
        )

    for flag in (
        "semantic_memory_written",
        "memory_persistence_performed",
        "memory_version_created",
        "memory_supersession_performed",
        "memory_retention_decision_performed",
        "memory_retrieval_performed",
        "learning_output_promoted_to_truth",
        "learning_engine_output_mutated",
        "graph_mutation_performed",
        "authority_rescored",
        "claim_integrity_redecided",
        "conflict_reclassified",
        "upstream_guard_disposition_changed",
        "target_created",
        "target_selected",
        "linking_decision_performed",
        "highlight_created",
    ):
        if boundaries.get(flag) is not False:
            raise SemanticMemoryError(
                "Unsafe pre-versioning boundary state: "
                f"{flag}"
            )

    all_memory_objects = memory_bundle.get(
        "all_memory_objects"
    )

    if not isinstance(
        all_memory_objects,
        tuple,
    ):
        raise SemanticMemoryError(
            "all_memory_objects must be a tuple."
        )

    if not all_memory_objects:
        raise SemanticMemoryError(
            "No Semantic Memory objects are available for versioning."
        )

    package_id = construction_result.get(
        "source_final_learning_engine_package_id"
    )

    package_digest = construction_result.get(
        "source_final_learning_engine_package_digest"
    )

    graph_id = construction_result.get(
        "source_final_graph_id"
    )

    graph_digest = construction_result.get(
        "source_final_graph_digest"
    )

    graph_snapshot_id = construction_result.get(
        "source_graph_snapshot_id"
    )

    graph_lineage_root_id = construction_result.get(
        "source_lineage_root_id"
    )

    learning_lineage_root_id = construction_result.get(
        "source_learning_lineage_root_id"
    )

    for name, value in (
        (
            "source_final_learning_engine_package_id",
            package_id,
        ),
        (
            "source_final_learning_engine_package_digest",
            package_digest,
        ),
        (
            "source_final_graph_id",
            graph_id,
        ),
        (
            "source_final_graph_digest",
            graph_digest,
        ),
        (
            "source_graph_snapshot_id",
            graph_snapshot_id,
        ),
        (
            "source_lineage_root_id",
            graph_lineage_root_id,
        ),
        (
            "source_learning_lineage_root_id",
            learning_lineage_root_id,
        ),
    ):
        if not isinstance(
            value,
            str,
        ) or not value:
            raise SemanticMemoryError(
                "Missing versioning provenance field: "
                f"{name}"
            )

    def validate_memory_object(
        memory_object: dict[str, Any],
    ) -> None:

        if not isinstance(
            memory_object,
            dict,
        ):
            raise SemanticMemoryError(
                "Memory object must be a dictionary."
            )

        if (
            memory_object.get("schema")
            != "semantic_memory_object_v1"
        ):
            raise SemanticMemoryError(
                "Invalid memory object schema."
            )

        if memory_object.get(
            "semantic_memory_owned"
        ) is not True:
            raise SemanticMemoryError(
                "Memory object is not owned by Semantic Memory."
            )

        if memory_object.get(
            "created_from_certified_learning"
        ) is not True:
            raise SemanticMemoryError(
                "Memory object is not from certified learning."
            )

        if memory_object.get(
            "version"
        ) != 1:
            raise SemanticMemoryError(
                "New memory object must begin at version 1."
            )

        if memory_object.get(
            "memory_state"
        ) not in (
            "ACTIVE",
            "HELD",
            "BLOCKED",
        ):
            raise SemanticMemoryError(
                "Invalid initial memory state."
            )

        for flag in (
            "is_certified_fact",
            "is_learned_truth",
            "memory_persisted",
            "version_persisted",
            "supersession_performed",
            "retention_decision_finalized",
            "retrieval_metadata_created",
            "learning_engine_output_mutated",
            "graph_mutated",
            "target_selected",
            "linking_decision_performed",
        ):
            if memory_object.get(flag) is not False:
                raise SemanticMemoryError(
                    "Unsafe initial memory object state: "
                    f"{flag}"
                )

        provenance = memory_object.get(
            "provenance_references"
        )

        if not isinstance(
            provenance,
            tuple,
        ) or not provenance:
            raise SemanticMemoryError(
                "Memory object provenance is missing."
            )

    for memory_object in all_memory_objects:
        validate_memory_object(
            memory_object
        )

    source_learning_ids = tuple(
        memory_object.get(
            "source_learning_object_id"
        )
        for memory_object in all_memory_objects
    )

    if any(
        not isinstance(item, str)
        or not item
        for item in source_learning_ids
    ):
        raise SemanticMemoryError(
            "A source learning object ID is missing."
        )

    if len(
        source_learning_ids
    ) != len(
        set(source_learning_ids)
    ):
        raise SemanticMemoryError(
            "Multiple initial memory objects reference the same "
            "learning object. Silent overwrite is forbidden."
        )

    def create_initial_version_record(
        memory_object: dict[str, Any],
    ) -> dict[str, Any]:

        memory_object_id = memory_object.get(
            "memory_object_id"
        )

        memory_object_digest = memory_object.get(
            "memory_object_digest"
        )

        source_learning_object_id = memory_object.get(
            "source_learning_object_id"
        )

        if not isinstance(
            memory_object_id,
            str,
        ) or not memory_object_id:
            raise SemanticMemoryError(
                "Memory object ID is missing."
            )

        if not isinstance(
            memory_object_digest,
            str,
        ) or not memory_object_digest:
            raise SemanticMemoryError(
                "Memory object digest is missing."
            )

        payload = {
            "memory_object_id":
                memory_object_id,

            "memory_object_digest":
                memory_object_digest,

            "source_learning_object_id":
                source_learning_object_id,

            "version":
                1,

            "previous_version_record_id":
                None,

            "supersedes_memory_object_id":
                None,

            "memory_state":
                memory_object.get(
                    "memory_state"
                ),

            "admission_state":
                memory_object.get(
                    "admission_state"
                ),

            "retention_state":
                memory_object.get(
                    "retention_state"
                ),

            "source_learning_engine_package_id":
                package_id,

            "source_final_graph_id":
                graph_id,

            "source_graph_snapshot_id":
                graph_snapshot_id,
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
                "semantic_memory_version_record_v1",

            "memory_version_record_id":
                "semanticmemoryversion:v1:"
                + digest,

            "memory_version_record_digest":
                digest,

            "memory_object_id":
                memory_object_id,

            "memory_object_digest":
                memory_object_digest,

            "source_learning_object_id":
                source_learning_object_id,

            "version":
                1,

            "is_initial_version":
                True,

            "is_current_version":
                True,

            "previous_version_record_id":
                None,

            "supersedes_memory_object_id":
                None,

            "superseded_by_memory_object_id":
                None,

            "supersession_state":
                "NOT_SUPERSEDED",

            "memory_state":
                memory_object.get(
                    "memory_state"
                ),

            "admission_state":
                memory_object.get(
                    "admission_state"
                ),

            "retention_state":
                memory_object.get(
                    "retention_state"
                ),

            "source_learning_engine_package_id":
                package_id,

            "source_learning_engine_package_digest":
                package_digest,

            "source_learning_lineage_root_id":
                learning_lineage_root_id,

            "source_final_graph_id":
                graph_id,

            "source_final_graph_digest":
                graph_digest,

            "source_graph_snapshot_id":
                graph_snapshot_id,

            "source_graph_lineage_root_id":
                graph_lineage_root_id,

            "provenance_references":
                tuple(
                    memory_object.get(
                        "provenance_references"
                    )
                ),

            "created_from_certified_learning":
                True,

            "is_certified_fact":
                False,

            "is_learned_truth":
                False,

            "history_preserved":
                True,

            "silent_overwrite_performed":
                False,

            "version_persisted":
                False,

            "memory_persisted":
                False,

            "learning_engine_output_mutated":
                False,

            "graph_mutated":
                False,

            "target_selected":
                False,

            "linking_decision_performed":
                False,
        }

    version_records = tuple(
        create_initial_version_record(
            memory_object
        )
        for memory_object in all_memory_objects
    )

    version_record_ids = tuple(
        record[
            "memory_version_record_id"
        ]
        for record in version_records
    )

    if len(
        version_record_ids
    ) != len(
        set(version_record_ids)
    ):
        raise SemanticMemoryError(
            "Duplicate Semantic Memory version record IDs."
        )

    versioned_memory_objects = tuple(
        {
            **copy.deepcopy(memory_object),

            "current_version":
                1,

            "current_version_record_id":
                version_record[
                    "memory_version_record_id"
                ],

            "versioning_performed":
                True,

            "history_preserved":
                True,

            "supersession_state":
                "NOT_SUPERSEDED",

            "supersedes_memory_object_id":
                None,

            "superseded_by_memory_object_id":
                None,

            "silent_overwrite_performed":
                False,

            "memory_persisted":
                False,

            "version_persisted":
                False,
        }
        for memory_object, version_record in zip(
            all_memory_objects,
            version_records,
        )
    )

    supersession_contract = {
        "schema":
            "semantic_memory_supersession_contract_v1",

        "silent_overwrite_forbidden":
            True,

        "new_memory_starts_at_version_one":
            True,

        "future_revision_requires_new_version":
            True,

        "future_revision_must_reference_previous_version":
            True,

        "superseded_versions_must_remain_historical":
            True,

        "superseded_version_must_not_be_deleted":
            True,

        "supersession_requires_same_semantic_memory_lineage":
            True,

        "supersession_requires_provenance_preservation":
            True,

        "supersession_does_not_create_truth":
            True,

        "supersession_does_not_mutate_learning_engine":
            True,

        "supersession_does_not_mutate_graph":
            True,

        "supersession_does_not_select_targets":
            True,

        "supersession_does_not_make_linking_decisions":
            True,
    }

    bundle_payload = {
        "memory_object_ids":
            [
                item[
                    "memory_object_id"
                ]
                for item in versioned_memory_objects
            ],

        "memory_version_record_ids":
            list(
                version_record_ids
            ),

        "source_memory_object_bundle_id":
            memory_bundle.get(
                "memory_object_bundle_id"
            ),

        "source_learning_engine_package_id":
            package_id,

        "version":
            1,
    }

    bundle_serialized = json.dumps(
        bundle_payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    bundle_digest = hashlib.sha256(
        bundle_serialized.encode("utf-8")
    ).hexdigest()

    versioning_bundle = {
        "schema":
            "semantic_memory_versioning_supersession_bundle_v1",

        "versioning_bundle_id":
            "semanticmemoryversionbundle:v1:"
            + bundle_digest,

        "versioning_bundle_digest":
            bundle_digest,

        "source_memory_object_bundle_id":
            memory_bundle.get(
                "memory_object_bundle_id"
            ),

        "versioned_memory_objects":
            versioned_memory_objects,

        "version_records":
            version_records,

        "supersession_records":
            (),

        "supersession_contract":
            supersession_contract,

        "initial_version_count":
            len(
                version_records
            ),

        "supersession_count":
            0,

        "versioning_policy":
            "VERSIONED_SEMANTIC_MEMORY_WITH_HISTORY_AND_NO_SILENT_OVERWRITE",

        "versioning_performed":
            True,

        "initial_versions_created":
            True,

        "supersession_supported":
            True,

        "supersession_performed":
            False,

        "history_preserved":
            True,

        "silent_overwrite_performed":
            False,

        "memory_persisted":
            False,

        "version_records_persisted":
            False,

        "retention_decision_finalized":
            False,

        "retrieval_performed":
            False,

        "truth_promotion_performed":
            False,

        "learning_engine_output_mutated":
            False,

        "graph_mutated":
            False,

        "target_selected":
            False,

        "linking_decision_performed":
            False,
    }

    return {
        "schema":
            "semantic_memory_versioning_supersession_result_v1",

        "semantic_memory_version":
            SEMANTIC_MEMORY_VERSION,

        "phase":
            SEMANTIC_MEMORY_PHASE,

        "patch":
            "4.6.28G",

        "status":
            "SEMANTIC_MEMORY_VERSIONING_SUPERSESSION_COMPLETED",

        "source_final_learning_engine_package_id":
            package_id,

        "source_final_learning_engine_package_digest":
            package_digest,

        "source_final_graph_id":
            graph_id,

        "source_final_graph_digest":
            graph_digest,

        "source_graph_snapshot_id":
            graph_snapshot_id,

        "source_lineage_root_id":
            graph_lineage_root_id,

        "source_learning_lineage_root_id":
            learning_lineage_root_id,

        "semantic_memory_ownership_mutation_contract":
            copy.deepcopy(
                ownership_contract
            ),

        "learned_knowledge_admission_bundle":
            copy.deepcopy(
                admission_bundle
            ),

        "semantic_memory_object_bundle":
            copy.deepcopy(
                memory_bundle
            ),

        "semantic_memory_versioning_supersession_bundle":
            versioning_bundle,

        "certified_learning_engine_input_inspection":
            copy.deepcopy(
                inspection
            ),

        "processing_boundaries": {
            "semantic_memory_admission_performed":
                True,

            "semantic_memory_object_created":
                True,

            "semantic_memory_written":
                False,

            "memory_persistence_performed":
                False,

            "memory_version_created":
                True,

            "memory_supersession_performed":
                False,

            "memory_retention_decision_performed":
                False,

            "memory_retrieval_performed":
                False,

            "learning_output_promoted_to_truth":
                False,

            "learning_engine_output_mutated":
                False,

            "graph_mutation_performed":
                False,

            "authority_rescored":
                False,

            "claim_integrity_redecided":
                False,

            "conflict_reclassified":
                False,

            "upstream_guard_disposition_changed":
                False,

            "target_created":
                False,

            "target_selected":
                False,

            "linking_decision_performed":
                False,

            "highlight_created":
                False,
        },

        "policy":
            "CERTIFIED_SEMANTIC_MEMORY_VERSIONING_SUPERSESSION",

        "next":
            "conflict_exception_memory_preservation",
    }

def preserve_conflict_exception_memory_v1(
    versioning_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.28H ? Conflict / Exception Memory Preservation.

    Preserves certified Learning Engine conflict and exception context
    in Semantic Memory without resolving, suppressing, reclassifying,
    or promoting any upstream semantic conclusion.

    Conflict and exception context remains evidence-bound, historical,
    provenance-preserving, and explicitly non-truth.
    """

    if not isinstance(
        versioning_result,
        dict,
    ):
        raise SemanticMemoryError(
            "versioning_result must be a dictionary."
        )

    expected = {
        "schema":
            "semantic_memory_versioning_supersession_result_v1",

        "semantic_memory_version":
            SEMANTIC_MEMORY_VERSION,

        "phase":
            SEMANTIC_MEMORY_PHASE,

        "patch":
            "4.6.28G",

        "status":
            "SEMANTIC_MEMORY_VERSIONING_SUPERSESSION_COMPLETED",

        "policy":
            "CERTIFIED_SEMANTIC_MEMORY_VERSIONING_SUPERSESSION",

        "next":
            "conflict_exception_memory_preservation",
    }

    for key, expected_value in expected.items():

        if versioning_result.get(key) != expected_value:
            raise SemanticMemoryError(
                "Invalid 4.6.28G lifecycle field: "
                f"{key}"
            )

    ownership_contract = versioning_result.get(
        "semantic_memory_ownership_mutation_contract"
    )

    versioning_bundle = versioning_result.get(
        "semantic_memory_versioning_supersession_bundle"
    )

    inspection = versioning_result.get(
        "certified_learning_engine_input_inspection"
    )

    boundaries = versioning_result.get(
        "processing_boundaries"
    )

    if not isinstance(
        ownership_contract,
        dict,
    ):
        raise SemanticMemoryError(
            "Semantic Memory ownership contract is missing."
        )

    if (
        ownership_contract.get("schema")
        != "semantic_memory_ownership_mutation_contract_v1"
    ):
        raise SemanticMemoryError(
            "Invalid ownership contract schema."
        )

    allowed_mutations = ownership_contract.get(
        "allowed_memory_mutations"
    )

    forbidden_mutations = ownership_contract.get(
        "forbidden_memory_mutations"
    )

    if not isinstance(
        allowed_mutations,
        tuple,
    ):
        raise SemanticMemoryError(
            "Allowed memory mutations must be a tuple."
        )

    if not isinstance(
        forbidden_mutations,
        tuple,
    ):
        raise SemanticMemoryError(
            "Forbidden memory mutations must be a tuple."
        )

    for permission in (
        "REGISTER_CONFLICT_MEMORY",
        "REGISTER_EXCEPTION_MEMORY",
        "PRESERVE_MEMORY_HISTORY",
        "ATTACH_LEARNING_PROVENANCE_REFERENCE",
        "ATTACH_LINEAGE_REFERENCE",
    ):
        if permission not in allowed_mutations:
            raise SemanticMemoryError(
                "Required conflict/exception permission missing: "
                f"{permission}"
            )

    for prohibition in (
        "MUTATE_LEARNING_ENGINE_OUTPUT",
        "RECLASSIFY_UPSTREAM_CONFLICT",
        "REWRITE_DYNAMIC_SEMANTIC_GRAPH",
        "PROMOTE_MEMORY_TO_CERTIFIED_TRUTH",
        "PROMOTE_MEMORY_TO_LEARNED_TRUTH",
        "SELECT_FINAL_TARGET",
        "MAKE_LINKING_DECISION",
        "PERFORM_RUNTIME_REASONING",
    ):
        if prohibition not in forbidden_mutations:
            raise SemanticMemoryError(
                "Required conflict/exception prohibition missing: "
                f"{prohibition}"
            )

    if ownership_contract.get(
        "conflict_classification_is_read_only"
    ) is not True:
        raise SemanticMemoryError(
            "Conflict classification must remain read-only."
        )

    if not isinstance(
        versioning_bundle,
        dict,
    ):
        raise SemanticMemoryError(
            "Semantic Memory versioning bundle is missing."
        )

    if (
        versioning_bundle.get("schema")
        != "semantic_memory_versioning_supersession_bundle_v1"
    ):
        raise SemanticMemoryError(
            "Invalid Semantic Memory versioning bundle schema."
        )

    if (
        versioning_bundle.get("versioning_policy")
        != "VERSIONED_SEMANTIC_MEMORY_WITH_HISTORY_AND_NO_SILENT_OVERWRITE"
    ):
        raise SemanticMemoryError(
            "Invalid Semantic Memory versioning policy."
        )

    if versioning_bundle.get(
        "versioning_performed"
    ) is not True:
        raise SemanticMemoryError(
            "Semantic Memory versioning has not completed."
        )

    if versioning_bundle.get(
        "history_preserved"
    ) is not True:
        raise SemanticMemoryError(
            "Semantic Memory history was not preserved."
        )

    if versioning_bundle.get(
        "silent_overwrite_performed"
    ) is not False:
        raise SemanticMemoryError(
            "Silent overwrite is forbidden."
        )

    for flag in (
        "memory_persisted",
        "version_records_persisted",
        "retention_decision_finalized",
        "retrieval_performed",
        "truth_promotion_performed",
        "learning_engine_output_mutated",
        "graph_mutated",
        "target_selected",
        "linking_decision_performed",
    ):
        if versioning_bundle.get(flag) is not False:
            raise SemanticMemoryError(
                "Unsafe pre-preservation versioning state: "
                f"{flag}"
            )

    if not isinstance(
        boundaries,
        dict,
    ):
        raise SemanticMemoryError(
            "4.6.28G processing boundaries are missing."
        )

    if boundaries.get(
        "semantic_memory_admission_performed"
    ) is not True:
        raise SemanticMemoryError(
            "Semantic Memory admission was not completed."
        )

    if boundaries.get(
        "semantic_memory_object_created"
    ) is not True:
        raise SemanticMemoryError(
            "Semantic Memory objects were not created."
        )

    if boundaries.get(
        "memory_version_created"
    ) is not True:
        raise SemanticMemoryError(
            "Semantic Memory versioning was not completed."
        )

    for flag in (
        "semantic_memory_written",
        "memory_persistence_performed",
        "memory_supersession_performed",
        "memory_retention_decision_performed",
        "memory_retrieval_performed",
        "learning_output_promoted_to_truth",
        "learning_engine_output_mutated",
        "graph_mutation_performed",
        "authority_rescored",
        "claim_integrity_redecided",
        "conflict_reclassified",
        "upstream_guard_disposition_changed",
        "target_created",
        "target_selected",
        "linking_decision_performed",
        "highlight_created",
    ):
        if boundaries.get(flag) is not False:
            raise SemanticMemoryError(
                "Unsafe pre-preservation boundary state: "
                f"{flag}"
            )

    if not isinstance(
        inspection,
        dict,
    ):
        raise SemanticMemoryError(
            "Certified Learning Engine inspection is missing."
        )

    if (
        inspection.get("schema")
        != "semantic_memory_learning_engine_input_inspection_result_v1"
    ):
        raise SemanticMemoryError(
            "Invalid Learning Engine inspection schema."
        )

    certified_input = inspection.get(
        "certified_learning_engine_input"
    )

    if not isinstance(
        certified_input,
        dict,
    ):
        raise SemanticMemoryError(
            "Certified Learning Engine input is missing."
        )

    if (
        certified_input.get("schema")
        != "full_learning_engine_hard_certification_result_v1"
    ):
        raise SemanticMemoryError(
            "Invalid Learning Engine certification schema."
        )

    if certified_input.get(
        "certified"
    ) is not True:
        raise SemanticMemoryError(
            "Learning Engine input is not hard-certified."
        )

    final_result = certified_input.get(
        "final_learning_engine_result"
    )

    if not isinstance(
        final_result,
        dict,
    ):
        raise SemanticMemoryError(
            "Final Learning Engine result is missing."
        )

    if (
        final_result.get("schema")
        != "final_learning_engine_result_v1"
    ):
        raise SemanticMemoryError(
            "Invalid final Learning Engine result schema."
        )

    final_package = final_result.get(
        "final_learning_engine_package"
    )

    if not isinstance(
        final_package,
        dict,
    ):
        raise SemanticMemoryError(
            "Final Learning Engine package is missing."
        )

    if (
        final_package.get("schema")
        != "final_learning_engine_package_v1"
    ):
        raise SemanticMemoryError(
            "Invalid final Learning Engine package schema."
        )

    if (
        final_package.get("final_policy")
        != "CERTIFIED_LEARNING_ENGINE_OUTPUT_FOR_SEMANTIC_MEMORY_HANDOFF"
    ):
        raise SemanticMemoryError(
            "Invalid final Learning Engine package policy."
        )

    conflict_exception_bundle = final_package.get(
        "conflict_exception_learning_bundle"
    )

    if not isinstance(
        conflict_exception_bundle,
        dict,
    ):
        raise SemanticMemoryError(
            "Certified conflict/exception learning bundle is missing."
        )

    source_bundle_copy = copy.deepcopy(
        conflict_exception_bundle
    )

    serialized_source_bundle = json.dumps(
        source_bundle_copy,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    )

    source_bundle_digest = hashlib.sha256(
        serialized_source_bundle.encode("utf-8")
    ).hexdigest()

    source_bundle_reference_id = (
        "learningconflictexception:v1:"
        + source_bundle_digest
    )

    versioned_memory_objects = versioning_bundle.get(
        "versioned_memory_objects"
    )

    version_records = versioning_bundle.get(
        "version_records"
    )

    if not isinstance(
        versioned_memory_objects,
        tuple,
    ):
        raise SemanticMemoryError(
            "versioned_memory_objects must be a tuple."
        )

    if not isinstance(
        version_records,
        tuple,
    ):
        raise SemanticMemoryError(
            "version_records must be a tuple."
        )

    if len(
        versioned_memory_objects
    ) != len(
        version_records
    ):
        raise SemanticMemoryError(
            "Memory object/version record count mismatch."
        )

    if not versioned_memory_objects:
        raise SemanticMemoryError(
            "No versioned memory objects are available."
        )

    version_record_by_object_id = {}

    for record in version_records:

        if not isinstance(
            record,
            dict,
        ):
            raise SemanticMemoryError(
                "Version record must be a dictionary."
            )

        if (
            record.get("schema")
            != "semantic_memory_version_record_v1"
        ):
            raise SemanticMemoryError(
                "Invalid version record schema."
            )

        memory_object_id = record.get(
            "memory_object_id"
        )

        if not isinstance(
            memory_object_id,
            str,
        ) or not memory_object_id:
            raise SemanticMemoryError(
                "Version record memory object ID is missing."
            )

        if memory_object_id in version_record_by_object_id:
            raise SemanticMemoryError(
                "Duplicate version record for memory object."
            )

        version_record_by_object_id[
            memory_object_id
        ] = record

    def preserve_for_memory_object(
        memory_object: dict[str, Any],
    ) -> dict[str, Any]:

        if not isinstance(
            memory_object,
            dict,
        ):
            raise SemanticMemoryError(
                "Versioned memory object must be a dictionary."
            )

        if (
            memory_object.get("schema")
            != "semantic_memory_object_v1"
        ):
            raise SemanticMemoryError(
                "Invalid Semantic Memory object schema."
            )

        if memory_object.get(
            "versioning_performed"
        ) is not True:
            raise SemanticMemoryError(
                "Memory object has not been versioned."
            )

        if memory_object.get(
            "history_preserved"
        ) is not True:
            raise SemanticMemoryError(
                "Memory object history is not preserved."
            )

        if memory_object.get(
            "memory_persisted"
        ) is not False:
            raise SemanticMemoryError(
                "Memory persistence occurred too early."
            )

        if memory_object.get(
            "is_certified_fact"
        ) is not False:
            raise SemanticMemoryError(
                "Memory object cannot be certified fact."
            )

        if memory_object.get(
            "is_learned_truth"
        ) is not False:
            raise SemanticMemoryError(
                "Memory object cannot be learned truth."
            )

        memory_object_id = memory_object.get(
            "memory_object_id"
        )

        if memory_object_id not in version_record_by_object_id:
            raise SemanticMemoryError(
                "Version record is missing for memory object."
            )

        version_record = version_record_by_object_id[
            memory_object_id
        ]

        payload = {
            "memory_object_id":
                memory_object_id,

            "memory_version_record_id":
                version_record.get(
                    "memory_version_record_id"
                ),

            "source_learning_object_id":
                memory_object.get(
                    "source_learning_object_id"
                ),

            "source_conflict_exception_bundle_reference_id":
                source_bundle_reference_id,

            "source_conflict_exception_bundle_digest":
                source_bundle_digest,

            "memory_state":
                memory_object.get(
                    "memory_state"
                ),

            "version":
                memory_object.get(
                    "current_version"
                ),
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
                "semantic_memory_conflict_exception_preservation_record_v1",

            "preservation_record_id":
                "semanticmemoryconflictexception:v1:"
                + digest,

            "preservation_record_digest":
                digest,

            "memory_object_id":
                memory_object_id,

            "memory_version_record_id":
                version_record.get(
                    "memory_version_record_id"
                ),

            "source_learning_object_id":
                memory_object.get(
                    "source_learning_object_id"
                ),

            "source_conflict_exception_bundle_reference_id":
                source_bundle_reference_id,

            "source_conflict_exception_bundle_digest":
                source_bundle_digest,

            "memory_state":
                memory_object.get(
                    "memory_state"
                ),

            "memory_version":
                memory_object.get(
                    "current_version"
                ),

            "conflict_context_preserved":
                True,

            "exception_context_preserved":
                True,

            "minority_patterns_preserved":
                True,

            "unresolved_state_preserved":
                True,

            "contested_state_preserved":
                True,

            "upstream_conflict_reclassified":
                False,

            "conflict_resolved":
                False,

            "exception_normalized_away":
                False,

            "minority_pattern_suppressed":
                False,

            "truth_adjudicated":
                False,

            "is_certified_fact":
                False,

            "is_learned_truth":
                False,

            "memory_persisted":
                False,

            "learning_engine_output_mutated":
                False,

            "graph_mutated":
                False,

            "target_selected":
                False,

            "linking_decision_performed":
                False,
        }

    preservation_records = tuple(
        preserve_for_memory_object(
            memory_object
        )
        for memory_object in versioned_memory_objects
    )

    preservation_record_ids = tuple(
        record[
            "preservation_record_id"
        ]
        for record in preservation_records
    )

    if len(
        preservation_record_ids
    ) != len(
        set(preservation_record_ids)
    ):
        raise SemanticMemoryError(
            "Duplicate conflict/exception preservation record IDs."
        )

    preserved_memory_objects = tuple(
        {
            **copy.deepcopy(memory_object),

            "conflict_exception_context_preserved":
                True,

            "conflict_exception_preservation_record_id":
                preservation_record[
                    "preservation_record_id"
                ],

            "source_conflict_exception_bundle_reference_id":
                source_bundle_reference_id,

            "source_conflict_exception_bundle_digest":
                source_bundle_digest,

            "upstream_conflict_reclassified":
                False,

            "truth_adjudicated":
                False,

            "memory_persisted":
                False,
        }
        for memory_object, preservation_record in zip(
            versioned_memory_objects,
            preservation_records,
        )
    )

    preservation_contract = {
        "schema":
            "semantic_memory_conflict_exception_preservation_contract_v1",

        "conflicts_are_first_class_memory_context":
            True,

        "exceptions_are_first_class_memory_context":
            True,

        "contested_patterns_must_be_preserved":
            True,

        "minority_patterns_must_be_preserved":
            True,

        "unresolved_conflict_must_remain_unresolved":
            True,

        "upstream_conflict_classification_is_read_only":
            True,

        "upstream_exception_classification_is_read_only":
            True,

        "conflict_presence_does_not_establish_truth":
            True,

        "exception_presence_does_not_establish_falsehood":
            True,

        "authority_does_not_resolve_conflict":
            True,

        "frequency_does_not_resolve_conflict":
            True,

        "memory_must_not_suppress_minority_pattern":
            True,

        "memory_must_not_normalize_exception_away":
            True,

        "memory_must_not_adjudicate_truth":
            True,

        "history_must_be_preserved":
            True,

        "provenance_must_be_preserved":
            True,
    }

    bundle_payload = {
        "source_versioning_bundle_id":
            versioning_bundle.get(
                "versioning_bundle_id"
            ),

        "source_conflict_exception_bundle_reference_id":
            source_bundle_reference_id,

        "preservation_record_ids":
            list(
                preservation_record_ids
            ),

        "memory_object_ids":
            [
                item[
                    "memory_object_id"
                ]
                for item in preserved_memory_objects
            ],
    }

    bundle_serialized = json.dumps(
        bundle_payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    bundle_digest = hashlib.sha256(
        bundle_serialized.encode("utf-8")
    ).hexdigest()

    preservation_bundle = {
        "schema":
            "semantic_memory_conflict_exception_preservation_bundle_v1",

        "preservation_bundle_id":
            "semanticmemoryconflictexceptionbundle:v1:"
            + bundle_digest,

        "preservation_bundle_digest":
            bundle_digest,

        "source_versioning_bundle_id":
            versioning_bundle.get(
                "versioning_bundle_id"
            ),

        "source_conflict_exception_bundle_reference_id":
            source_bundle_reference_id,

        "source_conflict_exception_bundle_digest":
            source_bundle_digest,

        "certified_source_conflict_exception_bundle":
            source_bundle_copy,

        "preservation_records":
            preservation_records,

        "preserved_memory_objects":
            preserved_memory_objects,

        "preservation_contract":
            preservation_contract,

        "preservation_record_count":
            len(
                preservation_records
            ),

        "preservation_policy":
            "PRESERVE_CERTIFIED_CONFLICT_EXCEPTION_CONTEXT_WITHOUT_RECLASSIFICATION_OR_TRUTH_ADJUDICATION",

        "conflict_context_preserved":
            True,

        "exception_context_preserved":
            True,

        "minority_patterns_preserved":
            True,

        "unresolved_context_preserved":
            True,

        "upstream_conflict_reclassified":
            False,

        "truth_adjudicated":
            False,

        "memory_persisted":
            False,

        "retention_decision_finalized":
            False,

        "retrieval_performed":
            False,

        "learning_engine_output_mutated":
            False,

        "graph_mutated":
            False,

        "target_selected":
            False,

        "linking_decision_performed":
            False,
    }

    return {
        "schema":
            "semantic_memory_conflict_exception_preservation_result_v1",

        "semantic_memory_version":
            SEMANTIC_MEMORY_VERSION,

        "phase":
            SEMANTIC_MEMORY_PHASE,

        "patch":
            "4.6.28H",

        "status":
            "SEMANTIC_MEMORY_CONFLICT_EXCEPTION_PRESERVED",

        "source_final_learning_engine_package_id":
            versioning_result.get(
                "source_final_learning_engine_package_id"
            ),

        "source_final_learning_engine_package_digest":
            versioning_result.get(
                "source_final_learning_engine_package_digest"
            ),

        "source_final_graph_id":
            versioning_result.get(
                "source_final_graph_id"
            ),

        "source_final_graph_digest":
            versioning_result.get(
                "source_final_graph_digest"
            ),

        "source_graph_snapshot_id":
            versioning_result.get(
                "source_graph_snapshot_id"
            ),

        "source_lineage_root_id":
            versioning_result.get(
                "source_lineage_root_id"
            ),

        "source_learning_lineage_root_id":
            versioning_result.get(
                "source_learning_lineage_root_id"
            ),

        "semantic_memory_ownership_mutation_contract":
            copy.deepcopy(
                ownership_contract
            ),

        "semantic_memory_versioning_supersession_bundle":
            copy.deepcopy(
                versioning_bundle
            ),

        "semantic_memory_conflict_exception_preservation_bundle":
            preservation_bundle,

        "certified_learning_engine_input_inspection":
            copy.deepcopy(
                inspection
            ),

        "processing_boundaries": {
            "semantic_memory_admission_performed":
                True,

            "semantic_memory_object_created":
                True,

            "memory_version_created":
                True,

            "conflict_exception_memory_preserved":
                True,

            "semantic_memory_written":
                False,

            "memory_persistence_performed":
                False,

            "memory_supersession_performed":
                False,

            "memory_retention_decision_performed":
                False,

            "memory_retrieval_performed":
                False,

            "learning_output_promoted_to_truth":
                False,

            "learning_engine_output_mutated":
                False,

            "graph_mutation_performed":
                False,

            "authority_rescored":
                False,

            "claim_integrity_redecided":
                False,

            "conflict_reclassified":
                False,

            "upstream_guard_disposition_changed":
                False,

            "target_created":
                False,

            "target_selected":
                False,

            "linking_decision_performed":
                False,

            "highlight_created":
                False,
        },

        "policy":
            "CERTIFIED_SEMANTIC_MEMORY_CONFLICT_EXCEPTION_PRESERVATION",

        "next":
            "memory_stability_and_retention",
    }

def apply_semantic_memory_stability_retention_v1(
    preservation_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.28I ? Memory Stability & Retention.

    Applies Semantic Memory-owned stability and retention decisions
    to conflict/exception-preserving memory objects.

    This stage does not rewrite Learning Engine stability, upstream
    conflict classification, certified graph state, or truth.

    ACTIVE  -> RETAIN
    HELD    -> HOLD
    BLOCKED -> HOLD

    Historical/versioned memory remains preserved.
    """

    if not isinstance(
        preservation_result,
        dict,
    ):
        raise SemanticMemoryError(
            "preservation_result must be a dictionary."
        )

    expected = {
        "schema":
            "semantic_memory_conflict_exception_preservation_result_v1",

        "semantic_memory_version":
            SEMANTIC_MEMORY_VERSION,

        "phase":
            SEMANTIC_MEMORY_PHASE,

        "patch":
            "4.6.28H",

        "status":
            "SEMANTIC_MEMORY_CONFLICT_EXCEPTION_PRESERVED",

        "policy":
            "CERTIFIED_SEMANTIC_MEMORY_CONFLICT_EXCEPTION_PRESERVATION",

        "next":
            "memory_stability_and_retention",
    }

    for key, expected_value in expected.items():

        if preservation_result.get(key) != expected_value:
            raise SemanticMemoryError(
                "Invalid 4.6.28H lifecycle field: "
                f"{key}"
            )

    ownership_contract = preservation_result.get(
        "semantic_memory_ownership_mutation_contract"
    )

    preservation_bundle = preservation_result.get(
        "semantic_memory_conflict_exception_preservation_bundle"
    )

    versioning_bundle = preservation_result.get(
        "semantic_memory_versioning_supersession_bundle"
    )

    inspection = preservation_result.get(
        "certified_learning_engine_input_inspection"
    )

    boundaries = preservation_result.get(
        "processing_boundaries"
    )

    if not isinstance(
        ownership_contract,
        dict,
    ):
        raise SemanticMemoryError(
            "Semantic Memory ownership contract is missing."
        )

    if (
        ownership_contract.get("schema")
        != "semantic_memory_ownership_mutation_contract_v1"
    ):
        raise SemanticMemoryError(
            "Invalid ownership contract schema."
        )

    allowed_mutations = ownership_contract.get(
        "allowed_memory_mutations"
    )

    forbidden_mutations = ownership_contract.get(
        "forbidden_memory_mutations"
    )

    if not isinstance(
        allowed_mutations,
        tuple,
    ):
        raise SemanticMemoryError(
            "Allowed memory mutations must be a tuple."
        )

    if not isinstance(
        forbidden_mutations,
        tuple,
    ):
        raise SemanticMemoryError(
            "Forbidden memory mutations must be a tuple."
        )

    for permission in (
        "SET_MEMORY_STATE",
        "SET_RETENTION_STATE",
        "PRESERVE_MEMORY_HISTORY",
        "RETIRE_MEMORY_OBJECT",
        "EXPIRE_MEMORY_OBJECT",
    ):
        if permission not in allowed_mutations:
            raise SemanticMemoryError(
                "Required stability/retention permission missing: "
                f"{permission}"
            )

    for prohibition in (
        "MUTATE_LEARNING_ENGINE_OUTPUT",
        "RECLASSIFY_UPSTREAM_CONFLICT",
        "CHANGE_UPSTREAM_GUARD_DISPOSITION",
        "REWRITE_DYNAMIC_SEMANTIC_GRAPH",
        "PROMOTE_MEMORY_TO_CERTIFIED_TRUTH",
        "PROMOTE_MEMORY_TO_LEARNED_TRUTH",
        "SELECT_FINAL_TARGET",
        "MAKE_LINKING_DECISION",
        "PERFORM_RUNTIME_REASONING",
    ):
        if prohibition not in forbidden_mutations:
            raise SemanticMemoryError(
                "Required stability/retention prohibition missing: "
                f"{prohibition}"
            )

    if not isinstance(
        preservation_bundle,
        dict,
    ):
        raise SemanticMemoryError(
            "Conflict/exception preservation bundle is missing."
        )

    if (
        preservation_bundle.get("schema")
        != "semantic_memory_conflict_exception_preservation_bundle_v1"
    ):
        raise SemanticMemoryError(
            "Invalid conflict/exception preservation bundle schema."
        )

    if (
        preservation_bundle.get("preservation_policy")
        != "PRESERVE_CERTIFIED_CONFLICT_EXCEPTION_CONTEXT_WITHOUT_RECLASSIFICATION_OR_TRUTH_ADJUDICATION"
    ):
        raise SemanticMemoryError(
            "Invalid conflict/exception preservation policy."
        )

    for flag in (
        "conflict_context_preserved",
        "exception_context_preserved",
        "minority_patterns_preserved",
        "unresolved_context_preserved",
    ):
        if preservation_bundle.get(flag) is not True:
            raise SemanticMemoryError(
                "Required preserved context missing: "
                f"{flag}"
            )

    for flag in (
        "upstream_conflict_reclassified",
        "truth_adjudicated",
        "memory_persisted",
        "retention_decision_finalized",
        "retrieval_performed",
        "learning_engine_output_mutated",
        "graph_mutated",
        "target_selected",
        "linking_decision_performed",
    ):
        if preservation_bundle.get(flag) is not False:
            raise SemanticMemoryError(
                "Unsafe pre-retention preservation state: "
                f"{flag}"
            )

    if not isinstance(
        versioning_bundle,
        dict,
    ):
        raise SemanticMemoryError(
            "Semantic Memory versioning bundle is missing."
        )

    if (
        versioning_bundle.get("schema")
        != "semantic_memory_versioning_supersession_bundle_v1"
    ):
        raise SemanticMemoryError(
            "Invalid Semantic Memory versioning bundle schema."
        )

    if versioning_bundle.get(
        "versioning_performed"
    ) is not True:
        raise SemanticMemoryError(
            "Semantic Memory versioning was not completed."
        )

    if versioning_bundle.get(
        "history_preserved"
    ) is not True:
        raise SemanticMemoryError(
            "Semantic Memory history was not preserved."
        )

    if versioning_bundle.get(
        "silent_overwrite_performed"
    ) is not False:
        raise SemanticMemoryError(
            "Silent overwrite is forbidden."
        )

    if not isinstance(
        boundaries,
        dict,
    ):
        raise SemanticMemoryError(
            "4.6.28H processing boundaries are missing."
        )

    for required_true in (
        "semantic_memory_admission_performed",
        "semantic_memory_object_created",
        "memory_version_created",
        "conflict_exception_memory_preserved",
    ):
        if boundaries.get(
            required_true
        ) is not True:
            raise SemanticMemoryError(
                "Required upstream Semantic Memory stage missing: "
                f"{required_true}"
            )

    for flag in (
        "semantic_memory_written",
        "memory_persistence_performed",
        "memory_supersession_performed",
        "memory_retention_decision_performed",
        "memory_retrieval_performed",
        "learning_output_promoted_to_truth",
        "learning_engine_output_mutated",
        "graph_mutation_performed",
        "authority_rescored",
        "claim_integrity_redecided",
        "conflict_reclassified",
        "upstream_guard_disposition_changed",
        "target_created",
        "target_selected",
        "linking_decision_performed",
        "highlight_created",
    ):
        if boundaries.get(flag) is not False:
            raise SemanticMemoryError(
                "Unsafe pre-retention boundary state: "
                f"{flag}"
            )

    preserved_memory_objects = preservation_bundle.get(
        "preserved_memory_objects"
    )

    preservation_records = preservation_bundle.get(
        "preservation_records"
    )

    if not isinstance(
        preserved_memory_objects,
        tuple,
    ):
        raise SemanticMemoryError(
            "preserved_memory_objects must be a tuple."
        )

    if not isinstance(
        preservation_records,
        tuple,
    ):
        raise SemanticMemoryError(
            "preservation_records must be a tuple."
        )

    if not preserved_memory_objects:
        raise SemanticMemoryError(
            "No preserved Semantic Memory objects are available."
        )

    if len(
        preserved_memory_objects
    ) != len(
        preservation_records
    ):
        raise SemanticMemoryError(
            "Preserved memory object/record count mismatch."
        )

    package_id = preservation_result.get(
        "source_final_learning_engine_package_id"
    )

    graph_id = preservation_result.get(
        "source_final_graph_id"
    )

    graph_snapshot_id = preservation_result.get(
        "source_graph_snapshot_id"
    )

    learning_lineage_root_id = preservation_result.get(
        "source_learning_lineage_root_id"
    )

    graph_lineage_root_id = preservation_result.get(
        "source_lineage_root_id"
    )

    for name, value in (
        (
            "source_final_learning_engine_package_id",
            package_id,
        ),
        (
            "source_final_graph_id",
            graph_id,
        ),
        (
            "source_graph_snapshot_id",
            graph_snapshot_id,
        ),
        (
            "source_learning_lineage_root_id",
            learning_lineage_root_id,
        ),
        (
            "source_lineage_root_id",
            graph_lineage_root_id,
        ),
    ):
        if not isinstance(
            value,
            str,
        ) or not value:
            raise SemanticMemoryError(
                "Missing retention provenance field: "
                f"{name}"
            )

    preservation_by_object_id = {}

    for record in preservation_records:

        if not isinstance(
            record,
            dict,
        ):
            raise SemanticMemoryError(
                "Preservation record must be a dictionary."
            )

        if (
            record.get("schema")
            != "semantic_memory_conflict_exception_preservation_record_v1"
        ):
            raise SemanticMemoryError(
                "Invalid preservation record schema."
            )

        memory_object_id = record.get(
            "memory_object_id"
        )

        if not isinstance(
            memory_object_id,
            str,
        ) or not memory_object_id:
            raise SemanticMemoryError(
                "Preservation record memory object ID is missing."
            )

        if memory_object_id in preservation_by_object_id:
            raise SemanticMemoryError(
                "Duplicate preservation record for memory object."
            )

        preservation_by_object_id[
            memory_object_id
        ] = record

    def decide_stability_retention(
        memory_object: dict[str, Any],
    ) -> tuple[str, str]:

        if not isinstance(
            memory_object,
            dict,
        ):
            raise SemanticMemoryError(
                "Preserved memory object must be a dictionary."
            )

        if (
            memory_object.get("schema")
            != "semantic_memory_object_v1"
        ):
            raise SemanticMemoryError(
                "Invalid preserved memory object schema."
            )

        if memory_object.get(
            "conflict_exception_context_preserved"
        ) is not True:
            raise SemanticMemoryError(
                "Conflict/exception context was not preserved."
            )

        if memory_object.get(
            "upstream_conflict_reclassified"
        ) is not False:
            raise SemanticMemoryError(
                "Upstream conflict classification changed."
            )

        if memory_object.get(
            "truth_adjudicated"
        ) is not False:
            raise SemanticMemoryError(
                "Truth adjudication is forbidden."
            )

        if memory_object.get(
            "memory_persisted"
        ) is not False:
            raise SemanticMemoryError(
                "Memory persistence occurred too early."
            )

        if memory_object.get(
            "is_certified_fact"
        ) is not False:
            raise SemanticMemoryError(
                "Memory object cannot be certified truth."
            )

        if memory_object.get(
            "is_learned_truth"
        ) is not False:
            raise SemanticMemoryError(
                "Memory object cannot be learned truth."
            )

        memory_object_id = memory_object.get(
            "memory_object_id"
        )

        if memory_object_id not in preservation_by_object_id:
            raise SemanticMemoryError(
                "Conflict/exception preservation record is missing."
            )

        memory_state = memory_object.get(
            "memory_state"
        )

        if memory_state == "ACTIVE":
            return (
                "STABLE",
                "RETAIN",
            )

        if memory_state == "HELD":
            return (
                "HELD",
                "HOLD",
            )

        if memory_state == "BLOCKED":
            return (
                "BLOCKED",
                "HOLD",
            )

        if memory_state == "CONTESTED":
            return (
                "CONTESTED",
                "RETAIN_WITH_CAUTION",
            )

        if memory_state == "WEAKENED":
            return (
                "WEAKENED",
                "RETAIN_WITH_CAUTION",
            )

        if memory_state == "SUPERSEDED":
            return (
                "SUPERSEDED",
                "SUPERSEDE",
            )

        if memory_state == "RETIRED":
            return (
                "RETIRED",
                "RETIRE",
            )

        if memory_state == "EXPIRED":
            return (
                "EXPIRED",
                "EXPIRE",
            )

        raise SemanticMemoryError(
            "Unsupported Semantic Memory state for retention."
        )

    retention_records = []

    retained_memory_objects = []

    for memory_object in preserved_memory_objects:

        stability_state, retention_state = (
            decide_stability_retention(
                memory_object
            )
        )

        memory_object_id = memory_object[
            "memory_object_id"
        ]

        preservation_record = (
            preservation_by_object_id[
                memory_object_id
            ]
        )

        payload = {
            "memory_object_id":
                memory_object_id,

            "memory_version_record_id":
                memory_object.get(
                    "current_version_record_id"
                ),

            "conflict_exception_preservation_record_id":
                preservation_record.get(
                    "preservation_record_id"
                ),

            "stability_state":
                stability_state,

            "retention_state":
                retention_state,

            "source_learning_object_id":
                memory_object.get(
                    "source_learning_object_id"
                ),

            "source_final_graph_id":
                graph_id,

            "source_graph_snapshot_id":
                graph_snapshot_id,
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

        retention_record = {
            "schema":
                "semantic_memory_stability_retention_record_v1",

            "retention_record_id":
                "semanticmemorystabilityretention:v1:"
                + digest,

            "retention_record_digest":
                digest,

            "memory_object_id":
                memory_object_id,

            "memory_version_record_id":
                memory_object.get(
                    "current_version_record_id"
                ),

            "conflict_exception_preservation_record_id":
                preservation_record.get(
                    "preservation_record_id"
                ),

            "source_learning_object_id":
                memory_object.get(
                    "source_learning_object_id"
                ),

            "stability_state":
                stability_state,

            "retention_state":
                retention_state,

            "history_preserved":
                True,

            "conflict_context_preserved":
                True,

            "exception_context_preserved":
                True,

            "minority_patterns_preserved":
                True,

            "retention_decision_finalized":
                True,

            "memory_deleted":
                False,

            "history_deleted":
                False,

            "supersession_fabricated":
                False,

            "upstream_stability_rewritten":
                False,

            "upstream_conflict_reclassified":
                False,

            "truth_adjudicated":
                False,

            "is_certified_fact":
                False,

            "is_learned_truth":
                False,

            "memory_persisted":
                False,

            "retrieval_performed":
                False,

            "learning_engine_output_mutated":
                False,

            "graph_mutated":
                False,

            "target_selected":
                False,

            "linking_decision_performed":
                False,
        }

        retention_records.append(
            retention_record
        )

        retained_memory_objects.append(
            {
                **copy.deepcopy(
                    memory_object
                ),

                "stability_state":
                    stability_state,

                "retention_state":
                    retention_state,

                "retention_decision_finalized":
                    True,

                "stability_retention_record_id":
                    retention_record[
                        "retention_record_id"
                    ],

                "history_preserved":
                    True,

                "memory_deleted":
                    False,

                "truth_adjudicated":
                    False,

                "memory_persisted":
                    False,
            }
        )

    retention_records = tuple(
        retention_records
    )

    retained_memory_objects = tuple(
        retained_memory_objects
    )

    retention_record_ids = tuple(
        record[
            "retention_record_id"
        ]
        for record in retention_records
    )

    if len(
        retention_record_ids
    ) != len(
        set(retention_record_ids)
    ):
        raise SemanticMemoryError(
            "Duplicate stability/retention record IDs."
        )

    stability_counts = {
        "STABLE":
            0,

        "HELD":
            0,

        "BLOCKED":
            0,

        "CONTESTED":
            0,

        "WEAKENED":
            0,

        "SUPERSEDED":
            0,

        "RETIRED":
            0,

        "EXPIRED":
            0,
    }

    retention_counts = {
        "RETAIN":
            0,

        "RETAIN_WITH_CAUTION":
            0,

        "HOLD":
            0,

        "SUPERSEDE":
            0,

        "RETIRE":
            0,

        "EXPIRE":
            0,
    }

    for record in retention_records:

        stability_counts[
            record[
                "stability_state"
            ]
        ] += 1

        retention_counts[
            record[
                "retention_state"
            ]
        ] += 1

    retention_contract = {
        "schema":
            "semantic_memory_stability_retention_contract_v1",

        "active_memory_may_be_stable":
            True,

        "held_memory_must_remain_held":
            True,

        "blocked_memory_must_remain_blocked":
            True,

        "contested_memory_must_not_be_promoted_to_stable":
            True,

        "weakened_memory_must_not_be_promoted_to_stable":
            True,

        "retention_does_not_establish_truth":
            True,

        "retention_does_not_resolve_conflict":
            True,

        "retention_does_not_rewrite_learning_engine_stability":
            True,

        "retention_does_not_rewrite_upstream_guard":
            True,

        "retention_does_not_delete_history":
            True,

        "retention_does_not_delete_superseded_versions":
            True,

        "retention_does_not_create_targets":
            True,

        "retention_does_not_select_targets":
            True,

        "retention_does_not_make_linking_decisions":
            True,

        "retention_does_not_perform_runtime_reasoning":
            True,
    }

    bundle_payload = {
        "source_preservation_bundle_id":
            preservation_bundle.get(
                "preservation_bundle_id"
            ),

        "retention_record_ids":
            list(
                retention_record_ids
            ),

        "memory_object_ids":
            [
                item[
                    "memory_object_id"
                ]
                for item in retained_memory_objects
            ],

        "stability_counts":
            stability_counts,

        "retention_counts":
            retention_counts,
    }

    bundle_serialized = json.dumps(
        bundle_payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    bundle_digest = hashlib.sha256(
        bundle_serialized.encode("utf-8")
    ).hexdigest()

    retention_bundle = {
        "schema":
            "semantic_memory_stability_retention_bundle_v1",

        "stability_retention_bundle_id":
            "semanticmemorystabilityretentionbundle:v1:"
            + bundle_digest,

        "stability_retention_bundle_digest":
            bundle_digest,

        "source_preservation_bundle_id":
            preservation_bundle.get(
                "preservation_bundle_id"
            ),

        "retention_records":
            retention_records,

        "retained_memory_objects":
            retained_memory_objects,

        "stability_counts":
            stability_counts,

        "retention_counts":
            retention_counts,

        "retention_contract":
            retention_contract,

        "retention_record_count":
            len(
                retention_records
            ),

        "retention_policy":
            "STATE_PRESERVING_SEMANTIC_MEMORY_STABILITY_AND_RETENTION",

        "stability_retention_applied":
            True,

        "retention_decisions_finalized":
            True,

        "history_preserved":
            True,

        "memory_deleted":
            False,

        "history_deleted":
            False,

        "supersession_fabricated":
            False,

        "truth_adjudicated":
            False,

        "upstream_stability_rewritten":
            False,

        "upstream_conflict_reclassified":
            False,

        "upstream_guard_rewritten":
            False,

        "memory_persisted":
            False,

        "retrieval_performed":
            False,

        "learning_engine_output_mutated":
            False,

        "graph_mutated":
            False,

        "target_selected":
            False,

        "linking_decision_performed":
            False,
    }

    return {
        "schema":
            "semantic_memory_stability_retention_result_v1",

        "semantic_memory_version":
            SEMANTIC_MEMORY_VERSION,

        "phase":
            SEMANTIC_MEMORY_PHASE,

        "patch":
            "4.6.28I",

        "status":
            "SEMANTIC_MEMORY_STABILITY_RETENTION_COMPLETED",

        "source_final_learning_engine_package_id":
            preservation_result.get(
                "source_final_learning_engine_package_id"
            ),

        "source_final_learning_engine_package_digest":
            preservation_result.get(
                "source_final_learning_engine_package_digest"
            ),

        "source_final_graph_id":
            preservation_result.get(
                "source_final_graph_id"
            ),

        "source_final_graph_digest":
            preservation_result.get(
                "source_final_graph_digest"
            ),

        "source_graph_snapshot_id":
            graph_snapshot_id,

        "source_lineage_root_id":
            graph_lineage_root_id,

        "source_learning_lineage_root_id":
            learning_lineage_root_id,

        "semantic_memory_ownership_mutation_contract":
            copy.deepcopy(
                ownership_contract
            ),

        "semantic_memory_versioning_supersession_bundle":
            copy.deepcopy(
                versioning_bundle
            ),

        "semantic_memory_conflict_exception_preservation_bundle":
            copy.deepcopy(
                preservation_bundle
            ),

        "semantic_memory_stability_retention_bundle":
            retention_bundle,

        "certified_learning_engine_input_inspection":
            copy.deepcopy(
                inspection
            ),

        "processing_boundaries": {
            "semantic_memory_admission_performed":
                True,

            "semantic_memory_object_created":
                True,

            "memory_version_created":
                True,

            "conflict_exception_memory_preserved":
                True,

            "memory_retention_decision_performed":
                True,

            "semantic_memory_written":
                False,

            "memory_persistence_performed":
                False,

            "memory_supersession_performed":
                False,

            "memory_retrieval_performed":
                False,

            "learning_output_promoted_to_truth":
                False,

            "learning_engine_output_mutated":
                False,

            "graph_mutation_performed":
                False,

            "authority_rescored":
                False,

            "claim_integrity_redecided":
                False,

            "conflict_reclassified":
                False,

            "upstream_guard_disposition_changed":
                False,

            "target_created":
                False,

            "target_selected":
                False,

            "linking_decision_performed":
                False,

            "highlight_created":
                False,
        },

        "policy":
            "CERTIFIED_SEMANTIC_MEMORY_STABILITY_RETENTION",

        "next":
            "memory_provenance_and_lineage",
    }

def build_semantic_memory_provenance_lineage_v1(
    retention_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.28J ? Memory Provenance & Lineage.

    Binds retained Semantic Memory objects to their complete certified
    ancestry without persisting or retrieving memory.

    The lineage chain preserves:
    - Semantic Memory object identity
    - memory version identity
    - admission identity
    - Learning Engine object/package identity
    - Learning Engine lineage root
    - final Dynamic Semantic Graph identity
    - graph snapshot identity
    - graph lineage root
    - conflict/exception preservation identity
    - stability/retention decision identity

    No upstream semantic state is rewritten.
    """

    if not isinstance(
        retention_result,
        dict,
    ):
        raise SemanticMemoryError(
            "retention_result must be a dictionary."
        )

    expected = {
        "schema":
            "semantic_memory_stability_retention_result_v1",

        "semantic_memory_version":
            SEMANTIC_MEMORY_VERSION,

        "phase":
            SEMANTIC_MEMORY_PHASE,

        "patch":
            "4.6.28I",

        "status":
            "SEMANTIC_MEMORY_STABILITY_RETENTION_COMPLETED",

        "policy":
            "CERTIFIED_SEMANTIC_MEMORY_STABILITY_RETENTION",

        "next":
            "memory_provenance_and_lineage",
    }

    for key, expected_value in expected.items():

        if retention_result.get(key) != expected_value:
            raise SemanticMemoryError(
                "Invalid 4.6.28I lifecycle field: "
                f"{key}"
            )

    ownership_contract = retention_result.get(
        "semantic_memory_ownership_mutation_contract"
    )

    versioning_bundle = retention_result.get(
        "semantic_memory_versioning_supersession_bundle"
    )

    preservation_bundle = retention_result.get(
        "semantic_memory_conflict_exception_preservation_bundle"
    )

    retention_bundle = retention_result.get(
        "semantic_memory_stability_retention_bundle"
    )

    inspection = retention_result.get(
        "certified_learning_engine_input_inspection"
    )

    boundaries = retention_result.get(
        "processing_boundaries"
    )

    if not isinstance(
        ownership_contract,
        dict,
    ):
        raise SemanticMemoryError(
            "Semantic Memory ownership contract is missing."
        )

    if (
        ownership_contract.get("schema")
        != "semantic_memory_ownership_mutation_contract_v1"
    ):
        raise SemanticMemoryError(
            "Invalid ownership contract schema."
        )

    allowed_mutations = ownership_contract.get(
        "allowed_memory_mutations"
    )

    forbidden_mutations = ownership_contract.get(
        "forbidden_memory_mutations"
    )

    if not isinstance(
        allowed_mutations,
        tuple,
    ):
        raise SemanticMemoryError(
            "Allowed memory mutations must be a tuple."
        )

    if not isinstance(
        forbidden_mutations,
        tuple,
    ):
        raise SemanticMemoryError(
            "Forbidden memory mutations must be a tuple."
        )

    for permission in (
        "ATTACH_SOURCE_LEARNING_REFERENCE",
        "ATTACH_LEARNING_PROVENANCE_REFERENCE",
        "ATTACH_GRAPH_PROVENANCE_REFERENCE",
        "ATTACH_LINEAGE_REFERENCE",
        "PRESERVE_MEMORY_HISTORY",
    ):
        if permission not in allowed_mutations:
            raise SemanticMemoryError(
                "Required provenance/lineage permission missing: "
                f"{permission}"
            )

    for prohibition in (
        "MUTATE_LEARNING_ENGINE_OUTPUT",
        "REWRITE_DYNAMIC_SEMANTIC_GRAPH",
        "REWRITE_CLAIM_INTEGRITY",
        "RESCORE_AUTHORITY",
        "RECLASSIFY_UPSTREAM_CONFLICT",
        "CHANGE_UPSTREAM_GUARD_DISPOSITION",
        "PROMOTE_MEMORY_TO_CERTIFIED_TRUTH",
        "PROMOTE_MEMORY_TO_LEARNED_TRUTH",
        "SELECT_FINAL_TARGET",
        "MAKE_LINKING_DECISION",
        "PERFORM_RUNTIME_REASONING",
    ):
        if prohibition not in forbidden_mutations:
            raise SemanticMemoryError(
                "Required provenance/lineage prohibition missing: "
                f"{prohibition}"
            )

    if not isinstance(
        versioning_bundle,
        dict,
    ):
        raise SemanticMemoryError(
            "Semantic Memory versioning bundle is missing."
        )

    if (
        versioning_bundle.get("schema")
        != "semantic_memory_versioning_supersession_bundle_v1"
    ):
        raise SemanticMemoryError(
            "Invalid versioning bundle schema."
        )

    if versioning_bundle.get(
        "versioning_performed"
    ) is not True:
        raise SemanticMemoryError(
            "Semantic Memory versioning was not completed."
        )

    if versioning_bundle.get(
        "history_preserved"
    ) is not True:
        raise SemanticMemoryError(
            "Semantic Memory history was not preserved."
        )

    if not isinstance(
        preservation_bundle,
        dict,
    ):
        raise SemanticMemoryError(
            "Conflict/exception preservation bundle is missing."
        )

    if (
        preservation_bundle.get("schema")
        != "semantic_memory_conflict_exception_preservation_bundle_v1"
    ):
        raise SemanticMemoryError(
            "Invalid conflict/exception preservation bundle schema."
        )

    if preservation_bundle.get(
        "conflict_context_preserved"
    ) is not True:
        raise SemanticMemoryError(
            "Conflict context was not preserved."
        )

    if preservation_bundle.get(
        "exception_context_preserved"
    ) is not True:
        raise SemanticMemoryError(
            "Exception context was not preserved."
        )

    if not isinstance(
        retention_bundle,
        dict,
    ):
        raise SemanticMemoryError(
            "Semantic Memory stability/retention bundle is missing."
        )

    if (
        retention_bundle.get("schema")
        != "semantic_memory_stability_retention_bundle_v1"
    ):
        raise SemanticMemoryError(
            "Invalid stability/retention bundle schema."
        )

    if retention_bundle.get(
        "stability_retention_applied"
    ) is not True:
        raise SemanticMemoryError(
            "Semantic Memory stability/retention was not applied."
        )

    if retention_bundle.get(
        "retention_decisions_finalized"
    ) is not True:
        raise SemanticMemoryError(
            "Semantic Memory retention decisions are not finalized."
        )

    if retention_bundle.get(
        "history_preserved"
    ) is not True:
        raise SemanticMemoryError(
            "Semantic Memory retention history was not preserved."
        )

    for flag in (
        "memory_deleted",
        "history_deleted",
        "supersession_fabricated",
        "truth_adjudicated",
        "upstream_stability_rewritten",
        "upstream_conflict_reclassified",
        "upstream_guard_rewritten",
        "memory_persisted",
        "retrieval_performed",
        "learning_engine_output_mutated",
        "graph_mutated",
        "target_selected",
        "linking_decision_performed",
    ):
        if retention_bundle.get(flag) is not False:
            raise SemanticMemoryError(
                "Unsafe pre-lineage retention state: "
                f"{flag}"
            )

    if not isinstance(
        boundaries,
        dict,
    ):
        raise SemanticMemoryError(
            "4.6.28I processing boundaries are missing."
        )

    for required_true in (
        "semantic_memory_admission_performed",
        "semantic_memory_object_created",
        "memory_version_created",
        "conflict_exception_memory_preserved",
        "memory_retention_decision_performed",
    ):
        if boundaries.get(
            required_true
        ) is not True:
            raise SemanticMemoryError(
                "Required upstream Semantic Memory stage missing: "
                f"{required_true}"
            )

    for flag in (
        "semantic_memory_written",
        "memory_persistence_performed",
        "memory_supersession_performed",
        "memory_retrieval_performed",
        "learning_output_promoted_to_truth",
        "learning_engine_output_mutated",
        "graph_mutation_performed",
        "authority_rescored",
        "claim_integrity_redecided",
        "conflict_reclassified",
        "upstream_guard_disposition_changed",
        "target_created",
        "target_selected",
        "linking_decision_performed",
        "highlight_created",
    ):
        if boundaries.get(flag) is not False:
            raise SemanticMemoryError(
                "Unsafe pre-lineage boundary state: "
                f"{flag}"
            )

    package_id = retention_result.get(
        "source_final_learning_engine_package_id"
    )

    package_digest = retention_result.get(
        "source_final_learning_engine_package_digest"
    )

    graph_id = retention_result.get(
        "source_final_graph_id"
    )

    graph_digest = retention_result.get(
        "source_final_graph_digest"
    )

    graph_snapshot_id = retention_result.get(
        "source_graph_snapshot_id"
    )

    graph_lineage_root_id = retention_result.get(
        "source_lineage_root_id"
    )

    learning_lineage_root_id = retention_result.get(
        "source_learning_lineage_root_id"
    )

    for name, value in (
        (
            "source_final_learning_engine_package_id",
            package_id,
        ),
        (
            "source_final_learning_engine_package_digest",
            package_digest,
        ),
        (
            "source_final_graph_id",
            graph_id,
        ),
        (
            "source_final_graph_digest",
            graph_digest,
        ),
        (
            "source_graph_snapshot_id",
            graph_snapshot_id,
        ),
        (
            "source_lineage_root_id",
            graph_lineage_root_id,
        ),
        (
            "source_learning_lineage_root_id",
            learning_lineage_root_id,
        ),
    ):
        if not isinstance(
            value,
            str,
        ) or not value:
            raise SemanticMemoryError(
                "Missing provenance/lineage field: "
                f"{name}"
            )

    retained_memory_objects = retention_bundle.get(
        "retained_memory_objects"
    )

    retention_records = retention_bundle.get(
        "retention_records"
    )

    version_records = versioning_bundle.get(
        "version_records"
    )

    preservation_records = preservation_bundle.get(
        "preservation_records"
    )

    for name, value in (
        (
            "retained_memory_objects",
            retained_memory_objects,
        ),
        (
            "retention_records",
            retention_records,
        ),
        (
            "version_records",
            version_records,
        ),
        (
            "preservation_records",
            preservation_records,
        ),
    ):
        if not isinstance(
            value,
            tuple,
        ):
            raise SemanticMemoryError(
                f"{name} must be a tuple."
            )

    if not retained_memory_objects:
        raise SemanticMemoryError(
            "No retained Semantic Memory objects are available."
        )

    if len(
        retained_memory_objects
    ) != len(
        retention_records
    ):
        raise SemanticMemoryError(
            "Retained memory object/retention record count mismatch."
        )

    version_by_object_id = {}

    for record in version_records:

        if not isinstance(
            record,
            dict,
        ):
            raise SemanticMemoryError(
                "Version record must be a dictionary."
            )

        if (
            record.get("schema")
            != "semantic_memory_version_record_v1"
        ):
            raise SemanticMemoryError(
                "Invalid version record schema."
            )

        memory_object_id = record.get(
            "memory_object_id"
        )

        if not isinstance(
            memory_object_id,
            str,
        ) or not memory_object_id:
            raise SemanticMemoryError(
                "Version record memory object ID is missing."
            )

        if memory_object_id in version_by_object_id:
            raise SemanticMemoryError(
                "Duplicate version record lineage."
            )

        version_by_object_id[
            memory_object_id
        ] = record

    preservation_by_object_id = {}

    for record in preservation_records:

        if not isinstance(
            record,
            dict,
        ):
            raise SemanticMemoryError(
                "Preservation record must be a dictionary."
            )

        if (
            record.get("schema")
            != "semantic_memory_conflict_exception_preservation_record_v1"
        ):
            raise SemanticMemoryError(
                "Invalid preservation record schema."
            )

        memory_object_id = record.get(
            "memory_object_id"
        )

        if not isinstance(
            memory_object_id,
            str,
        ) or not memory_object_id:
            raise SemanticMemoryError(
                "Preservation record memory object ID is missing."
            )

        if memory_object_id in preservation_by_object_id:
            raise SemanticMemoryError(
                "Duplicate preservation lineage."
            )

        preservation_by_object_id[
            memory_object_id
        ] = record

    retention_by_object_id = {}

    for record in retention_records:

        if not isinstance(
            record,
            dict,
        ):
            raise SemanticMemoryError(
                "Retention record must be a dictionary."
            )

        if (
            record.get("schema")
            != "semantic_memory_stability_retention_record_v1"
        ):
            raise SemanticMemoryError(
                "Invalid retention record schema."
            )

        memory_object_id = record.get(
            "memory_object_id"
        )

        if not isinstance(
            memory_object_id,
            str,
        ) or not memory_object_id:
            raise SemanticMemoryError(
                "Retention record memory object ID is missing."
            )

        if memory_object_id in retention_by_object_id:
            raise SemanticMemoryError(
                "Duplicate retention lineage."
            )

        retention_by_object_id[
            memory_object_id
        ] = record

    lineage_records = []
    lineage_bound_memory_objects = []

    for memory_object in retained_memory_objects:

        if not isinstance(
            memory_object,
            dict,
        ):
            raise SemanticMemoryError(
                "Retained memory object must be a dictionary."
            )

        if (
            memory_object.get("schema")
            != "semantic_memory_object_v1"
        ):
            raise SemanticMemoryError(
                "Invalid retained memory object schema."
            )

        if memory_object.get(
            "retention_decision_finalized"
        ) is not True:
            raise SemanticMemoryError(
                "Retention decision was not finalized."
            )

        if memory_object.get(
            "history_preserved"
        ) is not True:
            raise SemanticMemoryError(
                "Memory object history was not preserved."
            )

        if memory_object.get(
            "memory_deleted"
        ) is not False:
            raise SemanticMemoryError(
                "Memory object was deleted."
            )

        if memory_object.get(
            "truth_adjudicated"
        ) is not False:
            raise SemanticMemoryError(
                "Truth adjudication is forbidden."
            )

        if memory_object.get(
            "memory_persisted"
        ) is not False:
            raise SemanticMemoryError(
                "Memory persistence occurred too early."
            )

        memory_object_id = memory_object.get(
            "memory_object_id"
        )

        source_learning_object_id = memory_object.get(
            "source_learning_object_id"
        )

        source_admission_record_id = memory_object.get(
            "source_admission_record_id"
        )

        if not isinstance(
            memory_object_id,
            str,
        ) or not memory_object_id:
            raise SemanticMemoryError(
                "Memory object ID is missing."
            )

        if not isinstance(
            source_learning_object_id,
            str,
        ) or not source_learning_object_id:
            raise SemanticMemoryError(
                "Source learning object ID is missing."
            )

        if not isinstance(
            source_admission_record_id,
            str,
        ) or not source_admission_record_id:
            raise SemanticMemoryError(
                "Source admission record ID is missing."
            )

        if memory_object_id not in version_by_object_id:
            raise SemanticMemoryError(
                "Version lineage is missing."
            )

        if memory_object_id not in preservation_by_object_id:
            raise SemanticMemoryError(
                "Conflict/exception lineage is missing."
            )

        if memory_object_id not in retention_by_object_id:
            raise SemanticMemoryError(
                "Retention lineage is missing."
            )

        version_record = (
            version_by_object_id[
                memory_object_id
            ]
        )

        preservation_record = (
            preservation_by_object_id[
                memory_object_id
            ]
        )

        retention_record = (
            retention_by_object_id[
                memory_object_id
            ]
        )

        if (
            memory_object.get(
                "current_version_record_id"
            )
            != version_record.get(
                "memory_version_record_id"
            )
        ):
            raise SemanticMemoryError(
                "Memory version lineage mismatch."
            )

        if (
            memory_object.get(
                "conflict_exception_preservation_record_id"
            )
            != preservation_record.get(
                "preservation_record_id"
            )
        ):
            raise SemanticMemoryError(
                "Conflict/exception lineage mismatch."
            )

        if (
            memory_object.get(
                "stability_retention_record_id"
            )
            != retention_record.get(
                "retention_record_id"
            )
        ):
            raise SemanticMemoryError(
                "Stability/retention lineage mismatch."
            )

        lineage_chain = (
            source_learning_object_id,
            source_admission_record_id,
            memory_object_id,
            version_record[
                "memory_version_record_id"
            ],
            preservation_record[
                "preservation_record_id"
            ],
            retention_record[
                "retention_record_id"
            ],
            package_id,
            learning_lineage_root_id,
            graph_id,
            graph_snapshot_id,
            graph_lineage_root_id,
        )

        if any(
            not isinstance(item, str)
            or not item
            for item in lineage_chain
        ):
            raise SemanticMemoryError(
                "Semantic Memory lineage contains an invalid reference."
            )

        payload = {
            "memory_object_id":
                memory_object_id,

            "source_learning_object_id":
                source_learning_object_id,

            "source_admission_record_id":
                source_admission_record_id,

            "memory_version_record_id":
                version_record[
                    "memory_version_record_id"
                ],

            "preservation_record_id":
                preservation_record[
                    "preservation_record_id"
                ],

            "retention_record_id":
                retention_record[
                    "retention_record_id"
                ],

            "source_learning_engine_package_id":
                package_id,

            "source_learning_lineage_root_id":
                learning_lineage_root_id,

            "source_final_graph_id":
                graph_id,

            "source_graph_snapshot_id":
                graph_snapshot_id,

            "source_graph_lineage_root_id":
                graph_lineage_root_id,
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

        lineage_record = {
            "schema":
                "semantic_memory_provenance_lineage_record_v1",

            "memory_lineage_record_id":
                "semanticmemorylineage:v1:"
                + digest,

            "memory_lineage_record_digest":
                digest,

            "memory_object_id":
                memory_object_id,

            "source_learning_object_id":
                source_learning_object_id,

            "source_admission_record_id":
                source_admission_record_id,

            "memory_version_record_id":
                version_record[
                    "memory_version_record_id"
                ],

            "conflict_exception_preservation_record_id":
                preservation_record[
                    "preservation_record_id"
                ],

            "stability_retention_record_id":
                retention_record[
                    "retention_record_id"
                ],

            "source_learning_engine_package_id":
                package_id,

            "source_learning_engine_package_digest":
                package_digest,

            "source_learning_lineage_root_id":
                learning_lineage_root_id,

            "source_final_graph_id":
                graph_id,

            "source_final_graph_digest":
                graph_digest,

            "source_graph_snapshot_id":
                graph_snapshot_id,

            "source_graph_lineage_root_id":
                graph_lineage_root_id,

            "lineage_chain":
                lineage_chain,

            "provenance_complete":
                True,

            "lineage_complete":
                True,

            "history_preserved":
                True,

            "source_learning_reference_preserved":
                True,

            "graph_provenance_preserved":
                True,

            "conflict_exception_provenance_preserved":
                True,

            "stability_retention_provenance_preserved":
                True,

            "memory_is_certified_fact":
                False,

            "memory_is_learned_truth":
                False,

            "truth_adjudicated":
                False,

            "memory_persisted":
                False,

            "retrieval_performed":
                False,

            "learning_engine_output_mutated":
                False,

            "graph_mutated":
                False,

            "target_selected":
                False,

            "linking_decision_performed":
                False,
        }

        lineage_records.append(
            lineage_record
        )

        lineage_bound_memory_objects.append(
            {
                **copy.deepcopy(
                    memory_object
                ),

                "memory_lineage_record_id":
                    lineage_record[
                        "memory_lineage_record_id"
                    ],

                "provenance_complete":
                    True,

                "lineage_complete":
                    True,

                "source_learning_reference_preserved":
                    True,

                "graph_provenance_preserved":
                    True,

                "memory_persisted":
                    False,

                "retrieval_performed":
                    False,
            }
        )

    lineage_records = tuple(
        lineage_records
    )

    lineage_bound_memory_objects = tuple(
        lineage_bound_memory_objects
    )

    lineage_record_ids = tuple(
        record[
            "memory_lineage_record_id"
        ]
        for record in lineage_records
    )

    if len(
        lineage_record_ids
    ) != len(
        set(lineage_record_ids)
    ):
        raise SemanticMemoryError(
            "Duplicate Semantic Memory lineage IDs."
        )

    memory_lineage_root_payload = {
        "memory_lineage_record_ids":
            list(
                lineage_record_ids
            ),

        "source_learning_engine_package_id":
            package_id,

        "source_learning_lineage_root_id":
            learning_lineage_root_id,

        "source_final_graph_id":
            graph_id,

        "source_graph_snapshot_id":
            graph_snapshot_id,

        "source_graph_lineage_root_id":
            graph_lineage_root_id,
    }

    memory_lineage_root_serialized = json.dumps(
        memory_lineage_root_payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    memory_lineage_root_digest = hashlib.sha256(
        memory_lineage_root_serialized.encode(
            "utf-8"
        )
    ).hexdigest()

    semantic_memory_lineage_root_id = (
        "semanticmemorylineageroot:v1:"
        + memory_lineage_root_digest
    )

    provenance_contract = {
        "schema":
            "semantic_memory_provenance_lineage_contract_v1",

        "every_memory_object_requires_source_learning_reference":
            True,

        "every_memory_object_requires_admission_reference":
            True,

        "every_memory_object_requires_version_reference":
            True,

        "every_memory_object_requires_conflict_exception_reference":
            True,

        "every_memory_object_requires_retention_reference":
            True,

        "every_memory_object_requires_learning_engine_package_reference":
            True,

        "every_memory_object_requires_learning_lineage_reference":
            True,

        "every_memory_object_requires_final_graph_reference":
            True,

        "every_memory_object_requires_graph_snapshot_reference":
            True,

        "every_memory_object_requires_graph_lineage_reference":
            True,

        "lineage_must_be_deterministic":
            True,

        "lineage_must_preserve_history":
            True,

        "lineage_does_not_establish_truth":
            True,

        "lineage_does_not_mutate_learning_engine":
            True,

        "lineage_does_not_mutate_graph":
            True,

        "lineage_does_not_reclassify_conflict":
            True,

        "lineage_does_not_rewrite_upstream_guard":
            True,

        "lineage_does_not_create_targets":
            True,

        "lineage_does_not_select_targets":
            True,

        "lineage_does_not_make_linking_decisions":
            True,

        "lineage_does_not_perform_runtime_reasoning":
            True,
    }

    bundle_payload = {
        "semantic_memory_lineage_root_id":
            semantic_memory_lineage_root_id,

        "memory_lineage_record_ids":
            list(
                lineage_record_ids
            ),

        "source_retention_bundle_id":
            retention_bundle.get(
                "stability_retention_bundle_id"
            ),

        "source_learning_engine_package_id":
            package_id,

        "source_final_graph_id":
            graph_id,
    }

    bundle_serialized = json.dumps(
        bundle_payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    bundle_digest = hashlib.sha256(
        bundle_serialized.encode("utf-8")
    ).hexdigest()

    provenance_lineage_bundle = {
        "schema":
            "semantic_memory_provenance_lineage_bundle_v1",

        "provenance_lineage_bundle_id":
            "semanticmemoryprovenancelineagebundle:v1:"
            + bundle_digest,

        "provenance_lineage_bundle_digest":
            bundle_digest,

        "semantic_memory_lineage_root_id":
            semantic_memory_lineage_root_id,

        "semantic_memory_lineage_root_digest":
            memory_lineage_root_digest,

        "source_retention_bundle_id":
            retention_bundle.get(
                "stability_retention_bundle_id"
            ),

        "source_learning_engine_package_id":
            package_id,

        "source_learning_engine_package_digest":
            package_digest,

        "source_learning_lineage_root_id":
            learning_lineage_root_id,

        "source_final_graph_id":
            graph_id,

        "source_final_graph_digest":
            graph_digest,

        "source_graph_snapshot_id":
            graph_snapshot_id,

        "source_graph_lineage_root_id":
            graph_lineage_root_id,

        "lineage_records":
            lineage_records,

        "lineage_bound_memory_objects":
            lineage_bound_memory_objects,

        "provenance_contract":
            provenance_contract,

        "lineage_record_count":
            len(
                lineage_records
            ),

        "provenance_policy":
            "COMPLETE_DETERMINISTIC_SEMANTIC_MEMORY_PROVENANCE_AND_LINEAGE",

        "provenance_complete":
            True,

        "lineage_complete":
            True,

        "history_preserved":
            True,

        "memory_persisted":
            False,

        "retrieval_performed":
            False,

        "truth_adjudicated":
            False,

        "learning_engine_output_mutated":
            False,

        "graph_mutated":
            False,

        "conflict_reclassified":
            False,

        "upstream_guard_rewritten":
            False,

        "target_created":
            False,

        "target_selected":
            False,

        "linking_decision_performed":
            False,
    }

    return {
        "schema":
            "semantic_memory_provenance_lineage_result_v1",

        "semantic_memory_version":
            SEMANTIC_MEMORY_VERSION,

        "phase":
            SEMANTIC_MEMORY_PHASE,

        "patch":
            "4.6.28J",

        "status":
            "SEMANTIC_MEMORY_PROVENANCE_LINEAGE_COMPLETED",

        "source_final_learning_engine_package_id":
            package_id,

        "source_final_learning_engine_package_digest":
            package_digest,

        "source_final_graph_id":
            graph_id,

        "source_final_graph_digest":
            graph_digest,

        "source_graph_snapshot_id":
            graph_snapshot_id,

        "source_lineage_root_id":
            graph_lineage_root_id,

        "source_learning_lineage_root_id":
            learning_lineage_root_id,

        "semantic_memory_lineage_root_id":
            semantic_memory_lineage_root_id,

        "semantic_memory_ownership_mutation_contract":
            copy.deepcopy(
                ownership_contract
            ),

        "semantic_memory_versioning_supersession_bundle":
            copy.deepcopy(
                versioning_bundle
            ),

        "semantic_memory_conflict_exception_preservation_bundle":
            copy.deepcopy(
                preservation_bundle
            ),

        "semantic_memory_stability_retention_bundle":
            copy.deepcopy(
                retention_bundle
            ),

        "semantic_memory_provenance_lineage_bundle":
            provenance_lineage_bundle,

        "certified_learning_engine_input_inspection":
            copy.deepcopy(
                inspection
            ),

        "processing_boundaries": {
            "semantic_memory_admission_performed":
                True,

            "semantic_memory_object_created":
                True,

            "memory_version_created":
                True,

            "conflict_exception_memory_preserved":
                True,

            "memory_retention_decision_performed":
                True,

            "memory_provenance_lineage_built":
                True,

            "semantic_memory_written":
                False,

            "memory_persistence_performed":
                False,

            "memory_supersession_performed":
                False,

            "memory_retrieval_performed":
                False,

            "learning_output_promoted_to_truth":
                False,

            "learning_engine_output_mutated":
                False,

            "graph_mutation_performed":
                False,

            "authority_rescored":
                False,

            "claim_integrity_redecided":
                False,

            "conflict_reclassified":
                False,

            "upstream_guard_disposition_changed":
                False,

            "target_created":
                False,

            "target_selected":
                False,

            "linking_decision_performed":
                False,

            "highlight_created":
                False,
        },

        "policy":
            "CERTIFIED_SEMANTIC_MEMORY_PROVENANCE_LINEAGE",

        "next":
            "memory_retrieval_read_contract",
    }

def define_semantic_memory_retrieval_read_contract_v1(
    lineage_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.28K ? Memory Retrieval / Read Contract.

    Defines the canonical read contract and retrieval metadata for
    Semantic Memory without performing live persistence-backed
    retrieval.

    Readability does not establish truth.

    Default runtime reads are restricted to stable, retained memory.
    Held, blocked, contested, weakened, superseded, retired, expired,
    and historical memory require explicit state-aware retrieval.
    """

    if not isinstance(
        lineage_result,
        dict,
    ):
        raise SemanticMemoryError(
            "lineage_result must be a dictionary."
        )

    expected = {
        "schema":
            "semantic_memory_provenance_lineage_result_v1",

        "semantic_memory_version":
            SEMANTIC_MEMORY_VERSION,

        "phase":
            SEMANTIC_MEMORY_PHASE,

        "patch":
            "4.6.28J",

        "status":
            "SEMANTIC_MEMORY_PROVENANCE_LINEAGE_COMPLETED",

        "policy":
            "CERTIFIED_SEMANTIC_MEMORY_PROVENANCE_LINEAGE",

        "next":
            "memory_retrieval_read_contract",
    }

    for key, expected_value in expected.items():

        if lineage_result.get(key) != expected_value:
            raise SemanticMemoryError(
                "Invalid 4.6.28J lifecycle field: "
                f"{key}"
            )

    ownership_contract = lineage_result.get(
        "semantic_memory_ownership_mutation_contract"
    )

    retention_bundle = lineage_result.get(
        "semantic_memory_stability_retention_bundle"
    )

    lineage_bundle = lineage_result.get(
        "semantic_memory_provenance_lineage_bundle"
    )

    inspection = lineage_result.get(
        "certified_learning_engine_input_inspection"
    )

    boundaries = lineage_result.get(
        "processing_boundaries"
    )

    if not isinstance(
        ownership_contract,
        dict,
    ):
        raise SemanticMemoryError(
            "Semantic Memory ownership contract is missing."
        )

    if (
        ownership_contract.get("schema")
        != "semantic_memory_ownership_mutation_contract_v1"
    ):
        raise SemanticMemoryError(
            "Invalid ownership contract schema."
        )

    allowed_mutations = ownership_contract.get(
        "allowed_memory_mutations"
    )

    forbidden_mutations = ownership_contract.get(
        "forbidden_memory_mutations"
    )

    if not isinstance(
        allowed_mutations,
        tuple,
    ):
        raise SemanticMemoryError(
            "Allowed memory mutations must be a tuple."
        )

    if not isinstance(
        forbidden_mutations,
        tuple,
    ):
        raise SemanticMemoryError(
            "Forbidden memory mutations must be a tuple."
        )

    if (
        "CREATE_RETRIEVAL_METADATA"
        not in allowed_mutations
    ):
        raise SemanticMemoryError(
            "CREATE_RETRIEVAL_METADATA permission is missing."
        )

    for prohibition in (
        "MUTATE_LEARNING_ENGINE_OUTPUT",
        "REWRITE_DYNAMIC_SEMANTIC_GRAPH",
        "REWRITE_CLAIM_INTEGRITY",
        "RESCORE_AUTHORITY",
        "RECLASSIFY_UPSTREAM_CONFLICT",
        "CHANGE_UPSTREAM_GUARD_DISPOSITION",
        "PROMOTE_MEMORY_TO_CERTIFIED_TRUTH",
        "PROMOTE_MEMORY_TO_LEARNED_TRUTH",
        "SELECT_FINAL_TARGET",
        "MAKE_LINKING_DECISION",
        "PERFORM_RUNTIME_REASONING",
    ):
        if prohibition not in forbidden_mutations:
            raise SemanticMemoryError(
                "Required retrieval prohibition missing: "
                f"{prohibition}"
            )

    if not isinstance(
        retention_bundle,
        dict,
    ):
        raise SemanticMemoryError(
            "Semantic Memory stability/retention bundle is missing."
        )

    if (
        retention_bundle.get("schema")
        != "semantic_memory_stability_retention_bundle_v1"
    ):
        raise SemanticMemoryError(
            "Invalid stability/retention bundle schema."
        )

    if retention_bundle.get(
        "stability_retention_applied"
    ) is not True:
        raise SemanticMemoryError(
            "Stability/retention has not been applied."
        )

    if retention_bundle.get(
        "retention_decisions_finalized"
    ) is not True:
        raise SemanticMemoryError(
            "Retention decisions are not finalized."
        )

    if not isinstance(
        lineage_bundle,
        dict,
    ):
        raise SemanticMemoryError(
            "Semantic Memory provenance/lineage bundle is missing."
        )

    if (
        lineage_bundle.get("schema")
        != "semantic_memory_provenance_lineage_bundle_v1"
    ):
        raise SemanticMemoryError(
            "Invalid provenance/lineage bundle schema."
        )

    if lineage_bundle.get(
        "provenance_complete"
    ) is not True:
        raise SemanticMemoryError(
            "Semantic Memory provenance is incomplete."
        )

    if lineage_bundle.get(
        "lineage_complete"
    ) is not True:
        raise SemanticMemoryError(
            "Semantic Memory lineage is incomplete."
        )

    if lineage_bundle.get(
        "history_preserved"
    ) is not True:
        raise SemanticMemoryError(
            "Semantic Memory history was not preserved."
        )

    for flag in (
        "memory_persisted",
        "retrieval_performed",
        "truth_adjudicated",
        "learning_engine_output_mutated",
        "graph_mutated",
        "conflict_reclassified",
        "upstream_guard_rewritten",
        "target_created",
        "target_selected",
        "linking_decision_performed",
    ):
        if lineage_bundle.get(flag) is not False:
            raise SemanticMemoryError(
                "Unsafe pre-read-contract lineage state: "
                f"{flag}"
            )

    if not isinstance(
        boundaries,
        dict,
    ):
        raise SemanticMemoryError(
            "4.6.28J processing boundaries are missing."
        )

    for required_true in (
        "semantic_memory_admission_performed",
        "semantic_memory_object_created",
        "memory_version_created",
        "conflict_exception_memory_preserved",
        "memory_retention_decision_performed",
        "memory_provenance_lineage_built",
    ):
        if boundaries.get(
            required_true
        ) is not True:
            raise SemanticMemoryError(
                "Required upstream Semantic Memory stage missing: "
                f"{required_true}"
            )

    for flag in (
        "semantic_memory_written",
        "memory_persistence_performed",
        "memory_supersession_performed",
        "memory_retrieval_performed",
        "learning_output_promoted_to_truth",
        "learning_engine_output_mutated",
        "graph_mutation_performed",
        "authority_rescored",
        "claim_integrity_redecided",
        "conflict_reclassified",
        "upstream_guard_disposition_changed",
        "target_created",
        "target_selected",
        "linking_decision_performed",
        "highlight_created",
    ):
        if boundaries.get(flag) is not False:
            raise SemanticMemoryError(
                "Unsafe pre-read-contract boundary state: "
                f"{flag}"
            )

    lineage_objects = lineage_bundle.get(
        "lineage_bound_memory_objects"
    )

    lineage_records = lineage_bundle.get(
        "lineage_records"
    )

    if not isinstance(
        lineage_objects,
        tuple,
    ):
        raise SemanticMemoryError(
            "lineage_bound_memory_objects must be a tuple."
        )

    if not isinstance(
        lineage_records,
        tuple,
    ):
        raise SemanticMemoryError(
            "lineage_records must be a tuple."
        )

    if not lineage_objects:
        raise SemanticMemoryError(
            "No lineage-bound Semantic Memory objects are available."
        )

    if len(
        lineage_objects
    ) != len(
        lineage_records
    ):
        raise SemanticMemoryError(
            "Memory object/lineage record count mismatch."
        )

    lineage_record_by_object_id = {}

    for record in lineage_records:

        if not isinstance(
            record,
            dict,
        ):
            raise SemanticMemoryError(
                "Lineage record must be a dictionary."
            )

        if (
            record.get("schema")
            != "semantic_memory_provenance_lineage_record_v1"
        ):
            raise SemanticMemoryError(
                "Invalid lineage record schema."
            )

        memory_object_id = record.get(
            "memory_object_id"
        )

        if not isinstance(
            memory_object_id,
            str,
        ) or not memory_object_id:
            raise SemanticMemoryError(
                "Lineage record memory object ID is missing."
            )

        if memory_object_id in lineage_record_by_object_id:
            raise SemanticMemoryError(
                "Duplicate lineage record for memory object."
            )

        lineage_record_by_object_id[
            memory_object_id
        ] = record

    package_id = lineage_result.get(
        "source_final_learning_engine_package_id"
    )

    graph_id = lineage_result.get(
        "source_final_graph_id"
    )

    semantic_memory_lineage_root_id = (
        lineage_result.get(
            "semantic_memory_lineage_root_id"
        )
    )

    for name, value in (
        (
            "source_final_learning_engine_package_id",
            package_id,
        ),
        (
            "source_final_graph_id",
            graph_id,
        ),
        (
            "semantic_memory_lineage_root_id",
            semantic_memory_lineage_root_id,
        ),
    ):
        if not isinstance(
            value,
            str,
        ) or not value:
            raise SemanticMemoryError(
                "Missing retrieval contract provenance: "
                f"{name}"
            )

    default_readable_memory_ids = []
    held_memory_ids = []
    blocked_memory_ids = []
    contested_memory_ids = []
    historical_memory_ids = []
    retrieval_metadata_records = []

    def classify_retrieval(
        memory_object: dict[str, Any],
    ) -> tuple[str, bool]:

        memory_state = memory_object.get(
            "memory_state"
        )

        stability_state = memory_object.get(
            "stability_state"
        )

        retention_state = memory_object.get(
            "retention_state"
        )

        supersession_state = memory_object.get(
            "supersession_state"
        )

        if (
            memory_state == "ACTIVE"
            and stability_state == "STABLE"
            and retention_state == "RETAIN"
            and supersession_state
            in (
                None,
                "NOT_SUPERSEDED",
            )
        ):
            return (
                "ACTIVE_MEMORY",
                True,
            )

        if (
            memory_state == "BLOCKED"
            or stability_state == "BLOCKED"
        ):
            return (
                "BLOCKED_MEMORY",
                False,
            )

        if (
            memory_state == "HELD"
            or stability_state == "HELD"
            or retention_state == "HOLD"
        ):
            return (
                "HELD_MEMORY",
                False,
            )

        if (
            memory_state == "CONTESTED"
            or stability_state == "CONTESTED"
            or retention_state == "RETAIN_WITH_CAUTION"
        ):
            return (
                "CONTESTED_MEMORY",
                False,
            )

        if (
            memory_state
            in (
                "SUPERSEDED",
                "RETIRED",
                "EXPIRED",
            )
            or retention_state
            in (
                "SUPERSEDE",
                "RETIRE",
                "EXPIRE",
            )
            or supersession_state == "SUPERSEDED"
        ):
            return (
                "HISTORICAL_MEMORY",
                False,
            )

        if (
            memory_state == "WEAKENED"
            or stability_state == "WEAKENED"
        ):
            return (
                "CONTESTED_MEMORY",
                False,
            )

        return (
            "HISTORICAL_MEMORY",
            False,
        )

    for memory_object in lineage_objects:

        if not isinstance(
            memory_object,
            dict,
        ):
            raise SemanticMemoryError(
                "Lineage-bound memory object must be a dictionary."
            )

        if (
            memory_object.get("schema")
            != "semantic_memory_object_v1"
        ):
            raise SemanticMemoryError(
                "Invalid lineage-bound memory object schema."
            )

        if memory_object.get(
            "provenance_complete"
        ) is not True:
            raise SemanticMemoryError(
                "Memory object provenance is incomplete."
            )

        if memory_object.get(
            "lineage_complete"
        ) is not True:
            raise SemanticMemoryError(
                "Memory object lineage is incomplete."
            )

        if memory_object.get(
            "history_preserved"
        ) is not True:
            raise SemanticMemoryError(
                "Memory object history is incomplete."
            )

        if memory_object.get(
            "memory_persisted"
        ) is not False:
            raise SemanticMemoryError(
                "Memory persistence occurred too early."
            )

        if memory_object.get(
            "retrieval_performed"
        ) is not False:
            raise SemanticMemoryError(
                "Memory retrieval occurred too early."
            )

        if memory_object.get(
            "is_certified_fact"
        ) is not False:
            raise SemanticMemoryError(
                "Readable memory cannot be certified truth."
            )

        if memory_object.get(
            "is_learned_truth"
        ) is not False:
            raise SemanticMemoryError(
                "Readable memory cannot be learned truth."
            )

        memory_object_id = memory_object.get(
            "memory_object_id"
        )

        memory_lineage_record_id = (
            memory_object.get(
                "memory_lineage_record_id"
            )
        )

        if not isinstance(
            memory_object_id,
            str,
        ) or not memory_object_id:
            raise SemanticMemoryError(
                "Memory object ID is missing."
            )

        if memory_object_id not in lineage_record_by_object_id:
            raise SemanticMemoryError(
                "Memory lineage record is missing."
            )

        lineage_record = (
            lineage_record_by_object_id[
                memory_object_id
            ]
        )

        if (
            memory_lineage_record_id
            != lineage_record.get(
                "memory_lineage_record_id"
            )
        ):
            raise SemanticMemoryError(
                "Memory lineage reference mismatch."
            )

        retrieval_class, default_readable = (
            classify_retrieval(
                memory_object
            )
        )

        payload = {
            "memory_object_id":
                memory_object_id,

            "memory_lineage_record_id":
                memory_lineage_record_id,

            "retrieval_class":
                retrieval_class,

            "default_runtime_readable":
                default_readable,

            "memory_state":
                memory_object.get(
                    "memory_state"
                ),

            "stability_state":
                memory_object.get(
                    "stability_state"
                ),

            "retention_state":
                memory_object.get(
                    "retention_state"
                ),

            "current_version":
                memory_object.get(
                    "current_version"
                ),

            "source_final_graph_id":
                graph_id,
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

        metadata = {
            "schema":
                "semantic_memory_retrieval_metadata_v1",

            "retrieval_metadata_id":
                "semanticmemoryretrievalmetadata:v1:"
                + digest,

            "retrieval_metadata_digest":
                digest,

            "memory_object_id":
                memory_object_id,

            "memory_lineage_record_id":
                memory_lineage_record_id,

            "retrieval_class":
                retrieval_class,

            "default_runtime_readable":
                default_readable,

            "explicit_state_aware_read_required":
                not default_readable,

            "memory_state":
                memory_object.get(
                    "memory_state"
                ),

            "stability_state":
                memory_object.get(
                    "stability_state"
                ),

            "retention_state":
                memory_object.get(
                    "retention_state"
                ),

            "current_version":
                memory_object.get(
                    "current_version"
                ),

            "source_learning_object_id":
                memory_object.get(
                    "source_learning_object_id"
                ),

            "source_learning_engine_package_id":
                package_id,

            "source_final_graph_id":
                graph_id,

            "semantic_memory_lineage_root_id":
                semantic_memory_lineage_root_id,

            "provenance_required_on_read":
                True,

            "lineage_required_on_read":
                True,

            "version_required_on_read":
                True,

            "stability_required_on_read":
                True,

            "retention_required_on_read":
                True,

            "conflict_exception_context_required_on_read":
                True,

            "truth_status_required_on_read":
                True,

            "is_certified_fact":
                False,

            "is_learned_truth":
                False,

            "retrieval_performed":
                False,

            "memory_persisted":
                False,

            "runtime_reasoning_performed":
                False,

            "target_selected":
                False,

            "linking_decision_performed":
                False,

            "highlight_created":
                False,
        }

        retrieval_metadata_records.append(
            metadata
        )

        if retrieval_class == "ACTIVE_MEMORY":
            default_readable_memory_ids.append(
                memory_object_id
            )

        elif retrieval_class == "HELD_MEMORY":
            held_memory_ids.append(
                memory_object_id
            )

        elif retrieval_class == "BLOCKED_MEMORY":
            blocked_memory_ids.append(
                memory_object_id
            )

        elif retrieval_class == "CONTESTED_MEMORY":
            contested_memory_ids.append(
                memory_object_id
            )

        else:
            historical_memory_ids.append(
                memory_object_id
            )

    retrieval_metadata_records = tuple(
        retrieval_metadata_records
    )

    default_readable_memory_ids = tuple(
        default_readable_memory_ids
    )

    held_memory_ids = tuple(
        held_memory_ids
    )

    blocked_memory_ids = tuple(
        blocked_memory_ids
    )

    contested_memory_ids = tuple(
        contested_memory_ids
    )

    historical_memory_ids = tuple(
        historical_memory_ids
    )

    metadata_ids = tuple(
        item[
            "retrieval_metadata_id"
        ]
        for item in retrieval_metadata_records
    )

    if len(
        metadata_ids
    ) != len(
        set(metadata_ids)
    ):
        raise SemanticMemoryError(
            "Duplicate Semantic Memory retrieval metadata IDs."
        )

    read_contract = {
        "schema":
            "semantic_memory_retrieval_read_contract_v1",

        "default_runtime_read_class":
            "ACTIVE_MEMORY",

        "default_runtime_requires_stable_state":
            True,

        "default_runtime_requires_retain_state":
            True,

        "default_runtime_excludes_held_memory":
            True,

        "default_runtime_excludes_blocked_memory":
            True,

        "default_runtime_excludes_contested_memory":
            True,

        "default_runtime_excludes_weakened_memory":
            True,

        "default_runtime_excludes_superseded_memory":
            True,

        "default_runtime_excludes_retired_memory":
            True,

        "default_runtime_excludes_expired_memory":
            True,

        "held_memory_requires_explicit_read_class":
            True,

        "blocked_memory_requires_explicit_read_class":
            True,

        "contested_memory_requires_explicit_read_class":
            True,

        "historical_memory_requires_explicit_read_class":
            True,

        "all_reads_require_provenance":
            True,

        "all_reads_require_lineage":
            True,

        "all_reads_require_version":
            True,

        "all_reads_require_stability_state":
            True,

        "all_reads_require_retention_state":
            True,

        "all_reads_require_conflict_exception_context":
            True,

        "all_reads_require_truth_status":
            True,

        "retrieval_is_read_only":
            True,

        "retrieval_does_not_establish_truth":
            True,

        "retrieval_does_not_mutate_memory":
            True,

        "retrieval_does_not_mutate_learning_engine":
            True,

        "retrieval_does_not_mutate_graph":
            True,

        "retrieval_does_not_reclassify_conflict":
            True,

        "retrieval_does_not_rewrite_upstream_guard":
            True,

        "retrieval_does_not_create_targets":
            True,

        "retrieval_does_not_select_targets":
            True,

        "retrieval_does_not_score_targets":
            True,

        "retrieval_does_not_make_linking_decisions":
            True,

        "retrieval_does_not_create_highlights":
            True,

        "retrieval_does_not_perform_runtime_reasoning":
            True,
    }

    adapter_contract = {
        "schema":
            "semantic_memory_runtime_reader_adapter_contract_v1",

        "canonical_owner":
            "SEMANTIC_MEMORY",

        "runtime_access_mode":
            "READ_ONLY",

        "legacy_or_existing_store_may_serve_as_adapter":
            True,

        "adapter_must_not_override_canonical_contract":
            True,

        "adapter_must_preserve_retrieval_class":
            True,

        "adapter_must_preserve_provenance":
            True,

        "adapter_must_preserve_lineage":
            True,

        "adapter_must_preserve_version":
            True,

        "adapter_must_preserve_stability":
            True,

        "adapter_must_preserve_retention":
            True,

        "adapter_must_preserve_conflict_exception_context":
            True,

        "adapter_must_preserve_non_truth_status":
            True,

        "adapter_must_not_make_linking_decision":
            True,

        "adapter_must_not_select_target":
            True,

        "adapter_must_not_perform_semantic_reasoning":
            True,
    }

    bundle_payload = {
        "semantic_memory_lineage_root_id":
            semantic_memory_lineage_root_id,

        "retrieval_metadata_ids":
            list(
                metadata_ids
            ),

        "default_readable_memory_ids":
            list(
                default_readable_memory_ids
            ),

        "held_memory_ids":
            list(
                held_memory_ids
            ),

        "blocked_memory_ids":
            list(
                blocked_memory_ids
            ),

        "contested_memory_ids":
            list(
                contested_memory_ids
            ),

        "historical_memory_ids":
            list(
                historical_memory_ids
            ),
    }

    bundle_serialized = json.dumps(
        bundle_payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    bundle_digest = hashlib.sha256(
        bundle_serialized.encode("utf-8")
    ).hexdigest()

    retrieval_bundle = {
        "schema":
            "semantic_memory_retrieval_read_contract_bundle_v1",

        "retrieval_contract_bundle_id":
            "semanticmemoryretrievalcontractbundle:v1:"
            + bundle_digest,

        "retrieval_contract_bundle_digest":
            bundle_digest,

        "semantic_memory_lineage_root_id":
            semantic_memory_lineage_root_id,

        "retrieval_metadata_records":
            retrieval_metadata_records,

        "default_readable_memory_ids":
            default_readable_memory_ids,

        "held_memory_ids":
            held_memory_ids,

        "blocked_memory_ids":
            blocked_memory_ids,

        "contested_memory_ids":
            contested_memory_ids,

        "historical_memory_ids":
            historical_memory_ids,

        "read_contract":
            read_contract,

        "runtime_reader_adapter_contract":
            adapter_contract,

        "retrieval_policy":
            "PROVENANCE_AWARE_STATE_FILTERED_READ_ONLY_SEMANTIC_MEMORY_ACCESS",

        "retrieval_contract_defined":
            True,

        "retrieval_metadata_created":
            True,

        "live_retrieval_performed":
            False,

        "memory_persisted":
            False,

        "memory_mutated":
            False,

        "truth_adjudicated":
            False,

        "learning_engine_output_mutated":
            False,

        "graph_mutated":
            False,

        "conflict_reclassified":
            False,

        "upstream_guard_rewritten":
            False,

        "target_created":
            False,

        "target_selected":
            False,

        "target_scored":
            False,

        "runtime_reasoning_performed":
            False,

        "linking_decision_performed":
            False,

        "highlight_created":
            False,
    }

    return {
        "schema":
            "semantic_memory_retrieval_read_contract_result_v1",

        "semantic_memory_version":
            SEMANTIC_MEMORY_VERSION,

        "phase":
            SEMANTIC_MEMORY_PHASE,

        "patch":
            "4.6.28K",

        "status":
            "SEMANTIC_MEMORY_RETRIEVAL_READ_CONTRACT_DEFINED",

        "source_final_learning_engine_package_id":
            lineage_result.get(
                "source_final_learning_engine_package_id"
            ),

        "source_final_learning_engine_package_digest":
            lineage_result.get(
                "source_final_learning_engine_package_digest"
            ),

        "source_final_graph_id":
            lineage_result.get(
                "source_final_graph_id"
            ),

        "source_final_graph_digest":
            lineage_result.get(
                "source_final_graph_digest"
            ),

        "source_graph_snapshot_id":
            lineage_result.get(
                "source_graph_snapshot_id"
            ),

        "source_lineage_root_id":
            lineage_result.get(
                "source_lineage_root_id"
            ),

        "source_learning_lineage_root_id":
            lineage_result.get(
                "source_learning_lineage_root_id"
            ),

        "semantic_memory_lineage_root_id":
            semantic_memory_lineage_root_id,

        "semantic_memory_ownership_mutation_contract":
            copy.deepcopy(
                ownership_contract
            ),

        "semantic_memory_stability_retention_bundle":
            copy.deepcopy(
                retention_bundle
            ),

        "semantic_memory_provenance_lineage_bundle":
            copy.deepcopy(
                lineage_bundle
            ),

        "semantic_memory_retrieval_read_contract_bundle":
            retrieval_bundle,

        "certified_learning_engine_input_inspection":
            copy.deepcopy(
                inspection
            ),

        "processing_boundaries": {
            "semantic_memory_admission_performed":
                True,

            "semantic_memory_object_created":
                True,

            "memory_version_created":
                True,

            "conflict_exception_memory_preserved":
                True,

            "memory_retention_decision_performed":
                True,

            "memory_provenance_lineage_built":
                True,

            "memory_retrieval_read_contract_defined":
                True,

            "retrieval_metadata_created":
                True,

            "semantic_memory_written":
                False,

            "memory_persistence_performed":
                False,

            "memory_supersession_performed":
                False,

            "memory_retrieval_performed":
                False,

            "learning_output_promoted_to_truth":
                False,

            "learning_engine_output_mutated":
                False,

            "graph_mutation_performed":
                False,

            "authority_rescored":
                False,

            "claim_integrity_redecided":
                False,

            "conflict_reclassified":
                False,

            "upstream_guard_disposition_changed":
                False,

            "target_created":
                False,

            "target_selected":
                False,

            "target_scored":
                False,

            "runtime_reasoning_performed":
                False,

            "linking_decision_performed":
                False,

            "highlight_created":
                False,
        },

        "policy":
            "CERTIFIED_SEMANTIC_MEMORY_RETRIEVAL_READ_CONTRACT",

        "next":
            "final_semantic_memory_result",
    }

def build_final_semantic_memory_result_v1(
    retrieval_contract_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.28L ? Final Semantic Memory Result.

    Packages the fully constructed Semantic Memory chain into one
    canonical final artifact without fabricating persistence or live
    retrieval.

    The final package preserves:
    - ownership and mutation boundaries,
    - admitted learned knowledge,
    - Semantic Memory objects,
    - versioning/history,
    - conflict/exception context,
    - stability/retention,
    - provenance/lineage,
    - retrieval/read contracts,
    - explicit non-truth semantics.

    No upstream semantic state is rewritten.
    """

    if not isinstance(
        retrieval_contract_result,
        dict,
    ):
        raise SemanticMemoryError(
            "retrieval_contract_result must be a dictionary."
        )

    expected = {
        "schema":
            "semantic_memory_retrieval_read_contract_result_v1",

        "semantic_memory_version":
            SEMANTIC_MEMORY_VERSION,

        "phase":
            SEMANTIC_MEMORY_PHASE,

        "patch":
            "4.6.28K",

        "status":
            "SEMANTIC_MEMORY_RETRIEVAL_READ_CONTRACT_DEFINED",

        "policy":
            "CERTIFIED_SEMANTIC_MEMORY_RETRIEVAL_READ_CONTRACT",

        "next":
            "final_semantic_memory_result",
    }

    for key, expected_value in expected.items():

        if retrieval_contract_result.get(key) != expected_value:
            raise SemanticMemoryError(
                "Invalid 4.6.28K lifecycle field: "
                f"{key}"
            )

    ownership_contract = retrieval_contract_result.get(
        "semantic_memory_ownership_mutation_contract"
    )

    retention_bundle = retrieval_contract_result.get(
        "semantic_memory_stability_retention_bundle"
    )

    lineage_bundle = retrieval_contract_result.get(
        "semantic_memory_provenance_lineage_bundle"
    )

    retrieval_bundle = retrieval_contract_result.get(
        "semantic_memory_retrieval_read_contract_bundle"
    )

    inspection = retrieval_contract_result.get(
        "certified_learning_engine_input_inspection"
    )

    boundaries = retrieval_contract_result.get(
        "processing_boundaries"
    )

    for name, value in (
        (
            "semantic_memory_ownership_mutation_contract",
            ownership_contract,
        ),
        (
            "semantic_memory_stability_retention_bundle",
            retention_bundle,
        ),
        (
            "semantic_memory_provenance_lineage_bundle",
            lineage_bundle,
        ),
        (
            "semantic_memory_retrieval_read_contract_bundle",
            retrieval_bundle,
        ),
        (
            "certified_learning_engine_input_inspection",
            inspection,
        ),
        (
            "processing_boundaries",
            boundaries,
        ),
    ):
        if not isinstance(
            value,
            dict,
        ):
            raise SemanticMemoryError(
                f"{name} must be a dictionary."
            )

    if (
        ownership_contract.get("schema")
        != "semantic_memory_ownership_mutation_contract_v1"
    ):
        raise SemanticMemoryError(
            "Invalid Semantic Memory ownership contract schema."
        )

    if (
        retention_bundle.get("schema")
        != "semantic_memory_stability_retention_bundle_v1"
    ):
        raise SemanticMemoryError(
            "Invalid Semantic Memory retention bundle schema."
        )

    if (
        lineage_bundle.get("schema")
        != "semantic_memory_provenance_lineage_bundle_v1"
    ):
        raise SemanticMemoryError(
            "Invalid Semantic Memory provenance/lineage bundle schema."
        )

    if (
        retrieval_bundle.get("schema")
        != "semantic_memory_retrieval_read_contract_bundle_v1"
    ):
        raise SemanticMemoryError(
            "Invalid Semantic Memory retrieval/read bundle schema."
        )

    if (
        inspection.get("schema")
        != "semantic_memory_learning_engine_input_inspection_result_v1"
    ):
        raise SemanticMemoryError(
            "Invalid certified Learning Engine inspection schema."
        )

    if retention_bundle.get(
        "stability_retention_applied"
    ) is not True:
        raise SemanticMemoryError(
            "Semantic Memory stability/retention is incomplete."
        )

    if retention_bundle.get(
        "retention_decisions_finalized"
    ) is not True:
        raise SemanticMemoryError(
            "Semantic Memory retention decisions are incomplete."
        )

    if lineage_bundle.get(
        "provenance_complete"
    ) is not True:
        raise SemanticMemoryError(
            "Semantic Memory provenance is incomplete."
        )

    if lineage_bundle.get(
        "lineage_complete"
    ) is not True:
        raise SemanticMemoryError(
            "Semantic Memory lineage is incomplete."
        )

    if retrieval_bundle.get(
        "retrieval_contract_defined"
    ) is not True:
        raise SemanticMemoryError(
            "Semantic Memory retrieval contract is incomplete."
        )

    if retrieval_bundle.get(
        "retrieval_metadata_created"
    ) is not True:
        raise SemanticMemoryError(
            "Semantic Memory retrieval metadata is incomplete."
        )

    if retrieval_bundle.get(
        "live_retrieval_performed"
    ) is not False:
        raise SemanticMemoryError(
            "Live retrieval occurred before final certification."
        )

    for required_true in (
        "semantic_memory_admission_performed",
        "semantic_memory_object_created",
        "memory_version_created",
        "conflict_exception_memory_preserved",
        "memory_retention_decision_performed",
        "memory_provenance_lineage_built",
        "memory_retrieval_read_contract_defined",
        "retrieval_metadata_created",
    ):
        if boundaries.get(
            required_true
        ) is not True:
            raise SemanticMemoryError(
                "Required Semantic Memory stage is incomplete: "
                f"{required_true}"
            )

    for flag in (
        "semantic_memory_written",
        "memory_persistence_performed",
        "memory_supersession_performed",
        "memory_retrieval_performed",
        "learning_output_promoted_to_truth",
        "learning_engine_output_mutated",
        "graph_mutation_performed",
        "authority_rescored",
        "claim_integrity_redecided",
        "conflict_reclassified",
        "upstream_guard_disposition_changed",
        "target_created",
        "target_selected",
        "target_scored",
        "runtime_reasoning_performed",
        "linking_decision_performed",
        "highlight_created",
    ):
        if boundaries.get(flag) is not False:
            raise SemanticMemoryError(
                "Unsafe pre-final Semantic Memory state: "
                f"{flag}"
            )

    for flag in (
        "memory_persisted",
        "memory_mutated",
        "truth_adjudicated",
        "learning_engine_output_mutated",
        "graph_mutated",
        "conflict_reclassified",
        "upstream_guard_rewritten",
        "target_created",
        "target_selected",
        "target_scored",
        "runtime_reasoning_performed",
        "linking_decision_performed",
        "highlight_created",
    ):
        if retrieval_bundle.get(flag) is not False:
            raise SemanticMemoryError(
                "Unsafe final retrieval bundle state: "
                f"{flag}"
            )

    semantic_memory_lineage_root_id = (
        retrieval_contract_result.get(
            "semantic_memory_lineage_root_id"
        )
    )

    source_learning_engine_package_id = (
        retrieval_contract_result.get(
            "source_final_learning_engine_package_id"
        )
    )

    source_learning_engine_package_digest = (
        retrieval_contract_result.get(
            "source_final_learning_engine_package_digest"
        )
    )

    source_final_graph_id = (
        retrieval_contract_result.get(
            "source_final_graph_id"
        )
    )

    source_final_graph_digest = (
        retrieval_contract_result.get(
            "source_final_graph_digest"
        )
    )

    source_graph_snapshot_id = (
        retrieval_contract_result.get(
            "source_graph_snapshot_id"
        )
    )

    source_graph_lineage_root_id = (
        retrieval_contract_result.get(
            "source_lineage_root_id"
        )
    )

    source_learning_lineage_root_id = (
        retrieval_contract_result.get(
            "source_learning_lineage_root_id"
        )
    )

    for name, value in (
        (
            "semantic_memory_lineage_root_id",
            semantic_memory_lineage_root_id,
        ),
        (
            "source_final_learning_engine_package_id",
            source_learning_engine_package_id,
        ),
        (
            "source_final_learning_engine_package_digest",
            source_learning_engine_package_digest,
        ),
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
            source_graph_lineage_root_id,
        ),
        (
            "source_learning_lineage_root_id",
            source_learning_lineage_root_id,
        ),
    ):
        if not isinstance(
            value,
            str,
        ) or not value:
            raise SemanticMemoryError(
                "Missing final Semantic Memory provenance: "
                f"{name}"
            )

    lineage_objects = lineage_bundle.get(
        "lineage_bound_memory_objects"
    )

    retrieval_metadata = retrieval_bundle.get(
        "retrieval_metadata_records"
    )

    if not isinstance(
        lineage_objects,
        tuple,
    ):
        raise SemanticMemoryError(
            "lineage_bound_memory_objects must be a tuple."
        )

    if not isinstance(
        retrieval_metadata,
        tuple,
    ):
        raise SemanticMemoryError(
            "retrieval_metadata_records must be a tuple."
        )

    if not lineage_objects:
        raise SemanticMemoryError(
            "Final Semantic Memory cannot be empty."
        )

    if len(
        lineage_objects
    ) != len(
        retrieval_metadata
    ):
        raise SemanticMemoryError(
            "Memory object/retrieval metadata count mismatch."
        )

    metadata_by_object_id = {}

    for metadata in retrieval_metadata:

        if not isinstance(
            metadata,
            dict,
        ):
            raise SemanticMemoryError(
                "Retrieval metadata must be a dictionary."
            )

        if (
            metadata.get("schema")
            != "semantic_memory_retrieval_metadata_v1"
        ):
            raise SemanticMemoryError(
                "Invalid retrieval metadata schema."
            )

        memory_object_id = metadata.get(
            "memory_object_id"
        )

        if (
            not isinstance(
                memory_object_id,
                str,
            )
            or not memory_object_id
        ):
            raise SemanticMemoryError(
                "Retrieval metadata memory object ID is missing."
            )

        if memory_object_id in metadata_by_object_id:
            raise SemanticMemoryError(
                "Duplicate retrieval metadata for memory object."
            )

        metadata_by_object_id[
            memory_object_id
        ] = metadata

    final_memory_objects = []

    for memory_object in lineage_objects:

        if not isinstance(
            memory_object,
            dict,
        ):
            raise SemanticMemoryError(
                "Final Semantic Memory object must be a dictionary."
            )

        if (
            memory_object.get("schema")
            != "semantic_memory_object_v1"
        ):
            raise SemanticMemoryError(
                "Invalid final Semantic Memory object schema."
            )

        memory_object_id = memory_object.get(
            "memory_object_id"
        )

        if memory_object_id not in metadata_by_object_id:
            raise SemanticMemoryError(
                "Retrieval metadata missing for memory object."
            )

        metadata = metadata_by_object_id[
            memory_object_id
        ]

        if memory_object.get(
            "provenance_complete"
        ) is not True:
            raise SemanticMemoryError(
                "Final memory object provenance is incomplete."
            )

        if memory_object.get(
            "lineage_complete"
        ) is not True:
            raise SemanticMemoryError(
                "Final memory object lineage is incomplete."
            )

        if memory_object.get(
            "retention_decision_finalized"
        ) is not True:
            raise SemanticMemoryError(
                "Final memory object retention is incomplete."
            )

        if memory_object.get(
            "memory_persisted"
        ) is not False:
            raise SemanticMemoryError(
                "Persistence must not be fabricated."
            )

        if metadata.get(
            "retrieval_performed"
        ) is not False:
            raise SemanticMemoryError(
                "Live retrieval must not be fabricated."
            )

        if memory_object.get(
            "is_certified_fact"
        ) is not False:
            raise SemanticMemoryError(
                "Semantic Memory cannot be certified truth."
            )

        if memory_object.get(
            "is_learned_truth"
        ) is not False:
            raise SemanticMemoryError(
                "Semantic Memory cannot be learned truth."
            )

        final_memory_objects.append(
            {
                **copy.deepcopy(
                    memory_object
                ),

                "retrieval_metadata_id":
                    metadata[
                        "retrieval_metadata_id"
                    ],

                "retrieval_class":
                    metadata[
                        "retrieval_class"
                    ],

                "default_runtime_readable":
                    metadata[
                        "default_runtime_readable"
                    ],

                "explicit_state_aware_read_required":
                    metadata[
                        "explicit_state_aware_read_required"
                    ],

                "final_semantic_memory_member":
                    True,

                "memory_persisted":
                    False,

                "retrieval_performed":
                    False,

                "is_certified_fact":
                    False,

                "is_learned_truth":
                    False,
            }
        )

    final_memory_objects = tuple(
        final_memory_objects
    )

    final_memory_object_ids = tuple(
        item[
            "memory_object_id"
        ]
        for item in final_memory_objects
    )

    if len(
        final_memory_object_ids
    ) != len(
        set(final_memory_object_ids)
    ):
        raise SemanticMemoryError(
            "Duplicate final Semantic Memory object IDs."
        )

    default_readable_ids = tuple(
        retrieval_bundle.get(
            "default_readable_memory_ids",
            (),
        )
    )

    held_ids = tuple(
        retrieval_bundle.get(
            "held_memory_ids",
            (),
        )
    )

    blocked_ids = tuple(
        retrieval_bundle.get(
            "blocked_memory_ids",
            (),
        )
    )

    contested_ids = tuple(
        retrieval_bundle.get(
            "contested_memory_ids",
            (),
        )
    )

    historical_ids = tuple(
        retrieval_bundle.get(
            "historical_memory_ids",
            (),
        )
    )

    partition_sets = (
        set(default_readable_ids),
        set(held_ids),
        set(blocked_ids),
        set(contested_ids),
        set(historical_ids),
    )

    for index, left in enumerate(
        partition_sets
    ):
        for right in partition_sets[
            index + 1:
        ]:
            if left & right:
                raise SemanticMemoryError(
                    "Final Semantic Memory retrieval partitions overlap."
                )

    classified_ids = set().union(
        *partition_sets
    )

    if classified_ids != set(
        final_memory_object_ids
    ):
        raise SemanticMemoryError(
            "Final Semantic Memory retrieval classification is incomplete."
        )

    final_contract = {
        "schema":
            "final_semantic_memory_contract_v1",

        "semantic_memory_owns_persistent_learned_memory":
            True,

        "final_memory_is_versioned":
            True,

        "final_memory_preserves_history":
            True,

        "final_memory_preserves_conflicts":
            True,

        "final_memory_preserves_exceptions":
            True,

        "final_memory_preserves_provenance":
            True,

        "final_memory_preserves_lineage":
            True,

        "final_memory_preserves_retention_state":
            True,

        "final_memory_preserves_retrieval_class":
            True,

        "default_runtime_reads_are_state_filtered":
            True,

        "held_blocked_and_non_active_memory_not_default_readable":
            True,

        "memory_is_not_certified_truth":
            True,

        "memory_is_not_learned_truth":
            True,

        "persistence_must_use_semantic_memory_contract":
            True,

        "persistence_must_preserve_versions":
            True,

        "persistence_must_preserve_history":
            True,

        "persistence_must_preserve_provenance":
            True,

        "persistence_must_preserve_lineage":
            True,

        "persistence_must_preserve_conflict_exception_context":
            True,

        "persistence_must_preserve_non_truth_status":
            True,

        "runtime_readers_must_use_retrieval_contract":
            True,

        "runtime_readers_are_read_only":
            True,

        "final_memory_does_not_rewrite_learning_engine":
            True,

        "final_memory_does_not_rewrite_graph":
            True,

        "final_memory_does_not_reclassify_conflict":
            True,

        "final_memory_does_not_rewrite_upstream_guard":
            True,

        "final_memory_does_not_create_targets":
            True,

        "final_memory_does_not_select_targets":
            True,

        "final_memory_does_not_score_targets":
            True,

        "final_memory_does_not_make_linking_decisions":
            True,

        "final_memory_does_not_create_highlights":
            True,

        "final_memory_does_not_perform_runtime_reasoning":
            True,
    }

    package_payload = {
        "semantic_memory_lineage_root_id":
            semantic_memory_lineage_root_id,

        "final_memory_object_ids":
            list(
                final_memory_object_ids
            ),

        "default_readable_memory_ids":
            list(
                default_readable_ids
            ),

        "held_memory_ids":
            list(
                held_ids
            ),

        "blocked_memory_ids":
            list(
                blocked_ids
            ),

        "contested_memory_ids":
            list(
                contested_ids
            ),

        "historical_memory_ids":
            list(
                historical_ids
            ),

        "source_learning_engine_package_id":
            source_learning_engine_package_id,

        "source_final_graph_id":
            source_final_graph_id,

        "retrieval_contract_bundle_id":
            retrieval_bundle[
                "retrieval_contract_bundle_id"
            ],
    }

    package_serialized = json.dumps(
        package_payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    package_digest = hashlib.sha256(
        package_serialized.encode("utf-8")
    ).hexdigest()

    final_package = {
        "schema":
            "final_semantic_memory_package_v1",

        "final_semantic_memory_package_id":
            "finalsemanticmemory:v1:"
            + package_digest,

        "final_semantic_memory_package_digest":
            package_digest,

        "semantic_memory_lineage_root_id":
            semantic_memory_lineage_root_id,

        "source_final_learning_engine_package_id":
            source_learning_engine_package_id,

        "source_final_learning_engine_package_digest":
            source_learning_engine_package_digest,

        "source_learning_lineage_root_id":
            source_learning_lineage_root_id,

        "source_final_graph_id":
            source_final_graph_id,

        "source_final_graph_digest":
            source_final_graph_digest,

        "source_graph_snapshot_id":
            source_graph_snapshot_id,

        "source_graph_lineage_root_id":
            source_graph_lineage_root_id,

        "final_memory_objects":
            final_memory_objects,

        "default_readable_memory_ids":
            default_readable_ids,

        "held_memory_ids":
            held_ids,

        "blocked_memory_ids":
            blocked_ids,

        "contested_memory_ids":
            contested_ids,

        "historical_memory_ids":
            historical_ids,

        "semantic_memory_ownership_mutation_contract":
            copy.deepcopy(
                ownership_contract
            ),

        "semantic_memory_stability_retention_bundle":
            copy.deepcopy(
                retention_bundle
            ),

        "semantic_memory_provenance_lineage_bundle":
            copy.deepcopy(
                lineage_bundle
            ),

        "semantic_memory_retrieval_read_contract_bundle":
            copy.deepcopy(
                retrieval_bundle
            ),

        "final_semantic_memory_contract":
            final_contract,

        "final_memory_object_count":
            len(
                final_memory_objects
            ),

        "final_policy":
            "CERTIFIED_FINAL_SEMANTIC_MEMORY_FOR_PERSISTENCE_AND_DOWNSTREAM_READ_HANDOFF",

        "semantic_memory_complete":
            True,

        "persistence_contract_ready":
            True,

        "runtime_read_contract_ready":
            True,

        "explainability_handoff_ready":
            True,

        "memory_persisted":
            False,

        "semantic_memory_written":
            False,

        "live_retrieval_performed":
            False,

        "truth_adjudicated":
            False,

        "learning_output_promoted_to_truth":
            False,

        "learning_engine_output_mutated":
            False,

        "graph_mutated":
            False,

        "authority_rescored":
            False,

        "claim_integrity_redecided":
            False,

        "conflict_reclassified":
            False,

        "upstream_guard_rewritten":
            False,

        "target_created":
            False,

        "target_selected":
            False,

        "target_scored":
            False,

        "runtime_reasoning_performed":
            False,

        "linking_decision_performed":
            False,

        "highlight_created":
            False,
    }

    return {
        "schema":
            "final_semantic_memory_result_v1",

        "semantic_memory_version":
            SEMANTIC_MEMORY_VERSION,

        "phase":
            SEMANTIC_MEMORY_PHASE,

        "patch":
            "4.6.28L",

        "status":
            "FINAL_SEMANTIC_MEMORY_RESULT_BUILT",

        "final_semantic_memory_package":
            final_package,

        "processing_boundaries": {
            "semantic_memory_admission_performed":
                True,

            "semantic_memory_object_created":
                True,

            "memory_version_created":
                True,

            "conflict_exception_memory_preserved":
                True,

            "memory_retention_decision_performed":
                True,

            "memory_provenance_lineage_built":
                True,

            "memory_retrieval_read_contract_defined":
                True,

            "retrieval_metadata_created":
                True,

            "final_semantic_memory_result_built":
                True,

            "semantic_memory_written":
                False,

            "memory_persistence_performed":
                False,

            "memory_supersession_performed":
                False,

            "memory_retrieval_performed":
                False,

            "learning_output_promoted_to_truth":
                False,

            "learning_engine_output_mutated":
                False,

            "graph_mutation_performed":
                False,

            "authority_rescored":
                False,

            "claim_integrity_redecided":
                False,

            "conflict_reclassified":
                False,

            "upstream_guard_disposition_changed":
                False,

            "target_created":
                False,

            "target_selected":
                False,

            "target_scored":
                False,

            "runtime_reasoning_performed":
                False,

            "linking_decision_performed":
                False,

            "highlight_created":
                False,
        },

        "policy":
            "CERTIFIED_FINAL_SEMANTIC_MEMORY_RESULT",

        "next":
            "full_semantic_memory_hard_certification",
    }

def certify_full_semantic_memory_v1(
    final_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.28M ? Full Semantic Memory Hard Certification.

    Performs the final end-to-end hard certification of the canonical
    Semantic Memory chain.

    This certification confirms that the final Semantic Memory package
    is structurally complete, provenance-preserving, state-filtered,
    non-truth, persistence-ready, read-contract-ready, and free of
    forbidden upstream/downstream semantic side effects.

    It does not persist memory or perform live retrieval.
    """

    if not isinstance(
        final_result,
        dict,
    ):
        raise SemanticMemoryError(
            "final_result must be a dictionary."
        )

    expected = {
        "schema":
            "final_semantic_memory_result_v1",

        "semantic_memory_version":
            SEMANTIC_MEMORY_VERSION,

        "phase":
            SEMANTIC_MEMORY_PHASE,

        "patch":
            "4.6.28L",

        "status":
            "FINAL_SEMANTIC_MEMORY_RESULT_BUILT",

        "policy":
            "CERTIFIED_FINAL_SEMANTIC_MEMORY_RESULT",

        "next":
            "full_semantic_memory_hard_certification",
    }

    for key, expected_value in expected.items():

        if final_result.get(key) != expected_value:
            raise SemanticMemoryError(
                "Invalid 4.6.28L lifecycle field: "
                f"{key}"
            )

    final_package = final_result.get(
        "final_semantic_memory_package"
    )

    boundaries = final_result.get(
        "processing_boundaries"
    )

    if not isinstance(
        final_package,
        dict,
    ):
        raise SemanticMemoryError(
            "Final Semantic Memory package is missing."
        )

    if not isinstance(
        boundaries,
        dict,
    ):
        raise SemanticMemoryError(
            "Final Semantic Memory processing boundaries are missing."
        )

    if (
        final_package.get("schema")
        != "final_semantic_memory_package_v1"
    ):
        raise SemanticMemoryError(
            "Invalid final Semantic Memory package schema."
        )

    if (
        final_package.get("final_policy")
        != "CERTIFIED_FINAL_SEMANTIC_MEMORY_FOR_PERSISTENCE_AND_DOWNSTREAM_READ_HANDOFF"
    ):
        raise SemanticMemoryError(
            "Invalid final Semantic Memory package policy."
        )

    if final_package.get(
        "semantic_memory_complete"
    ) is not True:
        raise SemanticMemoryError(
            "Semantic Memory package is incomplete."
        )

    if final_package.get(
        "persistence_contract_ready"
    ) is not True:
        raise SemanticMemoryError(
            "Semantic Memory persistence contract is not ready."
        )

    if final_package.get(
        "runtime_read_contract_ready"
    ) is not True:
        raise SemanticMemoryError(
            "Semantic Memory runtime read contract is not ready."
        )

    if final_package.get(
        "explainability_handoff_ready"
    ) is not True:
        raise SemanticMemoryError(
            "Semantic Memory Explainability handoff is not ready."
        )

    final_contract = final_package.get(
        "final_semantic_memory_contract"
    )

    if not isinstance(
        final_contract,
        dict,
    ):
        raise SemanticMemoryError(
            "Final Semantic Memory contract is missing."
        )

    if (
        final_contract.get("schema")
        != "final_semantic_memory_contract_v1"
    ):
        raise SemanticMemoryError(
            "Invalid final Semantic Memory contract schema."
        )

    required_contract_true = (
        "semantic_memory_owns_persistent_learned_memory",
        "final_memory_is_versioned",
        "final_memory_preserves_history",
        "final_memory_preserves_conflicts",
        "final_memory_preserves_exceptions",
        "final_memory_preserves_provenance",
        "final_memory_preserves_lineage",
        "final_memory_preserves_retention_state",
        "final_memory_preserves_retrieval_class",
        "default_runtime_reads_are_state_filtered",
        "held_blocked_and_non_active_memory_not_default_readable",
        "memory_is_not_certified_truth",
        "memory_is_not_learned_truth",
        "persistence_must_use_semantic_memory_contract",
        "persistence_must_preserve_versions",
        "persistence_must_preserve_history",
        "persistence_must_preserve_provenance",
        "persistence_must_preserve_lineage",
        "persistence_must_preserve_conflict_exception_context",
        "persistence_must_preserve_non_truth_status",
        "runtime_readers_must_use_retrieval_contract",
        "runtime_readers_are_read_only",
        "final_memory_does_not_rewrite_learning_engine",
        "final_memory_does_not_rewrite_graph",
        "final_memory_does_not_reclassify_conflict",
        "final_memory_does_not_rewrite_upstream_guard",
        "final_memory_does_not_create_targets",
        "final_memory_does_not_select_targets",
        "final_memory_does_not_score_targets",
        "final_memory_does_not_make_linking_decisions",
        "final_memory_does_not_create_highlights",
        "final_memory_does_not_perform_runtime_reasoning",
    )

    for flag in required_contract_true:

        if final_contract.get(flag) is not True:
            raise SemanticMemoryError(
                "Final Semantic Memory contract drift: "
                f"{flag}"
            )

    required_package_false = (
        "memory_persisted",
        "semantic_memory_written",
        "live_retrieval_performed",
        "truth_adjudicated",
        "learning_output_promoted_to_truth",
        "learning_engine_output_mutated",
        "graph_mutated",
        "authority_rescored",
        "claim_integrity_redecided",
        "conflict_reclassified",
        "upstream_guard_rewritten",
        "target_created",
        "target_selected",
        "target_scored",
        "runtime_reasoning_performed",
        "linking_decision_performed",
        "highlight_created",
    )

    for flag in required_package_false:

        if final_package.get(flag) is not False:
            raise SemanticMemoryError(
                "Unsafe final Semantic Memory package state: "
                f"{flag}"
            )

    required_boundary_true = (
        "semantic_memory_admission_performed",
        "semantic_memory_object_created",
        "memory_version_created",
        "conflict_exception_memory_preserved",
        "memory_retention_decision_performed",
        "memory_provenance_lineage_built",
        "memory_retrieval_read_contract_defined",
        "retrieval_metadata_created",
        "final_semantic_memory_result_built",
    )

    for flag in required_boundary_true:

        if boundaries.get(flag) is not True:
            raise SemanticMemoryError(
                "Required Semantic Memory stage missing: "
                f"{flag}"
            )

    required_boundary_false = (
        "semantic_memory_written",
        "memory_persistence_performed",
        "memory_supersession_performed",
        "memory_retrieval_performed",
        "learning_output_promoted_to_truth",
        "learning_engine_output_mutated",
        "graph_mutation_performed",
        "authority_rescored",
        "claim_integrity_redecided",
        "conflict_reclassified",
        "upstream_guard_disposition_changed",
        "target_created",
        "target_selected",
        "target_scored",
        "runtime_reasoning_performed",
        "linking_decision_performed",
        "highlight_created",
    )

    for flag in required_boundary_false:

        if boundaries.get(flag) is not False:
            raise SemanticMemoryError(
                "Unsafe final Semantic Memory boundary state: "
                f"{flag}"
            )

    final_memory_objects = final_package.get(
        "final_memory_objects"
    )

    if not isinstance(
        final_memory_objects,
        tuple,
    ):
        raise SemanticMemoryError(
            "final_memory_objects must be a tuple."
        )

    if not final_memory_objects:
        raise SemanticMemoryError(
            "Final Semantic Memory package cannot be empty."
        )

    object_ids = []

    for memory_object in final_memory_objects:

        if not isinstance(
            memory_object,
            dict,
        ):
            raise SemanticMemoryError(
                "Final Semantic Memory object must be a dictionary."
            )

        if (
            memory_object.get("schema")
            != "semantic_memory_object_v1"
        ):
            raise SemanticMemoryError(
                "Invalid final Semantic Memory object schema."
            )

        memory_object_id = memory_object.get(
            "memory_object_id"
        )

        if (
            not isinstance(
                memory_object_id,
                str,
            )
            or not memory_object_id
        ):
            raise SemanticMemoryError(
                "Final Semantic Memory object ID is missing."
            )

        object_ids.append(
            memory_object_id
        )

        if memory_object.get(
            "final_semantic_memory_member"
        ) is not True:
            raise SemanticMemoryError(
                "Memory object is not marked as a final package member."
            )

        if memory_object.get(
            "provenance_complete"
        ) is not True:
            raise SemanticMemoryError(
                "Final memory object provenance is incomplete."
            )

        if memory_object.get(
            "lineage_complete"
        ) is not True:
            raise SemanticMemoryError(
                "Final memory object lineage is incomplete."
            )

        if memory_object.get(
            "retention_decision_finalized"
        ) is not True:
            raise SemanticMemoryError(
                "Final memory object retention is incomplete."
            )

        if memory_object.get(
            "memory_persisted"
        ) is not False:
            raise SemanticMemoryError(
                "Persistence was fabricated on final memory object."
            )

        if memory_object.get(
            "retrieval_performed"
        ) is not False:
            raise SemanticMemoryError(
                "Live retrieval was fabricated on final memory object."
            )

        if memory_object.get(
            "is_certified_fact"
        ) is not False:
            raise SemanticMemoryError(
                "Final memory object cannot be certified truth."
            )

        if memory_object.get(
            "is_learned_truth"
        ) is not False:
            raise SemanticMemoryError(
                "Final memory object cannot be learned truth."
            )

        retrieval_class = memory_object.get(
            "retrieval_class"
        )

        default_readable = memory_object.get(
            "default_runtime_readable"
        )

        if retrieval_class == "ACTIVE_MEMORY":

            if default_readable is not True:
                raise SemanticMemoryError(
                    "ACTIVE_MEMORY must be default-readable."
                )

            if memory_object.get(
                "stability_state"
            ) != "STABLE":
                raise SemanticMemoryError(
                    "Default-readable ACTIVE_MEMORY must be STABLE."
                )

            if memory_object.get(
                "retention_state"
            ) != "RETAIN":
                raise SemanticMemoryError(
                    "Default-readable ACTIVE_MEMORY must be RETAIN."
                )

        else:

            if default_readable is not False:
                raise SemanticMemoryError(
                    "Non-active memory cannot be default-readable."
                )

            if memory_object.get(
                "explicit_state_aware_read_required"
            ) is not True:
                raise SemanticMemoryError(
                    "Non-active memory requires explicit state-aware read."
                )

    if len(
        object_ids
    ) != len(
        set(object_ids)
    ):
        raise SemanticMemoryError(
            "Duplicate final Semantic Memory object IDs."
        )

    default_ids = tuple(
        final_package.get(
            "default_readable_memory_ids",
            (),
        )
    )

    held_ids = tuple(
        final_package.get(
            "held_memory_ids",
            (),
        )
    )

    blocked_ids = tuple(
        final_package.get(
            "blocked_memory_ids",
            (),
        )
    )

    contested_ids = tuple(
        final_package.get(
            "contested_memory_ids",
            (),
        )
    )

    historical_ids = tuple(
        final_package.get(
            "historical_memory_ids",
            (),
        )
    )

    partitions = (
        set(default_ids),
        set(held_ids),
        set(blocked_ids),
        set(contested_ids),
        set(historical_ids),
    )

    for index, left in enumerate(
        partitions
    ):

        for right in partitions[
            index + 1:
        ]:

            if left & right:
                raise SemanticMemoryError(
                    "Final Semantic Memory retrieval partitions overlap."
                )

    classified_ids = set().union(
        *partitions
    )

    if classified_ids != set(
        object_ids
    ):
        raise SemanticMemoryError(
            "Final Semantic Memory retrieval classification is incomplete."
        )

    final_package_id = final_package.get(
        "final_semantic_memory_package_id"
    )

    final_package_digest = final_package.get(
        "final_semantic_memory_package_digest"
    )

    semantic_memory_lineage_root_id = (
        final_package.get(
            "semantic_memory_lineage_root_id"
        )
    )

    for name, value in (
        (
            "final_semantic_memory_package_id",
            final_package_id,
        ),
        (
            "final_semantic_memory_package_digest",
            final_package_digest,
        ),
        (
            "semantic_memory_lineage_root_id",
            semantic_memory_lineage_root_id,
        ),
    ):

        if (
            not isinstance(
                value,
                str,
            )
            or not value
        ):
            raise SemanticMemoryError(
                "Missing final certification identity: "
                f"{name}"
            )

    return {
        "schema":
            "full_semantic_memory_hard_certification_result_v1",

        "semantic_memory_version":
            SEMANTIC_MEMORY_VERSION,

        "phase":
            SEMANTIC_MEMORY_PHASE,

        "patch":
            "4.6.28M",

        "status":
            "FULL_SEMANTIC_MEMORY_HARD_CERTIFIED",

        "certified":
            True,

        "stage_count":
            13,

        "final_semantic_memory_package_id":
            final_package_id,

        "final_semantic_memory_package_digest":
            final_package_digest,

        "semantic_memory_lineage_root_id":
            semantic_memory_lineage_root_id,

        "final_semantic_memory_result":
            copy.deepcopy(
                final_result
            ),

        "persistence_contract_ready":
            True,

        "runtime_read_contract_ready":
            True,

        "explainability_handoff_ready":
            True,

        "semantic_memory_written":
            False,

        "memory_persistence_performed":
            False,

        "memory_retrieval_performed":
            False,

        "learning_output_promoted_to_truth":
            False,

        "learning_engine_output_mutated":
            False,

        "graph_mutation_performed":
            False,

        "authority_rescored":
            False,

        "claim_integrity_redecided":
            False,

        "conflict_reclassified":
            False,

        "upstream_guard_disposition_changed":
            False,

        "target_created":
            False,

        "target_selected":
            False,

        "target_scored":
            False,

        "runtime_reasoning_performed":
            False,

        "linking_decision_performed":
            False,

        "highlight_created":
            False,

        "memory_is_certified_truth":
            False,

        "memory_is_learned_truth":
            False,

        "input_immutable":
            True,

        "certification_policy":
            "FULL_END_TO_END_SEMANTIC_MEMORY_HARD_CERTIFICATION",

        "next":
            "explainability",
    }
