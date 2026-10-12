from copy import deepcopy

from backend.server.stores.highlight_selection_engine import (
    select_highlight_candidates,
)


def _candidate(phrase, **extra):
    return {
        "phrase": phrase,
        "workspace_id": "ws-test",
        "doc_id": "doc-1",
        **extra,
    }


def _run(article, candidates, targets=None):
    return select_highlight_candidates(
        workspace_id="ws-test",
        doc_id="doc-1",
        article_text=article,
        phrase_candidates=candidates,
        resolved_targets=targets,
        vertical="general",
    )


def _ranking_key(item):
    return (
        item["selection_score"],
        1 if item["link_status"] == "linked" else 0,
        len(item["phrase_key"]),
    )


def test_final_different_scores_rank_descending():
    counts = [
        ("Alpha Signal", 1),
        ("Beta Signal", 2),
        ("Gamma Signal", 5),
        ("Delta Signal", 10),
    ]

    article = " ".join(
        (phrase + ". ") * count
        for phrase, count in counts
    )

    incoming = [
        _candidate(phrase, strength_score=40)
        for phrase, _ in counts
    ]

    before = deepcopy(incoming)
    result = _run(article, incoming)
    records = result["all_selected_phrase_candidates"]

    assert result["ok"] is True
    assert len(records) == 4
    assert incoming == before

    scores = [
        item["selection_score"]
        for item in records
    ]

    assert len(set(scores)) >= 3
    assert scores == sorted(scores, reverse=True)
    assert {
        item["phrase"] for item in records
    } == {
        phrase for phrase, _ in counts
    }


def test_final_linked_candidate_wins_equal_score_tie():
    incoming = [
        _candidate("Lunar Metric", strength_score=40),
        _candidate("Solar Metric", strength_score=40),
    ]

    before = deepcopy(incoming)

    result = _run(
        "Lunar Metric. Solar Metric.",
        incoming,
        [
            {
                "phrase": "Solar Metric",
                "target_url": "https://example.org/solar",
            }
        ],
    )

    records = result["all_selected_phrase_candidates"]

    assert len(records) == 2
    assert incoming == before

    assert (
        records[0]["selection_score"]
        == records[1]["selection_score"]
    )

    assert (
        len(records[0]["phrase_key"])
        == len(records[1]["phrase_key"])
    )

    assert records[0]["phrase"] == "Solar Metric"
    assert records[0]["link_status"] == "linked"
    assert records[0]["resolver_found_target"] is True

    assert records[1]["phrase"] == "Lunar Metric"
    assert records[1]["link_status"] == "unlinked_opportunity"

    assert result["stats"]["linked_count"] == 1
    assert result["stats"]["unlinked_opportunity_count"] == 1


def test_final_longer_anchor_wins_equal_score_tie():
    incoming = [
        _candidate("Short", strength_score=40),
        _candidate("Longer Phrase", strength_score=40),
    ]

    result = _run(
        "Short. Longer Phrase.",
        incoming,
    )

    records = result["all_selected_phrase_candidates"]

    assert len(records) == 2

    assert (
        records[0]["selection_score"]
        == records[1]["selection_score"]
    )

    assert (
        records[0]["link_status"]
        == records[1]["link_status"]
    )

    assert records[0]["phrase"] == "Longer Phrase"
    assert records[1]["phrase"] == "Short"


def test_final_selector_does_not_require_resolvers():
    incoming = [
        _candidate("Lunar Metric", strength_score=40),
        _candidate("Solar Metric", strength_score=40),
    ]

    before = deepcopy(incoming)

    result = _run(
        "Lunar Metric. Solar Metric.",
        incoming,
        None,
    )

    records = result["all_selected_phrase_candidates"]

    assert result["ok"] is True
    assert len(records) == 2
    assert incoming == before

    assert all(
        item["link_status"] == "unlinked_opportunity"
        for item in records
    )

    assert all(
        item["resolver_found_target"] is False
        for item in records
    )

    assert result["stats"]["linked_count"] == 0
    assert result["stats"]["unlinked_opportunity_count"] == 2


def test_final_240_candidates_survive_without_density_cap():
    phrases = [
        f"Clinical Topic {index:03d}"
        for index in range(240)
    ]

    article = ". ".join(phrases) + "."

    incoming = [
        _candidate(
            phrase,
            upstream_candidate_id=f"candidate-{index:03d}",
            custom_lineage={
                "source": "final-certification",
                "index": index,
            },
        )
        for index, phrase in enumerate(phrases)
    ]

    incoming.extend([
        _candidate(
            phrases[0],
            upstream_candidate_id="duplicate",
        ),
        _candidate(
            "Phrase Absent From Article",
            upstream_candidate_id="absent",
        ),
    ])

    before = deepcopy(incoming)
    result = _run(article, incoming)

    selected = result["selected"]
    canonical = result["all_selected_phrase_candidates"]
    stats = result["stats"]

    assert result["ok"] is True
    assert len(selected) == 240
    assert len(canonical) == 240
    assert len(result["rejected"]) == 2

    assert stats["total_candidates"] == 242
    assert stats["ranked_count"] == 240
    assert stats["rejected_count"] == 2

    assert selected is result["candidates"]
    assert canonical is not selected
    assert canonical == selected
    assert incoming == before

    assert {
        item["phrase"] for item in canonical
    } == set(phrases)

    assert len({
        item["selection_phrase_id"]
        for item in canonical
    }) == 240

    assert len({
        item["selection_occurrence_id"]
        for item in canonical
    }) == 240

    assert {
        item["upstream_candidate_id"]
        for item in canonical
    } == {
        f"candidate-{index:03d}"
        for index in range(240)
    }

    for item in canonical:
        lineage = item["custom_lineage"]

        assert lineage["source"] == "final-certification"
        assert item["upstream_candidate_id"] == (
            f"candidate-{lineage['index']:03d}"
        )

    keys = [
        _ranking_key(item)
        for item in canonical
    ]

    assert keys == sorted(keys, reverse=True)

    assert all(
        item["link_status"] == "unlinked_opportunity"
        for item in canonical
    )
