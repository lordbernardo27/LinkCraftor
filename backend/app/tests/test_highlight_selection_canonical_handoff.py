from copy import deepcopy
from hashlib import sha256

from backend.server.stores.highlight_selection_engine import (
    select_highlight_candidates,
)


WORKSPACE = "ws-test"
DOCUMENT = "doc-1"


def run_selector(article_text, candidates):
    return select_highlight_candidates(
        workspace_id=WORKSPACE,
        doc_id=DOCUMENT,
        article_text=article_text,
        phrase_candidates=candidates,
        resolved_targets=None,
        vertical="general",
    )


def test_canonical_handoff_empty_collection():
    result = run_selector("Heart rate matters.", [])

    assert result["ok"] is True
    assert result["selected"] == []
    assert result["candidates"] == []
    assert result["all_selected_phrase_candidates"] == []
    assert result["rejected"] == []

    assert result["selected"] is result["candidates"]
    assert (
        result["all_selected_phrase_candidates"]
        is not result["selected"]
    )


def test_canonical_handoff_absent_phrase_rejection():
    result = run_selector(
        "Heart rate matters.",
        [{
            "phrase": "Blood Pressure",
            "workspace_id": WORKSPACE,
            "doc_id": DOCUMENT,
        }],
    )

    assert result["ok"] is True
    assert result["all_selected_phrase_candidates"] == []
    assert result["stats"]["ranked_count"] == 0
    assert result["stats"]["rejected_count"] == 1

    assert result["rejected"][0]["reason"] == (
        "rejected_not_in_article"
    )


def test_canonical_handoff_transfers_all_150_valid_candidates():
    phrases = [
        f"candidateword{i:04d}"
        for i in range(1, 151)
    ]

    article = ". ".join(
        f"{phrase} appears in this article"
        for phrase in phrases
    ) + "."

    incoming = [
        {
            "phrase": phrase,
            "workspace_id": WORKSPACE,
            "doc_id": DOCUMENT,
            "upstream_candidate_id": f"upstream-{i:04d}",
            "upstream_lineage": {
                "record": i,
                "stages": [
                    "smart_phrase_extractor",
                    "candidate_window_guard",
                ],
            },
        }
        for i, phrase in enumerate(phrases, 1)
    ]

    duplicate = deepcopy(incoming[0])
    duplicate["upstream_candidate_id"] = "duplicate"

    absent = {
        "phrase": "missingcandidateword9999",
        "workspace_id": WORKSPACE,
        "doc_id": DOCUMENT,
    }

    incoming.extend([duplicate, absent])
    original_input = deepcopy(incoming)

    result = run_selector(article, incoming)

    selected = result["selected"]
    canonical = result["all_selected_phrase_candidates"]

    assert result["ok"] is True
    assert len(selected) == 150
    assert len(canonical) == 150
    assert len(result["rejected"]) == 2

    assert result["stats"]["total_candidates"] == 152
    assert result["stats"]["ranked_count"] == 150
    assert result["stats"]["rejected_count"] == 2

    assert len(selected) + len(result["rejected"]) == 152
    assert incoming == original_input

    assert {x["phrase"] for x in canonical} == set(phrases)

    assert len({
        x["selection_phrase_id"]
        for x in canonical
    }) == 150

    assert len({
        x["selection_occurrence_id"]
        for x in canonical
    }) == 150

    assert {
        x["reason"] for x in result["rejected"]
    } == {
        "rejected_duplicate",
        "rejected_not_in_article",
    }

    ranking = [
        (
            x["selection_score"],
            1 if x["link_status"] == "linked" else 0,
            len(x["phrase_key"]),
        )
        for x in canonical
    ]

    assert ranking == sorted(ranking, reverse=True)

    assert [
        x["selection_occurrence_id"] for x in canonical
    ] == [
        x["selection_occurrence_id"] for x in selected
    ]


