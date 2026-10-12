from backend.server.stores.phrase_merger import merge_phrase_candidates

BODY = (
    "Kidney disease requires monitoring.\n\n"
    "Treatment can slow kidney disease."
)

MARKDOWN = (
    "# Kidney Health\n\n"
    "Kidney disease requires monitoring.\n\n"
    "## Treatment\n\n"
    "Treatment can slow kidney disease."
)


def merge_one(text, section_id, *, html="", title=""):
    records = merge_phrase_candidates(
        text=text,
        html=html,
        title=title,
        document_id="section-test",
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


def test_plain_text_root_section():
    record = merge_one(BODY, "p0_s0")
    section = record["merger_section_intelligence"]

    assert section["status"] == "verified_original_article"
    assert section["section_index"] == 0
    assert section["parent_section_index"] is None
    assert section["section_span"]["start"] == 0
    assert section["section_span"]["end"] == len(BODY)
    assert section["section_span"]["coordinate_space"] == "original_article"


def test_parent_section_includes_nested_child():
    record = merge_one(MARKDOWN, "p1_s0")
    section = record["merger_section_intelligence"]

    assert section["original_article_verified"] is True
    assert section["section_index"] == 1
    assert section["heading_level"] == 1
    assert section["section_heading"] == "# Kidney Health"
    assert section["parent_section_index"] == 0

    assert [
        entry["section_index"]
        for entry in section["section_path"]
    ] == [0, 1]

    # The parent includes its nested Treatment subsection.
    assert section["section_span"]["end"] == len(MARKDOWN)

    # Its direct content ends before the child heading.
    assert (
        section["direct_section_span"]["end"]
        == MARKDOWN.index("## Treatment")
    )


def test_nested_child_hierarchy():
    record = merge_one(MARKDOWN, "p3_s0")
    section = record["merger_section_intelligence"]

    assert section["original_article_verified"] is True
    assert section["section_index"] == 2
    assert section["heading_level"] == 2
    assert section["section_heading"] == "## Treatment"
    assert section["parent_section_index"] == 1

    assert [
        entry["section_index"]
        for entry in section["section_path"]
    ] == [0, 1, 2]

    assert section["section_span"]["end"] == len(MARKDOWN)


def test_html_hierarchy_retains_unverified_surface_coordinates():
    html = (
        "<h2>Kidney Health</h2>"
        "<p>Kidney disease requires monitoring.</p>"
        "<h3>Treatment</h3>"
        "<p>Treatment can slow kidney disease.</p>"
    )

    record = merge_one(BODY, "p0_s0", html=html)
    section = record["merger_section_intelligence"]

    assert section["status"] == "unverified_original_article"
    assert section["original_article_verified"] is False
    assert section["section_index"] == 1
    assert section["section_heading"] == "Kidney Health"
    assert section["parent_section_index"] == 0
    assert (
        section["section_span"]["coordinate_space"]
        == "phrase_discovery_surface_v1"
    )
    assert (
        record["position_intelligence"]["original_article_span_verified"]
        is False
    )


def test_separate_title_does_not_claim_original_coordinates():
    record = merge_one(BODY, "p0_s0", title="Kidney Health")
    section = record["merger_section_intelligence"]

    assert section["status"] == "unverified_original_article"
    assert section["original_article_verified"] is False
    assert section["section_index"] == 0
    assert section["section_heading"] == "Kidney Health"
    assert section["section_span"]["coordinate_space"] != "original_article"
