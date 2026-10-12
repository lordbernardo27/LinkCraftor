from copy import deepcopy
from hashlib import sha256

from backend.server.stores.candidate_window_guard import (
    candidate_window_guard,
)
from backend.server.stores.phrase_strength_scorer import (
    score_phrase_strength,
)
from backend.server.stores.highlight_selection_engine import (
    select_highlight_candidates,
)
from backend.server.stores.highlight_density_engine import (
    apply_highlight_density,
)


PHRASES = (
    "Blood Pressure Monitoring",
    "Kidney Function Assessment",
    "Heart Failure Management",
)


def _run_pipeline2_contract():
    article = ". ".join(PHRASES) + "."
    article_hash = sha256(
        article.encode("utf-8")
    ).hexdigest()

    scorer_passed = []

    for index, phrase in enumerate(PHRASES):
        candidate = {
            "phrase": phrase,
            "workspace_id": "ws-test",
            "doc_id": "doc-integration",
            "source_type": "keyphrase",
            "source_hash": article_hash,
            "source_hash_basis": (
                "article_text_utf8_sha256"
            ),
            "upstream_candidate_id": (
                f"candidate-{index:03d}"
            ),
            "custom_lineage": {
                "origin": "integration-regression",
                "nested": {"index": index},
            },
        }

        original = deepcopy(candidate)

        guarded = candidate_window_guard(
            candidate,
            source_type="keyphrase",
            workspace_id="ws-test",
            document_id="doc-integration",
            vertical="general",
        )

        assert guarded.get("keep") is True

        scored = score_phrase_strength(
            guarded,
            source_type="keyphrase",
            workspace_id="ws-test",
            document_id="doc-integration",
            vertical="general",
        )

        assert scored.get("keep") is True

        for field in (
            "upstream_candidate_id",
            "custom_lineage",
            "source_hash",
            "source_hash_basis",
        ):
            assert guarded[field] == original[field]
            assert scored[field] == original[field]

        assert "guard_intelligence" in scored
        assert "scorer_intelligence" in scored
        assert "strength_score" in scored
        assert candidate == original

        scorer_passed.append(scored)

    scorer_snapshot = deepcopy(scorer_passed)

    selection = select_highlight_candidates(
        workspace_id="ws-test",
        doc_id="doc-integration",
        article_text=article,
        phrase_candidates=scorer_passed,
        resolved_targets=None,
        vertical="general",
    )

    assert selection["ok"] is True
    assert scorer_passed == scorer_snapshot

    return article, scorer_passed, selection


def test_pipeline2_metadata_and_canonical_handoff():
    article, scorer_passed, selection = (
        _run_pipeline2_contract()
    )

    selected = selection["selected"]
    canonical = selection[
        "all_selected_phrase_candidates"
    ]

    assert len(selected) == len(PHRASES)
    assert len(canonical) == len(PHRASES)

    assert canonical == selected
    assert canonical is not selected
    assert selected is selection["candidates"]

    source_by_id = {
        item["upstream_candidate_id"]: item
        for item in scorer_passed
    }

    for selected_item, canonical_item in zip(
        selected, canonical
    ):
        assert selected_item is not canonical_item

        original = source_by_id[
            canonical_item["upstream_candidate_id"]
        ]

        for field in (
            "custom_lineage",
            "source_hash",
            "source_hash_basis",
            "guard_intelligence",
            "scorer_intelligence",
            "strength_score",
        ):
            assert canonical_item[field] == original[field]

        assert (
            canonical_item["custom_lineage"]
            is not selected_item["custom_lineage"]
        )


def test_legacy_density_cannot_modify_canonical_output():
    article, scorer_passed, selection = (
        _run_pipeline2_contract()
    )

    selected = selection["selected"]
    canonical = selection[
        "all_selected_phrase_candidates"
    ]

    canonical_before = deepcopy(canonical)
    scorer_before = deepcopy(scorer_passed)

    density_result = apply_highlight_density(
        article_text=article,
        selected_candidates=selected,
    )

    assert isinstance(density_result, dict)
    assert "final_highlights" in density_result

    assert canonical == canonical_before
    assert scorer_passed == scorer_before
    assert len(canonical) == len(PHRASES)

    assert {
        item["upstream_candidate_id"]
        for item in canonical
    } == {
        item["upstream_candidate_id"]
        for item in scorer_before
    }

    selected[0]["custom_lineage"]["nested"][
        "index"
    ] = -999

    assert canonical == canonical_before
    assert scorer_passed == scorer_before

