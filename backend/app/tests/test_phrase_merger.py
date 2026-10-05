from backend.server.stores.phrase_merger import merge_phrase_candidates


def _discovery_candidate(
    phrase,
    *,
    start,
    end,
    section_id="p0_s0",
    sentence_index=0,
    section_index=0,
    sentence_role="body",
    block_index=0,
    block_kind="paragraph",
    all_positions=None,
    occurrence_count=None,
    snippet="",
):
    positions = list(all_positions if all_positions is not None else [start])

    if occurrence_count is None:
        occurrence_count = len(positions)

    return {
        "phrase": phrase,
        "source_type": "semantic_concept",
        "section_id": section_id,
        "snippet": snippet,
        "provenance": ["phrase_discovery"],
        "discovery_intelligence": {
            "literal_span_verified": True,
            "span": {
                "start": start,
                "end": end,
                "sentence_index": sentence_index,
                "section_index": section_index,
                "sentence_role": sentence_role,
                "block_index": block_index,
                "block_kind": block_kind,
            },
            "first_position": positions[0] if positions else -1,
            "all_positions": positions,
            "occurrence_count": occurrence_count,
            "position_source": "phrase_discovery",
            "position_basis": "literal_span",
        },
    }


def _extractor_candidate(
    phrase,
    *,
    section_id="p0_s0",
    snippet="",
):
    return {
        "phrase": phrase,
        "source_type": "smart_phrase_extractor",
        "section_id": section_id,
        "snippet": snippet,
        "extractor_intelligence": {
            "test_source": "extractor",
        },
    }


def test_phrase_merger_exact_cross_source_overlap():
    text = "Blood pressure affects health."

    extractor = [
        _extractor_candidate(
            "Blood pressure",
            section_id="p0_s0",
            snippet=text,
        )
    ]

    discovery = [
        _discovery_candidate(
            "Blood pressure",
            start=0,
            end=14,
            section_id="p0_s0",
            snippet=text,
        )
    ]

    diagnostics = {}

    result = merge_phrase_candidates(
        text=text,
        extractor_candidates=extractor,
        discovery_candidates=discovery,
        diagnostics=diagnostics,
    )

    assert len(result) == 1
    assert result[0]["provenance"] == [
        "smart_phrase_extractor",
        "phrase_discovery",
    ]
    assert result[0]["merger_intelligence"]["merged_cross_source"] is True
    assert (
        result[0]["merger_intelligence"]["overlap_type"]
        == "exact_phrase_exact_occurrence"
    )
    assert diagnostics["exact_cross_source_overlaps"] == 1


def test_phrase_merger_repeated_phrase_position():
    text = (
        "Blood pressure affects health. "
        "Later, blood pressure may change."
    )

    second_start = text.casefold().rfind("blood pressure")
    second_end = second_start + len("blood pressure")

    extractor = [
        _extractor_candidate(
            "blood pressure",
            section_id="p0_s1",
            snippet="Later, blood pressure may change.",
        )
    ]

    discovery = [
        _discovery_candidate(
            "blood pressure",
            start=second_start,
            end=second_end,
            section_id="p0_s1",
            sentence_index=1,
            all_positions=[0, second_start],
            occurrence_count=2,
            snippet="Later, blood pressure may change.",
        )
    ]

    result = merge_phrase_candidates(
        text=text,
        extractor_candidates=extractor,
        discovery_candidates=discovery,
    )

    assert len(result) == 1

    position = result[0]["position_intelligence"]

    assert position["matched_occurrence"]["start"] == second_start
    assert position["matched_occurrence"]["end"] == second_end
    assert position["all_positions"] == [0, second_start]
    assert position["occurrence_count"] == 2


def test_phrase_merger_preserves_related_but_distinct_variants():
    text = "High blood pressure can increase cardiovascular risk."

    high_start = text.index("High blood pressure")
    high_end = high_start + len("High blood pressure")

    extractor = [
        _extractor_candidate(
            "blood pressure",
            section_id="p0_s0",
            snippet=text,
        )
    ]

    discovery = [
        _discovery_candidate(
            "High blood pressure",
            start=high_start,
            end=high_end,
            section_id="p0_s0",
            snippet=text,
        )
    ]

    diagnostics = {}

    result = merge_phrase_candidates(
        text=text,
        extractor_candidates=extractor,
        discovery_candidates=discovery,
        diagnostics=diagnostics,
    )

    assert len(result) == 2
    assert {item["phrase"] for item in result} == {
        "blood pressure",
        "High blood pressure",
    }
    assert diagnostics["exact_cross_source_overlaps"] == 0
    assert diagnostics["extractor_only"] == 1
    assert diagnostics["discovery_only"] == 1


def test_phrase_merger_extractor_only():
    text = "Blood pressure affects health."

    extractor = [
        _extractor_candidate(
            "Blood pressure",
            section_id="p0_s0",
            snippet=text,
        )
    ]

    diagnostics = {}

    result = merge_phrase_candidates(
        text=text,
        extractor_candidates=extractor,
        discovery_candidates=[],
        diagnostics=diagnostics,
    )

    assert len(result) == 1
    assert result[0]["provenance"] == ["smart_phrase_extractor"]
    assert result[0]["merger_intelligence"]["merged_cross_source"] is False
    assert diagnostics["extractor_only"] == 1


