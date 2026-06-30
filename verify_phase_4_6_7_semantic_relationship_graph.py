from backend.server.stores.semantic_article_reader import read_semantic_article_v1
from backend.server.stores.semantic_context_builder import build_semantic_context_v1
from backend.server.stores.entity_concept_extraction import extract_entities_and_concepts_v1
from backend.server.stores.phrase_neighborhood_intelligence import build_phrase_neighborhoods_v1
from backend.server.stores.topic_intent_intelligence import build_topic_intent_v1
from backend.server.stores.section_evidence_builder import build_section_evidence_v1
from backend.server.stores.semantic_relationship_graph import (
    build_semantic_relationship_graph_v1,
    explain_semantic_relationship_graph_v1,
    save_semantic_relationship_graph_v1,
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

print("=== PHASE 4.6.7 — SEMANTIC RELATIONSHIP GRAPH VERIFICATION ===")

capabilities = explain_semantic_relationship_graph_v1()
print(json.dumps(capabilities, indent=2))

reading_model = read_semantic_article_v1(
    sample_article,
    article_id="article_phase_467_test",
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

assert context_model["patch"] == "4.6.2A"
assert extraction_model["patch"] == "4.6.3C"
assert neighborhood_model["patch"] == "4.6.4B"
assert intent_model["patch"] == "4.6.5B"
assert evidence_model["patch"] == "4.6.6A"

graph_model = build_semantic_relationship_graph_v1(evidence_model)

out = Path("backend/server/data/semantic_article_reader/phase_4_6_7_semantic_relationship_graph.json")
saved = save_semantic_relationship_graph_v1(evidence_model, out)

assert graph_model["schema_version"] == "semantic_relationship_graph_v1"
assert graph_model["phase"] == "4.6.7"
assert graph_model["patch"] == "4.6.7A"
assert "graph_lineage" in graph_model
assert graph_model["article"]["article_id"] == "article_phase_467_test"

assert graph_model["graph"]["nodes"]
assert graph_model["graph"]["edges"]
assert graph_model["metadata"]["node_count"] > 0
assert graph_model["metadata"]["edge_count"] > 0

node_types = set(graph_model["metadata"]["node_type_counts"].keys())
edge_types = set(graph_model["metadata"]["edge_type_counts"].keys())

required_node_types = {
    "article",
    "section",
    "article_intent",
    "section_intent",
    "semantic_object",
    "mention",
    "phrase_neighborhood",
    "section_evidence",
}

required_edge_types = {
    "contains_section",
    "has_article_intent",
    "has_section_intent",
    "has_section_evidence",
    "mentions_object",
    "has_mention",
    "relates_to",
    "supported_by_evidence",
    "supports_section_evidence",
}

assert required_node_types.intersection(node_types)
assert required_edge_types.intersection(edge_types)
assert "relates_to" in edge_types

for node in graph_model["graph"]["nodes"]:
    assert "node_id" in node
    assert "node_type" in node
    assert "node_layer" in node
    assert "partition" in node
    assert "label" in node
    assert "properties" in node

for edge in graph_model["graph"]["edges"]:
    assert "edge_id" in edge
    assert "source_id" in edge
    assert "target_id" in edge
    assert "edge_type" in edge
    assert "properties" in edge

assert "blue highlights" in graph_model["boundary_rule"]
assert "yellow highlights" in graph_model["boundary_rule"]
assert out.exists()

freeze_marker = {
    "phase": "4.6.7",
    "patch": "4.6.7A",
    "name": "Semantic Relationship Graph",
    "status": "FROZEN",
    "output_file": str(out),
    "certified_capabilities": capabilities["does"],
    "certified_boundaries": capabilities["does_not"],
    "boundary_rule": graph_model["boundary_rule"],
    "metadata": graph_model["metadata"],
}

freeze_path = Path("backend/server/data/semantic_article_reader/PHASE_4_6_7_FREEZE_MARKER.json")
freeze_path.write_text(json.dumps(freeze_marker, indent=2), encoding="utf-8")

print("\n=== CERTIFICATION RESULT ===")
print(json.dumps({
    "status": "PASSED",
    "phase": "4.6.7",
    "patch": "4.6.7A",
    "patch": "4.6.7A",
    "domain_label": graph_model["domain_label"],
    "node_count": graph_model["metadata"]["node_count"],
    "edge_count": graph_model["metadata"]["edge_count"],
    "node_type_counts": graph_model["metadata"]["node_type_counts"],
    "edge_type_counts": graph_model["metadata"]["edge_type_counts"],
    "node_layer_counts": graph_model["metadata"]["node_layer_counts"],
    "partition_counts": graph_model["metadata"]["partition_counts"],
    "graph_lineage": graph_model["graph_lineage"],
    "graph_model": str(out),
    "freeze_marker": str(freeze_path),
}, indent=2))
