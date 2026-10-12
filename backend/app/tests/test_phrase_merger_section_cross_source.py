from unittest.mock import patch

from backend.server.stores import phrase_merger as pm


ARTICLE = "Kidney disease requires monitoring."


def _position():
    return {
        "literal_span_verified": True,
        "matched_occurrence": {
            "start": 0,
            "end": 14,
        },
        "first_position": 0,
        "all_positions": [0],
        "occurrence_count": 1,
    }


def _merge_with_section_evidence(extractor_section, discovery_section):
    with (
        patch.object(
            pm,
            "_recover_extractor_occurrence",
            return_value=_position(),
        ),
        patch.object(
            pm,
            "_recover_discovery_occurrence",
            return_value=_position(),
        ),
        patch.object(
            pm,
            "_build_merger_section_intelligence",
            side_effect=[
                extractor_section,
                discovery_section,
            ],
        ),
    ):
        records = pm.merge_phrase_candidates(
            text=ARTICLE,
            document_id="cross-source-section-test",
            extractor_candidates=[{
                "phrase": "Kidney disease",
                "source_type": "body",
                "section_id": "p0_s0",
                "snippet": ARTICLE,
            }],
            discovery_candidates=[{
                "phrase": "Kidney disease",
                "source_type": "body",
                "section_id": "p0_s0",
                "snippet": ARTICLE,
            }],
        )

    assert len(records) == 1
    return records[0]


def test_primary_section_follows_primary_discovery_position():
    record = _merge_with_section_evidence(
        {
            "status": "verified_original_article",
            "section_index": 1,
            "source_marker": "extractor",
        },
        {
            "status": "verified_original_article",
            "section_index": 2,
            "source_marker": "discovery",
        },
    )

    merger = record["merger_intelligence"]

    assert merger["merged_cross_source"] is True
    assert record["position_intelligence"]["matched_occurrence"] == {
        "start": 0,
        "end": 14,
    }

    assert (
        record["merger_section_intelligence"]["source_marker"]
        == "discovery"
    )
    assert record["merger_section_intelligence"]["section_index"] == 2

    sources = merger["source_metadata"]

    assert (
        sources["smart_phrase_extractor"]
        ["merger_section_intelligence"]["section_index"]
        == 1
    )
    assert (
        sources["phrase_discovery"]
        ["merger_section_intelligence"]["section_index"]
        == 2
    )


def test_unresolved_discovery_section_does_not_inherit_extractor_section():
    record = _merge_with_section_evidence(
        {
            "status": "verified_original_article",
            "section_index": 1,
        },
        {
            "status": "unresolved",
            "section_index": None,
        },
    )

    assert (
        record["merger_section_intelligence"]["status"]
        == "unresolved"
    )
    assert (
        record["merger_section_intelligence"]["section_index"]
        is None
    )

    # The independent extractor evidence must still be available.
    sources = record["merger_intelligence"]["source_metadata"]

    assert (
        sources["smart_phrase_extractor"]
        ["merger_section_intelligence"]["section_index"]
        == 1
    )
