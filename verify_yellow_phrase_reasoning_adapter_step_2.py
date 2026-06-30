from backend.server.stores.yellow_semantic_phrase_registry import build_yellow_semantic_phrase_registry_v1
from backend.server.stores.yellow_phrase_reasoning_adapter import (
    adapt_yellow_phrase_registry_to_existing_reasoning_v1,
    explain_yellow_phrase_reasoning_adapter_v1,
    save_yellow_phrase_reasoning_adapter_v1,
)
from pathlib import Path
import json

print("=== REALIGNMENT STEP 2 ADAPTER — EXISTING REASONING ENGINE CONNECTION VERIFICATION ===")

capabilities = explain_yellow_phrase_reasoning_adapter_v1()
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

adapter_model = adapt_yellow_phrase_registry_to_existing_reasoning_v1(phrase_registry)

out = Path("backend/server/data/semantic_linking_execution/yellow_phrase_reasoning_adapter_test.json")
saved = save_yellow_phrase_reasoning_adapter_v1(phrase_registry, out)

assert adapter_model["schema_version"] == "yellow_phrase_reasoning_adapter_model_v1"
assert adapter_model["phase"] == "semantic_linking_execution.step_2"
assert adapter_model["patch"] == "step_2_adapter_A"
assert adapter_model["metadata"]["uses_existing_reasoning_engine"] is True
assert adapter_model["metadata"]["creates_new_reasoning_engine"] is False
assert adapter_model["adapted_yellow_phrases"]

for phrase in adapter_model["adapted_yellow_phrases"]:
    assert "semantic_reasoning_adapter" in phrase
    adapter = phrase["semantic_reasoning_adapter"]
    assert adapter["uses_existing_reasoning_engine"] is True
    assert adapter["creates_new_reasoning_engine"] is False
    assert "existing_reasoning_calls" in adapter
    assert adapter["existing_reasoning_calls"]

assert out.exists()

freeze_marker = {
    "realignment_step": 2,
    "patch": "step_2_adapter_A",
    "name": "Yellow Phrase Reasoning Adapter",
    "status": "PASSED",
    "output_file": str(out),
    "metadata": adapter_model["metadata"],
    "boundary_rule": adapter_model["boundary_rule"],
}

freeze_path = Path("backend/server/data/semantic_linking_execution/YELLOW_PHRASE_REASONING_ADAPTER_STEP_2A_MARKER.json")
freeze_path.write_text(json.dumps(freeze_marker, indent=2), encoding="utf-8")

print("\n=== VERIFICATION RESULT ===")
print(json.dumps({
    "status": "PASSED",
    "step": "Yellow Phrase Reasoning Adapter",
    "patch": "step_2_adapter_A",
    "metadata": adapter_model["metadata"],
    "sample_phrase": {
        "phrase_id": adapter_model["adapted_yellow_phrases"][0]["phrase_id"],
        "surface_text": adapter_model["adapted_yellow_phrases"][0]["surface_text"],
        "state": adapter_model["adapted_yellow_phrases"][0]["processing_state"]["current_state"],
        "adapter": adapter_model["adapted_yellow_phrases"][0]["semantic_reasoning_adapter"],
    },
    "output": str(out),
    "freeze_marker": str(freeze_path),
}, indent=2, default=str))
