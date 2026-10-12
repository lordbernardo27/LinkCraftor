from backend.server.stores.phrase_merger import merge_phrase_candidates


BODY = (
    "Kidney disease requires monitoring.\n\n"
    "Treatment can slow kidney disease."
)


def _merge(text, *, html="", title="", section_id="p0_s0"):
    records = merge_phrase_candidates(
        text=text,
        html=html,
        title=title,
        document_id="coordinate-test",
        extractor_candidates=[{
            "phrase": "Kidney disease",
            "source_type": "body",
            "section_id": section_id,
            "snippet": "Kidney disease requires monitoring.",
        }],
        discovery_candidates=[],
    )
    assert len(records) == 1
    return records[0]


def test_plain_text_original_coordinates_are_verified():
    record = _merge(BODY)
    info = record["position_intelligence"]

    assert info["original_article_span_verified"] is True
    assert info["literal_span_verified"] is True
    assert info["coordinate_space"] == "original_article"
    assert info["matched_occurrence"]["start"] == 0
    assert info["matched_occurrence"]["end"] == 14


def test_markdown_coordinates_are_verified_when_surfaces_match():
    article = (
        "# Kidney Health\n\n"
        "Kidney disease requires monitoring.\n\n"
        "## Treatment\n\n"
        "Treatment can slow kidney disease."
    )

    record = _merge(article, section_id="p1_s0")
    info = record["position_intelligence"]

    assert info["original_article_span_verified"] is True
    span = info["matched_occurrence"]

    assert article[span["start"]:span["end"]] == "Kidney disease"


def test_separate_title_does_not_certify_shifted_offsets():
    record = _merge(BODY, title="Kidney Health")
    info = record["position_intelligence"]

    assert info["original_article_span_verified"] is False
    assert info["literal_span_verified"] is False
    assert info["matched_occurrence"] is None
    assert info["original_article_alignment_status"] == "surface_mismatch"

    upstream = info["surface_position_intelligence"]
    assert upstream["literal_span_verified"] is True
    assert upstream["matched_occurrence"]["start"] == 15


def test_html_structure_does_not_certify_shifted_offsets():
    html = (
        "<h2>Kidney Health</h2>"
        "<p>Kidney disease requires monitoring.</p>"
        "<h3>Treatment</h3>"
        "<p>Treatment can slow kidney disease.</p>"
    )

    record = _merge(BODY, html=html)
    info = record["position_intelligence"]

    assert info["original_article_span_verified"] is False
    assert info["literal_span_verified"] is False
    assert info["matched_occurrence"] is None
    assert info["coordinate_space"] == "unverified_original_article"
    assert (
        info["surface_position_intelligence"]["matched_occurrence"]
        ["start"] == 15
    )


def test_discovery_surface_evidence_is_preserved_when_unaligned():
    records = merge_phrase_candidates(
        text=BODY,
        title="Kidney Health",
        document_id="coordinate-test",
        extractor_candidates=[],
        discovery_candidates=[{
            "phrase": "Kidney disease",
            "source_type": "discovery",
            "section_id": "p0_s0",
            "discovery_intelligence": {
                "literal_span_verified": True,
                "span": {
                    "start": 15,
                    "end": 29,
                    "section_index": 0,
                },
                "first_position": 15,
                "all_positions": [15],
                "occurrence_count": 1,
                "position_basis": "phrase_discovery_surface_v1",
            },
        }],
    )

    assert len(records) == 1
    info = records[0]["position_intelligence"]

    assert info["original_article_span_verified"] is False
    assert info["matched_occurrence"] is None

    upstream = info["surface_position_intelligence"]
    assert upstream["literal_span_verified"] is True
    assert upstream["matched_occurrence"]["start"] == 15
    assert upstream["matched_occurrence"]["section_index"] == 0
