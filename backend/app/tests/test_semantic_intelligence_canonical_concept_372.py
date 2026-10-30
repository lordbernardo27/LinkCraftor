
"""3.7.2: Concept ambiguity and identity preservation tests."""

from copy import deepcopy
import pytest

from backend.server.engine.semantic_intelligence_enricher import (
    enrich_selected_phrase_candidates,
)
from backend.server.engine.semantic_intelligence_canonical_concept_enrichment import (
    enrich_canonical_concept_entities,
)


def make_package(keys, status=None):
    matches = [
        {"concept_key": key, "concept": key, "match_type": "concept_match"}
        for key in keys
    ]
    registry = {
        f"graph_concept_0_{i}": {
            "source": "workspace_concept_store",
            "evidence_type": "concept_or_alias_match",
            "candidate_index": 0,
            "concept_key": m["concept_key"],
            "concept": m["concept"],
            "match_type": m["match_type"],
            "relationship_asserted": False,
            "certified": False,
            "validity_status": "not_evaluated",
        }
        for i, m in enumerate(matches)
    }
    return {
        "enriched_candidates": [{
            "candidate_id": "c1",
            "candidate_index": 0,
            "original_candidate": {"phrase": "Apple"},
            "intelligence_graph": {
                "status": status or (
                    "concept_evidence_found" if matches else "no_evidence"
                ),
                "concept_matches": matches,
            },
        }],
        "evidence_registry": registry,
    }


@pytest.mark.parametrize("workspace", [None, "ws_concept_test"])
def test_both_real_enricher_returns_have_summary(workspace):
    originals = [{
        "phrase": "Apple",
        "upstream_candidate_id": "c1",
    }]
    snapshot = deepcopy(originals)
    output = enrich_selected_phrase_candidates(
        selected_candidates=originals,
        workspace_id=workspace,
    )
    entry = output["enriched_candidates"][0]
    assert originals == snapshot
    assert entry["original_candidate"] == snapshot[0]
    assert entry["candidate_id"] == "c1"
    assert entry["candidate_index"] == 0
    assert "canonical_concept_entity" in entry
    assert entry["canonical_concept_entity"]["certified"] is False


def test_distinct_apple_meanings_ambiguous_and_blocked():
    result = enrich_canonical_concept_entities(
        make_package(["apple_fruit", "apple_company"])
    )["enriched_candidates"][0]["canonical_concept_entity"]
    assert result["status"] == "ambiguous"
    assert result["automatic_concept_linking_blocked"] is True
    assert result["canonical_entity_id"] is None
    assert len(result["candidate_evidence_ids"]) == 2


def test_same_concept_multiple_matches_not_ambiguous():
    result = enrich_canonical_concept_entities(
        make_package(["apple_fruit", "apple_fruit"])
    )["enriched_candidates"][0]["canonical_concept_entity"]
    assert result["status"] == "candidate_unverified"
    assert result["identity_verified"] is False


def test_one_concept_remains_unverified():
    result = enrich_canonical_concept_entities(
        make_package(["heart_attack"])
    )["enriched_candidates"][0]["canonical_concept_entity"]
    assert result["status"] == "candidate_unverified"
    assert result["canonical_name"] is None


def test_no_evidence_does_not_fabricate_identity():
    result = enrich_canonical_concept_entities(
        make_package([])
    )["enriched_candidates"][0]["canonical_concept_entity"]
    assert result["status"] == "no_evidence"
    assert result["candidate_evidence_ids"] == []
    assert result["canonical_concept_id"] is None


def test_missing_evidence_invalidates_result():
    data = make_package(["apple_fruit"])
    data["evidence_registry"].clear()
    result = enrich_canonical_concept_entities(
        data
    )["enriched_candidates"][0]["canonical_concept_entity"]
    assert result["status"] == "invalid"
    assert result["automatic_concept_linking_blocked"] is True


def test_forged_certification_invalidates_result():
    data = make_package(["apple_fruit"])
    data["evidence_registry"]["graph_concept_0_0"]["certified"] = True
    result = enrich_canonical_concept_entities(
        data
    )["enriched_candidates"][0]["canonical_concept_entity"]
    assert result["status"] == "invalid"


@pytest.mark.parametrize(
    "status", ["unavailable", "error", "invalid", "stale"]
)
def test_unusable_statuses_block_concept_linking(status):
    result = enrich_canonical_concept_entities(
        make_package([], status=status)
    )["enriched_candidates"][0]["canonical_concept_entity"]
    assert result["status"] == status
    assert result["automatic_concept_linking_blocked"] is True


def test_original_data_preserved():
    data = make_package(["apple_fruit", "apple_company"])
    before = deepcopy(data)
    enrich_canonical_concept_entities(data)
    assert data["evidence_registry"] == before["evidence_registry"]
    assert data["enriched_candidates"][0]["intelligence_graph"] == (
        before["enriched_candidates"][0]["intelligence_graph"]
    )
    assert data["enriched_candidates"][0]["original_candidate"] == (
        before["enriched_candidates"][0]["original_candidate"]
    )


def test_empty_batch():
    data = {"enriched_candidates": [], "evidence_registry": {}}
    assert enrich_canonical_concept_entities(
        data
    )["enriched_candidates"] == []


def test_candidate_order_mismatch_denied():
    data = make_package([])
    data["enriched_candidates"][0]["candidate_index"] = 2
    with pytest.raises(ValueError):
        enrich_canonical_concept_entities(data)


def test_workspace_free_graph_not_executed_is_not_invalid():
    data = make_package([], status="not_executed")
    result = enrich_canonical_concept_entities(
        data
    )["enriched_candidates"][0]["canonical_concept_entity"]

    assert result["status"] == "not_executed"
    assert result["canonical_concept_id"] is None
    assert result["identity_verified"] is False
    assert result["automatic_concept_linking_blocked"] is True


def test_workspace_free_real_enricher_preserves_not_executed():
    output = enrich_selected_phrase_candidates(
        selected_candidates=[{
            "phrase": "high blood pressure",
            "upstream_candidate_id": "alias_test_001",
        }],
        workspace_id=None,
    )
    identity = output["enriched_candidates"][0]["canonical_concept_entity"]

    assert identity["status"] == "not_executed"
    assert identity["certified"] is False
