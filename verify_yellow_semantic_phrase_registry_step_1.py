from backend.server.stores.yellow_semantic_phrase_registry import (
    build_yellow_semantic_phrase_registry_v1,
    explain_yellow_semantic_phrase_registry_v1,
    save_yellow_semantic_phrase_registry_v1,
    transition_yellow_phrase_state_v1,
)
import json
from pathlib import Path

print("=== REALIGNMENT STEP 1D — YELLOW SEMANTIC PHRASE REGISTRY REFINEMENT VERIFICATION ===")

capabilities = explain_yellow_semantic_phrase_registry_v1()
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

registry = build_yellow_semantic_phrase_registry_v1(editor_document)

out = Path("backend/server/data/semantic_linking_execution/yellow_semantic_phrase_registry_test.json")
saved = save_yellow_semantic_phrase_registry_v1(editor_document, out)

assert registry["schema_version"] == "yellow_semantic_phrase_registry_v1"
assert registry["phase"] == "semantic_linking_execution.step_1"
assert registry["patch"] == "step_1D"
assert registry["yellow_semantic_phrases"]
assert registry["metadata"]["yellow_phrase_count"] > 0
assert registry["metadata"]["span_policy"] == "longest_non_overlapping_semantic_span"
assert registry["metadata"]["processing_lifecycle_enabled"] is True

phrases = registry["yellow_semantic_phrases"]
normalized = [p["normalized_text"] for p in phrases]

# Longest-span checks:
# blood pressure monitoring should suppress embedded blood pressure in sentence 2.
assert "blood pressure monitoring" in normalized

# high blood pressure should suppress embedded blood pressure in sentence 3.
assert "high blood pressure" in normalized

for phrase in phrases:
    assert phrase["highlight_type"] == "yellow_candidate"
    assert phrase["resolver_lane"] == "semantic_yellow"
    assert phrase["status"] == "detected"
    assert phrase["processing_state"]["current_state"] == "detected"
    assert phrase["processing_state"]["next_expected_engine"] == "semantic_reasoning_engine"
    assert phrase["routing"]["send_to_reasoning_engine"] is True
    assert phrase["routing"]["send_to_blue_resolver"] is False
    assert phrase["routing"]["send_to_yellow_resolver"] is False
    assert phrase["span_policy"]["policy"] == "longest_non_overlapping_semantic_span"
    assert "phrase_id" in phrase
    assert "surface_text" in phrase
    assert "normalized_text" in phrase
    assert "editor_location" in phrase
    assert "surrounding_context" in phrase
    assert "semantic_identity" in phrase
    assert phrase["semantic_identity"]["identity_status"] == "pending"
    assert phrase["semantic_identity"]["canonical_concept"] is None
    assert phrase["semantic_identity"]["semantic_object_id"] is None

test_phrase = phrases[0]
reasoned = transition_yellow_phrase_state_v1(
    test_phrase,
    "reasoned",
    source="semantic_reasoning_engine",
    note="Semantic bridge found.",
)

assert reasoned["status"] == "reasoned"
assert reasoned["processing_state"]["current_state"] == "reasoned"
assert reasoned["processing_state"]["next_expected_engine"] == "semantic_target_discovery"
assert len(reasoned["processing_state"]["history"]) == 2

assert any(p["normalized_text"] == "hypertension" for p in phrases)
assert out.exists()

freeze_marker = {
    "realignment_step": 1,
    "patch": "step_1D",
    "name": "Yellow Semantic Phrase Registry",
    "status": "FROZEN",
    "semantic_identity_placeholder": True,
    "output_file": str(out),
    "metadata": registry["metadata"],
    "boundary_rule": registry["boundary_rule"],
}

freeze_path = Path("backend/server/data/semantic_linking_execution/YELLOW_SEMANTIC_PHRASE_REGISTRY_STEP_1D_FREEZE_MARKER.json")
freeze_path.write_text(json.dumps(freeze_marker, indent=2), encoding="utf-8")

print("\n=== VERIFICATION RESULT ===")
print(json.dumps({
    "status": "PASSED",
    "step": "Yellow Semantic Phrase Registry",
    "patch": "step_1D",
    "yellow_phrase_count": registry["metadata"]["yellow_phrase_count"],
    "phrases": [
        {
            "phrase_id": p["phrase_id"],
            "surface_text": p["surface_text"],
            "normalized_text": p["normalized_text"],
            "status": p["status"],
            "processing_state": p["processing_state"],
            "span_policy": p["span_policy"],
            "semantic_identity": p["semantic_identity"],
        }
        for p in phrases
    ],
    "state_transition_sample": {
        "phrase_id": reasoned["phrase_id"],
        "status": reasoned["status"],
        "next_expected_engine": reasoned["processing_state"]["next_expected_engine"],
        "history_count": len(reasoned["processing_state"]["history"]),
    },
    "output": str(out),
    "freeze_marker": str(freeze_path),
}, indent=2))