def test_phrase_merger_discovery_only():
    text = "Blood pressure affects health."

    discovery = [
        _discovery_candidate(
            "Blood pressure",
            start=0,
            end=14,
            section_id="p0_s0",
            snippet=text,
        )
    ]

    diagnostics = {}

    result = merge_phrase_candidates(
        text=text,
        extractor_candidates=[],
        discovery_candidates=discovery,
        diagnostics=diagnostics,
    )

    assert len(result) == 1
    assert result[0]["provenance"] == ["phrase_discovery"]
    assert result[0]["merger_intelligence"]["merged_cross_source"] is False
    assert diagnostics["discovery_only"] == 1


def test_phrase_merger_dual_provenance():
    text = "Blood pressure affects health."

    extractor = [
        _extractor_candidate(
            "Blood pressure",
            section_id="p0_s0",
            snippet=text,
        )
    ]

    discovery = [
        _discovery_candidate(
            "Blood pressure",
            start=0,
            end=14,
            section_id="p0_s0",
            snippet=text,
        )
    ]

    result = merge_phrase_candidates(
        text=text,
        extractor_candidates=extractor,
        discovery_candidates=discovery,
    )

    record = result[0]

    assert record["provenance"] == [
        "smart_phrase_extractor",
        "phrase_discovery",
    ]
    assert record["merger_intelligence"]["origins"] == [
        "smart_phrase_extractor",
        "phrase_discovery",
    ]
    assert "extractor_intelligence" in record
    assert "discovery_intelligence" in record


def test_phrase_merger_literal_span_invariant():
    text = (
        "Alpha phrase appears first. "
        "Beta phrase appears later."
    )

    extractor = [
        _extractor_candidate(
            "Alpha phrase",
            section_id="p0_s0",
            snippet="Alpha phrase appears first.",
        ),
        _extractor_candidate(
            "Beta phrase",
            section_id="p0_s1",
            snippet="Beta phrase appears later.",
        ),
    ]

    result = merge_phrase_candidates(
        text=text,
        extractor_candidates=extractor,
        discovery_candidates=[],
    )

    assert result

    for record in result:
        position = record["position_intelligence"]
        matched = position["matched_occurrence"]

        assert position["literal_span_verified"] is True
        assert matched is not None

        start = matched["start"]
        end = matched["end"]

        assert text[start:end].casefold() == record["phrase"].casefold()


def test_phrase_merger_position_preservation():
    text = (
        "Blood pressure affects health. "
        "Later, blood pressure may change."
    )

    second_start = text.casefold().rfind("blood pressure")
    second_end = second_start + len("blood pressure")

    extractor = [
        _extractor_candidate(
            "blood pressure",
            section_id="p0_s1",
            snippet="Later, blood pressure may change.",
        )
    ]

    discovery = [
        _discovery_candidate(
            "blood pressure",
            start=second_start,
            end=second_end,
            section_id="p0_s1",
            sentence_index=1,
            all_positions=[0, second_start],
            occurrence_count=2,
            snippet="Later, blood pressure may change.",
        )
    ]

    result = merge_phrase_candidates(
        text=text,
        extractor_candidates=extractor,
        discovery_candidates=discovery,
    )

    position = result[0]["position_intelligence"]

    assert position["first_position"] == 0
    assert position["all_positions"] == [0, second_start]
    assert position["occurrence_count"] == 2
    assert position["matched_occurrence"]["start"] == second_start
    assert position["matched_occurrence"]["end"] == second_end
    assert position["position_source"] == "phrase_discovery"
    assert position["position_basis"] == "literal_span"


def test_phrase_merger_deterministic_order():
    text = "Alpha phrase appears first. Beta phrase appears later."

    first_order = [
        _extractor_candidate(
            "Beta phrase",
            section_id="p0_s1",
            snippet="Beta phrase appears later.",
        ),
        _extractor_candidate(
            "Alpha phrase",
            section_id="p0_s0",
            snippet="Alpha phrase appears first.",
        ),
    ]

    second_order = list(reversed(first_order))

    first_result = merge_phrase_candidates(
        text=text,
        extractor_candidates=first_order,
        discovery_candidates=[],
    )

    second_result = merge_phrase_candidates(
        text=text,
        extractor_candidates=second_order,
        discovery_candidates=[],
    )

    first_view = [
        (
            record["phrase"],
            record["position_intelligence"]["matched_occurrence"]["start"],
        )
        for record in first_result
    ]

    second_view = [
        (
            record["phrase"],
            record["position_intelligence"]["matched_occurrence"]["start"],
        )
        for record in second_result
    ]

    assert first_view == second_view
    assert [item[0] for item in first_view] == [
        "Alpha phrase",
        "Beta phrase",
    ]
