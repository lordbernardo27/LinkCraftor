
"""Phase 3.11.3: Advisory handoff identity contract tests."""

from copy import deepcopy
import pytest

from backend.server.engine.semantic_enricher_scorer_handoff import (
    HandoffContractError,
    prepare_original_scorer_handoff,
)


def identity_fixture(with_upstream_ids=False):
    workspace = "ws_identity_verification"
    candidates = [
        {"phrase": "maternal health", "position": 10},
        {"phrase": "maternal health", "position": 60},
    ]

    if with_upstream_ids:
        for index, candidate in enumerate(candidates):
            candidate["upstream_candidate_id"] = f"upstream_{index}"

    enriched = []

    for index, candidate in enumerate(candidates):
        enriched.append({
            "candidate_index": index,
            "candidate_id": candidate.get("upstream_candidate_id"),
            "original_candidate": deepcopy(candidate),
            "evidence_certification": {
                "certified": False,
                "certification_performed": False,
                "semantic_certification_status": "not_performed",
                "workspace_id": workspace,
                "candidate_index": index,
                "status": "no_evidence",
            },
            "explainability": {
                "certified": False,
                "scorer_decision_performed": False,
                "evidence_ids": [],
            },
            "scorer_readiness": {"ready": False},
        })

    return {
        "ok": True,
        "candidate_count": len(candidates),
        "context": {"workspace_id": workspace},
        "candidates": candidates,
        "enriched_candidates": enriched,
        "evidence_registry": {},
        "downstream_contract": {
            "consumer": "original_scorer",
            "enrichment_is_advisory": True,
            "final_link_allocation_performed": False,
            "route_dispatch_performed": False,
            "target_resolution_performed": False,
            "final_highlight_validation_performed": False,
        },
    }


def test_3113_missing_optional_upstream_ids_are_preserved():
    package = identity_fixture()
    before = deepcopy(package)

    result = prepare_original_scorer_handoff(
        enrichment_package=package
    )

    assert result["status"] == "advisory_handoff_prepared"
    assert result["candidates_forwarded"] == 2
    assert result["candidates_removed"] == 0
    assert [c["candidate_id"] for c in result["candidates"]] == [
        None, None
    ]
    assert [
        c["original_candidate"] for c in result["candidates"]
    ] == package["candidates"]
    assert result["candidates"][0]["original_candidate"] != (
        result["candidates"][1]["original_candidate"]
    )
    assert package == before
    assert result["production_scorer_invoked"] is False
    assert result["linking_performed"] is False


def test_3113_supplied_upstream_ids_are_preserved():
    package = identity_fixture(with_upstream_ids=True)
    result = prepare_original_scorer_handoff(
        enrichment_package=package
    )

    assert [c["candidate_id"] for c in result["candidates"]] == [
        "upstream_0", "upstream_1"
    ]
    assert result["candidates_forwarded"] == 2


def test_3113_forged_candidate_id_rejected():
    package = identity_fixture(with_upstream_ids=True)
    package["enriched_candidates"][0]["candidate_id"] = "forged_id"

    with pytest.raises(
        HandoffContractError,
        match="Candidate identity lineage mismatch",
    ):
        prepare_original_scorer_handoff(
            enrichment_package=package
        )


def test_3113_reordered_original_candidate_rejected():
    package = identity_fixture()
    package["enriched_candidates"][0]["original_candidate"] = deepcopy(
        package["candidates"][1]
    )

    with pytest.raises(
        HandoffContractError,
        match="Original candidate mismatch",
    ):
        prepare_original_scorer_handoff(
            enrichment_package=package
        )
