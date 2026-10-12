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

def test_universal_leading_action_verbs_are_rejected_under_pos_fallback():
    cases = [
        "review investment returns",
        "review contractual obligations",
        "monitor server performance",
        "review blood pressure trends",
        "analyze customer behavior",
    ]

    for phrase in cases:
        result = candidate_window_guard(
            phrase,
            source_type="phrase_discovery",
            document_id="doc-universal-action-leak",
            vertical="general",
        )

        assert result["keep"] is False, phrase
        assert result["reason"] == "action_leak_start", phrase


def test_ambiguous_action_words_remain_valid_when_used_as_nouns():
    cases = [
        "annual performance review",
        "computer monitor stand",
        "product review system",
        "monitor stand",
    ]

    for phrase in cases:
        result = candidate_window_guard(
            phrase,
            source_type="phrase_discovery",
            document_id="doc-universal-noun-use",
            vertical="general",
        )

        assert result["keep"] is True, phrase

def test_universal_trailing_finite_verb_is_rejected_from_source_context():
    cases = [
        (
            "investment strategy aims",
            "The investment strategy aims to increase long-term returns."
        ),
        (
            "marketing strategy aims",
            "The marketing strategy aims to improve brand awareness."
        ),
        (
            "security policy aims",
            "The security policy aims to reduce unauthorized access."
        ),
        (
            "effective hypertension management aims",
            "Effective hypertension management aims to reduce long-term risk."
        ),
    ]

    for phrase, snippet in cases:
        candidate = _canonical_candidate(phrase)
        candidate["snippet"] = snippet

        result = candidate_window_guard(
            candidate,
            workspace_id="ws-universal-trailing-verb",
            document_id="doc-universal-trailing-verb",
            vertical="general",
        )

        assert result["keep"] is False, phrase
        assert result["reason"] == "action_leak_end", phrase


def test_ambiguous_trailing_word_remains_valid_when_used_as_noun():
    cases = [
        (
            "project aims",
            "The project aims and objectives were approved by the board."
        ),
        (
            "research aims",
            "The research aims and methodology are described below."
        ),
    ]

    for phrase, snippet in cases:
        candidate = _canonical_candidate(phrase)
        candidate["snippet"] = snippet

        result = candidate_window_guard(
            candidate,
            workspace_id="ws-universal-trailing-noun",
            document_id="doc-universal-trailing-noun",
            vertical="general",
        )

        assert result["keep"] is True, phrase
