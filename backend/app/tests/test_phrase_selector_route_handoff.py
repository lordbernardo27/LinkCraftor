from copy import deepcopy
import importlib
import re

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.mark.parametrize(
    ("fault", "expected_error"),
    [
        ("none", None),
        (
            "missing_top_level",
            "Phrase Selector canonical handoff contract is missing",
        ),
        (
            "bad_count",
            "Pipeline 2 canonical candidate count does not match",
        ),
        (
            "nested_mismatch",
            "Pipeline 2 coordinator and Selector canonical outputs disagree",
        ),
        (
            "density_mutation",
            "Legacy Density modified the canonical Pipeline 2 handoff",
        ),
    ],
)
def test_engine_route_canonical_handoff(
    monkeypatch, tmp_path, fault, expected_error
):
    route = importlib.import_module(
        "backend.server.routes.engine_run"
    )

    # All relative route writes must stay inside pytest storage.
    monkeypatch.chdir(tmp_path)

    phrases = [
        "Blood Pressure Monitoring",
        "Kidney Function Assessment",
        "Heart Failure Management",
    ]
    article = ". ".join(phrases) + "."

    candidates = [
        {
            "phrase": phrase,
            "upstream_candidate_id": f"candidate-{index:03d}",
            "source_hash": "controlled-source-hash",
            "custom_lineage": {
                "origin": "http-contract-test",
                "nested": {"index": index},
            },
        }
        for index, phrase in enumerate(phrases)
    ]

    selection = {
        "selected": deepcopy(candidates),
        "candidates": deepcopy(candidates),
        "all_selected_phrase_candidates": deepcopy(candidates),
        "rejected": [],
        "stats": {"selected_count": len(candidates)},
    }

    coordinator_result = {
        "ok": True,
        "status": "HIGHLIGHT_SELECTION_COMPLETED",
        "latest_stage": "highlight_selection_engine",
        "phrase_candidate_count": len(candidates),
        "all_selected_phrase_candidates": deepcopy(candidates),
        "all_selected_phrase_candidate_count": len(candidates),
        "highlight_selection": selection,
    }

    if fault == "missing_top_level":
        coordinator_result.pop("all_selected_phrase_candidates")
    elif fault == "bad_count":
        coordinator_result["all_selected_phrase_candidate_count"] = 2
    elif fault == "nested_mismatch":
        selection["all_selected_phrase_candidates"][0]["phrase"] = (
            "Different Phrase"
        )

    saved_priority_calls = []

    def fake_density(*, article_text, selected_candidates):
        assert article_text == article
        assert selected_candidates is selection["selected"]

        # Simulate legacy Density mutating and reducing its input.
        selected_candidates[0]["display_status"] = "legacy-density"

        if fault == "density_mutation":
            coordinator_result[
                "all_selected_phrase_candidates"
            ][0]["phrase"] = "Unauthorized Mutation"

        return {
            "final_highlights": [selected_candidates[0]],
            "stats": {"final_count": 1},
        }

    def fake_save_priority(**kwargs):
        saved_priority_calls.append(kwargs)
        return {"saved": True, "path": "isolated-test-storage"}

    monkeypatch.setattr(
        route,
        "build_rb2_phrase_contexts",
        lambda doc_id, **kwargs: {
            "version": "isolated-http-test",
            "paragraphs": [],
            "joinedText": kwargs.get("text") or "",
        },
    )
    monkeypatch.setattr(
        route,
        "run_uploaded_document_to_highlight_pipeline",
        lambda **kwargs: coordinator_result,
    )
    monkeypatch.setattr(
        route, "apply_highlight_density", fake_density
    )
    monkeypatch.setattr(
        route, "_save_priority_phrase_set", fake_save_priority
    )
    monkeypatch.setattr(
        route,
        "classify_highlight_buckets",
        lambda final_highlights: {
            "internal_strong": [],
            "semantic_optional": [],
        },
    )
    monkeypatch.setattr(
        route,
        "_apply_article_duplicate_url_guard",
        lambda hits: False,
    )

    app = FastAPI()
    app.include_router(route.router)
    client = TestClient(app)

    request = {
        "workspaceId": "ws-route-contract-test",
        "docId": "doc-route-contract-test",
        "text": article,
    }

    if expected_error is not None:
        with pytest.raises(
            RuntimeError,
            match=re.escape(expected_error),
        ):
            client.post("/api/engine/run", json=request)
        return

    response = client.post("/api/engine/run", json=request)

    assert response.status_code == 200, response.text

    payload = response.json()
    assert payload["ok"] is True

    meta = payload["meta"]
    assert meta["canonical_all_selected_phrase_candidate_count"] == 3
    assert meta["final_highlight_count"] == 1

    assert len(saved_priority_calls) == 1
    assert len(saved_priority_calls[0]["final_highlights"]) == 1

    assert coordinator_result[
        "all_selected_phrase_candidates"
    ] == candidates

    assert selection[
        "all_selected_phrase_candidates"
    ] == candidates

    assert selection["selected"][0]["display_status"] == (
        "legacy-density"
    )

    debug_file = (
        tmp_path
        / "backend/server/data/debug_highlight_selection_last.json"
    )
    assert debug_file.is_file()
