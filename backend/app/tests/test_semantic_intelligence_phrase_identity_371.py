
"""3.7.1 ? Canonical phrase identity preservation regressions."""

from copy import deepcopy

import pytest

from backend.server.engine.semantic_intelligence_enricher import (
    enrich_selected_phrase_candidates,
)


@pytest.mark.parametrize(
    "candidates",
    [
        [
            {
                "phrase": "blood pressure",
                "upstream_candidate_id": "candidate_A",
            },
            {
                "phrase": "heart health",
                "upstream_candidate_id": "candidate_B",
            },
        ],
        [
            {
                "phrase": "blood pressure",
                "upstream_candidate_id": "candidate_A",
            },
            {
                "phrase": "blood pressure",
                "upstream_candidate_id": "candidate_B",
            },
        ],
        [
            {
                "phrase": "blood pressure",
            },
        ],
    ],
)
def test_original_candidate_identity_and_order_preserved(candidates):
    original = deepcopy(candidates)

    result = enrich_selected_phrase_candidates(
        selected_candidates=candidates,
        workspace_id="ws_identity_test",
    )

    enriched = result["enriched_candidates"]

    assert len(enriched) == len(original)
    assert candidates == original

    for index, entry in enumerate(enriched):
        assert entry["candidate_index"] == index
        assert entry["original_candidate"] == original[index]
        assert (
            entry["candidate_id"]
            == original[index].get("upstream_candidate_id")
        )


def test_missing_identity_not_fabricated():
    result = enrich_selected_phrase_candidates(
        selected_candidates=[{"phrase": "blood pressure"}],
        workspace_id="ws_identity_test",
    )

    entry = result["enriched_candidates"][0]

    assert entry["candidate_id"] is None
    assert entry["candidate_index"] == 0


def test_duplicate_phrases_keep_distinct_upstream_ids():
    result = enrich_selected_phrase_candidates(
        selected_candidates=[
            {
                "phrase": "blood pressure",
                "upstream_candidate_id": "candidate_A",
            },
            {
                "phrase": "blood pressure",
                "upstream_candidate_id": "candidate_B",
            },
        ],
        workspace_id="ws_identity_test",
    )

    ids = [
        entry["candidate_id"]
        for entry in result["enriched_candidates"]
    ]

    assert ids == ["candidate_A", "candidate_B"]


def test_empty_batch_preserves_zero_candidates():
    result = enrich_selected_phrase_candidates(
        selected_candidates=[],
        workspace_id="ws_identity_test",
    )

    assert result["enriched_candidates"] == []
