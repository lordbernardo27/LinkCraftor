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

def test_low_information_contextual_wrappers_are_rejected():
    cases = [
        (
            "blood pressure in people",
            "Blood pressure in people can change throughout the day.",
        ),
        (
            "investment returns for people",
            "Investment returns for people depend on risk, fees, and time horizon.",
        ),
    ]

    for phrase, snippet in cases:
        candidate = _canonical_candidate(phrase)
        candidate["snippet"] = snippet

        result = score_phrase_strength(
            candidate,
            workspace_id="ws-wrapper-quality",
            document_id="doc-wrapper-quality",
            vertical="general",
        )

        assert result["keep"] is False, phrase
        assert result["reason"] == "low_information_contextual_wrapper", phrase
        assert result["phrase"] == phrase


def test_meaningful_relational_phrases_survive_wrapper_quality_gate():
    cases = [
        (
            "rate of return",
            "The rate of return measures investment performance.",
        ),
        (
            "cost of capital",
            "The cost of capital affects investment decisions.",
        ),
        (
            "security in cloud environments",
            "Security in cloud environments requires strong identity controls.",
        ),
        (
            "rights of employees",
            "The rights of employees are protected by employment law.",
        ),
        (
            "travel insurance for students",
            "Travel insurance for students may cover medical emergencies abroad.",
        ),
    ]

    for phrase, snippet in cases:
        candidate = _canonical_candidate(phrase)
        candidate["snippet"] = snippet

        result = score_phrase_strength(
            candidate,
            workspace_id="ws-wrapper-quality",
            document_id="doc-wrapper-quality",
            vertical="general",
        )

        assert result["keep"] is True, phrase
        assert result["phrase"] == phrase

def test_suffix_candidate_is_rejected_when_boundary_splits_known_semantic_unit():
    cases = [
        (
            "pressure management",
            "Lifestyle changes are part of blood pressure management.",
            "blood pressure management",
        ),
        (
            "flow management",
            "The company improved cash flow management this quarter.",
            "cash flow management",
        ),
        (
            "security controls",
            "The platform strengthened data security controls.",
            "data security controls",
        ),
        (
            "intent analysis",
            "The team uses search intent analysis for planning.",
            "search intent analysis",
        ),
        (
            "chain management",
            "The company upgraded supply chain management systems.",
            "supply chain management",
        ),
    ]

    for phrase, snippet, parent in cases:
        candidate = _canonical_candidate(phrase)
        candidate["snippet"] = snippet

        parent_candidate = _canonical_candidate(parent)
        parent_candidate["snippet"] = snippet

        result = score_phrase_strength(
            candidate,
            workspace_id="ws-truncated-compound",
            document_id="doc-truncated-compound",
            vertical="general",
            candidate_pool=[candidate, parent_candidate],
        )

        assert result["keep"] is False, phrase
        assert result["reason"] == "truncated_contained_candidate", phrase
        assert result["phrase"] == phrase


def test_suffix_candidate_survives_when_removed_prefix_is_only_optional_modifier():
    cases = [
        (
            "adverse effects",
            "Possible adverse effects should be discussed with patients.",
            "possible adverse effects",
        ),
        (
            "alcohol consumption",
            "Heavy alcohol consumption can increase health risks.",
            "heavy alcohol consumption",
        ),
        (
            "anti-inflammatory drugs",
            "Nonsteroidal anti-inflammatory drugs are widely used.",
            "nonsteroidal anti-inflammatory drugs",
        ),
        (
            "artery disease",
            "Coronary artery disease can cause serious complications.",
            "coronary artery disease",
        ),
        (
            "aerobic activity",
            "A combination of aerobic activity and resistance exercise is beneficial.",
            "combination of aerobic activity",
        ),
    ]

    for phrase, snippet, parent in cases:
        candidate = _canonical_candidate(phrase)
        candidate["snippet"] = snippet

        parent_candidate = _canonical_candidate(parent)
        parent_candidate["snippet"] = snippet

        result = score_phrase_strength(
            candidate,
            workspace_id="ws-truncated-compound",
            document_id="doc-truncated-compound",
            vertical="general",
            candidate_pool=[candidate, parent_candidate],
        )

        assert result["keep"] is True, phrase
        assert result["phrase"] == phrase


def _b4_candidate(phrase: str, snippet: str):
    candidate = _canonical_candidate(phrase)
    candidate["snippet"] = snippet
    return candidate