def test_coordinator_canonical_output_contract(monkeypatch, tmp_path):
    import importlib

    coordinator = importlib.import_module(
        "backend.server.pipelines.upload_document."
        "uploaded_document_to_highlight_pipeline.coordinator"
    )

    article = ". ".join(PHRASES) + "."
    article_hash = sha256(article.encode("utf-8")).hexdigest()

    upstream = []
    for index, phrase in enumerate(PHRASES):
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
                "origin": "coordinator-contract-test",
                "nested": {"index": index},
            },
        })

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

    # Redirect the coordinator diagnostic report to pytest storage.
    monkeypatch.setattr(
        coordinator,
        "Path",
        lambda ignored: (
            tmp_path / "a" / "b" / "c" / "coordinator.py"
        ),
    )

    result = coordinator.run_uploaded_document_to_highlight_pipeline(
        workspace_id="ws-test",
        document_id="doc-integration",
        extraction_result={
            "text": article,
            "title": "Canonical Phrase Contract Test",
        },
    )

    assert result["ok"] is True

    canonical = result["all_selected_phrase_candidates"]
    selection = result["highlight_selection"]
    nested_canonical = selection["all_selected_phrase_candidates"]
    legacy = selection["selected"]

    assert result["all_selected_phrase_candidate_count"] == len(PHRASES)
    assert len(canonical) == len(PHRASES)
    assert len(legacy) == len(PHRASES)

    assert canonical == nested_canonical
    assert canonical == legacy

    assert canonical is not nested_canonical
    assert canonical is not legacy

    # Ranking and ordering must remain exactly as selected.
    assert [
        item["upstream_candidate_id"] for item in canonical
    ] == [
        item["upstream_candidate_id"] for item in legacy
    ]

    originals = {
        item["upstream_candidate_id"]: item
        for item in upstream
    }

    assert {
        item["upstream_candidate_id"] for item in canonical
    } == set(originals)

    for item in canonical:
        original = originals[item["upstream_candidate_id"]]

        for field in (
            "source_hash",
            "source_hash_basis",
            "source_span",
            "custom_lineage",
        ):
            assert item[field] == original[field]

        assert "guard_intelligence" in item
        assert "scorer_intelligence" in item
        assert "strength_score" in item

    canonical_snapshot = deepcopy(canonical)
    nested_snapshot = deepcopy(nested_canonical)

    # Real legacy Density must not truncate or mutate canonical output.
    density_result = apply_highlight_density(
        article_text=article,
        selected_candidates=legacy,
    )
    assert isinstance(density_result, dict)
    assert "final_highlights" in density_result
    assert canonical == canonical_snapshot
    assert nested_canonical == nested_snapshot
    assert len(canonical) == len(PHRASES)
    assert result['all_selected_phrase_candidate_count'] == len(PHRASES)

    # Legacy mutations must not reach the canonical output.
    legacy[0]["custom_lineage"]["nested"]["index"] = -111
    legacy[0]["display_status"] = "painted"

    assert canonical == canonical_snapshot
    assert nested_canonical == nested_snapshot

    # Nested canonical mutations must not reach the top-level output.
    nested_canonical[0]["custom_lineage"]["nested"]["index"] = -222

    assert canonical == canonical_snapshot

    # The top-level output must also be independently mutable.
    canonical[0]["custom_lineage"]["nested"]["index"] = -333

    assert (
        nested_canonical[0]["custom_lineage"]["nested"]["index"]
        == -222
    )

    diagnostic_file = (
        tmp_path / "data" / "reports"
        / "uploaded_document_phrase_flow_diagnostics.jsonl"
    )
    assert diagnostic_file.is_file()
