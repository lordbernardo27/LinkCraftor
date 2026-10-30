
"""Phase 3.7.3 alias evidence and preservation tests."""

from copy import deepcopy

import pytest

from backend.server.engine.semantic_intelligence_enricher import (
    enrich_selected_phrase_candidates,
)
from backend.server.engine.semantic_intelligence_alias_enrichment import (
    enrich_phrase_aliases,
)


def base(identity="candidate_unverified"):
    return {
        "enriched_candidates": [{
            "candidate_id": "c1",
            "candidate_index": 0,
            "original_candidate": {
                "phrase": "high blood pressure",
                "upstream_candidate_id": "c1",
            },
            "canonical_concept_entity": {"status": identity},
            "semantic_memory": {
                "status": "no_evidence",
                "memory_matches": [],
                "evidence_ids": [],
            },
            "intelligence_graph": {
                "status": "no_evidence",
                "concept_matches": [],
            },
        }],
        "evidence_registry": {},
    }


def add_concept_alias(data, aliases):
    match = {
        "concept_key": "hypertension",
        "concept": "Hypertension",
        "match_type": "concept_match",
    }
    data["enriched_candidates"][0]["intelligence_graph"][
        "concept_matches"
    ] = [match]
    data["evidence_registry"]["graph_concept_0_0"] = {
        "candidate_index": 0,
        "source": "workspace_concept_store",
        "evidence_type": "concept_or_alias_match",
        "concept_key": "hypertension",
        "match_type": "concept_match",
        "certified": False,
        "source_record": {
            "aliases": aliases,
        },
    }


@pytest.mark.parametrize("workspace", [None, "ws_alias_test"])
def test_both_real_enricher_return_paths(workspace):
    candidates = [{
        "phrase": "high blood pressure",
        "upstream_candidate_id": "c1",
    }]
    before = deepcopy(candidates)

    result = enrich_selected_phrase_candidates(
        selected_candidates=candidates,
        workspace_id=workspace,
    )

    assert candidates == before
    assert len(result["enriched_candidates"]) == 1
    entry = result["enriched_candidates"][0]
    assert entry["original_candidate"] == before[0]
    assert entry["candidate_id"] == "c1"
    assert "alias_enrichment" in entry
    assert entry["alias_enrichment"]["certified"] is False


def test_explicit_alias_from_concept_record():
    data = base()
    add_concept_alias(data, ["high blood pressure"])

    result = enrich_phrase_aliases(data)[
        "enriched_candidates"
    ][0]["alias_enrichment"]

    assert result["status"] == "evidence_found_unverified"
    assert result["alias_candidates"][0]["alias"] == "high blood pressure"
    assert result["alias_evidence_ids"] == ["graph_concept_0_0"]
    assert result["automatic_alias_linking_blocked"] is True


def test_apple_ambiguity_is_preserved():
    data = base("ambiguous")
    add_concept_alias(data, ["Apple"])

    result = enrich_phrase_aliases(data)[
        "enriched_candidates"
    ][0]["alias_enrichment"]

    assert result["status"] == "ambiguous"
    assert result["canonical_identity_status"] == "ambiguous"
    assert result["automatic_alias_linking_blocked"] is True


def test_no_evidence_does_not_generate_synonyms():
    result = enrich_phrase_aliases(base())[
        "enriched_candidates"
    ][0]["alias_enrichment"]

    assert result["status"] == "no_evidence"
    assert result["alias_candidates"] == []


def test_memory_alias_with_evidence():
    data = base()
    entry = data["enriched_candidates"][0]

    entry["semantic_memory"]["memory_matches"] = [{
        "text": "hypertension",
        "aliases": ["high blood pressure"],
    }]
    entry["semantic_memory"]["evidence_ids"] = ["memory_0_0"]
    data["evidence_registry"]["memory_0_0"] = {
        "candidate_index": 0,
        "source": "semantic_memory",
    }

    result = enrich_phrase_aliases(data)[
        "enriched_candidates"
    ][0]["alias_enrichment"]

    assert result["status"] == "evidence_found_unverified"
    assert result["alias_candidates"][0]["source"] == "semantic_memory"


def test_missing_memory_evidence_is_invalid():
    data = base()
    entry = data["enriched_candidates"][0]
    entry["semantic_memory"]["memory_matches"] = [{
        "aliases": ["high blood pressure"]
    }]
    entry["semantic_memory"]["evidence_ids"] = ["missing"]

    result = enrich_phrase_aliases(data)[
        "enriched_candidates"
    ][0]["alias_enrichment"]

    assert result["status"] == "invalid"
    assert result["alias_candidates"] == []


def test_malformed_aliases_do_not_pass():
    data = base()
    add_concept_alias(data, ["valid alias", 42])

    result = enrich_phrase_aliases(data)[
        "enriched_candidates"
    ][0]["alias_enrichment"]

    assert result["status"] == "invalid"


def test_concept_match_without_aliases_not_invented():
    data = base()
    add_concept_alias(data, [])

    result = enrich_phrase_aliases(data)[
        "enriched_candidates"
    ][0]["alias_enrichment"]

    assert result["status"] == "no_evidence"


def test_original_intelligence_and_registry_preserved():
    data = base()
    add_concept_alias(data, ["high blood pressure"])
    before = deepcopy(data)

    enrich_phrase_aliases(data)

    assert data["evidence_registry"] == before["evidence_registry"]
    assert data["enriched_candidates"][0]["original_candidate"] == (
        before["enriched_candidates"][0]["original_candidate"]
    )
    assert data["enriched_candidates"][0]["intelligence_graph"] == (
        before["enriched_candidates"][0]["intelligence_graph"]
    )
    assert data["enriched_candidates"][0]["semantic_memory"] == (
        before["enriched_candidates"][0]["semantic_memory"]
    )


def test_empty_batch():
    result = enrich_phrase_aliases({
        "enriched_candidates": [],
        "evidence_registry": {},
    })
    assert result["enriched_candidates"] == []


def test_candidate_order_mismatch_rejected():
    data = base()
    data["enriched_candidates"][0]["candidate_index"] = 5

    with pytest.raises(ValueError):
        enrich_phrase_aliases(data)