def test_b4_right_extension_is_reported_without_changing_phrase_validity():
    phrase = "customer behavior"
    snippet = "Customer behavior analysis helps companies understand purchasing decisions."

    candidate = _b4_candidate(phrase, snippet)
    parent = _b4_candidate("customer behavior analysis", snippet)

    baseline = score_phrase_strength(
        candidate,
        workspace_id="ws-b4",
        document_id="doc-b4",
        vertical="general",
    )

    result = score_phrase_strength(
        candidate,
        workspace_id="ws-b4",
        document_id="doc-b4",
        vertical="general",
        candidate_pool=[candidate, parent],
    )

    quality = result["scorer_intelligence"]["containment_quality"]

    assert result["phrase"] == phrase
    assert result["keep"] == baseline["keep"]
    assert result["strength_score"] == baseline["strength_score"]
    assert quality["advisory_only"] is True
    assert quality["can_reject"] is False
    assert quality["has_containing_sibling"] is True

    comparison = quality["comparisons"][0]

    assert comparison["parent_phrase"] == "customer behavior analysis"
    assert comparison["relation"] == "right_extension"
    assert comparison["left_added"] == 0
    assert comparison["right_added"] == 1
    assert comparison["parent_in_current_snippet"] is True


def test_b4_left_extension_is_reported_without_suppressing_valid_child():
    phrase = "adverse effects"
    snippet = "Possible adverse effects should be discussed with patients."

    candidate = _b4_candidate(phrase, snippet)
    parent = _b4_candidate("possible adverse effects", snippet)

    result = score_phrase_strength(
        candidate,
        workspace_id="ws-b4",
        document_id="doc-b4",
        vertical="general",
        candidate_pool=[candidate, parent],
    )

    quality = result["scorer_intelligence"]["containment_quality"]

    assert result["phrase"] == phrase
    assert result["keep"] is True
    assert quality["advisory_only"] is True
    assert quality["can_reject"] is False
    assert quality["has_containing_sibling"] is True

    comparison = quality["comparisons"][0]

    assert comparison["parent_phrase"] == "possible adverse effects"
    assert comparison["relation"] == "left_extension"
    assert comparison["left_added"] == 1
    assert comparison["right_added"] == 0
    assert comparison["parent_in_current_snippet"] is True


def test_b4_both_sides_containment_is_reported_factually():
    phrase = "blood pressure"
    snippet = "Routine blood pressure measurement improves monitoring."

    candidate = _b4_candidate(phrase, snippet)
    parent = _b4_candidate("routine blood pressure measurement", snippet)

    result = score_phrase_strength(
        candidate,
        workspace_id="ws-b4",
        document_id="doc-b4",
        vertical="general",
        candidate_pool=[candidate, parent],
    )

    quality = result["scorer_intelligence"]["containment_quality"]
    comparison = quality["comparisons"][0]

    assert result["phrase"] == phrase
    assert result["keep"] is True
    assert quality["advisory_only"] is True
    assert quality["can_reject"] is False
    assert comparison["relation"] == "both_sides"
    assert comparison["left_added"] == 1
    assert comparison["right_added"] == 1
    assert comparison["parent_in_current_snippet"] is True


def test_b4_no_containing_sibling_produces_empty_advisory():
    phrase = "rental market"
    snippet = "The rental market remains competitive in major cities."

    candidate = _b4_candidate(phrase, snippet)

    result = score_phrase_strength(
        candidate,
        workspace_id="ws-b4",
        document_id="doc-b4",
        vertical="general",
        candidate_pool=[candidate],
    )

    quality = result["scorer_intelligence"]["containment_quality"]

    assert result["phrase"] == phrase
    assert result["keep"] is True
    assert quality["advisory_only"] is True
    assert quality["can_reject"] is False
    assert quality["has_containing_sibling"] is False
    assert quality["comparisons"] == []


def test_b4_parent_not_present_in_current_snippet_is_not_a_live_comparison():
    phrase = "student progress"
    snippet = "Student progress improves with regular feedback."

    candidate = _b4_candidate(phrase, snippet)
    parent = _b4_candidate(
        "student progress tracking",
        "Student progress tracking helps teachers identify learning gaps.",
    )

    result = score_phrase_strength(
        candidate,
        workspace_id="ws-b4",
        document_id="doc-b4",
        vertical="general",
        candidate_pool=[candidate, parent],
    )

    quality = result["scorer_intelligence"]["containment_quality"]

    assert result["phrase"] == phrase
    assert result["keep"] is True
    assert quality["has_containing_sibling"] is False
    assert quality["comparisons"] == []


