from copy import deepcopy

from backend.server.stores.highlight_selection_engine import (
    select_highlight_candidates,
)


def _selection():
    incoming = [
        {
            "phrase": "Blood Pressure",
            "workspace_id": "ws-test",
            "doc_id": "doc-1",
            "upstream_candidate_id": "upstream-001",
            "custom_lineage": {
                "source": {
                    "labels": ["original"],
                },
                "generation": 1,
            },
        }
    ]

    before = deepcopy(incoming)

    result = select_highlight_candidates(
        workspace_id="ws-test",
        doc_id="doc-1",
        article_text="Blood Pressure matters.",
        phrase_candidates=incoming,
        resolved_targets=None,
        vertical="general",
    )

    assert result["ok"] is True
    assert len(result["selected"]) == 1
    assert len(result["all_selected_phrase_candidates"]) == 1

    return incoming, before, result


def test_legacy_nested_mutation_does_not_change_input_or_canonical():
    incoming, before, result = _selection()

    selected = result["selected"]
    canonical = result["all_selected_phrase_candidates"]

    assert selected is result["candidates"]
    assert canonical is not selected
    assert canonical == selected
    assert incoming == before

    assert (
        selected[0]["custom_lineage"]
        is not incoming[0]["custom_lineage"]
    )

    selected[0]["custom_lineage"]["generation"] = 99
    selected[0]["custom_lineage"]["source"]["labels"].append(
        "downstream"
    )

    assert incoming == before

    assert canonical[0]["custom_lineage"] == {
        "source": {
            "labels": ["original"],
        },
        "generation": 1,
    }


def test_canonical_nested_mutation_does_not_change_legacy_or_input():
    incoming, before, result = _selection()

    selected = result["selected"]
    canonical = result["all_selected_phrase_candidates"]

    canonical[0]["custom_lineage"]["generation"] = 77
    canonical[0]["custom_lineage"]["source"]["labels"].append(
        "canonical"
    )

    assert selected[0]["custom_lineage"] == {
        "source": {
            "labels": ["original"],
        },
        "generation": 1,
    }

    assert incoming == before
