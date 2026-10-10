from backend.server.stores.highlight_selection_engine import (
    select_highlight_candidates,
)


def _candidate(
    phrase="Blood Pressure",
    strength_score=0.91,
    extractor_score=0.20,
    first_position=99,
):
    return {
        "phrase": phrase,
        "source_type": "phrase_discovery",
        "doc_id": "doc-1",
        "strength_score": strength_score,
        "extractor_intelligence": {
            "score": extractor_score,
        },
        "position_intelligence": {
            "coordinate_space": "literal_article",
            "first_position": first_position,
            "all_positions": [first_position],
            "occurrence_count": 1,
        },
        "guard_intelligence": {
            "stage": "candidate_window_guard",
        },
        "scorer_intelligence": {
            "stage": "phrase_strength_scorer",
        },
    }


def test_strength_score_has_priority_over_extractor_score():
    candidate = _candidate(
        strength_score=0.91,
        extractor_score=0.20,
    )

    result = select_highlight_candidates(
        workspace_id="ws-test",
        doc_id="doc-1",
        article_text="Blood Pressure matters.",
        phrase_candidates=[candidate],
        resolved_targets=None,
        vertical="general",
    )

    selected = result["selected"][0]

    assert selected["extractor_score"] == 91.0


def test_canonical_envelope_is_preserved():
    candidate = _candidate()

    result = select_highlight_candidates(
        workspace_id="ws-test",
        doc_id="doc-1",
        article_text="Blood Pressure matters.",
        phrase_candidates=[candidate],
        resolved_targets=None,
        vertical="general",
    )

    selected = result["selected"][0]

    assert selected["phrase"] == candidate["phrase"]
    assert selected["position_intelligence"] == candidate["position_intelligence"]
    assert selected["guard_intelligence"] == candidate["guard_intelligence"]
    assert selected["scorer_intelligence"] == candidate["scorer_intelligence"]


def test_selection_position_intelligence_uses_normalized_article_space():
    candidate = _candidate()

    result = select_highlight_candidates(
        workspace_id="ws-test",
        doc_id="doc-1",
        article_text="Blood Pressure matters. Blood Pressure should be monitored.",
        phrase_candidates=[candidate],
        resolved_targets=None,
        vertical="general",
    )

    selected = result["selected"][0]
    spi = selected["selection_position_intelligence"]

    assert spi["coordinate_space"] == "normalized_article"
    assert spi["normalization"] == "lowercase_whitespace_collapsed"
    assert spi["first_position"] == 0
    assert spi["all_positions"] == [0, 24]
    assert spi["occurrence_count"] == 2
    assert spi["canonical_position_intelligence_preserved"] is True

    assert selected["first_position"] == spi["first_position"]
    assert selected["all_positions"] == spi["all_positions"]
    assert selected["occurrence_count"] == spi["occurrence_count"]


def test_exact_duplicate_is_rejected_factually():
    first = _candidate(strength_score=0.80, extractor_score=0.20)
    second = _candidate(strength_score=0.95, extractor_score=0.90)

    result = select_highlight_candidates(
        workspace_id="ws-test",
        doc_id="doc-1",
        article_text="Blood Pressure matters.",
        phrase_candidates=[first, second],
        resolved_targets=None,
        vertical="general",
    )

    assert len(result["selected"]) == 1
    assert len(result["rejected"]) == 1
    assert result["rejected"][0]["reason"] == "rejected_duplicate"
    assert result["selected"][0]["strength_score"] == 0.95


def test_phrase_not_in_article_is_rejected_factually():
    candidate = _candidate(phrase="Blood Pressure")

    result = select_highlight_candidates(
        workspace_id="ws-test",
        doc_id="doc-1",
        article_text="Heart rate matters.",
        phrase_candidates=[candidate],
        resolved_targets=None,
        vertical="general",
    )

    assert result["selected"] == []
    assert len(result["rejected"]) == 1
    assert result["rejected"][0]["reason"] == "rejected_not_in_article"
