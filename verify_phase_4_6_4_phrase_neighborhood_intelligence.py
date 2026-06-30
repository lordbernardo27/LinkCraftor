from backend.server.stores.semantic_article_reader import read_semantic_article_v1
from backend.server.stores.semantic_context_builder import build_semantic_context_v1
from backend.server.stores.entity_concept_extraction import extract_entities_and_concepts_v1
from backend.server.stores.phrase_neighborhood_intelligence import (
    build_phrase_neighborhoods_v1,
    explain_phrase_neighborhood_intelligence_v1,
    save_phrase_neighborhoods_v1,
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
""".strip()

print("=== PHASE 4.6.4A — PHRASE NEIGHBORHOOD RELATIONSHIP CLASSIFIER VERIFICATION ===")

capabilities = explain_phrase_neighborhood_intelligence_v1()
print(json.dumps(capabilities, indent=2))

reading_model = read_semantic_article_v1(
    sample_article,
    article_id="article_phase_464_test",
    source_url="https://example.com/high-blood-pressure-pregnancy",
    title="High Blood Pressure During Pregnancy",
)

context_model = build_semantic_context_v1(reading_model, context_radius=2)

extraction_model = extract_entities_and_concepts_v1(
    context_model,
    min_frequency=1,
    max_semantic_objects=40,
)

assert extraction_model["phase"] == "4.6.3"
assert extraction_model["patch"] == "4.6.3C"

neighborhood_model = build_phrase_neighborhoods_v1(extraction_model)

out = Path("backend/server/data/semantic_article_reader/phase_4_6_4_phrase_neighborhood_model.json")
saved = save_phrase_neighborhoods_v1(extraction_model, out)

assert neighborhood_model["schema_version"] == "phrase_neighborhood_intelligence_v1"
assert neighborhood_model["phase"] == "4.6.4"
assert neighborhood_model["patch"] == "4.6.4B"
assert neighborhood_model["source_phase"] == "4.6.3"
assert neighborhood_model["source_patch"] == "4.6.3C"
assert neighborhood_model["article"]["article_id"] == "article_phase_464_test"

assert neighborhood_model["metadata"]["semantic_object_count"] == extraction_model["metadata"]["semantic_object_count"]
assert neighborhood_model["metadata"]["mention_count"] == extraction_model["metadata"]["mention_count"]
assert neighborhood_model["metadata"]["neighborhood_count"] > 0
assert neighborhood_model["metadata"]["object_neighborhood_count"] > 0
assert "relationship_type_counts" in neighborhood_model["metadata"]
assert "relationship_family_counts" in neighborhood_model["metadata"]

for neighborhood in neighborhood_model["neighborhoods"]:
    assert "neighborhood_id" in neighborhood
    assert "left_object_id" in neighborhood
    assert "right_object_id" in neighborhood
    assert "left_text" in neighborhood
    assert "right_text" in neighborhood
    assert "relationship_type" in neighborhood
    assert "relationship_family" in neighborhood
    assert "relationship_confidence" in neighborhood
    assert "classification_basis" in neighborhood
    assert "cooccurrence_count" in neighborhood
    assert "neighborhood_strength" in neighborhood
    assert "unit_type_counts" in neighborhood
    assert "evidence" in neighborhood

for object_neighborhood in neighborhood_model["object_neighborhoods"]:
    assert "semantic_object_id" in object_neighborhood
    assert "canonical_text" in object_neighborhood
    assert "neighbor_count" in object_neighborhood
    assert "neighbors" in object_neighborhood

relationship_types = set(neighborhood_model["metadata"]["relationship_type_counts"].keys())

assert relationship_types
assert any(
    rel in relationship_types
    for rel in {
        "peer_symptoms",
        "related_conditions",
        "condition_context",
        "monitoring_context",
        "measurement_context",
        "measurement_condition_association",
    }
)

assert "blue highlights" in neighborhood_model["boundary_rule"]
assert "yellow highlights" in neighborhood_model["boundary_rule"]
assert out.exists()

freeze_marker = {
    "phase": "4.6.4",
    "patch": "4.6.4B",
    "name": "Phrase Neighborhood Intelligence",
    "status": "FROZEN",
    "output_file": str(out),
    "certified_capabilities": capabilities["does"],
    "certified_boundaries": capabilities["does_not"],
    "boundary_rule": neighborhood_model["boundary_rule"],
    "metadata": neighborhood_model["metadata"],
}

freeze_path = Path("backend/server/data/semantic_article_reader/PHASE_4_6_4_FREEZE_MARKER.json")
freeze_path.write_text(json.dumps(freeze_marker, indent=2), encoding="utf-8")

print("\n=== CERTIFICATION RESULT ===")
print(json.dumps({
    "status": "PASSED",
    "phase": "4.6.4",
    "patch": "4.6.4B",
    "domain_label": neighborhood_model["domain_label"],
    "semantic_objects": neighborhood_model["metadata"]["semantic_object_count"],
    "mentions": neighborhood_model["metadata"]["mention_count"],
    "neighborhoods": neighborhood_model["metadata"]["neighborhood_count"],
    "object_neighborhoods": neighborhood_model["metadata"]["object_neighborhood_count"],
    "relationship_type_counts": neighborhood_model["metadata"]["relationship_type_counts"],
    "relationship_family_counts": neighborhood_model["metadata"]["relationship_family_counts"],
    "top_neighborhoods": neighborhood_model["neighborhoods"][:10],
    "neighborhood_model": str(out),
    "freeze_marker": str(freeze_path),
}, indent=2))
