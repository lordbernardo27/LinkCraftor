from backend.server.stores.semantic_article_reader import read_semantic_article_v1
from backend.server.stores.semantic_context_builder import build_semantic_context_v1
from backend.server.stores.entity_concept_extraction import (
    explain_entity_concept_extraction_v1,
    extract_entities_and_concepts_v1,
    save_entities_and_concepts_v1,
    load_semantic_vocabularies_v1,
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

print("=== PHASE 4.6.3C — UNIVERSAL SEMANTIC VOCABULARY REGISTRY VERIFICATION ===")

capabilities = explain_entity_concept_extraction_v1()
print(json.dumps(capabilities, indent=2))

vocab = load_semantic_vocabularies_v1()

assert vocab["vocab_file_count"] >= 6
assert "medical" in vocab["domains"]
assert "seo" in vocab["domains"]
assert "technology" in vocab["domains"]
assert "finance" in vocab["domains"]
assert "legal" in vocab["domains"]
assert "travel" in vocab["domains"]

reading_model = read_semantic_article_v1(
    sample_article,
    article_id="article_phase_463_test",
    source_url="https://example.com/high-blood-pressure-pregnancy",
    title="High Blood Pressure During Pregnancy",
)

assert reading_model["phase"] == "4.6.1"
assert reading_model["validation"]["valid"] is True

context_model = build_semantic_context_v1(reading_model, context_radius=2)

assert context_model["phase"] == "4.6.2"
assert context_model["patch"] == "4.6.2A"

extraction_model = extract_entities_and_concepts_v1(
    context_model,
    min_frequency=1,
    max_semantic_objects=40,
)

out = Path("backend/server/data/semantic_article_reader/phase_4_6_3_entity_concept_extraction_model.json")
saved = save_entities_and_concepts_v1(
    context_model,
    out,
    min_frequency=1,
    max_semantic_objects=40,
)

assert extraction_model["schema_version"] == "entity_concept_extraction_v1"
assert extraction_model["phase"] == "4.6.3"
assert extraction_model["patch"] == "4.6.3C"
assert extraction_model["source_phase"] == "4.6.2"
assert extraction_model["source_patch"] == "4.6.2A"
assert extraction_model["article"]["article_id"] == "article_phase_463_test"

assert extraction_model["domain_label"] == "medical"
assert extraction_model["vocabulary_registry"]["vocab_file_count"] >= 6
assert "medical" in extraction_model["vocabulary_registry"]["domains"]

bad_terms = {
    "blood", "pressure", "high", "gestational", "pregnancy-related",
    "pressure pregnancy", "hypertension high", "notice headaches swelling",
}

assert not any(term in bad_terms for term in extraction_model["dominant_terms"])

expected_terms = {
    "high blood pressure",
    "blood pressure",
    "pregnancy",
    "gestational hypertension",
    "preeclampsia",
    "blood pressure monitoring",
    "headaches",
    "swelling",
}

assert expected_terms.intersection(set(extraction_model["dominant_terms"]))

for semantic_object in extraction_model["semantic_objects"]:
    assert "semantic_object_id" in semantic_object
    assert "canonical_text" in semantic_object
    assert "category" in semantic_object
    assert "aliases" in semantic_object
    assert "extraction_confidence" in semantic_object
    assert semantic_object["normalization_source"] == "external_semantic_vocab_registry"

for mention in extraction_model["mentions"]:
    assert "context_fingerprint" in mention["evidence"]
    assert mention["evidence"]["normalization_source"] == "external_semantic_vocab_registry"

assert out.exists()

freeze_marker = {
    "phase": "4.6.3",
    "patch": "4.6.3C",
    "name": "Entity & Concept Extraction",
    "status": "FROZEN",
    "output_file": str(out),
    "certified_capabilities": capabilities["does"],
    "certified_boundaries": capabilities["does_not"],
    "boundary_rule": extraction_model["boundary_rule"],
    "vocabulary_registry": extraction_model["vocabulary_registry"],
    "metadata": extraction_model["metadata"],
}

freeze_path = Path("backend/server/data/semantic_article_reader/PHASE_4_6_3_FREEZE_MARKER.json")
freeze_path.write_text(json.dumps(freeze_marker, indent=2), encoding="utf-8")

print("\n=== CERTIFICATION RESULT ===")
print(json.dumps({
    "status": "PASSED",
    "phase": "4.6.3",
    "patch": "4.6.3C",
    "domain_label": extraction_model["domain_label"],
    "vocabulary_registry": extraction_model["vocabulary_registry"],
    "dominant_terms": extraction_model["dominant_terms"],
    "entity_candidates": extraction_model["entity_candidates"],
    "concept_candidates": extraction_model["concept_candidates"],
    "semantic_objects": extraction_model["metadata"]["semantic_object_count"],
    "mentions": extraction_model["metadata"]["mention_count"],
    "object_type_counts": extraction_model["metadata"]["object_type_counts"],
    "category_counts": extraction_model["metadata"]["category_counts"],
    "extraction_model": str(out),
    "freeze_marker": str(freeze_path),
}, indent=2))
