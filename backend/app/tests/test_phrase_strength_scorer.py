from backend.server.stores.phrase_strength_scorer import score_phrase_strength


def _canonical_candidate(phrase: str = "Blood Pressure"):
    return {
        "phrase": phrase,
        "source_type": "phrase_discovery",
        "section_id": "section-1",
        "doc_id": "doc-1",
        "snippet": f"{phrase} affects health",
        "provenance": [
            "smart_phrase_extractor",
            "phrase_discovery",
        ],
        "position_intelligence": {
            "literal_span_verified": True,
            "first_position": 0,
            "all_positions": [0],
            "occurrence_count": 1,
            "matched_occurrence": {
                "start": 0,
                "end": len(phrase),
            },
        },
        "merger_intelligence": {
            "merger_version": "phrase_merger/1.0",
            "origins": [
                "smart_phrase_extractor",
                "phrase_discovery",
            ],
            "merged_cross_source": True,
        },
        "extractor_intelligence": {
            "test_marker": "EXTRACTOR_PRESERVE",
        },
        "discovery_intelligence": {
            "test_marker": "DISCOVERY_PRESERVE",
        },
        "quality_gate": {
            "decision": "ACCEPT",
        },
        "guard_intelligence": {
            "stage": "candidate_window_guard",
            "literal_phrase_preserved": True,
        },
    }


def test_legacy_string_contract_still_works():
    result = score_phrase_strength(
        "blood pressure",
        source_type="phrase_discovery",
        document_id="doc-1",
    )

    assert isinstance(result, dict)
    assert result["phrase"] == "blood pressure"
    assert result["keep"] is True
    assert isinstance(result["score"], float)
    assert "reason" in result


def test_canonical_accept_preserves_complete_envelope():
    candidate = _canonical_candidate()

    result = score_phrase_strength(
        candidate,
        workspace_id="ws-test",
        document_id="doc-1",
        vertical="general",
    )

    assert result["keep"] is True
    assert result["phrase"] == candidate["phrase"]
    assert result["provenance"] == candidate["provenance"]
    assert result["position_intelligence"] == candidate["position_intelligence"]
    assert result["merger_intelligence"] == candidate["merger_intelligence"]
    assert result["extractor_intelligence"] == candidate["extractor_intelligence"]
    assert result["discovery_intelligence"] == candidate["discovery_intelligence"]
    assert result["quality_gate"] == candidate["quality_gate"]
    assert result["guard_intelligence"] == candidate["guard_intelligence"]
    assert result["strength"]["keep"] is True
    assert result["strength_score"] == result["strength"]["score"]


def test_canonical_rejection_preserves_complete_envelope():
    candidate = _canonical_candidate("the")

    result = score_phrase_strength(
        candidate,
        workspace_id="ws-test",
        document_id="doc-1",
        vertical="general",
    )

    assert result["keep"] is False
    assert result["phrase"] == "the"
    assert result["position_intelligence"] == candidate["position_intelligence"]
    assert result["merger_intelligence"] == candidate["merger_intelligence"]
    assert result["guard_intelligence"] == candidate["guard_intelligence"]
    assert result["strength"]["keep"] is False
    assert result["reason"] == result["strength"]["reason"]


def test_canonical_phrase_is_not_trimmed_or_rewritten():
    phrase = "Blood Pressure Management Strategy"
    candidate = _canonical_candidate(phrase)

    result = score_phrase_strength(
        candidate,
        workspace_id="ws-test",
        vertical="general",
    )

    assert result["phrase"] == phrase
    assert result["scorer_intelligence"]["literal_phrase_preserved"] is True
    assert result["scorer_intelligence"]["allow_trim"] is False


def test_scorer_intelligence_describes_canonical_contract():
    candidate = _canonical_candidate()

    result = score_phrase_strength(
        candidate,
        workspace_id="ws-test",
        vertical="general",
    )

    intelligence = result["scorer_intelligence"]

    assert intelligence["stage"] == "phrase_strength_scorer"
    assert intelligence["input_contract"] == "canonical_candidate_envelope"
    assert intelligence["literal_phrase_preserved"] is True
    assert intelligence["normalized_working_phrase"] == "blood pressure"
    assert intelligence["source_type"] == "phrase_discovery"
    assert intelligence["document_id"] == "doc-1"
    assert intelligence["keep"] == result["keep"]
    assert intelligence["score"] == result["strength_score"]
    assert intelligence["allow_trim"] is False
