from backend.server.stores.semantic_article_reader import read_semantic_article_v1
from backend.server.stores.semantic_context_builder import build_semantic_context_v1
from backend.server.stores.entity_concept_extraction import extract_entities_and_concepts_v1
from backend.server.stores.phrase_neighborhood_intelligence import build_phrase_neighborhoods_v1
from backend.server.stores.topic_intent_intelligence import build_topic_intent_v1
from backend.server.stores.section_evidence_builder import build_section_evidence_v1
from backend.server.stores.semantic_relationship_graph import build_semantic_relationship_graph_v1
from backend.server.stores.semantic_learning_export import (
    build_semantic_learning_export_v1,
    explain_semantic_learning_export_v1,
    save_semantic_learning_export_v1,
)
import json
from pathlib import Path

sample_article = """
# High Blood Pressure During Pregnancy

High blood pressure during pregnancy can increase health risks. Hypertension is another term used for high blood pressure.

## Symptoms and monitoring

Some people may notice headaches or swelling. Blood pressure monitoring helps track changes during pregnancy.

## Related conditions

Gestational hypertension and preeclampsia are pregnancy-related blood pressure conditions.

## Prevention

Regular monitoring and early care may help reduce the risk of complications.
""".strip()

print("=== PHASE 4.6.8 — SEMANTIC LEARNING EXPORT VERIFICATION ===")

capabilities = explain_semantic_learning_export_v1()
print(json.dumps(capabilities, indent=2))

reading_model = read_semantic_article_v1(
    sample_article,
    article_id="article_phase_468_test",
    source_url="https://example.com/high-blood-pressure-pregnancy",
    title="High Blood Pressure During Pregnancy",
)

context_model = build_semantic_context_v1(reading_model, context_radius=2)

extraction_model = extract_entities_and_concepts_v1(
    context_model,
    min_frequency=1,
    max_semantic_objects=40,
)

neighborhood_model = build_phrase_neighborhoods_v1(extraction_model)

intent_model = build_topic_intent_v1(
    context_model,
    extraction_model,
    neighborhood_model,
)

evidence_model = build_section_evidence_v1(
    context_model,
    extraction_model,
    neighborhood_model,
    intent_model,
)

graph_model = build_semantic_relationship_graph_v1(evidence_model)

assert context_model["patch"] == "4.6.2A"
assert extraction_model["patch"] == "4.6.3C"
assert neighborhood_model["patch"] == "4.6.4B"
assert intent_model["patch"] == "4.6.5B"
assert evidence_model["patch"] == "4.6.6A"
assert graph_model["patch"] == "4.6.7A"

learning_pack = build_semantic_learning_export_v1(graph_model)

out = Path("backend/server/data/semantic_article_reader/phase_4_6_8_semantic_learning_pack.json")
saved = save_semantic_learning_export_v1(graph_model, out)

assert learning_pack["schema_version"] == "semantic_learning_export_v1"
assert learning_pack["phase"] == "4.6.8"
assert learning_pack["patch"] == "4.6.8A"
assert "learning_fingerprint" in learning_pack
assert "learning_statistics" in learning_pack
assert learning_pack["article"]["article_id"] == "article_phase_468_test"

assert learning_pack["learning_pack_id"]
assert learning_pack["source_graph"]["patch"] == "4.6.7A"
assert learning_pack["source_graph"]["graph_lineage"]
assert learning_pack["canonical_concepts"]
assert learning_pack["learned_relationships"]
assert learning_pack["intent_patterns"]
assert learning_pack["section_evidence_summaries"]
assert learning_pack["learning_signals"]
assert learning_pack["learning_fingerprint"]["overall_signature"]
assert learning_pack["learning_statistics"]["semantic_richness_score"] >= 0

assert learning_pack["export_contract"]["consumer"] == "Semantic Workspace Learner"
assert learning_pack["export_contract"]["contract_type"] == "compiled_semantic_learning_pack"
assert learning_pack["export_contract"]["graph_internal_details_hidden"] is True
assert learning_pack["export_contract"]["memory_write_performed"] is False
assert learning_pack["export_contract"]["resolver_decision_performed"] is False

assert learning_pack["metadata"]["canonical_concept_count"] > 0
assert learning_pack["metadata"]["learned_relationship_count"] > 0
assert learning_pack["metadata"]["intent_pattern_count"] > 0
assert learning_pack["metadata"]["section_evidence_summary_count"] > 0

assert "blue highlights" in learning_pack["boundary_rule"]
assert "yellow highlights" in learning_pack["boundary_rule"]
assert out.exists()

freeze_marker = {
    "phase": "4.6.8",
    "patch": "4.6.8A",
    "name": "Semantic Learning Export",
    "status": "FROZEN",
    "output_file": str(out),
    "certified_capabilities": capabilities["does"],
    "certified_boundaries": capabilities["does_not"],
    "boundary_rule": learning_pack["boundary_rule"],
    "metadata": learning_pack["metadata"],
    "export_contract": learning_pack["export_contract"],
}

freeze_path = Path("backend/server/data/semantic_article_reader/PHASE_4_6_8_FREEZE_MARKER.json")
freeze_path.write_text(json.dumps(freeze_marker, indent=2), encoding="utf-8")

print("\n=== CERTIFICATION RESULT ===")
print(json.dumps({
    "status": "PASSED",
    "phase": "4.6.8",
    "patch": "4.6.8A",
    "patch": "4.6.8A",
    "domain_label": learning_pack["domain_label"],
    "learning_pack_id": learning_pack["learning_pack_id"],
    "canonical_concepts": learning_pack["metadata"]["canonical_concept_count"],
    "learned_relationships": learning_pack["metadata"]["learned_relationship_count"],
    "intent_patterns": learning_pack["metadata"]["intent_pattern_count"],
    "section_evidence_summaries": learning_pack["metadata"]["section_evidence_summary_count"],
    "learning_signals": learning_pack["learning_signals"],
    "learning_fingerprint": learning_pack["learning_fingerprint"],
    "learning_statistics": learning_pack["learning_statistics"],
    "export_contract": learning_pack["export_contract"],
    "learning_pack": str(out),
    "freeze_marker": str(freeze_path),
}, indent=2))
