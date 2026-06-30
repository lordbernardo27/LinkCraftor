from backend.server.stores.semantic_article_reader import read_semantic_article_v1
from backend.server.stores.semantic_context_builder import build_semantic_context_v1
from backend.server.stores.entity_concept_extraction import extract_entities_and_concepts_v1
from backend.server.stores.phrase_neighborhood_intelligence import build_phrase_neighborhoods_v1
from backend.server.stores.topic_intent_intelligence import build_topic_intent_v1
from backend.server.stores.section_evidence_builder import build_section_evidence_v1
from backend.server.stores.semantic_relationship_graph import build_semantic_relationship_graph_v1
from backend.server.stores.semantic_learning_export import build_semantic_learning_export_v1
from backend.server.stores.semantic_article_certification import (
    certify_semantic_article_pipeline_v1,
    explain_semantic_article_certification_v1,
    save_semantic_article_certification_v1,
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

print("=== PHASE 4.6.9 — END-TO-END SEMANTIC ARTICLE CERTIFICATION ===")

capabilities = explain_semantic_article_certification_v1()
print(json.dumps(capabilities, indent=2))

reading_model = read_semantic_article_v1(
    sample_article,
    article_id="article_phase_469_certification_test",
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

learning_pack = build_semantic_learning_export_v1(graph_model)

certification_model = certify_semantic_article_pipeline_v1(
    reading_model,
    context_model,
    extraction_model,
    neighborhood_model,
    intent_model,
    evidence_model,
    graph_model,
    learning_pack,
)

out = Path("backend/server/data/semantic_article_reader/phase_4_6_9_semantic_article_certification.json")
saved = save_semantic_article_certification_v1(certification_model, out)

assert certification_model["schema_version"] == "semantic_article_certification_v1"
assert certification_model["phase"] == "4.6.9"
assert certification_model["status"] == "PASSED"
assert certification_model["failed_checks"] == []
assert certification_model["metadata"]["failed_check_count"] == 0
assert certification_model["metadata"]["passed_check_count"] == certification_model["metadata"]["check_count"]

assert certification_model["certified_pipeline"] == [
    "4.6.1",
    "4.6.2A",
    "4.6.3C",
    "4.6.4B",
    "4.6.5B",
    "4.6.6A",
    "4.6.7A",
    "4.6.8A",
]

assert certification_model["final_learning_pack"]["learning_pack_id"]
assert certification_model["final_learning_pack"]["overall_signature"]
assert certification_model["final_learning_pack"]["semantic_richness_score"] >= 0

assert "blue highlights" in certification_model["boundary_rule"]
assert "yellow highlights" in certification_model["boundary_rule"]
assert out.exists()

freeze_marker = {
    "phase": "4.6.9",
    "name": "End-to-End Semantic Article Certification",
    "status": "FROZEN",
    "semantic_article_intelligence_status": "FULLY_CERTIFIED",
    "output_file": str(out),
    "certified_pipeline": certification_model["certified_pipeline"],
    "certified_capabilities": capabilities["does"],
    "certified_boundaries": capabilities["does_not"],
    "boundary_rule": certification_model["boundary_rule"],
    "metadata": certification_model["metadata"],
    "final_learning_pack": certification_model["final_learning_pack"],
}

freeze_path = Path("backend/server/data/semantic_article_reader/PHASE_4_6_9_FREEZE_MARKER.json")
freeze_path.write_text(json.dumps(freeze_marker, indent=2), encoding="utf-8")

print("\n=== FINAL CERTIFICATION RESULT ===")
print(json.dumps({
    "status": certification_model["status"],
    "phase": "4.6.9",
    "semantic_article_intelligence_status": "FULLY_CERTIFIED",
    "certification_id": certification_model["certification_id"],
    "certified_pipeline": certification_model["certified_pipeline"],
    "check_count": certification_model["metadata"]["check_count"],
    "passed_check_count": certification_model["metadata"]["passed_check_count"],
    "failed_check_count": certification_model["metadata"]["failed_check_count"],
    "final_learning_pack": certification_model["final_learning_pack"],
    "certification_model": str(out),
    "freeze_marker": str(freeze_path),
}, indent=2))
