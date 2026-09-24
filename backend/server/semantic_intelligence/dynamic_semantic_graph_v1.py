"""
LinkCraftor Semantic Intelligence
4.6.26 ? Dynamic Semantic Graph

Canonical responsibility:
Construct and maintain the certified dynamic semantic graph from
upstream semantic intelligence outputs while preserving provenance,
Authority, claim integrity, conflict state, and canonical ownership.

This component does not:
- write Semantic Memory,
- perform downstream reasoning,
- resolve links,
- score target pages,
- create editor highlights,
- select final targets,
- make linking decisions.
"""

from __future__ import annotations

import copy
from typing import Any


DYNAMIC_SEMANTIC_GRAPH_VERSION = (
    "dynamic_semantic_graph_v1"
)

DYNAMIC_SEMANTIC_GRAPH_PHASE = "4.6.26"


class DynamicSemanticGraphError(ValueError):
    """Raised when Dynamic Semantic Graph contracts are violated."""


def inspect_certified_claim_integrity_input_v1(
    claim_integrity_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.26A ? Certified Claim Integrity Input Inspection.

    Accepts only the certified 4.6.25K Final Claim Integrity Result.

    Inspection only.

    This stage does not:
    - create graph nodes,
    - create graph edges,
    - mutate graph state,
    - reassess claim support,
    - redetect conflicts,
    - redecide claim integrity,
    - alter guard dispositions,
    - rescore Authority,
    - write Semantic Memory,
    - select targets,
    - make linking decisions.
    """

    if not isinstance(
        claim_integrity_result,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "claim_integrity_result must be a dictionary."
        )

    expected_lifecycle = {
        "schema":
            "final_claim_integrity_result_v1",

        "claim_integrity_conflict_version":
            "claim_integrity_conflict_v1",

        "phase":
            "4.6.25",

        "patch":
            "4.6.25K",

        "status":
            "FINAL_CLAIM_INTEGRITY_RESULT_BUILT",

        "policy":
            "CERTIFIED_FINAL_CLAIM_INTEGRITY_RESULT",

        "next":
            "full_claim_integrity_conflict_hard_certification",
    }

    for key, expected in expected_lifecycle.items():

        if (
            claim_integrity_result.get(key)
            != expected
        ):
            raise DynamicSemanticGraphError(
                "Invalid certified Claim Integrity input "
                f"lifecycle field: {key}"
            )

    package = claim_integrity_result.get(
        "final_claim_integrity_package"
    )

    if not isinstance(
        package,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "final_claim_integrity_package must be a dictionary."
        )

    if (
        package.get("schema")
        != "final_claim_integrity_result_package_v1"
    ):
        raise DynamicSemanticGraphError(
            "Invalid final Claim Integrity package schema."
        )

    if (
        package.get("final_policy")
        !=
        "CERTIFIED_CLAIM_INTEGRITY_RESULT_FOR_DOWNSTREAM_CONSUMPTION"
    ):
        raise DynamicSemanticGraphError(
            "Final Claim Integrity package is not certified "
            "for downstream consumption."
        )

    required_package_true = (
        "authority_preserved",
        "support_preserved",
        "conflict_preserved",
        "integrity_preserved",
        "guard_preserved",
        "provenance_preserved",
        "active_target_set_ownership_preserved",
        "external_authority_partition_preserved",
        "external_route_eligibility_preserved",
        "external_resolver_ownership_preserved",
    )

    for flag in required_package_true:

        if package.get(flag) is not True:
            raise DynamicSemanticGraphError(
                "Claim Integrity package preservation "
                f"contract violated: {flag}"
            )

    records = claim_integrity_result.get(
        "final_claim_integrity_records"
    )

    if not isinstance(
        records,
        list,
    ):
        raise DynamicSemanticGraphError(
            "final_claim_integrity_records must be a list."
        )

    if (
        claim_integrity_result.get(
            "final_claim_integrity_record_count"
        )
        != len(records)
    ):
        raise DynamicSemanticGraphError(
            "Final Claim Integrity record count mismatch."
        )

    if (
        package.get("record_count")
        != len(records)
    ):
        raise DynamicSemanticGraphError(
            "Final Claim Integrity package count mismatch."
        )

    allowed_integrity_states = {
        "WELL_SUPPORTED",
        "SUPPORTED",
        "PARTIALLY_SUPPORTED",
        "DISPUTED",
        "CONTRADICTED",
        "INSUFFICIENT_EVIDENCE",
        "UNRESOLVED",
        "BLOCKED",
    }

    allowed_guard_dispositions = {
        "PASS",
        "CAUTION",
        "HOLD",
        "BLOCK",
    }

    inspected_records = []
    seen_claim_ids = set()
    seen_final_ids = set()

    for record in records:

        if not isinstance(
            record,
            dict,
        ):
            raise DynamicSemanticGraphError(
                "Final Claim Integrity record must be a dictionary."
            )

        if (
            record.get("schema")
            != "final_claim_integrity_record_v1"
        ):
            raise DynamicSemanticGraphError(
                "Invalid Final Claim Integrity record schema."
            )

        claim_id = record.get(
            "claim_id"
        )

        final_id = record.get(
            "final_claim_integrity_id"
        )

        final_digest = record.get(
            "final_claim_integrity_digest"
        )

        if (
            not isinstance(claim_id, str)
            or not claim_id.strip()
        ):
            raise DynamicSemanticGraphError(
                "Final Claim Integrity record requires claim_id."
            )

        if claim_id in seen_claim_ids:
            raise DynamicSemanticGraphError(
                "Duplicate claim_id detected."
            )

        seen_claim_ids.add(
            claim_id
        )

        if (
            not isinstance(final_id, str)
            or not final_id.startswith(
                "claimintegrity:v1:"
            )
        ):
            raise DynamicSemanticGraphError(
                "Invalid final_claim_integrity_id."
            )

        if final_id in seen_final_ids:
            raise DynamicSemanticGraphError(
                "Duplicate final_claim_integrity_id detected."
            )

        seen_final_ids.add(
            final_id
        )

        if (
            not isinstance(final_digest, str)
            or len(final_digest) != 64
        ):
            raise DynamicSemanticGraphError(
                "Invalid final_claim_integrity_digest."
            )

        integrity_state = record.get(
            "claim_integrity_state"
        )

        guard_disposition = record.get(
            "guard_disposition"
        )

        downstream_eligible = record.get(
            "downstream_claim_eligible"
        )

        if integrity_state not in allowed_integrity_states:
            raise DynamicSemanticGraphError(
                "Unsupported claim integrity state."
            )

        if guard_disposition not in allowed_guard_dispositions:
            raise DynamicSemanticGraphError(
                "Unsupported guard disposition."
            )

        if not isinstance(
            downstream_eligible,
            bool,
        ):
            raise DynamicSemanticGraphError(
                "downstream_claim_eligible must be boolean."
            )

        expected_eligibility = (
            guard_disposition
            in {
                "PASS",
                "CAUTION",
            }
        )

        if (
            downstream_eligible
            is not expected_eligibility
        ):
            raise DynamicSemanticGraphError(
                "Guard disposition and downstream eligibility drift."
            )

        authority_reference = record.get(
            "authority_reference"
        )

        evidence_trace = record.get(
            "evidence_trace"
        )

        conflict_trace = record.get(
            "conflict_trace"
        )

        conflict_summary = record.get(
            "conflict_summary"
        )

        if not isinstance(
            authority_reference,
            dict,
        ):
            raise DynamicSemanticGraphError(
                "authority_reference must be a dictionary."
            )

        if not isinstance(
            evidence_trace,
            list,
        ):
            raise DynamicSemanticGraphError(
                "evidence_trace must be a list."
            )

        if not isinstance(
            conflict_trace,
            list,
        ):
            raise DynamicSemanticGraphError(
                "conflict_trace must be a list."
            )

        if not isinstance(
            conflict_summary,
            dict,
        ):
            raise DynamicSemanticGraphError(
                "conflict_summary must be a dictionary."
            )

        required_record_true = (
            "authority_preserved",
            "support_preserved",
            "conflict_preserved",
            "integrity_decision_preserved",
            "guard_disposition_preserved",
            "provenance_preserved",
            "active_target_set_ownership_preserved",
            "external_authority_partition_preserved",
            "external_route_eligibility_preserved",
            "external_resolver_ownership_preserved",
        )

        for flag in required_record_true:

            if record.get(flag) is not True:
                raise DynamicSemanticGraphError(
                    "Final Claim Integrity record preservation "
                    f"contract violated: {flag}"
                )

        required_record_false = (
            "authority_used_as_truth_proxy",
            "authority_rescoring_performed",
            "authority_reclassification_performed",
            "external_target_created",
            "external_target_selected",
            "semantic_memory_written",
            "linking_decisions_performed",
        )

        for flag in required_record_false:

            if record.get(flag) is not False:
                raise DynamicSemanticGraphError(
                    "Final Claim Integrity forbidden-operation "
                    f"boundary violated: {flag}"
                )

        inspected_records.append(
            {
                "schema":
                    "dynamic_graph_claim_integrity_input_record_v1",

                "claim_id":
                    claim_id,

                "claim_type":
                    record.get(
                        "claim_type"
                    ),

                "claim_text":
                    record.get(
                        "claim_text"
                    ),

                "authority_reference":
                    copy.deepcopy(
                        authority_reference
                    ),

                "support_state":
                    record.get(
                        "support_state"
                    ),

                "support_balance":
                    record.get(
                        "support_balance"
                    ),

                "relationship_counts":
                    copy.deepcopy(
                        record.get(
                            "relationship_counts"
                        )
                    ),

                "evidence_trace":
                    copy.deepcopy(
                        evidence_trace
                    ),

                "conflict_trace":
                    copy.deepcopy(
                        conflict_trace
                    ),

                "conflict_summary":
                    copy.deepcopy(
                        conflict_summary
                    ),

                "claim_integrity_state":
                    integrity_state,

                "integrity_decision_basis":
                    record.get(
                        "integrity_decision_basis"
                    ),

                "guard_disposition":
                    guard_disposition,

                "downstream_claim_eligible":
                    downstream_eligible,

                "provenance_trace_id":
                    record.get(
                        "provenance_trace_id"
                    ),

                "provenance_trace_digest":
                    record.get(
                        "provenance_trace_digest"
                    ),

                "final_claim_integrity_id":
                    final_id,

                "final_claim_integrity_digest":
                    final_digest,

                "claim_integrity_input_preserved":
                    True,

                "authority_preserved":
                    True,

                "support_preserved":
                    True,

                "conflict_preserved":
                    True,

                "integrity_preserved":
                    True,

                "guard_preserved":
                    True,

                "provenance_preserved":
                    True,

                "active_target_set_ownership_preserved":
                    True,

                "external_authority_partition_preserved":
                    True,

                "external_route_eligibility_preserved":
                    True,

                "external_resolver_ownership_preserved":
                    True,
            }
        )

    return {
        "schema":
            "dynamic_semantic_graph_claim_integrity_input_inspection_result_v1",

        "dynamic_semantic_graph_version":
            DYNAMIC_SEMANTIC_GRAPH_VERSION,

        "phase":
            DYNAMIC_SEMANTIC_GRAPH_PHASE,

        "patch":
            "4.6.26A",

        "status":
            "CERTIFIED_CLAIM_INTEGRITY_INPUT_INSPECTED",

        "input_record_count":
            len(inspected_records),

        "claim_integrity_input_records":
            inspected_records,

        "final_claim_integrity_package":
            copy.deepcopy(
                package
            ),

        "architecture_boundaries": {
            "claim_integrity_input_inspection_performed":
                True,

            "graph_node_creation_performed":
                False,

            "graph_edge_creation_performed":
                False,

            "graph_mutation_performed":
                False,

            "support_reassessment_performed":
                False,

            "conflict_redetection_performed":
                False,

            "conflict_reclassification_performed":
                False,

            "integrity_redecision_performed":
                False,

            "guard_redisposition_performed":
                False,

            "authority_rescoring_performed":
                False,

            "authority_reclassification_performed":
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
        },

        "preservation_contract": {
            "claim_integrity_preserved":
                True,

            "authority_preserved":
                True,

            "support_preserved":
                True,

            "conflict_preserved":
                True,

            "guard_preserved":
                True,

            "provenance_preserved":
                True,

            "active_target_set_ownership_preserved":
                True,

            "external_authority_partition_preserved":
                True,

            "external_route_eligibility_preserved":
                True,

            "external_resolver_ownership_preserved":
                True,
        },

        "policy":
            "CERTIFIED_FINAL_CLAIM_INTEGRITY_INPUT_ONLY",

        "next":
            "dynamic_graph_architecture_definition",
    }

def define_dynamic_graph_architecture_v1(
    inspection_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.26B ? Dynamic Graph Architecture Definition.

    Defines the canonical Dynamic Semantic Graph architecture.

    Architecture definition only.

    No graph node, edge, graph-state mutation, reasoning,
    Semantic Memory write, target resolution, or linking decision
    is performed here.
    """

    if not isinstance(
        inspection_result,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "inspection_result must be a dictionary."
        )

    expected_lifecycle = {
        "schema":
            "dynamic_semantic_graph_claim_integrity_input_inspection_result_v1",

        "dynamic_semantic_graph_version":
            DYNAMIC_SEMANTIC_GRAPH_VERSION,

        "phase":
            DYNAMIC_SEMANTIC_GRAPH_PHASE,

        "patch":
            "4.6.26A",

        "status":
            "CERTIFIED_CLAIM_INTEGRITY_INPUT_INSPECTED",

        "policy":
            "CERTIFIED_FINAL_CLAIM_INTEGRITY_INPUT_ONLY",

        "next":
            "dynamic_graph_architecture_definition",
    }

    for key, expected in expected_lifecycle.items():

        if inspection_result.get(key) != expected:
            raise DynamicSemanticGraphError(
                "Invalid 4.6.26A lifecycle field: "
                f"{key}"
            )

    input_records = inspection_result.get(
        "claim_integrity_input_records"
    )

    preservation_contract = inspection_result.get(
        "preservation_contract"
    )

    final_claim_integrity_package = (
        inspection_result.get(
            "final_claim_integrity_package"
        )
    )

    if not isinstance(
        input_records,
        list,
    ):
        raise DynamicSemanticGraphError(
            "claim_integrity_input_records must be a list."
        )

    if (
        inspection_result.get(
            "input_record_count"
        )
        != len(input_records)
    ):
        raise DynamicSemanticGraphError(
            "Input record count mismatch."
        )

    if not isinstance(
        preservation_contract,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "preservation_contract must be a dictionary."
        )

    if not isinstance(
        final_claim_integrity_package,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "final_claim_integrity_package must be a dictionary."
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

        if preservation_contract.get(flag) is not True:
            raise DynamicSemanticGraphError(
                "Upstream preservation contract drift: "
                f"{flag}"
            )

    node_types = (
        "CLAIM_NODE",
        "EVIDENCE_NODE",
        "SOURCE_NODE",
        "AUTHORITY_NODE",
        "CONFLICT_NODE",
        "INTEGRITY_NODE",
        "GUARD_NODE",
        "PROVENANCE_NODE",
        "ENTITY_NODE",
        "CONCEPT_NODE",
        "TOPIC_NODE",
        "DOCUMENT_NODE",
        "SECTION_NODE",
        "PHRASE_NODE",
        "TARGET_NODE_REFERENCE",
    )

    edge_types = (
        "CLAIM_SUPPORTED_BY_EVIDENCE",
        "CLAIM_PARTIALLY_SUPPORTED_BY_EVIDENCE",
        "CLAIM_CHALLENGED_BY_EVIDENCE",
        "CLAIM_CONTRADICTED_BY_EVIDENCE",
        "CLAIM_HAS_NEUTRAL_EVIDENCE",
        "CLAIM_HAS_INSUFFICIENT_EVIDENCE",
        "CLAIM_HAS_UNRESOLVED_EVIDENCE",
        "CLAIM_ASSERTED_BY_SOURCE",
        "SOURCE_HAS_AUTHORITY",
        "CLAIM_HAS_INTEGRITY_STATE",
        "CLAIM_HAS_GUARD_DISPOSITION",
        "CLAIM_CONFLICTS_WITH_CLAIM",
        "CLAIM_AGREES_WITH_CLAIM",
        "CLAIM_QUALIFIES_CLAIM",
        "CLAIM_OVERLAPS_CLAIM",
        "CLAIM_RELATED_TO_ENTITY",
        "CLAIM_RELATED_TO_CONCEPT",
        "CLAIM_RELATED_TO_TOPIC",
        "CLAIM_ORIGINATES_FROM_DOCUMENT",
        "CLAIM_ORIGINATES_FROM_SECTION",
        "CLAIM_ASSOCIATED_WITH_PHRASE",
        "CLAIM_REFERENCES_TARGET",
        "EVIDENCE_HAS_PROVENANCE",
        "CONFLICT_HAS_PROVENANCE",
        "INTEGRITY_HAS_PROVENANCE",
        "GRAPH_ENTITY_RELATED_TO_GRAPH_ENTITY",
    )

    graph_layers = (
        "SEMANTIC_OBJECT_LAYER",
        "CLAIM_EVIDENCE_LAYER",
        "AUTHORITY_LAYER",
        "CONFLICT_LAYER",
        "INTEGRITY_LAYER",
        "PROVENANCE_LAYER",
        "CONTENT_CONTEXT_LAYER",
        "TARGET_REFERENCE_LAYER",
    )

    graph_identity_rules = (
        "EVERY_NODE_MUST_HAVE_STABLE_CANONICAL_ID",
        "EVERY_EDGE_MUST_HAVE_STABLE_CANONICAL_ID",
        "NODE_IDENTITY_MUST_BE_TYPE_SCOPED",
        "EDGE_IDENTITY_MUST_BE_ENDPOINT_AND_RELATION_SCOPED",
        "CANONICAL_IDS_MUST_BE_DETERMINISTIC",
        "GRAPH_OBJECTS_MUST_PRESERVE_UPSTREAM_IDS",
        "DUPLICATE_CANONICAL_OBJECTS_MUST_NOT_BE_CREATED",
    )

    mutation_rules = (
        "GRAPH_MUTATION_MUST_BE_EXPLICIT",
        "GRAPH_MUTATION_MUST_BE_VERSIONED",
        "GRAPH_MUTATION_MUST_BE_PROVENANCE_BOUND",
        "GRAPH_MUTATION_MUST_BE_IDEMPOTENT",
        "GRAPH_MUTATION_MUST_PRESERVE_REFERENTIAL_INTEGRITY",
        "GRAPH_MUTATION_MUST_NOT_REWRITE_CERTIFIED_UPSTREAM_FACTS",
        "GRAPH_MUTATION_MUST_NOT_OVERRIDE_CLAIM_GUARD_DISPOSITION",
        "GRAPH_MUTATION_MUST_NOT_RESCORE_AUTHORITY",
        "GRAPH_MUTATION_MUST_NOT_CREATE_LINKING_DECISIONS",
    )

    graph_invariants = (
        "CLAIM_INTEGRITY_OUTPUT_IS_IMMUTABLE_INPUT",
        "AUTHORITY_AND_CLAIM_INTEGRITY_REMAIN_DISTINCT",
        "CLAIM_SUPPORT_AND_CONFLICT_REMAIN_TRACEABLE",
        "BLOCKED_OR_HELD_CLAIMS_REMAIN_IN_GRAPH_WITH_GUARD_STATE",
        "GRAPH_PRESENCE_DOES_NOT_EQUAL_DOWNSTREAM_ELIGIBILITY",
        "GRAPH_RELATIONSHIP_DOES_NOT_EQUAL_LINKING_DECISION",
        "GRAPH_TARGET_REFERENCE_DOES_NOT_EQUAL_TARGET_SELECTION",
        "ACTIVE_TARGET_SET_REMAINS_TARGET_OWNER",
        "EXTERNAL_AUTHORITY_PARTITION_REMAINS_PRESERVED",
        "EXTERNAL_ROUTE_ELIGIBILITY_REMAINS_PRESERVED",
        "EXTERNAL_TARGET_RESOLVER_REMAINS_FINAL_EXTERNAL_SELECTOR",
        "NO_UNSUPPORTED_NODE_INVENTION",
        "NO_UNSUPPORTED_EDGE_INVENTION",
        "NO_SEMANTIC_MEMORY_WRITE",
        "NO_DOWNSTREAM_REASONING_EXECUTION",
        "NO_EDITOR_HIGHLIGHT_CREATION",
    )

    node_ownership = {
        "CLAIM_NODE":
            "DYNAMIC_SEMANTIC_GRAPH",

        "EVIDENCE_NODE":
            "DYNAMIC_SEMANTIC_GRAPH",

        "SOURCE_NODE":
            "DYNAMIC_SEMANTIC_GRAPH",

        "AUTHORITY_NODE":
            "DYNAMIC_SEMANTIC_GRAPH",

        "CONFLICT_NODE":
            "DYNAMIC_SEMANTIC_GRAPH",

        "INTEGRITY_NODE":
            "DYNAMIC_SEMANTIC_GRAPH",

        "GUARD_NODE":
            "DYNAMIC_SEMANTIC_GRAPH",

        "PROVENANCE_NODE":
            "DYNAMIC_SEMANTIC_GRAPH",

        "ENTITY_NODE":
            "DYNAMIC_SEMANTIC_GRAPH",

        "CONCEPT_NODE":
            "DYNAMIC_SEMANTIC_GRAPH",

        "TOPIC_NODE":
            "DYNAMIC_SEMANTIC_GRAPH",

        "DOCUMENT_NODE":
            "DYNAMIC_SEMANTIC_GRAPH",

        "SECTION_NODE":
            "DYNAMIC_SEMANTIC_GRAPH",

        "PHRASE_NODE":
            "DYNAMIC_SEMANTIC_GRAPH",

        "TARGET_NODE_REFERENCE":
            "REFERENCE_ONLY_ACTIVE_TARGET_SET_OWNS_TARGET",
    }

    target_ownership = {
        "canonical_target_owner":
            "ACTIVE_TARGET_SET",

        "external_partition":
            "EXTERNAL_AUTHORITY",

        "external_route":
            "EXTERNAL",

        "final_external_selection_owner":
            "EXTERNAL_TARGET_RESOLVER",

        "dynamic_graph_may_create_target":
            False,

        "dynamic_graph_may_select_final_target":
            False,

        "dynamic_graph_target_nodes_are_references_only":
            True,
    }

    downstream_boundaries = {
        "semantic_memory_write_owner":
            "SEMANTIC_MEMORY",

        "learning_owner":
            "LEARNING_ENGINE",

        "reasoning_owner":
            "REASONING_ENGINE",

        "final_external_target_selection_owner":
            "EXTERNAL_TARGET_RESOLVER",

        "linking_decision_owner":
            "LINKCRAFTOR_LINKING_INTELLIGENCE",

        "editor_highlight_owner":
            "EDITOR_HIGHLIGHT_PIPELINE",
    }

    architecture = {
        "schema":
            "dynamic_semantic_graph_architecture_v1",

        "architecture_question":
            (
                "HOW_SHOULD_CERTIFIED_SEMANTIC_OBJECTS_AND_THEIR_"
                "RELATIONSHIPS_BE_REPRESENTED_AS_A_DYNAMIC_TRACEABLE_"
                "GRAPH_WITHOUT_CHANGING_UPSTREAM_DECISIONS"
            ),

        "architecture_policy":
            (
                "CERTIFIED_PROVENANCE_BOUND_DYNAMIC_GRAPH_"
                "REPRESENTATION_ONLY"
            ),

        "graph_layers":
            graph_layers,

        "node_types":
            node_types,

        "edge_types":
            edge_types,

        "graph_identity_rules":
            graph_identity_rules,

        "mutation_rules":
            mutation_rules,

        "graph_invariants":
            graph_invariants,

        "node_ownership":
            node_ownership,

        "target_ownership":
            target_ownership,

        "downstream_boundaries":
            downstream_boundaries,

        "claim_integrity_is_upstream":
            True,

        "claim_integrity_must_not_be_redecided":
            True,

        "authority_must_not_be_rescored":
            True,

        "support_must_not_be_reassessed":
            True,

        "conflicts_must_not_be_redetected":
            True,

        "guard_dispositions_must_not_be_overridden":
            True,

        "graph_is_representation_not_truth_adjudication":
            True,

        "graph_is_not_link_resolver":
            True,

        "graph_is_not_semantic_memory":
            True,

        "graph_is_not_learning_engine":
            True,

        "graph_is_not_reasoning_engine":
            True,
    }

    return {
        "schema":
            "dynamic_semantic_graph_architecture_result_v1",

        "dynamic_semantic_graph_version":
            DYNAMIC_SEMANTIC_GRAPH_VERSION,

        "phase":
            DYNAMIC_SEMANTIC_GRAPH_PHASE,

        "patch":
            "4.6.26B",

        "status":
            "DYNAMIC_SEMANTIC_GRAPH_ARCHITECTURE_DEFINED",

        "architecture":
            architecture,

        "claim_integrity_input_records":
            copy.deepcopy(
                input_records
            ),

        "final_claim_integrity_package":
            copy.deepcopy(
                final_claim_integrity_package
            ),

        "preservation_contract":
            copy.deepcopy(
                preservation_contract
            ),

        "processing_boundaries": {
            "graph_architecture_definition_performed":
                True,

            "graph_node_creation_performed":
                False,

            "graph_edge_creation_performed":
                False,

            "graph_mutation_performed":
                False,

            "graph_merge_performed":
                False,

            "claim_support_reassessment_performed":
                False,

            "claim_conflict_redetection_performed":
                False,

            "claim_conflict_reclassification_performed":
                False,

            "claim_integrity_redecision_performed":
                False,

            "guard_redisposition_performed":
                False,

            "authority_rescoring_performed":
                False,

            "authority_reclassification_performed":
                False,

            "semantic_memory_written":
                False,

            "learning_performed":
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

            "unsupported_node_invention_performed":
                False,

            "unsupported_edge_invention_performed":
                False,
        },

        "policy":
            "CERTIFIED_DYNAMIC_SEMANTIC_GRAPH_ARCHITECTURE",

        "next":
            "graph_intake_validation",
    }

def validate_graph_intake_v1(
    architecture_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.26C ? Graph Intake Validation.

    Validates certified semantic objects before graph construction.

    This stage performs validation only.

    It does not:
    - create graph nodes,
    - create graph edges,
    - mutate graph state,
    - merge graph state,
    - reassess support,
    - redetect conflicts,
    - redecide integrity,
    - override guards,
    - rescore Authority,
    - write Semantic Memory,
    - perform learning or reasoning,
    - create/select targets,
    - make linking decisions.
    """

    if not isinstance(
        architecture_result,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "architecture_result must be a dictionary."
        )

    expected_lifecycle = {
        "schema":
            "dynamic_semantic_graph_architecture_result_v1",

        "dynamic_semantic_graph_version":
            DYNAMIC_SEMANTIC_GRAPH_VERSION,

        "phase":
            DYNAMIC_SEMANTIC_GRAPH_PHASE,

        "patch":
            "4.6.26B",

        "status":
            "DYNAMIC_SEMANTIC_GRAPH_ARCHITECTURE_DEFINED",

        "policy":
            "CERTIFIED_DYNAMIC_SEMANTIC_GRAPH_ARCHITECTURE",

        "next":
            "graph_intake_validation",
    }

    for key, expected in expected_lifecycle.items():

        if architecture_result.get(key) != expected:
            raise DynamicSemanticGraphError(
                "Invalid 4.6.26B lifecycle field: "
                f"{key}"
            )

    architecture = architecture_result.get(
        "architecture"
    )

    intake_records = architecture_result.get(
        "claim_integrity_input_records"
    )

    preservation_contract = architecture_result.get(
        "preservation_contract"
    )

    final_claim_integrity_package = (
        architecture_result.get(
            "final_claim_integrity_package"
        )
    )

    if not isinstance(
        architecture,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "architecture must be a dictionary."
        )

    if (
        architecture.get("schema")
        != "dynamic_semantic_graph_architecture_v1"
    ):
        raise DynamicSemanticGraphError(
            "Invalid Dynamic Semantic Graph architecture schema."
        )

    if not isinstance(
        intake_records,
        list,
    ):
        raise DynamicSemanticGraphError(
            "claim_integrity_input_records must be a list."
        )

    if not isinstance(
        preservation_contract,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "preservation_contract must be a dictionary."
        )

    if not isinstance(
        final_claim_integrity_package,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "final_claim_integrity_package must be a dictionary."
        )

    required_node_types = {
        "CLAIM_NODE",
        "EVIDENCE_NODE",
        "SOURCE_NODE",
        "AUTHORITY_NODE",
        "CONFLICT_NODE",
        "INTEGRITY_NODE",
        "GUARD_NODE",
        "PROVENANCE_NODE",
        "ENTITY_NODE",
        "CONCEPT_NODE",
        "TOPIC_NODE",
        "DOCUMENT_NODE",
        "SECTION_NODE",
        "PHRASE_NODE",
        "TARGET_NODE_REFERENCE",
    }

    architecture_node_types = set(
        architecture.get(
            "node_types",
            (),
        )
    )

    if not required_node_types.issubset(
        architecture_node_types
    ):
        raise DynamicSemanticGraphError(
            "Dynamic graph architecture node-type contract drift."
        )

    required_edges = {
        "CLAIM_SUPPORTED_BY_EVIDENCE",
        "CLAIM_PARTIALLY_SUPPORTED_BY_EVIDENCE",
        "CLAIM_CHALLENGED_BY_EVIDENCE",
        "CLAIM_CONTRADICTED_BY_EVIDENCE",
        "CLAIM_ASSERTED_BY_SOURCE",
        "SOURCE_HAS_AUTHORITY",
        "CLAIM_HAS_INTEGRITY_STATE",
        "CLAIM_HAS_GUARD_DISPOSITION",
        "CLAIM_CONFLICTS_WITH_CLAIM",
        "EVIDENCE_HAS_PROVENANCE",
    }

    architecture_edges = set(
        architecture.get(
            "edge_types",
            (),
        )
    )

    if not required_edges.issubset(
        architecture_edges
    ):
        raise DynamicSemanticGraphError(
            "Dynamic graph architecture edge-type contract drift."
        )

    target_ownership = architecture.get(
        "target_ownership"
    )

    if not isinstance(
        target_ownership,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "target_ownership must be a dictionary."
        )

    expected_target_ownership = {
        "canonical_target_owner":
            "ACTIVE_TARGET_SET",

        "external_partition":
            "EXTERNAL_AUTHORITY",

        "external_route":
            "EXTERNAL",

        "final_external_selection_owner":
            "EXTERNAL_TARGET_RESOLVER",

        "dynamic_graph_may_create_target":
            False,

        "dynamic_graph_may_select_final_target":
            False,

        "dynamic_graph_target_nodes_are_references_only":
            True,
    }

    for key, expected in expected_target_ownership.items():

        if target_ownership.get(key) != expected:
            raise DynamicSemanticGraphError(
                "Target ownership architecture drift: "
                f"{key}"
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

        if preservation_contract.get(flag) is not True:
            raise DynamicSemanticGraphError(
                "Preservation contract drift: "
                f"{flag}"
            )

    allowed_integrity_states = {
        "WELL_SUPPORTED",
        "SUPPORTED",
        "PARTIALLY_SUPPORTED",
        "DISPUTED",
        "CONTRADICTED",
        "INSUFFICIENT_EVIDENCE",
        "UNRESOLVED",
        "BLOCKED",
    }

    allowed_guard_dispositions = {
        "PASS",
        "CAUTION",
        "HOLD",
        "BLOCK",
    }

    allowed_claim_types = {
        "FACTUAL_CLAIM",
        "CAUSAL_CLAIM",
        "QUANTITATIVE_CLAIM",
        "COMPARATIVE_CLAIM",
        "TEMPORAL_CLAIM",
        "DEFINITIONAL_CLAIM",
        "ATTRIBUTION_CLAIM",
        "CONDITIONAL_CLAIM",
    }

    validated_records = []
    seen_claim_ids = set()
    seen_final_integrity_ids = set()
    seen_provenance_trace_ids = set()

    for record in intake_records:

        if not isinstance(
            record,
            dict,
        ):
            raise DynamicSemanticGraphError(
                "Graph intake record must be a dictionary."
            )

        if (
            record.get("schema")
            != "dynamic_graph_claim_integrity_input_record_v1"
        ):
            raise DynamicSemanticGraphError(
                "Invalid graph intake record schema."
            )

        claim_id = record.get(
            "claim_id"
        )

        claim_type = record.get(
            "claim_type"
        )

        claim_text = record.get(
            "claim_text"
        )

        final_integrity_id = record.get(
            "final_claim_integrity_id"
        )

        final_integrity_digest = record.get(
            "final_claim_integrity_digest"
        )

        provenance_trace_id = record.get(
            "provenance_trace_id"
        )

        provenance_trace_digest = record.get(
            "provenance_trace_digest"
        )

        if (
            not isinstance(claim_id, str)
            or not claim_id.strip()
        ):
            raise DynamicSemanticGraphError(
                "Graph intake requires claim_id."
            )

        if claim_id in seen_claim_ids:
            raise DynamicSemanticGraphError(
                "Duplicate graph intake claim_id."
            )

        seen_claim_ids.add(
            claim_id
        )

        if claim_type not in allowed_claim_types:
            raise DynamicSemanticGraphError(
                "Unsupported graph intake claim_type."
            )

        if (
            not isinstance(claim_text, str)
            or not claim_text.strip()
        ):
            raise DynamicSemanticGraphError(
                "Graph intake requires non-empty claim_text."
            )

        if (
            not isinstance(final_integrity_id, str)
            or not final_integrity_id.startswith(
                "claimintegrity:v1:"
            )
        ):
            raise DynamicSemanticGraphError(
                "Invalid final_claim_integrity_id."
            )

        if final_integrity_id in seen_final_integrity_ids:
            raise DynamicSemanticGraphError(
                "Duplicate final_claim_integrity_id."
            )

        seen_final_integrity_ids.add(
            final_integrity_id
        )

        if (
            not isinstance(final_integrity_digest, str)
            or len(final_integrity_digest) != 64
        ):
            raise DynamicSemanticGraphError(
                "Invalid final_claim_integrity_digest."
            )

        if (
            not isinstance(provenance_trace_id, str)
            or not provenance_trace_id.startswith(
                "claimtrace:v1:"
            )
        ):
            raise DynamicSemanticGraphError(
                "Invalid provenance_trace_id."
            )

        if provenance_trace_id in seen_provenance_trace_ids:
            raise DynamicSemanticGraphError(
                "Duplicate provenance_trace_id."
            )

        seen_provenance_trace_ids.add(
            provenance_trace_id
        )

        if (
            not isinstance(provenance_trace_digest, str)
            or len(provenance_trace_digest) != 64
        ):
            raise DynamicSemanticGraphError(
                "Invalid provenance_trace_digest."
            )

        authority_reference = record.get(
            "authority_reference"
        )

        evidence_trace = record.get(
            "evidence_trace"
        )

        conflict_trace = record.get(
            "conflict_trace"
        )

        conflict_summary = record.get(
            "conflict_summary"
        )

        relationship_counts = record.get(
            "relationship_counts"
        )

        if not isinstance(
            authority_reference,
            dict,
        ):
            raise DynamicSemanticGraphError(
                "authority_reference must be a dictionary."
            )

        if not isinstance(
            evidence_trace,
            list,
        ):
            raise DynamicSemanticGraphError(
                "evidence_trace must be a list."
            )

        if not isinstance(
            conflict_trace,
            list,
        ):
            raise DynamicSemanticGraphError(
                "conflict_trace must be a list."
            )

        if not isinstance(
            conflict_summary,
            dict,
        ):
            raise DynamicSemanticGraphError(
                "conflict_summary must be a dictionary."
            )

        if not isinstance(
            relationship_counts,
            dict,
        ):
            raise DynamicSemanticGraphError(
                "relationship_counts must be a dictionary."
            )

        integrity_state = record.get(
            "claim_integrity_state"
        )

        guard_disposition = record.get(
            "guard_disposition"
        )

        downstream_eligible = record.get(
            "downstream_claim_eligible"
        )

        if integrity_state not in allowed_integrity_states:
            raise DynamicSemanticGraphError(
                "Unsupported claim_integrity_state."
            )

        if guard_disposition not in allowed_guard_dispositions:
            raise DynamicSemanticGraphError(
                "Unsupported guard_disposition."
            )

        if not isinstance(
            downstream_eligible,
            bool,
        ):
            raise DynamicSemanticGraphError(
                "downstream_claim_eligible must be boolean."
            )

        expected_eligibility = (
            guard_disposition
            in {
                "PASS",
                "CAUTION",
            }
        )

        if downstream_eligible is not expected_eligibility:
            raise DynamicSemanticGraphError(
                "Guard disposition and eligibility mismatch."
            )

        required_record_true = (
            "claim_integrity_input_preserved",
            "authority_preserved",
            "support_preserved",
            "conflict_preserved",
            "integrity_preserved",
            "guard_preserved",
            "provenance_preserved",
            "active_target_set_ownership_preserved",
            "external_authority_partition_preserved",
            "external_route_eligibility_preserved",
            "external_resolver_ownership_preserved",
        )

        for flag in required_record_true:

            if record.get(flag) is not True:
                raise DynamicSemanticGraphError(
                    "Graph intake preservation drift: "
                    f"{flag}"
                )

        validated_records.append(
            {
                "schema":
                    "dynamic_graph_validated_intake_record_v1",

                "claim_id":
                    claim_id,

                "claim_type":
                    claim_type,

                "claim_text":
                    claim_text,

                "authority_reference":
                    copy.deepcopy(
                        authority_reference
                    ),

                "support_state":
                    record.get(
                        "support_state"
                    ),

                "support_balance":
                    record.get(
                        "support_balance"
                    ),

                "relationship_counts":
                    copy.deepcopy(
                        relationship_counts
                    ),

                "evidence_trace":
                    copy.deepcopy(
                        evidence_trace
                    ),

                "conflict_trace":
                    copy.deepcopy(
                        conflict_trace
                    ),

                "conflict_summary":
                    copy.deepcopy(
                        conflict_summary
                    ),

                "claim_integrity_state":
                    integrity_state,

                "integrity_decision_basis":
                    record.get(
                        "integrity_decision_basis"
                    ),

                "guard_disposition":
                    guard_disposition,

                "downstream_claim_eligible":
                    downstream_eligible,

                "provenance_trace_id":
                    provenance_trace_id,

                "provenance_trace_digest":
                    provenance_trace_digest,

                "final_claim_integrity_id":
                    final_integrity_id,

                "final_claim_integrity_digest":
                    final_integrity_digest,

                "graph_intake_validated":
                    True,

                "graph_construction_authorized":
                    True,

                "upstream_semantic_state_preserved":
                    True,

                "target_ownership_preserved":
                    True,
            }
        )

    return {
        "schema":
            "dynamic_semantic_graph_intake_validation_result_v1",

        "dynamic_semantic_graph_version":
            DYNAMIC_SEMANTIC_GRAPH_VERSION,

        "phase":
            DYNAMIC_SEMANTIC_GRAPH_PHASE,

        "patch":
            "4.6.26C",

        "status":
            "GRAPH_INTAKE_VALIDATED",

        "validated_record_count":
            len(validated_records),

        "validated_graph_intake_records":
            validated_records,

        "architecture":
            copy.deepcopy(
                architecture
            ),

        "final_claim_integrity_package":
            copy.deepcopy(
                final_claim_integrity_package
            ),

        "preservation_contract":
            copy.deepcopy(
                preservation_contract
            ),

        "processing_boundaries": {
            "graph_intake_validation_performed":
                True,

            "graph_node_creation_performed":
                False,

            "graph_edge_creation_performed":
                False,

            "graph_mutation_performed":
                False,

            "graph_merge_performed":
                False,

            "support_reassessment_performed":
                False,

            "conflict_redetection_performed":
                False,

            "conflict_reclassification_performed":
                False,

            "integrity_redecision_performed":
                False,

            "guard_redisposition_performed":
                False,

            "authority_rescoring_performed":
                False,

            "authority_reclassification_performed":
                False,

            "semantic_memory_written":
                False,

            "learning_performed":
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

            "unsupported_node_invention_performed":
                False,

            "unsupported_edge_invention_performed":
                False,
        },

        "policy":
            "CERTIFIED_DYNAMIC_GRAPH_INTAKE_VALIDATION",

        "next":
            "graph_scope_and_mutation_contract",
    }

def define_graph_scope_and_mutation_contract_v1(
    intake_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.26D ? Graph Scope & Mutation Contract.

    Defines the graph's representational scope and mutation permissions
    before any node or edge construction occurs.

    No graph objects are created in this stage.
    """

    if not isinstance(
        intake_result,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "intake_result must be a dictionary."
        )

    expected_lifecycle = {
        "schema":
            "dynamic_semantic_graph_intake_validation_result_v1",

        "dynamic_semantic_graph_version":
            DYNAMIC_SEMANTIC_GRAPH_VERSION,

        "phase":
            DYNAMIC_SEMANTIC_GRAPH_PHASE,

        "patch":
            "4.6.26C",

        "status":
            "GRAPH_INTAKE_VALIDATED",

        "policy":
            "CERTIFIED_DYNAMIC_GRAPH_INTAKE_VALIDATION",

        "next":
            "graph_scope_and_mutation_contract",
    }

    for key, expected in expected_lifecycle.items():

        if intake_result.get(key) != expected:
            raise DynamicSemanticGraphError(
                "Invalid 4.6.26C lifecycle field: "
                f"{key}"
            )

    validated_records = intake_result.get(
        "validated_graph_intake_records"
    )

    architecture = intake_result.get(
        "architecture"
    )

    preservation_contract = intake_result.get(
        "preservation_contract"
    )

    final_claim_integrity_package = (
        intake_result.get(
            "final_claim_integrity_package"
        )
    )

    if not isinstance(
        validated_records,
        list,
    ):
        raise DynamicSemanticGraphError(
            "validated_graph_intake_records must be a list."
        )

    if (
        intake_result.get(
            "validated_record_count"
        )
        != len(validated_records)
    ):
        raise DynamicSemanticGraphError(
            "Validated graph intake count mismatch."
        )

    if not isinstance(
        architecture,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "architecture must be a dictionary."
        )

    if (
        architecture.get("schema")
        != "dynamic_semantic_graph_architecture_v1"
    ):
        raise DynamicSemanticGraphError(
            "Invalid graph architecture schema."
        )

    if not isinstance(
        preservation_contract,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "preservation_contract must be a dictionary."
        )

    if not isinstance(
        final_claim_integrity_package,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "final_claim_integrity_package must be a dictionary."
        )

    representational_scope = {
        "may_represent_claims":
            True,

        "may_represent_evidence":
            True,

        "may_represent_sources":
            True,

        "may_represent_authority":
            True,

        "may_represent_conflicts":
            True,

        "may_represent_integrity_states":
            True,

        "may_represent_guard_states":
            True,

        "may_represent_provenance":
            True,

        "may_represent_entities":
            True,

        "may_represent_concepts":
            True,

        "may_represent_topics":
            True,

        "may_represent_documents":
            True,

        "may_represent_sections":
            True,

        "may_represent_phrases":
            True,

        "may_represent_target_references":
            True,

        "may_represent_cross_object_relationships":
            True,
    }

    mutation_permissions = {
        "may_create_graph_nodes_from_certified_input":
            True,

        "may_create_graph_edges_from_certified_relationships":
            True,

        "may_add_new_graph_versions":
            True,

        "may_merge_equivalent_graph_objects":
            True,

        "may_update_graph_metadata":
            True,

        "may_attach_provenance":
            True,

        "may_attach_integrity_state":
            True,

        "may_attach_guard_state":
            True,

        "may_attach_authority_reference":
            True,

        "may_attach_target_reference":
            True,

        "may_mark_graph_object_superseded":
            True,

        "may_preserve_historical_graph_versions":
            True,
    }

    forbidden_mutations = {
        "may_rewrite_claim_text":
            False,

        "may_reassess_claim_support":
            False,

        "may_redetect_claim_conflict":
            False,

        "may_reclassify_claim_conflict":
            False,

        "may_redecide_claim_integrity":
            False,

        "may_override_guard_disposition":
            False,

        "may_rescore_authority":
            False,

        "may_reclassify_authority":
            False,

        "may_invent_unsupported_nodes":
            False,

        "may_invent_unsupported_edges":
            False,

        "may_create_active_targets":
            False,

        "may_change_active_target_owner":
            False,

        "may_move_external_target_partition":
            False,

        "may_change_external_route_eligibility":
            False,

        "may_select_final_external_target":
            False,

        "may_write_semantic_memory":
            False,

        "may_execute_learning":
            False,

        "may_execute_reasoning":
            False,

        "may_make_linking_decision":
            False,

        "may_create_editor_highlight":
            False,
    }

    graph_object_lifecycle = (
        "PROPOSED",
        "VALIDATED",
        "ACTIVE",
        "SUPERSEDED",
        "RETIRED",
    )

    graph_mutation_types = (
        "CREATE_NODE",
        "CREATE_EDGE",
        "ATTACH_METADATA",
        "ATTACH_PROVENANCE",
        "MERGE_EQUIVALENT_OBJECT",
        "VERSION_OBJECT",
        "SUPERSEDE_OBJECT",
        "RETIRE_OBJECT",
    )

    mutation_requirements = (
        "MUTATION_REQUIRES_CERTIFIED_INPUT",
        "MUTATION_REQUIRES_STABLE_OBJECT_ID",
        "MUTATION_REQUIRES_MUTATION_TYPE",
        "MUTATION_REQUIRES_PROVENANCE",
        "MUTATION_REQUIRES_GRAPH_VERSION",
        "MUTATION_REQUIRES_IDEMPOTENCY_KEY",
        "MUTATION_MUST_PRESERVE_REFERENTIAL_INTEGRITY",
        "MUTATION_MUST_PRESERVE_UPSTREAM_IDENTIFIERS",
        "MUTATION_MUST_PRESERVE_HISTORICAL_TRACE",
        "MUTATION_MUST_NOT_DESTROY_CERTIFIED_UPSTREAM_STATE",
    )

    target_reference_contract = {
        "target_owner":
            "ACTIVE_TARGET_SET",

        "external_partition":
            "EXTERNAL_AUTHORITY",

        "external_route":
            "EXTERNAL",

        "final_external_selector":
            "EXTERNAL_TARGET_RESOLVER",

        "graph_target_object_type":
            "TARGET_NODE_REFERENCE",

        "reference_only":
            True,

        "graph_owns_target":
            False,

        "graph_may_create_target":
            False,

        "graph_may_select_target":
            False,
    }

    scope_contract = {
        "schema":
            "dynamic_semantic_graph_scope_mutation_contract_v1",

        "representational_scope":
            representational_scope,

        "mutation_permissions":
            mutation_permissions,

        "forbidden_mutations":
            forbidden_mutations,

        "graph_object_lifecycle":
            graph_object_lifecycle,

        "graph_mutation_types":
            graph_mutation_types,

        "mutation_requirements":
            mutation_requirements,

        "target_reference_contract":
            target_reference_contract,

        "certified_input_is_source_of_truth_for_graph_representation":
            True,

        "graph_mutation_is_representation_change_not_truth_change":
            True,

        "historical_graph_state_must_be_traceable":
            True,

        "graph_object_identity_must_be_deterministic":
            True,

        "graph_mutations_must_be_idempotent":
            True,

        "graph_must_preserve_upstream_semantic_state":
            True,
    }

    return {
        "schema":
            "dynamic_semantic_graph_scope_mutation_result_v1",

        "dynamic_semantic_graph_version":
            DYNAMIC_SEMANTIC_GRAPH_VERSION,

        "phase":
            DYNAMIC_SEMANTIC_GRAPH_PHASE,

        "patch":
            "4.6.26D",

        "status":
            "GRAPH_SCOPE_AND_MUTATION_CONTRACT_DEFINED",

        "scope_mutation_contract":
            scope_contract,

        "validated_graph_intake_records":
            copy.deepcopy(
                validated_records
            ),

        "architecture":
            copy.deepcopy(
                architecture
            ),

        "final_claim_integrity_package":
            copy.deepcopy(
                final_claim_integrity_package
            ),

        "preservation_contract":
            copy.deepcopy(
                preservation_contract
            ),

        "processing_boundaries": {
            "graph_scope_contract_defined":
                True,

            "graph_mutation_contract_defined":
                True,

            "graph_node_creation_performed":
                False,

            "graph_edge_creation_performed":
                False,

            "graph_mutation_performed":
                False,

            "graph_merge_performed":
                False,

            "support_reassessment_performed":
                False,

            "conflict_redetection_performed":
                False,

            "conflict_reclassification_performed":
                False,

            "integrity_redecision_performed":
                False,

            "guard_redisposition_performed":
                False,

            "authority_rescoring_performed":
                False,

            "authority_reclassification_performed":
                False,

            "semantic_memory_written":
                False,

            "learning_performed":
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

            "unsupported_node_invention_performed":
                False,

            "unsupported_edge_invention_performed":
                False,
        },

        "policy":
            "CERTIFIED_DYNAMIC_GRAPH_SCOPE_AND_MUTATION_CONTRACT",

        "next":
            "canonical_graph_node_construction",
    }

def construct_canonical_graph_nodes_v1(
    scope_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.26E ? Canonical Graph Node Construction.

    Constructs deterministic canonical graph nodes from explicit,
    certified upstream semantic objects.

    This stage creates nodes only.

    It does not:
    - create graph edges,
    - infer unsupported semantic objects,
    - merge graph versions,
    - alter upstream semantic decisions,
    - write Semantic Memory,
    - execute learning/reasoning,
    - create/select targets,
    - make linking decisions.
    """

    import hashlib
    import json

    if not isinstance(
        scope_result,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "scope_result must be a dictionary."
        )

    expected_lifecycle = {
        "schema":
            "dynamic_semantic_graph_scope_mutation_result_v1",

        "dynamic_semantic_graph_version":
            DYNAMIC_SEMANTIC_GRAPH_VERSION,

        "phase":
            DYNAMIC_SEMANTIC_GRAPH_PHASE,

        "patch":
            "4.6.26D",

        "status":
            "GRAPH_SCOPE_AND_MUTATION_CONTRACT_DEFINED",

        "policy":
            "CERTIFIED_DYNAMIC_GRAPH_SCOPE_AND_MUTATION_CONTRACT",

        "next":
            "canonical_graph_node_construction",
    }

    for key, expected in expected_lifecycle.items():

        if scope_result.get(key) != expected:
            raise DynamicSemanticGraphError(
                "Invalid 4.6.26D lifecycle field: "
                f"{key}"
            )

    contract = scope_result.get(
        "scope_mutation_contract"
    )

    validated_records = scope_result.get(
        "validated_graph_intake_records"
    )

    architecture = scope_result.get(
        "architecture"
    )

    preservation_contract = scope_result.get(
        "preservation_contract"
    )

    final_claim_integrity_package = (
        scope_result.get(
            "final_claim_integrity_package"
        )
    )

    if not isinstance(
        contract,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "scope_mutation_contract must be a dictionary."
        )

    if (
        contract.get("schema")
        != "dynamic_semantic_graph_scope_mutation_contract_v1"
    ):
        raise DynamicSemanticGraphError(
            "Invalid graph scope/mutation contract schema."
        )

    if not isinstance(
        validated_records,
        list,
    ):
        raise DynamicSemanticGraphError(
            "validated_graph_intake_records must be a list."
        )

    if not isinstance(
        architecture,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "architecture must be a dictionary."
        )

    if not isinstance(
        preservation_contract,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "preservation_contract must be a dictionary."
        )

    if not isinstance(
        final_claim_integrity_package,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "final_claim_integrity_package must be a dictionary."
        )

    permissions = contract.get(
        "mutation_permissions"
    )

    forbidden = contract.get(
        "forbidden_mutations"
    )

    if not isinstance(
        permissions,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "mutation_permissions must be a dictionary."
        )

    if not isinstance(
        forbidden,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "forbidden_mutations must be a dictionary."
        )

    if (
        permissions.get(
            "may_create_graph_nodes_from_certified_input"
        )
        is not True
    ):
        raise DynamicSemanticGraphError(
            "Canonical graph node construction is not authorized."
        )

    required_forbidden_false = (
        "may_rewrite_claim_text",
        "may_reassess_claim_support",
        "may_redetect_claim_conflict",
        "may_reclassify_claim_conflict",
        "may_redecide_claim_integrity",
        "may_override_guard_disposition",
        "may_rescore_authority",
        "may_reclassify_authority",
        "may_invent_unsupported_nodes",
        "may_create_active_targets",
        "may_change_active_target_owner",
        "may_select_final_external_target",
        "may_write_semantic_memory",
        "may_execute_learning",
        "may_execute_reasoning",
        "may_make_linking_decision",
        "may_create_editor_highlight",
    )

    for flag in required_forbidden_false:

        if forbidden.get(flag) is not False:
            raise DynamicSemanticGraphError(
                "Graph mutation prohibition drift: "
                f"{flag}"
            )

    allowed_node_types = set(
        architecture.get(
            "node_types",
            (),
        )
    )

    required_node_types = {
        "CLAIM_NODE",
        "EVIDENCE_NODE",
        "AUTHORITY_NODE",
        "INTEGRITY_NODE",
        "GUARD_NODE",
        "PROVENANCE_NODE",
    }

    if not required_node_types.issubset(
        allowed_node_types
    ):
        raise DynamicSemanticGraphError(
            "Required canonical graph node types are missing."
        )

    def canonical_json(value: Any) -> str:

        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )

    def digest(value: Any) -> str:

        return hashlib.sha256(
            canonical_json(
                value
            ).encode(
                "utf-8"
            )
        ).hexdigest()

    def make_node(
        *,
        node_type: str,
        source_object_type: str,
        source_object_id: str,
        payload: dict[str, Any],
        provenance: dict[str, Any],
    ) -> dict[str, Any]:

        if node_type not in allowed_node_types:
            raise DynamicSemanticGraphError(
                "Unsupported canonical node type: "
                f"{node_type}"
            )

        if (
            not isinstance(source_object_id, str)
            or not source_object_id.strip()
        ):
            raise DynamicSemanticGraphError(
                "Canonical node requires source_object_id."
            )

        if not isinstance(
            payload,
            dict,
        ):
            raise DynamicSemanticGraphError(
                "Canonical node payload must be a dictionary."
            )

        if not isinstance(
            provenance,
            dict,
        ):
            raise DynamicSemanticGraphError(
                "Canonical node provenance must be a dictionary."
            )

        identity_material = {
            "node_type":
                node_type,

            "source_object_type":
                source_object_type,

            "source_object_id":
                source_object_id,
        }

        node_hash = digest(
            identity_material
        )

        payload_digest = digest(
            payload
        )

        node_id = (
            "graphnode:v1:"
            + node_hash
        )

        return {
            "schema":
                "dynamic_semantic_graph_node_v1",

            "node_id":
                node_id,

            "node_type":
                node_type,

            "source_object_type":
                source_object_type,

            "source_object_id":
                source_object_id,

            "lifecycle_state":
                "ACTIVE",

            "payload":
                copy.deepcopy(
                    payload
                ),

            "payload_digest":
                payload_digest,

            "provenance":
                copy.deepcopy(
                    provenance
                ),

            "idempotency_key":
                (
                    "graphnode-idempotency:v1:"
                    + node_hash
                ),

            "canonical_identity_deterministic":
                True,

            "certified_input_backed":
                True,

            "unsupported_invention_performed":
                False,
        }

    nodes = []
    node_by_id = {}

    def register_node(
        node: dict[str, Any],
    ) -> None:

        node_id = node[
            "node_id"
        ]

        existing = node_by_id.get(
            node_id
        )

        if existing is None:

            node_by_id[
                node_id
            ] = copy.deepcopy(
                node
            )

            nodes.append(
                node
            )

            return

        if existing != node:
            raise DynamicSemanticGraphError(
                "Canonical graph node identity collision."
            )

    for record in validated_records:

        if not isinstance(
            record,
            dict,
        ):
            raise DynamicSemanticGraphError(
                "Validated graph intake record must be a dictionary."
            )

        if (
            record.get("schema")
            != "dynamic_graph_validated_intake_record_v1"
        ):
            raise DynamicSemanticGraphError(
                "Invalid validated graph intake record schema."
            )

        if record.get(
            "graph_intake_validated"
        ) is not True:
            raise DynamicSemanticGraphError(
                "Graph intake record is not validated."
            )

        if record.get(
            "graph_construction_authorized"
        ) is not True:
            raise DynamicSemanticGraphError(
                "Graph construction is not authorized for record."
            )

        claim_id = record.get(
            "claim_id"
        )

        claim_text = record.get(
            "claim_text"
        )

        claim_type = record.get(
            "claim_type"
        )

        final_integrity_id = record.get(
            "final_claim_integrity_id"
        )

        provenance_trace_id = record.get(
            "provenance_trace_id"
        )

        if (
            not isinstance(claim_id, str)
            or not claim_id.strip()
        ):
            raise DynamicSemanticGraphError(
                "Validated record requires claim_id."
            )

        if (
            not isinstance(claim_text, str)
            or not claim_text.strip()
        ):
            raise DynamicSemanticGraphError(
                "Validated record requires claim_text."
            )

        provenance = {
            "claim_id":
                claim_id,

            "final_claim_integrity_id":
                final_integrity_id,

            "final_claim_integrity_digest":
                record.get(
                    "final_claim_integrity_digest"
                ),

            "provenance_trace_id":
                provenance_trace_id,

            "provenance_trace_digest":
                record.get(
                    "provenance_trace_digest"
                ),
        }

        # ----------------------------------------------------------
        # CLAIM NODE
        # ----------------------------------------------------------

        register_node(
            make_node(
                node_type=
                    "CLAIM_NODE",

                source_object_type=
                    "CERTIFIED_CLAIM",

                source_object_id=
                    claim_id,

                payload={
                    "claim_id":
                        claim_id,

                    "claim_type":
                        claim_type,

                    "claim_text":
                        claim_text,

                    "support_state":
                        record.get(
                            "support_state"
                        ),

                    "support_balance":
                        record.get(
                            "support_balance"
                        ),

                    "relationship_counts":
                        copy.deepcopy(
                            record.get(
                                "relationship_counts"
                            )
                        ),

                    "downstream_claim_eligible":
                        record.get(
                            "downstream_claim_eligible"
                        ),
                },

                provenance=
                    provenance,
            )
        )

        # ----------------------------------------------------------
        # AUTHORITY NODE
        # ----------------------------------------------------------

        authority_reference = record.get(
            "authority_reference"
        )

        if not isinstance(
            authority_reference,
            dict,
        ):
            raise DynamicSemanticGraphError(
                "Validated graph record requires authority_reference."
            )

        authority_id = authority_reference.get(
            "final_authority_id"
        )

        if (
            isinstance(authority_id, str)
            and authority_id.strip()
        ):

            register_node(
                make_node(
                    node_type=
                        "AUTHORITY_NODE",

                    source_object_type=
                        "CERTIFIED_AUTHORITY",

                    source_object_id=
                        authority_id,

                    payload=
                        copy.deepcopy(
                            authority_reference
                        ),

                    provenance=
                        provenance,
                )
            )

        # ----------------------------------------------------------
        # INTEGRITY NODE
        # ----------------------------------------------------------

        integrity_state = record.get(
            "claim_integrity_state"
        )

        if (
            not isinstance(integrity_state, str)
            or not integrity_state.strip()
        ):
            raise DynamicSemanticGraphError(
                "Validated graph record requires claim integrity state."
            )

        register_node(
            make_node(
                node_type=
                    "INTEGRITY_NODE",

                source_object_type=
                    "CERTIFIED_CLAIM_INTEGRITY",

                source_object_id=
                    final_integrity_id,

                payload={
                    "claim_id":
                        claim_id,

                    "claim_integrity_state":
                        integrity_state,

                    "integrity_decision_basis":
                        record.get(
                            "integrity_decision_basis"
                        ),
                },

                provenance=
                    provenance,
            )
        )

        # ----------------------------------------------------------
        # GUARD NODE
        # ----------------------------------------------------------

        guard_disposition = record.get(
            "guard_disposition"
        )

        if (
            not isinstance(guard_disposition, str)
            or not guard_disposition.strip()
        ):
            raise DynamicSemanticGraphError(
                "Validated graph record requires guard disposition."
            )

        register_node(
            make_node(
                node_type=
                    "GUARD_NODE",

                source_object_type=
                    "CERTIFIED_CLAIM_GUARD",

                source_object_id=
                    (
                        str(final_integrity_id)
                        + ":guard"
                    ),

                payload={
                    "claim_id":
                        claim_id,

                    "guard_disposition":
                        guard_disposition,

                    "downstream_claim_eligible":
                        record.get(
                            "downstream_claim_eligible"
                        ),
                },

                provenance=
                    provenance,
            )
        )

        # ----------------------------------------------------------
        # PROVENANCE NODE
        # ----------------------------------------------------------

        if (
            not isinstance(provenance_trace_id, str)
            or not provenance_trace_id.strip()
        ):
            raise DynamicSemanticGraphError(
                "Validated graph record requires provenance trace id."
            )

        register_node(
            make_node(
                node_type=
                    "PROVENANCE_NODE",

                source_object_type=
                    "CERTIFIED_PROVENANCE_TRACE",

                source_object_id=
                    provenance_trace_id,

                payload={
                    "claim_id":
                        claim_id,

                    "provenance_trace_id":
                        provenance_trace_id,

                    "provenance_trace_digest":
                        record.get(
                            "provenance_trace_digest"
                        ),
                },

                provenance=
                    provenance,
            )
        )

        # ----------------------------------------------------------
        # EXPLICIT EVIDENCE NODES
        # ----------------------------------------------------------

        evidence_trace = record.get(
            "evidence_trace"
        )

        if not isinstance(
            evidence_trace,
            list,
        ):
            raise DynamicSemanticGraphError(
                "evidence_trace must be a list."
            )

        for evidence in evidence_trace:

            if not isinstance(
                evidence,
                dict,
            ):
                raise DynamicSemanticGraphError(
                    "Evidence trace item must be a dictionary."
                )

            evidence_id = evidence.get(
                "evidence_id"
            )

            if evidence_id is None:
                continue

            if (
                not isinstance(evidence_id, str)
                or not evidence_id.strip()
            ):
                raise DynamicSemanticGraphError(
                    "Explicit evidence_id must be non-empty."
                )

            register_node(
                make_node(
                    node_type=
                        "EVIDENCE_NODE",

                    source_object_type=
                        "CERTIFIED_EVIDENCE_TRACE",

                    source_object_id=
                        evidence_id,

                    payload=
                        copy.deepcopy(
                            evidence
                        ),

                    provenance=
                        provenance,
                )
            )

    nodes.sort(
        key=lambda item: (
            item["node_type"],
            item["source_object_id"],
            item["node_id"],
        )
    )

    node_ids = [
        node["node_id"]
        for node in nodes
    ]

    if len(node_ids) != len(
        set(node_ids)
    ):
        raise DynamicSemanticGraphError(
            "Duplicate canonical graph node IDs detected."
        )

    graph_version_material = {
        "dynamic_semantic_graph_version":
            DYNAMIC_SEMANTIC_GRAPH_VERSION,

        "node_ids":
            node_ids,

        "node_payload_digests": [
            node[
                "payload_digest"
            ]
            for node in nodes
        ],
    }

    graph_version_digest = digest(
        graph_version_material
    )

    graph_version_id = (
        "graphversion:v1:"
        + graph_version_digest
    )

    node_type_counts = {}

    for node in nodes:

        node_type = node[
            "node_type"
        ]

        node_type_counts[
            node_type
        ] = (
            node_type_counts.get(
                node_type,
                0,
            )
            + 1
        )

    return {
        "schema":
            "dynamic_semantic_graph_node_construction_result_v1",

        "dynamic_semantic_graph_version":
            DYNAMIC_SEMANTIC_GRAPH_VERSION,

        "phase":
            DYNAMIC_SEMANTIC_GRAPH_PHASE,

        "patch":
            "4.6.26E",

        "status":
            "CANONICAL_GRAPH_NODES_CONSTRUCTED",

        "graph_version_id":
            graph_version_id,

        "graph_version_digest":
            graph_version_digest,

        "node_count":
            len(nodes),

        "node_type_counts":
            node_type_counts,

        "canonical_graph_nodes":
            nodes,

        "validated_graph_intake_records":
            copy.deepcopy(
                validated_records
            ),

        "scope_mutation_contract":
            copy.deepcopy(
                contract
            ),

        "architecture":
            copy.deepcopy(
                architecture
            ),

        "final_claim_integrity_package":
            copy.deepcopy(
                final_claim_integrity_package
            ),

        "preservation_contract":
            copy.deepcopy(
                preservation_contract
            ),

        "processing_boundaries": {
            "canonical_graph_node_construction_performed":
                True,

            "graph_node_creation_performed":
                True,

            "graph_mutation_performed":
                True,

            "graph_edge_creation_performed":
                False,

            "graph_merge_performed":
                False,

            "support_reassessment_performed":
                False,

            "conflict_redetection_performed":
                False,

            "conflict_reclassification_performed":
                False,

            "integrity_redecision_performed":
                False,

            "guard_redisposition_performed":
                False,

            "authority_rescoring_performed":
                False,

            "authority_reclassification_performed":
                False,

            "semantic_memory_written":
                False,

            "learning_performed":
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

            "unsupported_node_invention_performed":
                False,

            "unsupported_edge_invention_performed":
                False,
        },

        "policy":
            "CERTIFIED_CANONICAL_DYNAMIC_GRAPH_NODE_CONSTRUCTION",

        "next":
            "canonical_graph_edge_construction",
    }

def construct_canonical_graph_edges_v1(
    node_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.26F ? Canonical Graph Edge Construction.

    Constructs deterministic canonical graph edges only from
    relationships explicitly represented by certified upstream input.

    This stage does not:
    - invent unsupported relationships,
    - project claim-to-claim conflicts,
    - perform Authority integration,
    - merge graph versions,
    - reassess semantic intelligence,
    - write Semantic Memory,
    - execute learning/reasoning,
    - select targets,
    - make linking decisions.
    """

    import hashlib
    import json

    if not isinstance(
        node_result,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "node_result must be a dictionary."
        )

    expected_lifecycle = {
        "schema":
            "dynamic_semantic_graph_node_construction_result_v1",

        "dynamic_semantic_graph_version":
            DYNAMIC_SEMANTIC_GRAPH_VERSION,

        "phase":
            DYNAMIC_SEMANTIC_GRAPH_PHASE,

        "patch":
            "4.6.26E",

        "status":
            "CANONICAL_GRAPH_NODES_CONSTRUCTED",

        "policy":
            "CERTIFIED_CANONICAL_DYNAMIC_GRAPH_NODE_CONSTRUCTION",

        "next":
            "canonical_graph_edge_construction",
    }

    for key, expected in expected_lifecycle.items():

        if node_result.get(key) != expected:
            raise DynamicSemanticGraphError(
                "Invalid 4.6.26E lifecycle field: "
                f"{key}"
            )

    nodes = node_result.get(
        "canonical_graph_nodes"
    )

    validated_records = node_result.get(
        "validated_graph_intake_records"
    )

    contract = node_result.get(
        "scope_mutation_contract"
    )

    architecture = node_result.get(
        "architecture"
    )

    preservation_contract = node_result.get(
        "preservation_contract"
    )

    final_claim_integrity_package = (
        node_result.get(
            "final_claim_integrity_package"
        )
    )

    if not isinstance(nodes, list):
        raise DynamicSemanticGraphError(
            "canonical_graph_nodes must be a list."
        )

    if (
        node_result.get("node_count")
        != len(nodes)
    ):
        raise DynamicSemanticGraphError(
            "Canonical graph node count mismatch."
        )

    if not isinstance(
        validated_records,
        list,
    ):
        raise DynamicSemanticGraphError(
            "validated_graph_intake_records must be a list."
        )

    if not isinstance(contract, dict):
        raise DynamicSemanticGraphError(
            "scope_mutation_contract must be a dictionary."
        )

    if (
        contract.get("schema")
        != "dynamic_semantic_graph_scope_mutation_contract_v1"
    ):
        raise DynamicSemanticGraphError(
            "Invalid scope/mutation contract schema."
        )

    if not isinstance(architecture, dict):
        raise DynamicSemanticGraphError(
            "architecture must be a dictionary."
        )

    if not isinstance(
        preservation_contract,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "preservation_contract must be a dictionary."
        )

    if not isinstance(
        final_claim_integrity_package,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "final_claim_integrity_package must be a dictionary."
        )

    permissions = contract.get(
        "mutation_permissions"
    )

    forbidden = contract.get(
        "forbidden_mutations"
    )

    if not isinstance(permissions, dict):
        raise DynamicSemanticGraphError(
            "mutation_permissions must be a dictionary."
        )

    if not isinstance(forbidden, dict):
        raise DynamicSemanticGraphError(
            "forbidden_mutations must be a dictionary."
        )

    if (
        permissions.get(
            "may_create_graph_edges_from_certified_relationships"
        )
        is not True
    ):
        raise DynamicSemanticGraphError(
            "Canonical graph edge construction is not authorized."
        )

    if (
        forbidden.get(
            "may_invent_unsupported_edges"
        )
        is not False
    ):
        raise DynamicSemanticGraphError(
            "Unsupported graph-edge invention prohibition drift."
        )

    allowed_edge_types = set(
        architecture.get(
            "edge_types",
            (),
        )
    )

    required_edge_types = {
        "CLAIM_SUPPORTED_BY_EVIDENCE",
        "CLAIM_PARTIALLY_SUPPORTED_BY_EVIDENCE",
        "CLAIM_CHALLENGED_BY_EVIDENCE",
        "CLAIM_CONTRADICTED_BY_EVIDENCE",
        "CLAIM_HAS_NEUTRAL_EVIDENCE",
        "CLAIM_HAS_INSUFFICIENT_EVIDENCE",
        "CLAIM_HAS_UNRESOLVED_EVIDENCE",
        "CLAIM_HAS_INTEGRITY_STATE",
        "CLAIM_HAS_GUARD_DISPOSITION",
        "EVIDENCE_HAS_PROVENANCE",
        "INTEGRITY_HAS_PROVENANCE",
    }

    if not required_edge_types.issubset(
        allowed_edge_types
    ):
        raise DynamicSemanticGraphError(
            "Required canonical graph edge types are missing."
        )

    def canonical_json(value: Any) -> str:

        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )

    def digest(value: Any) -> str:

        return hashlib.sha256(
            canonical_json(
                value
            ).encode(
                "utf-8"
            )
        ).hexdigest()

    node_by_key = {}

    for node in nodes:

        if not isinstance(node, dict):
            raise DynamicSemanticGraphError(
                "Canonical graph node must be a dictionary."
            )

        if (
            node.get("schema")
            != "dynamic_semantic_graph_node_v1"
        ):
            raise DynamicSemanticGraphError(
                "Invalid canonical graph node schema."
            )

        node_id = node.get(
            "node_id"
        )

        node_type = node.get(
            "node_type"
        )

        source_object_id = node.get(
            "source_object_id"
        )

        if (
            not isinstance(node_id, str)
            or not node_id.startswith(
                "graphnode:v1:"
            )
        ):
            raise DynamicSemanticGraphError(
                "Invalid canonical graph node ID."
            )

        key = (
            node_type,
            source_object_id,
        )

        if key in node_by_key:
            raise DynamicSemanticGraphError(
                "Duplicate canonical graph node key."
            )

        node_by_key[key] = node

    def require_node(
        node_type: str,
        source_object_id: str,
    ) -> dict[str, Any]:

        node = node_by_key.get(
            (
                node_type,
                source_object_id,
            )
        )

        if node is None:
            raise DynamicSemanticGraphError(
                "Required canonical graph node is missing: "
                f"{node_type}:{source_object_id}"
            )

        return node

    def make_edge(
        *,
        edge_type: str,
        from_node: dict[str, Any],
        to_node: dict[str, Any],
        relation_source_id: str,
        payload: dict[str, Any],
        provenance: dict[str, Any],
    ) -> dict[str, Any]:

        if edge_type not in allowed_edge_types:
            raise DynamicSemanticGraphError(
                "Unsupported canonical edge type: "
                f"{edge_type}"
            )

        if (
            not isinstance(relation_source_id, str)
            or not relation_source_id.strip()
        ):
            raise DynamicSemanticGraphError(
                "Canonical edge requires relation_source_id."
            )

        identity_material = {
            "edge_type":
                edge_type,

            "from_node_id":
                from_node["node_id"],

            "to_node_id":
                to_node["node_id"],

            "relation_source_id":
                relation_source_id,
        }

        edge_hash = digest(
            identity_material
        )

        return {
            "schema":
                "dynamic_semantic_graph_edge_v1",

            "edge_id":
                "graphedge:v1:"
                + edge_hash,

            "edge_type":
                edge_type,

            "from_node_id":
                from_node[
                    "node_id"
                ],

            "to_node_id":
                to_node[
                    "node_id"
                ],

            "from_node_type":
                from_node[
                    "node_type"
                ],

            "to_node_type":
                to_node[
                    "node_type"
                ],

            "relation_source_id":
                relation_source_id,

            "lifecycle_state":
                "ACTIVE",

            "payload":
                copy.deepcopy(
                    payload
                ),

            "payload_digest":
                digest(
                    payload
                ),

            "provenance":
                copy.deepcopy(
                    provenance
                ),

            "idempotency_key":
                "graphedge-idempotency:v1:"
                + edge_hash,

            "canonical_identity_deterministic":
                True,

            "certified_relationship_backed":
                True,

            "unsupported_invention_performed":
                False,
        }

    edges = []
    edge_by_id = {}

    def register_edge(
        edge: dict[str, Any],
    ) -> None:

        edge_id = edge[
            "edge_id"
        ]

        existing = edge_by_id.get(
            edge_id
        )

        if existing is None:

            edge_by_id[
                edge_id
            ] = copy.deepcopy(
                edge
            )

            edges.append(
                edge
            )

            return

        if existing != edge:
            raise DynamicSemanticGraphError(
                "Canonical graph edge identity collision."
            )

    evidence_relationship_to_edge = {
        "SUPPORTS":
            "CLAIM_SUPPORTED_BY_EVIDENCE",

        "PARTIALLY_SUPPORTS":
            "CLAIM_PARTIALLY_SUPPORTED_BY_EVIDENCE",

        "CHALLENGES":
            "CLAIM_CHALLENGED_BY_EVIDENCE",

        "CONTRADICTS":
            "CLAIM_CONTRADICTED_BY_EVIDENCE",

        "NEUTRAL":
            "CLAIM_HAS_NEUTRAL_EVIDENCE",

        "INSUFFICIENT":
            "CLAIM_HAS_INSUFFICIENT_EVIDENCE",

        "UNRESOLVED":
            "CLAIM_HAS_UNRESOLVED_EVIDENCE",
    }

    for record in validated_records:

        if not isinstance(record, dict):
            raise DynamicSemanticGraphError(
                "Validated graph intake record must be a dictionary."
            )

        if (
            record.get("schema")
            != "dynamic_graph_validated_intake_record_v1"
        ):
            raise DynamicSemanticGraphError(
                "Invalid validated graph intake record schema."
            )

        claim_id = record.get(
            "claim_id"
        )

        final_integrity_id = record.get(
            "final_claim_integrity_id"
        )

        provenance_trace_id = record.get(
            "provenance_trace_id"
        )

        if (
            not isinstance(claim_id, str)
            or not claim_id.strip()
        ):
            raise DynamicSemanticGraphError(
                "Validated record requires claim_id."
            )

        if (
            not isinstance(final_integrity_id, str)
            or not final_integrity_id.strip()
        ):
            raise DynamicSemanticGraphError(
                "Validated record requires final_claim_integrity_id."
            )

        if (
            not isinstance(provenance_trace_id, str)
            or not provenance_trace_id.strip()
        ):
            raise DynamicSemanticGraphError(
                "Validated record requires provenance_trace_id."
            )

        claim_node = require_node(
            "CLAIM_NODE",
            claim_id,
        )

        integrity_node = require_node(
            "INTEGRITY_NODE",
            final_integrity_id,
        )

        guard_node = require_node(
            "GUARD_NODE",
            final_integrity_id
            + ":guard",
        )

        provenance_node = require_node(
            "PROVENANCE_NODE",
            provenance_trace_id,
        )

        provenance = {
            "claim_id":
                claim_id,

            "final_claim_integrity_id":
                final_integrity_id,

            "provenance_trace_id":
                provenance_trace_id,

            "provenance_trace_digest":
                record.get(
                    "provenance_trace_digest"
                ),
        }

        register_edge(
            make_edge(
                edge_type=
                    "CLAIM_HAS_INTEGRITY_STATE",

                from_node=
                    claim_node,

                to_node=
                    integrity_node,

                relation_source_id=
                    final_integrity_id,

                payload={
                    "claim_id":
                        claim_id,

                    "claim_integrity_state":
                        record.get(
                            "claim_integrity_state"
                        ),

                    "integrity_decision_basis":
                        record.get(
                            "integrity_decision_basis"
                        ),
                },

                provenance=
                    provenance,
            )
        )

        register_edge(
            make_edge(
                edge_type=
                    "CLAIM_HAS_GUARD_DISPOSITION",

                from_node=
                    claim_node,

                to_node=
                    guard_node,

                relation_source_id=
                    final_integrity_id
                    + ":guard",

                payload={
                    "claim_id":
                        claim_id,

                    "guard_disposition":
                        record.get(
                            "guard_disposition"
                        ),

                    "downstream_claim_eligible":
                        record.get(
                            "downstream_claim_eligible"
                        ),
                },

                provenance=
                    provenance,
            )
        )

        register_edge(
            make_edge(
                edge_type=
                    "INTEGRITY_HAS_PROVENANCE",

                from_node=
                    integrity_node,

                to_node=
                    provenance_node,

                relation_source_id=
                    provenance_trace_id,

                payload={
                    "claim_id":
                        claim_id,

                    "provenance_trace_id":
                        provenance_trace_id,
                },

                provenance=
                    provenance,
            )
        )

        evidence_trace = record.get(
            "evidence_trace"
        )

        if not isinstance(
            evidence_trace,
            list,
        ):
            raise DynamicSemanticGraphError(
                "evidence_trace must be a list."
            )

        for evidence in evidence_trace:

            if not isinstance(
                evidence,
                dict,
            ):
                raise DynamicSemanticGraphError(
                    "Evidence trace item must be a dictionary."
                )

            evidence_id = evidence.get(
                "evidence_id"
            )

            if evidence_id is None:
                continue

            if (
                not isinstance(evidence_id, str)
                or not evidence_id.strip()
            ):
                raise DynamicSemanticGraphError(
                    "Explicit evidence_id must be non-empty."
                )

            relationship = evidence.get(
                "relationship"
            )

            if relationship not in evidence_relationship_to_edge:
                raise DynamicSemanticGraphError(
                    "Unsupported evidence relationship for graph edge: "
                    f"{relationship}"
                )

            evidence_node = require_node(
                "EVIDENCE_NODE",
                evidence_id,
            )

            edge_type = (
                evidence_relationship_to_edge[
                    relationship
                ]
            )

            register_edge(
                make_edge(
                    edge_type=
                        edge_type,

                    from_node=
                        claim_node,

                    to_node=
                        evidence_node,

                    relation_source_id=
                        evidence_id
                        + ":"
                        + relationship,

                    payload={
                        "claim_id":
                            claim_id,

                        "evidence_id":
                            evidence_id,

                        "relationship":
                            relationship,

                        "source_subject_id":
                            evidence.get(
                                "source_subject_id"
                            ),
                    },

                    provenance=
                        provenance,
                )
            )

            register_edge(
                make_edge(
                    edge_type=
                        "EVIDENCE_HAS_PROVENANCE",

                    from_node=
                        evidence_node,

                    to_node=
                        provenance_node,

                    relation_source_id=
                        evidence_id
                        + ":provenance:"
                        + provenance_trace_id,

                    payload={
                        "claim_id":
                            claim_id,

                        "evidence_id":
                            evidence_id,

                        "provenance_trace_id":
                            provenance_trace_id,
                    },

                    provenance=
                        provenance,
                )
            )

    edges.sort(
        key=lambda item: (
            item[
                "edge_type"
            ],
            item[
                "from_node_id"
            ],
            item[
                "to_node_id"
            ],
            item[
                "edge_id"
            ],
        )
    )

    edge_ids = [
        edge[
            "edge_id"
        ]
        for edge in edges
    ]

    if len(edge_ids) != len(
        set(edge_ids)
    ):
        raise DynamicSemanticGraphError(
            "Duplicate canonical graph edge IDs detected."
        )

    node_ids = {
        node[
            "node_id"
        ]
        for node in nodes
    }

    for edge in edges:

        if (
            edge[
                "from_node_id"
            ]
            not in node_ids
        ):
            raise DynamicSemanticGraphError(
                "Canonical edge has missing from-node."
            )

        if (
            edge[
                "to_node_id"
            ]
            not in node_ids
        ):
            raise DynamicSemanticGraphError(
                "Canonical edge has missing to-node."
            )

    base_graph_version_id = node_result.get(
        "graph_version_id"
    )

    base_graph_version_digest = node_result.get(
        "graph_version_digest"
    )

    if (
        not isinstance(
            base_graph_version_id,
            str,
        )
        or not base_graph_version_id.startswith(
            "graphversion:v1:"
        )
    ):
        raise DynamicSemanticGraphError(
            "Invalid base graph version ID."
        )

    if (
        not isinstance(
            base_graph_version_digest,
            str,
        )
        or len(
            base_graph_version_digest
        )
        != 64
    ):
        raise DynamicSemanticGraphError(
            "Invalid base graph version digest."
        )

    graph_version_material = {
        "base_graph_version_id":
            base_graph_version_id,

        "base_graph_version_digest":
            base_graph_version_digest,

        "edge_ids":
            edge_ids,

        "edge_payload_digests": [
            edge[
                "payload_digest"
            ]
            for edge in edges
        ],
    }

    graph_version_digest = digest(
        graph_version_material
    )

    graph_version_id = (
        "graphversion:v1:"
        + graph_version_digest
    )

    edge_type_counts = {}

    for edge in edges:

        edge_type = edge[
            "edge_type"
        ]

        edge_type_counts[
            edge_type
        ] = (
            edge_type_counts.get(
                edge_type,
                0,
            )
            + 1
        )

    return {
        "schema":
            "dynamic_semantic_graph_edge_construction_result_v1",

        "dynamic_semantic_graph_version":
            DYNAMIC_SEMANTIC_GRAPH_VERSION,

        "phase":
            DYNAMIC_SEMANTIC_GRAPH_PHASE,

        "patch":
            "4.6.26F",

        "status":
            "CANONICAL_GRAPH_EDGES_CONSTRUCTED",

        "base_graph_version_id":
            base_graph_version_id,

        "base_graph_version_digest":
            base_graph_version_digest,

        "graph_version_id":
            graph_version_id,

        "graph_version_digest":
            graph_version_digest,

        "node_count":
            len(nodes),

        "edge_count":
            len(edges),

        "edge_type_counts":
            edge_type_counts,

        "canonical_graph_nodes":
            copy.deepcopy(
                nodes
            ),

        "canonical_graph_edges":
            edges,

        "validated_graph_intake_records":
            copy.deepcopy(
                validated_records
            ),

        "scope_mutation_contract":
            copy.deepcopy(
                contract
            ),

        "architecture":
            copy.deepcopy(
                architecture
            ),

        "final_claim_integrity_package":
            copy.deepcopy(
                final_claim_integrity_package
            ),

        "preservation_contract":
            copy.deepcopy(
                preservation_contract
            ),

        "processing_boundaries": {
            "canonical_graph_edge_construction_performed":
                True,

            "graph_node_creation_performed":
                False,

            "graph_edge_creation_performed":
                True,

            "graph_mutation_performed":
                True,

            "claim_evidence_edges_created":
                True,

            "claim_integrity_edges_created":
                True,

            "claim_guard_edges_created":
                True,

            "evidence_provenance_edges_created":
                True,

            "integrity_provenance_edges_created":
                True,

            "claim_conflict_edges_created":
                False,

            "authority_integration_performed":
                False,

            "graph_merge_performed":
                False,

            "support_reassessment_performed":
                False,

            "conflict_redetection_performed":
                False,

            "conflict_reclassification_performed":
                False,

            "integrity_redecision_performed":
                False,

            "guard_redisposition_performed":
                False,

            "authority_rescoring_performed":
                False,

            "authority_reclassification_performed":
                False,

            "semantic_memory_written":
                False,

            "learning_performed":
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

            "unsupported_node_invention_performed":
                False,

            "unsupported_edge_invention_performed":
                False,
        },

        "policy":
            "CERTIFIED_CANONICAL_DYNAMIC_GRAPH_EDGE_CONSTRUCTION",

        "next":
            "claim_evidence_authority_graph_integration",
    }

def integrate_claim_evidence_authority_graph_v1(
    edge_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.26G ? Claim / Evidence / Authority Graph Integration.

    Integrates the certified Claim/Evidence graph with the certified
    Authority subject relationship.

    It may construct a minimal SOURCE_NODE only from a certified,
    deterministic Authority subject identity.

    It does not:
    - fetch source metadata,
    - invent source identities,
    - rescore/reclassify Authority,
    - reassess claims,
    - detect/reclassify conflict,
    - make integrity decisions,
    - override guard state,
    - write Semantic Memory,
    - execute learning/reasoning,
    - create/select targets,
    - make linking decisions.
    """

    import hashlib
    import json

    if not isinstance(
        edge_result,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "edge_result must be a dictionary."
        )

    expected_lifecycle = {
        "schema":
            "dynamic_semantic_graph_edge_construction_result_v1",

        "dynamic_semantic_graph_version":
            DYNAMIC_SEMANTIC_GRAPH_VERSION,

        "phase":
            DYNAMIC_SEMANTIC_GRAPH_PHASE,

        "patch":
            "4.6.26F",

        "status":
            "CANONICAL_GRAPH_EDGES_CONSTRUCTED",

        "policy":
            "CERTIFIED_CANONICAL_DYNAMIC_GRAPH_EDGE_CONSTRUCTION",

        "next":
            "claim_evidence_authority_graph_integration",
    }

    for key, expected in expected_lifecycle.items():

        if edge_result.get(key) != expected:
            raise DynamicSemanticGraphError(
                "Invalid 4.6.26F lifecycle field: "
                f"{key}"
            )

    nodes = edge_result.get(
        "canonical_graph_nodes"
    )

    edges = edge_result.get(
        "canonical_graph_edges"
    )

    validated_records = edge_result.get(
        "validated_graph_intake_records"
    )

    contract = edge_result.get(
        "scope_mutation_contract"
    )

    architecture = edge_result.get(
        "architecture"
    )

    preservation_contract = edge_result.get(
        "preservation_contract"
    )

    final_claim_integrity_package = (
        edge_result.get(
            "final_claim_integrity_package"
        )
    )

    if not isinstance(nodes, list):
        raise DynamicSemanticGraphError(
            "canonical_graph_nodes must be a list."
        )

    if not isinstance(edges, list):
        raise DynamicSemanticGraphError(
            "canonical_graph_edges must be a list."
        )

    if (
        edge_result.get("node_count")
        != len(nodes)
    ):
        raise DynamicSemanticGraphError(
            "Canonical graph node count mismatch."
        )

    if (
        edge_result.get("edge_count")
        != len(edges)
    ):
        raise DynamicSemanticGraphError(
            "Canonical graph edge count mismatch."
        )

    if not isinstance(
        validated_records,
        list,
    ):
        raise DynamicSemanticGraphError(
            "validated_graph_intake_records must be a list."
        )

    if not isinstance(contract, dict):
        raise DynamicSemanticGraphError(
            "scope_mutation_contract must be a dictionary."
        )

    if (
        contract.get("schema")
        != "dynamic_semantic_graph_scope_mutation_contract_v1"
    ):
        raise DynamicSemanticGraphError(
            "Invalid graph scope/mutation contract schema."
        )

    if not isinstance(architecture, dict):
        raise DynamicSemanticGraphError(
            "architecture must be a dictionary."
        )

    if not isinstance(
        preservation_contract,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "preservation_contract must be a dictionary."
        )

    if not isinstance(
        final_claim_integrity_package,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "final_claim_integrity_package must be a dictionary."
        )

    allowed_node_types = set(
        architecture.get(
            "node_types",
            (),
        )
    )

    allowed_edge_types = set(
        architecture.get(
            "edge_types",
            (),
        )
    )

    if "SOURCE_NODE" not in allowed_node_types:
        raise DynamicSemanticGraphError(
            "SOURCE_NODE is not permitted by graph architecture."
        )

    for required_edge in (
        "CLAIM_ASSERTED_BY_SOURCE",
        "SOURCE_HAS_AUTHORITY",
    ):

        if required_edge not in allowed_edge_types:
            raise DynamicSemanticGraphError(
                "Required Authority integration edge is missing: "
                f"{required_edge}"
            )

    forbidden = contract.get(
        "forbidden_mutations"
    )

    if not isinstance(forbidden, dict):
        raise DynamicSemanticGraphError(
            "forbidden_mutations must be a dictionary."
        )

    for flag in (
        "may_invent_unsupported_nodes",
        "may_invent_unsupported_edges",
        "may_rescore_authority",
        "may_reclassify_authority",
        "may_write_semantic_memory",
        "may_execute_learning",
        "may_execute_reasoning",
        "may_create_active_targets",
        "may_select_final_external_target",
        "may_make_linking_decision",
        "may_create_editor_highlight",
    ):

        if forbidden.get(flag) is not False:
            raise DynamicSemanticGraphError(
                "Forbidden integration capability drift: "
                f"{flag}"
            )

    def canonical_json(
        value: Any,
    ) -> str:

        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )

    def digest(
        value: Any,
    ) -> str:

        return hashlib.sha256(
            canonical_json(
                value
            ).encode(
                "utf-8"
            )
        ).hexdigest()

    integrated_nodes = copy.deepcopy(
        nodes
    )

    integrated_edges = copy.deepcopy(
        edges
    )

    node_by_key = {}

    node_by_id = {}

    for node in integrated_nodes:

        if (
            not isinstance(node, dict)
            or node.get("schema")
            != "dynamic_semantic_graph_node_v1"
        ):
            raise DynamicSemanticGraphError(
                "Invalid canonical graph node."
            )

        node_id = node.get(
            "node_id"
        )

        node_type = node.get(
            "node_type"
        )

        source_object_id = node.get(
            "source_object_id"
        )

        if (
            not isinstance(node_id, str)
            or not node_id.startswith(
                "graphnode:v1:"
            )
        ):
            raise DynamicSemanticGraphError(
                "Invalid canonical graph node ID."
            )

        key = (
            node_type,
            source_object_id,
        )

        if key in node_by_key:
            raise DynamicSemanticGraphError(
                "Duplicate canonical graph node key."
            )

        if node_id in node_by_id:
            raise DynamicSemanticGraphError(
                "Duplicate canonical graph node ID."
            )

        node_by_key[key] = node
        node_by_id[node_id] = node

    edge_by_id = {}

    for edge in integrated_edges:

        if (
            not isinstance(edge, dict)
            or edge.get("schema")
            != "dynamic_semantic_graph_edge_v1"
        ):
            raise DynamicSemanticGraphError(
                "Invalid canonical graph edge."
            )

        edge_id = edge.get(
            "edge_id"
        )

        if (
            not isinstance(edge_id, str)
            or not edge_id.startswith(
                "graphedge:v1:"
            )
        ):
            raise DynamicSemanticGraphError(
                "Invalid canonical graph edge ID."
            )

        if edge_id in edge_by_id:
            raise DynamicSemanticGraphError(
                "Duplicate canonical graph edge ID."
            )

        edge_by_id[
            edge_id
        ] = edge

    def require_node(
        node_type: str,
        source_object_id: str,
    ) -> dict[str, Any]:

        node = node_by_key.get(
            (
                node_type,
                source_object_id,
            )
        )

        if node is None:
            raise DynamicSemanticGraphError(
                "Required graph node is missing: "
                f"{node_type}:{source_object_id}"
            )

        return node

    def register_node(
        node: dict[str, Any],
    ) -> dict[str, Any]:

        key = (
            node[
                "node_type"
            ],
            node[
                "source_object_id"
            ],
        )

        existing = node_by_key.get(
            key
        )

        if existing is not None:

            if existing != node:
                raise DynamicSemanticGraphError(
                    "Graph source-node identity collision."
                )

            return existing

        node_id = node[
            "node_id"
        ]

        if node_id in node_by_id:
            raise DynamicSemanticGraphError(
                "Graph source-node ID collision."
            )

        integrated_nodes.append(
            node
        )

        node_by_key[
            key
        ] = node

        node_by_id[
            node_id
        ] = node

        return node

    def make_source_node(
        *,
        subject_id: str,
        authority_reference: dict[str, Any],
        provenance: dict[str, Any],
    ) -> dict[str, Any]:

        identity_material = {
            "node_type":
                "SOURCE_NODE",

            "source_object_type":
                "CERTIFIED_AUTHORITY_SUBJECT",

            "source_object_id":
                subject_id,
        }

        node_hash = digest(
            identity_material
        )

        payload = {
            "subject_id":
                subject_id,

            "subject_type":
                "SOURCE",

            "authority_reference_id":
                authority_reference.get(
                    "final_authority_id"
                ),

            "authority_reference_digest":
                authority_reference.get(
                    "final_authority_digest"
                ),
        }

        return {
            "schema":
                "dynamic_semantic_graph_node_v1",

            "node_id":
                "graphnode:v1:"
                + node_hash,

            "node_type":
                "SOURCE_NODE",

            "source_object_type":
                "CERTIFIED_AUTHORITY_SUBJECT",

            "source_object_id":
                subject_id,

            "lifecycle_state":
                "ACTIVE",

            "payload":
                payload,

            "payload_digest":
                digest(
                    payload
                ),

            "provenance":
                copy.deepcopy(
                    provenance
                ),

            "idempotency_key":
                "graphnode-idempotency:v1:"
                + node_hash,

            "canonical_identity_deterministic":
                True,

            "certified_input_backed":
                True,

            "unsupported_invention_performed":
                False,
        }

    def make_edge(
        *,
        edge_type: str,
        from_node: dict[str, Any],
        to_node: dict[str, Any],
        relation_source_id: str,
        payload: dict[str, Any],
        provenance: dict[str, Any],
    ) -> dict[str, Any]:

        identity_material = {
            "edge_type":
                edge_type,

            "from_node_id":
                from_node[
                    "node_id"
                ],

            "to_node_id":
                to_node[
                    "node_id"
                ],

            "relation_source_id":
                relation_source_id,
        }

        edge_hash = digest(
            identity_material
        )

        return {
            "schema":
                "dynamic_semantic_graph_edge_v1",

            "edge_id":
                "graphedge:v1:"
                + edge_hash,

            "edge_type":
                edge_type,

            "from_node_id":
                from_node[
                    "node_id"
                ],

            "to_node_id":
                to_node[
                    "node_id"
                ],

            "from_node_type":
                from_node[
                    "node_type"
                ],

            "to_node_type":
                to_node[
                    "node_type"
                ],

            "relation_source_id":
                relation_source_id,

            "lifecycle_state":
                "ACTIVE",

            "payload":
                copy.deepcopy(
                    payload
                ),

            "payload_digest":
                digest(
                    payload
                ),

            "provenance":
                copy.deepcopy(
                    provenance
                ),

            "idempotency_key":
                "graphedge-idempotency:v1:"
                + edge_hash,

            "canonical_identity_deterministic":
                True,

            "certified_relationship_backed":
                True,

            "unsupported_invention_performed":
                False,
        }

    def register_edge(
        edge: dict[str, Any],
    ) -> None:

        edge_id = edge[
            "edge_id"
        ]

        existing = edge_by_id.get(
            edge_id
        )

        if existing is not None:

            if existing != edge:
                raise DynamicSemanticGraphError(
                    "Authority integration edge collision."
                )

            return

        integrated_edges.append(
            edge
        )

        edge_by_id[
            edge_id
        ] = edge

    integrated_source_ids = set()
    integrated_authority_ids = set()

    for record in validated_records:

        if (
            not isinstance(record, dict)
            or record.get("schema")
            != "dynamic_graph_validated_intake_record_v1"
        ):
            raise DynamicSemanticGraphError(
                "Invalid validated graph intake record."
            )

        claim_id = record.get(
            "claim_id"
        )

        authority_reference = record.get(
            "authority_reference"
        )

        if (
            not isinstance(claim_id, str)
            or not claim_id.strip()
        ):
            raise DynamicSemanticGraphError(
                "Authority integration requires claim_id."
            )

        if not isinstance(
            authority_reference,
            dict,
        ):
            raise DynamicSemanticGraphError(
                "Authority integration requires authority_reference."
            )

        authority_id = authority_reference.get(
            "final_authority_id"
        )

        if (
            not isinstance(authority_id, str)
            or not authority_id.startswith(
                "authfinal:v1:"
            )
        ):
            raise DynamicSemanticGraphError(
                "Invalid certified final_authority_id."
            )

        subject_id = authority_id[
            len("authfinal:v1:"):
        ]

        if not subject_id.strip():
            raise DynamicSemanticGraphError(
                "Authority subject identity is empty."
            )

        reconstructed_authority_id = (
            "authfinal:v1:"
            + subject_id
        )

        if reconstructed_authority_id != authority_id:
            raise DynamicSemanticGraphError(
                "Authority subject identity contract mismatch."
            )

        claim_node = require_node(
            "CLAIM_NODE",
            claim_id,
        )

        authority_node = require_node(
            "AUTHORITY_NODE",
            authority_id,
        )

        provenance = {
            "claim_id":
                claim_id,

            "final_authority_id":
                authority_id,

            "final_authority_digest":
                authority_reference.get(
                    "final_authority_digest"
                ),

            "provenance_trace_id":
                record.get(
                    "provenance_trace_id"
                ),

            "provenance_trace_digest":
                record.get(
                    "provenance_trace_digest"
                ),
        }

        source_node = register_node(
            make_source_node(
                subject_id=
                    subject_id,

                authority_reference=
                    authority_reference,

                provenance=
                    provenance,
            )
        )

        register_edge(
            make_edge(
                edge_type=
                    "CLAIM_ASSERTED_BY_SOURCE",

                from_node=
                    claim_node,

                to_node=
                    source_node,

                relation_source_id=
                    claim_id
                    + ":source:"
                    + subject_id,

                payload={
                    "claim_id":
                        claim_id,

                    "source_subject_id":
                        subject_id,

                    "authority_reference_id":
                        authority_id,
                },

                provenance=
                    provenance,
            )
        )

        register_edge(
            make_edge(
                edge_type=
                    "SOURCE_HAS_AUTHORITY",

                from_node=
                    source_node,

                to_node=
                    authority_node,

                relation_source_id=
                    subject_id
                    + ":authority:"
                    + authority_id,

                payload={
                    "source_subject_id":
                        subject_id,

                    "final_authority_id":
                        authority_id,

                    "authority_score":
                        authority_reference.get(
                            "authority_score"
                        ),

                    "authority_class":
                        authority_reference.get(
                            "authority_class"
                        ),

                    "confidence":
                        authority_reference.get(
                            "confidence"
                        ),

                    "guard_outcome":
                        authority_reference.get(
                            "guard_outcome"
                        ),

                    "final_authority_disposition":
                        authority_reference.get(
                            "final_authority_disposition"
                        ),
                },

                provenance=
                    provenance,
            )
        )

        evidence_trace = record.get(
            "evidence_trace"
        )

        if not isinstance(
            evidence_trace,
            list,
        ):
            raise DynamicSemanticGraphError(
                "Authority integration requires evidence_trace list."
            )

        for evidence in evidence_trace:

            if not isinstance(
                evidence,
                dict,
            ):
                raise DynamicSemanticGraphError(
                    "Evidence trace item must be a dictionary."
                )

            evidence_source_id = evidence.get(
                "source_subject_id"
            )

            if evidence_source_id is None:
                continue

            if (
                not isinstance(
                    evidence_source_id,
                    str,
                )
                or not evidence_source_id.strip()
            ):
                raise DynamicSemanticGraphError(
                    "Evidence source_subject_id must be non-empty."
                )

            if evidence_source_id == subject_id:

                evidence_id = evidence.get(
                    "evidence_id"
                )

                if (
                    isinstance(
                        evidence_id,
                        str,
                    )
                    and evidence_id.strip()
                ):

                    require_node(
                        "EVIDENCE_NODE",
                        evidence_id,
                    )

        integrated_source_ids.add(
            subject_id
        )

        integrated_authority_ids.add(
            authority_id
        )

    integrated_nodes.sort(
        key=lambda item: (
            item[
                "node_type"
            ],
            item[
                "source_object_id"
            ],
            item[
                "node_id"
            ],
        )
    )

    integrated_edges.sort(
        key=lambda item: (
            item[
                "edge_type"
            ],
            item[
                "from_node_id"
            ],
            item[
                "to_node_id"
            ],
            item[
                "edge_id"
            ],
        )
    )

    node_ids = [
        node[
            "node_id"
        ]
        for node in integrated_nodes
    ]

    edge_ids = [
        edge[
            "edge_id"
        ]
        for edge in integrated_edges
    ]

    if len(node_ids) != len(
        set(node_ids)
    ):
        raise DynamicSemanticGraphError(
            "Duplicate graph node IDs after Authority integration."
        )

    if len(edge_ids) != len(
        set(edge_ids)
    ):
        raise DynamicSemanticGraphError(
            "Duplicate graph edge IDs after Authority integration."
        )

    node_id_set = set(
        node_ids
    )

    for edge in integrated_edges:

        if (
            edge.get(
                "from_node_id"
            )
            not in node_id_set
        ):
            raise DynamicSemanticGraphError(
                "Authority integration edge has missing from-node."
            )

        if (
            edge.get(
                "to_node_id"
            )
            not in node_id_set
        ):
            raise DynamicSemanticGraphError(
                "Authority integration edge has missing to-node."
            )

    previous_graph_version_id = (
        edge_result.get(
            "graph_version_id"
        )
    )

    previous_graph_version_digest = (
        edge_result.get(
            "graph_version_digest"
        )
    )

    if (
        not isinstance(
            previous_graph_version_id,
            str,
        )
        or not previous_graph_version_id.startswith(
            "graphversion:v1:"
        )
    ):
        raise DynamicSemanticGraphError(
            "Invalid previous graph version ID."
        )

    if (
        not isinstance(
            previous_graph_version_digest,
            str,
        )
        or len(
            previous_graph_version_digest
        )
        != 64
    ):
        raise DynamicSemanticGraphError(
            "Invalid previous graph version digest."
        )

    graph_version_material = {
        "previous_graph_version_id":
            previous_graph_version_id,

        "previous_graph_version_digest":
            previous_graph_version_digest,

        "node_ids":
            node_ids,

        "node_payload_digests": [
            node[
                "payload_digest"
            ]
            for node in integrated_nodes
        ],

        "edge_ids":
            edge_ids,

        "edge_payload_digests": [
            edge[
                "payload_digest"
            ]
            for edge in integrated_edges
        ],
    }

    graph_version_digest = digest(
        graph_version_material
    )

    graph_version_id = (
        "graphversion:v1:"
        + graph_version_digest
    )

    node_type_counts = {}

    for node in integrated_nodes:

        node_type = node[
            "node_type"
        ]

        node_type_counts[
            node_type
        ] = (
            node_type_counts.get(
                node_type,
                0,
            )
            + 1
        )

    edge_type_counts = {}

    for edge in integrated_edges:

        edge_type = edge[
            "edge_type"
        ]

        edge_type_counts[
            edge_type
        ] = (
            edge_type_counts.get(
                edge_type,
                0,
            )
            + 1
        )

    return {
        "schema":
            "dynamic_semantic_graph_authority_integration_result_v1",

        "dynamic_semantic_graph_version":
            DYNAMIC_SEMANTIC_GRAPH_VERSION,

        "phase":
            DYNAMIC_SEMANTIC_GRAPH_PHASE,

        "patch":
            "4.6.26G",

        "status":
            "CLAIM_EVIDENCE_AUTHORITY_GRAPH_INTEGRATED",

        "previous_graph_version_id":
            previous_graph_version_id,

        "previous_graph_version_digest":
            previous_graph_version_digest,

        "graph_version_id":
            graph_version_id,

        "graph_version_digest":
            graph_version_digest,

        "node_count":
            len(
                integrated_nodes
            ),

        "edge_count":
            len(
                integrated_edges
            ),

        "node_type_counts":
            node_type_counts,

        "edge_type_counts":
            edge_type_counts,

        "integrated_source_count":
            len(
                integrated_source_ids
            ),

        "integrated_authority_count":
            len(
                integrated_authority_ids
            ),

        "canonical_graph_nodes":
            integrated_nodes,

        "canonical_graph_edges":
            integrated_edges,

        "validated_graph_intake_records":
            copy.deepcopy(
                validated_records
            ),

        "scope_mutation_contract":
            copy.deepcopy(
                contract
            ),

        "architecture":
            copy.deepcopy(
                architecture
            ),

        "final_claim_integrity_package":
            copy.deepcopy(
                final_claim_integrity_package
            ),

        "preservation_contract":
            copy.deepcopy(
                preservation_contract
            ),

        "processing_boundaries": {
            "claim_evidence_authority_integration_performed":
                True,

            "source_node_integration_performed":
                True,

            "claim_source_edges_created":
                True,

            "source_authority_edges_created":
                True,

            "graph_node_creation_performed":
                True,

            "graph_edge_creation_performed":
                True,

            "graph_mutation_performed":
                True,

            "claim_conflict_edges_created":
                False,

            "conflict_projection_performed":
                False,

            "graph_merge_performed":
                False,

            "support_reassessment_performed":
                False,

            "conflict_redetection_performed":
                False,

            "conflict_reclassification_performed":
                False,

            "integrity_redecision_performed":
                False,

            "guard_redisposition_performed":
                False,

            "authority_rescoring_performed":
                False,

            "authority_reclassification_performed":
                False,

            "source_metadata_fetch_performed":
                False,

            "semantic_memory_written":
                False,

            "learning_performed":
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

            "unsupported_node_invention_performed":
                False,

            "unsupported_edge_invention_performed":
                False,
        },

        "policy":
            "CERTIFIED_CLAIM_EVIDENCE_AUTHORITY_GRAPH_INTEGRATION",

        "next":
            "conflict_and_integrity_graph_projection",
    }

def project_conflict_and_integrity_graph_v1(
    authority_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.26H ? Conflict & Integrity Graph Projection.

    Projects certified claim-conflict and integrity state into the
    Dynamic Semantic Graph.

    This stage represents previously certified conflict only.

    It does not:
    - detect new conflicts,
    - reclassify existing conflicts,
    - decide claim integrity,
    - override guard disposition,
    - alter Authority,
    - invent claims or relationships,
    - write Semantic Memory,
    - execute learning/reasoning,
    - create/select targets,
    - make linking decisions.
    """

    import hashlib
    import json

    if not isinstance(
        authority_result,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "authority_result must be a dictionary."
        )

    expected_lifecycle = {
        "schema":
            "dynamic_semantic_graph_authority_integration_result_v1",

        "dynamic_semantic_graph_version":
            DYNAMIC_SEMANTIC_GRAPH_VERSION,

        "phase":
            DYNAMIC_SEMANTIC_GRAPH_PHASE,

        "patch":
            "4.6.26G",

        "status":
            "CLAIM_EVIDENCE_AUTHORITY_GRAPH_INTEGRATED",

        "policy":
            "CERTIFIED_CLAIM_EVIDENCE_AUTHORITY_GRAPH_INTEGRATION",

        "next":
            "conflict_and_integrity_graph_projection",
    }

    for key, expected in expected_lifecycle.items():

        if authority_result.get(key) != expected:
            raise DynamicSemanticGraphError(
                "Invalid 4.6.26G lifecycle field: "
                f"{key}"
            )

    nodes = authority_result.get(
        "canonical_graph_nodes"
    )

    edges = authority_result.get(
        "canonical_graph_edges"
    )

    validated_records = authority_result.get(
        "validated_graph_intake_records"
    )

    contract = authority_result.get(
        "scope_mutation_contract"
    )

    architecture = authority_result.get(
        "architecture"
    )

    preservation_contract = authority_result.get(
        "preservation_contract"
    )

    final_claim_integrity_package = (
        authority_result.get(
            "final_claim_integrity_package"
        )
    )

    if not isinstance(nodes, list):
        raise DynamicSemanticGraphError(
            "canonical_graph_nodes must be a list."
        )

    if not isinstance(edges, list):
        raise DynamicSemanticGraphError(
            "canonical_graph_edges must be a list."
        )

    if (
        authority_result.get("node_count")
        != len(nodes)
    ):
        raise DynamicSemanticGraphError(
            "Graph node count mismatch."
        )

    if (
        authority_result.get("edge_count")
        != len(edges)
    ):
        raise DynamicSemanticGraphError(
            "Graph edge count mismatch."
        )

    if not isinstance(
        validated_records,
        list,
    ):
        raise DynamicSemanticGraphError(
            "validated_graph_intake_records must be a list."
        )

    if not isinstance(contract, dict):
        raise DynamicSemanticGraphError(
            "scope_mutation_contract must be a dictionary."
        )

    if not isinstance(architecture, dict):
        raise DynamicSemanticGraphError(
            "architecture must be a dictionary."
        )

    if not isinstance(
        preservation_contract,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "preservation_contract must be a dictionary."
        )

    if not isinstance(
        final_claim_integrity_package,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "final_claim_integrity_package must be a dictionary."
        )

    forbidden = contract.get(
        "forbidden_mutations"
    )

    if not isinstance(forbidden, dict):
        raise DynamicSemanticGraphError(
            "forbidden_mutations must be a dictionary."
        )

    for flag in (
        "may_redetect_claim_conflict",
        "may_reclassify_claim_conflict",
        "may_redecide_claim_integrity",
        "may_override_guard_disposition",
        "may_rescore_authority",
        "may_reclassify_authority",
        "may_invent_unsupported_nodes",
        "may_invent_unsupported_edges",
        "may_write_semantic_memory",
        "may_execute_learning",
        "may_execute_reasoning",
        "may_create_active_targets",
        "may_select_final_external_target",
        "may_make_linking_decision",
        "may_create_editor_highlight",
    ):

        if forbidden.get(flag) is not False:
            raise DynamicSemanticGraphError(
                "Conflict projection prohibition drift: "
                f"{flag}"
            )

    allowed_node_types = set(
        architecture.get(
            "node_types",
            (),
        )
    )

    allowed_edge_types = set(
        architecture.get(
            "edge_types",
            (),
        )
    )

    if "CONFLICT_NODE" not in allowed_node_types:
        raise DynamicSemanticGraphError(
            "CONFLICT_NODE is not permitted."
        )

    required_edge_types = {
        "CLAIM_CONFLICTS_WITH_CLAIM",
        "CLAIM_AGREES_WITH_CLAIM",
        "CLAIM_QUALIFIES_CLAIM",
        "CLAIM_OVERLAPS_CLAIM",
        "CONFLICT_HAS_PROVENANCE",
    }

    if not required_edge_types.issubset(
        allowed_edge_types
    ):
        raise DynamicSemanticGraphError(
            "Required conflict projection edge types are missing."
        )

    def canonical_json(
        value: Any,
    ) -> str:

        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )

    def digest(
        value: Any,
    ) -> str:

        return hashlib.sha256(
            canonical_json(
                value
            ).encode(
                "utf-8"
            )
        ).hexdigest()

    projected_nodes = copy.deepcopy(
        nodes
    )

    projected_edges = copy.deepcopy(
        edges
    )

    node_by_key = {}
    node_by_id = {}

    for node in projected_nodes:

        if (
            not isinstance(node, dict)
            or node.get("schema")
            != "dynamic_semantic_graph_node_v1"
        ):
            raise DynamicSemanticGraphError(
                "Invalid canonical graph node."
            )

        node_id = node.get(
            "node_id"
        )

        key = (
            node.get(
                "node_type"
            ),
            node.get(
                "source_object_id"
            ),
        )

        if key in node_by_key:
            raise DynamicSemanticGraphError(
                "Duplicate graph node key."
            )

        if node_id in node_by_id:
            raise DynamicSemanticGraphError(
                "Duplicate graph node ID."
            )

        node_by_key[key] = node
        node_by_id[node_id] = node

    edge_by_id = {}

    for edge in projected_edges:

        if (
            not isinstance(edge, dict)
            or edge.get("schema")
            != "dynamic_semantic_graph_edge_v1"
        ):
            raise DynamicSemanticGraphError(
                "Invalid canonical graph edge."
            )

        edge_id = edge.get(
            "edge_id"
        )

        if edge_id in edge_by_id:
            raise DynamicSemanticGraphError(
                "Duplicate graph edge ID."
            )

        edge_by_id[
            edge_id
        ] = edge

    def require_node(
        node_type: str,
        source_object_id: str,
    ) -> dict[str, Any]:

        node = node_by_key.get(
            (
                node_type,
                source_object_id,
            )
        )

        if node is None:
            raise DynamicSemanticGraphError(
                "Required graph node is missing: "
                f"{node_type}:{source_object_id}"
            )

        return node

    def make_conflict_node(
        conflict: dict[str, Any],
        provenance: dict[str, Any],
    ) -> dict[str, Any]:

        observation_id = conflict.get(
            "observation_id"
        )

        if (
            not isinstance(observation_id, str)
            or not observation_id.strip()
        ):
            raise DynamicSemanticGraphError(
                "Certified conflict requires observation_id."
            )

        identity_material = {
            "node_type":
                "CONFLICT_NODE",

            "source_object_type":
                "CERTIFIED_CLAIM_CONFLICT",

            "source_object_id":
                observation_id,
        }

        node_hash = digest(
            identity_material
        )

        payload = {
            "observation_id":
                observation_id,

            "claim_a_id":
                conflict.get(
                    "claim_a_id"
                ),

            "claim_b_id":
                conflict.get(
                    "claim_b_id"
                ),

            "claim_relationship":
                conflict.get(
                    "claim_relationship"
                ),

            "conflict_class":
                conflict.get(
                    "conflict_class"
                ),

            "materiality":
                copy.deepcopy(
                    conflict.get(
                        "materiality"
                    )
                ),

            "basis":
                copy.deepcopy(
                    conflict.get(
                        "basis"
                    )
                ),
        }

        return {
            "schema":
                "dynamic_semantic_graph_node_v1",

            "node_id":
                "graphnode:v1:"
                + node_hash,

            "node_type":
                "CONFLICT_NODE",

            "source_object_type":
                "CERTIFIED_CLAIM_CONFLICT",

            "source_object_id":
                observation_id,

            "lifecycle_state":
                "ACTIVE",

            "payload":
                payload,

            "payload_digest":
                digest(
                    payload
                ),

            "provenance":
                copy.deepcopy(
                    provenance
                ),

            "idempotency_key":
                "graphnode-idempotency:v1:"
                + node_hash,

            "canonical_identity_deterministic":
                True,

            "certified_input_backed":
                True,

            "unsupported_invention_performed":
                False,
        }

    def register_node(
        node: dict[str, Any],
    ) -> dict[str, Any]:

        key = (
            node[
                "node_type"
            ],
            node[
                "source_object_id"
            ],
        )

        existing = node_by_key.get(
            key
        )

        if existing is not None:

            if existing != node:
                raise DynamicSemanticGraphError(
                    "Conflict node identity collision."
                )

            return existing

        node_id = node[
            "node_id"
        ]

        if node_id in node_by_id:
            raise DynamicSemanticGraphError(
                "Conflict node ID collision."
            )

        projected_nodes.append(
            node
        )

        node_by_key[
            key
        ] = node

        node_by_id[
            node_id
        ] = node

        return node

    def make_edge(
        *,
        edge_type: str,
        from_node: dict[str, Any],
        to_node: dict[str, Any],
        relation_source_id: str,
        payload: dict[str, Any],
        provenance: dict[str, Any],
    ) -> dict[str, Any]:

        if edge_type not in allowed_edge_types:
            raise DynamicSemanticGraphError(
                "Unsupported conflict projection edge type."
            )

        identity_material = {
            "edge_type":
                edge_type,

            "from_node_id":
                from_node[
                    "node_id"
                ],

            "to_node_id":
                to_node[
                    "node_id"
                ],

            "relation_source_id":
                relation_source_id,
        }

        edge_hash = digest(
            identity_material
        )

        return {
            "schema":
                "dynamic_semantic_graph_edge_v1",

            "edge_id":
                "graphedge:v1:"
                + edge_hash,

            "edge_type":
                edge_type,

            "from_node_id":
                from_node[
                    "node_id"
                ],

            "to_node_id":
                to_node[
                    "node_id"
                ],

            "from_node_type":
                from_node[
                    "node_type"
                ],

            "to_node_type":
                to_node[
                    "node_type"
                ],

            "relation_source_id":
                relation_source_id,

            "lifecycle_state":
                "ACTIVE",

            "payload":
                copy.deepcopy(
                    payload
                ),

            "payload_digest":
                digest(
                    payload
                ),

            "provenance":
                copy.deepcopy(
                    provenance
                ),

            "idempotency_key":
                "graphedge-idempotency:v1:"
                + edge_hash,

            "canonical_identity_deterministic":
                True,

            "certified_relationship_backed":
                True,

            "unsupported_invention_performed":
                False,
        }

    def register_edge(
        edge: dict[str, Any],
    ) -> None:

        edge_id = edge[
            "edge_id"
        ]

        existing = edge_by_id.get(
            edge_id
        )

        if existing is not None:

            if existing != edge:
                raise DynamicSemanticGraphError(
                    "Conflict edge identity collision."
                )

            return

        projected_edges.append(
            edge
        )

        edge_by_id[
            edge_id
        ] = edge

    relation_to_edge = {
        "AGREES":
            "CLAIM_AGREES_WITH_CLAIM",

        "COMPATIBLE":
            "CLAIM_AGREES_WITH_CLAIM",

        "PARTIALLY_OVERLAPS":
            "CLAIM_OVERLAPS_CLAIM",

        "QUALIFIES":
            "CLAIM_QUALIFIES_CLAIM",

        "DISAGREES":
            "CLAIM_CONFLICTS_WITH_CLAIM",

        "CONTRADICTS":
            "CLAIM_CONFLICTS_WITH_CLAIM",
    }

    conflict_by_observation = {}

    for record in validated_records:

        if (
            not isinstance(record, dict)
            or record.get("schema")
            != "dynamic_graph_validated_intake_record_v1"
        ):
            raise DynamicSemanticGraphError(
                "Invalid validated graph intake record."
            )

        claim_id = record.get(
            "claim_id"
        )

        provenance_trace_id = record.get(
            "provenance_trace_id"
        )

        require_node(
            "CLAIM_NODE",
            claim_id,
        )

        require_node(
            "INTEGRITY_NODE",
            record.get(
                "final_claim_integrity_id"
            ),
        )

        conflict_trace = record.get(
            "conflict_trace"
        )

        if not isinstance(
            conflict_trace,
            list,
        ):
            raise DynamicSemanticGraphError(
                "conflict_trace must be a list."
            )

        for conflict in conflict_trace:

            if not isinstance(
                conflict,
                dict,
            ):
                raise DynamicSemanticGraphError(
                    "Conflict trace item must be a dictionary."
                )

            if (
                conflict.get("schema")
                != "claim_integrity_conflict_trace_record_v1"
            ):
                raise DynamicSemanticGraphError(
                    "Invalid conflict trace schema."
                )

            observation_id = conflict.get(
                "observation_id"
            )

            claim_a_id = conflict.get(
                "claim_a_id"
            )

            claim_b_id = conflict.get(
                "claim_b_id"
            )

            claim_relationship = conflict.get(
                "claim_relationship"
            )

            conflict_class = conflict.get(
                "conflict_class"
            )

            if (
                not isinstance(observation_id, str)
                or not observation_id.strip()
            ):
                raise DynamicSemanticGraphError(
                    "Conflict observation_id is required."
                )

            if (
                not isinstance(claim_a_id, str)
                or not claim_a_id.strip()
                or not isinstance(claim_b_id, str)
                or not claim_b_id.strip()
            ):
                raise DynamicSemanticGraphError(
                    "Conflict requires both claim IDs."
                )

            if claim_a_id == claim_b_id:
                raise DynamicSemanticGraphError(
                    "Conflict cannot compare a claim with itself."
                )

            claim_a_node = require_node(
                "CLAIM_NODE",
                claim_a_id,
            )

            claim_b_node = require_node(
                "CLAIM_NODE",
                claim_b_id,
            )

            previous_conflict = (
                conflict_by_observation.get(
                    observation_id
                )
            )

            canonical_conflict = {
                "schema":
                    "claim_integrity_conflict_trace_record_v1",

                "observation_id":
                    observation_id,

                "claim_a_id":
                    claim_a_id,

                "claim_b_id":
                    claim_b_id,

                "claim_relationship":
                    claim_relationship,

                "conflict_class":
                    conflict_class,

                "materiality":
                    copy.deepcopy(
                        conflict.get(
                            "materiality"
                        )
                    ),

                "basis":
                    copy.deepcopy(
                        conflict.get(
                            "basis"
                        )
                    ),
            }

            if previous_conflict is not None:

                if (
                    previous_conflict
                    != canonical_conflict
                ):
                    raise DynamicSemanticGraphError(
                        "Duplicate observation_id carries conflicting data."
                    )

                continue

            conflict_by_observation[
                observation_id
            ] = canonical_conflict

            provenance = {
                "observation_id":
                    observation_id,

                "claim_a_id":
                    claim_a_id,

                "claim_b_id":
                    claim_b_id,

                "provenance_trace_id":
                    provenance_trace_id,

                "conflict_class":
                    conflict_class,
            }

            conflict_node = register_node(
                make_conflict_node(
                    canonical_conflict,
                    provenance,
                )
            )

            if claim_relationship in relation_to_edge:

                relation_edge_type = (
                    relation_to_edge[
                        claim_relationship
                    ]
                )

                register_edge(
                    make_edge(
                        edge_type=
                            relation_edge_type,

                        from_node=
                            claim_a_node,

                        to_node=
                            claim_b_node,

                        relation_source_id=
                            observation_id,

                        payload={
                            "observation_id":
                                observation_id,

                            "claim_relationship":
                                claim_relationship,

                            "conflict_class":
                                conflict_class,

                            "materiality":
                                copy.deepcopy(
                                    conflict.get(
                                        "materiality"
                                    )
                                ),

                            "basis":
                                copy.deepcopy(
                                    conflict.get(
                                        "basis"
                                    )
                                ),
                        },

                        provenance=
                            provenance,
                    )
                )

            provenance_node = require_node(
                "PROVENANCE_NODE",
                provenance_trace_id,
            )

            register_edge(
                make_edge(
                    edge_type=
                        "CONFLICT_HAS_PROVENANCE",

                    from_node=
                        conflict_node,

                    to_node=
                        provenance_node,

                    relation_source_id=
                        observation_id
                        + ":provenance",

                    payload={
                        "observation_id":
                            observation_id,

                        "claim_a_id":
                            claim_a_id,

                        "claim_b_id":
                            claim_b_id,

                        "conflict_class":
                            conflict_class,
                    },

                    provenance=
                        provenance,
                )
            )

    projected_nodes.sort(
        key=lambda item: (
            item[
                "node_type"
            ],
            item[
                "source_object_id"
            ],
            item[
                "node_id"
            ],
        )
    )

    projected_edges.sort(
        key=lambda item: (
            item[
                "edge_type"
            ],
            item[
                "from_node_id"
            ],
            item[
                "to_node_id"
            ],
            item[
                "edge_id"
            ],
        )
    )

    node_ids = [
        node[
            "node_id"
        ]
        for node in projected_nodes
    ]

    edge_ids = [
        edge[
            "edge_id"
        ]
        for edge in projected_edges
    ]

    if len(node_ids) != len(
        set(node_ids)
    ):
        raise DynamicSemanticGraphError(
            "Duplicate node IDs after conflict projection."
        )

    if len(edge_ids) != len(
        set(edge_ids)
    ):
        raise DynamicSemanticGraphError(
            "Duplicate edge IDs after conflict projection."
        )

    node_id_set = set(
        node_ids
    )

    for edge in projected_edges:

        if (
            edge[
                "from_node_id"
            ]
            not in node_id_set
        ):
            raise DynamicSemanticGraphError(
                "Conflict edge has missing from-node."
            )

        if (
            edge[
                "to_node_id"
            ]
            not in node_id_set
        ):
            raise DynamicSemanticGraphError(
                "Conflict edge has missing to-node."
            )

    previous_graph_version_id = (
        authority_result.get(
            "graph_version_id"
        )
    )

    previous_graph_version_digest = (
        authority_result.get(
            "graph_version_digest"
        )
    )

    if (
        not isinstance(
            previous_graph_version_id,
            str,
        )
        or not previous_graph_version_id.startswith(
            "graphversion:v1:"
        )
    ):
        raise DynamicSemanticGraphError(
            "Invalid previous graph version ID."
        )

    if (
        not isinstance(
            previous_graph_version_digest,
            str,
        )
        or len(
            previous_graph_version_digest
        )
        != 64
    ):
        raise DynamicSemanticGraphError(
            "Invalid previous graph version digest."
        )

    graph_version_material = {
        "previous_graph_version_id":
            previous_graph_version_id,

        "previous_graph_version_digest":
            previous_graph_version_digest,

        "node_ids":
            node_ids,

        "node_payload_digests": [
            node[
                "payload_digest"
            ]
            for node in projected_nodes
        ],

        "edge_ids":
            edge_ids,

        "edge_payload_digests": [
            edge[
                "payload_digest"
            ]
            for edge in projected_edges
        ],
    }

    graph_version_digest = digest(
        graph_version_material
    )

    graph_version_id = (
        "graphversion:v1:"
        + graph_version_digest
    )

    node_type_counts = {}

    for node in projected_nodes:

        node_type = node[
            "node_type"
        ]

        node_type_counts[
            node_type
        ] = (
            node_type_counts.get(
                node_type,
                0,
            )
            + 1
        )

    edge_type_counts = {}

    for edge in projected_edges:

        edge_type = edge[
            "edge_type"
        ]

        edge_type_counts[
            edge_type
        ] = (
            edge_type_counts.get(
                edge_type,
                0,
            )
            + 1
        )

    return {
        "schema":
            "dynamic_semantic_graph_conflict_projection_result_v1",

        "dynamic_semantic_graph_version":
            DYNAMIC_SEMANTIC_GRAPH_VERSION,

        "phase":
            DYNAMIC_SEMANTIC_GRAPH_PHASE,

        "patch":
            "4.6.26H",

        "status":
            "CONFLICT_AND_INTEGRITY_GRAPH_PROJECTED",

        "previous_graph_version_id":
            previous_graph_version_id,

        "previous_graph_version_digest":
            previous_graph_version_digest,

        "graph_version_id":
            graph_version_id,

        "graph_version_digest":
            graph_version_digest,

        "node_count":
            len(
                projected_nodes
            ),

        "edge_count":
            len(
                projected_edges
            ),

        "conflict_node_count":
            len(
                conflict_by_observation
            ),

        "node_type_counts":
            node_type_counts,

        "edge_type_counts":
            edge_type_counts,

        "canonical_graph_nodes":
            projected_nodes,

        "canonical_graph_edges":
            projected_edges,

        "validated_graph_intake_records":
            copy.deepcopy(
                validated_records
            ),

        "scope_mutation_contract":
            copy.deepcopy(
                contract
            ),

        "architecture":
            copy.deepcopy(
                architecture
            ),

        "final_claim_integrity_package":
            copy.deepcopy(
                final_claim_integrity_package
            ),

        "preservation_contract":
            copy.deepcopy(
                preservation_contract
            ),

        "processing_boundaries": {
            "conflict_and_integrity_projection_performed":
                True,

            "conflict_nodes_created":
                True,

            "claim_relationship_edges_created":
                True,

            "conflict_provenance_edges_created":
                True,

            "existing_integrity_projection_preserved":
                True,

            "graph_node_creation_performed":
                True,

            "graph_edge_creation_performed":
                True,

            "graph_mutation_performed":
                True,

            "support_reassessment_performed":
                False,

            "conflict_redetection_performed":
                False,

            "conflict_reclassification_performed":
                False,

            "integrity_redecision_performed":
                False,

            "guard_redisposition_performed":
                False,

            "authority_rescoring_performed":
                False,

            "authority_reclassification_performed":
                False,

            "graph_merge_performed":
                False,

            "semantic_memory_written":
                False,

            "learning_performed":
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

            "unsupported_node_invention_performed":
                False,

            "unsupported_edge_invention_performed":
                False,
        },

        "policy":
            "CERTIFIED_CONFLICT_AND_INTEGRITY_GRAPH_PROJECTION",

        "next":
            "graph_consistency_and_referential_integrity",
    }

def validate_graph_consistency_and_referential_integrity_v1(
    projection_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.26I ? Graph Consistency & Referential Integrity.

    Certifies structural consistency of the Dynamic Semantic Graph.

    Validation only.

    No nodes, edges, semantic states, Authority states, claims,
    conflicts, targets, memory, reasoning, or linking decisions
    are created or changed.
    """

    if not isinstance(
        projection_result,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "projection_result must be a dictionary."
        )

    expected_lifecycle = {
        "schema":
            "dynamic_semantic_graph_conflict_projection_result_v1",

        "dynamic_semantic_graph_version":
            DYNAMIC_SEMANTIC_GRAPH_VERSION,

        "phase":
            DYNAMIC_SEMANTIC_GRAPH_PHASE,

        "patch":
            "4.6.26H",

        "status":
            "CONFLICT_AND_INTEGRITY_GRAPH_PROJECTED",

        "policy":
            "CERTIFIED_CONFLICT_AND_INTEGRITY_GRAPH_PROJECTION",

        "next":
            "graph_consistency_and_referential_integrity",
    }

    for key, expected in expected_lifecycle.items():

        if projection_result.get(key) != expected:
            raise DynamicSemanticGraphError(
                "Invalid 4.6.26H lifecycle field: "
                f"{key}"
            )

    nodes = projection_result.get(
        "canonical_graph_nodes"
    )

    edges = projection_result.get(
        "canonical_graph_edges"
    )

    validated_records = projection_result.get(
        "validated_graph_intake_records"
    )

    contract = projection_result.get(
        "scope_mutation_contract"
    )

    architecture = projection_result.get(
        "architecture"
    )

    preservation_contract = projection_result.get(
        "preservation_contract"
    )

    final_claim_integrity_package = (
        projection_result.get(
            "final_claim_integrity_package"
        )
    )

    if not isinstance(nodes, list):
        raise DynamicSemanticGraphError(
            "canonical_graph_nodes must be a list."
        )

    if not isinstance(edges, list):
        raise DynamicSemanticGraphError(
            "canonical_graph_edges must be a list."
        )

    if (
        projection_result.get("node_count")
        != len(nodes)
    ):
        raise DynamicSemanticGraphError(
            "Graph node count mismatch."
        )

    if (
        projection_result.get("edge_count")
        != len(edges)
    ):
        raise DynamicSemanticGraphError(
            "Graph edge count mismatch."
        )

    if not isinstance(
        validated_records,
        list,
    ):
        raise DynamicSemanticGraphError(
            "validated_graph_intake_records must be a list."
        )

    if not isinstance(contract, dict):
        raise DynamicSemanticGraphError(
            "scope_mutation_contract must be a dictionary."
        )

    if not isinstance(architecture, dict):
        raise DynamicSemanticGraphError(
            "architecture must be a dictionary."
        )

    if not isinstance(
        preservation_contract,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "preservation_contract must be a dictionary."
        )

    if not isinstance(
        final_claim_integrity_package,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "final_claim_integrity_package must be a dictionary."
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

        if preservation_contract.get(flag) is not True:
            raise DynamicSemanticGraphError(
                "Graph preservation contract drift: "
                f"{flag}"
            )

    allowed_node_types = set(
        architecture.get(
            "node_types",
            (),
        )
    )

    allowed_edge_types = set(
        architecture.get(
            "edge_types",
            (),
        )
    )

    node_by_id = {}
    node_by_key = {}

    for node in nodes:

        if (
            not isinstance(node, dict)
            or node.get("schema")
            != "dynamic_semantic_graph_node_v1"
        ):
            raise DynamicSemanticGraphError(
                "Invalid canonical graph node."
            )

        node_id = node.get(
            "node_id"
        )

        node_type = node.get(
            "node_type"
        )

        source_object_id = node.get(
            "source_object_id"
        )

        if (
            not isinstance(node_id, str)
            or not node_id.startswith(
                "graphnode:v1:"
            )
        ):
            raise DynamicSemanticGraphError(
                "Invalid canonical graph node ID."
            )

        if node_type not in allowed_node_types:
            raise DynamicSemanticGraphError(
                "Graph node type is not allowed by architecture."
            )

        if (
            not isinstance(source_object_id, str)
            or not source_object_id.strip()
        ):
            raise DynamicSemanticGraphError(
                "Graph node requires source_object_id."
            )

        if node_id in node_by_id:
            raise DynamicSemanticGraphError(
                "Duplicate canonical graph node ID."
            )

        key = (
            node_type,
            source_object_id,
        )

        if key in node_by_key:
            raise DynamicSemanticGraphError(
                "Duplicate canonical graph node identity."
            )

        if node.get(
            "canonical_identity_deterministic"
        ) is not True:
            raise DynamicSemanticGraphError(
                "Graph node deterministic identity contract violated."
            )

        if node.get(
            "certified_input_backed"
        ) is not True:
            raise DynamicSemanticGraphError(
                "Graph node is not certified-input-backed."
            )

        if node.get(
            "unsupported_invention_performed"
        ) is not False:
            raise DynamicSemanticGraphError(
                "Unsupported graph node invention detected."
            )

        node_by_id[
            node_id
        ] = node

        node_by_key[
            key
        ] = node

    endpoint_contracts = {
        "CLAIM_SUPPORTED_BY_EVIDENCE":
            (
                "CLAIM_NODE",
                "EVIDENCE_NODE",
            ),

        "CLAIM_PARTIALLY_SUPPORTED_BY_EVIDENCE":
            (
                "CLAIM_NODE",
                "EVIDENCE_NODE",
            ),

        "CLAIM_CHALLENGED_BY_EVIDENCE":
            (
                "CLAIM_NODE",
                "EVIDENCE_NODE",
            ),

        "CLAIM_CONTRADICTED_BY_EVIDENCE":
            (
                "CLAIM_NODE",
                "EVIDENCE_NODE",
            ),

        "CLAIM_HAS_NEUTRAL_EVIDENCE":
            (
                "CLAIM_NODE",
                "EVIDENCE_NODE",
            ),

        "CLAIM_HAS_INSUFFICIENT_EVIDENCE":
            (
                "CLAIM_NODE",
                "EVIDENCE_NODE",
            ),

        "CLAIM_HAS_UNRESOLVED_EVIDENCE":
            (
                "CLAIM_NODE",
                "EVIDENCE_NODE",
            ),

        "CLAIM_ASSERTED_BY_SOURCE":
            (
                "CLAIM_NODE",
                "SOURCE_NODE",
            ),

        "SOURCE_HAS_AUTHORITY":
            (
                "SOURCE_NODE",
                "AUTHORITY_NODE",
            ),

        "CLAIM_HAS_INTEGRITY_STATE":
            (
                "CLAIM_NODE",
                "INTEGRITY_NODE",
            ),

        "CLAIM_HAS_GUARD_DISPOSITION":
            (
                "CLAIM_NODE",
                "GUARD_NODE",
            ),

        "CLAIM_CONFLICTS_WITH_CLAIM":
            (
                "CLAIM_NODE",
                "CLAIM_NODE",
            ),

        "CLAIM_AGREES_WITH_CLAIM":
            (
                "CLAIM_NODE",
                "CLAIM_NODE",
            ),

        "CLAIM_QUALIFIES_CLAIM":
            (
                "CLAIM_NODE",
                "CLAIM_NODE",
            ),

        "CLAIM_OVERLAPS_CLAIM":
            (
                "CLAIM_NODE",
                "CLAIM_NODE",
            ),

        "EVIDENCE_HAS_PROVENANCE":
            (
                "EVIDENCE_NODE",
                "PROVENANCE_NODE",
            ),

        "CONFLICT_HAS_PROVENANCE":
            (
                "CONFLICT_NODE",
                "PROVENANCE_NODE",
            ),

        "INTEGRITY_HAS_PROVENANCE":
            (
                "INTEGRITY_NODE",
                "PROVENANCE_NODE",
            ),
    }

    edge_by_id = {}

    incoming_count = {
        node_id:
            0
        for node_id
        in node_by_id
    }

    outgoing_count = {
        node_id:
            0
        for node_id
        in node_by_id
    }

    for edge in edges:

        if (
            not isinstance(edge, dict)
            or edge.get("schema")
            != "dynamic_semantic_graph_edge_v1"
        ):
            raise DynamicSemanticGraphError(
                "Invalid canonical graph edge."
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

        if (
            not isinstance(edge_id, str)
            or not edge_id.startswith(
                "graphedge:v1:"
            )
        ):
            raise DynamicSemanticGraphError(
                "Invalid canonical graph edge ID."
            )

        if edge_id in edge_by_id:
            raise DynamicSemanticGraphError(
                "Duplicate canonical graph edge ID."
            )

        if edge_type not in allowed_edge_types:
            raise DynamicSemanticGraphError(
                "Graph edge type is not allowed by architecture."
            )

        if from_node_id not in node_by_id:
            raise DynamicSemanticGraphError(
                "Graph edge references missing from-node."
            )

        if to_node_id not in node_by_id:
            raise DynamicSemanticGraphError(
                "Graph edge references missing to-node."
            )

        from_node = node_by_id[
            from_node_id
        ]

        to_node = node_by_id[
            to_node_id
        ]

        if (
            edge.get("from_node_type")
            != from_node.get("node_type")
        ):
            raise DynamicSemanticGraphError(
                "Graph edge from-node type drift."
            )

        if (
            edge.get("to_node_type")
            != to_node.get("node_type")
        ):
            raise DynamicSemanticGraphError(
                "Graph edge to-node type drift."
            )

        expected_endpoint_types = (
            endpoint_contracts.get(
                edge_type
            )
        )

        if expected_endpoint_types is not None:

            expected_from, expected_to = (
                expected_endpoint_types
            )

            if (
                from_node.get("node_type")
                != expected_from
                or to_node.get("node_type")
                != expected_to
            ):
                raise DynamicSemanticGraphError(
                    "Graph edge endpoint contract violated: "
                    f"{edge_type}"
                )

        if edge.get(
            "canonical_identity_deterministic"
        ) is not True:
            raise DynamicSemanticGraphError(
                "Graph edge deterministic identity contract violated."
            )

        if edge.get(
            "certified_relationship_backed"
        ) is not True:
            raise DynamicSemanticGraphError(
                "Graph edge is not certified-relationship-backed."
            )

        if edge.get(
            "unsupported_invention_performed"
        ) is not False:
            raise DynamicSemanticGraphError(
                "Unsupported graph edge invention detected."
            )

        edge_by_id[
            edge_id
        ] = edge

        outgoing_count[
            from_node_id
        ] += 1

        incoming_count[
            to_node_id
        ] += 1

    claim_ids = {
        node[
            "source_object_id"
        ]
        for node in nodes
        if node[
            "node_type"
        ]
        == "CLAIM_NODE"
    }

    for record in validated_records:

        if (
            not isinstance(record, dict)
            or record.get("schema")
            != "dynamic_graph_validated_intake_record_v1"
        ):
            raise DynamicSemanticGraphError(
                "Invalid validated graph intake record."
            )

        claim_id = record.get(
            "claim_id"
        )

        if claim_id not in claim_ids:
            raise DynamicSemanticGraphError(
                "Validated claim is missing CLAIM_NODE."
            )

        final_integrity_id = record.get(
            "final_claim_integrity_id"
        )

        provenance_trace_id = record.get(
            "provenance_trace_id"
        )

        integrity_node = node_by_key.get(
            (
                "INTEGRITY_NODE",
                final_integrity_id,
            )
        )

        guard_node = node_by_key.get(
            (
                "GUARD_NODE",
                str(final_integrity_id)
                + ":guard",
            )
        )

        provenance_node = node_by_key.get(
            (
                "PROVENANCE_NODE",
                provenance_trace_id,
            )
        )

        if integrity_node is None:
            raise DynamicSemanticGraphError(
                "Validated claim is missing INTEGRITY_NODE."
            )

        if guard_node is None:
            raise DynamicSemanticGraphError(
                "Validated claim is missing GUARD_NODE."
            )

        if provenance_node is None:
            raise DynamicSemanticGraphError(
                "Validated claim is missing PROVENANCE_NODE."
            )

    for node in nodes:

        node_type = node[
            "node_type"
        ]

        node_id = node[
            "node_id"
        ]

        if node_type == "CONFLICT_NODE":

            if outgoing_count[
                node_id
            ] < 1:
                raise DynamicSemanticGraphError(
                    "Orphaned CONFLICT_NODE detected."
                )

            has_conflict_provenance = any(
                edge[
                    "edge_type"
                ]
                == "CONFLICT_HAS_PROVENANCE"
                and edge[
                    "from_node_id"
                ]
                == node_id
                for edge in edges
            )

            if not has_conflict_provenance:
                raise DynamicSemanticGraphError(
                    "Conflict node lacks provenance edge."
                )

        if node_type == "SOURCE_NODE":

            has_authority_edge = any(
                edge[
                    "edge_type"
                ]
                == "SOURCE_HAS_AUTHORITY"
                and edge[
                    "from_node_id"
                ]
                == node_id
                for edge in edges
            )

            if not has_authority_edge:
                raise DynamicSemanticGraphError(
                    "Source node lacks Authority relationship."
                )

        if node_type == "AUTHORITY_NODE":

            has_source_edge = any(
                edge[
                    "edge_type"
                ]
                == "SOURCE_HAS_AUTHORITY"
                and edge[
                    "to_node_id"
                ]
                == node_id
                for edge in edges
            )

            if not has_source_edge:
                raise DynamicSemanticGraphError(
                    "Authority node is not connected to a source."
                )

    graph_version_id = projection_result.get(
        "graph_version_id"
    )

    graph_version_digest = projection_result.get(
        "graph_version_digest"
    )

    if (
        not isinstance(graph_version_id, str)
        or not graph_version_id.startswith(
            "graphversion:v1:"
        )
    ):
        raise DynamicSemanticGraphError(
            "Invalid graph version ID."
        )

    if (
        not isinstance(graph_version_digest, str)
        or len(graph_version_digest) != 64
    ):
        raise DynamicSemanticGraphError(
            "Invalid graph version digest."
        )

    consistency_report = {
        "schema":
            "dynamic_semantic_graph_consistency_report_v1",

        "graph_version_id":
            graph_version_id,

        "graph_version_digest":
            graph_version_digest,

        "node_count":
            len(nodes),

        "edge_count":
            len(edges),

        "unique_node_ids":
            True,

        "unique_node_identities":
            True,

        "unique_edge_ids":
            True,

        "all_edge_endpoints_exist":
            True,

        "all_edge_endpoint_types_match":
            True,

        "all_nodes_architecture_allowed":
            True,

        "all_edges_architecture_allowed":
            True,

        "all_validated_claims_represented":
            True,

        "all_claim_integrity_nodes_present":
            True,

        "all_claim_guard_nodes_present":
            True,

        "all_claim_provenance_nodes_present":
            True,

        "all_conflict_nodes_provenance_bound":
            True,

        "all_source_nodes_authority_bound":
            True,

        "all_authority_nodes_source_bound":
            True,

        "certified_input_backing_preserved":
            True,

        "certified_relationship_backing_preserved":
            True,

        "unsupported_invention_absent":
            True,

        "referential_integrity_valid":
            True,

        "graph_consistency_valid":
            True,
    }

    return {
        "schema":
            "dynamic_semantic_graph_consistency_validation_result_v1",

        "dynamic_semantic_graph_version":
            DYNAMIC_SEMANTIC_GRAPH_VERSION,

        "phase":
            DYNAMIC_SEMANTIC_GRAPH_PHASE,

        "patch":
            "4.6.26I",

        "status":
            "GRAPH_CONSISTENCY_AND_REFERENTIAL_INTEGRITY_VALIDATED",

        "graph_version_id":
            graph_version_id,

        "graph_version_digest":
            graph_version_digest,

        "node_count":
            len(nodes),

        "edge_count":
            len(edges),

        "canonical_graph_nodes":
            copy.deepcopy(
                nodes
            ),

        "canonical_graph_edges":
            copy.deepcopy(
                edges
            ),

        "consistency_report":
            consistency_report,

        "validated_graph_intake_records":
            copy.deepcopy(
                validated_records
            ),

        "scope_mutation_contract":
            copy.deepcopy(
                contract
            ),

        "architecture":
            copy.deepcopy(
                architecture
            ),

        "final_claim_integrity_package":
            copy.deepcopy(
                final_claim_integrity_package
            ),

        "preservation_contract":
            copy.deepcopy(
                preservation_contract
            ),

        "processing_boundaries": {
            "graph_consistency_validation_performed":
                True,

            "referential_integrity_validation_performed":
                True,

            "graph_node_creation_performed":
                False,

            "graph_edge_creation_performed":
                False,

            "graph_mutation_performed":
                False,

            "graph_merge_performed":
                False,

            "support_reassessment_performed":
                False,

            "conflict_redetection_performed":
                False,

            "conflict_reclassification_performed":
                False,

            "integrity_redecision_performed":
                False,

            "guard_redisposition_performed":
                False,

            "authority_rescoring_performed":
                False,

            "authority_reclassification_performed":
                False,

            "semantic_memory_written":
                False,

            "learning_performed":
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

            "unsupported_node_invention_performed":
                False,

            "unsupported_edge_invention_performed":
                False,
        },

        "policy":
            "CERTIFIED_DYNAMIC_GRAPH_CONSISTENCY_AND_REFERENTIAL_INTEGRITY",

        "next":
            "dynamic_graph_update_and_merge_engine",
    }

def update_and_merge_dynamic_semantic_graph_v1(
    consistency_result: dict[str, Any],
    previous_graph_snapshot: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    4.6.26J ? Dynamic Graph Update / Merge Engine.

    Deterministically merges a newly certified graph with an optional
    previous graph snapshot.

    Rules:
    - stable canonical IDs are preserved,
    - identical objects are reused,
    - new objects are added,
    - changed representations supersede prior representations,
    - prior versions remain historically traceable,
    - no certified upstream semantic decision is recomputed.

    This stage does not:
    - reassess claims,
    - detect/reclassify conflict,
    - redecide integrity,
    - override guards,
    - rescore/reclassify Authority,
    - write Semantic Memory,
    - execute learning/reasoning,
    - create/select Active Target Set targets,
    - make linking decisions.
    """

    import hashlib
    import json

    if not isinstance(
        consistency_result,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "consistency_result must be a dictionary."
        )

    expected_lifecycle = {
        "schema":
            "dynamic_semantic_graph_consistency_validation_result_v1",

        "dynamic_semantic_graph_version":
            DYNAMIC_SEMANTIC_GRAPH_VERSION,

        "phase":
            DYNAMIC_SEMANTIC_GRAPH_PHASE,

        "patch":
            "4.6.26I",

        "status":
            "GRAPH_CONSISTENCY_AND_REFERENTIAL_INTEGRITY_VALIDATED",

        "policy":
            "CERTIFIED_DYNAMIC_GRAPH_CONSISTENCY_AND_REFERENTIAL_INTEGRITY",

        "next":
            "dynamic_graph_update_and_merge_engine",
    }

    for key, expected in expected_lifecycle.items():

        if consistency_result.get(key) != expected:
            raise DynamicSemanticGraphError(
                "Invalid 4.6.26I lifecycle field: "
                f"{key}"
            )

    report = consistency_result.get(
        "consistency_report"
    )

    if not isinstance(report, dict):
        raise DynamicSemanticGraphError(
            "consistency_report must be a dictionary."
        )

    if report.get(
        "referential_integrity_valid"
    ) is not True:
        raise DynamicSemanticGraphError(
            "Graph is not referentially valid."
        )

    if report.get(
        "graph_consistency_valid"
    ) is not True:
        raise DynamicSemanticGraphError(
            "Graph is not consistency certified."
        )

    incoming_nodes = consistency_result.get(
        "canonical_graph_nodes"
    )

    incoming_edges = consistency_result.get(
        "canonical_graph_edges"
    )

    contract = consistency_result.get(
        "scope_mutation_contract"
    )

    architecture = consistency_result.get(
        "architecture"
    )

    preservation_contract = consistency_result.get(
        "preservation_contract"
    )

    validated_records = consistency_result.get(
        "validated_graph_intake_records"
    )

    final_claim_integrity_package = (
        consistency_result.get(
            "final_claim_integrity_package"
        )
    )

    if not isinstance(
        incoming_nodes,
        list,
    ):
        raise DynamicSemanticGraphError(
            "canonical_graph_nodes must be a list."
        )

    if not isinstance(
        incoming_edges,
        list,
    ):
        raise DynamicSemanticGraphError(
            "canonical_graph_edges must be a list."
        )

    if (
        consistency_result.get(
            "node_count"
        )
        != len(incoming_nodes)
    ):
        raise DynamicSemanticGraphError(
            "Incoming node count mismatch."
        )

    if (
        consistency_result.get(
            "edge_count"
        )
        != len(incoming_edges)
    ):
        raise DynamicSemanticGraphError(
            "Incoming edge count mismatch."
        )

    if not isinstance(contract, dict):
        raise DynamicSemanticGraphError(
            "scope_mutation_contract must be a dictionary."
        )

    if not isinstance(
        architecture,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "architecture must be a dictionary."
        )

    if not isinstance(
        preservation_contract,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "preservation_contract must be a dictionary."
        )

    permissions = contract.get(
        "mutation_permissions"
    )

    forbidden = contract.get(
        "forbidden_mutations"
    )

    if not isinstance(
        permissions,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "mutation_permissions must be a dictionary."
        )

    if not isinstance(
        forbidden,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "forbidden_mutations must be a dictionary."
        )

    required_permissions = (
        "may_add_new_graph_versions",
        "may_merge_equivalent_graph_objects",
        "may_update_graph_metadata",
        "may_mark_graph_object_superseded",
        "may_preserve_historical_graph_versions",
    )

    for flag in required_permissions:

        if permissions.get(flag) is not True:
            raise DynamicSemanticGraphError(
                "Dynamic graph merge permission missing: "
                f"{flag}"
            )

    required_forbidden_false = (
        "may_rewrite_claim_text",
        "may_reassess_claim_support",
        "may_redetect_claim_conflict",
        "may_reclassify_claim_conflict",
        "may_redecide_claim_integrity",
        "may_override_guard_disposition",
        "may_rescore_authority",
        "may_reclassify_authority",
        "may_invent_unsupported_nodes",
        "may_invent_unsupported_edges",
        "may_create_active_targets",
        "may_change_active_target_owner",
        "may_move_external_target_partition",
        "may_change_external_route_eligibility",
        "may_select_final_external_target",
        "may_write_semantic_memory",
        "may_execute_learning",
        "may_execute_reasoning",
        "may_make_linking_decision",
        "may_create_editor_highlight",
    )

    for flag in required_forbidden_false:

        if forbidden.get(flag) is not False:
            raise DynamicSemanticGraphError(
                "Dynamic graph merge prohibition drift: "
                f"{flag}"
            )

    def canonical_json(
        value: Any,
    ) -> str:

        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )

    def digest(
        value: Any,
    ) -> str:

        return hashlib.sha256(
            canonical_json(
                value
            ).encode(
                "utf-8"
            )
        ).hexdigest()

    def validate_node(
        node: dict[str, Any],
    ) -> None:

        if (
            not isinstance(node, dict)
            or node.get("schema")
            != "dynamic_semantic_graph_node_v1"
        ):
            raise DynamicSemanticGraphError(
                "Invalid graph node during merge."
            )

        if (
            not isinstance(
                node.get("node_id"),
                str,
            )
            or not node[
                "node_id"
            ].startswith(
                "graphnode:v1:"
            )
        ):
            raise DynamicSemanticGraphError(
                "Invalid graph node ID during merge."
            )

        if node.get(
            "canonical_identity_deterministic"
        ) is not True:
            raise DynamicSemanticGraphError(
                "Non-deterministic node rejected."
            )

        if node.get(
            "certified_input_backed"
        ) is not True:
            raise DynamicSemanticGraphError(
                "Uncertified node rejected."
            )

        if node.get(
            "unsupported_invention_performed"
        ) is not False:
            raise DynamicSemanticGraphError(
                "Invented graph node rejected."
            )

    def validate_edge(
        edge: dict[str, Any],
    ) -> None:

        if (
            not isinstance(edge, dict)
            or edge.get("schema")
            != "dynamic_semantic_graph_edge_v1"
        ):
            raise DynamicSemanticGraphError(
                "Invalid graph edge during merge."
            )

        if (
            not isinstance(
                edge.get("edge_id"),
                str,
            )
            or not edge[
                "edge_id"
            ].startswith(
                "graphedge:v1:"
            )
        ):
            raise DynamicSemanticGraphError(
                "Invalid graph edge ID during merge."
            )

        if edge.get(
            "canonical_identity_deterministic"
        ) is not True:
            raise DynamicSemanticGraphError(
                "Non-deterministic edge rejected."
            )

        if edge.get(
            "certified_relationship_backed"
        ) is not True:
            raise DynamicSemanticGraphError(
                "Uncertified relationship rejected."
            )

        if edge.get(
            "unsupported_invention_performed"
        ) is not False:
            raise DynamicSemanticGraphError(
                "Invented graph edge rejected."
            )

    for node in incoming_nodes:
        validate_node(
            node
        )

    for edge in incoming_edges:
        validate_edge(
            edge
        )

    incoming_node_ids = {
        node[
            "node_id"
        ]
        for node in incoming_nodes
    }

    if len(
        incoming_node_ids
    ) != len(
        incoming_nodes
    ):
        raise DynamicSemanticGraphError(
            "Duplicate incoming node IDs."
        )

    incoming_edge_ids = {
        edge[
            "edge_id"
        ]
        for edge in incoming_edges
    }

    if len(
        incoming_edge_ids
    ) != len(
        incoming_edges
    ):
        raise DynamicSemanticGraphError(
            "Duplicate incoming edge IDs."
        )

    previous_nodes = []
    previous_edges = []
    previous_history = []
    previous_snapshot_id = None
    previous_snapshot_digest = None

    if previous_graph_snapshot is not None:

        if not isinstance(
            previous_graph_snapshot,
            dict,
        ):
            raise DynamicSemanticGraphError(
                "previous_graph_snapshot must be a dictionary."
            )

        if (
            previous_graph_snapshot.get(
                "schema"
            )
            != "dynamic_semantic_graph_snapshot_v1"
        ):
            raise DynamicSemanticGraphError(
                "Invalid previous graph snapshot schema."
            )

        previous_snapshot_id = (
            previous_graph_snapshot.get(
                "graph_snapshot_id"
            )
        )

        previous_snapshot_digest = (
            previous_graph_snapshot.get(
                "graph_snapshot_digest"
            )
        )

        if (
            not isinstance(
                previous_snapshot_id,
                str,
            )
            or not previous_snapshot_id.startswith(
                "graphsnapshot:v1:"
            )
        ):
            raise DynamicSemanticGraphError(
                "Invalid previous graph snapshot ID."
            )

        if (
            not isinstance(
                previous_snapshot_digest,
                str,
            )
            or len(
                previous_snapshot_digest
            )
            != 64
        ):
            raise DynamicSemanticGraphError(
                "Invalid previous graph snapshot digest."
            )

        previous_nodes = (
            previous_graph_snapshot.get(
                "canonical_graph_nodes"
            )
        )

        previous_edges = (
            previous_graph_snapshot.get(
                "canonical_graph_edges"
            )
        )

        previous_history = (
            previous_graph_snapshot.get(
                "historical_object_versions",
                [],
            )
        )

        if not isinstance(
            previous_nodes,
            list,
        ):
            raise DynamicSemanticGraphError(
                "Previous snapshot nodes must be a list."
            )

        if not isinstance(
            previous_edges,
            list,
        ):
            raise DynamicSemanticGraphError(
                "Previous snapshot edges must be a list."
            )

        if not isinstance(
            previous_history,
            list,
        ):
            raise DynamicSemanticGraphError(
                "Previous graph history must be a list."
            )

        for node in previous_nodes:
            validate_node(
                node
            )

        for edge in previous_edges:
            validate_edge(
                edge
            )

    previous_node_by_id = {
        node[
            "node_id"
        ]:
            node
        for node in previous_nodes
    }

    previous_edge_by_id = {
        edge[
            "edge_id"
        ]:
            edge
        for edge in previous_edges
    }

    if len(
        previous_node_by_id
    ) != len(
        previous_nodes
    ):
        raise DynamicSemanticGraphError(
            "Duplicate previous node IDs."
        )

    if len(
        previous_edge_by_id
    ) != len(
        previous_edges
    ):
        raise DynamicSemanticGraphError(
            "Duplicate previous edge IDs."
        )

    merged_nodes = []
    merged_edges = []

    historical_versions = copy.deepcopy(
        previous_history
    )

    added_node_count = 0
    reused_node_count = 0
    superseded_node_count = 0

    added_edge_count = 0
    reused_edge_count = 0
    superseded_edge_count = 0

    for incoming in incoming_nodes:

        node_id = incoming[
            "node_id"
        ]

        previous = (
            previous_node_by_id.get(
                node_id
            )
        )

        if previous is None:

            merged_nodes.append(
                copy.deepcopy(
                    incoming
                )
            )

            added_node_count += 1
            continue

        if previous == incoming:

            merged_nodes.append(
                copy.deepcopy(
                    incoming
                )
            )

            reused_node_count += 1
            continue

        if (
            previous.get(
                "node_type"
            )
            != incoming.get(
                "node_type"
            )
            or previous.get(
                "source_object_id"
            )
            != incoming.get(
                "source_object_id"
            )
        ):
            raise DynamicSemanticGraphError(
                "Stable node identity collision during merge."
            )

        historical_versions.append(
            {
                "schema":
                    "dynamic_semantic_graph_historical_object_version_v1",

                "object_kind":
                    "NODE",

                "object_id":
                    node_id,

                "supersession_reason":
                    "NEW_CERTIFIED_REPRESENTATION",

                "previous_object":
                    copy.deepcopy(
                        previous
                    ),

                "replacement_object":
                    copy.deepcopy(
                        incoming
                    ),

                "historical_state":
                    "SUPERSEDED",

                "upstream_truth_rewritten":
                    False,
            }
        )

        merged_nodes.append(
            copy.deepcopy(
                incoming
            )
        )

        superseded_node_count += 1

    incoming_node_id_set = {
        node[
            "node_id"
        ]
        for node in incoming_nodes
    }

    retired_node_count = 0

    for previous in previous_nodes:

        if previous[
            "node_id"
        ] not in incoming_node_id_set:

            historical_versions.append(
                {
                    "schema":
                        "dynamic_semantic_graph_historical_object_version_v1",

                    "object_kind":
                        "NODE",

                    "object_id":
                        previous[
                            "node_id"
                        ],

                    "supersession_reason":
                        "NOT_PRESENT_IN_NEW_CERTIFIED_GRAPH",

                    "previous_object":
                        copy.deepcopy(
                            previous
                        ),

                    "replacement_object":
                        None,

                    "historical_state":
                        "RETIRED",

                    "upstream_truth_rewritten":
                        False,
                }
            )

            retired_node_count += 1

    for incoming in incoming_edges:

        edge_id = incoming[
            "edge_id"
        ]

        previous = (
            previous_edge_by_id.get(
                edge_id
            )
        )

        if previous is None:

            merged_edges.append(
                copy.deepcopy(
                    incoming
                )
            )

            added_edge_count += 1
            continue

        if previous == incoming:

            merged_edges.append(
                copy.deepcopy(
                    incoming
                )
            )

            reused_edge_count += 1
            continue

        if (
            previous.get(
                "edge_type"
            )
            != incoming.get(
                "edge_type"
            )
            or previous.get(
                "from_node_id"
            )
            != incoming.get(
                "from_node_id"
            )
            or previous.get(
                "to_node_id"
            )
            != incoming.get(
                "to_node_id"
            )
        ):
            raise DynamicSemanticGraphError(
                "Stable edge identity collision during merge."
            )

        historical_versions.append(
            {
                "schema":
                    "dynamic_semantic_graph_historical_object_version_v1",

                "object_kind":
                    "EDGE",

                "object_id":
                    edge_id,

                "supersession_reason":
                    "NEW_CERTIFIED_REPRESENTATION",

                "previous_object":
                    copy.deepcopy(
                        previous
                    ),

                "replacement_object":
                    copy.deepcopy(
                        incoming
                    ),

                "historical_state":
                    "SUPERSEDED",

                "upstream_truth_rewritten":
                    False,
            }
        )

        merged_edges.append(
            copy.deepcopy(
                incoming
            )
        )

        superseded_edge_count += 1

    incoming_edge_id_set = {
        edge[
            "edge_id"
        ]
        for edge in incoming_edges
    }

    retired_edge_count = 0

    for previous in previous_edges:

        if previous[
            "edge_id"
        ] not in incoming_edge_id_set:

            historical_versions.append(
                {
                    "schema":
                        "dynamic_semantic_graph_historical_object_version_v1",

                    "object_kind":
                        "EDGE",

                    "object_id":
                        previous[
                            "edge_id"
                        ],

                    "supersession_reason":
                        "NOT_PRESENT_IN_NEW_CERTIFIED_GRAPH",

                    "previous_object":
                        copy.deepcopy(
                            previous
                        ),

                    "replacement_object":
                        None,

                    "historical_state":
                        "RETIRED",

                    "upstream_truth_rewritten":
                        False,
                }
            )

            retired_edge_count += 1

    merged_nodes.sort(
        key=lambda item: (
            item[
                "node_type"
            ],
            item[
                "source_object_id"
            ],
            item[
                "node_id"
            ],
        )
    )

    merged_edges.sort(
        key=lambda item: (
            item[
                "edge_type"
            ],
            item[
                "from_node_id"
            ],
            item[
                "to_node_id"
            ],
            item[
                "edge_id"
            ],
        )
    )

    historical_versions.sort(
        key=lambda item: (
            item.get(
                "object_kind",
                "",
            ),
            item.get(
                "object_id",
                "",
            ),
            item.get(
                "historical_state",
                "",
            ),
            digest(
                item
            ),
        )
    )

    merged_node_ids = {
        node[
            "node_id"
        ]
        for node in merged_nodes
    }

    if len(
        merged_node_ids
    ) != len(
        merged_nodes
    ):
        raise DynamicSemanticGraphError(
            "Merged graph contains duplicate node IDs."
        )

    merged_edge_ids = {
        edge[
            "edge_id"
        ]
        for edge in merged_edges
    }

    if len(
        merged_edge_ids
    ) != len(
        merged_edges
    ):
        raise DynamicSemanticGraphError(
            "Merged graph contains duplicate edge IDs."
        )

    for edge in merged_edges:

        if (
            edge[
                "from_node_id"
            ]
            not in merged_node_ids
        ):
            raise DynamicSemanticGraphError(
                "Merged graph contains missing from-node."
            )

        if (
            edge[
                "to_node_id"
            ]
            not in merged_node_ids
        ):
            raise DynamicSemanticGraphError(
                "Merged graph contains missing to-node."
            )

    incoming_graph_version_id = (
        consistency_result.get(
            "graph_version_id"
        )
    )

    incoming_graph_version_digest = (
        consistency_result.get(
            "graph_version_digest"
        )
    )

    if (
        not isinstance(
            incoming_graph_version_id,
            str,
        )
        or not incoming_graph_version_id.startswith(
            "graphversion:v1:"
        )
    ):
        raise DynamicSemanticGraphError(
            "Invalid incoming graph version ID."
        )

    if (
        not isinstance(
            incoming_graph_version_digest,
            str,
        )
        or len(
            incoming_graph_version_digest
        )
        != 64
    ):
        raise DynamicSemanticGraphError(
            "Invalid incoming graph version digest."
        )

    merge_material = {
        "previous_graph_snapshot_id":
            previous_snapshot_id,

        "previous_graph_snapshot_digest":
            previous_snapshot_digest,

        "incoming_graph_version_id":
            incoming_graph_version_id,

        "incoming_graph_version_digest":
            incoming_graph_version_digest,

        "active_node_ids": [
            node[
                "node_id"
            ]
            for node in merged_nodes
        ],

        "active_node_payload_digests": [
            node[
                "payload_digest"
            ]
            for node in merged_nodes
        ],

        "active_edge_ids": [
            edge[
                "edge_id"
            ]
            for edge in merged_edges
        ],

        "active_edge_payload_digests": [
            edge[
                "payload_digest"
            ]
            for edge in merged_edges
        ],

        "historical_version_digests": [
            digest(
                item
            )
            for item in historical_versions
        ],
    }

    graph_snapshot_digest = digest(
        merge_material
    )

    graph_snapshot_id = (
        "graphsnapshot:v1:"
        + graph_snapshot_digest
    )

    snapshot = {
        "schema":
            "dynamic_semantic_graph_snapshot_v1",

        "graph_snapshot_id":
            graph_snapshot_id,

        "graph_snapshot_digest":
            graph_snapshot_digest,

        "parent_graph_snapshot_id":
            previous_snapshot_id,

        "parent_graph_snapshot_digest":
            previous_snapshot_digest,

        "source_graph_version_id":
            incoming_graph_version_id,

        "source_graph_version_digest":
            incoming_graph_version_digest,

        "node_count":
            len(
                merged_nodes
            ),

        "edge_count":
            len(
                merged_edges
            ),

        "historical_version_count":
            len(
                historical_versions
            ),

        "canonical_graph_nodes":
            copy.deepcopy(
                merged_nodes
            ),

        "canonical_graph_edges":
            copy.deepcopy(
                merged_edges
            ),

        "historical_object_versions":
            copy.deepcopy(
                historical_versions
            ),

        "referential_integrity_preserved":
            True,

        "historical_trace_preserved":
            True,

        "idempotent_merge":
            True,

        "upstream_truth_rewritten":
            False,
    }

    merge_report = {
        "schema":
            "dynamic_semantic_graph_merge_report_v1",

        "previous_snapshot_present":
            previous_graph_snapshot
            is not None,

        "added_node_count":
            added_node_count,

        "reused_node_count":
            reused_node_count,

        "superseded_node_count":
            superseded_node_count,

        "retired_node_count":
            retired_node_count,

        "added_edge_count":
            added_edge_count,

        "reused_edge_count":
            reused_edge_count,

        "superseded_edge_count":
            superseded_edge_count,

        "retired_edge_count":
            retired_edge_count,

        "historical_version_count":
            len(
                historical_versions
            ),

        "referential_integrity_preserved":
            True,

        "stable_identity_preserved":
            True,

        "historical_versions_preserved":
            True,

        "upstream_semantic_state_recomputed":
            False,

        "upstream_truth_rewritten":
            False,
    }

    return {
        "schema":
            "dynamic_semantic_graph_update_merge_result_v1",

        "dynamic_semantic_graph_version":
            DYNAMIC_SEMANTIC_GRAPH_VERSION,

        "phase":
            DYNAMIC_SEMANTIC_GRAPH_PHASE,

        "patch":
            "4.6.26J",

        "status":
            "DYNAMIC_GRAPH_UPDATED_AND_MERGED",

        "graph_snapshot_id":
            graph_snapshot_id,

        "graph_snapshot_digest":
            graph_snapshot_digest,

        "node_count":
            len(
                merged_nodes
            ),

        "edge_count":
            len(
                merged_edges
            ),

        "canonical_graph_nodes":
            merged_nodes,

        "canonical_graph_edges":
            merged_edges,

        "historical_object_versions":
            historical_versions,

        "graph_snapshot":
            snapshot,

        "merge_report":
            merge_report,

        "validated_graph_intake_records":
            copy.deepcopy(
                validated_records
            ),

        "scope_mutation_contract":
            copy.deepcopy(
                contract
            ),

        "architecture":
            copy.deepcopy(
                architecture
            ),

        "final_claim_integrity_package":
            copy.deepcopy(
                final_claim_integrity_package
            ),

        "preservation_contract":
            copy.deepcopy(
                preservation_contract
            ),

        "processing_boundaries": {
            "dynamic_graph_update_performed":
                True,

            "dynamic_graph_merge_performed":
                True,

            "graph_snapshot_created":
                True,

            "historical_versions_preserved":
                True,

            "graph_mutation_performed":
                True,

            "support_reassessment_performed":
                False,

            "conflict_redetection_performed":
                False,

            "conflict_reclassification_performed":
                False,

            "integrity_redecision_performed":
                False,

            "guard_redisposition_performed":
                False,

            "authority_rescoring_performed":
                False,

            "authority_reclassification_performed":
                False,

            "semantic_memory_written":
                False,

            "learning_performed":
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

            "unsupported_node_invention_performed":
                False,

            "unsupported_edge_invention_performed":
                False,

            "upstream_truth_rewritten":
                False,
        },

        "policy":
            "CERTIFIED_DYNAMIC_GRAPH_UPDATE_AND_MERGE",

        "next":
            "graph_provenance_and_lineage_trace",
    }

def build_graph_provenance_and_lineage_trace_v1(
    merge_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.26K ? Graph Provenance & Lineage Trace.

    Builds deterministic provenance and lineage records for the active
    Dynamic Semantic Graph snapshot and all preserved historical graph
    object versions.

    Traceability only.

    It does not:
    - create new semantic knowledge,
    - alter graph semantic objects,
    - reassess claims,
    - detect/reclassify conflicts,
    - redecide integrity,
    - override guards,
    - rescore/reclassify Authority,
    - write Semantic Memory,
    - execute learning/reasoning,
    - create/select targets,
    - make linking decisions.
    """

    import hashlib
    import json

    if not isinstance(
        merge_result,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "merge_result must be a dictionary."
        )

    expected_lifecycle = {
        "schema":
            "dynamic_semantic_graph_update_merge_result_v1",

        "dynamic_semantic_graph_version":
            DYNAMIC_SEMANTIC_GRAPH_VERSION,

        "phase":
            DYNAMIC_SEMANTIC_GRAPH_PHASE,

        "patch":
            "4.6.26J",

        "status":
            "DYNAMIC_GRAPH_UPDATED_AND_MERGED",

        "policy":
            "CERTIFIED_DYNAMIC_GRAPH_UPDATE_AND_MERGE",

        "next":
            "graph_provenance_and_lineage_trace",
    }

    for key, expected in expected_lifecycle.items():

        if merge_result.get(key) != expected:
            raise DynamicSemanticGraphError(
                "Invalid 4.6.26J lifecycle field: "
                f"{key}"
            )

    snapshot = merge_result.get(
        "graph_snapshot"
    )

    nodes = merge_result.get(
        "canonical_graph_nodes"
    )

    edges = merge_result.get(
        "canonical_graph_edges"
    )

    history = merge_result.get(
        "historical_object_versions"
    )

    merge_report = merge_result.get(
        "merge_report"
    )

    preservation_contract = merge_result.get(
        "preservation_contract"
    )

    validated_records = merge_result.get(
        "validated_graph_intake_records"
    )

    contract = merge_result.get(
        "scope_mutation_contract"
    )

    architecture = merge_result.get(
        "architecture"
    )

    final_claim_integrity_package = (
        merge_result.get(
            "final_claim_integrity_package"
        )
    )

    if not isinstance(snapshot, dict):
        raise DynamicSemanticGraphError(
            "graph_snapshot must be a dictionary."
        )

    if (
        snapshot.get("schema")
        != "dynamic_semantic_graph_snapshot_v1"
    ):
        raise DynamicSemanticGraphError(
            "Invalid graph snapshot schema."
        )

    if not isinstance(nodes, list):
        raise DynamicSemanticGraphError(
            "canonical_graph_nodes must be a list."
        )

    if not isinstance(edges, list):
        raise DynamicSemanticGraphError(
            "canonical_graph_edges must be a list."
        )

    if not isinstance(history, list):
        raise DynamicSemanticGraphError(
            "historical_object_versions must be a list."
        )

    if not isinstance(merge_report, dict):
        raise DynamicSemanticGraphError(
            "merge_report must be a dictionary."
        )

    if not isinstance(
        preservation_contract,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "preservation_contract must be a dictionary."
        )

    if (
        merge_result.get("node_count")
        != len(nodes)
    ):
        raise DynamicSemanticGraphError(
            "Lineage input node count mismatch."
        )

    if (
        merge_result.get("edge_count")
        != len(edges)
    ):
        raise DynamicSemanticGraphError(
            "Lineage input edge count mismatch."
        )

    graph_snapshot_id = (
        merge_result.get(
            "graph_snapshot_id"
        )
    )

    graph_snapshot_digest = (
        merge_result.get(
            "graph_snapshot_digest"
        )
    )

    if (
        not isinstance(
            graph_snapshot_id,
            str,
        )
        or not graph_snapshot_id.startswith(
            "graphsnapshot:v1:"
        )
    ):
        raise DynamicSemanticGraphError(
            "Invalid graph snapshot ID."
        )

    if (
        not isinstance(
            graph_snapshot_digest,
            str,
        )
        or len(
            graph_snapshot_digest
        )
        != 64
    ):
        raise DynamicSemanticGraphError(
            "Invalid graph snapshot digest."
        )

    if (
        snapshot.get(
            "graph_snapshot_id"
        )
        != graph_snapshot_id
    ):
        raise DynamicSemanticGraphError(
            "Graph snapshot ID drift."
        )

    if (
        snapshot.get(
            "graph_snapshot_digest"
        )
        != graph_snapshot_digest
    ):
        raise DynamicSemanticGraphError(
            "Graph snapshot digest drift."
        )

    if snapshot.get(
        "historical_trace_preserved"
    ) is not True:
        raise DynamicSemanticGraphError(
            "Historical graph trace is not preserved."
        )

    if snapshot.get(
        "upstream_truth_rewritten"
    ) is not False:
        raise DynamicSemanticGraphError(
            "Upstream truth rewrite detected."
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

        if preservation_contract.get(flag) is not True:
            raise DynamicSemanticGraphError(
                "Lineage preservation contract drift: "
                f"{flag}"
            )

    def canonical_json(
        value: Any,
    ) -> str:

        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )

    def digest(
        value: Any,
    ) -> str:

        return hashlib.sha256(
            canonical_json(
                value
            ).encode(
                "utf-8"
            )
        ).hexdigest()

    active_object_lineage = []

    for node in nodes:

        if (
            not isinstance(node, dict)
            or node.get("schema")
            != "dynamic_semantic_graph_node_v1"
        ):
            raise DynamicSemanticGraphError(
                "Invalid active graph node in lineage stage."
            )

        node_id = node.get(
            "node_id"
        )

        lineage_core = {
            "object_kind":
                "NODE",

            "object_id":
                node_id,

            "object_type":
                node.get(
                    "node_type"
                ),

            "source_object_type":
                node.get(
                    "source_object_type"
                ),

            "source_object_id":
                node.get(
                    "source_object_id"
                ),

            "payload_digest":
                node.get(
                    "payload_digest"
                ),

            "object_provenance":
                copy.deepcopy(
                    node.get(
                        "provenance"
                    )
                ),

            "graph_snapshot_id":
                graph_snapshot_id,

            "graph_snapshot_digest":
                graph_snapshot_digest,

            "source_graph_version_id":
                snapshot.get(
                    "source_graph_version_id"
                ),

            "source_graph_version_digest":
                snapshot.get(
                    "source_graph_version_digest"
                ),

            "parent_graph_snapshot_id":
                snapshot.get(
                    "parent_graph_snapshot_id"
                ),

            "lifecycle_state":
                node.get(
                    "lifecycle_state"
                ),

            "certified_input_backed":
                node.get(
                    "certified_input_backed"
                ),

            "upstream_truth_rewritten":
                False,
        }

        lineage_digest = digest(
            lineage_core
        )

        active_object_lineage.append(
            {
                "schema":
                    "dynamic_semantic_graph_object_lineage_record_v1",

                "lineage_id":
                    "graphlineage:v1:"
                    + lineage_digest,

                "lineage_digest":
                    lineage_digest,

                **lineage_core,
            }
        )

    for edge in edges:

        if (
            not isinstance(edge, dict)
            or edge.get("schema")
            != "dynamic_semantic_graph_edge_v1"
        ):
            raise DynamicSemanticGraphError(
                "Invalid active graph edge in lineage stage."
            )

        edge_id = edge.get(
            "edge_id"
        )

        lineage_core = {
            "object_kind":
                "EDGE",

            "object_id":
                edge_id,

            "object_type":
                edge.get(
                    "edge_type"
                ),

            "from_node_id":
                edge.get(
                    "from_node_id"
                ),

            "to_node_id":
                edge.get(
                    "to_node_id"
                ),

            "relation_source_id":
                edge.get(
                    "relation_source_id"
                ),

            "payload_digest":
                edge.get(
                    "payload_digest"
                ),

            "object_provenance":
                copy.deepcopy(
                    edge.get(
                        "provenance"
                    )
                ),

            "graph_snapshot_id":
                graph_snapshot_id,

            "graph_snapshot_digest":
                graph_snapshot_digest,

            "source_graph_version_id":
                snapshot.get(
                    "source_graph_version_id"
                ),

            "source_graph_version_digest":
                snapshot.get(
                    "source_graph_version_digest"
                ),

            "parent_graph_snapshot_id":
                snapshot.get(
                    "parent_graph_snapshot_id"
                ),

            "lifecycle_state":
                edge.get(
                    "lifecycle_state"
                ),

            "certified_relationship_backed":
                edge.get(
                    "certified_relationship_backed"
                ),

            "upstream_truth_rewritten":
                False,
        }

        lineage_digest = digest(
            lineage_core
        )

        active_object_lineage.append(
            {
                "schema":
                    "dynamic_semantic_graph_object_lineage_record_v1",

                "lineage_id":
                    "graphlineage:v1:"
                    + lineage_digest,

                "lineage_digest":
                    lineage_digest,

                **lineage_core,
            }
        )

    historical_lineage = []

    for item in history:

        if (
            not isinstance(item, dict)
            or item.get("schema")
            != "dynamic_semantic_graph_historical_object_version_v1"
        ):
            raise DynamicSemanticGraphError(
                "Invalid historical graph object record."
            )

        if item.get(
            "upstream_truth_rewritten"
        ) is not False:
            raise DynamicSemanticGraphError(
                "Historical object rewrites upstream truth."
            )

        previous_object = item.get(
            "previous_object"
        )

        if not isinstance(
            previous_object,
            dict,
        ):
            raise DynamicSemanticGraphError(
                "Historical lineage requires previous_object."
            )

        replacement_object = item.get(
            "replacement_object"
        )

        core = {
            "object_kind":
                item.get(
                    "object_kind"
                ),

            "object_id":
                item.get(
                    "object_id"
                ),

            "historical_state":
                item.get(
                    "historical_state"
                ),

            "supersession_reason":
                item.get(
                    "supersession_reason"
                ),

            "previous_object_digest":
                digest(
                    previous_object
                ),

            "replacement_object_digest":
                (
                    digest(
                        replacement_object
                    )
                    if replacement_object
                    is not None
                    else None
                ),

            "graph_snapshot_id":
                graph_snapshot_id,

            "parent_graph_snapshot_id":
                snapshot.get(
                    "parent_graph_snapshot_id"
                ),

            "upstream_truth_rewritten":
                False,
        }

        historical_digest = digest(
            core
        )

        historical_lineage.append(
            {
                "schema":
                    "dynamic_semantic_graph_historical_lineage_record_v1",

                "lineage_id":
                    "graphhistorylineage:v1:"
                    + historical_digest,

                "lineage_digest":
                    historical_digest,

                **core,
            }
        )

    active_object_lineage.sort(
        key=lambda item: (
            item[
                "object_kind"
            ],
            item[
                "object_id"
            ],
            item[
                "lineage_id"
            ],
        )
    )

    historical_lineage.sort(
        key=lambda item: (
            item[
                "object_kind"
            ],
            item[
                "object_id"
            ],
            item[
                "historical_state"
            ],
            item[
                "lineage_id"
            ],
        )
    )

    active_ids = [
        item[
            "lineage_id"
        ]
        for item in active_object_lineage
    ]

    historical_ids = [
        item[
            "lineage_id"
        ]
        for item in historical_lineage
    ]

    if len(active_ids) != len(
        set(active_ids)
    ):
        raise DynamicSemanticGraphError(
            "Duplicate active lineage IDs."
        )

    if len(historical_ids) != len(
        set(historical_ids)
    ):
        raise DynamicSemanticGraphError(
            "Duplicate historical lineage IDs."
        )

    lineage_root_material = {
        "graph_snapshot_id":
            graph_snapshot_id,

        "graph_snapshot_digest":
            graph_snapshot_digest,

        "parent_graph_snapshot_id":
            snapshot.get(
                "parent_graph_snapshot_id"
            ),

        "source_graph_version_id":
            snapshot.get(
                "source_graph_version_id"
            ),

        "active_lineage_digests": [
            item[
                "lineage_digest"
            ]
            for item
            in active_object_lineage
        ],

        "historical_lineage_digests": [
            item[
                "lineage_digest"
            ]
            for item
            in historical_lineage
        ],
    }

    lineage_root_digest = digest(
        lineage_root_material
    )

    lineage_root_id = (
        "graphlineageroot:v1:"
        + lineage_root_digest
    )

    lineage_report = {
        "schema":
            "dynamic_semantic_graph_lineage_report_v1",

        "lineage_root_id":
            lineage_root_id,

        "lineage_root_digest":
            lineage_root_digest,

        "graph_snapshot_id":
            graph_snapshot_id,

        "parent_graph_snapshot_id":
            snapshot.get(
                "parent_graph_snapshot_id"
            ),

        "active_node_lineage_count":
            sum(
                1
                for item
                in active_object_lineage
                if item[
                    "object_kind"
                ]
                == "NODE"
            ),

        "active_edge_lineage_count":
            sum(
                1
                for item
                in active_object_lineage
                if item[
                    "object_kind"
                ]
                == "EDGE"
            ),

        "historical_lineage_count":
            len(
                historical_lineage
            ),

        "every_active_graph_object_traced":
            len(
                active_object_lineage
            )
            == (
                len(nodes)
                + len(edges)
            ),

        "historical_versions_traced":
            len(
                historical_lineage
            )
            == len(history),

        "snapshot_parentage_traced":
            True,

        "graph_version_origin_traced":
            True,

        "object_provenance_preserved":
            True,

        "historical_supersession_preserved":
            True,

        "upstream_truth_rewritten":
            False,

        "lineage_complete":
            True,
    }

    return {
        "schema":
            "dynamic_semantic_graph_provenance_lineage_result_v1",

        "dynamic_semantic_graph_version":
            DYNAMIC_SEMANTIC_GRAPH_VERSION,

        "phase":
            DYNAMIC_SEMANTIC_GRAPH_PHASE,

        "patch":
            "4.6.26K",

        "status":
            "GRAPH_PROVENANCE_AND_LINEAGE_TRACED",

        "graph_snapshot_id":
            graph_snapshot_id,

        "graph_snapshot_digest":
            graph_snapshot_digest,

        "lineage_root_id":
            lineage_root_id,

        "lineage_root_digest":
            lineage_root_digest,

        "active_object_lineage_count":
            len(
                active_object_lineage
            ),

        "historical_lineage_count":
            len(
                historical_lineage
            ),

        "active_object_lineage":
            active_object_lineage,

        "historical_lineage":
            historical_lineage,

        "lineage_report":
            lineage_report,

        "graph_snapshot":
            copy.deepcopy(
                snapshot
            ),

        "canonical_graph_nodes":
            copy.deepcopy(
                nodes
            ),

        "canonical_graph_edges":
            copy.deepcopy(
                edges
            ),

        "historical_object_versions":
            copy.deepcopy(
                history
            ),

        "merge_report":
            copy.deepcopy(
                merge_report
            ),

        "validated_graph_intake_records":
            copy.deepcopy(
                validated_records
            ),

        "scope_mutation_contract":
            copy.deepcopy(
                contract
            ),

        "architecture":
            copy.deepcopy(
                architecture
            ),

        "final_claim_integrity_package":
            copy.deepcopy(
                final_claim_integrity_package
            ),

        "preservation_contract":
            copy.deepcopy(
                preservation_contract
            ),

        "processing_boundaries": {
            "graph_provenance_trace_built":
                True,

            "graph_lineage_trace_built":
                True,

            "active_object_lineage_built":
                True,

            "historical_object_lineage_built":
                True,

            "snapshot_parentage_traced":
                True,

            "graph_version_origin_traced":
                True,

            "graph_node_creation_performed":
                False,

            "graph_edge_creation_performed":
                False,

            "graph_mutation_performed":
                False,

            "graph_merge_performed":
                False,

            "support_reassessment_performed":
                False,

            "conflict_redetection_performed":
                False,

            "conflict_reclassification_performed":
                False,

            "integrity_redecision_performed":
                False,

            "guard_redisposition_performed":
                False,

            "authority_rescoring_performed":
                False,

            "authority_reclassification_performed":
                False,

            "semantic_memory_written":
                False,

            "learning_performed":
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

            "unsupported_node_invention_performed":
                False,

            "unsupported_edge_invention_performed":
                False,

            "upstream_truth_rewritten":
                False,
        },

        "policy":
            "CERTIFIED_DYNAMIC_GRAPH_PROVENANCE_AND_LINEAGE",

        "next":
            "final_dynamic_semantic_graph_result",
    }

def build_final_dynamic_semantic_graph_result_v1(
    lineage_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.26L ? Final Dynamic Semantic Graph Result.

    Packages the fully constructed, consistency-certified, dynamically
    versioned, provenance-bound Dynamic Semantic Graph for downstream
    consumption.

    Packaging only.

    It does not:
    - create or modify semantic knowledge,
    - create nodes or edges,
    - merge graph state,
    - reassess support,
    - detect/reclassify conflict,
    - redecide integrity,
    - override guard disposition,
    - rescore/reclassify Authority,
    - write Semantic Memory,
    - execute Learning Engine behavior,
    - execute reasoning,
    - create/select Active Target Set targets,
    - make linking decisions,
    - create editor highlights.
    """

    import hashlib
    import json

    if not isinstance(
        lineage_result,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "lineage_result must be a dictionary."
        )

    expected_lifecycle = {
        "schema":
            "dynamic_semantic_graph_provenance_lineage_result_v1",

        "dynamic_semantic_graph_version":
            DYNAMIC_SEMANTIC_GRAPH_VERSION,

        "phase":
            DYNAMIC_SEMANTIC_GRAPH_PHASE,

        "patch":
            "4.6.26K",

        "status":
            "GRAPH_PROVENANCE_AND_LINEAGE_TRACED",

        "policy":
            "CERTIFIED_DYNAMIC_GRAPH_PROVENANCE_AND_LINEAGE",

        "next":
            "final_dynamic_semantic_graph_result",
    }

    for key, expected in expected_lifecycle.items():

        if lineage_result.get(key) != expected:
            raise DynamicSemanticGraphError(
                "Invalid 4.6.26K lifecycle field: "
                f"{key}"
            )

    graph_snapshot = lineage_result.get(
        "graph_snapshot"
    )

    nodes = lineage_result.get(
        "canonical_graph_nodes"
    )

    edges = lineage_result.get(
        "canonical_graph_edges"
    )

    history = lineage_result.get(
        "historical_object_versions"
    )

    active_lineage = lineage_result.get(
        "active_object_lineage"
    )

    historical_lineage = lineage_result.get(
        "historical_lineage"
    )

    lineage_report = lineage_result.get(
        "lineage_report"
    )

    merge_report = lineage_result.get(
        "merge_report"
    )

    preservation_contract = lineage_result.get(
        "preservation_contract"
    )

    architecture = lineage_result.get(
        "architecture"
    )

    scope_mutation_contract = lineage_result.get(
        "scope_mutation_contract"
    )

    final_claim_integrity_package = (
        lineage_result.get(
            "final_claim_integrity_package"
        )
    )

    validated_records = lineage_result.get(
        "validated_graph_intake_records"
    )

    if not isinstance(
        graph_snapshot,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "graph_snapshot must be a dictionary."
        )

    if (
        graph_snapshot.get("schema")
        != "dynamic_semantic_graph_snapshot_v1"
    ):
        raise DynamicSemanticGraphError(
            "Invalid graph snapshot schema."
        )

    if not isinstance(nodes, list):
        raise DynamicSemanticGraphError(
            "canonical_graph_nodes must be a list."
        )

    if not isinstance(edges, list):
        raise DynamicSemanticGraphError(
            "canonical_graph_edges must be a list."
        )

    if not isinstance(history, list):
        raise DynamicSemanticGraphError(
            "historical_object_versions must be a list."
        )

    if not isinstance(
        active_lineage,
        list,
    ):
        raise DynamicSemanticGraphError(
            "active_object_lineage must be a list."
        )

    if not isinstance(
        historical_lineage,
        list,
    ):
        raise DynamicSemanticGraphError(
            "historical_lineage must be a list."
        )

    if not isinstance(
        lineage_report,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "lineage_report must be a dictionary."
        )

    if not isinstance(
        merge_report,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "merge_report must be a dictionary."
        )

    if not isinstance(
        preservation_contract,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "preservation_contract must be a dictionary."
        )

    if not isinstance(
        architecture,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "architecture must be a dictionary."
        )

    if not isinstance(
        scope_mutation_contract,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "scope_mutation_contract must be a dictionary."
        )

    if not isinstance(
        final_claim_integrity_package,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "final_claim_integrity_package must be a dictionary."
        )

    if not isinstance(
        validated_records,
        list,
    ):
        raise DynamicSemanticGraphError(
            "validated_graph_intake_records must be a list."
        )

    graph_snapshot_id = lineage_result.get(
        "graph_snapshot_id"
    )

    graph_snapshot_digest = lineage_result.get(
        "graph_snapshot_digest"
    )

    lineage_root_id = lineage_result.get(
        "lineage_root_id"
    )

    lineage_root_digest = lineage_result.get(
        "lineage_root_digest"
    )

    if (
        not isinstance(
            graph_snapshot_id,
            str,
        )
        or not graph_snapshot_id.startswith(
            "graphsnapshot:v1:"
        )
    ):
        raise DynamicSemanticGraphError(
            "Invalid graph snapshot ID."
        )

    if (
        not isinstance(
            graph_snapshot_digest,
            str,
        )
        or len(
            graph_snapshot_digest
        )
        != 64
    ):
        raise DynamicSemanticGraphError(
            "Invalid graph snapshot digest."
        )

    if (
        graph_snapshot.get(
            "graph_snapshot_id"
        )
        != graph_snapshot_id
    ):
        raise DynamicSemanticGraphError(
            "Graph snapshot ID mismatch."
        )

    if (
        graph_snapshot.get(
            "graph_snapshot_digest"
        )
        != graph_snapshot_digest
    ):
        raise DynamicSemanticGraphError(
            "Graph snapshot digest mismatch."
        )

    if (
        not isinstance(
            lineage_root_id,
            str,
        )
        or not lineage_root_id.startswith(
            "graphlineageroot:v1:"
        )
    ):
        raise DynamicSemanticGraphError(
            "Invalid lineage root ID."
        )

    if (
        not isinstance(
            lineage_root_digest,
            str,
        )
        or len(
            lineage_root_digest
        )
        != 64
    ):
        raise DynamicSemanticGraphError(
            "Invalid lineage root digest."
        )

    if lineage_report.get(
        "lineage_root_id"
    ) != lineage_root_id:
        raise DynamicSemanticGraphError(
            "Lineage root ID mismatch."
        )

    if lineage_report.get(
        "lineage_root_digest"
    ) != lineage_root_digest:
        raise DynamicSemanticGraphError(
            "Lineage root digest mismatch."
        )

    for flag in (
        "every_active_graph_object_traced",
        "historical_versions_traced",
        "snapshot_parentage_traced",
        "graph_version_origin_traced",
        "object_provenance_preserved",
        "historical_supersession_preserved",
        "lineage_complete",
    ):

        if lineage_report.get(flag) is not True:
            raise DynamicSemanticGraphError(
                "Incomplete graph lineage contract: "
                f"{flag}"
            )

    if lineage_report.get(
        "upstream_truth_rewritten"
    ) is not False:
        raise DynamicSemanticGraphError(
            "Lineage indicates upstream truth rewrite."
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

        if preservation_contract.get(flag) is not True:
            raise DynamicSemanticGraphError(
                "Final graph preservation drift: "
                f"{flag}"
            )

    target_ownership = architecture.get(
        "target_ownership"
    )

    if not isinstance(
        target_ownership,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "architecture target_ownership must be a dictionary."
        )

    expected_target_contract = {
        "canonical_target_owner":
            "ACTIVE_TARGET_SET",

        "external_partition":
            "EXTERNAL_AUTHORITY",

        "external_route":
            "EXTERNAL",

        "final_external_selection_owner":
            "EXTERNAL_TARGET_RESOLVER",

        "dynamic_graph_may_create_target":
            False,

        "dynamic_graph_may_select_final_target":
            False,

        "dynamic_graph_target_nodes_are_references_only":
            True,
    }

    for key, expected in expected_target_contract.items():

        if target_ownership.get(key) != expected:
            raise DynamicSemanticGraphError(
                "Final graph target ownership drift: "
                f"{key}"
            )

    if (
        graph_snapshot.get(
            "referential_integrity_preserved"
        )
        is not True
    ):
        raise DynamicSemanticGraphError(
            "Graph snapshot referential integrity is not preserved."
        )

    if (
        graph_snapshot.get(
            "historical_trace_preserved"
        )
        is not True
    ):
        raise DynamicSemanticGraphError(
            "Graph snapshot history is not preserved."
        )

    if (
        graph_snapshot.get(
            "upstream_truth_rewritten"
        )
        is not False
    ):
        raise DynamicSemanticGraphError(
            "Graph snapshot rewrites upstream truth."
        )

    if (
        len(active_lineage)
        != len(nodes)
        + len(edges)
    ):
        raise DynamicSemanticGraphError(
            "Active graph lineage count mismatch."
        )

    if (
        len(historical_lineage)
        != len(history)
    ):
        raise DynamicSemanticGraphError(
            "Historical graph lineage count mismatch."
        )

    node_ids = [
        node.get(
            "node_id"
        )
        for node in nodes
    ]

    edge_ids = [
        edge.get(
            "edge_id"
        )
        for edge in edges
    ]

    if len(node_ids) != len(
        set(node_ids)
    ):
        raise DynamicSemanticGraphError(
            "Duplicate final graph node IDs."
        )

    if len(edge_ids) != len(
        set(edge_ids)
    ):
        raise DynamicSemanticGraphError(
            "Duplicate final graph edge IDs."
        )

    node_id_set = set(
        node_ids
    )

    for edge in edges:

        if edge.get(
            "from_node_id"
        ) not in node_id_set:
            raise DynamicSemanticGraphError(
                "Final graph edge has missing from-node."
            )

        if edge.get(
            "to_node_id"
        ) not in node_id_set:
            raise DynamicSemanticGraphError(
                "Final graph edge has missing to-node."
            )

    def canonical_json(
        value: Any,
    ) -> str:

        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )

    def digest(
        value: Any,
    ) -> str:

        return hashlib.sha256(
            canonical_json(
                value
            ).encode(
                "utf-8"
            )
        ).hexdigest()

    final_core = {
        "dynamic_semantic_graph_version":
            DYNAMIC_SEMANTIC_GRAPH_VERSION,

        "graph_snapshot_id":
            graph_snapshot_id,

        "graph_snapshot_digest":
            graph_snapshot_digest,

        "lineage_root_id":
            lineage_root_id,

        "lineage_root_digest":
            lineage_root_digest,

        "node_count":
            len(nodes),

        "edge_count":
            len(edges),

        "historical_version_count":
            len(history),

        "active_lineage_count":
            len(active_lineage),

        "historical_lineage_count":
            len(historical_lineage),

        "node_ids":
            node_ids,

        "node_payload_digests": [
            node.get(
                "payload_digest"
            )
            for node in nodes
        ],

        "edge_ids":
            edge_ids,

        "edge_payload_digests": [
            edge.get(
                "payload_digest"
            )
            for edge in edges
        ],

        "active_lineage_digests": [
            item.get(
                "lineage_digest"
            )
            for item in active_lineage
        ],

        "historical_lineage_digests": [
            item.get(
                "lineage_digest"
            )
            for item in historical_lineage
        ],

        "target_owner":
            "ACTIVE_TARGET_SET",

        "external_partition":
            "EXTERNAL_AUTHORITY",

        "external_route":
            "EXTERNAL",

        "final_external_selector":
            "EXTERNAL_TARGET_RESOLVER",
    }

    final_graph_digest = digest(
        final_core
    )

    final_graph_id = (
        "dynamicgraphfinal:v1:"
        + final_graph_digest
    )

    downstream_contract = {
        "schema":
            "dynamic_semantic_graph_downstream_contract_v1",

        "final_graph_id":
            final_graph_id,

        "final_graph_digest":
            final_graph_digest,

        "graph_represents_certified_semantic_state":
            True,

        "graph_is_dynamic_and_versioned":
            True,

        "graph_is_provenance_bound":
            True,

        "graph_is_lineage_traceable":
            True,

        "graph_preserves_historical_versions":
            True,

        "graph_preserves_claim_integrity":
            True,

        "graph_preserves_authority":
            True,

        "graph_preserves_conflict":
            True,

        "graph_preserves_guard_state":
            True,

        "graph_preserves_active_target_set_ownership":
            True,

        "graph_target_references_are_reference_only":
            True,

        "graph_does_not_select_final_external_target":
            True,

        "graph_does_not_write_semantic_memory":
            True,

        "graph_does_not_execute_learning":
            True,

        "graph_does_not_execute_reasoning":
            True,

        "graph_does_not_make_linking_decisions":
            True,

        "graph_does_not_create_editor_highlights":
            True,

        "upstream_truth_rewritten":
            False,

        "downstream_consumption_authorized":
            True,

        "next_semantic_intelligence_component":
            "LEARNING_ENGINE",
    }

    final_package = {
        "schema":
            "final_dynamic_semantic_graph_package_v1",

        "final_graph_id":
            final_graph_id,

        "final_graph_digest":
            final_graph_digest,

        "graph_snapshot_id":
            graph_snapshot_id,

        "graph_snapshot_digest":
            graph_snapshot_digest,

        "lineage_root_id":
            lineage_root_id,

        "lineage_root_digest":
            lineage_root_digest,

        "node_count":
            len(nodes),

        "edge_count":
            len(edges),

        "historical_version_count":
            len(history),

        "canonical_graph_nodes":
            copy.deepcopy(
                nodes
            ),

        "canonical_graph_edges":
            copy.deepcopy(
                edges
            ),

        "historical_object_versions":
            copy.deepcopy(
                history
            ),

        "active_object_lineage":
            copy.deepcopy(
                active_lineage
            ),

        "historical_lineage":
            copy.deepcopy(
                historical_lineage
            ),

        "graph_snapshot":
            copy.deepcopy(
                graph_snapshot
            ),

        "lineage_report":
            copy.deepcopy(
                lineage_report
            ),

        "merge_report":
            copy.deepcopy(
                merge_report
            ),

        "downstream_contract":
            copy.deepcopy(
                downstream_contract
            ),

        "preservation_contract":
            copy.deepcopy(
                preservation_contract
            ),

        "architecture":
            copy.deepcopy(
                architecture
            ),

        "scope_mutation_contract":
            copy.deepcopy(
                scope_mutation_contract
            ),

        "final_policy":
            "CERTIFIED_DYNAMIC_SEMANTIC_GRAPH_FOR_DOWNSTREAM_CONSUMPTION",
    }

    return {
        "schema":
            "final_dynamic_semantic_graph_result_v1",

        "dynamic_semantic_graph_version":
            DYNAMIC_SEMANTIC_GRAPH_VERSION,

        "phase":
            DYNAMIC_SEMANTIC_GRAPH_PHASE,

        "patch":
            "4.6.26L",

        "status":
            "FINAL_DYNAMIC_SEMANTIC_GRAPH_RESULT_BUILT",

        "final_graph_id":
            final_graph_id,

        "final_graph_digest":
            final_graph_digest,

        "graph_snapshot_id":
            graph_snapshot_id,

        "graph_snapshot_digest":
            graph_snapshot_digest,

        "lineage_root_id":
            lineage_root_id,

        "lineage_root_digest":
            lineage_root_digest,

        "node_count":
            len(nodes),

        "edge_count":
            len(edges),

        "historical_version_count":
            len(history),

        "final_dynamic_semantic_graph_package":
            final_package,

        "downstream_contract":
            downstream_contract,

        "validated_graph_intake_records":
            copy.deepcopy(
                validated_records
            ),

        "final_claim_integrity_package":
            copy.deepcopy(
                final_claim_integrity_package
            ),

        "preservation_contract":
            copy.deepcopy(
                preservation_contract
            ),

        "processing_boundaries": {
            "final_dynamic_graph_result_built":
                True,

            "final_dynamic_graph_package_built":
                True,

            "downstream_contract_built":
                True,

            "graph_node_creation_performed":
                False,

            "graph_edge_creation_performed":
                False,

            "graph_mutation_performed":
                False,

            "graph_merge_performed":
                False,

            "support_reassessment_performed":
                False,

            "conflict_redetection_performed":
                False,

            "conflict_reclassification_performed":
                False,

            "integrity_redecision_performed":
                False,

            "guard_redisposition_performed":
                False,

            "authority_rescoring_performed":
                False,

            "authority_reclassification_performed":
                False,

            "semantic_memory_written":
                False,

            "learning_performed":
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

            "unsupported_node_invention_performed":
                False,

            "unsupported_edge_invention_performed":
                False,

            "upstream_truth_rewritten":
                False,
        },

        "policy":
            "CERTIFIED_FINAL_DYNAMIC_SEMANTIC_GRAPH_RESULT",

        "next":
            "full_dynamic_semantic_graph_hard_certification",
    }

def certify_full_dynamic_semantic_graph_v1(
    final_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.26M ? Full Dynamic Semantic Graph Hard Certification.

    Performs the final certification gate over the complete
    4.6.26A -> 4.6.26L Dynamic Semantic Graph implementation.

    Certification only.

    No semantic state, graph object, target, memory, learning,
    reasoning, linking decision, or editor highlight is changed.
    """

    if not isinstance(
        final_result,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "final_result must be a dictionary."
        )

    expected_lifecycle = {
        "schema":
            "final_dynamic_semantic_graph_result_v1",

        "dynamic_semantic_graph_version":
            DYNAMIC_SEMANTIC_GRAPH_VERSION,

        "phase":
            DYNAMIC_SEMANTIC_GRAPH_PHASE,

        "patch":
            "4.6.26L",

        "status":
            "FINAL_DYNAMIC_SEMANTIC_GRAPH_RESULT_BUILT",

        "policy":
            "CERTIFIED_FINAL_DYNAMIC_SEMANTIC_GRAPH_RESULT",

        "next":
            "full_dynamic_semantic_graph_hard_certification",
    }

    for key, expected in expected_lifecycle.items():

        if final_result.get(key) != expected:
            raise DynamicSemanticGraphError(
                "Invalid 4.6.26L lifecycle field: "
                f"{key}"
            )

    required_stage_functions = (
        "inspect_certified_claim_integrity_input_v1",
        "define_dynamic_graph_architecture_v1",
        "validate_graph_intake_v1",
        "define_graph_scope_and_mutation_contract_v1",
        "construct_canonical_graph_nodes_v1",
        "construct_canonical_graph_edges_v1",
        "integrate_claim_evidence_authority_graph_v1",
        "project_conflict_and_integrity_graph_v1",
        "validate_graph_consistency_and_referential_integrity_v1",
        "update_and_merge_dynamic_semantic_graph_v1",
        "build_graph_provenance_and_lineage_trace_v1",
        "build_final_dynamic_semantic_graph_result_v1",
    )

    for function_name in required_stage_functions:

        function_object = globals().get(
            function_name
        )

        if not callable(function_object):
            raise DynamicSemanticGraphError(
                "Dynamic Semantic Graph stage function missing: "
                f"{function_name}"
            )

    package = final_result.get(
        "final_dynamic_semantic_graph_package"
    )

    downstream = final_result.get(
        "downstream_contract"
    )

    preservation = final_result.get(
        "preservation_contract"
    )

    boundaries = final_result.get(
        "processing_boundaries"
    )

    if not isinstance(package, dict):
        raise DynamicSemanticGraphError(
            "Final Dynamic Semantic Graph package is missing."
        )

    if (
        package.get("schema")
        != "final_dynamic_semantic_graph_package_v1"
    ):
        raise DynamicSemanticGraphError(
            "Invalid final graph package schema."
        )

    if (
        package.get("final_policy")
        != "CERTIFIED_DYNAMIC_SEMANTIC_GRAPH_FOR_DOWNSTREAM_CONSUMPTION"
    ):
        raise DynamicSemanticGraphError(
            "Invalid final graph package policy."
        )

    if not isinstance(downstream, dict):
        raise DynamicSemanticGraphError(
            "downstream_contract must be a dictionary."
        )

    if (
        downstream.get("schema")
        != "dynamic_semantic_graph_downstream_contract_v1"
    ):
        raise DynamicSemanticGraphError(
            "Invalid downstream contract schema."
        )

    if not isinstance(
        preservation,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "preservation_contract must be a dictionary."
        )

    if not isinstance(
        boundaries,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "processing_boundaries must be a dictionary."
        )

    final_graph_id = final_result.get(
        "final_graph_id"
    )

    final_graph_digest = final_result.get(
        "final_graph_digest"
    )

    graph_snapshot_id = final_result.get(
        "graph_snapshot_id"
    )

    graph_snapshot_digest = final_result.get(
        "graph_snapshot_digest"
    )

    lineage_root_id = final_result.get(
        "lineage_root_id"
    )

    lineage_root_digest = final_result.get(
        "lineage_root_digest"
    )

    if (
        not isinstance(final_graph_id, str)
        or not final_graph_id.startswith(
            "dynamicgraphfinal:v1:"
        )
    ):
        raise DynamicSemanticGraphError(
            "Invalid final graph ID."
        )

    if (
        not isinstance(final_graph_digest, str)
        or len(final_graph_digest) != 64
    ):
        raise DynamicSemanticGraphError(
            "Invalid final graph digest."
        )

    if (
        not isinstance(graph_snapshot_id, str)
        or not graph_snapshot_id.startswith(
            "graphsnapshot:v1:"
        )
    ):
        raise DynamicSemanticGraphError(
            "Invalid graph snapshot ID."
        )

    if (
        not isinstance(graph_snapshot_digest, str)
        or len(graph_snapshot_digest) != 64
    ):
        raise DynamicSemanticGraphError(
            "Invalid graph snapshot digest."
        )

    if (
        not isinstance(lineage_root_id, str)
        or not lineage_root_id.startswith(
            "graphlineageroot:v1:"
        )
    ):
        raise DynamicSemanticGraphError(
            "Invalid lineage root ID."
        )

    if (
        not isinstance(lineage_root_digest, str)
        or len(lineage_root_digest) != 64
    ):
        raise DynamicSemanticGraphError(
            "Invalid lineage root digest."
        )

    for key in (
        "final_graph_id",
        "final_graph_digest",
        "graph_snapshot_id",
        "graph_snapshot_digest",
        "lineage_root_id",
        "lineage_root_digest",
    ):

        if package.get(key) != final_result.get(key):
            raise DynamicSemanticGraphError(
                "Final package identity drift: "
                f"{key}"
            )

    nodes = package.get(
        "canonical_graph_nodes"
    )

    edges = package.get(
        "canonical_graph_edges"
    )

    history = package.get(
        "historical_object_versions"
    )

    active_lineage = package.get(
        "active_object_lineage"
    )

    historical_lineage = package.get(
        "historical_lineage"
    )

    graph_snapshot = package.get(
        "graph_snapshot"
    )

    lineage_report = package.get(
        "lineage_report"
    )

    architecture = package.get(
        "architecture"
    )

    if not isinstance(nodes, list):
        raise DynamicSemanticGraphError(
            "Final graph nodes must be a list."
        )

    if not isinstance(edges, list):
        raise DynamicSemanticGraphError(
            "Final graph edges must be a list."
        )

    if not isinstance(history, list):
        raise DynamicSemanticGraphError(
            "Historical versions must be a list."
        )

    if not isinstance(
        active_lineage,
        list,
    ):
        raise DynamicSemanticGraphError(
            "Active lineage must be a list."
        )

    if not isinstance(
        historical_lineage,
        list,
    ):
        raise DynamicSemanticGraphError(
            "Historical lineage must be a list."
        )

    if not isinstance(
        graph_snapshot,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "Graph snapshot must be a dictionary."
        )

    if not isinstance(
        lineage_report,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "Lineage report must be a dictionary."
        )

    if not isinstance(
        architecture,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "Graph architecture must be a dictionary."
        )

    if (
        final_result.get("node_count")
        != len(nodes)
    ):
        raise DynamicSemanticGraphError(
            "Final graph node count mismatch."
        )

    if (
        final_result.get("edge_count")
        != len(edges)
    ):
        raise DynamicSemanticGraphError(
            "Final graph edge count mismatch."
        )

    if (
        final_result.get(
            "historical_version_count"
        )
        != len(history)
    ):
        raise DynamicSemanticGraphError(
            "Final historical version count mismatch."
        )

    if (
        len(active_lineage)
        != len(nodes)
        + len(edges)
    ):
        raise DynamicSemanticGraphError(
            "Final active lineage coverage mismatch."
        )

    if len(
        historical_lineage
    ) != len(history):
        raise DynamicSemanticGraphError(
            "Final historical lineage coverage mismatch."
        )

    node_ids = set()

    for node in nodes:

        if (
            not isinstance(node, dict)
            or node.get("schema")
            != "dynamic_semantic_graph_node_v1"
        ):
            raise DynamicSemanticGraphError(
                "Invalid final graph node."
            )

        node_id = node.get(
            "node_id"
        )

        if (
            not isinstance(node_id, str)
            or not node_id.startswith(
                "graphnode:v1:"
            )
        ):
            raise DynamicSemanticGraphError(
                "Invalid final graph node ID."
            )

        if node_id in node_ids:
            raise DynamicSemanticGraphError(
                "Duplicate final graph node ID."
            )

        if node.get(
            "canonical_identity_deterministic"
        ) is not True:
            raise DynamicSemanticGraphError(
                "Final graph node identity is not deterministic."
            )

        if node.get(
            "certified_input_backed"
        ) is not True:
            raise DynamicSemanticGraphError(
                "Final graph node is not certified-input-backed."
            )

        if node.get(
            "unsupported_invention_performed"
        ) is not False:
            raise DynamicSemanticGraphError(
                "Unsupported final graph node invention detected."
            )

        node_ids.add(
            node_id
        )

    edge_ids = set()

    for edge in edges:

        if (
            not isinstance(edge, dict)
            or edge.get("schema")
            != "dynamic_semantic_graph_edge_v1"
        ):
            raise DynamicSemanticGraphError(
                "Invalid final graph edge."
            )

        edge_id = edge.get(
            "edge_id"
        )

        if (
            not isinstance(edge_id, str)
            or not edge_id.startswith(
                "graphedge:v1:"
            )
        ):
            raise DynamicSemanticGraphError(
                "Invalid final graph edge ID."
            )

        if edge_id in edge_ids:
            raise DynamicSemanticGraphError(
                "Duplicate final graph edge ID."
            )

        if edge.get(
            "from_node_id"
        ) not in node_ids:
            raise DynamicSemanticGraphError(
                "Final graph edge has missing from-node."
            )

        if edge.get(
            "to_node_id"
        ) not in node_ids:
            raise DynamicSemanticGraphError(
                "Final graph edge has missing to-node."
            )

        if edge.get(
            "canonical_identity_deterministic"
        ) is not True:
            raise DynamicSemanticGraphError(
                "Final graph edge identity is not deterministic."
            )

        if edge.get(
            "certified_relationship_backed"
        ) is not True:
            raise DynamicSemanticGraphError(
                "Final graph edge is not certified-relationship-backed."
            )

        if edge.get(
            "unsupported_invention_performed"
        ) is not False:
            raise DynamicSemanticGraphError(
                "Unsupported final graph edge invention detected."
            )

        edge_ids.add(
            edge_id
        )

    if (
        graph_snapshot.get("schema")
        != "dynamic_semantic_graph_snapshot_v1"
    ):
        raise DynamicSemanticGraphError(
            "Invalid final graph snapshot schema."
        )

    if graph_snapshot.get(
        "referential_integrity_preserved"
    ) is not True:
        raise DynamicSemanticGraphError(
            "Final graph snapshot lost referential integrity."
        )

    if graph_snapshot.get(
        "historical_trace_preserved"
    ) is not True:
        raise DynamicSemanticGraphError(
            "Final graph snapshot lost historical trace."
        )

    if graph_snapshot.get(
        "upstream_truth_rewritten"
    ) is not False:
        raise DynamicSemanticGraphError(
            "Final graph snapshot rewrote upstream truth."
        )

    if lineage_report.get(
        "lineage_complete"
    ) is not True:
        raise DynamicSemanticGraphError(
            "Final graph lineage is incomplete."
        )

    if lineage_report.get(
        "every_active_graph_object_traced"
    ) is not True:
        raise DynamicSemanticGraphError(
            "Not every active graph object is lineage-traced."
        )

    if lineage_report.get(
        "historical_versions_traced"
    ) is not True:
        raise DynamicSemanticGraphError(
            "Historical graph versions are not fully traced."
        )

    if lineage_report.get(
        "upstream_truth_rewritten"
    ) is not False:
        raise DynamicSemanticGraphError(
            "Lineage indicates upstream truth rewrite."
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
            raise DynamicSemanticGraphError(
                "Full certification preservation drift: "
                f"{flag}"
            )

    target_ownership = architecture.get(
        "target_ownership"
    )

    if not isinstance(
        target_ownership,
        dict,
    ):
        raise DynamicSemanticGraphError(
            "Target ownership contract is missing."
        )

    expected_target_contract = {
        "canonical_target_owner":
            "ACTIVE_TARGET_SET",

        "external_partition":
            "EXTERNAL_AUTHORITY",

        "external_route":
            "EXTERNAL",

        "final_external_selection_owner":
            "EXTERNAL_TARGET_RESOLVER",

        "dynamic_graph_may_create_target":
            False,

        "dynamic_graph_may_select_final_target":
            False,

        "dynamic_graph_target_nodes_are_references_only":
            True,
    }

    for key, expected in expected_target_contract.items():

        if target_ownership.get(key) != expected:
            raise DynamicSemanticGraphError(
                "Full certification target ownership drift: "
                f"{key}"
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
            raise DynamicSemanticGraphError(
                "Full certification downstream contract drift: "
                f"{flag}"
            )

    if downstream.get(
        "upstream_truth_rewritten"
    ) is not False:
        raise DynamicSemanticGraphError(
            "Downstream contract permits upstream truth rewrite."
        )

    if (
        downstream.get(
            "next_semantic_intelligence_component"
        )
        != "LEARNING_ENGINE"
    ):
        raise DynamicSemanticGraphError(
            "Dynamic Semantic Graph downstream handoff drift."
        )

    required_boundary_true = (
        "final_dynamic_graph_result_built",
        "final_dynamic_graph_package_built",
        "downstream_contract_built",
    )

    for flag in required_boundary_true:

        if boundaries.get(flag) is not True:
            raise DynamicSemanticGraphError(
                "Final result boundary missing: "
                f"{flag}"
            )

    required_boundary_false = (
        "graph_node_creation_performed",
        "graph_edge_creation_performed",
        "graph_mutation_performed",
        "graph_merge_performed",
        "support_reassessment_performed",
        "conflict_redetection_performed",
        "conflict_reclassification_performed",
        "integrity_redecision_performed",
        "guard_redisposition_performed",
        "authority_rescoring_performed",
        "authority_reclassification_performed",
        "semantic_memory_written",
        "learning_performed",
        "reasoning_performed",
        "external_target_created",
        "external_target_selected",
        "linking_decisions_performed",
        "highlights_created",
        "unsupported_node_invention_performed",
        "unsupported_edge_invention_performed",
        "upstream_truth_rewritten",
    )

    for flag in required_boundary_false:

        if boundaries.get(flag) is not False:
            raise DynamicSemanticGraphError(
                "Final result forbidden side effect detected: "
                f"{flag}"
            )

    stage_chain = (
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

    return {
        "schema":
            "full_dynamic_semantic_graph_hard_certification_result_v1",

        "dynamic_semantic_graph_version":
            DYNAMIC_SEMANTIC_GRAPH_VERSION,

        "phase":
            DYNAMIC_SEMANTIC_GRAPH_PHASE,

        "patch":
            "4.6.26M",

        "status":
            "DYNAMIC_SEMANTIC_GRAPH_FULL_HARD_CERTIFIED",

        "certified_stage_chain":
            stage_chain,

        "certified_stage_count":
            len(stage_chain),

        "final_graph_id":
            final_graph_id,

        "final_graph_digest":
            final_graph_digest,

        "graph_snapshot_id":
            graph_snapshot_id,

        "graph_snapshot_digest":
            graph_snapshot_digest,

        "lineage_root_id":
            lineage_root_id,

        "lineage_root_digest":
            lineage_root_digest,

        "final_package_schema":
            package.get(
                "schema"
            ),

        "final_package_policy":
            package.get(
                "final_policy"
            ),

        "preservation_certified":
            True,

        "referential_integrity_certified":
            True,

        "dynamic_versioning_certified":
            True,

        "historical_trace_certified":
            True,

        "provenance_lineage_certified":
            True,

        "target_ownership_certified":
            True,

        "no_truth_rewrite_certified":
            True,

        "no_semantic_memory_write_certified":
            True,

        "no_learning_execution_certified":
            True,

        "no_reasoning_execution_certified":
            True,

        "no_target_selection_certified":
            True,

        "no_linking_decision_certified":
            True,

        "downstream_handoff":
            "LEARNING_ENGINE",

        "policy":
            "CERTIFIED_FULL_DYNAMIC_SEMANTIC_GRAPH_V1",

        "next":
            "learning_engine",
    }