def test_b4_rejected_parent_is_not_used_as_containment_quality_evidence():
    phrase = "blood pressure"
    snippet = "Blood pressure in people can change throughout the day."

    candidate = _b4_candidate(phrase, snippet)
    rejected_parent = _b4_candidate("blood pressure in people", snippet)

    result = score_phrase_strength(
        candidate,
        workspace_id="ws-b4",
        document_id="doc-b4",
        vertical="general",
        candidate_pool=[candidate, rejected_parent],
    )

    quality = result["scorer_intelligence"]["containment_quality"]

    assert result["phrase"] == phrase
    assert result["keep"] is True
    assert quality["has_containing_sibling"] is False
    assert quality["comparisons"] == []


def test_b4_records_existing_child_and_parent_quality_signals_factually():
    phrase = "blood pressure"
    snippet = "Blood pressure monitoring helps identify persistent hypertension."

    candidate = _b4_candidate(phrase, snippet)
    parent = _b4_candidate("blood pressure monitoring", snippet)

    result = score_phrase_strength(
        candidate,
        workspace_id="ws-b4",
        document_id="doc-b4",
        vertical="general",
        candidate_pool=[candidate, parent],
    )

    quality = result["scorer_intelligence"]["containment_quality"]
    child = quality["child_independence"]

    assert child["exact_canonical_anchor"] is True
    assert child["valid_ordered_pair"] is True
    assert child["natural_compound"] is True
    assert child["has_structural_signal"] is True
    assert "structural_canonical_anchor" in child["structural_signals"]
    assert "structural_valid_ordered_pair" in child["structural_signals"]
    assert "structural_natural_compound" in child["structural_signals"]

    comparison = quality["comparisons"][0]
    parent_quality = comparison["parent_quality"]

    assert parent_quality["valid_ordered_pair"] is True
    assert parent_quality["natural_compound"] is True
    assert parent_quality["has_structural_signal"] is True
    assert isinstance(parent_quality["structural_signals"], list)


def test_b4_absence_of_known_quality_signals_is_evidence_not_rejection():
    phrase = "customer behavior"
    snippet = "Customer behavior analysis helps companies understand purchasing decisions."

    candidate = _b4_candidate(phrase, snippet)
    parent = _b4_candidate("customer behavior analysis", snippet)

    baseline = score_phrase_strength(
        candidate,
        workspace_id="ws-b4",
        document_id="doc-b4",
        vertical="general",
    )

    result = score_phrase_strength(
        candidate,
        workspace_id="ws-b4",
        document_id="doc-b4",
        vertical="general",
        candidate_pool=[candidate, parent],
    )

    quality = result["scorer_intelligence"]["containment_quality"]
    child = quality["child_independence"]

    assert result["phrase"] == phrase
    assert result["keep"] == baseline["keep"]
    assert result["strength_score"] == baseline["strength_score"]

    assert child["exact_canonical_anchor"] is False
    assert child["valid_ordered_pair"] is False
    assert child["natural_compound"] is False
    assert child["has_structural_signal"] is False
    assert child["structural_signals"] == []

    assert quality["has_containing_sibling"] is True
    assert "parent_quality" in quality["comparisons"][0]


def test_b5_ambiguous_right_extension_does_not_create_hard_rejection():
    cases = [
        (
            "calcium channel",
            "Calcium channel blockers are commonly used medicines.",
            "calcium channel blockers",
        ),
        (
            "customer behavior",
            "Customer behavior analysis helps companies understand purchasing decisions.",
            "customer behavior analysis",
        ),
        (
            "cash reserve",
            "Cash reserve requirements can affect bank liquidity.",
            "cash reserve requirements",
        ),
        (
            "student progress",
            "Student progress tracking helps teachers identify learning gaps.",
            "student progress tracking",
        ),
        (
            "rental market",
            "Rental market trends vary across major cities.",
            "rental market trends",
        ),
    ]

    for phrase, snippet, parent in cases:
        candidate = _b4_candidate(phrase, snippet)
        parent_candidate = _b4_candidate(parent, snippet)

        result = score_phrase_strength(
            candidate,
            workspace_id="ws-b5",
            document_id="doc-b5",
            vertical="general",
            candidate_pool=[candidate, parent_candidate],
        )

        assert result["phrase"] == phrase
        assert result["keep"] is True, phrase

        quality = result["scorer_intelligence"]["containment_quality"]

        assert quality["advisory_only"] is True
        assert quality["can_reject"] is False
        assert quality["has_containing_sibling"] is True
