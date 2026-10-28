"""Phase 3.6.1M: canonical Semantic Memory reference regressions."""

from copy import deepcopy

import pytest

from backend.server.semantic_intelligence.semantic_memory_v1 import (
    SEMANTIC_MEMORY_PHASE,
    SEMANTIC_MEMORY_VERSION,
    define_semantic_memory_retrieval_read_contract_v1 as retrieve,
    build_final_semantic_memory_result_v1 as build,
    certify_full_semantic_memory_v1 as certify,
)
from backend.server.engine.semantic_memory_certification_reference_adapter import (
    inspect_semantic_memory_certification_reference as inspect,
)


MEMORY_ID = "semanticmemoryobject:v1:" + "a" * 64
ROOT_ID = "semanticmemorylineageroot:v1:" + "b" * 64

PARTITIONS = (
    "default_readable_memory_ids",
    "held_memory_ids",
    "blocked_memory_ids",
    "contested_memory_ids",
    "historical_memory_ids",
)

FORBIDDEN = (
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
)

TRUE_FLAGS = (
    "semantic_memory_admission_performed",
    "semantic_memory_object_created",
    "memory_version_created",
    "conflict_exception_memory_preserved",
    "memory_retention_decision_performed",
    "memory_provenance_lineage_built",
)

FALSE_FLAGS = (
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
)

LINEAGE_FALSE = (
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
)

AUTHORITY_FLAGS = (
    "certified",
    "authority_verified",
    "certification_performed",
    "memory_is_certified_truth",
)


def make_lineage_fixture():
    memory = {
        "schema": "semantic_memory_object_v1",
        "memory_object_id": MEMORY_ID,
        "memory_lineage_record_id": "synthetic-lineage-record-001",
        "memory_state": "ACTIVE",
        "stability_state": "STABLE",
        "retention_state": "RETAIN",
        "retention_decision_finalized": True,
        "supersession_state": "NOT_SUPERSEDED",
        "current_version": 1,
        "source_learning_object_id": "synthetic-learning-object",
        "provenance_complete": True,
        "lineage_complete": True,
        "history_preserved": True,
        "memory_persisted": False,
        "retrieval_performed": False,
        "is_certified_fact": False,
        "is_learned_truth": False,
    }

    return {
        "schema": "semantic_memory_provenance_lineage_result_v1",
        "semantic_memory_version": SEMANTIC_MEMORY_VERSION,
        "phase": SEMANTIC_MEMORY_PHASE,
        "patch": "4.6.28J",
        "status": "SEMANTIC_MEMORY_PROVENANCE_LINEAGE_COMPLETED",
        "policy": "CERTIFIED_SEMANTIC_MEMORY_PROVENANCE_LINEAGE",
        "next": "memory_retrieval_read_contract",
        "source_final_learning_engine_package_id": "synthetic-learning-package",
        "source_final_learning_engine_package_digest": "synthetic-learning-digest",
        "source_final_graph_id": "synthetic-final-graph",
        "source_final_graph_digest": "synthetic-graph-digest",
        "source_graph_snapshot_id": "synthetic-graph-snapshot",
        "source_lineage_root_id": "synthetic-upstream-lineage",
        "source_learning_lineage_root_id": "synthetic-learning-lineage",
        "semantic_memory_lineage_root_id": ROOT_ID,
        "semantic_memory_ownership_mutation_contract": {
            "schema": "semantic_memory_ownership_mutation_contract_v1",
            "allowed_memory_mutations": ("CREATE_RETRIEVAL_METADATA",),
            "forbidden_memory_mutations": FORBIDDEN,
        },
        "semantic_memory_stability_retention_bundle": {
            "schema": "semantic_memory_stability_retention_bundle_v1",
            "stability_retention_applied": True,
            "retention_decisions_finalized": True,
        },
        "semantic_memory_provenance_lineage_bundle": {
            "schema": "semantic_memory_provenance_lineage_bundle_v1",
            "provenance_complete": True,
            "lineage_complete": True,
            "history_preserved": True,
            "lineage_bound_memory_objects": (memory,),
            "lineage_records": ({
                "schema": "semantic_memory_provenance_lineage_record_v1",
                "memory_object_id": MEMORY_ID,
                "memory_lineage_record_id": "synthetic-lineage-record-001",
            },),
            **{key: False for key in LINEAGE_FALSE},
        },
        "certified_learning_engine_input_inspection": {
            "schema":
                "semantic_memory_learning_engine_input_inspection_result_v1",
        },
        "processing_boundaries": {
            **{key: True for key in TRUE_FLAGS},
            **{key: False for key in FALSE_FLAGS},
        },
    }


