from backend.server.stores.highlight_selection_engine import (
    candidate_matches_rc2_pattern,
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

def _dis_pattern(
    *,
    stage="phrase_discovery_engine",
    word_count=2,
    structure_type="two_term_candidate",
    historical_risk=1.0,
    historical_confidence=1.0,
    component="semantic_discovery",
    capability="semantic_span_search",
    pattern_id="pattern-1",
):
    evidence = {}
    if component:
        evidence["discovery_component"] = component
    if capability:
        evidence["discovery_capability"] = capability

    return {
        "pattern_id": pattern_id,
        "historical_risk": historical_risk,
        "historical_confidence": historical_confidence,
        "failure_reasons": ["discovery_nonliteral"],
        "latest_event": {
            "pipeline_stage": stage,
            "evidence": evidence,
            "pattern_signature": {
                "source_stage": stage,
                "word_count_band": word_count,
                "structure_type": structure_type,
                "failure_category": "general_rejection_pattern",
                "failure_reason": "discovery_nonliteral",
            },
        },
    }


def _discovery_candidate():
    candidate = _candidate(
        phrase="Cloud Infrastructure",
        strength_score=0.90,
        extractor_score=0.20,
    )
    candidate["discovery_intelligence"] = {
        "component": "semantic_discovery",
        "capability": "semantic_span_search",
        "capabilities": ["semantic_span_search"],
    }
    return candidate


def test_dis_structure_mismatch_does_not_match():
    candidate = _discovery_candidate()
    pattern = _dis_pattern(
        word_count=3,
        structure_type="multi_term_candidate",
    )

    result = candidate_matches_rc2_pattern(
        "cloud infrastructure",
        candidate,
        [pattern],
    )

    assert result["matched"] is False
    assert result["effective_risk"] == 0.0


def test_dis_discovery_provenance_mismatch_does_not_match():
    candidate = _discovery_candidate()
    pattern = _dis_pattern(component="different_component")

    result = candidate_matches_rc2_pattern(
        "cloud infrastructure",
        candidate,
        [pattern],
    )

    assert result["matched"] is False
    assert result["effective_risk"] == 0.0


def test_dis_matcher_selects_highest_effective_risk():
    candidate = _discovery_candidate()

    weak = _dis_pattern(
        historical_risk=0.40,
        pattern_id="weak-pattern",
    )
    strong = _dis_pattern(
        historical_risk=0.90,
        pattern_id="strong-pattern",
    )

    result = candidate_matches_rc2_pattern(
        "cloud infrastructure",
        candidate,
        [weak, strong],
    )

    assert result["matched"] is True
    assert result["pattern_id"] == "strong-pattern"
    assert result["match_confidence"] == 0.70
    assert result["effective_risk"] == 0.63


def test_dis_penalty_changes_ranking_only(monkeypatch):
    import backend.server.stores.highlight_selection_engine as engine

    candidate = _discovery_candidate()

    monkeypatch.setattr(
        engine,
        "get_rejection_pattern_knowledge",
        lambda *_a, **_k: {"patterns": []},
    )
    baseline = select_highlight_candidates(
        workspace_id="ws-test",
        doc_id="doc-1",
        article_text="Cloud Infrastructure supports modern systems.",
        phrase_candidates=[candidate],
        resolved_targets=None,
        vertical="general",
    )

    monkeypatch.setattr(
        engine,
        "get_rejection_pattern_knowledge",
        lambda *_a, **_k: {
            "patterns": [
                _dis_pattern(
                    historical_risk=1.0,
                    historical_confidence=1.0,
                )
            ]
        },
    )
    with_history = select_highlight_candidates(
        workspace_id="ws-test",
        doc_id="doc-1",
        article_text="Cloud Infrastructure supports modern systems.",
        phrase_candidates=[candidate],
        resolved_targets=None,
        vertical="general",
    )

    baseline_candidate = baseline["selected"][0]
    ranked_candidate = with_history["selected"][0]

    assert baseline_candidate["dis_penalty"] == 0.0
    assert baseline_candidate["base_selection_score"] == ranked_candidate["base_selection_score"]

    assert ranked_candidate["dis_pattern_match"] is True
    assert ranked_candidate["dis_penalty"] == 5.6
    assert ranked_candidate["selection_score"] < ranked_candidate["base_selection_score"]

    assert len(with_history["selected"]) == 1
    assert with_history["rejected"] == []
    assert ranked_candidate["selection_status"] == "ranked_candidate"

    assert ranked_candidate["dis_advisory_only"] is True
    assert ranked_candidate["dis_can_block"] is False
    assert 0.0 <= ranked_candidate["dis_penalty"] <= 8.0


def test_verified_duplicate_occurrence_has_specific_reason():
    first = _candidate(
        strength_score=0.80,
        extractor_score=0.20,
    )
    second = _candidate(
        strength_score=0.95,
        extractor_score=0.90,
    )

    for item in (first, second):
        item["position_intelligence"] = {
            "source_coordinate_space": "original_article",
            "original_article_span_verified": True,
            "literal_span_verified": True,
            "matched_occurrence": {
                "start": 0,
                "end": 14,
            },
        }

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
    assert (
        result["rejected"][0]["reason"]
        == "rejected_duplicate_occurrence"
    )
    assert result["selected"][0]["strength_score"] == 0.95


def _verified_quality_candidate(
    phrase,
    start,
    end,
    *,
    strength_score=0.90,
    parent_phrase=None,
    relation=None,
    right_added=0,
    child_structural=False,
):
    candidate = _candidate(
        phrase=phrase,
        strength_score=strength_score,
    )

    candidate["position_intelligence"] = {
        "source_coordinate_space": "original_article",
        "original_article_span_verified": True,
        "literal_span_verified": True,
        "matched_occurrence": {
            "start": start,
            "end": end,
        },
    }

    comparisons = []

    if parent_phrase is not None:
        comparisons.append({
            "parent_phrase": parent_phrase,
            "relation": relation,
            "left_added": 0,
            "right_added": right_added,
            "parent_in_current_snippet": True,
            "parent_quality": {
                "exact_canonical_anchor": False,
                "valid_ordered_pair": False,
                "natural_compound": False,
                "has_structural_signal": False,
                "structural_signals": [],
            },
        })

    candidate["scorer_intelligence"]["containment_quality"] = {
        "comparison_version": "containment_quality/1.0",
        "advisory_only": True,
        "can_reject": False,
        "has_containing_sibling": bool(comparisons),
        "child_independence": {
            "exact_canonical_anchor": False,
            "valid_ordered_pair": False,
            "natural_compound": False,
            "has_structural_signal": child_structural,
            "structural_signals": (
                ["structural_test_signal"]
                if child_structural
                else []
            ),
        },
        "comparisons": comparisons,
    }

    return candidate


def test_quality_dominance_is_occurrence_specific_and_ranking_only(monkeypatch):
    import backend.server.stores.highlight_selection_engine as engine

    monkeypatch.setattr(
        engine,
        "get_rejection_pattern_knowledge",
        lambda *_a, **_k: {"patterns": []},
    )

    article = "Calcium channel blockers are commonly used."

    child = _verified_quality_candidate(
        "Calcium channel",
        0,
        15,
        strength_score=0.90,
        parent_phrase="Calcium channel blockers",
        relation="right_extension",
        right_added=1,
        child_structural=False,
    )

    parent = _verified_quality_candidate(
        "Calcium channel blockers",
        0,
        24,
        strength_score=0.90,
    )

    result = select_highlight_candidates(
        workspace_id="ws-test",
        doc_id="doc-1",
        article_text=article,
        phrase_candidates=[child, parent],
        resolved_targets=None,
        vertical="general",
    )

    assert len(result["selected"]) == 2
    assert result["rejected"] == []

    by_phrase = {
        item["phrase"].lower(): item
        for item in result["selected"]
    }

    child_result = by_phrase["calcium channel"]
    parent_result = by_phrase["calcium channel blockers"]

    assert child_result["quality_dominance_applied"] is True
    assert child_result["quality_dominance_can_block"] is False
    assert child_result["quality_dominance_penalty"] > 0.0
    assert child_result["strength_score"] == 0.90

    assert parent_result["quality_dominance_applied"] is False
    assert parent_result["quality_dominance_penalty"] == 0.0

    assert (
        parent_result["selection_score"]
        > child_result["selection_score"]
    )


def test_quality_dominance_does_not_penalize_independent_child_occurrence(monkeypatch):
    import backend.server.stores.highlight_selection_engine as engine

    monkeypatch.setattr(
        engine,
        "get_rejection_pattern_knowledge",
        lambda *_a, **_k: {"patterns": []},
    )

    article = (
        "Calcium channel activity was measured. "
        "Calcium channel blockers were then administered."
    )

    child = _verified_quality_candidate(
        "Calcium channel",
        0,
        15,
        strength_score=0.90,
        parent_phrase="Calcium channel blockers",
        relation="right_extension",
        right_added=1,
        child_structural=False,
    )

    parent_start = article.index("Calcium channel blockers")
    parent = _verified_quality_candidate(
        "Calcium channel blockers",
        parent_start,
        parent_start + len("Calcium channel blockers"),
        strength_score=0.90,
    )

    result = select_highlight_candidates(
        workspace_id="ws-test",
        doc_id="doc-1",
        article_text=article,
        phrase_candidates=[child, parent],
        resolved_targets=None,
        vertical="general",
    )

    child_result = next(
        item for item in result["selected"]
        if item["phrase"].lower() == "calcium channel"
    )

    assert child_result["quality_dominance_applied"] is False
    assert child_result["quality_dominance_penalty"] == 0.0


def test_quality_dominance_does_not_penalize_structurally_independent_child(monkeypatch):
    import backend.server.stores.highlight_selection_engine as engine

    monkeypatch.setattr(
        engine,
        "get_rejection_pattern_knowledge",
        lambda *_a, **_k: {"patterns": []},
    )

    article = "Blood pressure management requires regular monitoring."

    child = _verified_quality_candidate(
        "Blood pressure",
        0,
        14,
        strength_score=0.90,
        parent_phrase="Blood pressure management",
        relation="right_extension",
        right_added=1,
        child_structural=True,
    )

    parent = _verified_quality_candidate(
        "Blood pressure management",
        0,
        25,
        strength_score=0.90,
    )

    result = select_highlight_candidates(
        workspace_id="ws-test",
        doc_id="doc-1",
        article_text=article,
        phrase_candidates=[child, parent],
        resolved_targets=None,
        vertical="general",
    )

    child_result = next(
        item for item in result["selected"]
        if item["phrase"].lower() == "blood pressure"
    )

    assert child_result["quality_dominance_applied"] is False
    assert child_result["quality_dominance_penalty"] == 0.0


def test_quality_dominance_does_not_apply_to_left_extension(monkeypatch):
    import backend.server.stores.highlight_selection_engine as engine

    monkeypatch.setattr(
        engine,
        "get_rejection_pattern_knowledge",
        lambda *_a, **_k: {"patterns": []},
    )

    article = "Possible adverse effects should be discussed."

    child_start = article.index("adverse effects")

    child = _verified_quality_candidate(
        "adverse effects",
        child_start,
        child_start + len("adverse effects"),
        strength_score=0.90,
        parent_phrase="Possible adverse effects",
        relation="left_extension",
        right_added=0,
        child_structural=False,
    )

    parent = _verified_quality_candidate(
        "Possible adverse effects",
        0,
        len("Possible adverse effects"),
        strength_score=0.90,
    )

    result = select_highlight_candidates(
        workspace_id="ws-test",
        doc_id="doc-1",
        article_text=article,
        phrase_candidates=[child, parent],
        resolved_targets=None,
        vertical="general",
    )

    child_result = next(
        item for item in result["selected"]
        if item["phrase"].lower() == "adverse effects"
    )

    assert child_result["quality_dominance_applied"] is False
    assert child_result["quality_dominance_penalty"] == 0.0


def test_quality_dominance_cross_niche_independent_occurrences_are_protected(monkeypatch):
    import backend.server.stores.highlight_selection_engine as engine

    monkeypatch.setattr(
        engine,
        "get_rejection_pattern_knowledge",
        lambda *_a, **_k: {"patterns": []},
    )

    cases = [
        (
            "Customer behavior affects purchasing decisions. "
            "Customer behavior analysis supports market research.",
            "Customer behavior",
            "Customer behavior analysis",
        ),
        (
            "A cash reserve improves resilience. "
            "Cash reserve requirements differ by institution.",
            "cash reserve",
            "Cash reserve requirements",
        ),
        (
            "Student progress matters to teachers. "
            "Student progress tracking can reveal learning gaps.",
            "Student progress",
            "Student progress tracking",
        ),
        (
            "The rental market remains competitive. "
            "Rental market trends vary across cities.",
            "rental market",
            "Rental market trends",
        ),
    ]

    for article, child_phrase, parent_phrase in cases:
        child_start = article.lower().index(child_phrase.lower())
        parent_start = article.lower().index(
            parent_phrase.lower(),
            child_start + len(child_phrase),
        )

        child = _verified_quality_candidate(
            child_phrase,
            child_start,
            child_start + len(child_phrase),
            strength_score=0.90,
            parent_phrase=parent_phrase,
            relation="right_extension",
            right_added=1,
            child_structural=False,
        )

        parent = _verified_quality_candidate(
            parent_phrase,
            parent_start,
            parent_start + len(parent_phrase),
            strength_score=0.90,
        )

        result = select_highlight_candidates(
            workspace_id="ws-test",
            doc_id="doc-1",
            article_text=article,
            phrase_candidates=[child, parent],
            resolved_targets=None,
            vertical="general",
        )

        selected_child = next(
            item
            for item in result["selected"]
            if item["phrase"].casefold() == child_phrase.casefold()
        )

        assert selected_child["quality_dominance_applied"] is False
        assert selected_child["quality_dominance_penalty"] == 0.0
        assert selected_child["quality_dominance_can_block"] is False
        assert selected_child["strength_score"] == 0.90


def test_quality_dominance_preserves_valid_left_extended_shorter_concept(monkeypatch):
    import backend.server.stores.highlight_selection_engine as engine

    monkeypatch.setattr(
        engine,
        "get_rejection_pattern_knowledge",
        lambda *_a, **_k: {"patterns": []},
    )

    article = "High blood pressure requires careful management."
    child_phrase = "blood pressure"
    parent_phrase = "High blood pressure"

    child_start = article.index(child_phrase)

    child = _verified_quality_candidate(
        child_phrase,
        child_start,
        child_start + len(child_phrase),
        strength_score=0.90,
        parent_phrase=parent_phrase,
        relation="left_extension",
        right_added=0,
        child_structural=True,
    )

    parent = _verified_quality_candidate(
        parent_phrase,
        0,
        len(parent_phrase),
        strength_score=0.90,
    )

    result = select_highlight_candidates(
        workspace_id="ws-test",
        doc_id="doc-1",
        article_text=article,
        phrase_candidates=[child, parent],
        resolved_targets=None,
        vertical="general",
    )

    selected_child = next(
        item
        for item in result["selected"]
        if item["phrase"].casefold() == child_phrase.casefold()
    )

    assert selected_child["quality_dominance_applied"] is False
    assert selected_child["quality_dominance_penalty"] == 0.0
    assert selected_child["quality_dominance_can_block"] is False
    assert selected_child["strength_score"] == 0.90


def test_quality_dominance_compensates_only_inherited_phrase_strength_advantage(monkeypatch):
    import backend.server.stores.highlight_selection_engine as engine

    monkeypatch.setattr(
        engine,
        "get_rejection_pattern_knowledge",
        lambda *_a, **_k: {"patterns": []},
    )

    article = "Calcium channel blockers are commonly prescribed."

    child_phrase = "Calcium channel"
    parent_phrase = "Calcium channel blockers"

    child = _verified_quality_candidate(
        child_phrase,
        0,
        len(child_phrase),
        strength_score=1.00,
        parent_phrase=parent_phrase,
        relation="right_extension",
        right_added=1,
        child_structural=False,
    )

    parent = _verified_quality_candidate(
        parent_phrase,
        0,
        len(parent_phrase),
        strength_score=0.72,
    )

    result = select_highlight_candidates(
        workspace_id="ws-test",
        doc_id="doc-1",
        article_text=article,
        phrase_candidates=[child, parent],
        resolved_targets=None,
        vertical="general",
    )

    selected_child = next(
        item
        for item in result["selected"]
        if item["phrase"].casefold() == child_phrase.casefold()
    )

    selected_parent = next(
        item
        for item in result["selected"]
        if item["phrase"].casefold() == parent_phrase.casefold()
    )

    # Upstream Scorer authority is preserved.
    assert selected_child["strength_score"] == 1.00
    assert selected_parent["strength_score"] == 0.72

    # Quality dominance remains advisory/ranking-only.
    assert selected_child["quality_dominance_applied"] is True
    assert selected_child["quality_dominance_can_block"] is False

    # The incomplete child's inherited phrase-strength advantage must be
    # neutralized, while retaining the bounded four-point quality margin.
    assert selected_child["quality_dominance_penalty"] == 19.4

    # Complete same-occurrence parent must outrank its degraded child.
    assert (
        selected_parent["selection_score"]
        > selected_child["selection_score"]
    )
