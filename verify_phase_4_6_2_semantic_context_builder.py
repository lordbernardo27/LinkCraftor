from backend.server.stores.semantic_article_reader import read_semantic_article_v1
from backend.server.stores.semantic_context_builder import (
    build_semantic_context_v1,
    explain_semantic_context_builder_v1,
    save_semantic_context_v1,
)
import json
from pathlib import Path

sample_article = """
# Pregnancy Symptoms

Pregnancy symptoms can vary from person to person. Some people notice symptoms early, while others may not notice changes right away.

## Early signs

Missed periods are one common early sign. Nausea and tiredness may also occur.

- Breast tenderness
- Frequent urination
- Food aversions

### Less common signs

Some symptoms may appear later.

## When to test

A home pregnancy test works best after a missed period. Follow the test instructions carefully.
""".strip()

print("=== PHASE 4.6.2A — SEMANTIC CONTEXT BUILDER HARDENING VERIFICATION ===")

capabilities = explain_semantic_context_builder_v1()
print(json.dumps(capabilities, indent=2))

reading_model = read_semantic_article_v1(
    sample_article,
    article_id="article_phase_462_test",
    source_url="https://example.com/pregnancy-symptoms",
    title="Pregnancy Symptoms",
)

assert reading_model["phase"] == "4.6.1"
assert reading_model["validation"]["valid"] is True

context_model = build_semantic_context_v1(reading_model, context_radius=2)

out = Path("backend/server/data/semantic_article_reader/phase_4_6_2_semantic_context_model.json")
saved = save_semantic_context_v1(reading_model, out, context_radius=2)

assert context_model["schema_version"] == "semantic_context_builder_v1"
assert context_model["phase"] == "4.6.2"
assert context_model["patch"] == "4.6.2A"
assert context_model["source_phase"] == "4.6.1"
assert context_model["article"]["article_id"] == "article_phase_462_test"

assert context_model["metadata"]["section_context_count"] == len(reading_model["sections"])
assert context_model["metadata"]["block_context_count"] == len(reading_model["blocks"])
assert context_model["metadata"]["sentence_context_count"] == reading_model["article"]["metadata"]["sentence_count"]
assert context_model["metadata"]["has_document_context"] is True
assert context_model["metadata"]["has_cross_reference_index"] is True
assert context_model["metadata"]["has_context_fingerprints"] is True

assert "document_context" in context_model
assert "document_fingerprint" in context_model["document_context"]
assert "cross_reference_index" in context_model

index = context_model["cross_reference_index"]
assert "block_to_section" in index
assert "paragraph_to_block" in index
assert "sentence_to_block" in index
assert "section_to_sentences" in index

for block_context in context_model["block_contexts"]:
    assert "context_fingerprint" in block_context
    assert "breadcrumb" in block_context["context"]
    assert "heading_ancestry" in block_context["context"]
    assert "section_entry_block_id" in block_context["context"]
    assert "section_exit_block_id" in block_context["context"]

for section_context in context_model["section_contexts"]:
    assert "context_fingerprint" in section_context
    assert "breadcrumb" in section_context["context"]
    assert "heading_ancestry" in section_context["context"]
    assert "entry_block_id" in section_context["context"]
    assert "exit_block_id" in section_context["context"]
    assert "previous_section_id" in section_context["context"]
    assert "next_section_id" in section_context["context"]

for sentence_context in context_model["sentence_contexts"]:
    assert "context_fingerprint" in sentence_context
    assert "breadcrumb" in sentence_context["context"]
    assert "heading_ancestry" in sentence_context["context"]
    assert "previous_block_text" in sentence_context["context"]
    assert "next_block_text" in sentence_context["context"]

assert out.exists()

freeze_marker = {
    "phase": "4.6.2",
    "patch": "4.6.2A",
    "name": "Semantic Context Builder",
    "status": "FROZEN",
    "output_file": str(out),
    "certified_capabilities": capabilities["does"],
    "certified_boundaries": capabilities["does_not"],
    "boundary_rule": context_model["boundary_rule"],
    "metadata": context_model["metadata"],
}

freeze_path = Path("backend/server/data/semantic_article_reader/PHASE_4_6_2_FREEZE_MARKER.json")
freeze_path.write_text(json.dumps(freeze_marker, indent=2), encoding="utf-8")

print("\n=== CERTIFICATION RESULT ===")
print(json.dumps({
    "status": "PASSED",
    "phase": "4.6.2",
    "patch": "4.6.2A",
    "section_contexts": context_model["metadata"]["section_context_count"],
    "block_contexts": context_model["metadata"]["block_context_count"],
    "sentence_contexts": context_model["metadata"]["sentence_context_count"],
    "has_document_context": context_model["metadata"]["has_document_context"],
    "has_cross_reference_index": context_model["metadata"]["has_cross_reference_index"],
    "has_context_fingerprints": context_model["metadata"]["has_context_fingerprints"],
    "context_model": str(out),
    "freeze_marker": str(freeze_path),
}, indent=2))