@pytest.fixture
def canonical_inputs():
    lineage = make_lineage_fixture()
    retrieval = retrieve(deepcopy(lineage))
    final = build(deepcopy(retrieval))
    certification = certify(deepcopy(final))

    return {
        "workspace_id": "phase361_producer_integration",
        "operational_memory_id": "synthetic-operational",
        "canonical_memory_object_id": MEMORY_ID,
        "certification_result": certification,
        "final_package": final["final_semantic_memory_package"],
        "retrieval_bundle":
            retrieval["semantic_memory_retrieval_read_contract_bundle"],
    }


def check_non_authority(result):
    for field in AUTHORITY_FLAGS:
        assert result[field] is False, (field, result)


def inspect_without_mutation(inputs):
    original = deepcopy(inputs)
    result = inspect(**inputs)
    assert inputs == original, "Reference inspection mutated inputs"
    check_non_authority(result)
    return result


def assert_rejected(inputs):
    result = inspect_without_mutation(inputs)
    assert result["reference_integrity_valid"] is False, result
    assert result["certification_reference"] is None
    assert result["certification_lineage"] is None


def test_real_producer_chain_reference_integrity(canonical_inputs):
    package = canonical_inputs["final_package"]
    assert isinstance(package["final_memory_objects"], (list, tuple))
    assert "final_memory_object_ids" not in package

    for field in PARTITIONS:
        assert isinstance(package[field], (list, tuple))

    result = inspect_without_mutation(canonical_inputs)

    assert result["reference_integrity_valid"] is True, result
    assert result["canonical_memory_object_id"] == MEMORY_ID


def test_canonical_certifier_does_not_grant_adapter_authority(
    canonical_inputs,
):
    assert canonical_inputs["certification_result"]["certified"] is True

    result = inspect_without_mutation(canonical_inputs)
    assert result["reference_integrity_valid"] is True
    check_non_authority(result)


def test_final_package_digest_tampering_rejected(canonical_inputs):
    canonical_inputs["final_package"][
        "final_semantic_memory_package_digest"
    ] = "0" * 64

    assert_rejected(canonical_inputs)


def test_retrieval_contract_digest_tampering_rejected(canonical_inputs):
    canonical_inputs["retrieval_bundle"][
        "retrieval_contract_bundle_digest"
    ] = "0" * 64

    assert_rejected(canonical_inputs)


@pytest.mark.parametrize("partition", PARTITIONS)
def test_each_partition_tampering_rejected(canonical_inputs, partition):
    package = canonical_inputs["final_package"]
    package[partition] = tuple(package[partition]) + (
        "synthetic-unrecognized-memory",
    )

    assert_rejected(canonical_inputs)


def test_duplicate_canonical_object_identity_rejected(canonical_inputs):
    package = canonical_inputs["final_package"]
    package["final_memory_objects"] = tuple(
        package["final_memory_objects"]
    ) * 2

    assert_rejected(canonical_inputs)


def test_missing_canonical_object_identity_rejected(canonical_inputs):
    package = canonical_inputs["final_package"]
    objects = deepcopy(package["final_memory_objects"])
    objects[0].pop("memory_object_id", None)
    package["final_memory_objects"] = objects

    assert_rejected(canonical_inputs)


def test_explicit_ids_must_match_canonical_objects(canonical_inputs):
    canonical_inputs["final_package"]["final_memory_object_ids"] = [
        "synthetic-unrecognized-memory"
    ]

    assert_rejected(canonical_inputs)


def test_retrieval_metadata_digest_tampering_rejected(canonical_inputs):
    bundle = canonical_inputs["retrieval_bundle"]
    records = deepcopy(bundle["retrieval_metadata_records"])
    assert records, "Synthetic fixture must generate metadata"
    records[0]["memory_state"] = "TAMPERED"
    bundle["retrieval_metadata_records"] = records

    assert_rejected(canonical_inputs)


def test_cross_artifact_lineage_tampering_rejected(canonical_inputs):
    canonical_inputs["retrieval_bundle"][
        "semantic_memory_lineage_root_id"
    ] = "synthetic-wrong-lineage-root"

    assert_rejected(canonical_inputs)
