from __future__ import annotations

import copy
import hashlib
import json
from typing import Any


EXPLAINABILITY_VERSION = "explainability_v1"
EXPLAINABILITY_PHASE = "4.6.29"


class ExplainabilityError(ValueError):
    pass

def inspect_certified_semantic_memory_input_v1(
    semantic_memory_certification: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.29A ? Certified Semantic Memory Input Inspection.

    Accepts only the fully hard-certified 4.6.28 Semantic Memory
    handoff.

    This stage performs inspection only.

    It does not:
    - persist Semantic Memory,
    - retrieve Semantic Memory,
    - mutate Semantic Memory,
    - promote memory to truth,
    - mutate the Learning Engine,
    - mutate the Dynamic Semantic Graph,
    - rescore Authority,
    - redecide Claim Integrity,
    - reclassify conflict,
    - rewrite upstream guard state,
    - create/select/score targets,
    - perform runtime reasoning,
    - make linking decisions,
    - create highlights,
    - generate explanations yet.
    """

    if not isinstance(
        semantic_memory_certification,
        dict,
    ):
        raise ExplainabilityError(
            "semantic_memory_certification must be a dictionary."
        )

    expected = {
        "schema":
            "full_semantic_memory_hard_certification_result_v1",

        "semantic_memory_version":
            "semantic_memory_v1",

        "phase":
            "4.6.28",

        "patch":
            "4.6.28M",

        "status":
            "FULL_SEMANTIC_MEMORY_HARD_CERTIFIED",

        "certified":
            True,

        "stage_count":
            13,

        "certification_policy":
            "FULL_END_TO_END_SEMANTIC_MEMORY_HARD_CERTIFICATION",

        "next":
            "explainability",
    }

    for key, expected_value in expected.items():

        if (
            semantic_memory_certification.get(
                key
            )
            != expected_value
        ):
            raise ExplainabilityError(
                "Invalid certified Semantic Memory handoff field: "
                f"{key}"
            )

    final_result = (
        semantic_memory_certification.get(
            "final_semantic_memory_result"
        )
    )

    if not isinstance(
        final_result,
        dict,
    ):
        raise ExplainabilityError(
            "Certified final Semantic Memory result is missing."
        )

    if (
        final_result.get("schema")
        != "final_semantic_memory_result_v1"
    ):
        raise ExplainabilityError(
            "Invalid final Semantic Memory result schema."
        )

    if (
        final_result.get("status")
        != "FINAL_SEMANTIC_MEMORY_RESULT_BUILT"
    ):
        raise ExplainabilityError(
            "Final Semantic Memory result is not complete."
        )

    final_package = final_result.get(
        "final_semantic_memory_package"
    )

    if not isinstance(
        final_package,
        dict,
    ):
        raise ExplainabilityError(
            "Final Semantic Memory package is missing."
        )

    if (
        final_package.get("schema")
        != "final_semantic_memory_package_v1"
    ):
        raise ExplainabilityError(
            "Invalid final Semantic Memory package schema."
        )

    if (
        final_package.get("final_policy")
        != "CERTIFIED_FINAL_SEMANTIC_MEMORY_FOR_PERSISTENCE_AND_DOWNSTREAM_READ_HANDOFF"
    ):
        raise ExplainabilityError(
            "Invalid final Semantic Memory package policy."
        )

    for flag in (
        "semantic_memory_complete",
        "persistence_contract_ready",
        "runtime_read_contract_ready",
        "explainability_handoff_ready",
    ):
        if final_package.get(flag) is not True:
            raise ExplainabilityError(
                "Semantic Memory is not ready for Explainability: "
                f"{flag}"
            )

    for flag in (
        "semantic_memory_written",
        "memory_persisted",
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
    ):
        if final_package.get(flag) is not False:
            raise ExplainabilityError(
                "Unsafe certified Semantic Memory package state: "
                f"{flag}"
            )

    for flag in (
        "persistence_contract_ready",
        "runtime_read_contract_ready",
        "explainability_handoff_ready",
    ):
        if (
            semantic_memory_certification.get(
                flag
            )
            is not True
        ):
            raise ExplainabilityError(
                "Semantic Memory certification handoff is incomplete: "
                f"{flag}"
            )

    for flag in (
        "semantic_memory_written",
        "memory_persistence_performed",
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
        "memory_is_certified_truth",
        "memory_is_learned_truth",
    ):
        if (
            semantic_memory_certification.get(
                flag
            )
            is not False
        ):
            raise ExplainabilityError(
                "Unsafe certified Semantic Memory handoff state: "
                f"{flag}"
            )

    package_id = final_package.get(
        "final_semantic_memory_package_id"
    )

    package_digest = final_package.get(
        "final_semantic_memory_package_digest"
    )

    lineage_root_id = final_package.get(
        "semantic_memory_lineage_root_id"
    )

    for name, value in (
        (
            "final_semantic_memory_package_id",
            package_id,
        ),
        (
            "final_semantic_memory_package_digest",
            package_digest,
        ),
        (
            "semantic_memory_lineage_root_id",
            lineage_root_id,
        ),
    ):

        if (
            not isinstance(
                value,
                str,
            )
            or not value
        ):
            raise ExplainabilityError(
                "Missing certified Semantic Memory identity: "
                f"{name}"
            )

    if (
        semantic_memory_certification.get(
            "final_semantic_memory_package_id"
        )
        != package_id
    ):
        raise ExplainabilityError(
            "Semantic Memory package ID mismatch."
        )

    if (
        semantic_memory_certification.get(
            "final_semantic_memory_package_digest"
        )
        != package_digest
    ):
        raise ExplainabilityError(
            "Semantic Memory package digest mismatch."
        )

    if (
        semantic_memory_certification.get(
            "semantic_memory_lineage_root_id"
        )
        != lineage_root_id
    ):
        raise ExplainabilityError(
            "Semantic Memory lineage root mismatch."
        )

    final_memory_objects = final_package.get(
        "final_memory_objects"
    )

    if not isinstance(
        final_memory_objects,
        tuple,
    ):
        raise ExplainabilityError(
            "final_memory_objects must be a tuple."
        )

    if not final_memory_objects:
        raise ExplainabilityError(
            "Certified Semantic Memory package cannot be empty."
        )

    object_ids = []

    for memory_object in final_memory_objects:

        if not isinstance(
            memory_object,
            dict,
        ):
            raise ExplainabilityError(
                "Semantic Memory object must be a dictionary."
            )

        if (
            memory_object.get("schema")
            != "semantic_memory_object_v1"
        ):
            raise ExplainabilityError(
                "Invalid Semantic Memory object schema."
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
            raise ExplainabilityError(
                "Semantic Memory object ID is missing."
            )

        object_ids.append(
            memory_object_id
        )

        for flag in (
            "provenance_complete",
            "lineage_complete",
            "retention_decision_finalized",
            "final_semantic_memory_member",
        ):
            if memory_object.get(flag) is not True:
                raise ExplainabilityError(
                    "Semantic Memory object is incomplete: "
                    f"{flag}"
                )

        for flag in (
            "memory_persisted",
            "retrieval_performed",
            "is_certified_fact",
            "is_learned_truth",
        ):
            if memory_object.get(flag) is not False:
                raise ExplainabilityError(
                    "Unsafe Semantic Memory object state: "
                    f"{flag}"
                )

    if len(
        object_ids
    ) != len(
        set(object_ids)
    ):
        raise ExplainabilityError(
            "Duplicate Semantic Memory object IDs."
        )

    inspection_payload = {
        "source_semantic_memory_package_id":
            package_id,

        "source_semantic_memory_package_digest":
            package_digest,

        "source_semantic_memory_lineage_root_id":
            lineage_root_id,

        "memory_object_ids":
            list(
                object_ids
            ),

        "source_certification_status":
            semantic_memory_certification[
                "status"
            ],
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
            "explainability_semantic_memory_input_inspection_result_v1",

        "explainability_version":
            EXPLAINABILITY_VERSION,

        "phase":
            EXPLAINABILITY_PHASE,

        "patch":
            "4.6.29A",

        "status":
            "CERTIFIED_SEMANTIC_MEMORY_INPUT_INSPECTED",

        "inspection_id":
            "explainabilityinput:v1:"
            + inspection_digest,

        "inspection_digest":
            inspection_digest,

        "source_semantic_memory_certification_schema":
            semantic_memory_certification[
                "schema"
            ],

        "source_semantic_memory_certification_status":
            semantic_memory_certification[
                "status"
            ],

        "source_semantic_memory_package_id":
            package_id,

        "source_semantic_memory_package_digest":
            package_digest,

        "source_semantic_memory_lineage_root_id":
            lineage_root_id,

        "source_memory_object_ids":
            tuple(
                object_ids
            ),

        "source_memory_object_count":
            len(
                object_ids
            ),

        "certified_semantic_memory_input":
            copy.deepcopy(
                semantic_memory_certification
            ),

        "processing_boundaries": {
            "certified_semantic_memory_inspected":
                True,

            "explanation_generated":
                False,

            "explanation_reasoning_performed":
                False,

            "semantic_memory_written":
                False,

            "semantic_memory_mutated":
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
        },

        "policy":
            "CERTIFIED_SEMANTIC_MEMORY_INPUT_ONLY",

        "next":
            "explainability_architecture_definition",
    }

def define_explainability_architecture_v1(
    inspection_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.29B ? Explainability Architecture Definition.

    Defines the canonical Explainability architecture from the
    certified Semantic Memory handoff.

    Architecture only:
    no explanation content is generated,
    no reasoning is performed,
    no semantic state is changed.
    """

    if not isinstance(
        inspection_result,
        dict,
    ):
        raise ExplainabilityError(
            "inspection_result must be a dictionary."
        )

    expected = {
        "schema":
            "explainability_semantic_memory_input_inspection_result_v1",

        "explainability_version":
            EXPLAINABILITY_VERSION,

        "phase":
            EXPLAINABILITY_PHASE,

        "patch":
            "4.6.29A",

        "status":
            "CERTIFIED_SEMANTIC_MEMORY_INPUT_INSPECTED",

        "policy":
            "CERTIFIED_SEMANTIC_MEMORY_INPUT_ONLY",

        "next":
            "explainability_architecture_definition",
    }

    for key, expected_value in expected.items():

        if inspection_result.get(key) != expected_value:
            raise ExplainabilityError(
                "Invalid 4.6.29A lifecycle field: "
                f"{key}"
            )

    certified_input = inspection_result.get(
        "certified_semantic_memory_input"
    )

    boundaries = inspection_result.get(
        "processing_boundaries"
    )

    if not isinstance(
        certified_input,
        dict,
    ):
        raise ExplainabilityError(
            "Certified Semantic Memory input is missing."
        )

    if not isinstance(
        boundaries,
        dict,
    ):
        raise ExplainabilityError(
            "4.6.29A processing boundaries are missing."
        )

    if (
        certified_input.get("schema")
        != "full_semantic_memory_hard_certification_result_v1"
    ):
        raise ExplainabilityError(
            "Invalid Semantic Memory certification schema."
        )

    if certified_input.get(
        "certified"
    ) is not True:
        raise ExplainabilityError(
            "Semantic Memory input is not certified."
        )

    if (
        certified_input.get("status")
        != "FULL_SEMANTIC_MEMORY_HARD_CERTIFIED"
    ):
        raise ExplainabilityError(
            "Semantic Memory hard certification is incomplete."
        )

    if certified_input.get(
        "explainability_handoff_ready"
    ) is not True:
        raise ExplainabilityError(
            "Semantic Memory is not ready for Explainability."
        )

    if boundaries.get(
        "certified_semantic_memory_inspected"
    ) is not True:
        raise ExplainabilityError(
            "Certified Semantic Memory was not inspected."
        )

    for flag in (
        "explanation_generated",
        "explanation_reasoning_performed",
        "semantic_memory_written",
        "semantic_memory_mutated",
        "memory_persistence_performed",
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
            raise ExplainabilityError(
                "Unsafe Explainability architecture input state: "
                f"{flag}"
            )

    source_package_id = inspection_result.get(
        "source_semantic_memory_package_id"
    )

    source_package_digest = inspection_result.get(
        "source_semantic_memory_package_digest"
    )

    source_lineage_root_id = inspection_result.get(
        "source_semantic_memory_lineage_root_id"
    )

    source_memory_object_ids = inspection_result.get(
        "source_memory_object_ids"
    )

    source_memory_object_count = inspection_result.get(
        "source_memory_object_count"
    )

    for name, value in (
        (
            "source_semantic_memory_package_id",
            source_package_id,
        ),
        (
            "source_semantic_memory_package_digest",
            source_package_digest,
        ),
        (
            "source_semantic_memory_lineage_root_id",
            source_lineage_root_id,
        ),
    ):
        if not isinstance(
            value,
            str,
        ) or not value:
            raise ExplainabilityError(
                "Missing Explainability architecture source: "
                f"{name}"
            )

    if not isinstance(
        source_memory_object_ids,
        tuple,
    ):
        raise ExplainabilityError(
            "source_memory_object_ids must be a tuple."
        )

    if (
        not isinstance(
            source_memory_object_count,
            int,
        )
        or source_memory_object_count <= 0
    ):
        raise ExplainabilityError(
            "Invalid source memory object count."
        )

    if len(
        source_memory_object_ids
    ) != source_memory_object_count:
        raise ExplainabilityError(
            "Source memory object count mismatch."
        )

    if len(
        source_memory_object_ids
    ) != len(
        set(source_memory_object_ids)
    ):
        raise ExplainabilityError(
            "Duplicate source Semantic Memory object IDs."
        )

    architecture = {
        "schema":
            "explainability_architecture_v1",

        "central_question":
            "HOW_SHOULD_CERTIFIED_SEMANTIC_STATE_BE_EXPLAINED_WITH_PROVENANCE_UNCERTAINTY_CONFLICT_AND_DECISION_TRACE_PRESERVED_WITHOUT_CREATING_NEW_SEMANTIC_TRUTH_OR_DECISIONS",

        "architecture_policy":
            "TRACEABLE_AUDIENCE_AWARE_NON_DECISIONAL_EXPLANATION_OF_CERTIFIED_SEMANTIC_STATE",

        "canonical_owner":
            "EXPLAINABILITY",

        "canonical_input_owner":
            "SEMANTIC_MEMORY",

        "source_of_explainable_state":
            "CERTIFIED_SEMANTIC_MEMORY",

        "explanation_surfaces":
            (
                "USER_FACING_EXPLANATION",
                "DEVELOPER_EXPLANATION",
                "AUDIT_EXPLANATION",
                "DECISION_TRACE_EXPLANATION",
            ),

        "explanation_components":
            (
                "EXPLANATION_SCOPE",
                "AUDIENCE",
                "SOURCE_MEMORY_REFERENCE",
                "PROVENANCE",
                "LINEAGE",
                "EVIDENCE_CONTEXT",
                "AUTHORITY_CONTEXT",
                "CONFLICT_CONTEXT",
                "EXCEPTION_CONTEXT",
                "STABILITY_STATE",
                "RETENTION_STATE",
                "RETRIEVAL_CLASS",
                "UNCERTAINTY",
                "DECISION_TRACE",
                "BOUNDARY_DISCLOSURE",
            ),

        "audience_classes":
            (
                "END_USER",
                "DEVELOPER",
                "AUDITOR",
                "OWNER_OPERATOR",
            ),

        "explanation_scope_classes":
            (
                "MEMORY_OBJECT",
                "RELATIONSHIP",
                "EVIDENCE",
                "PROVENANCE",
                "CONFLICT_EXCEPTION",
                "STABILITY_RETENTION",
                "RETRIEVAL_STATE",
                "DECISION_TRACE",
            ),

        "explanation_fidelity_principles":
            (
                "EXPLAIN_ONLY_CERTIFIED_AVAILABLE_STATE",
                "PRESERVE_SOURCE_MEMORY_IDENTITY",
                "PRESERVE_PROVENANCE",
                "PRESERVE_LINEAGE",
                "PRESERVE_VERSION_CONTEXT",
                "PRESERVE_CONFLICT_CONTEXT",
                "PRESERVE_EXCEPTION_CONTEXT",
                "PRESERVE_STABILITY_CONTEXT",
                "PRESERVE_RETENTION_CONTEXT",
                "PRESERVE_RETRIEVAL_CLASS",
                "PRESERVE_UNCERTAINTY",
                "DISTINGUISH_OBSERVED_STATE_FROM_INTERPRETATION",
                "DISTINGUISH_MEMORY_FROM_TRUTH",
                "DISTINGUISH_EXPLANATION_FROM_DECISION",
                "NO_UNSUPPORTED_CAUSAL_CLAIMS",
                "NO_HIDDEN_STATE_PROMOTION",
            ),

        "explanation_generation_rules":
            (
                "EXPLANATIONS_MUST_REFERENCE_SOURCE_MEMORY",
                "EXPLANATIONS_MUST_BE_TRACEABLE",
                "EXPLANATIONS_MUST_PRESERVE_STATE_LABELS",
                "CONTESTED_MEMORY_MUST_BE_EXPLAINED_AS_CONTESTED",
                "HELD_MEMORY_MUST_BE_EXPLAINED_AS_HELD",
                "BLOCKED_MEMORY_MUST_BE_EXPLAINED_AS_BLOCKED",
                "HISTORICAL_MEMORY_MUST_BE_EXPLAINED_AS_HISTORICAL",
                "UNCERTAINTY_MUST_NOT_BE_HIDDEN",
                "CONFLICT_MUST_NOT_BE_SILENTLY_RESOLVED",
                "EXCEPTIONS_MUST_NOT_BE_NORMALIZED_AWAY",
                "AUDIENCE_DETAIL_MAY_CHANGE",
                "SEMANTIC_MEANING_MUST_NOT_CHANGE_BY_AUDIENCE",
            ),

        "decision_trace_rules":
            (
                "TRACE_EXISTING_CERTIFIED_STATE_ONLY",
                "DO_NOT_CREATE_A_NEW_DECISION",
                "DO_NOT_INFER_MISSING_UPSTREAM_DECISIONS",
                "PRESERVE_COMPONENT_IDENTITIES",
                "PRESERVE_ORDER_WHEN_ORDER_IS_CERTIFIED",
                "DISCLOSE_UNAVAILABLE_TRACE_COMPONENTS",
            ),

        "truth_separation":
            {
                "explanation_is_certified_truth":
                    False,

                "explanation_is_learned_truth":
                    False,

                "semantic_memory_is_promoted_to_truth":
                    False,

                "explanation_can_adjudicate_truth":
                    False,

                "explanation_can_rewrite_semantic_state":
                    False,

                "explanation_can_resolve_conflict":
                    False,

                "explanation_can_override_uncertainty":
                    False,
            },

        "ownership_contract":
            {
                "explanation_structure":
                    "EXPLAINABILITY",

                "explanation_rendering":
                    "EXPLAINABILITY",

                "semantic_memory_objects":
                    "SEMANTIC_MEMORY",

                "semantic_memory_versions":
                    "SEMANTIC_MEMORY",

                "semantic_memory_retention":
                    "SEMANTIC_MEMORY",

                "semantic_memory_retrieval_contract":
                    "SEMANTIC_MEMORY",

                "learned_relationships":
                    "LEARNING_ENGINE",

                "dynamic_semantic_graph":
                    "DYNAMIC_SEMANTIC_GRAPH",

                "authority_state":
                    "AUTHORITY_INTELLIGENCE",

                "claim_integrity_state":
                    "CLAIM_INTEGRITY_CONFLICT",

                "target_selection":
                    "TARGET_RESOLVERS",

                "linking_decision":
                    "DOWNSTREAM_LINKING_RUNTIME",
            },

        "prohibited_capabilities":
            (
                "WRITE_SEMANTIC_MEMORY",
                "MUTATE_SEMANTIC_MEMORY",
                "PERSIST_SEMANTIC_MEMORY",
                "PERFORM_LIVE_MEMORY_RETRIEVAL",
                "PROMOTE_MEMORY_TO_TRUTH",
                "MUTATE_LEARNING_ENGINE_OUTPUT",
                "MUTATE_DYNAMIC_SEMANTIC_GRAPH",
                "RESCORE_AUTHORITY",
                "REDECIDE_CLAIM_INTEGRITY",
                "RECLASSIFY_CONFLICT",
                "REWRITE_UPSTREAM_GUARD",
                "CREATE_TARGET",
                "SELECT_TARGET",
                "SCORE_TARGET",
                "DISCOVER_EXTERNAL_URL",
                "PERFORM_RUNTIME_SEMANTIC_REASONING",
                "MAKE_LINKING_DECISION",
                "CREATE_EDITOR_HIGHLIGHT",
                "FABRICATE_PROVENANCE",
                "FABRICATE_EVIDENCE",
                "FABRICATE_DECISION_TRACE",
                "HIDE_UNCERTAINTY",
                "SILENTLY_RESOLVE_CONFLICT",
            ),

        "downstream_architecture_sequence":
            (
                "EXPLANATION_SCOPE_AND_AUDIENCE_CONTRACT",
                "EVIDENCE_PROVENANCE_EXPLANATION_MAPPING",
                "CONFLICT_EXCEPTION_EXPLANATION_HANDLING",
                "CONFIDENCE_UNCERTAINTY_EXPLANATION_CONTRACT",
                "DECISION_TRACE_EXPLANATION_CONSTRUCTION",
                "USER_FACING_EXPLANATION_CONSTRUCTION",
                "DEVELOPER_AUDIT_EXPLANATION_CONSTRUCTION",
                "EXPLANATION_SAFETY_BOUNDARY_ENFORCEMENT",
                "FINAL_EXPLAINABILITY_RESULT",
                "FULL_EXPLAINABILITY_HARD_CERTIFICATION",
            ),
    }

    architecture_payload = {
        "source_semantic_memory_package_id":
            source_package_id,

        "source_semantic_memory_package_digest":
            source_package_digest,

        "source_semantic_memory_lineage_root_id":
            source_lineage_root_id,

        "source_memory_object_ids":
            list(
                source_memory_object_ids
            ),

        "architecture":
            architecture,
    }

    serialized = json.dumps(
        architecture_payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    architecture_digest = hashlib.sha256(
        serialized.encode("utf-8")
    ).hexdigest()

    return {
        "schema":
            "explainability_architecture_definition_result_v1",

        "explainability_version":
            EXPLAINABILITY_VERSION,

        "phase":
            EXPLAINABILITY_PHASE,

        "patch":
            "4.6.29B",

        "status":
            "EXPLAINABILITY_ARCHITECTURE_DEFINED",

        "architecture_id":
            "explainabilityarchitecture:v1:"
            + architecture_digest,

        "architecture_digest":
            architecture_digest,

        "source_semantic_memory_package_id":
            source_package_id,

        "source_semantic_memory_package_digest":
            source_package_digest,

        "source_semantic_memory_lineage_root_id":
            source_lineage_root_id,

        "source_memory_object_ids":
            tuple(
                source_memory_object_ids
            ),

        "source_memory_object_count":
            source_memory_object_count,

        "explainability_architecture":
            architecture,

        "certified_semantic_memory_input_inspection":
            copy.deepcopy(
                inspection_result
            ),

        "processing_boundaries": {
            "certified_semantic_memory_inspected":
                True,

            "explainability_architecture_defined":
                True,

            "explanation_generated":
                False,

            "explanation_reasoning_performed":
                False,

            "semantic_memory_written":
                False,

            "semantic_memory_mutated":
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
        },

        "policy":
            "CERTIFIED_EXPLAINABILITY_ARCHITECTURE",

        "next":
            "explanation_scope_and_audience_contract",
    }

def define_explanation_scope_audience_contract_v1(
    architecture_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.29C ? Explanation Scope & Audience Contract.

    Defines canonical explanation scopes, audience-specific detail
    levels, disclosure requirements, and audience-invariant semantic
    meaning.

    This stage defines contracts only.
    It does not generate explanation prose.
    """

    if not isinstance(
        architecture_result,
        dict,
    ):
        raise ExplainabilityError(
            "architecture_result must be a dictionary."
        )

    expected = {
        "schema":
            "explainability_architecture_definition_result_v1",

        "explainability_version":
            EXPLAINABILITY_VERSION,

        "phase":
            EXPLAINABILITY_PHASE,

        "patch":
            "4.6.29B",

        "status":
            "EXPLAINABILITY_ARCHITECTURE_DEFINED",

        "policy":
            "CERTIFIED_EXPLAINABILITY_ARCHITECTURE",

        "next":
            "explanation_scope_and_audience_contract",
    }

    for key, expected_value in expected.items():

        if architecture_result.get(key) != expected_value:
            raise ExplainabilityError(
                "Invalid 4.6.29B lifecycle field: "
                f"{key}"
            )

    architecture = architecture_result.get(
        "explainability_architecture"
    )

    boundaries = architecture_result.get(
        "processing_boundaries"
    )

    if not isinstance(
        architecture,
        dict,
    ):
        raise ExplainabilityError(
            "Explainability architecture is missing."
        )

    if not isinstance(
        boundaries,
        dict,
    ):
        raise ExplainabilityError(
            "4.6.29B processing boundaries are missing."
        )

    if (
        architecture.get("schema")
        != "explainability_architecture_v1"
    ):
        raise ExplainabilityError(
            "Invalid Explainability architecture schema."
        )

    if (
        architecture.get("canonical_owner")
        != "EXPLAINABILITY"
    ):
        raise ExplainabilityError(
            "Explainability ownership mismatch."
        )

    if (
        architecture.get("canonical_input_owner")
        != "SEMANTIC_MEMORY"
    ):
        raise ExplainabilityError(
            "Explainability input ownership mismatch."
        )

    required_surfaces = (
        "USER_FACING_EXPLANATION",
        "DEVELOPER_EXPLANATION",
        "AUDIT_EXPLANATION",
        "DECISION_TRACE_EXPLANATION",
    )

    required_audiences = (
        "END_USER",
        "DEVELOPER",
        "AUDITOR",
        "OWNER_OPERATOR",
    )

    required_scopes = (
        "MEMORY_OBJECT",
        "RELATIONSHIP",
        "EVIDENCE",
        "PROVENANCE",
        "CONFLICT_EXCEPTION",
        "STABILITY_RETENTION",
        "RETRIEVAL_STATE",
        "DECISION_TRACE",
    )

    for value in required_surfaces:

        if value not in architecture.get(
            "explanation_surfaces",
            (),
        ):
            raise ExplainabilityError(
                "Required explanation surface missing: "
                f"{value}"
            )

    for value in required_audiences:

        if value not in architecture.get(
            "audience_classes",
            (),
        ):
            raise ExplainabilityError(
                "Required audience missing: "
                f"{value}"
            )

    for value in required_scopes:

        if value not in architecture.get(
            "explanation_scope_classes",
            (),
        ):
            raise ExplainabilityError(
                "Required explanation scope missing: "
                f"{value}"
            )

    for flag in (
        "certified_semantic_memory_inspected",
        "explainability_architecture_defined",
    ):
        if boundaries.get(flag) is not True:
            raise ExplainabilityError(
                "Required upstream Explainability state missing: "
                f"{flag}"
            )

    for flag in (
        "explanation_generated",
        "explanation_reasoning_performed",
        "semantic_memory_written",
        "semantic_memory_mutated",
        "memory_persistence_performed",
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
            raise ExplainabilityError(
                "Unsafe 4.6.29C input boundary state: "
                f"{flag}"
            )

    source_package_id = architecture_result.get(
        "source_semantic_memory_package_id"
    )

    source_package_digest = architecture_result.get(
        "source_semantic_memory_package_digest"
    )

    source_lineage_root_id = architecture_result.get(
        "source_semantic_memory_lineage_root_id"
    )

    source_memory_object_ids = architecture_result.get(
        "source_memory_object_ids"
    )

    source_memory_object_count = architecture_result.get(
        "source_memory_object_count"
    )

    if not isinstance(
        source_memory_object_ids,
        tuple,
    ):
        raise ExplainabilityError(
            "source_memory_object_ids must be a tuple."
        )

    if (
        source_memory_object_count
        != len(source_memory_object_ids)
    ):
        raise ExplainabilityError(
            "Source memory object count mismatch."
        )

    audience_contracts = (
        {
            "schema":
                "explanation_audience_contract_v1",

            "audience":
                "END_USER",

            "primary_surface":
                "USER_FACING_EXPLANATION",

            "detail_level":
                "CONCISE",

            "technical_depth":
                "LOW",

            "provenance_detail":
                "SUMMARY",

            "lineage_detail":
                "SUMMARY",

            "decision_trace_detail":
                "SUMMARY_WHEN_RELEVANT",

            "conflict_disclosure_required":
                True,

            "uncertainty_disclosure_required":
                True,

            "state_label_preservation_required":
                True,

            "truth_separation_disclosure_required":
                True,

            "raw_internal_identifiers_required":
                False,

            "semantic_meaning_may_change":
                False,
        },

        {
            "schema":
                "explanation_audience_contract_v1",

            "audience":
                "DEVELOPER",

            "primary_surface":
                "DEVELOPER_EXPLANATION",

            "detail_level":
                "DETAILED",

            "technical_depth":
                "HIGH",

            "provenance_detail":
                "FULL",

            "lineage_detail":
                "FULL",

            "decision_trace_detail":
                "DETAILED",

            "conflict_disclosure_required":
                True,

            "uncertainty_disclosure_required":
                True,

            "state_label_preservation_required":
                True,

            "truth_separation_disclosure_required":
                True,

            "raw_internal_identifiers_required":
                True,

            "semantic_meaning_may_change":
                False,
        },

        {
            "schema":
                "explanation_audience_contract_v1",

            "audience":
                "AUDITOR",

            "primary_surface":
                "AUDIT_EXPLANATION",

            "detail_level":
                "EXHAUSTIVE",

            "technical_depth":
                "HIGH",

            "provenance_detail":
                "FULL",

            "lineage_detail":
                "FULL",

            "decision_trace_detail":
                "FULL",

            "conflict_disclosure_required":
                True,

            "uncertainty_disclosure_required":
                True,

            "state_label_preservation_required":
                True,

            "truth_separation_disclosure_required":
                True,

            "raw_internal_identifiers_required":
                True,

            "semantic_meaning_may_change":
                False,
        },

        {
            "schema":
                "explanation_audience_contract_v1",

            "audience":
                "OWNER_OPERATOR",

            "primary_surface":
                "AUDIT_EXPLANATION",

            "detail_level":
                "OPERATIONAL_DETAILED",

            "technical_depth":
                "HIGH",

            "provenance_detail":
                "FULL",

            "lineage_detail":
                "FULL",

            "decision_trace_detail":
                "DETAILED",

            "conflict_disclosure_required":
                True,

            "uncertainty_disclosure_required":
                True,

            "state_label_preservation_required":
                True,

            "truth_separation_disclosure_required":
                True,

            "raw_internal_identifiers_required":
                True,

            "semantic_meaning_may_change":
                False,
        },
    )

    scope_contracts = (
        {
            "scope":
                "MEMORY_OBJECT",

            "must_preserve":
                (
                    "MEMORY_OBJECT_ID",
                    "MEMORY_STATE",
                    "STABILITY_STATE",
                    "RETENTION_STATE",
                    "RETRIEVAL_CLASS",
                    "PROVENANCE",
                    "LINEAGE",
                    "NON_TRUTH_STATUS",
                ),
        },

        {
            "scope":
                "RELATIONSHIP",

            "must_preserve":
                (
                    "SOURCE_LEARNING_REFERENCE",
                    "RELATIONSHIP_CONTEXT",
                    "PROVENANCE",
                    "LINEAGE",
                    "UNCERTAINTY",
                ),
        },

        {
            "scope":
                "EVIDENCE",

            "must_preserve":
                (
                    "EVIDENCE_CONTEXT",
                    "PROVENANCE",
                    "AUTHORITY_CONTEXT",
                    "UNCERTAINTY",
                ),
        },

        {
            "scope":
                "PROVENANCE",

            "must_preserve":
                (
                    "SOURCE_MEMORY_REFERENCE",
                    "SOURCE_LEARNING_REFERENCE",
                    "GRAPH_REFERENCE",
                    "LINEAGE_REFERENCE",
                    "VERSION_CONTEXT",
                ),
        },

        {
            "scope":
                "CONFLICT_EXCEPTION",

            "must_preserve":
                (
                    "CONFLICT_STATE",
                    "EXCEPTION_STATE",
                    "MINORITY_CONTEXT",
                    "NON_RESOLUTION_DISCLOSURE",
                ),
        },

        {
            "scope":
                "STABILITY_RETENTION",

            "must_preserve":
                (
                    "STABILITY_STATE",
                    "RETENTION_STATE",
                    "STATE_CAUTION",
                ),
        },

        {
            "scope":
                "RETRIEVAL_STATE",

            "must_preserve":
                (
                    "RETRIEVAL_CLASS",
                    "DEFAULT_READABILITY",
                    "STATE_AWARE_READ_REQUIREMENT",
                ),
        },

        {
            "scope":
                "DECISION_TRACE",

            "must_preserve":
                (
                    "CERTIFIED_AVAILABLE_TRACE_ONLY",
                    "COMPONENT_IDENTITY",
                    "TRACE_ORDER_IF_CERTIFIED",
                    "MISSING_TRACE_DISCLOSURE",
                ),
        },
    )

    scope_rules = {
        "schema":
            "explanation_scope_contract_v1",

        "allowed_scopes":
            required_scopes,

        "scope_contracts":
            scope_contracts,

        "single_scope_explanation_allowed":
            True,

        "multi_scope_explanation_allowed":
            True,

        "scope_combination_must_preserve_each_scope_contract":
            True,

        "scope_expansion_requires_certified_available_state":
            True,

        "scope_must_not_infer_missing_state":
            True,

        "scope_must_not_create_new_semantic_state":
            True,

        "scope_must_not_create_new_decision":
            True,
    }

    audience_invariance = {
        "schema":
            "explanation_audience_invariance_contract_v1",

        "semantic_meaning_invariant_across_audiences":
            True,

        "source_memory_identity_invariant":
            True,

        "provenance_invariant":
            True,

        "lineage_invariant":
            True,

        "memory_state_invariant":
            True,

        "conflict_state_invariant":
            True,

        "exception_state_invariant":
            True,

        "uncertainty_state_invariant":
            True,

        "truth_status_invariant":
            True,

        "decision_status_invariant":
            True,

        "detail_level_may_vary":
            True,

        "technical_depth_may_vary":
            True,

        "identifier_visibility_may_vary":
            True,

        "wording_may_vary":
            True,

        "meaning_may_vary":
            False,

        "conflict_may_be_hidden":
            False,

        "uncertainty_may_be_hidden":
            False,

        "truth_status_may_be_hidden":
            False,
    }

    surface_routing_contract = {
        "schema":
            "explanation_surface_routing_contract_v1",

        "END_USER":
            "USER_FACING_EXPLANATION",

        "DEVELOPER":
            "DEVELOPER_EXPLANATION",

        "AUDITOR":
            "AUDIT_EXPLANATION",

        "OWNER_OPERATOR":
            "AUDIT_EXPLANATION",

        "DECISION_TRACE_EXPLANATION":
            "AVAILABLE_AS_ADDITIONAL_TRACE_SURFACE_WHEN_CERTIFIED_TRACE_EXISTS",
    }

    prohibited_audience_behaviors = (
        "CHANGE_SEMANTIC_MEANING_BY_AUDIENCE",
        "HIDE_CONFLICT_FROM_ANY_AUDIENCE",
        "HIDE_UNCERTAINTY_FROM_ANY_AUDIENCE",
        "PROMOTE_MEMORY_TO_TRUTH_FOR_SIMPLICITY",
        "SIMPLIFY_AWAY_EXCEPTION_CONTEXT",
        "FABRICATE_DETAIL_FOR_TECHNICAL_AUDIENCE",
        "FABRICATE_CAUSAL_REASON",
        "FABRICATE_DECISION_TRACE",
        "CHANGE_MEMORY_STATE_LABEL",
        "CHANGE_RETRIEVAL_CLASS",
        "CHANGE_RETENTION_STATE",
        "CHANGE_STABILITY_STATE",
        "SELECT_TARGET",
        "SCORE_TARGET",
        "MAKE_LINKING_DECISION",
    )

    contract_payload = {
        "source_semantic_memory_package_id":
            source_package_id,

        "source_semantic_memory_package_digest":
            source_package_digest,

        "source_semantic_memory_lineage_root_id":
            source_lineage_root_id,

        "source_memory_object_ids":
            list(
                source_memory_object_ids
            ),

        "audience_contracts":
            audience_contracts,

        "scope_rules":
            scope_rules,

        "audience_invariance":
            audience_invariance,

        "surface_routing_contract":
            surface_routing_contract,

        "prohibited_audience_behaviors":
            prohibited_audience_behaviors,
    }

    serialized = json.dumps(
        contract_payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    contract_digest = hashlib.sha256(
        serialized.encode("utf-8")
    ).hexdigest()

    contract_bundle = {
        "schema":
            "explanation_scope_audience_contract_bundle_v1",

        "scope_audience_contract_id":
            "explainabilityscopeaudience:v1:"
            + contract_digest,

        "scope_audience_contract_digest":
            contract_digest,

        "source_semantic_memory_package_id":
            source_package_id,

        "source_semantic_memory_package_digest":
            source_package_digest,

        "source_semantic_memory_lineage_root_id":
            source_lineage_root_id,

        "audience_contracts":
            audience_contracts,

        "scope_contract":
            scope_rules,

        "audience_invariance_contract":
            audience_invariance,

        "surface_routing_contract":
            surface_routing_contract,

        "prohibited_audience_behaviors":
            prohibited_audience_behaviors,

        "audience_contract_defined":
            True,

        "scope_contract_defined":
            True,

        "semantic_meaning_locked":
            True,

        "explanation_generated":
            False,

        "explanation_reasoning_performed":
            False,

        "semantic_memory_mutated":
            False,

        "graph_mutated":
            False,

        "target_selected":
            False,

        "target_scored":
            False,

        "runtime_reasoning_performed":
            False,

        "linking_decision_performed":
            False,
    }

    return {
        "schema":
            "explanation_scope_audience_contract_result_v1",

        "explainability_version":
            EXPLAINABILITY_VERSION,

        "phase":
            EXPLAINABILITY_PHASE,

        "patch":
            "4.6.29C",

        "status":
            "EXPLANATION_SCOPE_AUDIENCE_CONTRACT_DEFINED",

        "source_semantic_memory_package_id":
            source_package_id,

        "source_semantic_memory_package_digest":
            source_package_digest,

        "source_semantic_memory_lineage_root_id":
            source_lineage_root_id,

        "source_memory_object_ids":
            tuple(
                source_memory_object_ids
            ),

        "source_memory_object_count":
            source_memory_object_count,

        "explainability_architecture":
            copy.deepcopy(
                architecture
            ),

        "explanation_scope_audience_contract_bundle":
            contract_bundle,

        "explainability_architecture_definition":
            copy.deepcopy(
                architecture_result
            ),

        "processing_boundaries": {
            "certified_semantic_memory_inspected":
                True,

            "explainability_architecture_defined":
                True,

            "explanation_scope_audience_contract_defined":
                True,

            "explanation_generated":
                False,

            "explanation_reasoning_performed":
                False,

            "semantic_memory_written":
                False,

            "semantic_memory_mutated":
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
        },

        "policy":
            "CERTIFIED_EXPLANATION_SCOPE_AUDIENCE_CONTRACT",

        "next":
            "evidence_provenance_explanation_mapping",
    }

def map_evidence_provenance_explanation_v1(
    scope_audience_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.29D ? Evidence / Provenance Explanation Mapping.

    Maps certified Semantic Memory provenance/evidence context into
    Explainability-owned explanation metadata.

    This stage maps only certified available context.
    It does not fabricate evidence, rewrite provenance, rescore
    authority, adjudicate truth, or generate final user-facing prose.
    """

    if not isinstance(
        scope_audience_result,
        dict,
    ):
        raise ExplainabilityError(
            "scope_audience_result must be a dictionary."
        )

    expected = {
        "schema":
            "explanation_scope_audience_contract_result_v1",

        "explainability_version":
            EXPLAINABILITY_VERSION,

        "phase":
            EXPLAINABILITY_PHASE,

        "patch":
            "4.6.29C",

        "status":
            "EXPLANATION_SCOPE_AUDIENCE_CONTRACT_DEFINED",

        "policy":
            "CERTIFIED_EXPLANATION_SCOPE_AUDIENCE_CONTRACT",

        "next":
            "evidence_provenance_explanation_mapping",
    }

    for key, expected_value in expected.items():

        if scope_audience_result.get(key) != expected_value:
            raise ExplainabilityError(
                "Invalid 4.6.29C lifecycle field: "
                f"{key}"
            )

    architecture = scope_audience_result.get(
        "explainability_architecture"
    )

    contract_bundle = scope_audience_result.get(
        "explanation_scope_audience_contract_bundle"
    )

    architecture_definition = scope_audience_result.get(
        "explainability_architecture_definition"
    )

    boundaries = scope_audience_result.get(
        "processing_boundaries"
    )

    for name, value in (
        (
            "explainability_architecture",
            architecture,
        ),
        (
            "explanation_scope_audience_contract_bundle",
            contract_bundle,
        ),
        (
            "explainability_architecture_definition",
            architecture_definition,
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
            raise ExplainabilityError(
                f"{name} must be a dictionary."
            )

    if (
        architecture.get("schema")
        != "explainability_architecture_v1"
    ):
        raise ExplainabilityError(
            "Invalid Explainability architecture schema."
        )

    if (
        contract_bundle.get("schema")
        != "explanation_scope_audience_contract_bundle_v1"
    ):
        raise ExplainabilityError(
            "Invalid scope/audience contract bundle schema."
        )

    if contract_bundle.get(
        "audience_contract_defined"
    ) is not True:
        raise ExplainabilityError(
            "Audience contract is incomplete."
        )

    if contract_bundle.get(
        "scope_contract_defined"
    ) is not True:
        raise ExplainabilityError(
            "Scope contract is incomplete."
        )

    if contract_bundle.get(
        "semantic_meaning_locked"
    ) is not True:
        raise ExplainabilityError(
            "Semantic meaning is not locked."
        )

    for required_scope in (
        "EVIDENCE",
        "PROVENANCE",
    ):
        if required_scope not in architecture.get(
            "explanation_scope_classes",
            (),
        ):
            raise ExplainabilityError(
                "Required Explainability scope missing: "
                f"{required_scope}"
            )

    for required_component in (
        "SOURCE_MEMORY_REFERENCE",
        "PROVENANCE",
        "LINEAGE",
        "EVIDENCE_CONTEXT",
        "AUTHORITY_CONTEXT",
    ):
        if required_component not in architecture.get(
            "explanation_components",
            (),
        ):
            raise ExplainabilityError(
                "Required Explainability component missing: "
                f"{required_component}"
            )

    for flag in (
        "certified_semantic_memory_inspected",
        "explainability_architecture_defined",
        "explanation_scope_audience_contract_defined",
    ):
        if boundaries.get(flag) is not True:
            raise ExplainabilityError(
                "Required upstream Explainability state missing: "
                f"{flag}"
            )

    for flag in (
        "explanation_generated",
        "explanation_reasoning_performed",
        "semantic_memory_written",
        "semantic_memory_mutated",
        "memory_persistence_performed",
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
            raise ExplainabilityError(
                "Unsafe 4.6.29D input boundary state: "
                f"{flag}"
            )

    source_package_id = scope_audience_result.get(
        "source_semantic_memory_package_id"
    )

    source_package_digest = scope_audience_result.get(
        "source_semantic_memory_package_digest"
    )

    source_lineage_root_id = scope_audience_result.get(
        "source_semantic_memory_lineage_root_id"
    )

    source_memory_object_ids = scope_audience_result.get(
        "source_memory_object_ids"
    )

    source_memory_object_count = scope_audience_result.get(
        "source_memory_object_count"
    )

    if not isinstance(
        source_memory_object_ids,
        tuple,
    ):
        raise ExplainabilityError(
            "source_memory_object_ids must be a tuple."
        )

    if (
        not isinstance(
            source_memory_object_count,
            int,
        )
        or source_memory_object_count
        != len(source_memory_object_ids)
    ):
        raise ExplainabilityError(
            "Source memory object count mismatch."
        )

    if len(
        source_memory_object_ids
    ) != len(
        set(source_memory_object_ids)
    ):
        raise ExplainabilityError(
            "Duplicate source memory object IDs."
        )

    certified_inspection = (
        architecture_definition.get(
            "certified_semantic_memory_input_inspection"
        )
    )

    if not isinstance(
        certified_inspection,
        dict,
    ):
        raise ExplainabilityError(
            "Certified Semantic Memory inspection is missing."
        )

    certified_input = certified_inspection.get(
        "certified_semantic_memory_input"
    )

    if not isinstance(
        certified_input,
        dict,
    ):
        raise ExplainabilityError(
            "Certified Semantic Memory input is missing."
        )

    final_result = certified_input.get(
        "final_semantic_memory_result"
    )

    if not isinstance(
        final_result,
        dict,
    ):
        raise ExplainabilityError(
            "Final Semantic Memory result is missing."
        )

    final_package = final_result.get(
        "final_semantic_memory_package"
    )

    if not isinstance(
        final_package,
        dict,
    ):
        raise ExplainabilityError(
            "Final Semantic Memory package is missing."
        )

    final_memory_objects = final_package.get(
        "final_memory_objects"
    )

    if not isinstance(
        final_memory_objects,
        tuple,
    ):
        raise ExplainabilityError(
            "Final Semantic Memory objects must be a tuple."
        )

    memory_by_id = {}

    for memory_object in final_memory_objects:

        if not isinstance(
            memory_object,
            dict,
        ):
            raise ExplainabilityError(
                "Semantic Memory object must be a dictionary."
            )

        if (
            memory_object.get("schema")
            != "semantic_memory_object_v1"
        ):
            raise ExplainabilityError(
                "Invalid Semantic Memory object schema."
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
            raise ExplainabilityError(
                "Semantic Memory object ID is missing."
            )

        if memory_object_id in memory_by_id:
            raise ExplainabilityError(
                "Duplicate Semantic Memory object ID."
            )

        memory_by_id[
            memory_object_id
        ] = memory_object

    if set(
        source_memory_object_ids
    ) != set(
        memory_by_id
    ):
        raise ExplainabilityError(
            "Source Semantic Memory object identity mismatch."
        )

    mapping_records = []

    for memory_object_id in source_memory_object_ids:

        memory_object = memory_by_id[
            memory_object_id
        ]

        source_learning_object_id = memory_object.get(
            "source_learning_object_id"
        )

        memory_lineage_record_id = memory_object.get(
            "memory_lineage_record_id"
        )

        retrieval_metadata_id = memory_object.get(
            "retrieval_metadata_id"
        )

        memory_state = memory_object.get(
            "memory_state"
        )

        stability_state = memory_object.get(
            "stability_state"
        )

        retention_state = memory_object.get(
            "retention_state"
        )

        retrieval_class = memory_object.get(
            "retrieval_class"
        )

        for name, value in (
            (
                "memory_object_id",
                memory_object_id,
            ),
            (
                "source_learning_object_id",
                source_learning_object_id,
            ),
            (
                "memory_lineage_record_id",
                memory_lineage_record_id,
            ),
            (
                "retrieval_metadata_id",
                retrieval_metadata_id,
            ),
            (
                "memory_state",
                memory_state,
            ),
            (
                "stability_state",
                stability_state,
            ),
            (
                "retention_state",
                retention_state,
            ),
            (
                "retrieval_class",
                retrieval_class,
            ),
        ):
            if not isinstance(
                value,
                str,
            ) or not value:
                raise ExplainabilityError(
                    "Missing certified evidence/provenance field: "
                    f"{name}"
                )

        if memory_object.get(
            "provenance_complete"
        ) is not True:
            raise ExplainabilityError(
                "Semantic Memory provenance is incomplete."
            )

        if memory_object.get(
            "lineage_complete"
        ) is not True:
            raise ExplainabilityError(
                "Semantic Memory lineage is incomplete."
            )

        if memory_object.get(
            "is_certified_fact"
        ) is not False:
            raise ExplainabilityError(
                "Semantic Memory cannot be promoted to certified truth."
            )

        if memory_object.get(
            "is_learned_truth"
        ) is not False:
            raise ExplainabilityError(
                "Semantic Memory cannot be promoted to learned truth."
            )

        record_payload = {
            "memory_object_id":
                memory_object_id,

            "source_learning_object_id":
                source_learning_object_id,

            "memory_lineage_record_id":
                memory_lineage_record_id,

            "retrieval_metadata_id":
                retrieval_metadata_id,

            "memory_state":
                memory_state,

            "stability_state":
                stability_state,

            "retention_state":
                retention_state,

            "retrieval_class":
                retrieval_class,

            "source_semantic_memory_package_id":
                source_package_id,

            "source_semantic_memory_lineage_root_id":
                source_lineage_root_id,
        }

        serialized = json.dumps(
            record_payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )

        record_digest = hashlib.sha256(
            serialized.encode("utf-8")
        ).hexdigest()

        mapping_records.append(
            {
                "schema":
                    "evidence_provenance_explanation_mapping_record_v1",

                "evidence_provenance_mapping_id":
                    "explainabilityevidence:v1:"
                    + record_digest,

                "memory_object_id":
                    memory_object_id,

                "source_learning_object_id":
                    source_learning_object_id,

                "memory_lineage_record_id":
                    memory_lineage_record_id,

                "retrieval_metadata_id":
                    retrieval_metadata_id,

                "source_semantic_memory_package_id":
                    source_package_id,

                "source_semantic_memory_package_digest":
                    source_package_digest,

                "source_semantic_memory_lineage_root_id":
                    source_lineage_root_id,

                "memory_state":
                    memory_state,

                "stability_state":
                    stability_state,

                "retention_state":
                    retention_state,

                "retrieval_class":
                    retrieval_class,

                "provenance_complete":
                    True,

                "lineage_complete":
                    True,

                "evidence_context_available":
                    True,

                "authority_context_available":
                    True,

                "non_truth_status_preserved":
                    True,

                "explanation_may_reference_source_memory":
                    True,

                "explanation_may_reference_provenance":
                    True,

                "explanation_may_reference_lineage":
                    True,

                "explanation_may_reference_evidence_context":
                    True,

                "explanation_may_reference_authority_context":
                    True,

                "evidence_fabricated":
                    False,

                "provenance_fabricated":
                    False,

                "lineage_fabricated":
                    False,

                "authority_rescored":
                    False,

                "truth_adjudicated":
                    False,

                "semantic_state_mutated":
                    False,
            }
        )

    mapping_records = tuple(
        mapping_records
    )

    mapping_contract = {
        "schema":
            "evidence_provenance_explanation_mapping_contract_v1",

        "canonical_owner":
            "EXPLAINABILITY",

        "source_owner":
            "SEMANTIC_MEMORY",

        "mapping_is_read_only":
            True,

        "mapping_uses_certified_available_state_only":
            True,

        "mapping_preserves_source_memory_identity":
            True,

        "mapping_preserves_source_learning_reference":
            True,

        "mapping_preserves_provenance":
            True,

        "mapping_preserves_lineage":
            True,

        "mapping_preserves_memory_state":
            True,

        "mapping_preserves_stability_state":
            True,

        "mapping_preserves_retention_state":
            True,

        "mapping_preserves_retrieval_class":
            True,

        "mapping_preserves_non_truth_status":
            True,

        "missing_evidence_must_be_disclosed":
            True,

        "missing_provenance_must_be_disclosed":
            True,

        "missing_lineage_must_be_disclosed":
            True,

        "authority_context_is_explanatory_not_truth":
            True,

        "high_authority_does_not_establish_truth":
            True,

        "explanation_must_not_invent_evidence":
            True,

        "explanation_must_not_invent_provenance":
            True,

        "explanation_must_not_invent_lineage":
            True,

        "explanation_must_not_rescore_authority":
            True,

        "explanation_must_not_redecide_claim_integrity":
            True,

        "explanation_must_not_reclassify_conflict":
            True,

        "explanation_must_not_change_memory_state":
            True,

        "explanation_must_not_select_target":
            True,

        "explanation_must_not_score_target":
            True,

        "explanation_must_not_make_linking_decision":
            True,
    }

    bundle_payload = {
        "source_semantic_memory_package_id":
            source_package_id,

        "source_semantic_memory_package_digest":
            source_package_digest,

        "source_semantic_memory_lineage_root_id":
            source_lineage_root_id,

        "mapping_ids":
            [
                item[
                    "evidence_provenance_mapping_id"
                ]
                for item in mapping_records
            ],
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

    mapping_bundle = {
        "schema":
            "evidence_provenance_explanation_mapping_bundle_v1",

        "evidence_provenance_mapping_bundle_id":
            "explainabilityevidencebundle:v1:"
            + bundle_digest,

        "evidence_provenance_mapping_bundle_digest":
            bundle_digest,

        "source_semantic_memory_package_id":
            source_package_id,

        "source_semantic_memory_package_digest":
            source_package_digest,

        "source_semantic_memory_lineage_root_id":
            source_lineage_root_id,

        "mapping_records":
            mapping_records,

        "mapping_contract":
            mapping_contract,

        "mapping_record_count":
            len(
                mapping_records
            ),

        "evidence_provenance_mapping_complete":
            True,

        "source_memory_identity_preserved":
            True,

        "provenance_preserved":
            True,

        "lineage_preserved":
            True,

        "non_truth_status_preserved":
            True,

        "evidence_fabricated":
            False,

        "provenance_fabricated":
            False,

        "lineage_fabricated":
            False,

        "authority_rescored":
            False,

        "claim_integrity_redecided":
            False,

        "conflict_reclassified":
            False,

        "semantic_memory_mutated":
            False,

        "graph_mutated":
            False,

        "target_selected":
            False,

        "target_scored":
            False,

        "runtime_reasoning_performed":
            False,

        "linking_decision_performed":
            False,

        "explanation_generated":
            False,
    }

    return {
        "schema":
            "evidence_provenance_explanation_mapping_result_v1",

        "explainability_version":
            EXPLAINABILITY_VERSION,

        "phase":
            EXPLAINABILITY_PHASE,

        "patch":
            "4.6.29D",

        "status":
            "EVIDENCE_PROVENANCE_EXPLANATION_MAPPING_COMPLETED",

        "source_semantic_memory_package_id":
            source_package_id,

        "source_semantic_memory_package_digest":
            source_package_digest,

        "source_semantic_memory_lineage_root_id":
            source_lineage_root_id,

        "source_memory_object_ids":
            tuple(
                source_memory_object_ids
            ),

        "source_memory_object_count":
            source_memory_object_count,

        "explainability_architecture":
            copy.deepcopy(
                architecture
            ),

        "explanation_scope_audience_contract_bundle":
            copy.deepcopy(
                contract_bundle
            ),

        "evidence_provenance_explanation_mapping_bundle":
            mapping_bundle,

        "explanation_scope_audience_contract_result":
            copy.deepcopy(
                scope_audience_result
            ),

        "processing_boundaries": {
            "certified_semantic_memory_inspected":
                True,

            "explainability_architecture_defined":
                True,

            "explanation_scope_audience_contract_defined":
                True,

            "evidence_provenance_explanation_mapping_completed":
                True,

            "explanation_generated":
                False,

            "explanation_reasoning_performed":
                False,

            "semantic_memory_written":
                False,

            "semantic_memory_mutated":
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
        },

        "policy":
            "CERTIFIED_EVIDENCE_PROVENANCE_EXPLANATION_MAPPING",

        "next":
            "conflict_exception_explanation_handling",
    }

def handle_conflict_exception_explanation_v1(
    evidence_mapping_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.29E ? Conflict / Exception Explanation Handling.

    Defines and constructs Explainability-owned conflict/exception
    explanation metadata from certified Semantic Memory state.

    This stage preserves disagreement, exception, contested, held,
    blocked, weakened, historical, and minority context without
    resolving or suppressing it.

    It does not generate final prose or make semantic decisions.
    """

    if not isinstance(
        evidence_mapping_result,
        dict,
    ):
        raise ExplainabilityError(
            "evidence_mapping_result must be a dictionary."
        )

    expected = {
        "schema":
            "evidence_provenance_explanation_mapping_result_v1",

        "explainability_version":
            EXPLAINABILITY_VERSION,

        "phase":
            EXPLAINABILITY_PHASE,

        "patch":
            "4.6.29D",

        "status":
            "EVIDENCE_PROVENANCE_EXPLANATION_MAPPING_COMPLETED",

        "policy":
            "CERTIFIED_EVIDENCE_PROVENANCE_EXPLANATION_MAPPING",

        "next":
            "conflict_exception_explanation_handling",
    }

    for key, expected_value in expected.items():

        if evidence_mapping_result.get(key) != expected_value:
            raise ExplainabilityError(
                "Invalid 4.6.29D lifecycle field: "
                f"{key}"
            )

    architecture = evidence_mapping_result.get(
        "explainability_architecture"
    )

    scope_bundle = evidence_mapping_result.get(
        "explanation_scope_audience_contract_bundle"
    )

    mapping_bundle = evidence_mapping_result.get(
        "evidence_provenance_explanation_mapping_bundle"
    )

    boundaries = evidence_mapping_result.get(
        "processing_boundaries"
    )

    for name, value in (
        (
            "explainability_architecture",
            architecture,
        ),
        (
            "explanation_scope_audience_contract_bundle",
            scope_bundle,
        ),
        (
            "evidence_provenance_explanation_mapping_bundle",
            mapping_bundle,
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
            raise ExplainabilityError(
                f"{name} must be a dictionary."
            )

    if (
        architecture.get("schema")
        != "explainability_architecture_v1"
    ):
        raise ExplainabilityError(
            "Invalid Explainability architecture schema."
        )

    if (
        mapping_bundle.get("schema")
        != "evidence_provenance_explanation_mapping_bundle_v1"
    ):
        raise ExplainabilityError(
            "Invalid evidence/provenance mapping bundle schema."
        )

    if mapping_bundle.get(
        "evidence_provenance_mapping_complete"
    ) is not True:
        raise ExplainabilityError(
            "Evidence/provenance mapping is incomplete."
        )

    if mapping_bundle.get(
        "source_memory_identity_preserved"
    ) is not True:
        raise ExplainabilityError(
            "Source memory identity was not preserved."
        )

    if mapping_bundle.get(
        "provenance_preserved"
    ) is not True:
        raise ExplainabilityError(
            "Provenance was not preserved."
        )

    if mapping_bundle.get(
        "lineage_preserved"
    ) is not True:
        raise ExplainabilityError(
            "Lineage was not preserved."
        )

    if mapping_bundle.get(
        "non_truth_status_preserved"
    ) is not True:
        raise ExplainabilityError(
            "Non-truth status was not preserved."
        )

    for required_component in (
        "CONFLICT_CONTEXT",
        "EXCEPTION_CONTEXT",
        "STABILITY_STATE",
        "RETENTION_STATE",
        "RETRIEVAL_CLASS",
        "BOUNDARY_DISCLOSURE",
    ):
        if required_component not in architecture.get(
            "explanation_components",
            (),
        ):
            raise ExplainabilityError(
                "Required conflict/exception component missing: "
                f"{required_component}"
            )

    for required_scope in (
        "CONFLICT_EXCEPTION",
        "STABILITY_RETENTION",
        "RETRIEVAL_STATE",
    ):
        if required_scope not in architecture.get(
            "explanation_scope_classes",
            (),
        ):
            raise ExplainabilityError(
                "Required conflict/exception scope missing: "
                f"{required_scope}"
            )

    for flag in (
        "certified_semantic_memory_inspected",
        "explainability_architecture_defined",
        "explanation_scope_audience_contract_defined",
        "evidence_provenance_explanation_mapping_completed",
    ):
        if boundaries.get(flag) is not True:
            raise ExplainabilityError(
                "Required upstream Explainability state missing: "
                f"{flag}"
            )

    for flag in (
        "explanation_generated",
        "explanation_reasoning_performed",
        "semantic_memory_written",
        "semantic_memory_mutated",
        "memory_persistence_performed",
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
            raise ExplainabilityError(
                "Unsafe 4.6.29E input boundary state: "
                f"{flag}"
            )

    source_package_id = evidence_mapping_result.get(
        "source_semantic_memory_package_id"
    )

    source_package_digest = evidence_mapping_result.get(
        "source_semantic_memory_package_digest"
    )

    source_lineage_root_id = evidence_mapping_result.get(
        "source_semantic_memory_lineage_root_id"
    )

    source_memory_object_ids = evidence_mapping_result.get(
        "source_memory_object_ids"
    )

    source_memory_object_count = evidence_mapping_result.get(
        "source_memory_object_count"
    )

    if not isinstance(
        source_memory_object_ids,
        tuple,
    ):
        raise ExplainabilityError(
            "source_memory_object_ids must be a tuple."
        )

    if (
        not isinstance(
            source_memory_object_count,
            int,
        )
        or source_memory_object_count
        != len(source_memory_object_ids)
    ):
        raise ExplainabilityError(
            "Source memory object count mismatch."
        )

    mapping_records = mapping_bundle.get(
        "mapping_records"
    )

    if not isinstance(
        mapping_records,
        tuple,
    ):
        raise ExplainabilityError(
            "mapping_records must be a tuple."
        )

    if len(
        mapping_records
    ) != source_memory_object_count:
        raise ExplainabilityError(
            "Evidence/provenance mapping count mismatch."
        )

    mapping_by_memory_id = {}

    for record in mapping_records:

        if not isinstance(
            record,
            dict,
        ):
            raise ExplainabilityError(
                "Evidence/provenance mapping record must be a dictionary."
            )

        if (
            record.get("schema")
            != "evidence_provenance_explanation_mapping_record_v1"
        ):
            raise ExplainabilityError(
                "Invalid evidence/provenance mapping record schema."
            )

        memory_object_id = record.get(
            "memory_object_id"
        )

        if (
            not isinstance(
                memory_object_id,
                str,
            )
            or not memory_object_id
        ):
            raise ExplainabilityError(
                "Mapping record memory object ID is missing."
            )

        if memory_object_id in mapping_by_memory_id:
            raise ExplainabilityError(
                "Duplicate evidence/provenance memory mapping."
            )

        mapping_by_memory_id[
            memory_object_id
        ] = record

    if set(
        source_memory_object_ids
    ) != set(
        mapping_by_memory_id
    ):
        raise ExplainabilityError(
            "Conflict/exception source identity mismatch."
        )

    classification_rules = {
        "ACTIVE_MEMORY":
            "NO_SPECIAL_CONFLICT_EXCEPTION_DISCLOSURE",

        "CONTESTED_MEMORY":
            "DISCLOSE_CONTESTED_STATE_AND_UNRESOLVED_CONFLICT",

        "HELD_MEMORY":
            "DISCLOSE_HELD_STATE_AND_NON_DEFAULT_READABILITY",

        "BLOCKED_MEMORY":
            "DISCLOSE_BLOCKED_STATE_AND_NON_DEFAULT_READABILITY",

        "HISTORICAL_MEMORY":
            "DISCLOSE_HISTORICAL_STATE_AND_NON_CURRENT_STATUS",
    }

    handling_records = []

    for memory_object_id in source_memory_object_ids:

        mapping = mapping_by_memory_id[
            memory_object_id
        ]

        memory_state = mapping.get(
            "memory_state"
        )

        stability_state = mapping.get(
            "stability_state"
        )

        retention_state = mapping.get(
            "retention_state"
        )

        retrieval_class = mapping.get(
            "retrieval_class"
        )

        for name, value in (
            (
                "memory_state",
                memory_state,
            ),
            (
                "stability_state",
                stability_state,
            ),
            (
                "retention_state",
                retention_state,
            ),
            (
                "retrieval_class",
                retrieval_class,
            ),
        ):
            if not isinstance(
                value,
                str,
            ) or not value:
                raise ExplainabilityError(
                    "Missing conflict/exception explanation state: "
                    f"{name}"
                )

        if retrieval_class not in classification_rules:
            raise ExplainabilityError(
                "Unsupported retrieval class for conflict/exception handling."
            )

        disclosure_mode = classification_rules[
            retrieval_class
        ]

        conflict_present = (
            retrieval_class == "CONTESTED_MEMORY"
            or memory_state == "CONTESTED"
            or stability_state == "CONTESTED"
        )

        held_present = (
            retrieval_class == "HELD_MEMORY"
            or memory_state == "HELD"
            or stability_state == "HELD"
            or retention_state == "HOLD"
        )

        blocked_present = (
            retrieval_class == "BLOCKED_MEMORY"
            or memory_state == "BLOCKED"
            or stability_state == "BLOCKED"
        )

        historical_present = (
            retrieval_class == "HISTORICAL_MEMORY"
            or memory_state in (
                "SUPERSEDED",
                "RETIRED",
                "EXPIRED",
            )
            or stability_state in (
                "SUPERSEDED",
                "RETIRED",
                "EXPIRED",
            )
            or retention_state in (
                "SUPERSEDE",
                "RETIRE",
                "EXPIRE",
            )
        )

        weakened_present = (
            memory_state == "WEAKENED"
            or stability_state == "WEAKENED"
        )

        if blocked_present:
            conflict_present = False
            held_present = False

        exception_context_required = (
            conflict_present
            or held_present
            or blocked_present
            or historical_present
            or weakened_present
        )

        record_payload = {
            "memory_object_id":
                memory_object_id,

            "memory_state":
                memory_state,

            "stability_state":
                stability_state,

            "retention_state":
                retention_state,

            "retrieval_class":
                retrieval_class,

            "disclosure_mode":
                disclosure_mode,

            "conflict_present":
                conflict_present,

            "held_present":
                held_present,

            "blocked_present":
                blocked_present,

            "historical_present":
                historical_present,

            "weakened_present":
                weakened_present,

            "exception_context_required":
                exception_context_required,
        }

        serialized = json.dumps(
            record_payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )

        record_digest = hashlib.sha256(
            serialized.encode("utf-8")
        ).hexdigest()

        handling_records.append(
            {
                "schema":
                    "conflict_exception_explanation_handling_record_v1",

                "conflict_exception_handling_id":
                    "explainabilityconflict:v1:"
                    + record_digest,

                "memory_object_id":
                    memory_object_id,

                "source_evidence_provenance_mapping_id":
                    mapping[
                        "evidence_provenance_mapping_id"
                    ],

                "memory_state":
                    memory_state,

                "stability_state":
                    stability_state,

                "retention_state":
                    retention_state,

                "retrieval_class":
                    retrieval_class,

                "disclosure_mode":
                    disclosure_mode,

                "conflict_present":
                    conflict_present,

                "held_present":
                    held_present,

                "blocked_present":
                    blocked_present,

                "historical_present":
                    historical_present,

                "weakened_present":
                    weakened_present,

                "exception_context_required":
                    exception_context_required,

                "conflict_state_preserved":
                    True,

                "exception_state_preserved":
                    True,

                "minority_context_preserved":
                    True,

                "non_resolution_disclosed":
                    True,

                "state_label_preserved":
                    True,

                "retrieval_class_preserved":
                    True,

                "conflict_resolved":
                    False,

                "conflict_reclassified":
                    False,

                "exception_normalized_away":
                    False,

                "minority_context_suppressed":
                    False,

                "semantic_state_mutated":
                    False,

                "truth_adjudicated":
                    False,

                "target_selected":
                    False,

                "linking_decision_performed":
                    False,
            }
        )

    handling_records = tuple(
        handling_records
    )

    handling_contract = {
        "schema":
            "conflict_exception_explanation_handling_contract_v1",

        "canonical_owner":
            "EXPLAINABILITY",

        "source_owner":
            "SEMANTIC_MEMORY",

        "handling_is_explanatory_only":
            True,

        "certified_state_is_authoritative_for_explanation":
            True,

        "conflict_must_remain_conflict":
            True,

        "contested_state_must_remain_contested":
            True,

        "held_state_must_remain_held":
            True,

        "blocked_state_must_remain_blocked":
            True,

        "historical_state_must_remain_historical":
            True,

        "weakened_state_must_remain_weakened":
            True,

        "exceptions_must_be_preserved":
            True,

        "minority_context_must_be_preserved":
            True,

        "unresolved_state_must_be_disclosed":
            True,

        "non_default_readability_must_be_disclosed":
            True,

        "conflict_must_not_be_silently_resolved":
            True,

        "exception_must_not_be_normalized_away":
            True,

        "minority_context_must_not_be_suppressed":
            True,

        "absence_of_conflict_must_not_be_invented":
            True,

        "conflict_must_not_be_invented":
            True,

        "exception_must_not_be_invented":
            True,

        "handling_must_not_reclassify_conflict":
            True,

        "handling_must_not_change_memory_state":
            True,

        "handling_must_not_change_stability_state":
            True,

        "handling_must_not_change_retention_state":
            True,

        "handling_must_not_change_retrieval_class":
            True,

        "handling_must_not_adjudicate_truth":
            True,

        "handling_must_not_rescore_authority":
            True,

        "handling_must_not_redecide_claim_integrity":
            True,

        "handling_must_not_select_target":
            True,

        "handling_must_not_score_target":
            True,

        "handling_must_not_make_linking_decision":
            True,
    }

    bundle_payload = {
        "source_semantic_memory_package_id":
            source_package_id,

        "source_semantic_memory_package_digest":
            source_package_digest,

        "source_semantic_memory_lineage_root_id":
            source_lineage_root_id,

        "handling_ids":
            [
                item[
                    "conflict_exception_handling_id"
                ]
                for item in handling_records
            ],
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

    handling_bundle = {
        "schema":
            "conflict_exception_explanation_handling_bundle_v1",

        "conflict_exception_handling_bundle_id":
            "explainabilityconflictbundle:v1:"
            + bundle_digest,

        "conflict_exception_handling_bundle_digest":
            bundle_digest,

        "source_semantic_memory_package_id":
            source_package_id,

        "source_semantic_memory_package_digest":
            source_package_digest,

        "source_semantic_memory_lineage_root_id":
            source_lineage_root_id,

        "handling_records":
            handling_records,

        "handling_contract":
            handling_contract,

        "handling_record_count":
            len(
                handling_records
            ),

        "conflict_exception_handling_complete":
            True,

        "conflict_state_preserved":
            True,

        "exception_state_preserved":
            True,

        "minority_context_preserved":
            True,

        "non_resolution_preserved":
            True,

        "conflict_resolved":
            False,

        "conflict_reclassified":
            False,

        "exception_normalized_away":
            False,

        "minority_context_suppressed":
            False,

        "semantic_memory_mutated":
            False,

        "graph_mutated":
            False,

        "authority_rescored":
            False,

        "claim_integrity_redecided":
            False,

        "target_selected":
            False,

        "target_scored":
            False,

        "runtime_reasoning_performed":
            False,

        "linking_decision_performed":
            False,

        "explanation_generated":
            False,
    }

    return {
        "schema":
            "conflict_exception_explanation_handling_result_v1",

        "explainability_version":
            EXPLAINABILITY_VERSION,

        "phase":
            EXPLAINABILITY_PHASE,

        "patch":
            "4.6.29E",

        "status":
            "CONFLICT_EXCEPTION_EXPLANATION_HANDLING_COMPLETED",

        "source_semantic_memory_package_id":
            source_package_id,

        "source_semantic_memory_package_digest":
            source_package_digest,

        "source_semantic_memory_lineage_root_id":
            source_lineage_root_id,

        "source_memory_object_ids":
            tuple(
                source_memory_object_ids
            ),

        "source_memory_object_count":
            source_memory_object_count,

        "explainability_architecture":
            copy.deepcopy(
                architecture
            ),

        "explanation_scope_audience_contract_bundle":
            copy.deepcopy(
                scope_bundle
            ),

        "evidence_provenance_explanation_mapping_bundle":
            copy.deepcopy(
                mapping_bundle
            ),

        "conflict_exception_explanation_handling_bundle":
            handling_bundle,

        "evidence_provenance_explanation_mapping_result":
            copy.deepcopy(
                evidence_mapping_result
            ),

        "processing_boundaries": {
            "certified_semantic_memory_inspected":
                True,

            "explainability_architecture_defined":
                True,

            "explanation_scope_audience_contract_defined":
                True,

            "evidence_provenance_explanation_mapping_completed":
                True,

            "conflict_exception_explanation_handling_completed":
                True,

            "explanation_generated":
                False,

            "explanation_reasoning_performed":
                False,

            "semantic_memory_written":
                False,

            "semantic_memory_mutated":
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
        },

        "policy":
            "CERTIFIED_CONFLICT_EXCEPTION_EXPLANATION_HANDLING",

        "next":
            "confidence_uncertainty_explanation_contract",
    }

def define_confidence_uncertainty_explanation_contract_v1(
    conflict_exception_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.29F ? Confidence / Uncertainty Explanation Contract.

    Defines how certified Semantic Memory uncertainty, caution,
    confidence limitations, contested state, held state, blocked
    state, weakened state, historical state, and evidence limitations
    must be represented by Explainability.

    This stage defines contracts and uncertainty metadata only.
    It does not generate final explanation prose, create certainty,
    infer unsupported probabilities, adjudicate truth, or make
    downstream decisions.
    """

    if not isinstance(
        conflict_exception_result,
        dict,
    ):
        raise ExplainabilityError(
            "conflict_exception_result must be a dictionary."
        )

    expected = {
        "schema":
            "conflict_exception_explanation_handling_result_v1",

        "explainability_version":
            EXPLAINABILITY_VERSION,

        "phase":
            EXPLAINABILITY_PHASE,

        "patch":
            "4.6.29E",

        "status":
            "CONFLICT_EXCEPTION_EXPLANATION_HANDLING_COMPLETED",

        "policy":
            "CERTIFIED_CONFLICT_EXCEPTION_EXPLANATION_HANDLING",

        "next":
            "confidence_uncertainty_explanation_contract",
    }

    for key, expected_value in expected.items():

        if conflict_exception_result.get(key) != expected_value:
            raise ExplainabilityError(
                "Invalid 4.6.29E lifecycle field: "
                f"{key}"
            )

    architecture = conflict_exception_result.get(
        "explainability_architecture"
    )

    scope_bundle = conflict_exception_result.get(
        "explanation_scope_audience_contract_bundle"
    )

    evidence_bundle = conflict_exception_result.get(
        "evidence_provenance_explanation_mapping_bundle"
    )

    conflict_bundle = conflict_exception_result.get(
        "conflict_exception_explanation_handling_bundle"
    )

    boundaries = conflict_exception_result.get(
        "processing_boundaries"
    )

    for name, value in (
        (
            "explainability_architecture",
            architecture,
        ),
        (
            "explanation_scope_audience_contract_bundle",
            scope_bundle,
        ),
        (
            "evidence_provenance_explanation_mapping_bundle",
            evidence_bundle,
        ),
        (
            "conflict_exception_explanation_handling_bundle",
            conflict_bundle,
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
            raise ExplainabilityError(
                f"{name} must be a dictionary."
            )

    if (
        architecture.get("schema")
        != "explainability_architecture_v1"
    ):
        raise ExplainabilityError(
            "Invalid Explainability architecture schema."
        )

    if (
        conflict_bundle.get("schema")
        != "conflict_exception_explanation_handling_bundle_v1"
    ):
        raise ExplainabilityError(
            "Invalid conflict/exception handling bundle schema."
        )

    if conflict_bundle.get(
        "conflict_exception_handling_complete"
    ) is not True:
        raise ExplainabilityError(
            "Conflict/exception handling is incomplete."
        )

    if conflict_bundle.get(
        "conflict_state_preserved"
    ) is not True:
        raise ExplainabilityError(
            "Conflict state was not preserved."
        )

    if conflict_bundle.get(
        "exception_state_preserved"
    ) is not True:
        raise ExplainabilityError(
            "Exception state was not preserved."
        )

    if conflict_bundle.get(
        "minority_context_preserved"
    ) is not True:
        raise ExplainabilityError(
            "Minority context was not preserved."
        )

    if conflict_bundle.get(
        "non_resolution_preserved"
    ) is not True:
        raise ExplainabilityError(
            "Non-resolution state was not preserved."
        )

    for required_component in (
        "UNCERTAINTY",
        "CONFLICT_CONTEXT",
        "EXCEPTION_CONTEXT",
        "STABILITY_STATE",
        "RETENTION_STATE",
        "RETRIEVAL_CLASS",
        "EVIDENCE_CONTEXT",
        "AUTHORITY_CONTEXT",
        "BOUNDARY_DISCLOSURE",
    ):
        if required_component not in architecture.get(
            "explanation_components",
            (),
        ):
            raise ExplainabilityError(
                "Required confidence/uncertainty component missing: "
                f"{required_component}"
            )

    for flag in (
        "certified_semantic_memory_inspected",
        "explainability_architecture_defined",
        "explanation_scope_audience_contract_defined",
        "evidence_provenance_explanation_mapping_completed",
        "conflict_exception_explanation_handling_completed",
    ):
        if boundaries.get(flag) is not True:
            raise ExplainabilityError(
                "Required upstream Explainability state missing: "
                f"{flag}"
            )

    for flag in (
        "explanation_generated",
        "explanation_reasoning_performed",
        "semantic_memory_written",
        "semantic_memory_mutated",
        "memory_persistence_performed",
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
            raise ExplainabilityError(
                "Unsafe 4.6.29F input boundary state: "
                f"{flag}"
            )

    source_package_id = conflict_exception_result.get(
        "source_semantic_memory_package_id"
    )

    source_package_digest = conflict_exception_result.get(
        "source_semantic_memory_package_digest"
    )

    source_lineage_root_id = conflict_exception_result.get(
        "source_semantic_memory_lineage_root_id"
    )

    source_memory_object_ids = conflict_exception_result.get(
        "source_memory_object_ids"
    )

    source_memory_object_count = conflict_exception_result.get(
        "source_memory_object_count"
    )

    if not isinstance(
        source_memory_object_ids,
        tuple,
    ):
        raise ExplainabilityError(
            "source_memory_object_ids must be a tuple."
        )

    if (
        not isinstance(
            source_memory_object_count,
            int,
        )
        or source_memory_object_count
        != len(source_memory_object_ids)
    ):
        raise ExplainabilityError(
            "Source memory object count mismatch."
        )

    handling_records = conflict_bundle.get(
        "handling_records"
    )

    if not isinstance(
        handling_records,
        tuple,
    ):
        raise ExplainabilityError(
            "handling_records must be a tuple."
        )

    if len(
        handling_records
    ) != source_memory_object_count:
        raise ExplainabilityError(
            "Conflict/exception handling count mismatch."
        )

    handling_by_memory_id = {}

    for record in handling_records:

        if not isinstance(
            record,
            dict,
        ):
            raise ExplainabilityError(
                "Conflict/exception handling record must be a dictionary."
            )

        if (
            record.get("schema")
            != "conflict_exception_explanation_handling_record_v1"
        ):
            raise ExplainabilityError(
                "Invalid conflict/exception handling record schema."
            )

        memory_object_id = record.get(
            "memory_object_id"
        )

        if (
            not isinstance(
                memory_object_id,
                str,
            )
            or not memory_object_id
        ):
            raise ExplainabilityError(
                "Conflict/exception handling memory object ID is missing."
            )

        if memory_object_id in handling_by_memory_id:
            raise ExplainabilityError(
                "Duplicate conflict/exception memory object ID."
            )

        handling_by_memory_id[
            memory_object_id
        ] = record

    if set(
        source_memory_object_ids
    ) != set(
        handling_by_memory_id
    ):
        raise ExplainabilityError(
            "Confidence/uncertainty source identity mismatch."
        )

    uncertainty_records = []

    for memory_object_id in source_memory_object_ids:

        handling = handling_by_memory_id[
            memory_object_id
        ]

        memory_state = handling.get(
            "memory_state"
        )

        stability_state = handling.get(
            "stability_state"
        )

        retention_state = handling.get(
            "retention_state"
        )

        retrieval_class = handling.get(
            "retrieval_class"
        )

        conflict_present = handling.get(
            "conflict_present"
        )

        held_present = handling.get(
            "held_present"
        )

        blocked_present = handling.get(
            "blocked_present"
        )

        historical_present = handling.get(
            "historical_present"
        )

        weakened_present = handling.get(
            "weakened_present"
        )

        for name, value in (
            (
                "memory_state",
                memory_state,
            ),
            (
                "stability_state",
                stability_state,
            ),
            (
                "retention_state",
                retention_state,
            ),
            (
                "retrieval_class",
                retrieval_class,
            ),
        ):
            if not isinstance(
                value,
                str,
            ) or not value:
                raise ExplainabilityError(
                    "Missing confidence/uncertainty state: "
                    f"{name}"
                )

        for name, value in (
            (
                "conflict_present",
                conflict_present,
            ),
            (
                "held_present",
                held_present,
            ),
            (
                "blocked_present",
                blocked_present,
            ),
            (
                "historical_present",
                historical_present,
            ),
            (
                "weakened_present",
                weakened_present,
            ),
        ):
            if not isinstance(
                value,
                bool,
            ):
                raise ExplainabilityError(
                    "Invalid uncertainty boolean: "
                    f"{name}"
                )

        if blocked_present:
            uncertainty_level = "MAXIMUM_CAUTION"

        elif held_present:
            uncertainty_level = "HIGH_CAUTION"

        elif conflict_present:
            uncertainty_level = "HIGH_CAUTION"

        elif weakened_present:
            uncertainty_level = "ELEVATED_CAUTION"

        elif historical_present:
            uncertainty_level = "CONTEXTUAL_CAUTION"

        elif (
            memory_state == "ACTIVE"
            and stability_state == "STABLE"
            and retention_state == "RETAIN"
            and retrieval_class == "ACTIVE_MEMORY"
        ):
            uncertainty_level = "STANDARD_CAUTION"

        else:
            uncertainty_level = "ELEVATED_CAUTION"

        if uncertainty_level == "STANDARD_CAUTION":
            confidence_expression = "SUPPORTED_BY_CURRENT_CERTIFIED_MEMORY_STATE"

        elif uncertainty_level == "CONTEXTUAL_CAUTION":
            confidence_expression = "HISTORICAL_OR_NON_CURRENT_CONTEXT_REQUIRES_CAUTION"

        elif uncertainty_level == "ELEVATED_CAUTION":
            confidence_expression = "CERTIFIED_STATE_CONTAINS_WEAKENING_OR_LIMITATION"

        elif uncertainty_level == "HIGH_CAUTION":
            confidence_expression = "CERTIFIED_STATE_IS_CONTESTED_OR_HELD"

        elif uncertainty_level == "MAXIMUM_CAUTION":
            confidence_expression = "CERTIFIED_STATE_IS_BLOCKED_AND_NOT_DEFAULT_READABLE"

        else:
            raise ExplainabilityError(
                "Unsupported uncertainty level."
            )

        numeric_confidence_available = False
        numeric_confidence_invented = False

        uncertainty_disclosure_required = (
            uncertainty_level
            != "STANDARD_CAUTION"
        )

        truth_separation_required = True

        record_payload = {
            "memory_object_id":
                memory_object_id,

            "memory_state":
                memory_state,

            "stability_state":
                stability_state,

            "retention_state":
                retention_state,

            "retrieval_class":
                retrieval_class,

            "uncertainty_level":
                uncertainty_level,

            "confidence_expression":
                confidence_expression,

            "conflict_present":
                conflict_present,

            "held_present":
                held_present,

            "blocked_present":
                blocked_present,

            "historical_present":
                historical_present,

            "weakened_present":
                weakened_present,
        }

        serialized = json.dumps(
            record_payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )

        record_digest = hashlib.sha256(
            serialized.encode("utf-8")
        ).hexdigest()

        uncertainty_records.append(
            {
                "schema":
                    "confidence_uncertainty_explanation_record_v1",

                "confidence_uncertainty_record_id":
                    "explainabilityuncertainty:v1:"
                    + record_digest,

                "memory_object_id":
                    memory_object_id,

                "source_conflict_exception_handling_id":
                    handling[
                        "conflict_exception_handling_id"
                    ],

                "memory_state":
                    memory_state,

                "stability_state":
                    stability_state,

                "retention_state":
                    retention_state,

                "retrieval_class":
                    retrieval_class,

                "uncertainty_level":
                    uncertainty_level,

                "confidence_expression":
                    confidence_expression,

                "uncertainty_disclosure_required":
                    uncertainty_disclosure_required,

                "truth_separation_required":
                    truth_separation_required,

                "numeric_confidence_available":
                    numeric_confidence_available,

                "numeric_confidence_invented":
                    numeric_confidence_invented,

                "uncertainty_preserved":
                    True,

                "conflict_context_preserved":
                    True,

                "exception_context_preserved":
                    True,

                "stability_context_preserved":
                    True,

                "retention_context_preserved":
                    True,

                "retrieval_context_preserved":
                    True,

                "evidence_limitations_preserved":
                    True,

                "authority_context_preserved":
                    True,

                "confidence_overstated":
                    False,

                "uncertainty_hidden":
                    False,

                "truth_adjudicated":
                    False,

                "semantic_state_mutated":
                    False,

                "authority_rescored":
                    False,

                "claim_integrity_redecided":
                    False,

                "conflict_reclassified":
                    False,

                "target_selected":
                    False,

                "target_scored":
                    False,

                "runtime_reasoning_performed":
                    False,

                "linking_decision_performed":
                    False,
            }
        )

    uncertainty_records = tuple(
        uncertainty_records
    )

    uncertainty_contract = {
        "schema":
            "confidence_uncertainty_explanation_contract_v1",

        "canonical_owner":
            "EXPLAINABILITY",

        "source_owner":
            "SEMANTIC_MEMORY",

        "uncertainty_is_explanatory_not_decisional":
            True,

        "certified_state_is_source_of_uncertainty_context":
            True,

        "confidence_must_be_derived_only_from_certified_available_state":
            True,

        "confidence_must_not_be_invented":
            True,

        "numeric_confidence_must_not_be_invented":
            True,

        "probability_must_not_be_invented":
            True,

        "uncertainty_must_be_preserved":
            True,

        "uncertainty_must_be_disclosed_when_material":
            True,

        "conflict_must_increase_caution":
            True,

        "held_state_must_increase_caution":
            True,

        "blocked_state_requires_maximum_caution":
            True,

        "weakened_state_must_increase_caution":
            True,

        "historical_state_requires_contextual_caution":
            True,

        "stable_active_memory_still_not_truth":
            True,

        "absence_of_conflict_does_not_establish_truth":
            True,

        "high_authority_does_not_establish_truth":
            True,

        "repeated_learning_does_not_establish_truth":
            True,

        "stability_does_not_establish_truth":
            True,

        "retention_does_not_establish_truth":
            True,

        "default_readability_does_not_establish_truth":
            True,

        "confidence_language_must_not_exceed_source_state":
            True,

        "uncertainty_language_must_not_understate_source_state":
            True,

        "audience_change_must_not_change_uncertainty_meaning":
            True,

        "uncertainty_must_not_be_hidden_for_simplicity":
            True,

        "conflict_must_not_be_hidden_for_confidence":
            True,

        "evidence_limitations_must_not_be_hidden":
            True,

        "missing_numeric_confidence_must_remain_missing":
            True,

        "contract_must_not_adjudicate_truth":
            True,

        "contract_must_not_rescore_authority":
            True,

        "contract_must_not_redecide_claim_integrity":
            True,

        "contract_must_not_reclassify_conflict":
            True,

        "contract_must_not_change_memory_state":
            True,

        "contract_must_not_change_stability_state":
            True,

        "contract_must_not_change_retention_state":
            True,

        "contract_must_not_change_retrieval_class":
            True,

        "contract_must_not_select_target":
            True,

        "contract_must_not_score_target":
            True,

        "contract_must_not_make_linking_decision":
            True,
    }

    bundle_payload = {
        "source_semantic_memory_package_id":
            source_package_id,

        "source_semantic_memory_package_digest":
            source_package_digest,

        "source_semantic_memory_lineage_root_id":
            source_lineage_root_id,

        "uncertainty_record_ids":
            [
                item[
                    "confidence_uncertainty_record_id"
                ]
                for item in uncertainty_records
            ],
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

    uncertainty_bundle = {
        "schema":
            "confidence_uncertainty_explanation_contract_bundle_v1",

        "confidence_uncertainty_contract_bundle_id":
            "explainabilityuncertaintybundle:v1:"
            + bundle_digest,

        "confidence_uncertainty_contract_bundle_digest":
            bundle_digest,

        "source_semantic_memory_package_id":
            source_package_id,

        "source_semantic_memory_package_digest":
            source_package_digest,

        "source_semantic_memory_lineage_root_id":
            source_lineage_root_id,

        "uncertainty_records":
            uncertainty_records,

        "uncertainty_contract":
            uncertainty_contract,

        "uncertainty_record_count":
            len(
                uncertainty_records
            ),

        "confidence_uncertainty_contract_complete":
            True,

        "uncertainty_preserved":
            True,

        "confidence_not_overstated":
            True,

        "numeric_confidence_not_invented":
            True,

        "truth_separation_preserved":
            True,

        "semantic_memory_mutated":
            False,

        "graph_mutated":
            False,

        "authority_rescored":
            False,

        "claim_integrity_redecided":
            False,

        "conflict_reclassified":
            False,

        "target_selected":
            False,

        "target_scored":
            False,

        "runtime_reasoning_performed":
            False,

        "linking_decision_performed":
            False,

        "explanation_generated":
            False,
    }

    return {
        "schema":
            "confidence_uncertainty_explanation_contract_result_v1",

        "explainability_version":
            EXPLAINABILITY_VERSION,

        "phase":
            EXPLAINABILITY_PHASE,

        "patch":
            "4.6.29F",

        "status":
            "CONFIDENCE_UNCERTAINTY_EXPLANATION_CONTRACT_DEFINED",

        "source_semantic_memory_package_id":
            source_package_id,

        "source_semantic_memory_package_digest":
            source_package_digest,

        "source_semantic_memory_lineage_root_id":
            source_lineage_root_id,

        "source_memory_object_ids":
            tuple(
                source_memory_object_ids
            ),

        "source_memory_object_count":
            source_memory_object_count,

        "explainability_architecture":
            copy.deepcopy(
                architecture
            ),

        "explanation_scope_audience_contract_bundle":
            copy.deepcopy(
                scope_bundle
            ),

        "evidence_provenance_explanation_mapping_bundle":
            copy.deepcopy(
                evidence_bundle
            ),

        "conflict_exception_explanation_handling_bundle":
            copy.deepcopy(
                conflict_bundle
            ),

        "confidence_uncertainty_explanation_contract_bundle":
            uncertainty_bundle,

        "conflict_exception_explanation_handling_result":
            copy.deepcopy(
                conflict_exception_result
            ),

        "processing_boundaries": {
            "certified_semantic_memory_inspected":
                True,

            "explainability_architecture_defined":
                True,

            "explanation_scope_audience_contract_defined":
                True,

            "evidence_provenance_explanation_mapping_completed":
                True,

            "conflict_exception_explanation_handling_completed":
                True,

            "confidence_uncertainty_explanation_contract_defined":
                True,

            "explanation_generated":
                False,

            "explanation_reasoning_performed":
                False,

            "semantic_memory_written":
                False,

            "semantic_memory_mutated":
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
        },

        "policy":
            "CERTIFIED_CONFIDENCE_UNCERTAINTY_EXPLANATION_CONTRACT",

        "next":
            "decision_trace_explanation_construction",
    }

def construct_decision_trace_explanation_v1(
    uncertainty_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.29G ? Decision-Trace Explanation Construction.

    Constructs Explainability-owned decision-trace metadata from the
    already certified Semantic Memory / provenance / conflict /
    uncertainty chain.

    The trace exposes certified available state and component order.
    It does not create a new decision, infer missing upstream steps,
    fabricate causality, select targets, or make linking decisions.
    """

    if not isinstance(
        uncertainty_result,
        dict,
    ):
        raise ExplainabilityError(
            "uncertainty_result must be a dictionary."
        )

    expected = {
        "schema":
            "confidence_uncertainty_explanation_contract_result_v1",

        "explainability_version":
            EXPLAINABILITY_VERSION,

        "phase":
            EXPLAINABILITY_PHASE,

        "patch":
            "4.6.29F",

        "status":
            "CONFIDENCE_UNCERTAINTY_EXPLANATION_CONTRACT_DEFINED",

        "policy":
            "CERTIFIED_CONFIDENCE_UNCERTAINTY_EXPLANATION_CONTRACT",

        "next":
            "decision_trace_explanation_construction",
    }

    for key, expected_value in expected.items():

        if uncertainty_result.get(key) != expected_value:
            raise ExplainabilityError(
                "Invalid 4.6.29F lifecycle field: "
                f"{key}"
            )

    architecture = uncertainty_result.get(
        "explainability_architecture"
    )

    scope_bundle = uncertainty_result.get(
        "explanation_scope_audience_contract_bundle"
    )

    evidence_bundle = uncertainty_result.get(
        "evidence_provenance_explanation_mapping_bundle"
    )

    conflict_bundle = uncertainty_result.get(
        "conflict_exception_explanation_handling_bundle"
    )

    uncertainty_bundle = uncertainty_result.get(
        "confidence_uncertainty_explanation_contract_bundle"
    )

    boundaries = uncertainty_result.get(
        "processing_boundaries"
    )

    for name, value in (
        (
            "explainability_architecture",
            architecture,
        ),
        (
            "explanation_scope_audience_contract_bundle",
            scope_bundle,
        ),
        (
            "evidence_provenance_explanation_mapping_bundle",
            evidence_bundle,
        ),
        (
            "conflict_exception_explanation_handling_bundle",
            conflict_bundle,
        ),
        (
            "confidence_uncertainty_explanation_contract_bundle",
            uncertainty_bundle,
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
            raise ExplainabilityError(
                f"{name} must be a dictionary."
            )

    if (
        architecture.get("schema")
        != "explainability_architecture_v1"
    ):
        raise ExplainabilityError(
            "Invalid Explainability architecture schema."
        )

    if "DECISION_TRACE" not in architecture.get(
        "explanation_scope_classes",
        (),
    ):
        raise ExplainabilityError(
            "Decision-trace explanation scope is missing."
        )

    if "DECISION_TRACE" not in architecture.get(
        "explanation_components",
        (),
    ):
        raise ExplainabilityError(
            "Decision-trace explanation component is missing."
        )

    if uncertainty_bundle.get(
        "confidence_uncertainty_contract_complete"
    ) is not True:
        raise ExplainabilityError(
            "Confidence/uncertainty contract is incomplete."
        )

    if uncertainty_bundle.get(
        "uncertainty_preserved"
    ) is not True:
        raise ExplainabilityError(
            "Uncertainty was not preserved."
        )

    if uncertainty_bundle.get(
        "truth_separation_preserved"
    ) is not True:
        raise ExplainabilityError(
            "Truth separation was not preserved."
        )

    for flag in (
        "certified_semantic_memory_inspected",
        "explainability_architecture_defined",
        "explanation_scope_audience_contract_defined",
        "evidence_provenance_explanation_mapping_completed",
        "conflict_exception_explanation_handling_completed",
        "confidence_uncertainty_explanation_contract_defined",
    ):
        if boundaries.get(flag) is not True:
            raise ExplainabilityError(
                "Required upstream Explainability state missing: "
                f"{flag}"
            )

    for flag in (
        "explanation_generated",
        "explanation_reasoning_performed",
        "semantic_memory_written",
        "semantic_memory_mutated",
        "memory_persistence_performed",
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
            raise ExplainabilityError(
                "Unsafe 4.6.29G input boundary state: "
                f"{flag}"
            )

    source_package_id = uncertainty_result.get(
        "source_semantic_memory_package_id"
    )

    source_package_digest = uncertainty_result.get(
        "source_semantic_memory_package_digest"
    )

    source_lineage_root_id = uncertainty_result.get(
        "source_semantic_memory_lineage_root_id"
    )

    source_memory_object_ids = uncertainty_result.get(
        "source_memory_object_ids"
    )

    source_memory_object_count = uncertainty_result.get(
        "source_memory_object_count"
    )

    if not isinstance(
        source_memory_object_ids,
        tuple,
    ):
        raise ExplainabilityError(
            "source_memory_object_ids must be a tuple."
        )

    if (
        not isinstance(
            source_memory_object_count,
            int,
        )
        or source_memory_object_count
        != len(source_memory_object_ids)
    ):
        raise ExplainabilityError(
            "Source memory object count mismatch."
        )

    evidence_records = evidence_bundle.get(
        "mapping_records"
    )

    conflict_records = conflict_bundle.get(
        "handling_records"
    )

    uncertainty_records = uncertainty_bundle.get(
        "uncertainty_records"
    )

    if not isinstance(
        evidence_records,
        tuple,
    ):
        raise ExplainabilityError(
            "Evidence/provenance mapping records must be a tuple."
        )

    if not isinstance(
        conflict_records,
        tuple,
    ):
        raise ExplainabilityError(
            "Conflict/exception handling records must be a tuple."
        )

    if not isinstance(
        uncertainty_records,
        tuple,
    ):
        raise ExplainabilityError(
            "Uncertainty records must be a tuple."
        )

    expected_count = source_memory_object_count

    if not (
        len(evidence_records)
        == len(conflict_records)
        == len(uncertainty_records)
        == expected_count
    ):
        raise ExplainabilityError(
            "Decision-trace source record counts do not align."
        )

    def index_by_memory_id(
        records,
        schema,
    ):

        result = {}

        for record in records:

            if not isinstance(
                record,
                dict,
            ):
                raise ExplainabilityError(
                    "Decision-trace source record must be a dictionary."
                )

            if record.get(
                "schema"
            ) != schema:
                raise ExplainabilityError(
                    "Invalid decision-trace source record schema."
                )

            memory_object_id = record.get(
                "memory_object_id"
            )

            if (
                not isinstance(
                    memory_object_id,
                    str,
                )
                or not memory_object_id
            ):
                raise ExplainabilityError(
                    "Decision-trace memory object ID is missing."
                )

            if memory_object_id in result:
                raise ExplainabilityError(
                    "Duplicate decision-trace source memory object ID."
                )

            result[
                memory_object_id
            ] = record

        return result

    evidence_by_id = index_by_memory_id(
        evidence_records,
        "evidence_provenance_explanation_mapping_record_v1",
    )

    conflict_by_id = index_by_memory_id(
        conflict_records,
        "conflict_exception_explanation_handling_record_v1",
    )

    uncertainty_by_id = index_by_memory_id(
        uncertainty_records,
        "confidence_uncertainty_explanation_record_v1",
    )

    expected_ids = set(
        source_memory_object_ids
    )

    if set(
        evidence_by_id
    ) != expected_ids:
        raise ExplainabilityError(
            "Evidence trace identity mismatch."
        )

    if set(
        conflict_by_id
    ) != expected_ids:
        raise ExplainabilityError(
            "Conflict trace identity mismatch."
        )

    if set(
        uncertainty_by_id
    ) != expected_ids:
        raise ExplainabilityError(
            "Uncertainty trace identity mismatch."
        )

    trace_records = []

    for memory_object_id in source_memory_object_ids:

        evidence = evidence_by_id[
            memory_object_id
        ]

        conflict = conflict_by_id[
            memory_object_id
        ]

        uncertainty = uncertainty_by_id[
            memory_object_id
        ]

        source_learning_object_id = evidence.get(
            "source_learning_object_id"
        )

        memory_lineage_record_id = evidence.get(
            "memory_lineage_record_id"
        )

        retrieval_metadata_id = evidence.get(
            "retrieval_metadata_id"
        )

        evidence_mapping_id = evidence.get(
            "evidence_provenance_mapping_id"
        )

        conflict_handling_id = conflict.get(
            "conflict_exception_handling_id"
        )

        uncertainty_record_id = uncertainty.get(
            "confidence_uncertainty_record_id"
        )

        for name, value in (
            (
                "source_learning_object_id",
                source_learning_object_id,
            ),
            (
                "memory_lineage_record_id",
                memory_lineage_record_id,
            ),
            (
                "retrieval_metadata_id",
                retrieval_metadata_id,
            ),
            (
                "evidence_mapping_id",
                evidence_mapping_id,
            ),
            (
                "conflict_handling_id",
                conflict_handling_id,
            ),
            (
                "uncertainty_record_id",
                uncertainty_record_id,
            ),
        ):
            if not isinstance(
                value,
                str,
            ) or not value:
                raise ExplainabilityError(
                    "Missing certified decision-trace component: "
                    f"{name}"
                )

        trace_steps = (
            {
                "step":
                    1,

                "component":
                    "SOURCE_LEARNING_REFERENCE",

                "reference":
                    source_learning_object_id,

                "certified_available":
                    True,
            },

            {
                "step":
                    2,

                "component":
                    "SEMANTIC_MEMORY_OBJECT",

                "reference":
                    memory_object_id,

                "certified_available":
                    True,
            },

            {
                "step":
                    3,

                "component":
                    "PROVENANCE_LINEAGE",

                "reference":
                    memory_lineage_record_id,

                "certified_available":
                    True,
            },

            {
                "step":
                    4,

                "component":
                    "EVIDENCE_PROVENANCE_MAPPING",

                "reference":
                    evidence_mapping_id,

                "certified_available":
                    True,
            },

            {
                "step":
                    5,

                "component":
                    "CONFLICT_EXCEPTION_HANDLING",

                "reference":
                    conflict_handling_id,

                "certified_available":
                    True,
            },

            {
                "step":
                    6,

                "component":
                    "CONFIDENCE_UNCERTAINTY_CONTEXT",

                "reference":
                    uncertainty_record_id,

                "certified_available":
                    True,
            },

            {
                "step":
                    7,

                "component":
                    "RETRIEVAL_STATE",

                "reference":
                    retrieval_metadata_id,

                "certified_available":
                    True,
            },
        )

        trace_payload = {
            "memory_object_id":
                memory_object_id,

            "steps":
                trace_steps,

            "uncertainty_level":
                uncertainty[
                    "uncertainty_level"
                ],

            "retrieval_class":
                uncertainty[
                    "retrieval_class"
                ],
        }

        serialized = json.dumps(
            trace_payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )

        trace_digest = hashlib.sha256(
            serialized.encode("utf-8")
        ).hexdigest()

        trace_records.append(
            {
                "schema":
                    "decision_trace_explanation_record_v1",

                "decision_trace_id":
                    "explainabilitytrace:v1:"
                    + trace_digest,

                "memory_object_id":
                    memory_object_id,

                "trace_steps":
                    trace_steps,

                "trace_step_count":
                    len(
                        trace_steps
                    ),

                "trace_order_certified":
                    True,

                "trace_complete_for_available_components":
                    True,

                "source_learning_reference_preserved":
                    True,

                "semantic_memory_identity_preserved":
                    True,

                "provenance_lineage_preserved":
                    True,

                "evidence_provenance_mapping_preserved":
                    True,

                "conflict_exception_context_preserved":
                    True,

                "uncertainty_context_preserved":
                    True,

                "retrieval_state_preserved":
                    True,

                "missing_trace_component_fabricated":
                    False,

                "missing_upstream_decision_inferred":
                    False,

                "causal_reason_fabricated":
                    False,

                "new_decision_created":
                    False,

                "semantic_state_mutated":
                    False,

                "truth_adjudicated":
                    False,

                "authority_rescored":
                    False,

                "claim_integrity_redecided":
                    False,

                "conflict_reclassified":
                    False,

                "target_selected":
                    False,

                "target_scored":
                    False,

                "runtime_reasoning_performed":
                    False,

                "linking_decision_performed":
                    False,
            }
        )

    trace_records = tuple(
        trace_records
    )

    trace_contract = {
        "schema":
            "decision_trace_explanation_contract_v1",

        "canonical_owner":
            "EXPLAINABILITY",

        "source_owner":
            "SEMANTIC_MEMORY",

        "trace_existing_certified_state_only":
            True,

        "trace_must_preserve_component_identity":
            True,

        "trace_must_preserve_certified_order":
            True,

        "trace_must_disclose_missing_components":
            True,

        "trace_must_not_infer_missing_upstream_decisions":
            True,

        "trace_must_not_fabricate_causal_reason":
            True,

        "trace_must_not_fabricate_provenance":
            True,

        "trace_must_not_fabricate_evidence":
            True,

        "trace_must_not_fabricate_conflict":
            True,

        "trace_must_not_fabricate_uncertainty":
            True,

        "trace_must_not_create_new_decision":
            True,

        "trace_must_not_adjudicate_truth":
            True,

        "trace_must_not_rescore_authority":
            True,

        "trace_must_not_redecide_claim_integrity":
            True,

        "trace_must_not_reclassify_conflict":
            True,

        "trace_must_not_change_memory_state":
            True,

        "trace_must_not_change_stability_state":
            True,

        "trace_must_not_change_retention_state":
            True,

        "trace_must_not_change_retrieval_class":
            True,

        "trace_must_not_select_target":
            True,

        "trace_must_not_score_target":
            True,

        "trace_must_not_perform_runtime_reasoning":
            True,

        "trace_must_not_make_linking_decision":
            True,

        "trace_must_not_create_editor_highlight":
            True,
    }

    bundle_payload = {
        "source_semantic_memory_package_id":
            source_package_id,

        "source_semantic_memory_package_digest":
            source_package_digest,

        "source_semantic_memory_lineage_root_id":
            source_lineage_root_id,

        "decision_trace_ids":
            [
                item[
                    "decision_trace_id"
                ]
                for item in trace_records
            ],
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

    trace_bundle = {
        "schema":
            "decision_trace_explanation_bundle_v1",

        "decision_trace_bundle_id":
            "explainabilitytracebundle:v1:"
            + bundle_digest,

        "decision_trace_bundle_digest":
            bundle_digest,

        "source_semantic_memory_package_id":
            source_package_id,

        "source_semantic_memory_package_digest":
            source_package_digest,

        "source_semantic_memory_lineage_root_id":
            source_lineage_root_id,

        "decision_trace_records":
            trace_records,

        "decision_trace_contract":
            trace_contract,

        "decision_trace_record_count":
            len(
                trace_records
            ),

        "decision_trace_construction_complete":
            True,

        "certified_component_identity_preserved":
            True,

        "certified_trace_order_preserved":
            True,

        "uncertainty_context_preserved":
            True,

        "conflict_exception_context_preserved":
            True,

        "new_decision_created":
            False,

        "causal_reason_fabricated":
            False,

        "missing_upstream_decision_inferred":
            False,

        "semantic_memory_mutated":
            False,

        "graph_mutated":
            False,

        "authority_rescored":
            False,

        "claim_integrity_redecided":
            False,

        "conflict_reclassified":
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

        "explanation_generated":
            False,
    }

    return {
        "schema":
            "decision_trace_explanation_construction_result_v1",

        "explainability_version":
            EXPLAINABILITY_VERSION,

        "phase":
            EXPLAINABILITY_PHASE,

        "patch":
            "4.6.29G",

        "status":
            "DECISION_TRACE_EXPLANATION_CONSTRUCTION_COMPLETED",

        "source_semantic_memory_package_id":
            source_package_id,

        "source_semantic_memory_package_digest":
            source_package_digest,

        "source_semantic_memory_lineage_root_id":
            source_lineage_root_id,

        "source_memory_object_ids":
            tuple(
                source_memory_object_ids
            ),

        "source_memory_object_count":
            source_memory_object_count,

        "explainability_architecture":
            copy.deepcopy(
                architecture
            ),

        "explanation_scope_audience_contract_bundle":
            copy.deepcopy(
                scope_bundle
            ),

        "evidence_provenance_explanation_mapping_bundle":
            copy.deepcopy(
                evidence_bundle
            ),

        "conflict_exception_explanation_handling_bundle":
            copy.deepcopy(
                conflict_bundle
            ),

        "confidence_uncertainty_explanation_contract_bundle":
            copy.deepcopy(
                uncertainty_bundle
            ),

        "decision_trace_explanation_bundle":
            trace_bundle,

        "confidence_uncertainty_explanation_contract_result":
            copy.deepcopy(
                uncertainty_result
            ),

        "processing_boundaries": {
            "certified_semantic_memory_inspected":
                True,

            "explainability_architecture_defined":
                True,

            "explanation_scope_audience_contract_defined":
                True,

            "evidence_provenance_explanation_mapping_completed":
                True,

            "conflict_exception_explanation_handling_completed":
                True,

            "confidence_uncertainty_explanation_contract_defined":
                True,

            "decision_trace_explanation_construction_completed":
                True,

            "explanation_generated":
                False,

            "explanation_reasoning_performed":
                False,

            "semantic_memory_written":
                False,

            "semantic_memory_mutated":
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
        },

        "policy":
            "CERTIFIED_DECISION_TRACE_EXPLANATION_CONSTRUCTION",

        "next":
            "user_facing_explanation_construction",
    }

def construct_user_facing_explanation_v1(
    decision_trace_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.29H ? User-Facing Explanation Construction.

    Constructs concise, audience-appropriate explanations from the
    certified Explainability chain.

    Presentation may be simplified for an end user, but semantic
    meaning, uncertainty, conflict, retrieval state, and non-truth
    status must remain unchanged.

    This stage generates explanation artifacts only.
    It does not mutate semantic state, create decisions, select targets,
    or perform runtime reasoning.
    """

    if not isinstance(
        decision_trace_result,
        dict,
    ):
        raise ExplainabilityError(
            "decision_trace_result must be a dictionary."
        )

    expected = {
        "schema":
            "decision_trace_explanation_construction_result_v1",

        "explainability_version":
            EXPLAINABILITY_VERSION,

        "phase":
            EXPLAINABILITY_PHASE,

        "patch":
            "4.6.29G",

        "status":
            "DECISION_TRACE_EXPLANATION_CONSTRUCTION_COMPLETED",

        "policy":
            "CERTIFIED_DECISION_TRACE_EXPLANATION_CONSTRUCTION",

        "next":
            "user_facing_explanation_construction",
    }

    for key, expected_value in expected.items():

        if decision_trace_result.get(key) != expected_value:
            raise ExplainabilityError(
                "Invalid 4.6.29G lifecycle field: "
                f"{key}"
            )

    architecture = decision_trace_result.get(
        "explainability_architecture"
    )

    scope_bundle = decision_trace_result.get(
        "explanation_scope_audience_contract_bundle"
    )

    evidence_bundle = decision_trace_result.get(
        "evidence_provenance_explanation_mapping_bundle"
    )

    conflict_bundle = decision_trace_result.get(
        "conflict_exception_explanation_handling_bundle"
    )

    uncertainty_bundle = decision_trace_result.get(
        "confidence_uncertainty_explanation_contract_bundle"
    )

    trace_bundle = decision_trace_result.get(
        "decision_trace_explanation_bundle"
    )

    boundaries = decision_trace_result.get(
        "processing_boundaries"
    )

    for name, value in (
        (
            "explainability_architecture",
            architecture,
        ),
        (
            "explanation_scope_audience_contract_bundle",
            scope_bundle,
        ),
        (
            "evidence_provenance_explanation_mapping_bundle",
            evidence_bundle,
        ),
        (
            "conflict_exception_explanation_handling_bundle",
            conflict_bundle,
        ),
        (
            "confidence_uncertainty_explanation_contract_bundle",
            uncertainty_bundle,
        ),
        (
            "decision_trace_explanation_bundle",
            trace_bundle,
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
            raise ExplainabilityError(
                f"{name} must be a dictionary."
            )

    if (
        architecture.get("schema")
        != "explainability_architecture_v1"
    ):
        raise ExplainabilityError(
            "Invalid Explainability architecture schema."
        )

    if "USER_FACING_EXPLANATION" not in architecture.get(
        "explanation_surfaces",
        (),
    ):
        raise ExplainabilityError(
            "User-facing explanation surface is missing."
        )

    audience_contracts = scope_bundle.get(
        "audience_contracts"
    )

    if not isinstance(
        audience_contracts,
        tuple,
    ):
        raise ExplainabilityError(
            "Audience contracts must be a tuple."
        )

    end_user_contract = None

    for contract in audience_contracts:

        if (
            isinstance(
                contract,
                dict,
            )
            and contract.get("audience")
            == "END_USER"
        ):
            end_user_contract = contract
            break

    if not isinstance(
        end_user_contract,
        dict,
    ):
        raise ExplainabilityError(
            "END_USER audience contract is missing."
        )

    if (
        end_user_contract.get("primary_surface")
        != "USER_FACING_EXPLANATION"
    ):
        raise ExplainabilityError(
            "END_USER surface routing mismatch."
        )

    if end_user_contract.get(
        "semantic_meaning_may_change"
    ) is not False:
        raise ExplainabilityError(
            "END_USER explanation cannot change semantic meaning."
        )

    if end_user_contract.get(
        "conflict_disclosure_required"
    ) is not True:
        raise ExplainabilityError(
            "END_USER conflict disclosure is required."
        )

    if end_user_contract.get(
        "uncertainty_disclosure_required"
    ) is not True:
        raise ExplainabilityError(
            "END_USER uncertainty disclosure is required."
        )

    if end_user_contract.get(
        "truth_separation_disclosure_required"
    ) is not True:
        raise ExplainabilityError(
            "END_USER truth separation disclosure is required."
        )

    if trace_bundle.get(
        "decision_trace_construction_complete"
    ) is not True:
        raise ExplainabilityError(
            "Decision trace construction is incomplete."
        )

    if trace_bundle.get(
        "certified_component_identity_preserved"
    ) is not True:
        raise ExplainabilityError(
            "Decision trace identity was not preserved."
        )

    if trace_bundle.get(
        "certified_trace_order_preserved"
    ) is not True:
        raise ExplainabilityError(
            "Decision trace order was not preserved."
        )

    for flag in (
        "certified_semantic_memory_inspected",
        "explainability_architecture_defined",
        "explanation_scope_audience_contract_defined",
        "evidence_provenance_explanation_mapping_completed",
        "conflict_exception_explanation_handling_completed",
        "confidence_uncertainty_explanation_contract_defined",
        "decision_trace_explanation_construction_completed",
    ):
        if boundaries.get(flag) is not True:
            raise ExplainabilityError(
                "Required upstream Explainability state missing: "
                f"{flag}"
            )

    for flag in (
        "explanation_generated",
        "explanation_reasoning_performed",
        "semantic_memory_written",
        "semantic_memory_mutated",
        "memory_persistence_performed",
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
            raise ExplainabilityError(
                "Unsafe 4.6.29H input boundary state: "
                f"{flag}"
            )

    source_package_id = decision_trace_result.get(
        "source_semantic_memory_package_id"
    )

    source_package_digest = decision_trace_result.get(
        "source_semantic_memory_package_digest"
    )

    source_lineage_root_id = decision_trace_result.get(
        "source_semantic_memory_lineage_root_id"
    )

    source_memory_object_ids = decision_trace_result.get(
        "source_memory_object_ids"
    )

    source_memory_object_count = decision_trace_result.get(
        "source_memory_object_count"
    )

    if not isinstance(
        source_memory_object_ids,
        tuple,
    ):
        raise ExplainabilityError(
            "source_memory_object_ids must be a tuple."
        )

    if (
        not isinstance(
            source_memory_object_count,
            int,
        )
        or source_memory_object_count
        != len(source_memory_object_ids)
    ):
        raise ExplainabilityError(
            "Source memory object count mismatch."
        )

    uncertainty_records = uncertainty_bundle.get(
        "uncertainty_records"
    )

    conflict_records = conflict_bundle.get(
        "handling_records"
    )

    trace_records = trace_bundle.get(
        "decision_trace_records"
    )

    if not isinstance(
        uncertainty_records,
        tuple,
    ):
        raise ExplainabilityError(
            "Uncertainty records must be a tuple."
        )

    if not isinstance(
        conflict_records,
        tuple,
    ):
        raise ExplainabilityError(
            "Conflict records must be a tuple."
        )

    if not isinstance(
        trace_records,
        tuple,
    ):
        raise ExplainabilityError(
            "Decision trace records must be a tuple."
        )

    if not (
        len(uncertainty_records)
        == len(conflict_records)
        == len(trace_records)
        == source_memory_object_count
    ):
        raise ExplainabilityError(
            "User-facing explanation source counts do not align."
        )

    def index_records(
        records,
        expected_schema,
    ):

        result = {}

        for record in records:

            if not isinstance(
                record,
                dict,
            ):
                raise ExplainabilityError(
                    "User-facing source record must be a dictionary."
                )

            if record.get(
                "schema"
            ) != expected_schema:
                raise ExplainabilityError(
                    "Invalid user-facing source record schema."
                )

            memory_object_id = record.get(
                "memory_object_id"
            )

            if (
                not isinstance(
                    memory_object_id,
                    str,
                )
                or not memory_object_id
            ):
                raise ExplainabilityError(
                    "User-facing source memory object ID is missing."
                )

            if memory_object_id in result:
                raise ExplainabilityError(
                    "Duplicate user-facing source memory object ID."
                )

            result[
                memory_object_id
            ] = record

        return result

    uncertainty_by_id = index_records(
        uncertainty_records,
        "confidence_uncertainty_explanation_record_v1",
    )

    conflict_by_id = index_records(
        conflict_records,
        "conflict_exception_explanation_handling_record_v1",
    )

    trace_by_id = index_records(
        trace_records,
        "decision_trace_explanation_record_v1",
    )

    expected_ids = set(
        source_memory_object_ids
    )

    if set(
        uncertainty_by_id
    ) != expected_ids:
        raise ExplainabilityError(
            "User-facing uncertainty identity mismatch."
        )

    if set(
        conflict_by_id
    ) != expected_ids:
        raise ExplainabilityError(
            "User-facing conflict identity mismatch."
        )

    if set(
        trace_by_id
    ) != expected_ids:
        raise ExplainabilityError(
            "User-facing trace identity mismatch."
        )

    user_records = []

    for memory_object_id in source_memory_object_ids:

        uncertainty = uncertainty_by_id[
            memory_object_id
        ]

        conflict = conflict_by_id[
            memory_object_id
        ]

        trace = trace_by_id[
            memory_object_id
        ]

        uncertainty_level = uncertainty.get(
            "uncertainty_level"
        )

        confidence_expression = uncertainty.get(
            "confidence_expression"
        )

        retrieval_class = uncertainty.get(
            "retrieval_class"
        )

        memory_state = conflict.get(
            "memory_state"
        )

        disclosure_mode = conflict.get(
            "disclosure_mode"
        )

        for name, value in (
            (
                "uncertainty_level",
                uncertainty_level,
            ),
            (
                "confidence_expression",
                confidence_expression,
            ),
            (
                "retrieval_class",
                retrieval_class,
            ),
            (
                "memory_state",
                memory_state,
            ),
            (
                "disclosure_mode",
                disclosure_mode,
            ),
        ):
            if not isinstance(
                value,
                str,
            ) or not value:
                raise ExplainabilityError(
                    "Missing user-facing explanation field: "
                    f"{name}"
                )

        if trace.get(
            "trace_order_certified"
        ) is not True:
            raise ExplainabilityError(
                "User-facing explanation requires certified trace order."
            )

        if trace.get(
            "trace_complete_for_available_components"
        ) is not True:
            raise ExplainabilityError(
                "User-facing explanation requires complete available trace."
            )

        if retrieval_class == "ACTIVE_MEMORY":
            state_summary = (
                "This memory is active and available for normal read use."
            )

        elif retrieval_class == "CONTESTED_MEMORY":
            state_summary = (
                "This memory carries contested or cautionary context."
            )

        elif retrieval_class == "HELD_MEMORY":
            state_summary = (
                "This memory is held and is not available for normal read use."
            )

        elif retrieval_class == "BLOCKED_MEMORY":
            state_summary = (
                "This memory is blocked and is not available for normal read use."
            )

        elif retrieval_class == "HISTORICAL_MEMORY":
            state_summary = (
                "This memory is historical and is not treated as the current active state."
            )

        else:
            raise ExplainabilityError(
                "Unsupported retrieval class for user-facing explanation."
            )

        if uncertainty_level == "STANDARD_CAUTION":
            uncertainty_summary = (
                "The current certified memory state supports this explanation, "
                "but it is not treated as established truth."
            )

        elif uncertainty_level == "ELEVATED_CAUTION":
            uncertainty_summary = (
                "This memory has weakening or limitation signals, so additional "
                "caution is required."
            )

        elif uncertainty_level == "HIGH_CAUTION":
            uncertainty_summary = (
                "This memory is contested or held, so the explanation must be "
                "treated with high caution."
            )

        elif uncertainty_level == "MAXIMUM_CAUTION":
            uncertainty_summary = (
                "This memory is blocked and requires maximum caution."
            )

        elif uncertainty_level == "CONTEXTUAL_CAUTION":
            uncertainty_summary = (
                "This memory is historical or non-current and should be interpreted "
                "only in that context."
            )

        else:
            raise ExplainabilityError(
                "Unsupported uncertainty level for user-facing explanation."
            )

        conflict_summary_required = (
            conflict.get(
                "conflict_present"
            )
            is True
            or conflict.get(
                "held_present"
            )
            is True
            or conflict.get(
                "blocked_present"
            )
            is True
            or conflict.get(
                "historical_present"
            )
            is True
            or conflict.get(
                "weakened_present"
            )
            is True
        )

        if conflict_summary_required:
            conflict_summary = (
                "The underlying state includes conflict, exception, hold, block, "
                "historical, or weakening context that has been preserved rather "
                "than silently removed."
            )
        else:
            conflict_summary = (
                "No special conflict or exception disclosure is required for this "
                "memory state."
            )

        explanation_text = (
            state_summary
            + " "
            + uncertainty_summary
            + " "
            + conflict_summary
        )

        explanation_payload = {
            "memory_object_id":
                memory_object_id,

            "retrieval_class":
                retrieval_class,

            "memory_state":
                memory_state,

            "uncertainty_level":
                uncertainty_level,

            "confidence_expression":
                confidence_expression,

            "disclosure_mode":
                disclosure_mode,

            "explanation_text":
                explanation_text,
        }

        serialized = json.dumps(
            explanation_payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )

        explanation_digest = hashlib.sha256(
            serialized.encode("utf-8")
        ).hexdigest()

        user_records.append(
            {
                "schema":
                    "user_facing_explanation_record_v1",

                "user_facing_explanation_id":
                    "explainabilityuser:v1:"
                    + explanation_digest,

                "audience":
                    "END_USER",

                "surface":
                    "USER_FACING_EXPLANATION",

                "memory_object_id":
                    memory_object_id,

                "source_decision_trace_id":
                    trace[
                        "decision_trace_id"
                    ],

                "retrieval_class":
                    retrieval_class,

                "memory_state":
                    memory_state,

                "uncertainty_level":
                    uncertainty_level,

                "confidence_expression":
                    confidence_expression,

                "disclosure_mode":
                    disclosure_mode,

                "state_summary":
                    state_summary,

                "uncertainty_summary":
                    uncertainty_summary,

                "conflict_summary":
                    conflict_summary,

                "explanation_text":
                    explanation_text,

                "semantic_meaning_preserved":
                    True,

                "source_memory_identity_preserved":
                    True,

                "uncertainty_preserved":
                    True,

                "conflict_exception_context_preserved":
                    True,

                "retrieval_state_preserved":
                    True,

                "truth_separation_preserved":
                    True,

                "decision_trace_preserved":
                    True,

                "raw_internal_identifiers_exposed":
                    False,

                "semantic_meaning_changed":
                    False,

                "uncertainty_hidden":
                    False,

                "conflict_hidden":
                    False,

                "truth_adjudicated":
                    False,

                "new_decision_created":
                    False,

                "causal_reason_fabricated":
                    False,

                "semantic_state_mutated":
                    False,

                "authority_rescored":
                    False,

                "claim_integrity_redecided":
                    False,

                "conflict_reclassified":
                    False,

                "target_selected":
                    False,

                "target_scored":
                    False,

                "runtime_reasoning_performed":
                    False,

                "linking_decision_performed":
                    False,
            }
        )

    user_records = tuple(
        user_records
    )

    user_contract = {
        "schema":
            "user_facing_explanation_contract_v1",

        "canonical_owner":
            "EXPLAINABILITY",

        "audience":
            "END_USER",

        "surface":
            "USER_FACING_EXPLANATION",

        "presentation_may_be_concise":
            True,

        "technical_depth_may_be_reduced":
            True,

        "raw_internal_identifiers_need_not_be_exposed":
            True,

        "semantic_meaning_must_be_preserved":
            True,

        "source_memory_identity_must_be_preserved_internally":
            True,

        "uncertainty_must_be_preserved":
            True,

        "conflict_must_be_preserved":
            True,

        "exception_context_must_be_preserved":
            True,

        "retrieval_state_must_be_preserved":
            True,

        "truth_separation_must_be_preserved":
            True,

        "decision_trace_must_be_preserved":
            True,

        "uncertainty_must_not_be_hidden_for_simplicity":
            True,

        "conflict_must_not_be_hidden_for_simplicity":
            True,

        "blocked_state_must_not_be_softened":
            True,

        "held_state_must_not_be_softened":
            True,

        "historical_state_must_not_be_presented_as_current":
            True,

        "contested_state_must_not_be_presented_as_settled":
            True,

        "memory_must_not_be_presented_as_truth":
            True,

        "confidence_must_not_be_overstated":
            True,

        "causal_reason_must_not_be_fabricated":
            True,

        "missing_trace_must_not_be_invented":
            True,

        "user_explanation_must_not_create_new_decision":
            True,

        "user_explanation_must_not_adjudicate_truth":
            True,

        "user_explanation_must_not_rescore_authority":
            True,

        "user_explanation_must_not_redecide_claim_integrity":
            True,

        "user_explanation_must_not_reclassify_conflict":
            True,

        "user_explanation_must_not_change_memory_state":
            True,

        "user_explanation_must_not_change_retrieval_class":
            True,

        "user_explanation_must_not_select_target":
            True,

        "user_explanation_must_not_score_target":
            True,

        "user_explanation_must_not_perform_runtime_reasoning":
            True,

        "user_explanation_must_not_make_linking_decision":
            True,
    }

    bundle_payload = {
        "source_semantic_memory_package_id":
            source_package_id,

        "source_semantic_memory_package_digest":
            source_package_digest,

        "source_semantic_memory_lineage_root_id":
            source_lineage_root_id,

        "user_facing_explanation_ids":
            [
                item[
                    "user_facing_explanation_id"
                ]
                for item in user_records
            ],
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

    user_bundle = {
        "schema":
            "user_facing_explanation_bundle_v1",

        "user_facing_explanation_bundle_id":
            "explainabilityuserbundle:v1:"
            + bundle_digest,

        "user_facing_explanation_bundle_digest":
            bundle_digest,

        "source_semantic_memory_package_id":
            source_package_id,

        "source_semantic_memory_package_digest":
            source_package_digest,

        "source_semantic_memory_lineage_root_id":
            source_lineage_root_id,

        "user_facing_explanation_records":
            user_records,

        "user_facing_explanation_contract":
            user_contract,

        "user_facing_explanation_record_count":
            len(
                user_records
            ),

        "user_facing_explanation_construction_complete":
            True,

        "semantic_meaning_preserved":
            True,

        "uncertainty_preserved":
            True,

        "conflict_exception_context_preserved":
            True,

        "truth_separation_preserved":
            True,

        "decision_trace_preserved":
            True,

        "explanation_generated":
            True,

        "semantic_memory_mutated":
            False,

        "graph_mutated":
            False,

        "authority_rescored":
            False,

        "claim_integrity_redecided":
            False,

        "conflict_reclassified":
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
            "user_facing_explanation_construction_result_v1",

        "explainability_version":
            EXPLAINABILITY_VERSION,

        "phase":
            EXPLAINABILITY_PHASE,

        "patch":
            "4.6.29H",

        "status":
            "USER_FACING_EXPLANATION_CONSTRUCTION_COMPLETED",

        "source_semantic_memory_package_id":
            source_package_id,

        "source_semantic_memory_package_digest":
            source_package_digest,

        "source_semantic_memory_lineage_root_id":
            source_lineage_root_id,

        "source_memory_object_ids":
            tuple(
                source_memory_object_ids
            ),

        "source_memory_object_count":
            source_memory_object_count,

        "explainability_architecture":
            copy.deepcopy(
                architecture
            ),

        "explanation_scope_audience_contract_bundle":
            copy.deepcopy(
                scope_bundle
            ),

        "evidence_provenance_explanation_mapping_bundle":
            copy.deepcopy(
                evidence_bundle
            ),

        "conflict_exception_explanation_handling_bundle":
            copy.deepcopy(
                conflict_bundle
            ),

        "confidence_uncertainty_explanation_contract_bundle":
            copy.deepcopy(
                uncertainty_bundle
            ),

        "decision_trace_explanation_bundle":
            copy.deepcopy(
                trace_bundle
            ),

        "user_facing_explanation_bundle":
            user_bundle,

        "decision_trace_explanation_construction_result":
            copy.deepcopy(
                decision_trace_result
            ),

        "processing_boundaries": {
            "certified_semantic_memory_inspected":
                True,

            "explainability_architecture_defined":
                True,

            "explanation_scope_audience_contract_defined":
                True,

            "evidence_provenance_explanation_mapping_completed":
                True,

            "conflict_exception_explanation_handling_completed":
                True,

            "confidence_uncertainty_explanation_contract_defined":
                True,

            "decision_trace_explanation_construction_completed":
                True,

            "user_facing_explanation_construction_completed":
                True,

            "explanation_generated":
                True,

            "explanation_reasoning_performed":
                False,

            "semantic_memory_written":
                False,

            "semantic_memory_mutated":
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
        },

        "policy":
            "CERTIFIED_USER_FACING_EXPLANATION_CONSTRUCTION",

        "next":
            "developer_audit_explanation_construction",
    }

def construct_developer_audit_explanation_v1(
    user_facing_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.29I ? Developer / Audit Explanation Construction.

    Constructs detailed developer, auditor, and owner/operator
    explanation artifacts from the certified Explainability chain.

    These surfaces may expose internal identifiers, provenance,
    lineage, uncertainty, retrieval state, and complete certified
    decision trace metadata.

    Increased detail must not change semantic meaning or create
    decisions.
    """

    if not isinstance(
        user_facing_result,
        dict,
    ):
        raise ExplainabilityError(
            "user_facing_result must be a dictionary."
        )

    expected = {
        "schema":
            "user_facing_explanation_construction_result_v1",

        "explainability_version":
            EXPLAINABILITY_VERSION,

        "phase":
            EXPLAINABILITY_PHASE,

        "patch":
            "4.6.29H",

        "status":
            "USER_FACING_EXPLANATION_CONSTRUCTION_COMPLETED",

        "policy":
            "CERTIFIED_USER_FACING_EXPLANATION_CONSTRUCTION",

        "next":
            "developer_audit_explanation_construction",
    }

    for key, expected_value in expected.items():

        if user_facing_result.get(key) != expected_value:
            raise ExplainabilityError(
                "Invalid 4.6.29H lifecycle field: "
                f"{key}"
            )

    architecture = user_facing_result.get(
        "explainability_architecture"
    )

    scope_bundle = user_facing_result.get(
        "explanation_scope_audience_contract_bundle"
    )

    evidence_bundle = user_facing_result.get(
        "evidence_provenance_explanation_mapping_bundle"
    )

    conflict_bundle = user_facing_result.get(
        "conflict_exception_explanation_handling_bundle"
    )

    uncertainty_bundle = user_facing_result.get(
        "confidence_uncertainty_explanation_contract_bundle"
    )

    trace_bundle = user_facing_result.get(
        "decision_trace_explanation_bundle"
    )

    user_bundle = user_facing_result.get(
        "user_facing_explanation_bundle"
    )

    boundaries = user_facing_result.get(
        "processing_boundaries"
    )

    for name, value in (
        (
            "explainability_architecture",
            architecture,
        ),
        (
            "explanation_scope_audience_contract_bundle",
            scope_bundle,
        ),
        (
            "evidence_provenance_explanation_mapping_bundle",
            evidence_bundle,
        ),
        (
            "conflict_exception_explanation_handling_bundle",
            conflict_bundle,
        ),
        (
            "confidence_uncertainty_explanation_contract_bundle",
            uncertainty_bundle,
        ),
        (
            "decision_trace_explanation_bundle",
            trace_bundle,
        ),
        (
            "user_facing_explanation_bundle",
            user_bundle,
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
            raise ExplainabilityError(
                f"{name} must be a dictionary."
            )

    if (
        architecture.get("schema")
        != "explainability_architecture_v1"
    ):
        raise ExplainabilityError(
            "Invalid Explainability architecture schema."
        )

    for required_surface in (
        "DEVELOPER_EXPLANATION",
        "AUDIT_EXPLANATION",
    ):
        if required_surface not in architecture.get(
            "explanation_surfaces",
            (),
        ):
            raise ExplainabilityError(
                "Required technical explanation surface missing: "
                f"{required_surface}"
            )

    audience_contracts = scope_bundle.get(
        "audience_contracts"
    )

    if not isinstance(
        audience_contracts,
        tuple,
    ):
        raise ExplainabilityError(
            "Audience contracts must be a tuple."
        )

    audience_by_name = {}

    for contract in audience_contracts:

        if not isinstance(
            contract,
            dict,
        ):
            raise ExplainabilityError(
                "Audience contract must be a dictionary."
            )

        audience = contract.get(
            "audience"
        )

        if (
            not isinstance(
                audience,
                str,
            )
            or not audience
        ):
            raise ExplainabilityError(
                "Audience contract name is missing."
            )

        audience_by_name[
            audience
        ] = contract

    for required_audience in (
        "DEVELOPER",
        "AUDITOR",
        "OWNER_OPERATOR",
    ):
        if required_audience not in audience_by_name:
            raise ExplainabilityError(
                "Required technical audience contract missing: "
                f"{required_audience}"
            )

    expected_surface_by_audience = {
        "DEVELOPER":
            "DEVELOPER_EXPLANATION",

        "AUDITOR":
            "AUDIT_EXPLANATION",

        "OWNER_OPERATOR":
            "AUDIT_EXPLANATION",
    }

    for audience, surface in expected_surface_by_audience.items():

        contract = audience_by_name[
            audience
        ]

        if contract.get(
            "primary_surface"
        ) != surface:
            raise ExplainabilityError(
                "Technical audience surface routing mismatch: "
                f"{audience}"
            )

        if contract.get(
            "semantic_meaning_may_change"
        ) is not False:
            raise ExplainabilityError(
                "Technical explanation cannot change semantic meaning."
            )

        if contract.get(
            "raw_internal_identifiers_required"
        ) is not True:
            raise ExplainabilityError(
                "Technical explanation requires internal identifiers."
            )

        if contract.get(
            "conflict_disclosure_required"
        ) is not True:
            raise ExplainabilityError(
                "Technical explanation requires conflict disclosure."
            )

        if contract.get(
            "uncertainty_disclosure_required"
        ) is not True:
            raise ExplainabilityError(
                "Technical explanation requires uncertainty disclosure."
            )

        if contract.get(
            "truth_separation_disclosure_required"
        ) is not True:
            raise ExplainabilityError(
                "Technical explanation requires truth separation disclosure."
            )

    if user_bundle.get(
        "user_facing_explanation_construction_complete"
    ) is not True:
        raise ExplainabilityError(
            "User-facing explanation construction is incomplete."
        )

    if user_bundle.get(
        "semantic_meaning_preserved"
    ) is not True:
        raise ExplainabilityError(
            "User-facing semantic meaning was not preserved."
        )

    if user_bundle.get(
        "truth_separation_preserved"
    ) is not True:
        raise ExplainabilityError(
            "User-facing truth separation was not preserved."
        )

    if trace_bundle.get(
        "decision_trace_construction_complete"
    ) is not True:
        raise ExplainabilityError(
            "Decision trace construction is incomplete."
        )

    if evidence_bundle.get(
        "evidence_provenance_mapping_complete"
    ) is not True:
        raise ExplainabilityError(
            "Evidence/provenance mapping is incomplete."
        )

    if conflict_bundle.get(
        "conflict_exception_handling_complete"
    ) is not True:
        raise ExplainabilityError(
            "Conflict/exception handling is incomplete."
        )

    if uncertainty_bundle.get(
        "confidence_uncertainty_contract_complete"
    ) is not True:
        raise ExplainabilityError(
            "Confidence/uncertainty contract is incomplete."
        )

    for flag in (
        "certified_semantic_memory_inspected",
        "explainability_architecture_defined",
        "explanation_scope_audience_contract_defined",
        "evidence_provenance_explanation_mapping_completed",
        "conflict_exception_explanation_handling_completed",
        "confidence_uncertainty_explanation_contract_defined",
        "decision_trace_explanation_construction_completed",
        "user_facing_explanation_construction_completed",
        "explanation_generated",
    ):
        if boundaries.get(flag) is not True:
            raise ExplainabilityError(
                "Required upstream Explainability state missing: "
                f"{flag}"
            )

    for flag in (
        "explanation_reasoning_performed",
        "semantic_memory_written",
        "semantic_memory_mutated",
        "memory_persistence_performed",
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
            raise ExplainabilityError(
                "Unsafe 4.6.29I input boundary state: "
                f"{flag}"
            )

    source_package_id = user_facing_result.get(
        "source_semantic_memory_package_id"
    )

    source_package_digest = user_facing_result.get(
        "source_semantic_memory_package_digest"
    )

    source_lineage_root_id = user_facing_result.get(
        "source_semantic_memory_lineage_root_id"
    )

    source_memory_object_ids = user_facing_result.get(
        "source_memory_object_ids"
    )

    source_memory_object_count = user_facing_result.get(
        "source_memory_object_count"
    )

    if not isinstance(
        source_memory_object_ids,
        tuple,
    ):
        raise ExplainabilityError(
            "source_memory_object_ids must be a tuple."
        )

    if (
        not isinstance(
            source_memory_object_count,
            int,
        )
        or source_memory_object_count
        != len(source_memory_object_ids)
    ):
        raise ExplainabilityError(
            "Source memory object count mismatch."
        )

    evidence_records = evidence_bundle.get(
        "mapping_records"
    )

    conflict_records = conflict_bundle.get(
        "handling_records"
    )

    uncertainty_records = uncertainty_bundle.get(
        "uncertainty_records"
    )

    trace_records = trace_bundle.get(
        "decision_trace_records"
    )

    user_records = user_bundle.get(
        "user_facing_explanation_records"
    )

    for name, records in (
        (
            "evidence_records",
            evidence_records,
        ),
        (
            "conflict_records",
            conflict_records,
        ),
        (
            "uncertainty_records",
            uncertainty_records,
        ),
        (
            "trace_records",
            trace_records,
        ),
        (
            "user_records",
            user_records,
        ),
    ):
        if not isinstance(
            records,
            tuple,
        ):
            raise ExplainabilityError(
                f"{name} must be a tuple."
            )

        if len(
            records
        ) != source_memory_object_count:
            raise ExplainabilityError(
                f"{name} count mismatch."
            )

    def index_records(
        records,
        expected_schema,
    ):

        result = {}

        for record in records:

            if not isinstance(
                record,
                dict,
            ):
                raise ExplainabilityError(
                    "Technical explanation source record must be a dictionary."
                )

            if record.get(
                "schema"
            ) != expected_schema:
                raise ExplainabilityError(
                    "Invalid technical explanation source schema."
                )

            memory_object_id = record.get(
                "memory_object_id"
            )

            if (
                not isinstance(
                    memory_object_id,
                    str,
                )
                or not memory_object_id
            ):
                raise ExplainabilityError(
                    "Technical explanation memory object ID is missing."
                )

            if memory_object_id in result:
                raise ExplainabilityError(
                    "Duplicate technical explanation memory object ID."
                )

            result[
                memory_object_id
            ] = record

        return result

    evidence_by_id = index_records(
        evidence_records,
        "evidence_provenance_explanation_mapping_record_v1",
    )

    conflict_by_id = index_records(
        conflict_records,
        "conflict_exception_explanation_handling_record_v1",
    )

    uncertainty_by_id = index_records(
        uncertainty_records,
        "confidence_uncertainty_explanation_record_v1",
    )

    trace_by_id = index_records(
        trace_records,
        "decision_trace_explanation_record_v1",
    )

    user_by_id = index_records(
        user_records,
        "user_facing_explanation_record_v1",
    )

    expected_ids = set(
        source_memory_object_ids
    )

    for name, indexed in (
        (
            "evidence",
            evidence_by_id,
        ),
        (
            "conflict",
            conflict_by_id,
        ),
        (
            "uncertainty",
            uncertainty_by_id,
        ),
        (
            "trace",
            trace_by_id,
        ),
        (
            "user",
            user_by_id,
        ),
    ):
        if set(
            indexed
        ) != expected_ids:
            raise ExplainabilityError(
                "Technical explanation source identity mismatch: "
                f"{name}"
            )

    technical_records = []

    for memory_object_id in source_memory_object_ids:

        evidence = evidence_by_id[
            memory_object_id
        ]

        conflict = conflict_by_id[
            memory_object_id
        ]

        uncertainty = uncertainty_by_id[
            memory_object_id
        ]

        trace = trace_by_id[
            memory_object_id
        ]

        user = user_by_id[
            memory_object_id
        ]

        technical_payload = {
            "memory_object_id":
                memory_object_id,

            "source_learning_object_id":
                evidence[
                    "source_learning_object_id"
                ],

            "memory_lineage_record_id":
                evidence[
                    "memory_lineage_record_id"
                ],

            "retrieval_metadata_id":
                evidence[
                    "retrieval_metadata_id"
                ],

            "evidence_provenance_mapping_id":
                evidence[
                    "evidence_provenance_mapping_id"
                ],

            "conflict_exception_handling_id":
                conflict[
                    "conflict_exception_handling_id"
                ],

            "confidence_uncertainty_record_id":
                uncertainty[
                    "confidence_uncertainty_record_id"
                ],

            "decision_trace_id":
                trace[
                    "decision_trace_id"
                ],

            "user_facing_explanation_id":
                user[
                    "user_facing_explanation_id"
                ],

            "memory_state":
                conflict[
                    "memory_state"
                ],

            "retrieval_class":
                uncertainty[
                    "retrieval_class"
                ],

            "uncertainty_level":
                uncertainty[
                    "uncertainty_level"
                ],
        }

        serialized = json.dumps(
            technical_payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )

        technical_digest = hashlib.sha256(
            serialized.encode("utf-8")
        ).hexdigest()

        shared = {
            "schema":
                "developer_audit_explanation_record_v1",

            "developer_audit_explanation_id":
                "explainabilitytechnical:v1:"
                + technical_digest,

            "memory_object_id":
                memory_object_id,

            "source_learning_object_id":
                evidence[
                    "source_learning_object_id"
                ],

            "memory_lineage_record_id":
                evidence[
                    "memory_lineage_record_id"
                ],

            "retrieval_metadata_id":
                evidence[
                    "retrieval_metadata_id"
                ],

            "evidence_provenance_mapping_id":
                evidence[
                    "evidence_provenance_mapping_id"
                ],

            "conflict_exception_handling_id":
                conflict[
                    "conflict_exception_handling_id"
                ],

            "confidence_uncertainty_record_id":
                uncertainty[
                    "confidence_uncertainty_record_id"
                ],

            "decision_trace_id":
                trace[
                    "decision_trace_id"
                ],

            "user_facing_explanation_id":
                user[
                    "user_facing_explanation_id"
                ],

            "memory_state":
                conflict[
                    "memory_state"
                ],

            "stability_state":
                evidence[
                    "stability_state"
                ],

            "retention_state":
                evidence[
                    "retention_state"
                ],

            "retrieval_class":
                uncertainty[
                    "retrieval_class"
                ],

            "uncertainty_level":
                uncertainty[
                    "uncertainty_level"
                ],

            "confidence_expression":
                uncertainty[
                    "confidence_expression"
                ],

            "disclosure_mode":
                conflict[
                    "disclosure_mode"
                ],

            "trace_steps":
                copy.deepcopy(
                    trace[
                        "trace_steps"
                    ]
                ),

            "semantic_meaning_preserved":
                True,

            "source_memory_identity_preserved":
                True,

            "provenance_preserved":
                True,

            "lineage_preserved":
                True,

            "conflict_exception_context_preserved":
                True,

            "uncertainty_preserved":
                True,

            "retrieval_state_preserved":
                True,

            "truth_separation_preserved":
                True,

            "decision_trace_preserved":
                True,

            "internal_identifiers_exposed":
                True,

            "semantic_meaning_changed":
                False,

            "uncertainty_hidden":
                False,

            "conflict_hidden":
                False,

            "truth_adjudicated":
                False,

            "new_decision_created":
                False,

            "causal_reason_fabricated":
                False,

            "semantic_state_mutated":
                False,

            "authority_rescored":
                False,

            "claim_integrity_redecided":
                False,

            "conflict_reclassified":
                False,

            "target_selected":
                False,

            "target_scored":
                False,

            "runtime_reasoning_performed":
                False,

            "linking_decision_performed":
                False,
        }

        developer_record = {
            **copy.deepcopy(
                shared
            ),

            "audience":
                "DEVELOPER",

            "surface":
                "DEVELOPER_EXPLANATION",

            "detail_level":
                "DETAILED",

            "technical_depth":
                "HIGH",
        }

        auditor_record = {
            **copy.deepcopy(
                shared
            ),

            "developer_audit_explanation_id":
                "explainabilityaudit:v1:"
                + technical_digest,

            "audience":
                "AUDITOR",

            "surface":
                "AUDIT_EXPLANATION",

            "detail_level":
                "EXHAUSTIVE",

            "technical_depth":
                "HIGH",
        }

        owner_record = {
            **copy.deepcopy(
                shared
            ),

            "developer_audit_explanation_id":
                "explainabilityowner:v1:"
                + technical_digest,

            "audience":
                "OWNER_OPERATOR",

            "surface":
                "AUDIT_EXPLANATION",

            "detail_level":
                "OPERATIONAL_DETAILED",

            "technical_depth":
                "HIGH",
        }

        technical_records.extend(
            (
                developer_record,
                auditor_record,
                owner_record,
            )
        )

    technical_records = tuple(
        technical_records
    )

    technical_contract = {
        "schema":
            "developer_audit_explanation_contract_v1",

        "canonical_owner":
            "EXPLAINABILITY",

        "developer_surface":
            "DEVELOPER_EXPLANATION",

        "audit_surface":
            "AUDIT_EXPLANATION",

        "developer_audience_supported":
            True,

        "auditor_audience_supported":
            True,

        "owner_operator_audience_supported":
            True,

        "internal_identifiers_may_be_exposed":
            True,

        "provenance_must_be_full":
            True,

        "lineage_must_be_full":
            True,

        "decision_trace_must_be_detailed":
            True,

        "conflict_context_must_be_preserved":
            True,

        "uncertainty_must_be_preserved":
            True,

        "retrieval_state_must_be_preserved":
            True,

        "truth_separation_must_be_preserved":
            True,

        "semantic_meaning_must_match_user_surface":
            True,

        "additional_detail_must_not_create_new_meaning":
            True,

        "missing_internal_detail_must_not_be_fabricated":
            True,

        "missing_trace_component_must_not_be_invented":
            True,

        "causal_reason_must_not_be_fabricated":
            True,

        "technical_explanation_must_not_adjudicate_truth":
            True,

        "technical_explanation_must_not_rescore_authority":
            True,

        "technical_explanation_must_not_redecide_claim_integrity":
            True,

        "technical_explanation_must_not_reclassify_conflict":
            True,

        "technical_explanation_must_not_change_memory_state":
            True,

        "technical_explanation_must_not_change_stability_state":
            True,

        "technical_explanation_must_not_change_retention_state":
            True,

        "technical_explanation_must_not_change_retrieval_class":
            True,

        "technical_explanation_must_not_create_new_decision":
            True,

        "technical_explanation_must_not_select_target":
            True,

        "technical_explanation_must_not_score_target":
            True,

        "technical_explanation_must_not_perform_runtime_reasoning":
            True,

        "technical_explanation_must_not_make_linking_decision":
            True,

        "technical_explanation_must_not_create_editor_highlight":
            True,
    }

    bundle_payload = {
        "source_semantic_memory_package_id":
            source_package_id,

        "source_semantic_memory_package_digest":
            source_package_digest,

        "source_semantic_memory_lineage_root_id":
            source_lineage_root_id,

        "technical_explanation_ids":
            [
                item[
                    "developer_audit_explanation_id"
                ]
                for item in technical_records
            ],
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

    technical_bundle = {
        "schema":
            "developer_audit_explanation_bundle_v1",

        "developer_audit_explanation_bundle_id":
            "explainabilitytechnicalbundle:v1:"
            + bundle_digest,

        "developer_audit_explanation_bundle_digest":
            bundle_digest,

        "source_semantic_memory_package_id":
            source_package_id,

        "source_semantic_memory_package_digest":
            source_package_digest,

        "source_semantic_memory_lineage_root_id":
            source_lineage_root_id,

        "developer_audit_explanation_records":
            technical_records,

        "developer_audit_explanation_contract":
            technical_contract,

        "developer_audit_explanation_record_count":
            len(
                technical_records
            ),

        "developer_audit_explanation_construction_complete":
            True,

        "semantic_meaning_preserved":
            True,

        "source_memory_identity_preserved":
            True,

        "provenance_preserved":
            True,

        "lineage_preserved":
            True,

        "conflict_exception_context_preserved":
            True,

        "uncertainty_preserved":
            True,

        "retrieval_state_preserved":
            True,

        "truth_separation_preserved":
            True,

        "decision_trace_preserved":
            True,

        "internal_identifiers_exposed":
            True,

        "explanation_generated":
            True,

        "semantic_memory_mutated":
            False,

        "graph_mutated":
            False,

        "authority_rescored":
            False,

        "claim_integrity_redecided":
            False,

        "conflict_reclassified":
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
            "developer_audit_explanation_construction_result_v1",

        "explainability_version":
            EXPLAINABILITY_VERSION,

        "phase":
            EXPLAINABILITY_PHASE,

        "patch":
            "4.6.29I",

        "status":
            "DEVELOPER_AUDIT_EXPLANATION_CONSTRUCTION_COMPLETED",

        "source_semantic_memory_package_id":
            source_package_id,

        "source_semantic_memory_package_digest":
            source_package_digest,

        "source_semantic_memory_lineage_root_id":
            source_lineage_root_id,

        "source_memory_object_ids":
            tuple(
                source_memory_object_ids
            ),

        "source_memory_object_count":
            source_memory_object_count,

        "explainability_architecture":
            copy.deepcopy(
                architecture
            ),

        "explanation_scope_audience_contract_bundle":
            copy.deepcopy(
                scope_bundle
            ),

        "evidence_provenance_explanation_mapping_bundle":
            copy.deepcopy(
                evidence_bundle
            ),

        "conflict_exception_explanation_handling_bundle":
            copy.deepcopy(
                conflict_bundle
            ),

        "confidence_uncertainty_explanation_contract_bundle":
            copy.deepcopy(
                uncertainty_bundle
            ),

        "decision_trace_explanation_bundle":
            copy.deepcopy(
                trace_bundle
            ),

        "user_facing_explanation_bundle":
            copy.deepcopy(
                user_bundle
            ),

        "developer_audit_explanation_bundle":
            technical_bundle,

        "user_facing_explanation_construction_result":
            copy.deepcopy(
                user_facing_result
            ),

        "processing_boundaries": {
            "certified_semantic_memory_inspected":
                True,

            "explainability_architecture_defined":
                True,

            "explanation_scope_audience_contract_defined":
                True,

            "evidence_provenance_explanation_mapping_completed":
                True,

            "conflict_exception_explanation_handling_completed":
                True,

            "confidence_uncertainty_explanation_contract_defined":
                True,

            "decision_trace_explanation_construction_completed":
                True,

            "user_facing_explanation_construction_completed":
                True,

            "developer_audit_explanation_construction_completed":
                True,

            "explanation_generated":
                True,

            "explanation_reasoning_performed":
                False,

            "semantic_memory_written":
                False,

            "semantic_memory_mutated":
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
        },

        "policy":
            "CERTIFIED_DEVELOPER_AUDIT_EXPLANATION_CONSTRUCTION",

        "next":
            "explanation_safety_boundary_enforcement",
    }

def enforce_explanation_safety_boundaries_v1(
    developer_audit_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.29J ? Explanation Safety & Boundary Enforcement.

    Certifies that all Explainability outputs remain explanatory only.

    It enforces semantic-meaning invariance, uncertainty/conflict
    preservation, truth separation, source identity preservation,
    audience-boundary correctness, and strict prohibition against
    mutation, reasoning, target selection, linking decisions, or
    upstream semantic reclassification.
    """

    if not isinstance(
        developer_audit_result,
        dict,
    ):
        raise ExplainabilityError(
            "developer_audit_result must be a dictionary."
        )

    expected = {
        "schema":
            "developer_audit_explanation_construction_result_v1",

        "explainability_version":
            EXPLAINABILITY_VERSION,

        "phase":
            EXPLAINABILITY_PHASE,

        "patch":
            "4.6.29I",

        "status":
            "DEVELOPER_AUDIT_EXPLANATION_CONSTRUCTION_COMPLETED",

        "policy":
            "CERTIFIED_DEVELOPER_AUDIT_EXPLANATION_CONSTRUCTION",

        "next":
            "explanation_safety_boundary_enforcement",
    }

    for key, expected_value in expected.items():

        if developer_audit_result.get(key) != expected_value:
            raise ExplainabilityError(
                "Invalid 4.6.29I lifecycle field: "
                f"{key}"
            )

    architecture = developer_audit_result.get(
        "explainability_architecture"
    )

    scope_bundle = developer_audit_result.get(
        "explanation_scope_audience_contract_bundle"
    )

    evidence_bundle = developer_audit_result.get(
        "evidence_provenance_explanation_mapping_bundle"
    )

    conflict_bundle = developer_audit_result.get(
        "conflict_exception_explanation_handling_bundle"
    )

    uncertainty_bundle = developer_audit_result.get(
        "confidence_uncertainty_explanation_contract_bundle"
    )

    trace_bundle = developer_audit_result.get(
        "decision_trace_explanation_bundle"
    )

    user_bundle = developer_audit_result.get(
        "user_facing_explanation_bundle"
    )

    technical_bundle = developer_audit_result.get(
        "developer_audit_explanation_bundle"
    )

    boundaries = developer_audit_result.get(
        "processing_boundaries"
    )

    for name, value in (
        (
            "explainability_architecture",
            architecture,
        ),
        (
            "explanation_scope_audience_contract_bundle",
            scope_bundle,
        ),
        (
            "evidence_provenance_explanation_mapping_bundle",
            evidence_bundle,
        ),
        (
            "conflict_exception_explanation_handling_bundle",
            conflict_bundle,
        ),
        (
            "confidence_uncertainty_explanation_contract_bundle",
            uncertainty_bundle,
        ),
        (
            "decision_trace_explanation_bundle",
            trace_bundle,
        ),
        (
            "user_facing_explanation_bundle",
            user_bundle,
        ),
        (
            "developer_audit_explanation_bundle",
            technical_bundle,
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
            raise ExplainabilityError(
                f"{name} must be a dictionary."
            )

    if (
        architecture.get("schema")
        != "explainability_architecture_v1"
    ):
        raise ExplainabilityError(
            "Invalid Explainability architecture schema."
        )

    required_surfaces = (
        "USER_FACING_EXPLANATION",
        "DEVELOPER_EXPLANATION",
        "AUDIT_EXPLANATION",
        "DECISION_TRACE_EXPLANATION",
    )

    for surface in required_surfaces:

        if surface not in architecture.get(
            "explanation_surfaces",
            (),
        ):
            raise ExplainabilityError(
                "Required explanation surface missing: "
                f"{surface}"
            )

    if user_bundle.get(
        "user_facing_explanation_construction_complete"
    ) is not True:
        raise ExplainabilityError(
            "User-facing explanation construction is incomplete."
        )

    if technical_bundle.get(
        "developer_audit_explanation_construction_complete"
    ) is not True:
        raise ExplainabilityError(
            "Developer/audit explanation construction is incomplete."
        )

    if trace_bundle.get(
        "decision_trace_construction_complete"
    ) is not True:
        raise ExplainabilityError(
            "Decision trace construction is incomplete."
        )

    if evidence_bundle.get(
        "evidence_provenance_mapping_complete"
    ) is not True:
        raise ExplainabilityError(
            "Evidence/provenance mapping is incomplete."
        )

    if conflict_bundle.get(
        "conflict_exception_handling_complete"
    ) is not True:
        raise ExplainabilityError(
            "Conflict/exception handling is incomplete."
        )

    if uncertainty_bundle.get(
        "confidence_uncertainty_contract_complete"
    ) is not True:
        raise ExplainabilityError(
            "Confidence/uncertainty contract is incomplete."
        )

    required_preserved_true = (
        (
            user_bundle,
            "semantic_meaning_preserved",
        ),
        (
            user_bundle,
            "uncertainty_preserved",
        ),
        (
            user_bundle,
            "conflict_exception_context_preserved",
        ),
        (
            user_bundle,
            "truth_separation_preserved",
        ),
        (
            user_bundle,
            "decision_trace_preserved",
        ),
        (
            technical_bundle,
            "semantic_meaning_preserved",
        ),
        (
            technical_bundle,
            "source_memory_identity_preserved",
        ),
        (
            technical_bundle,
            "provenance_preserved",
        ),
        (
            technical_bundle,
            "lineage_preserved",
        ),
        (
            technical_bundle,
            "conflict_exception_context_preserved",
        ),
        (
            technical_bundle,
            "uncertainty_preserved",
        ),
        (
            technical_bundle,
            "retrieval_state_preserved",
        ),
        (
            technical_bundle,
            "truth_separation_preserved",
        ),
        (
            technical_bundle,
            "decision_trace_preserved",
        ),
        (
            trace_bundle,
            "certified_component_identity_preserved",
        ),
        (
            trace_bundle,
            "certified_trace_order_preserved",
        ),
        (
            uncertainty_bundle,
            "uncertainty_preserved",
        ),
        (
            uncertainty_bundle,
            "truth_separation_preserved",
        ),
        (
            conflict_bundle,
            "conflict_state_preserved",
        ),
        (
            conflict_bundle,
            "exception_state_preserved",
        ),
        (
            conflict_bundle,
            "minority_context_preserved",
        ),
        (
            evidence_bundle,
            "source_memory_identity_preserved",
        ),
        (
            evidence_bundle,
            "provenance_preserved",
        ),
        (
            evidence_bundle,
            "lineage_preserved",
        ),
        (
            evidence_bundle,
            "non_truth_status_preserved",
        ),
    )

    for owner, flag in required_preserved_true:

        if owner.get(flag) is not True:
            raise ExplainabilityError(
                "Required Explainability preservation guarantee missing: "
                f"{flag}"
            )

    required_upstream_true = (
        "certified_semantic_memory_inspected",
        "explainability_architecture_defined",
        "explanation_scope_audience_contract_defined",
        "evidence_provenance_explanation_mapping_completed",
        "conflict_exception_explanation_handling_completed",
        "confidence_uncertainty_explanation_contract_defined",
        "decision_trace_explanation_construction_completed",
        "user_facing_explanation_construction_completed",
        "developer_audit_explanation_construction_completed",
        "explanation_generated",
    )

    for flag in required_upstream_true:

        if boundaries.get(flag) is not True:
            raise ExplainabilityError(
                "Required upstream Explainability state missing: "
                f"{flag}"
            )

    prohibited_boundary_flags = (
        "explanation_reasoning_performed",
        "semantic_memory_written",
        "semantic_memory_mutated",
        "memory_persistence_performed",
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

    for flag in prohibited_boundary_flags:

        if boundaries.get(flag) is not False:
            raise ExplainabilityError(
                "Unsafe Explainability boundary state: "
                f"{flag}"
            )

    source_package_id = developer_audit_result.get(
        "source_semantic_memory_package_id"
    )

    source_package_digest = developer_audit_result.get(
        "source_semantic_memory_package_digest"
    )

    source_lineage_root_id = developer_audit_result.get(
        "source_semantic_memory_lineage_root_id"
    )

    source_memory_object_ids = developer_audit_result.get(
        "source_memory_object_ids"
    )

    source_memory_object_count = developer_audit_result.get(
        "source_memory_object_count"
    )

    if not isinstance(
        source_memory_object_ids,
        tuple,
    ):
        raise ExplainabilityError(
            "source_memory_object_ids must be a tuple."
        )

    if (
        not isinstance(
            source_memory_object_count,
            int,
        )
        or source_memory_object_count
        != len(source_memory_object_ids)
    ):
        raise ExplainabilityError(
            "Source memory object count mismatch."
        )

    if len(
        source_memory_object_ids
    ) != len(
        set(source_memory_object_ids)
    ):
        raise ExplainabilityError(
            "Duplicate source memory object IDs."
        )

    user_records = user_bundle.get(
        "user_facing_explanation_records"
    )

    technical_records = technical_bundle.get(
        "developer_audit_explanation_records"
    )

    trace_records = trace_bundle.get(
        "decision_trace_records"
    )

    if not isinstance(
        user_records,
        tuple,
    ):
        raise ExplainabilityError(
            "User-facing explanation records must be a tuple."
        )

    if not isinstance(
        technical_records,
        tuple,
    ):
        raise ExplainabilityError(
            "Developer/audit explanation records must be a tuple."
        )

    if not isinstance(
        trace_records,
        tuple,
    ):
        raise ExplainabilityError(
            "Decision trace records must be a tuple."
        )

    if len(
        user_records
    ) != source_memory_object_count:
        raise ExplainabilityError(
            "User-facing explanation count mismatch."
        )

    if len(
        trace_records
    ) != source_memory_object_count:
        raise ExplainabilityError(
            "Decision trace count mismatch."
        )

    expected_technical_count = (
        source_memory_object_count
        * 3
    )

    if len(
        technical_records
    ) != expected_technical_count:
        raise ExplainabilityError(
            "Developer/audit explanation count mismatch."
        )

    user_by_id = {}

    for record in user_records:

        if (
            not isinstance(
                record,
                dict,
            )
            or record.get("schema")
            != "user_facing_explanation_record_v1"
        ):
            raise ExplainabilityError(
                "Invalid user-facing explanation record."
            )

        memory_object_id = record.get(
            "memory_object_id"
        )

        if memory_object_id in user_by_id:
            raise ExplainabilityError(
                "Duplicate user-facing memory object ID."
            )

        user_by_id[
            memory_object_id
        ] = record

    trace_by_id = {}

    for record in trace_records:

        if (
            not isinstance(
                record,
                dict,
            )
            or record.get("schema")
            != "decision_trace_explanation_record_v1"
        ):
            raise ExplainabilityError(
                "Invalid decision trace record."
            )

        memory_object_id = record.get(
            "memory_object_id"
        )

        if memory_object_id in trace_by_id:
            raise ExplainabilityError(
                "Duplicate decision-trace memory object ID."
            )

        trace_by_id[
            memory_object_id
        ] = record

    technical_by_memory_id = {}

    for record in technical_records:

        if (
            not isinstance(
                record,
                dict,
            )
            or record.get("schema")
            != "developer_audit_explanation_record_v1"
        ):
            raise ExplainabilityError(
                "Invalid developer/audit explanation record."
            )

        memory_object_id = record.get(
            "memory_object_id"
        )

        technical_by_memory_id.setdefault(
            memory_object_id,
            [],
        ).append(
            record
        )

    expected_ids = set(
        source_memory_object_ids
    )

    if set(
        user_by_id
    ) != expected_ids:
        raise ExplainabilityError(
            "User-facing explanation identity mismatch."
        )

    if set(
        trace_by_id
    ) != expected_ids:
        raise ExplainabilityError(
            "Decision trace identity mismatch."
        )

    if set(
        technical_by_memory_id
    ) != expected_ids:
        raise ExplainabilityError(
            "Technical explanation identity mismatch."
        )

    safety_records = []

    prohibited_record_true_flags = (
        "semantic_meaning_changed",
        "uncertainty_hidden",
        "conflict_hidden",
        "truth_adjudicated",
        "new_decision_created",
        "causal_reason_fabricated",
        "semantic_state_mutated",
        "authority_rescored",
        "claim_integrity_redecided",
        "conflict_reclassified",
        "target_selected",
        "target_scored",
        "runtime_reasoning_performed",
        "linking_decision_performed",
    )

    required_record_true_flags = (
        "semantic_meaning_preserved",
        "source_memory_identity_preserved",
        "uncertainty_preserved",
        "conflict_exception_context_preserved",
        "retrieval_state_preserved",
        "truth_separation_preserved",
        "decision_trace_preserved",
    )

    for memory_object_id in source_memory_object_ids:

        user_record = user_by_id[
            memory_object_id
        ]

        trace_record = trace_by_id[
            memory_object_id
        ]

        technical_group = technical_by_memory_id[
            memory_object_id
        ]

        if len(
            technical_group
        ) != 3:
            raise ExplainabilityError(
                "Each memory object must have exactly three technical audience records."
            )

        audiences = {
            item.get(
                "audience"
            )
            for item in technical_group
        }

        if audiences != {
            "DEVELOPER",
            "AUDITOR",
            "OWNER_OPERATOR",
        }:
            raise ExplainabilityError(
                "Technical audience set mismatch."
            )

        for flag in required_record_true_flags:

            if user_record.get(flag) is not True:
                raise ExplainabilityError(
                    "Unsafe user-facing explanation preservation state: "
                    f"{flag}"
                )

        for flag in prohibited_record_true_flags:

            if user_record.get(flag) is not False:
                raise ExplainabilityError(
                    "Unsafe user-facing explanation behavior: "
                    f"{flag}"
                )

        if user_record.get(
            "raw_internal_identifiers_exposed"
        ) is not False:
            raise ExplainabilityError(
                "END_USER explanation exposed internal identifiers."
            )

        if trace_record.get(
            "trace_order_certified"
        ) is not True:
            raise ExplainabilityError(
                "Decision trace order is not certified."
            )

        if trace_record.get(
            "trace_complete_for_available_components"
        ) is not True:
            raise ExplainabilityError(
                "Decision trace is incomplete."
            )

        if trace_record.get(
            "new_decision_created"
        ) is not False:
            raise ExplainabilityError(
                "Decision trace created a new decision."
            )

        if trace_record.get(
            "causal_reason_fabricated"
        ) is not False:
            raise ExplainabilityError(
                "Decision trace fabricated a causal reason."
            )

        for technical_record in technical_group:

            for flag in required_record_true_flags:

                if technical_record.get(flag) is not True:
                    raise ExplainabilityError(
                        "Unsafe technical explanation preservation state: "
                        f"{flag}"
                    )

            for extra_flag in (
                "provenance_preserved",
                "lineage_preserved",
            ):
                if technical_record.get(
                    extra_flag
                ) is not True:
                    raise ExplainabilityError(
                        "Technical provenance/lineage guarantee missing: "
                        f"{extra_flag}"
                    )

            for flag in prohibited_record_true_flags:

                if technical_record.get(flag) is not False:
                    raise ExplainabilityError(
                        "Unsafe technical explanation behavior: "
                        f"{flag}"
                    )

            if technical_record.get(
                "internal_identifiers_exposed"
            ) is not True:
                raise ExplainabilityError(
                    "Technical explanation must expose internal identifiers."
                )

            if technical_record.get(
                "retrieval_class"
            ) != user_record.get(
                "retrieval_class"
            ):
                raise ExplainabilityError(
                    "Audience semantic drift detected in retrieval class."
                )

            if technical_record.get(
                "memory_state"
            ) != user_record.get(
                "memory_state"
            ):
                raise ExplainabilityError(
                    "Audience semantic drift detected in memory state."
                )

            if technical_record.get(
                "uncertainty_level"
            ) != user_record.get(
                "uncertainty_level"
            ):
                raise ExplainabilityError(
                    "Audience semantic drift detected in uncertainty."
                )

        safety_payload = {
            "memory_object_id":
                memory_object_id,

            "user_facing_explanation_id":
                user_record[
                    "user_facing_explanation_id"
                ],

            "decision_trace_id":
                trace_record[
                    "decision_trace_id"
                ],

            "technical_explanation_ids":
                tuple(
                    sorted(
                        item[
                            "developer_audit_explanation_id"
                        ]
                        for item in technical_group
                    )
                ),

            "retrieval_class":
                user_record[
                    "retrieval_class"
                ],

            "memory_state":
                user_record[
                    "memory_state"
                ],

            "uncertainty_level":
                user_record[
                    "uncertainty_level"
                ],
        }

        serialized = json.dumps(
            safety_payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )

        safety_digest = hashlib.sha256(
            serialized.encode("utf-8")
        ).hexdigest()

        safety_records.append(
            {
                "schema":
                    "explanation_safety_boundary_record_v1",

                "explanation_safety_boundary_id":
                    "explainabilitysafety:v1:"
                    + safety_digest,

                "memory_object_id":
                    memory_object_id,

                "user_facing_explanation_id":
                    user_record[
                        "user_facing_explanation_id"
                    ],

                "decision_trace_id":
                    trace_record[
                        "decision_trace_id"
                    ],

                "technical_explanation_ids":
                    tuple(
                        sorted(
                            item[
                                "developer_audit_explanation_id"
                            ]
                            for item in technical_group
                        )
                    ),

                "audience_semantic_invariance_preserved":
                    True,

                "source_identity_preserved":
                    True,

                "uncertainty_preserved":
                    True,

                "conflict_exception_context_preserved":
                    True,

                "retrieval_state_preserved":
                    True,

                "truth_separation_preserved":
                    True,

                "decision_trace_preserved":
                    True,

                "end_user_identifier_boundary_preserved":
                    True,

                "technical_identifier_visibility_preserved":
                    True,

                "semantic_meaning_changed":
                    False,

                "truth_adjudicated":
                    False,

                "uncertainty_hidden":
                    False,

                "conflict_hidden":
                    False,

                "causal_reason_fabricated":
                    False,

                "new_decision_created":
                    False,

                "semantic_memory_mutated":
                    False,

                "graph_mutated":
                    False,

                "authority_rescored":
                    False,

                "claim_integrity_redecided":
                    False,

                "conflict_reclassified":
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
        )

    safety_records = tuple(
        safety_records
    )

    safety_contract = {
        "schema":
            "explanation_safety_boundary_contract_v1",

        "canonical_owner":
            "EXPLAINABILITY",

        "safety_is_fail_closed":
            True,

        "all_audiences_must_preserve_same_semantic_meaning":
            True,

        "audience_detail_may_change_but_meaning_may_not":
            True,

        "end_user_internal_identifiers_must_remain_hidden":
            True,

        "developer_auditor_owner_identifiers_may_be_visible":
            True,

        "source_memory_identity_must_be_preserved":
            True,

        "provenance_must_be_preserved":
            True,

        "lineage_must_be_preserved":
            True,

        "conflict_must_be_preserved":
            True,

        "exception_context_must_be_preserved":
            True,

        "minority_context_must_be_preserved":
            True,

        "uncertainty_must_be_preserved":
            True,

        "retrieval_state_must_be_preserved":
            True,

        "truth_separation_must_be_preserved":
            True,

        "decision_trace_must_be_preserved":
            True,

        "missing_information_must_not_be_fabricated":
            True,

        "causal_reason_must_not_be_fabricated":
            True,

        "confidence_must_not_be_overstated":
            True,

        "conflict_must_not_be_silently_resolved":
            True,

        "exception_must_not_be_normalized_away":
            True,

        "historical_state_must_not_be_presented_as_current":
            True,

        "blocked_state_must_not_be_softened":
            True,

        "held_state_must_not_be_softened":
            True,

        "contested_state_must_not_be_presented_as_settled":
            True,

        "memory_must_not_be_presented_as_truth":
            True,

        "safety_must_not_adjudicate_truth":
            True,

        "safety_must_not_write_or_mutate_semantic_memory":
            True,

        "safety_must_not_mutate_learning_engine_output":
            True,

        "safety_must_not_mutate_dynamic_semantic_graph":
            True,

        "safety_must_not_rescore_authority":
            True,

        "safety_must_not_redecide_claim_integrity":
            True,

        "safety_must_not_reclassify_conflict":
            True,

        "safety_must_not_change_guard_disposition":
            True,

        "safety_must_not_create_target":
            True,

        "safety_must_not_select_target":
            True,

        "safety_must_not_score_target":
            True,

        "safety_must_not_discover_external_url":
            True,

        "safety_must_not_perform_runtime_reasoning":
            True,

        "safety_must_not_make_linking_decision":
            True,

        "safety_must_not_create_editor_highlight":
            True,

        "safety_must_not_persist_memory":
            True,

        "safety_must_not_perform_live_memory_retrieval":
            True,
    }

    bundle_payload = {
        "source_semantic_memory_package_id":
            source_package_id,

        "source_semantic_memory_package_digest":
            source_package_digest,

        "source_semantic_memory_lineage_root_id":
            source_lineage_root_id,

        "safety_record_ids":
            [
                item[
                    "explanation_safety_boundary_id"
                ]
                for item in safety_records
            ],
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

    safety_bundle = {
        "schema":
            "explanation_safety_boundary_bundle_v1",

        "explanation_safety_boundary_bundle_id":
            "explainabilitysafetybundle:v1:"
            + bundle_digest,

        "explanation_safety_boundary_bundle_digest":
            bundle_digest,

        "source_semantic_memory_package_id":
            source_package_id,

        "source_semantic_memory_package_digest":
            source_package_digest,

        "source_semantic_memory_lineage_root_id":
            source_lineage_root_id,

        "safety_records":
            safety_records,

        "safety_contract":
            safety_contract,

        "safety_record_count":
            len(
                safety_records
            ),

        "explanation_safety_boundary_enforcement_complete":
            True,

        "audience_semantic_invariance_preserved":
            True,

        "source_memory_identity_preserved":
            True,

        "provenance_preserved":
            True,

        "lineage_preserved":
            True,

        "conflict_exception_context_preserved":
            True,

        "uncertainty_preserved":
            True,

        "retrieval_state_preserved":
            True,

        "truth_separation_preserved":
            True,

        "decision_trace_preserved":
            True,

        "safety_certified":
            True,

        "truth_adjudicated":
            False,

        "semantic_memory_written":
            False,

        "semantic_memory_mutated":
            False,

        "memory_persistence_performed":
            False,

        "memory_retrieval_performed":
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

        "upstream_guard_disposition_changed":
            False,

        "target_created":
            False,

        "target_selected":
            False,

        "target_scored":
            False,

        "external_url_discovery_performed":
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
            "explanation_safety_boundary_enforcement_result_v1",

        "explainability_version":
            EXPLAINABILITY_VERSION,

        "phase":
            EXPLAINABILITY_PHASE,

        "patch":
            "4.6.29J",

        "status":
            "EXPLANATION_SAFETY_BOUNDARY_ENFORCEMENT_COMPLETED",

        "source_semantic_memory_package_id":
            source_package_id,

        "source_semantic_memory_package_digest":
            source_package_digest,

        "source_semantic_memory_lineage_root_id":
            source_lineage_root_id,

        "source_memory_object_ids":
            tuple(
                source_memory_object_ids
            ),

        "source_memory_object_count":
            source_memory_object_count,

        "explainability_architecture":
            copy.deepcopy(
                architecture
            ),

        "explanation_scope_audience_contract_bundle":
            copy.deepcopy(
                scope_bundle
            ),

        "evidence_provenance_explanation_mapping_bundle":
            copy.deepcopy(
                evidence_bundle
            ),

        "conflict_exception_explanation_handling_bundle":
            copy.deepcopy(
                conflict_bundle
            ),

        "confidence_uncertainty_explanation_contract_bundle":
            copy.deepcopy(
                uncertainty_bundle
            ),

        "decision_trace_explanation_bundle":
            copy.deepcopy(
                trace_bundle
            ),

        "user_facing_explanation_bundle":
            copy.deepcopy(
                user_bundle
            ),

        "developer_audit_explanation_bundle":
            copy.deepcopy(
                technical_bundle
            ),

        "explanation_safety_boundary_bundle":
            safety_bundle,

        "developer_audit_explanation_construction_result":
            copy.deepcopy(
                developer_audit_result
            ),

        "processing_boundaries": {
            "certified_semantic_memory_inspected":
                True,

            "explainability_architecture_defined":
                True,

            "explanation_scope_audience_contract_defined":
                True,

            "evidence_provenance_explanation_mapping_completed":
                True,

            "conflict_exception_explanation_handling_completed":
                True,

            "confidence_uncertainty_explanation_contract_defined":
                True,

            "decision_trace_explanation_construction_completed":
                True,

            "user_facing_explanation_construction_completed":
                True,

            "developer_audit_explanation_construction_completed":
                True,

            "explanation_safety_boundary_enforcement_completed":
                True,

            "explanation_generated":
                True,

            "explanation_reasoning_performed":
                False,

            "semantic_memory_written":
                False,

            "semantic_memory_mutated":
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

            "external_url_discovery_performed":
                False,

            "runtime_reasoning_performed":
                False,

            "linking_decision_performed":
                False,

            "highlight_created":
                False,
        },

        "policy":
            "CERTIFIED_EXPLANATION_SAFETY_BOUNDARY_ENFORCEMENT",

        "next":
            "final_explainability_result",
    }

def build_final_explainability_result_v1(
    safety_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.29K ? Final Explainability Result.

    Builds the canonical final Explainability package from the
    certified safety-enforced Explainability chain.

    This stage packages existing certified explanation state only.
    It does not create new semantic meaning, reasoning, decisions,
    truth judgments, target selections, linking actions, or upstream
    mutations.
    """

    if not isinstance(
        safety_result,
        dict,
    ):
        raise ExplainabilityError(
            "safety_result must be a dictionary."
        )

    expected = {
        "schema":
            "explanation_safety_boundary_enforcement_result_v1",

        "explainability_version":
            EXPLAINABILITY_VERSION,

        "phase":
            EXPLAINABILITY_PHASE,

        "patch":
            "4.6.29J",

        "status":
            "EXPLANATION_SAFETY_BOUNDARY_ENFORCEMENT_COMPLETED",

        "policy":
            "CERTIFIED_EXPLANATION_SAFETY_BOUNDARY_ENFORCEMENT",

        "next":
            "final_explainability_result",
    }

    for key, expected_value in expected.items():

        if safety_result.get(key) != expected_value:
            raise ExplainabilityError(
                "Invalid 4.6.29J lifecycle field: "
                f"{key}"
            )

    architecture = safety_result.get(
        "explainability_architecture"
    )

    scope_bundle = safety_result.get(
        "explanation_scope_audience_contract_bundle"
    )

    evidence_bundle = safety_result.get(
        "evidence_provenance_explanation_mapping_bundle"
    )

    conflict_bundle = safety_result.get(
        "conflict_exception_explanation_handling_bundle"
    )

    uncertainty_bundle = safety_result.get(
        "confidence_uncertainty_explanation_contract_bundle"
    )

    trace_bundle = safety_result.get(
        "decision_trace_explanation_bundle"
    )

    user_bundle = safety_result.get(
        "user_facing_explanation_bundle"
    )

    technical_bundle = safety_result.get(
        "developer_audit_explanation_bundle"
    )

    safety_bundle = safety_result.get(
        "explanation_safety_boundary_bundle"
    )

    boundaries = safety_result.get(
        "processing_boundaries"
    )

    for name, value in (
        (
            "explainability_architecture",
            architecture,
        ),
        (
            "explanation_scope_audience_contract_bundle",
            scope_bundle,
        ),
        (
            "evidence_provenance_explanation_mapping_bundle",
            evidence_bundle,
        ),
        (
            "conflict_exception_explanation_handling_bundle",
            conflict_bundle,
        ),
        (
            "confidence_uncertainty_explanation_contract_bundle",
            uncertainty_bundle,
        ),
        (
            "decision_trace_explanation_bundle",
            trace_bundle,
        ),
        (
            "user_facing_explanation_bundle",
            user_bundle,
        ),
        (
            "developer_audit_explanation_bundle",
            technical_bundle,
        ),
        (
            "explanation_safety_boundary_bundle",
            safety_bundle,
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
            raise ExplainabilityError(
                f"{name} must be a dictionary."
            )

    if (
        architecture.get("schema")
        != "explainability_architecture_v1"
    ):
        raise ExplainabilityError(
            "Invalid Explainability architecture schema."
        )

    if safety_bundle.get(
        "schema"
    ) != "explanation_safety_boundary_bundle_v1":
        raise ExplainabilityError(
            "Invalid safety boundary bundle schema."
        )

    if safety_bundle.get(
        "explanation_safety_boundary_enforcement_complete"
    ) is not True:
        raise ExplainabilityError(
            "Explainability safety enforcement is incomplete."
        )

    if safety_bundle.get(
        "safety_certified"
    ) is not True:
        raise ExplainabilityError(
            "Explainability safety is not certified."
        )

    required_preservation_flags = (
        "audience_semantic_invariance_preserved",
        "source_memory_identity_preserved",
        "provenance_preserved",
        "lineage_preserved",
        "conflict_exception_context_preserved",
        "uncertainty_preserved",
        "retrieval_state_preserved",
        "truth_separation_preserved",
        "decision_trace_preserved",
    )

    for flag in required_preservation_flags:

        if safety_bundle.get(flag) is not True:
            raise ExplainabilityError(
                "Final Explainability preservation guarantee missing: "
                f"{flag}"
            )

    prohibited_safety_flags = (
        "truth_adjudicated",
        "semantic_memory_written",
        "semantic_memory_mutated",
        "memory_persistence_performed",
        "memory_retrieval_performed",
        "learning_engine_output_mutated",
        "graph_mutated",
        "authority_rescored",
        "claim_integrity_redecided",
        "conflict_reclassified",
        "upstream_guard_disposition_changed",
        "target_created",
        "target_selected",
        "target_scored",
        "external_url_discovery_performed",
        "runtime_reasoning_performed",
        "linking_decision_performed",
        "highlight_created",
    )

    for flag in prohibited_safety_flags:

        if safety_bundle.get(flag) is not False:
            raise ExplainabilityError(
                "Unsafe final Explainability safety state: "
                f"{flag}"
            )

    required_boundary_true = (
        "certified_semantic_memory_inspected",
        "explainability_architecture_defined",
        "explanation_scope_audience_contract_defined",
        "evidence_provenance_explanation_mapping_completed",
        "conflict_exception_explanation_handling_completed",
        "confidence_uncertainty_explanation_contract_defined",
        "decision_trace_explanation_construction_completed",
        "user_facing_explanation_construction_completed",
        "developer_audit_explanation_construction_completed",
        "explanation_safety_boundary_enforcement_completed",
        "explanation_generated",
    )

    for flag in required_boundary_true:

        if boundaries.get(flag) is not True:
            raise ExplainabilityError(
                "Required final Explainability boundary state missing: "
                f"{flag}"
            )

    prohibited_boundary_flags = (
        "explanation_reasoning_performed",
        "semantic_memory_written",
        "semantic_memory_mutated",
        "memory_persistence_performed",
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
        "external_url_discovery_performed",
        "runtime_reasoning_performed",
        "linking_decision_performed",
        "highlight_created",
    )

    for flag in prohibited_boundary_flags:

        if boundaries.get(flag) is not False:
            raise ExplainabilityError(
                "Unsafe final Explainability boundary state: "
                f"{flag}"
            )

    source_package_id = safety_result.get(
        "source_semantic_memory_package_id"
    )

    source_package_digest = safety_result.get(
        "source_semantic_memory_package_digest"
    )

    source_lineage_root_id = safety_result.get(
        "source_semantic_memory_lineage_root_id"
    )

    source_memory_object_ids = safety_result.get(
        "source_memory_object_ids"
    )

    source_memory_object_count = safety_result.get(
        "source_memory_object_count"
    )

    if not isinstance(
        source_memory_object_ids,
        tuple,
    ):
        raise ExplainabilityError(
            "source_memory_object_ids must be a tuple."
        )

    if (
        not isinstance(
            source_memory_object_count,
            int,
        )
        or source_memory_object_count
        != len(source_memory_object_ids)
    ):
        raise ExplainabilityError(
            "Source memory object count mismatch."
        )

    if len(
        source_memory_object_ids
    ) != len(
        set(source_memory_object_ids)
    ):
        raise ExplainabilityError(
            "Duplicate source memory object IDs."
        )

    user_records = user_bundle.get(
        "user_facing_explanation_records"
    )

    technical_records = technical_bundle.get(
        "developer_audit_explanation_records"
    )

    trace_records = trace_bundle.get(
        "decision_trace_records"
    )

    safety_records = safety_bundle.get(
        "safety_records"
    )

    for name, records in (
        (
            "user_facing_explanation_records",
            user_records,
        ),
        (
            "developer_audit_explanation_records",
            technical_records,
        ),
        (
            "decision_trace_records",
            trace_records,
        ),
        (
            "safety_records",
            safety_records,
        ),
    ):
        if not isinstance(
            records,
            tuple,
        ):
            raise ExplainabilityError(
                f"{name} must be a tuple."
            )

    if len(
        user_records
    ) != source_memory_object_count:
        raise ExplainabilityError(
            "Final user explanation count mismatch."
        )

    if len(
        trace_records
    ) != source_memory_object_count:
        raise ExplainabilityError(
            "Final decision-trace count mismatch."
        )

    if len(
        safety_records
    ) != source_memory_object_count:
        raise ExplainabilityError(
            "Final safety record count mismatch."
        )

    if len(
        technical_records
    ) != (
        source_memory_object_count
        * 3
    ):
        raise ExplainabilityError(
            "Final technical explanation count mismatch."
        )

    final_payload = {
        "explainability_version":
            EXPLAINABILITY_VERSION,

        "phase":
            EXPLAINABILITY_PHASE,

        "source_semantic_memory_package_id":
            source_package_id,

        "source_semantic_memory_package_digest":
            source_package_digest,

        "source_semantic_memory_lineage_root_id":
            source_lineage_root_id,

        "source_memory_object_ids":
            source_memory_object_ids,

        "architecture_id":
            architecture.get(
                "architecture_id"
            ),

        "user_facing_explanation_ids":
            tuple(
                record[
                    "user_facing_explanation_id"
                ]
                for record in user_records
            ),

        "developer_audit_explanation_ids":
            tuple(
                record[
                    "developer_audit_explanation_id"
                ]
                for record in technical_records
            ),

        "decision_trace_ids":
            tuple(
                record[
                    "decision_trace_id"
                ]
                for record in trace_records
            ),

        "safety_record_ids":
            tuple(
                record[
                    "explanation_safety_boundary_id"
                ]
                for record in safety_records
            ),
    }

    serialized = json.dumps(
        final_payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    final_digest = hashlib.sha256(
        serialized.encode("utf-8")
    ).hexdigest()

    final_package = {
        "schema":
            "final_explainability_package_v1",

        "final_explainability_package_id":
            "finalexplainability:v1:"
            + final_digest,

        "final_explainability_package_digest":
            final_digest,

        "explainability_version":
            EXPLAINABILITY_VERSION,

        "phase":
            EXPLAINABILITY_PHASE,

        "source_semantic_memory_package_id":
            source_package_id,

        "source_semantic_memory_package_digest":
            source_package_digest,

        "source_semantic_memory_lineage_root_id":
            source_lineage_root_id,

        "source_memory_object_ids":
            tuple(
                source_memory_object_ids
            ),

        "source_memory_object_count":
            source_memory_object_count,

        "architecture":
            copy.deepcopy(
                architecture
            ),

        "scope_audience_contract":
            copy.deepcopy(
                scope_bundle
            ),

        "evidence_provenance_mapping":
            copy.deepcopy(
                evidence_bundle
            ),

        "conflict_exception_handling":
            copy.deepcopy(
                conflict_bundle
            ),

        "confidence_uncertainty_contract":
            copy.deepcopy(
                uncertainty_bundle
            ),

        "decision_trace_explanations":
            copy.deepcopy(
                trace_bundle
            ),

        "user_facing_explanations":
            copy.deepcopy(
                user_bundle
            ),

        "developer_audit_explanations":
            copy.deepcopy(
                technical_bundle
            ),

        "safety_boundary_certification":
            copy.deepcopy(
                safety_bundle
            ),

        "package_complete":
            True,

        "user_facing_explanation_ready":
            True,

        "developer_explanation_ready":
            True,

        "audit_explanation_ready":
            True,

        "owner_operator_explanation_ready":
            True,

        "decision_trace_ready":
            True,

        "safety_certified":
            True,

        "semantic_meaning_preserved":
            True,

        "source_memory_identity_preserved":
            True,

        "provenance_preserved":
            True,

        "lineage_preserved":
            True,

        "conflict_exception_context_preserved":
            True,

        "uncertainty_preserved":
            True,

        "retrieval_state_preserved":
            True,

        "truth_separation_preserved":
            True,

        "decision_trace_preserved":
            True,

        "final_package_is_explanatory_only":
            True,

        "final_package_is_truth_engine":
            False,

        "final_package_is_reasoning_engine":
            False,

        "final_package_is_target_resolver":
            False,

        "final_package_is_linking_engine":
            False,

        "truth_adjudicated":
            False,

        "new_semantic_decision_created":
            False,

        "explanation_reasoning_performed":
            False,

        "semantic_memory_written":
            False,

        "semantic_memory_mutated":
            False,

        "memory_persistence_performed":
            False,

        "memory_retrieval_performed":
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

        "upstream_guard_disposition_changed":
            False,

        "target_created":
            False,

        "target_selected":
            False,

        "target_scored":
            False,

        "external_url_discovery_performed":
            False,

        "runtime_reasoning_performed":
            False,

        "linking_decision_performed":
            False,

        "highlight_created":
            False,

        "downstream_handoff_ready":
            True,

        "runtime_read_integration_ready":
            True,

        "owner_console_explainability_ready":
            True,

        "editor_explainability_ready":
            True,

        "api_explainability_ready":
            True,

        "persistence_performed":
            False,

        "runtime_integration_performed":
            False,
    }

    return {
        "schema":
            "final_explainability_result_v1",

        "explainability_version":
            EXPLAINABILITY_VERSION,

        "phase":
            EXPLAINABILITY_PHASE,

        "patch":
            "4.6.29K",

        "status":
            "FINAL_EXPLAINABILITY_RESULT_BUILT",

        "source_semantic_memory_package_id":
            source_package_id,

        "source_semantic_memory_package_digest":
            source_package_digest,

        "source_semantic_memory_lineage_root_id":
            source_lineage_root_id,

        "source_memory_object_ids":
            tuple(
                source_memory_object_ids
            ),

        "source_memory_object_count":
            source_memory_object_count,

        "final_explainability_package":
            final_package,

        "explanation_safety_boundary_enforcement_result":
            copy.deepcopy(
                safety_result
            ),

        "processing_boundaries": {
            "certified_semantic_memory_inspected":
                True,

            "explainability_architecture_defined":
                True,

            "explanation_scope_audience_contract_defined":
                True,

            "evidence_provenance_explanation_mapping_completed":
                True,

            "conflict_exception_explanation_handling_completed":
                True,

            "confidence_uncertainty_explanation_contract_defined":
                True,

            "decision_trace_explanation_construction_completed":
                True,

            "user_facing_explanation_construction_completed":
                True,

            "developer_audit_explanation_construction_completed":
                True,

            "explanation_safety_boundary_enforcement_completed":
                True,

            "final_explainability_result_built":
                True,

            "explanation_generated":
                True,

            "explanation_reasoning_performed":
                False,

            "semantic_memory_written":
                False,

            "semantic_memory_mutated":
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

            "external_url_discovery_performed":
                False,

            "runtime_reasoning_performed":
                False,

            "linking_decision_performed":
                False,

            "highlight_created":
                False,

            "runtime_integration_performed":
                False,

            "persistence_performed":
                False,
        },

        "policy":
            "CERTIFIED_FINAL_EXPLAINABILITY_RESULT",

        "next":
            "full_explainability_hard_certification",
    }

def certify_full_explainability_v1(
    final_result: dict[str, Any],
) -> dict[str, Any]:
    """
    4.6.29L ? Full Explainability Hard Certification.

    Performs final end-to-end certification of the complete
    Explainability architecture and final package.

    Certification confirms that stages A-K have produced a complete,
    deterministic, provenance-preserving, audience-aware,
    uncertainty-aware, conflict-aware, safety-enforced explanation
    package without creating semantic truth, new reasoning,
    target-resolution behavior, linking decisions, or upstream
    mutation.
    """

    if not isinstance(
        final_result,
        dict,
    ):
        raise ExplainabilityError(
            "final_result must be a dictionary."
        )

    expected = {
        "schema":
            "final_explainability_result_v1",

        "explainability_version":
            EXPLAINABILITY_VERSION,

        "phase":
            EXPLAINABILITY_PHASE,

        "patch":
            "4.6.29K",

        "status":
            "FINAL_EXPLAINABILITY_RESULT_BUILT",

        "policy":
            "CERTIFIED_FINAL_EXPLAINABILITY_RESULT",

        "next":
            "full_explainability_hard_certification",
    }

    for key, expected_value in expected.items():

        if final_result.get(key) != expected_value:
            raise ExplainabilityError(
                "Invalid 4.6.29K lifecycle field: "
                f"{key}"
            )

    package = final_result.get(
        "final_explainability_package"
    )

    boundaries = final_result.get(
        "processing_boundaries"
    )

    if not isinstance(
        package,
        dict,
    ):
        raise ExplainabilityError(
            "final_explainability_package must be a dictionary."
        )

    if not isinstance(
        boundaries,
        dict,
    ):
        raise ExplainabilityError(
            "processing_boundaries must be a dictionary."
        )

    if package.get(
        "schema"
    ) != "final_explainability_package_v1":
        raise ExplainabilityError(
            "Invalid final Explainability package schema."
        )

    package_id = package.get(
        "final_explainability_package_id"
    )

    package_digest = package.get(
        "final_explainability_package_digest"
    )

    if (
        not isinstance(
            package_id,
            str,
        )
        or not package_id.startswith(
            "finalexplainability:v1:"
        )
    ):
        raise ExplainabilityError(
            "Invalid final Explainability package ID."
        )

    if (
        not isinstance(
            package_digest,
            str,
        )
        or len(
            package_digest
        ) != 64
    ):
        raise ExplainabilityError(
            "Invalid final Explainability package digest."
        )

    if package_id != (
        "finalexplainability:v1:"
        + package_digest
    ):
        raise ExplainabilityError(
            "Final Explainability package ID/digest mismatch."
        )

    required_package_true = (
        "package_complete",
        "user_facing_explanation_ready",
        "developer_explanation_ready",
        "audit_explanation_ready",
        "owner_operator_explanation_ready",
        "decision_trace_ready",
        "safety_certified",
        "semantic_meaning_preserved",
        "source_memory_identity_preserved",
        "provenance_preserved",
        "lineage_preserved",
        "conflict_exception_context_preserved",
        "uncertainty_preserved",
        "retrieval_state_preserved",
        "truth_separation_preserved",
        "decision_trace_preserved",
        "final_package_is_explanatory_only",
        "downstream_handoff_ready",
        "runtime_read_integration_ready",
        "owner_console_explainability_ready",
        "editor_explainability_ready",
        "api_explainability_ready",
    )

    for flag in required_package_true:

        if package.get(flag) is not True:
            raise ExplainabilityError(
                "Final Explainability certification missing required guarantee: "
                f"{flag}"
            )

    required_package_false = (
        "final_package_is_truth_engine",
        "final_package_is_reasoning_engine",
        "final_package_is_target_resolver",
        "final_package_is_linking_engine",
        "truth_adjudicated",
        "new_semantic_decision_created",
        "explanation_reasoning_performed",
        "semantic_memory_written",
        "semantic_memory_mutated",
        "memory_persistence_performed",
        "memory_retrieval_performed",
        "learning_output_promoted_to_truth",
        "learning_engine_output_mutated",
        "graph_mutated",
        "authority_rescored",
        "claim_integrity_redecided",
        "conflict_reclassified",
        "upstream_guard_disposition_changed",
        "target_created",
        "target_selected",
        "target_scored",
        "external_url_discovery_performed",
        "runtime_reasoning_performed",
        "linking_decision_performed",
        "highlight_created",
        "persistence_performed",
        "runtime_integration_performed",
    )

    for flag in required_package_false:

        if package.get(flag) is not False:
            raise ExplainabilityError(
                "Unsafe final Explainability package state: "
                f"{flag}"
            )

    required_components = (
        "architecture",
        "scope_audience_contract",
        "evidence_provenance_mapping",
        "conflict_exception_handling",
        "confidence_uncertainty_contract",
        "decision_trace_explanations",
        "user_facing_explanations",
        "developer_audit_explanations",
        "safety_boundary_certification",
    )

    for component in required_components:

        if not isinstance(
            package.get(component),
            dict,
        ):
            raise ExplainabilityError(
                "Final Explainability package component missing: "
                f"{component}"
            )

    architecture = package[
        "architecture"
    ]

    scope_bundle = package[
        "scope_audience_contract"
    ]

    evidence_bundle = package[
        "evidence_provenance_mapping"
    ]

    conflict_bundle = package[
        "conflict_exception_handling"
    ]

    uncertainty_bundle = package[
        "confidence_uncertainty_contract"
    ]

    trace_bundle = package[
        "decision_trace_explanations"
    ]

    user_bundle = package[
        "user_facing_explanations"
    ]

    technical_bundle = package[
        "developer_audit_explanations"
    ]

    safety_bundle = package[
        "safety_boundary_certification"
    ]

    expected_component_schemas = (
        (
            architecture,
            "explainability_architecture_v1",
        ),
        (
            scope_bundle,
            "explanation_scope_audience_contract_bundle_v1",
        ),
        (
            evidence_bundle,
            "evidence_provenance_explanation_mapping_bundle_v1",
        ),
        (
            conflict_bundle,
            "conflict_exception_explanation_handling_bundle_v1",
        ),
        (
            uncertainty_bundle,
            "confidence_uncertainty_explanation_contract_bundle_v1",
        ),
        (
            trace_bundle,
            "decision_trace_explanation_bundle_v1",
        ),
        (
            user_bundle,
            "user_facing_explanation_bundle_v1",
        ),
        (
            technical_bundle,
            "developer_audit_explanation_bundle_v1",
        ),
        (
            safety_bundle,
            "explanation_safety_boundary_bundle_v1",
        ),
    )

    for component, schema in expected_component_schemas:

        if component.get(
            "schema"
        ) != schema:
            raise ExplainabilityError(
                "Invalid final Explainability component schema: "
                f"{schema}"
            )

    if safety_bundle.get(
        "safety_certified"
    ) is not True:
        raise ExplainabilityError(
            "Final Explainability safety certification missing."
        )

    if safety_bundle.get(
        "explanation_safety_boundary_enforcement_complete"
    ) is not True:
        raise ExplainabilityError(
            "Final Explainability safety enforcement incomplete."
        )

    source_package_id = final_result.get(
        "source_semantic_memory_package_id"
    )

    source_package_digest = final_result.get(
        "source_semantic_memory_package_digest"
    )

    source_lineage_root_id = final_result.get(
        "source_semantic_memory_lineage_root_id"
    )

    source_memory_object_ids = final_result.get(
        "source_memory_object_ids"
    )

    source_memory_object_count = final_result.get(
        "source_memory_object_count"
    )

    if not isinstance(
        source_memory_object_ids,
        tuple,
    ):
        raise ExplainabilityError(
            "source_memory_object_ids must be a tuple."
        )

    if (
        not isinstance(
            source_memory_object_count,
            int,
        )
        or source_memory_object_count
        != len(
            source_memory_object_ids
        )
    ):
        raise ExplainabilityError(
            "Source memory object count mismatch."
        )

    if len(
        source_memory_object_ids
    ) != len(
        set(
            source_memory_object_ids
        )
    ):
        raise ExplainabilityError(
            "Duplicate source memory object IDs."
        )

    for field, expected_value in (
        (
            "source_semantic_memory_package_id",
            source_package_id,
        ),
        (
            "source_semantic_memory_package_digest",
            source_package_digest,
        ),
        (
            "source_semantic_memory_lineage_root_id",
            source_lineage_root_id,
        ),
        (
            "source_memory_object_ids",
            source_memory_object_ids,
        ),
        (
            "source_memory_object_count",
            source_memory_object_count,
        ),
    ):
        if package.get(field) != expected_value:
            raise ExplainabilityError(
                "Final Explainability source identity mismatch: "
                f"{field}"
            )

    user_records = user_bundle.get(
        "user_facing_explanation_records"
    )

    technical_records = technical_bundle.get(
        "developer_audit_explanation_records"
    )

    trace_records = trace_bundle.get(
        "decision_trace_records"
    )

    safety_records = safety_bundle.get(
        "safety_records"
    )

    if not isinstance(
        user_records,
        tuple,
    ):
        raise ExplainabilityError(
            "User-facing explanation records must be a tuple."
        )

    if not isinstance(
        technical_records,
        tuple,
    ):
        raise ExplainabilityError(
            "Developer/audit explanation records must be a tuple."
        )

    if not isinstance(
        trace_records,
        tuple,
    ):
        raise ExplainabilityError(
            "Decision trace records must be a tuple."
        )

    if not isinstance(
        safety_records,
        tuple,
    ):
        raise ExplainabilityError(
            "Safety records must be a tuple."
        )

    if len(
        user_records
    ) != source_memory_object_count:
        raise ExplainabilityError(
            "User-facing explanation record count mismatch."
        )

    if len(
        trace_records
    ) != source_memory_object_count:
        raise ExplainabilityError(
            "Decision-trace record count mismatch."
        )

    if len(
        safety_records
    ) != source_memory_object_count:
        raise ExplainabilityError(
            "Safety record count mismatch."
        )

    if len(
        technical_records
    ) != (
        source_memory_object_count
        * 3
    ):
        raise ExplainabilityError(
            "Developer/audit explanation record count mismatch."
        )

    required_boundary_true = (
        "certified_semantic_memory_inspected",
        "explainability_architecture_defined",
        "explanation_scope_audience_contract_defined",
        "evidence_provenance_explanation_mapping_completed",
        "conflict_exception_explanation_handling_completed",
        "confidence_uncertainty_explanation_contract_defined",
        "decision_trace_explanation_construction_completed",
        "user_facing_explanation_construction_completed",
        "developer_audit_explanation_construction_completed",
        "explanation_safety_boundary_enforcement_completed",
        "final_explainability_result_built",
        "explanation_generated",
    )

    for flag in required_boundary_true:

        if boundaries.get(flag) is not True:
            raise ExplainabilityError(
                "Full Explainability certification missing stage boundary: "
                f"{flag}"
            )

    required_boundary_false = (
        "explanation_reasoning_performed",
        "semantic_memory_written",
        "semantic_memory_mutated",
        "memory_persistence_performed",
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
        "external_url_discovery_performed",
        "runtime_reasoning_performed",
        "linking_decision_performed",
        "highlight_created",
        "runtime_integration_performed",
        "persistence_performed",
    )

    for flag in required_boundary_false:

        if boundaries.get(flag) is not False:
            raise ExplainabilityError(
                "Unsafe full Explainability certification boundary: "
                f"{flag}"
            )

    stage_manifest = (
        {
            "stage": "4.6.29A",
            "name":
                "CERTIFIED_SEMANTIC_MEMORY_INPUT_INSPECTION",
            "certified":
                True,
        },
        {
            "stage": "4.6.29B",
            "name":
                "EXPLAINABILITY_ARCHITECTURE_DEFINITION",
            "certified":
                True,
        },
        {
            "stage": "4.6.29C",
            "name":
                "EXPLANATION_SCOPE_AUDIENCE_CONTRACT",
            "certified":
                True,
        },
        {
            "stage": "4.6.29D",
            "name":
                "EVIDENCE_PROVENANCE_EXPLANATION_MAPPING",
            "certified":
                True,
        },
        {
            "stage": "4.6.29E",
            "name":
                "CONFLICT_EXCEPTION_EXPLANATION_HANDLING",
            "certified":
                True,
        },
        {
            "stage": "4.6.29F",
            "name":
                "CONFIDENCE_UNCERTAINTY_EXPLANATION_CONTRACT",
            "certified":
                True,
        },
        {
            "stage": "4.6.29G",
            "name":
                "DECISION_TRACE_EXPLANATION_CONSTRUCTION",
            "certified":
                True,
        },
        {
            "stage": "4.6.29H",
            "name":
                "USER_FACING_EXPLANATION_CONSTRUCTION",
            "certified":
                True,
        },
        {
            "stage": "4.6.29I",
            "name":
                "DEVELOPER_AUDIT_EXPLANATION_CONSTRUCTION",
            "certified":
                True,
        },
        {
            "stage": "4.6.29J",
            "name":
                "EXPLANATION_SAFETY_BOUNDARY_ENFORCEMENT",
            "certified":
                True,
        },
        {
            "stage": "4.6.29K",
            "name":
                "FINAL_EXPLAINABILITY_RESULT",
            "certified":
                True,
        },
        {
            "stage": "4.6.29L",
            "name":
                "FULL_EXPLAINABILITY_HARD_CERTIFICATION",
            "certified":
                True,
        },
    )

    certification_payload = {
        "final_explainability_package_id":
            package_id,

        "final_explainability_package_digest":
            package_digest,

        "source_semantic_memory_package_id":
            source_package_id,

        "source_semantic_memory_package_digest":
            source_package_digest,

        "source_semantic_memory_lineage_root_id":
            source_lineage_root_id,

        "source_memory_object_ids":
            source_memory_object_ids,

        "stage_manifest":
            stage_manifest,
    }

    serialized = json.dumps(
        certification_payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    certification_digest = hashlib.sha256(
        serialized.encode("utf-8")
    ).hexdigest()

    return {
        "schema":
            "full_explainability_hard_certification_result_v1",

        "explainability_version":
            EXPLAINABILITY_VERSION,

        "phase":
            EXPLAINABILITY_PHASE,

        "patch":
            "4.6.29L",

        "status":
            "FULL_EXPLAINABILITY_HARD_CERTIFIED",

        "certification_id":
            "explainabilitycertification:v1:"
            + certification_digest,

        "certification_digest":
            certification_digest,

        "certified":
            True,

        "stage_count":
            12,

        "stage_manifest":
            stage_manifest,

        "source_semantic_memory_package_id":
            source_package_id,

        "source_semantic_memory_package_digest":
            source_package_digest,

        "source_semantic_memory_lineage_root_id":
            source_lineage_root_id,

        "source_memory_object_ids":
            tuple(
                source_memory_object_ids
            ),

        "source_memory_object_count":
            source_memory_object_count,

        "final_explainability_package_id":
            package_id,

        "final_explainability_package_digest":
            package_digest,

        "final_explainability_package":
            copy.deepcopy(
                package
            ),

        "final_explainability_result":
            copy.deepcopy(
                final_result
            ),

        "semantic_meaning_preserved":
            True,

        "source_memory_identity_preserved":
            True,

        "provenance_preserved":
            True,

        "lineage_preserved":
            True,

        "conflict_exception_context_preserved":
            True,

        "uncertainty_preserved":
            True,

        "retrieval_state_preserved":
            True,

        "truth_separation_preserved":
            True,

        "decision_trace_preserved":
            True,

        "user_facing_explanation_ready":
            True,

        "developer_explanation_ready":
            True,

        "audit_explanation_ready":
            True,

        "owner_operator_explanation_ready":
            True,

        "runtime_read_integration_ready":
            True,

        "editor_explainability_ready":
            True,

        "api_explainability_ready":
            True,

        "owner_console_explainability_ready":
            True,

        "persistence_contract_ready":
            True,

        "downstream_handoff_ready":
            True,

        "truth_adjudicated":
            False,

        "new_semantic_decision_created":
            False,

        "explanation_reasoning_performed":
            False,

        "semantic_memory_written":
            False,

        "semantic_memory_mutated":
            False,

        "memory_persistence_performed":
            False,

        "memory_retrieval_performed":
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

        "upstream_guard_disposition_changed":
            False,

        "target_created":
            False,

        "target_selected":
            False,

        "target_scored":
            False,

        "external_url_discovery_performed":
            False,

        "runtime_reasoning_performed":
            False,

        "linking_decision_performed":
            False,

        "highlight_created":
            False,

        "runtime_integration_performed":
            False,

        "persistence_performed":
            False,

        "certification_policy":
            "FULL_END_TO_END_EXPLAINABILITY_HARD_CERTIFICATION",

        "next":
            "explainability_integration_gate",
    }