def test_canonical_handoff_preserves_provenance_and_spans():
    article = (
        "Blood Pressure supports clinical decisions. "
        "Heart Rate matters. "
        "Blood Pressure monitoring is useful."
    )

    specs = [
        ("Blood Pressure", True),
        ("Heart Rate", True),
        ("monitoring", False),
    ]

    incoming = []

    for index, (phrase, verified) in enumerate(specs, 1):
        start = article.index(phrase)

        incoming.append({
            "phrase": phrase,
            "workspace_id": WORKSPACE,
            "doc_id": DOCUMENT,
            "source_version": "test-source-v1",
            "candidate_id": f"upstream-candidate-{index}",
            "phrase_id": f"upstream-phrase-{index}",
            "occurrence_id": f"upstream-occurrence-{index}",
            "position_intelligence": {
                "original_article_span_verified": verified,
                "literal_span_verified": verified,
                "matched_occurrence": {
                    "start": start,
                    "end": start + len(phrase),
                },
            },
            "semantic_intelligence": {
                "fixture_only": True,
                "context": ["clinical", phrase],
                "relationships": {"confidence": 0.91},
            },
            "upstream_lineage": {
                "stages": [
                    "certified_semantic_output",
                    "smart_phrase_extractor",
                    "candidate_window_guard",
                ],
            },
            "source_authorization": {
                "fixture_only": True,
                "scope": ["read", "selection"],
            },
            "extractor_score": 87.0,
            "target_url": "https://example.invalid/upstream",
            "dis_signal_reasons": ["upstream_fixture"],
            "selection_score": 999.0,
        })

    original_input = deepcopy(incoming)
    result = run_selector(article, incoming)

    canonical = {
        x["phrase"]: x
        for x in result["all_selected_phrase_candidates"]
    }

    assert len(canonical) == 3
    assert incoming == original_input

    expected_hash = sha256(
        article.encode("utf-8")
    ).hexdigest()

    for original in original_input:
        phrase = original["phrase"]
        record = canonical[phrase]

        for field in (
            "source_version",
            "candidate_id",
            "phrase_id",
            "occurrence_id",
            "position_intelligence",
            "semantic_intelligence",
            "upstream_lineage",
            "source_authorization",
        ):
            assert record[field] == original[field]

        assert (
            record["selection_article_text_sha256"]
            == expected_hash
        )

        assert record["selection_article_text_hash_basis"] == (
            "article_text_utf8_sha256"
        )

        assert record["selection_source_version_status"] == (
            "provided_unverified"
        )

        assert record["selection_phrase_id"].startswith("sp_")
        assert record["selection_occurrence_id"].startswith("so_")

        assert record["selection_phrase_id"] != record["phrase_id"]
        assert record["selection_occurrence_id"] != record["occurrence_id"]

        inherited = record["selection_inherited_overwrites"]

        for field in (
            "extractor_score",
            "target_url",
            "dis_signal_reasons",
            "selection_score",
        ):
            assert inherited[field] == original[field]

    for phrase, verified in specs:
        record = canonical[phrase]

        if verified:
            assert record["selection_source_span_status"] == "verified"
            span = record["selection_source_span"]

            assert article[span["start"]:span["end"]] == phrase
            assert span["coordinate_space"] == "original_article"
        else:
            assert record["selection_source_span_status"] != "verified"
            assert record["selection_source_span"] is None


def test_canonical_handoff_snapshot_is_independent():
    incoming = [{
        "phrase": "Blood Pressure",
        "workspace_id": WORKSPACE,
        "doc_id": DOCUMENT,
        "upstream_lineage": {
            "stages": [
                "smart_phrase_extractor",
                "candidate_window_guard",
            ],
            "evidence": {"confidence": 0.91},
        },
    }]

    result = run_selector(
        "Blood Pressure matters.",
        incoming,
    )

    legacy = result["selected"]
    canonical = result["all_selected_phrase_candidates"]

    assert legacy is result["candidates"]
    assert canonical is not legacy
    assert canonical == legacy
    assert canonical[0] is not legacy[0]

    snapshot_before = deepcopy(canonical[0])

    legacy[0]["upstream_lineage"]["evidence"]["confidence"] = 0.01
    legacy[0]["phrase"] = "LEGACY_MUTATION"

    incoming[0]["upstream_lineage"]["stages"].append(
        "INPUT_MUTATION"
    )

    assert canonical[0] == snapshot_before


def test_canonical_handoff_is_deterministic():
    article = (
        "Blood Pressure matters. "
        "Heart Rate matters. "
        "Clinical Monitoring matters."
    )

    incoming = [
        {
            "phrase": phrase,
            "workspace_id": WORKSPACE,
            "doc_id": DOCUMENT,
            "upstream_candidate_id": f"source-{index}",
        }
        for index, phrase in enumerate(
            [
                "Blood Pressure",
                "Heart Rate",
                "Clinical Monitoring",
            ],
            1,
        )
    ]

    first = run_selector(article, deepcopy(incoming))
    second = run_selector(article, deepcopy(incoming))

    assert (
        first["all_selected_phrase_candidates"]
        == second["all_selected_phrase_candidates"]
    )

    assert (
        first["stats"]["ranked_count"]
        == second["stats"]["ranked_count"]
        == 3
    )
