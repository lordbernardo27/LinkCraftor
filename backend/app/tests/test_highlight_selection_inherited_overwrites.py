
from copy import deepcopy

from backend.app.tests.test_highlight_selection_source_identity import (
    candidate,
    select,
)


def test_selector_preserves_inherited_overwritten_fields():
    incoming = candidate(
        target_url="https://upstream.example/original",
        target_title="Original upstream target",
        extractor_score=17.25,
        dis_signal_reasons=["upstream evidence"],
        selection_score=99.0,
        custom_lineage={"stage": "candidate_window_guard"},
    )

    original = deepcopy(incoming)

    result = select([incoming])

    # The two output keys intentionally alias one candidate list.
    assert result["selected"] is result["candidates"]

    records = result["selected"]
    assert len(records) == 1

    record = records[0]
    inherited = record["selection_inherited_overwrites"]

    for field in (
        "target_url",
        "target_title",
        "extractor_score",
        "dis_signal_reasons",
        "selection_score",
    ):
        assert inherited[field] == original[field]

    assert record["custom_lineage"] == original["custom_lineage"]
    assert incoming == original

    incoming["dis_signal_reasons"].append("later mutation")

    assert inherited["dis_signal_reasons"] == [
        "upstream evidence"
    ]
