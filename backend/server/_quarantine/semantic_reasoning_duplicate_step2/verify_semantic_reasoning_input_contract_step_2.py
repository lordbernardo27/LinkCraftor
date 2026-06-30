from backend.server.stores.yellow_semantic_phrase_registry import build_yellow_semantic_phrase_registry_v1
from backend.server.stores.semantic_reasoning_input_contract import (
    reason_yellow_semantic_phrase_registry_v1,
    explain_semantic_reasoning_input_contract_v1,
    save_semantic_reasoning_input_contract_v1,
)
import json
from pathlib import Path

print("=== REALIGNMENT STEP 2A — SEMANTIC REASONING ENGINE INPUT CONTRACT VERIFICATION ===")

capabilities = explain_semantic_reasoning_input_contract_v1()
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

reasoning_model = reason_yellow_semantic_phrase_registry_v1(phrase_registry)

out = Path("backend/server/data/semantic_linking_execution/semantic_reasoning_input_contract_test.json")
saved = save_semantic_reasoning_input_contract_v1(phrase_registry, out)

assert reasoning_model["schema_version"] == "semantic_reasoning_input_contract_v1"
assert reasoning_model["phase"] == "semantic_linking_execution.step_2"
assert reasoning_model["patch"] == "step_2G"
assert reasoning_model["source_registry"]["patch"] == "step_1D"
assert reasoning_model["reasoned_yellow_phrases"]
assert reasoning_model["metadata"]["input_phrase_count"] == phrase_registry["metadata"]["yellow_phrase_count"]
assert reasoning_model["metadata"]["reasoned_phrase_count"] == phrase_registry["metadata"]["yellow_phrase_count"]
assert reasoning_model["metadata"]["bound_identity_count"] > 0

for phrase in reasoning_model["reasoned_yellow_phrases"]:
    assert "semantic_reasoning" in phrase
    sr = phrase["semantic_reasoning"]
    assert "semantic_identity" in sr
    assert "semantic_interpretation" in sr
    assert "workspace_snapshot" in sr
    assert "confidence_breakdown" in sr
    assert "reasoning_result" in sr
    assert phrase["processing_state"]["current_state"] in {"reasoned", "rejected"}

    if sr["semantic_identity"]["identity_status"] == "bound":
        assert sr["semantic_identity"]["canonical_concept"]
        assert sr["semantic_identity"]["semantic_object_id"]
        assert sr["semantic_identity"]["identity_confidence"] > 0
        assert sr["semantic_interpretation"]["interpretation_status"] == "interpreted"
        assert sr["semantic_interpretation"]["bridge_type"]
        assert sr["semantic_interpretation"]["bridge_path"]
        assert sr["semantic_interpretation"]["evidence"]
        assert sr["workspace_snapshot"]["reasoning_revision"] == "semantic_reasoning_step_2B"
        assert sr["confidence_breakdown"]["overall_confidence"] > 0
        assert sr["reasoning_result"]["semantic_match_found"] is True
        assert sr["reasoning_result"]["eligible_for_target_discovery"] is True
        assert sr["reasoning_result"]["recommended_target_topics"]
        for topic in sr["reasoning_result"]["recommended_target_topics"]:
            assert "topic_id" in topic
            assert "canonical_concept" in topic
            assert "relationship" in topic
            assert "source_phrase" in topic
            assert "confidence" in topic
            assert "target_search_strategy" in topic
            assert "priority" in topic["target_search_strategy"]
            assert "match_mode" in topic["target_search_strategy"]
            assert "target_search_plan" in topic
            assert isinstance(topic["target_search_plan"], list)
            assert topic["target_search_plan"]
            assert any(
                item["provider"]["provider_id"] == "provider_active_target_set"
                for item in topic["target_search_plan"]
            )
            for plan_item in topic["target_search_plan"]:
                assert "provider" in plan_item
                assert "provider_id" in plan_item["provider"]
                assert "provider_type" in plan_item["provider"]
                assert "provider_name" in plan_item["provider"]
                assert "priority" in plan_item
                assert "match_mode" in plan_item
                assert "required" in plan_item
            assert "search_intent" in topic
            assert topic["search_intent"]["goal"] == "discover_best_target_url"
            assert topic["search_intent"]["expected_output"] == "candidate_urls"
            assert topic["search_intent"]["minimum_candidates"] >= 1
            assert topic["search_intent"]["maximum_candidates"] >= topic["search_intent"]["minimum_candidates"]
        assert phrase["routing"]["requires_target_discovery"] is True
        assert phrase["processing_state"]["next_expected_engine"] == "semantic_target_discovery"

assert any(
    phrase["normalized_text"] == "hypertension"
    and phrase["semantic_reasoning"]["semantic_identity"]["canonical_concept"] == "high blood pressure"
    for phrase in reasoning_model["reasoned_yellow_phrases"]
)

assert "target discovery" in reasoning_model["boundary_rule"].lower()
assert out.exists()

freeze_marker = {
    "realignment_step": 2,
    "patch": "step_2G",
    "name": "Semantic Reasoning Engine Input Contract",
    "status": "FROZEN",
    "output_file": str(out),
    "metadata": reasoning_model["metadata"],
    "boundary_rule": reasoning_model["boundary_rule"],
}

freeze_path = Path("backend/server/data/semantic_linking_execution/SEMANTIC_REASONING_INPUT_CONTRACT_STEP_2G_FREEZE_MARKER.json")
freeze_path.write_text(json.dumps(freeze_marker, indent=2), encoding="utf-8")

print("\n=== VERIFICATION RESULT ===")
print(json.dumps({
    "status": "PASSED",
    "step": "Semantic Reasoning Engine Input Contract",
    "patch": "step_2G",
    "metadata": reasoning_model["metadata"],
    "reasoned_phrases": [
        {
            "phrase_id": p["phrase_id"],
            "surface_text": p["surface_text"],
            "normalized_text": p["normalized_text"],
            "status": p["status"],
            "semantic_reasoning": p["semantic_reasoning"],
            "next_expected_engine": p["processing_state"]["next_expected_engine"],
        }
        for p in reasoning_model["reasoned_yellow_phrases"]
    ],
    "output": str(out),
    "freeze_marker": str(freeze_path),
}, indent=2))
