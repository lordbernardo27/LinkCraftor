from copy import deepcopy
from hashlib import sha256
import importlib

from fastapi import FastAPI
from fastapi.testclient import TestClient


def test_real_coordinator_through_production_http_route(
    monkeypatch, tmp_path
):
    route = importlib.import_module(
        "backend.server.routes.engine_run"
    )
    coordinator = importlib.import_module(
        "backend.server.pipelines.upload_document."
        "uploaded_document_to_highlight_pipeline.coordinator"
    )

    phrases = (
        "Blood Pressure Monitoring",
        "Kidney Function Assessment",
        "Heart Failure Management",
    )
    article = ". ".join(phrases) + "."
    article_hash = sha256(
        article.encode("utf-8")
    ).hexdigest()

    upstream = []
    for index, phrase in enumerate(phrases):
        start = article.index(phrase)
        upstream.append({
            "phrase": phrase,
            "workspace_id": "ws-test",
            "doc_id": "doc-integration",
            "source_type": "keyphrase",
            "source_hash": article_hash,
            "source_hash_basis": "article_text_utf8_sha256",
            "upstream_candidate_id": f"candidate-{index:03d}",
            "source_span": {
                "start": start,
                "end": start + len(phrase),
            },
            "custom_lineage": {
                "origin": "combined-route-integration",
                "nested": {"index": index},
            },
        })

    # Isolate upstream input; retain the real Guard,
    # Strength Scorer, Selector, and coordinator logic.
    monkeypatch.setattr(
        coordinator,
        "extract_smart_phrases",
        lambda **kwargs: deepcopy(upstream),
    )
    monkeypatch.setattr(
        coordinator,
        "discover_phrases",
        lambda **kwargs: [],
    )
    monkeypatch.setattr(
        coordinator,
        "merge_phrase_candidates",
        lambda **kwargs: deepcopy(upstream),
    )

    # Redirect coordinator diagnostics to pytest storage.
    monkeypatch.setattr(
        coordinator,
        "Path",
        lambda ignored: (
            tmp_path / "a" / "b" / "c" / "coordinator.py"
        ),
    )

    # Redirect route debug output to pytest storage.
    monkeypatch.chdir(tmp_path)

    monkeypatch.setattr(
        route,
        "build_rb2_phrase_contexts",
        lambda doc_id, **kwargs: {
            "version": "combined-integration-test",
            "paragraphs": [],
            "joinedText": kwargs.get("text") or "",
        },
    )

    observed = {
        "coordinator_calls": 0,
        "density_calls": 0,
        "priority_saves": 0,
    }

    real_coordinator = (
        coordinator.run_uploaded_document_to_highlight_pipeline
    )
    real_density = route.apply_highlight_density

    def coordinator_spy(**kwargs):
        observed["coordinator_calls"] += 1
        result = real_coordinator(**kwargs)
        observed["coordinator_result"] = result
        observed["canonical_before_density"] = deepcopy(
            result["all_selected_phrase_candidates"]
        )
        return result

    def density_spy(*, article_text, selected_candidates):
        observed["density_calls"] += 1
        observed["density_input_count"] = len(
            selected_candidates
        )
        result = real_density(
            article_text=article_text,
            selected_candidates=selected_candidates,
        )
        observed["density_result"] = result
        return result

    def fake_priority_save(**kwargs):
        observed["priority_saves"] += 1
        observed["saved_highlights"] = deepcopy(
            kwargs["final_highlights"]
        )
        return {"saved": True, "isolated": True}

    monkeypatch.setattr(
        route,
        "run_uploaded_document_to_highlight_pipeline",
        coordinator_spy,
    )
    monkeypatch.setattr(
        route,
        "apply_highlight_density",
        density_spy,
    )
    monkeypatch.setattr(
        route,
        "_save_priority_phrase_set",
        fake_priority_save,
    )
    monkeypatch.setattr(
        route,
        "classify_highlight_buckets",
        lambda highlights: {
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

    response = client.post(
        "/api/engine/run",
        json={
            "workspaceId": "ws-test",
            "docId": "doc-integration",
            "text": article,
        },
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["ok"] is True

    assert observed["coordinator_calls"] == 1
    assert observed["density_calls"] == 1
    assert observed["priority_saves"] == 1

    result = observed["coordinator_result"]
    canonical = result["all_selected_phrase_candidates"]
    nested = result["highlight_selection"][
        "all_selected_phrase_candidates"
    ]

    assert result["ok"] is True
    assert result["all_selected_phrase_candidate_count"] == 3
    assert len(canonical) == 3
    assert canonical == observed["canonical_before_density"]
    assert nested == canonical
    assert canonical is not nested

    assert observed["density_input_count"] == 3

    # Selector ranking may differ from extraction order.
    # Preserve every identity in the Selector-selected order.
    canonical_ids = [
        item["upstream_candidate_id"] for item in canonical
    ]
    upstream_ids = [
        item["upstream_candidate_id"] for item in upstream
    ]
    selected_ids = [
        item["upstream_candidate_id"]
        for item in result["highlight_selection"]["selected"]
    ]
    assert len(canonical_ids) == len(set(canonical_ids))
    assert set(canonical_ids) == set(upstream_ids)
    assert canonical_ids == selected_ids

    for item in canonical:
        assert "guard_intelligence" in item
        assert "scorer_intelligence" in item
        assert "strength_score" in item
        assert "source_hash" in item
        assert "source_span" in item
        assert "custom_lineage" in item

    final_highlights = observed[
        "density_result"
    ]["final_highlights"]

    assert payload["meta"][
        "canonical_all_selected_phrase_candidate_count"
    ] == 3
    assert payload["meta"][
        "final_highlight_count"
    ] == len(final_highlights)
    assert len(final_highlights) <= 3
    assert len(observed["saved_highlights"]) == len(
        final_highlights
    )

    assert (
        tmp_path
        / "backend/server/data/debug_highlight_selection_last.json"
    ).is_file()

    assert (
        tmp_path
        / "data/reports/"
        "uploaded_document_phrase_flow_diagnostics.jsonl"
    ).is_file()
