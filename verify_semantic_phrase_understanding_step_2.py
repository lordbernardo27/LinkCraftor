from backend.server.stores.yellow_semantic_phrase_registry import build_yellow_semantic_phrase_registry_v1
from backend.server.stores.semantic_phrase_understanding import (
    understand_yellow_semantic_phrase_registry_v1,
    explain_semantic_phrase_understanding_v1,
    save_semantic_phrase_understanding_v1,
)
from pathlib import Path
import json

print("=== REALIGNMENT STEP 2 — SEMANTIC PHRASE UNDERSTANDING VERIFICATION ===")

capabilities = explain_semantic_phrase_understanding_v1()
print(json.dumps(capabilities, indent=2))

editor_document = {
    "workspace_id": "ws_whattoexpect_com",
    "document_id": "doc_editor_test_001",
    "title": "Pregnancy Blood Pressure Draft",
    "text": (
        "Hypertension can affect pregnancy. "
        "Blood pressure monitoring may help track changes. "
        "Morning sickness is different from high blood pressure."
    ),
}

phrase_registry = build_yellow_semantic_phrase_registry_v1(editor_document)

assert phrase_registry["patch"] == "step_1D"

model = understand_yellow_semantic_phrase_registry_v1(phrase_registry)

out = Path("backend/server/data/semantic_linking_execution/semantic_phrase_understanding_test.json")
saved = save_semantic_phrase_understanding_v1(phrase_registry, out)

assert model["schema_version"] == "semantic_phrase_understanding_model_v1"
assert model["phase"] == "semantic_linking_execution.step_2"
assert model["patch"] == "step_2_semantic_phrase_understanding_C"
assert model["metadata"]["calls_semantic_linking_reasoning_engine"] is False
assert model["metadata"]["creates_new_reasoning_engine"] is False
assert model["metadata"]["active_target_set_queried"] is False
assert model["metadata"]["understood_phrase_count"] > 0

for phrase in model["understood_yellow_phrases"]:
    assert "semantic_understanding" in phrase
    assert "semantic_identity" in phrase

    if phrase["semantic_understanding"]["understanding_status"] == "understood":
        assert phrase["semantic_understanding"]["semantic_object_id"]
        assert phrase["semantic_understanding"]["canonical_concept"]
        assert phrase["semantic_understanding"]["search_candidates"]
        assert phrase["semantic_understanding"]["semantic_fingerprint"]
        assert phrase["semantic_identity"]["semantic_fingerprint"]
        assert phrase["semantic_identity"]["identity_status"] == "bound"
        for candidate in phrase["semantic_understanding"]["search_candidates"]:
            assert "search_candidate_id" in candidate
            assert "search_text" in candidate
            assert "semantic_fingerprint" in candidate
            assert "priority" in candidate
            assert "search_weight" in candidate
            assert "search_mode" in candidate
        assert phrase["routing"]["requires_target_discovery"] is True
        assert phrase["processing_state"]["current_state"] == "reasoned"
        assert phrase["processing_state"]["next_expected_engine"] == "semantic_target_discovery"

assert any(
    phrase["normalized_text"] == "hypertension"
    and phrase["semantic_understanding"]["canonical_concept"] == "high blood pressure"
    for phrase in model["understood_yellow_phrases"]
)

assert out.exists()

freeze_marker = {
    "realignment_step": 2,
    "patch": "step_2_semantic_phrase_understanding_C",
    "name": "Semantic Phrase Understanding",
    "status": "FROZEN",
    "output_file": str(out),
    "metadata": model["metadata"],
    "boundary_rule": model["boundary_rule"],
}

freeze_path = Path("backend/server/data/semantic_linking_execution/SEMANTIC_PHRASE_UNDERSTANDING_STEP_2C_FREEZE_MARKER.json")
freeze_path.write_text(json.dumps(freeze_marker, indent=2), encoding="utf-8")

print("\n=== VERIFICATION RESULT ===")
print(json.dumps({
    "status": "PASSED",
    "step": "Semantic Phrase Understanding",
    "patch": "step_2_semantic_phrase_understanding_C",
    "metadata": model["metadata"],
    "understood_phrases": [
        {
            "phrase_id": p["phrase_id"],
            "surface_text": p["surface_text"],
            "normalized_text": p["normalized_text"],
            "status": p["status"],
            "semantic_understanding": p["semantic_understanding"],
            "semantic_identity": p["semantic_identity"],
            "next_expected_engine": p["processing_state"]["next_expected_engine"],
        }
        for p in model["understood_yellow_phrases"]
    ],
    "output": str(out),
    "freeze_marker": str(freeze_path),
}, indent=2))
