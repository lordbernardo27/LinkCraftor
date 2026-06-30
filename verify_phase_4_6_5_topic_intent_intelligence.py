from backend.server.stores.semantic_article_reader import read_semantic_article_v1
from backend.server.stores.semantic_context_builder import build_semantic_context_v1
from backend.server.stores.entity_concept_extraction import extract_entities_and_concepts_v1
from backend.server.stores.phrase_neighborhood_intelligence import build_phrase_neighborhoods_v1
from backend.server.stores.topic_intent_intelligence import (
    build_topic_intent_v1,
    explain_topic_intent_intelligence_v1,
    save_topic_intent_v1,
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

print("=== PHASE 4.6.5A — SEMANTIC INTENT DECISION ENGINE VERIFICATION ===")

capabilities = explain_topic_intent_intelligence_v1()
print(json.dumps(capabilities, indent=2))

reading_model = read_semantic_article_v1(
    sample_article,
    article_id="article_phase_465_test",
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

assert extraction_model["phase"] == "4.6.3"
assert extraction_model["patch"] == "4.6.3C"
assert neighborhood_model["phase"] == "4.6.4"
assert neighborhood_model["patch"] == "4.6.4B"

intent_model = build_topic_intent_v1(
    context_model,
    extraction_model,
    neighborhood_model,
)

out = Path("backend/server/data/semantic_article_reader/phase_4_6_5_topic_intent_model.json")
saved = save_topic_intent_v1(
    context_model,
    extraction_model,
    neighborhood_model,
    out,
)

assert intent_model["schema_version"] == "topic_intent_intelligence_v1"
assert intent_model["phase"] == "4.6.5"
assert intent_model["patch"] == "4.6.5B"
assert intent_model["article"]["article_id"] == "article_phase_465_test"
assert intent_model["section_intents"]
assert intent_model["metadata"]["section_intent_count"] == len(context_model["section_contexts"])
assert "intent_family_counts" in intent_model["metadata"]
assert "dominant_intent_family" in intent_model
assert "article_intent" in intent_model

for section_intent in intent_model["section_intents"]:
    assert "section_intent_id" in section_intent
    assert "section_id" in section_intent
    assert section_intent["intent_scope"] == "section"
    assert "section_position" in section_intent
    assert "intent_family" in section_intent
    assert "topic_intent" in section_intent
    assert "intent_confidence" in section_intent
    assert "reader_goal" in section_intent
    assert "section_role" in section_intent
    assert "information_type" in section_intent
    assert "intent_scores" in section_intent
    assert "decision_evidence" in section_intent
    assert "semantic_objects" in section_intent
    assert "relationship_family_counts" in section_intent
    assert "relationship_type_counts" in section_intent
    assert "evidence" in section_intent

intents = {item["topic_intent"] for item in intent_model["section_intents"]}
families = {item["intent_family"] for item in intent_model["section_intents"]}

assert "symptoms_or_signs" in intents or "measurement_or_monitoring" in intents
assert "prevention" in intents
assert "related_topics" in intents
assert families

article_intent = intent_model["article_intent"]
assert article_intent["intent_scope"] == "article"
assert "article_intent" in article_intent
assert "article_intent_family" in article_intent
assert "article_purpose" in article_intent
assert "primary_reader_goal" in article_intent
assert "supporting_section_intents" in article_intent
assert len(article_intent["supporting_section_intents"]) == len(intent_model["section_intents"])

assert "blue highlights" in intent_model["boundary_rule"]
assert "yellow highlights" in intent_model["boundary_rule"]
assert out.exists()

freeze_marker = {
    "phase": "4.6.5",
    "patch": "4.6.5B",
    "name": "Universal Topic Intent Intelligence",
    "status": "FROZEN",
    "output_file": str(out),
    "certified_capabilities": capabilities["does"],
    "certified_boundaries": capabilities["does_not"],
    "boundary_rule": intent_model["boundary_rule"],
    "metadata": intent_model["metadata"],
}

freeze_path = Path("backend/server/data/semantic_article_reader/PHASE_4_6_5_FREEZE_MARKER.json")
freeze_path.write_text(json.dumps(freeze_marker, indent=2), encoding="utf-8")

print("\n=== CERTIFICATION RESULT ===")
print(json.dumps({
    "status": "PASSED",
    "phase": "4.6.5",
    "patch": "4.6.5B",
    "domain_label": intent_model["domain_label"],
    "dominant_article_intent": intent_model["dominant_article_intent"],
    "dominant_intent_family": intent_model["dominant_intent_family"],
    "article_intent": intent_model["article_intent"],
    "section_intents": [
        {
            "section_title": item["section_title"],
            "section_position": item["section_position"],
            "intent_family": item["intent_family"],
            "topic_intent": item["topic_intent"],
            "reader_goal": item["reader_goal"],
            "section_role": item["section_role"],
            "information_type": item["information_type"],
            "intent_confidence": item["intent_confidence"],
            "decision_evidence": item["decision_evidence"],
        }
        for item in intent_model["section_intents"]
    ],
    "metadata": intent_model["metadata"],
    "intent_model": str(out),
    "freeze_marker": str(freeze_path),
}, indent=2))
