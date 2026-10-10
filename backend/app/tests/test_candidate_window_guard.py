from backend.server.stores.candidate_window_guard import candidate_window_guard


def _canonical_candidate(phrase: str = "blood pressure"):
    return {
        "phrase": phrase,
        "source_type": "phrase_discovery",
        "section_id": "section-1",
        "doc_id": "doc-1",
        "snippet": f"{phrase} affects health",
        "provenance": ["smart_phrase_extractor", "phrase_discovery"],
        "position_intelligence": {
            "literal_span_verified": True,
            "first_position": 0,
            "all_positions": [0],
            "occurrence_count": 1,
            "matched_occurrence": {
                "start": 0,
                "end": len(phrase),
                "sentence_index": 0,
                "section_index": 0,
                "section_id": "section-1",
            },
        },
        "merger_intelligence": {
            "merger_version": "phrase_merger/1.0",
            "origins": ["smart_phrase_extractor", "phrase_discovery"],
            "merged_cross_source": True,
            "overlap_type": "exact_phrase_exact_occurrence",
        },
        "extractor_intelligence": {
            "test_marker": "EXTRACTOR_PRESERVE",
        },
        "discovery_intelligence": {
            "test_marker": "DISCOVERY_PRESERVE",
        },
    }


def test_legacy_string_contract_still_works():
    result = candidate_window_guard(
        "blood pressure",
        source_type="smart_phrase_extractor",
        document_id="doc-1",
    )

    assert result["keep"] is True
    assert result["phrase"] == "blood pressure"
    assert isinstance(result["quality_gate"], dict)


def test_canonical_accept_preserves_complete_envelope():
    candidate = _canonical_candidate()
    result = candidate_window_guard(
        candidate,
        workspace_id="ws-test",
        document_id="doc-1",
        vertical="general",
    )

    assert result["keep"] is True
    assert result["phrase"] == candidate["phrase"]
    assert result["source_type"] == candidate["source_type"]
    assert result["section_id"] == candidate["section_id"]
    assert result["doc_id"] == candidate["doc_id"]
    assert result["snippet"] == candidate["snippet"]
    assert result["provenance"] == candidate["provenance"]
    assert result["position_intelligence"] == candidate["position_intelligence"]
    assert result["merger_intelligence"] == candidate["merger_intelligence"]
    assert result["extractor_intelligence"] == candidate["extractor_intelligence"]
    assert result["discovery_intelligence"] == candidate["discovery_intelligence"]


def test_canonical_rejection_preserves_envelope():
    candidate = _canonical_candidate("reduce churn")
    result = candidate_window_guard(
        candidate,
        workspace_id="ws-test",
        document_id="doc-1",
        vertical="general",
    )

    assert result["keep"] is False
    assert result["phrase"] == "reduce churn"
    assert result["provenance"] == candidate["provenance"]
    assert result["position_intelligence"] == candidate["position_intelligence"]
    assert result["merger_intelligence"] == candidate["merger_intelligence"]
    assert result["discovery_intelligence"] == candidate["discovery_intelligence"]
    assert isinstance(result["quality_gate"], dict)
    assert result["quality_gate"]["decision"] == "REJECT"


def test_canonical_phrase_is_not_boundary_rewritten():
    candidate = _canonical_candidate("the blood pressure")
    result = candidate_window_guard(
        candidate,
        workspace_id="ws-test",
        document_id="doc-1",
        vertical="general",
    )

    assert result["keep"] is False
    assert result["reason"] == "bad_boundary"
    assert result["phrase"] == "the blood pressure"
    assert result["position_intelligence"] == candidate["position_intelligence"]


def test_guard_intelligence_describes_canonical_contract():
    candidate = _canonical_candidate()
    result = candidate_window_guard(candidate, document_id="doc-1")

    guard = result["guard_intelligence"]

    assert guard["stage"] == "candidate_window_guard"
    assert guard["input_contract"] == "canonical_phrase_merger_candidate"
    assert guard["literal_phrase_preserved"] is True
    assert guard["source_type"] == candidate["source_type"]
    assert guard["document_id"] == candidate["doc_id"]
    assert guard["decision"] == result["quality_gate"]["decision"]
    assert guard["keep"] == result["keep"]
    assert guard["reason"] == result["reason"]
