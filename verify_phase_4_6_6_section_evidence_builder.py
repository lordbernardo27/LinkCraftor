from backend.server.stores.semantic_article_reader import read_semantic_article_v1
from backend.server.stores.semantic_context_builder import build_semantic_context_v1
from backend.server.stores.entity_concept_extraction import extract_entities_and_concepts_v1
from backend.server.stores.phrase_neighborhood_intelligence import build_phrase_neighborhoods_v1
from backend.server.stores.topic_intent_intelligence import build_topic_intent_v1
from backend.server.stores.section_evidence_builder import (
    build_section_evidence_v1,
    explain_section_evidence_builder_v1,
    save_section_evidence_v1,
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

print("=== PHASE 4.6.6 — SECTION EVIDENCE BUILDER VERIFICATION ===")

capabilities = explain_section_evidence_builder_v1()
print(json.dumps(capabilities, indent=2))

reading_model = read_semantic_article_v1(
    sample_article,
    article_id="article_phase_466_test",
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

assert extraction_model["patch"] == "4.6.3C"
assert neighborhood_model["patch"] == "4.6.4B"
assert intent_model["patch"] == "4.6.5B"

evidence_model = build_section_evidence_v1(
    context_model,
    extraction_model,
    neighborhood_model,
    intent_model,
)

out = Path("backend/server/data/semantic_article_reader/phase_4_6_6_section_evidence_model.json")
saved = save_section_evidence_v1(
    context_model,
    extraction_model,
    neighborhood_model,
    intent_model,
    out,
)

assert evidence_model["schema_version"] == "section_evidence_builder_v1"
assert evidence_model["phase"] == "4.6.6"
assert evidence_model["patch"] == "4.6.6A"
assert evidence_model["article"]["article_id"] == "article_phase_466_test"
assert evidence_model["section_evidence"]
assert evidence_model["metadata"]["section_evidence_count"] == len(context_model["section_contexts"])
assert evidence_model["metadata"]["article_intent_present"] is True

for record in evidence_model["section_evidence"]:
    assert "section_evidence_id" in record
    assert "evidence_scope" in record
    assert record["evidence_scope"] == "section"
    assert "article_reference" in record
    assert "article_intent_id" in record["article_reference"]
    assert "section_intent" in record
    assert "semantic_objects" in record
    assert "mentions" in record
    assert "phrase_neighborhoods" in record
    assert "object_category_counts" in record
    assert "relationship_family_counts" in record
    assert "relationship_type_counts" in record
    assert "structural_context" in record
    assert "provenance" in record
    assert "evidence_lineage" in record
    assert "semantic_context_section_id" in record["evidence_lineage"]
    assert "semantic_object_ids" in record["evidence_lineage"]
    assert "mention_ids" in record["evidence_lineage"]
    assert "relationship_ids" in record["evidence_lineage"]
    assert "section_intent_id" in record["evidence_lineage"]
    assert "article_intent_id" in record["evidence_lineage"]
    assert "evidence_metrics" in record
    assert "evidence_confidence" in record["evidence_metrics"]

assert "blue highlights" in evidence_model["boundary_rule"]
assert "yellow highlights" in evidence_model["boundary_rule"]
assert out.exists()

freeze_marker = {
    "phase": "4.6.6",
    "patch": "4.6.6A",
    "name": "Section Evidence Builder",
    "status": "FROZEN",
    "output_file": str(out),
    "certified_capabilities": capabilities["does"],
    "certified_boundaries": capabilities["does_not"],
    "boundary_rule": evidence_model["boundary_rule"],
    "metadata": evidence_model["metadata"],
}

freeze_path = Path("backend/server/data/semantic_article_reader/PHASE_4_6_6_FREEZE_MARKER.json")
freeze_path.write_text(json.dumps(freeze_marker, indent=2), encoding="utf-8")

print("\n=== CERTIFICATION RESULT ===")
print(json.dumps({
    "status": "PASSED",
    "phase": "4.6.6",
    "patch": "4.6.6A",
    "patch": "4.6.6A",
    "domain_label": evidence_model["domain_label"],
    "article_evidence_summary": evidence_model["article_evidence_summary"],
    "section_evidence_count": evidence_model["metadata"]["section_evidence_count"],
    "total_semantic_objects": evidence_model["metadata"]["total_semantic_objects"],
    "total_mentions": evidence_model["metadata"]["total_mentions"],
    "total_phrase_neighborhoods": evidence_model["metadata"]["total_phrase_neighborhoods"],
    "section_samples": [
        {
            "section_title": item["section_title"],
            "topic_intent": item["section_intent"]["topic_intent"] if item["section_intent"] else None,
            "semantic_objects": item["evidence_metrics"]["semantic_object_count"],
            "mentions": item["evidence_metrics"]["mention_count"],
            "phrase_neighborhoods": item["evidence_metrics"]["phrase_neighborhood_count"],
            "evidence_confidence": item["evidence_metrics"]["evidence_confidence"],
        }
        for item in evidence_model["section_evidence"]
    ],
    "evidence_model": str(out),
    "freeze_marker": str(freeze_path),
}, indent=2))
