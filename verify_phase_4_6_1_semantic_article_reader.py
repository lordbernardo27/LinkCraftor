from backend.server.stores.semantic_article_reader import (
    explain_semantic_article_reader_v1,
    read_semantic_article_v1,
    save_semantic_article_reading_v1,
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

> Some symptoms may appear later.

Note: Symptoms alone cannot confirm pregnancy.

## When to test

A home pregnancy test works best after a missed period. Follow the test instructions carefully.

## References

This article is for educational purposes only.
""".strip()

print("=== PHASE 4.6.1A — SEMANTIC ARTICLE READER STRUCTURAL HARDENING VERIFICATION ===")

capabilities = explain_semantic_article_reader_v1()
print(json.dumps(capabilities, indent=2))

model = read_semantic_article_v1(
    sample_article,
    article_id="article_phase_461_test",
    source_url="https://example.com/pregnancy-symptoms",
    title="Pregnancy Symptoms",
)

out = Path("backend/server/data/semantic_article_reader/phase_4_6_1_semantic_reading_model.json")
saved = save_semantic_article_reading_v1(
    sample_article,
    out,
    article_id="article_phase_461_test",
    source_url="https://example.com/pregnancy-symptoms",
    title="Pregnancy Symptoms",
)

assert model["schema_version"] == "semantic_article_reader_v1"
assert model["phase"] == "4.6.1"
assert model["patch"] == "4.6.1A"
assert model["article"]["article_id"] == "article_phase_461_test"
assert model["article"]["original_text"] == sample_article
assert model["article"]["metadata"]["section_count"] >= 4
assert model["article"]["metadata"]["block_count"] == len(model["blocks"])
assert model["article"]["metadata"]["sentence_count"] > 0
assert len(model["reading_order"]) == len(model["blocks"])
assert model["validation"]["valid"] is True

navigation = model["article"]["navigation"]
assert navigation["first_block_id"] == model["blocks"][0]["block_id"]
assert navigation["last_block_id"] == model["blocks"][-1]["block_id"]
assert navigation["first_section_id"] == model["sections"][0]["section_id"]
assert navigation["last_section_id"] == model["sections"][-1]["section_id"]

section_ids = {s["section_id"] for s in model["sections"]}
block_ids = {b["block_id"] for b in model["blocks"]}

for section in model["sections"]:
    assert "parent_section_id" in section
    assert "children_section_ids" in section
    assert "start_line" in section
    assert "end_line" in section
    assert "start_char" in section
    assert "end_char" in section
    assert "section_word_count" in section["metadata"]
    assert "section_sentence_count" in section["metadata"]
    assert "section_paragraph_count" in section["metadata"]

    if section["parent_section_id"]:
        assert section["parent_section_id"] in section_ids

    for block_id in section["block_ids"]:
        assert block_id in block_ids

for i, block in enumerate(model["blocks"]):
    assert block["block_id"] == model["reading_order"][i]
    assert "start_line" in block
    assert "end_line" in block
    assert "start_char" in block
    assert "end_char" in block
    assert "block_depth" in block
    assert "section_depth" in block
    assert "article_progress" in block

    if i == 0:
        assert block["previous_block_id"] is None
        assert block["article_progress"] == 0.0
    else:
        assert block["previous_block_id"] == model["blocks"][i - 1]["block_id"]

    if i == len(model["blocks"]) - 1:
        assert block["next_block_id"] is None
        assert block["article_progress"] == 1.0
    else:
        assert block["next_block_id"] == model["blocks"][i + 1]["block_id"]

assert model["statistics"]["sections"] == model["article"]["metadata"]["section_count"]
assert model["statistics"]["blocks"] == model["article"]["metadata"]["block_count"]
assert model["statistics"]["paragraphs"] == model["article"]["metadata"]["paragraph_count"]
assert model["statistics"]["sentences"] == model["article"]["metadata"]["sentence_count"]
assert model["statistics"]["headings"] >= 4
assert "block_type_counts" in model["statistics"]
assert "heading_distribution" in model["statistics"]

assert out.exists()

freeze_marker = {
    "phase": "4.6.1",
    "patch": "4.6.1A",
    "name": "Semantic Article Reader",
    "status": "FROZEN",
    "output_file": str(out),
    "certified_capabilities": capabilities["does"],
    "certified_boundaries": capabilities["does_not"],
    "supported_block_types": capabilities["supported_block_types"],
    "canonical_rule": model["canonical_rule"],
    "validation": model["validation"],
    "statistics": model["statistics"],
}

freeze_path = Path("backend/server/data/semantic_article_reader/PHASE_4_6_1_FREEZE_MARKER.json")
freeze_path.write_text(json.dumps(freeze_marker, indent=2), encoding="utf-8")

print("\n=== CERTIFICATION RESULT ===")
print(json.dumps({
    "status": "PASSED",
    "phase": "4.6.1",
    "patch": "4.6.1A",
    "sections": model["article"]["metadata"]["section_count"],
    "blocks": model["article"]["metadata"]["block_count"],
    "paragraphs": model["article"]["metadata"]["paragraph_count"],
    "sentences": model["article"]["metadata"]["sentence_count"],
    "validation": model["validation"],
    "statistics": model["statistics"],
    "reading_model": str(out),
    "freeze_marker": str(freeze_path),
}, indent=2))
