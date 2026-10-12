from copy import deepcopy
import re

from backend.app.tests.test_highlight_selection_source_identity import (
    candidate,
    select,
)


REQUIRED_FIELDS = (
    "workspace_id",
    "doc_id",
    "phrase",
    "phrase_key",
    "selection_phrase_id",
    "selection_occurrence_id",
    "selection_source_span",
    "selection_source_span_status",
    "selection_article_text_sha256",
    "selection_article_text_hash_basis",
    "selection_source_hash_status",
    "selection_source_version_status",
    "selection_position_intelligence",
    "selection_score",
    "base_selection_score",
    "selection_status",
    "dis_advisory_only",
    "dis_can_block",
    "dis_penalty",
)


def _single_record(incoming):
    original = deepcopy(incoming)
    result = select([incoming])

    assert result["ok"] is True
    assert result["selected"] is result["candidates"]
    assert len(result["selected"]) == 1
    assert incoming == original

    return result, result["selected"][0]


def test_contract_required_fields():
    _, record = _single_record(candidate())

    for key in REQUIRED_FIELDS:
        assert key in record, (
            f"Required selected-candidate field missing: {key}"
        )

    for key in (
        "workspace_id",
        "doc_id",
        "phrase",
        "phrase_key",
        "selection_phrase_id",
        "selection_occurrence_id",
    ):
        assert isinstance(record[key], str)
        assert record[key].strip()

    assert isinstance(
        record["selection_position_intelligence"], dict
    )

    assert isinstance(
        record["selection_score"], (int, float)
    )


def test_contract_source_hash_and_unverified_span():
    _, record = _single_record(candidate())

    assert (
        record["selection_article_text_hash_basis"]
        == "article_text_utf8_sha256"
    )

    assert re.fullmatch(
        r"[0-9a-f]{64}",
        record["selection_article_text_sha256"],
    )

    assert isinstance(
        record["selection_source_hash_status"], str
    )

    assert isinstance(
        record["selection_source_version_status"], str
    )

    if record["selection_source_span"] is None:
        assert (
            record["selection_source_span_status"]
            != "verified"
        )


def test_contract_preserves_upstream_metadata():
    incoming = candidate(
        custom_lineage={
            "origin": "candidate_window_guard",
            "nested": {
                "evidence": ["extractor", "guard"],
            },
        },
        upstream_intelligence={
            "component": "certified_semantic_output",
            "evidence": {
                "confidence": 0.87,
            },
        },
    )

    original = deepcopy(incoming)
    _, record = _single_record(incoming)

    assert (
        record["custom_lineage"]
        == original["custom_lineage"]
    )

    assert (
        record["upstream_intelligence"]
        == original["upstream_intelligence"]
    )

    assert incoming == original


def test_contract_preserves_overwritten_upstream_values():
    incoming = candidate(
        target_url="https://upstream.example/original",
        target_title="Original target",
        extractor_score=17.25,
        dis_signal_reasons=["historical evidence"],
    )

    original = deepcopy(incoming)
    _, record = _single_record(incoming)

    snapshot = record["selection_inherited_overwrites"]

    assert isinstance(snapshot, dict)

    for key in (
        "target_url",
        "target_title",
        "extractor_score",
        "dis_signal_reasons",
    ):
        assert key in snapshot
        assert snapshot[key] == original[key]

    for key, original_value in original.items():
        if key in snapshot:
            assert snapshot[key] == original_value
        else:
            assert key in record
            assert record[key] == original_value


def test_contract_dis_is_advisory_only():
    _, record = _single_record(candidate())

    assert record["dis_advisory_only"] is True
    assert record["dis_can_block"] is False

    assert type(record["dis_penalty"]) in (
        int, float
    )

    assert record["dis_penalty"] >= 0


def test_contract_output_envelope_and_optional_metadata():
    baseline_result, baseline = _single_record(
        candidate()
    )

    rich_result, rich = _single_record(
        candidate(
            custom_lineage={
                "origin": "candidate_window_guard",
            },
        )
    )

    assert "custom_lineage" not in baseline

    assert rich["custom_lineage"] == {
        "origin": "candidate_window_guard",
    }

    for result in (
        baseline_result,
        rich_result,
    ):
        assert result["selected"] is result["candidates"]
        assert result["stats"]["total_candidates"] == 1
        assert result["stats"]["ranked_count"] == 1
        assert len(result["selected"]) == 1
        assert isinstance(result["rejected"], list)
