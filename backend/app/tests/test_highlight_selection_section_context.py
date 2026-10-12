from copy import deepcopy

from backend.server.stores.phrase_merger import merge_phrase_candidates
from backend.server.stores.highlight_selection_engine import (
    _selection_section_context_from_merger,
    select_highlight_candidates,
)


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


def merge_one(article, section_id, *, html="", title=""):
    records = merge_phrase_candidates(
        text=article,
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


def verified_span(record):
    occurrence = record["position_intelligence"]["matched_occurrence"]
    return occurrence["start"], occurrence["end"]


def test_plain_text_root_section_is_certified():
    record = merge_one(BODY, "p0_s0")

    context, status = _selection_section_context_from_merger(
        record,
        verified_span(record),
        BODY,
    )

    assert status == "verified_original_article"
    assert context["section_index"] == 0
    assert context["coordinate_space"] == "original_article"
    assert context["section_span"]["start"] == 0
    assert context["section_span"]["end"] == len(BODY)


def test_markdown_parent_has_direct_and_hierarchical_spans():
    record = merge_one(MARKDOWN, "p1_s0")

    context, status = _selection_section_context_from_merger(
        record,
        verified_span(record),
        MARKDOWN,
    )

    assert status == "verified_original_article"
    assert context["section_index"] == 1
    assert context["section_heading"] == "# Kidney Health"
    assert context["section_span"]["end"] == len(MARKDOWN)
    assert (
        context["direct_section_span"]["end"]
        == MARKDOWN.index("## Treatment")
    )


def test_nested_section_hierarchy_is_certified():
    record = merge_one(MARKDOWN, "p3_s0")

    context, status = _selection_section_context_from_merger(
        record,
        verified_span(record),
        MARKDOWN,
    )

    assert status == "verified_original_article"
    assert context["section_index"] == 2
    assert context["parent_section_index"] == 1
    assert [
        entry["section_index"]
        for entry in context["section_path"]
    ] == [0, 1, 2]


def test_html_section_is_advisory_without_original_offsets():
    html = (
        "<h2>Kidney Health</h2>"
        "<p>Kidney disease requires monitoring.</p>"
        "<h3>Treatment</h3>"
        "<p>Treatment can slow kidney disease.</p>"
    )

    record = merge_one(BODY, "p0_s0", html=html)

    context, status = _selection_section_context_from_merger(
        record,
        None,
        BODY,
    )

    assert status == "unverified_original_article"
    assert context["section_index"] == 1
    assert context["section_heading"] == "Kidney Health"
    assert context["section_span"] is None
    assert context["direct_section_span"] is None
    assert context["heading_span"] is None
    assert all(
        entry["heading_span"] is None
        for entry in context["section_path"]
    )


def test_invalid_section_boundary_is_not_certified():
    record = merge_one(MARKDOWN, "p1_s0")
    tampered = deepcopy(record)

    tampered["merger_section_intelligence"][
        "section_span"
    ]["end"] = len(MARKDOWN) + 10

    context, status = _selection_section_context_from_merger(
        tampered,
        verified_span(tampered),
        MARKDOWN,
    )

    assert status == "invalid_section_alignment"
    assert context["coordinate_space"] != "original_article"
    assert context["section_span"] is None


def test_missing_section_evidence_is_explicit():
    context, status = _selection_section_context_from_merger(
        {"phrase": "Kidney disease"},
        None,
        BODY,
    )

    assert context is None
    assert status == "missing_section_evidence"


def test_real_selector_preserves_and_certifies_section_context():
    record = merge_one(BODY, "p0_s0")

    result = select_highlight_candidates(
        workspace_id="ws_section_test",
        doc_id="section-test",
        article_text=BODY,
        phrase_candidates=[record],
        resolved_targets=None,
        vertical="health",
    )

    def walk(value):
        if isinstance(value, dict):
            if "selection_section_context_status" in value:
                yield value

            for child in value.values():
                yield from walk(child)

        elif isinstance(value, (list, tuple)):
            for child in value:
                yield from walk(child)

    candidates = list(walk(result))
    selected = [
        item for item in candidates
        if item.get("phrase") == "Kidney disease"
    ]

    assert selected, "Selector did not return section-context candidate"

    candidate = selected[0]

    assert (
        candidate["selection_section_context_status"]
        == "verified_original_article"
    )
    assert candidate["selection_section_context"]["section_index"] == 0
    assert (
        candidate["selection_section_context"]["coordinate_space"]
        == "original_article"
    )

    assert (
        candidate["merger_section_intelligence"]
        == record["merger_section_intelligence"]
    )
