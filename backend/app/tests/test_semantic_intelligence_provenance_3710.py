from copy import deepcopy

from backend.server.engine.semantic_intelligence_explanation_evidence_379 import (
    associate_explanation_evidence,
)
from backend.server.engine.semantic_intelligence_provenance_3710 import (
    associate_candidate_provenance,
)


def fixture():
    candidate = {
        "selection_occurrence_id": "occ-1",
        "article_sha256": "a" * 64,
    }
    registry = {
        "e1": {
            "candidate_index": 0,
            "source": "semantic_memory",
            "evidence_type": "semantic_memory_match",
            "certified": False,
            "document_id": "doc1",
        }
    }
    association = associate_explanation_evidence(
        candidate_index=0,
        evidence_ids=["e1"],
        evidence_registry=registry,
    )
    return candidate, registry, association


def run(candidate=None, registry=None, association=None):
    c, r, a = fixture()
    return associate_candidate_provenance(
        candidate_index=0,
        original_candidate=c if candidate is None else candidate,
        evidence_association=a if association is None else association,
        evidence_registry=r if registry is None else registry,
    )


def test_positive_lineage_association():
    result = run()
    assert result["status"] == "provenance_references_associated"
    assert result["evidence_ids"] == ["e1"]
    assert result["evidence_count"] == 1
    assert result["evidence_lineage"][0]["source"] == "semantic_memory"


def test_candidate_origin_preserved():
    result = run()
    assert result["candidate_origin"]["selection_occurrence_id"] == "occ-1"
    assert result["candidate_origin"]["article_sha256"] == "a" * 64


def test_missing_optional_origin_not_fabricated():
    result = run(candidate={})
    assert result["status"] == "provenance_references_associated"
    assert result["candidate_origin"] == {}


def test_no_evidence_is_distinct():
    candidate, registry, _ = fixture()
    association = associate_explanation_evidence(
        candidate_index=0,
        evidence_ids=[],
        evidence_registry=registry,
    )
    result = run(association=association)
    assert result["status"] == "no_evidence"
    assert result["evidence_count"] == 0


def test_cross_candidate_evidence_rejected():
    candidate, registry, association = fixture()
    registry["e1"]["candidate_index"] = 1
    assert run(registry=registry, association=association)[
        "status"
    ] == "invalid"


def test_unresolved_evidence_rejected():
    candidate, registry, association = fixture()
    registry.clear()
    assert run(registry=registry, association=association)[
        "reason"
    ] == "unresolved_evidence_lineage"


def test_no_source_mutations():
    candidate, registry, association = fixture()
    before = deepcopy((candidate, registry, association))
    run(candidate=candidate, registry=registry,
        association=association)
    assert (candidate, registry, association) == before


def test_provenance_not_promoted_to_authority():
    result = run()
    assert result["registry_references_resolved"] is True
    assert result["independent_provenance_verified"] is False
    assert result["semantic_proof_certified"] is False
    assert result["scorer_decision_performed"] is False
    assert result["automatic_linking_authorized"] is False



def test_37103_candidate_origin_fields_preserved_exactly():
    candidate, registry, association = fixture()
    candidate.update({
        "selection_source_span_status": "verified",
        "selection_source_span": {"start": 12, "end": 27},
        "sentence_span": {"start": 0, "end": 50},
    })
    before = deepcopy(candidate)
    result = run(candidate=candidate)
    assert result["status"] == "provenance_references_associated"
    assert result["candidate_origin"] == before
    assert result["source_content_independently_verified"] is False


def test_37103_malformed_occurrence_rejected():
    for bad in ("", " ", 17, None, True):
        candidate, _, _ = fixture()
        candidate["selection_occurrence_id"] = bad
        result = run(candidate=candidate)
        assert result["status"] == "invalid"
        assert result["reason"] == "invalid_selection_occurrence_id"
        assert result["evidence_lineage"] == []


def test_37103_article_hash_format_validated():
    for bad in ("xyz", "a" * 63, "g" * 64, None, 15):
        candidate, _, _ = fixture()
        candidate["article_sha256"] = bad
        result = run(candidate=candidate)
        assert result["reason"] == "invalid_article_sha256"

    candidate, _, _ = fixture()
    candidate["article_sha256"] = "A" * 64
    assert run(candidate=candidate)["status"] == (
        "provenance_references_associated"
    )


def test_37103_span_shapes_validated():
    for field in ("selection_source_span", "source_span",
                  "sentence_span"):
        candidate, _, _ = fixture()
        candidate[field] = [0, 10]
        result = run(candidate=candidate)
        assert result["reason"] == (
            "invalid_candidate_origin_span:" + field
        )


def test_37103_missing_origin_fields_not_fabricated():
    result = run(candidate={})
    assert result["status"] == "provenance_references_associated"
    assert result["candidate_origin"] == {}
    assert result["origin_fields_present"] == []
    assert result["candidate_origin_status"] == (
        "no_candidate_origin_metadata"
    )


def test_37103_origin_does_not_prove_semantics():
    result = run()
    assert result["candidate_origin_status"] == (
        "source_fields_preserved_unverified"
    )
    assert result["source_content_independently_verified"] is False
    assert result["independent_provenance_verified"] is False
    assert result["semantic_proof_certified"] is False
    assert result["automatic_linking_authorized"] is False



def test_37104_source_metadata_matches_registry():
    result = run()
    assert result["status"] == "provenance_references_associated"
    lineage = result["evidence_lineage"][0]["source_lineage"]
    assert lineage["source_metadata"] == {"document_id": "doc1"}
    assert lineage["lineage_consistency"] == "registry_fields_match"
    assert lineage["source_authenticity_verified"] is False


def test_37104_forged_document_reference_rejected():
    candidate, registry, association = fixture()
    association["evidence_trace"][0]["evidence_lineage"][
        "source_metadata"
    ]["document_id"] = "forged_document"
    result = run(registry=registry, association=association)
    assert result["status"] == "invalid"
    assert result["reason"] == "source_registry_metadata_mismatch"
    assert result["evidence_lineage"] == []


def test_37104_unregistered_metadata_rejected():
    candidate, registry, association = fixture()
    association["evidence_trace"][0]["evidence_lineage"][
        "source_metadata"
    ]["source_url"] = "https://example.com/unsupported"
    result = run(registry=registry, association=association)
    assert result["reason"] == "source_registry_metadata_mismatch"


def test_37104_missing_registry_metadata_rejected():
    candidate, registry, association = fixture()
    registry["e1"]["source_reference"] = "new_reference"
    result = run(registry=registry, association=association)
    assert result["reason"] == "source_registry_metadata_mismatch"


def test_37104_evidence_type_mismatch_rejected():
    candidate, registry, association = fixture()
    association["evidence_trace"][0]["evidence_type"] = "incorrect"
    result = run(registry=registry, association=association)
    assert result["reason"] == "source_evidence_type_mismatch"


def test_37104_legacy_semantic_memory_still_supported():
    candidate, registry, association = fixture()
    registry["e1"].pop("evidence_type")
    association = associate_explanation_evidence(
        candidate_index=0,
        evidence_ids=["e1"],
        evidence_registry=registry,
    )
    result = run(registry=registry, association=association)
    assert result["status"] == "provenance_references_associated"
    assert result["evidence_lineage"][0]["source_lineage"][
        "evidence_type"
    ] == "legacy_semantic_memory_record"


def test_37104_original_inputs_unchanged():
    candidate, registry, association = fixture()
    original = deepcopy((candidate, registry, association))
    result = run(
        candidate=candidate,
        registry=registry,
        association=association,
    )
    assert result["status"] == "provenance_references_associated"
    assert (candidate, registry, association) == original



def test_37105_four_intelligence_scopes_remain_separate():
    from backend.server.engine.semantic_intelligence_provenance_3710 import (
        inventory_cross_intelligence_provenance,
    )
    sections = {
        "explainability": {"evidence_ids": ["registry_a"]},
        "reasoning_intelligence": {
            "document_relationship_provenance": [{"source_evidence_id": "doc_b"}]
        },
        "intelligence_graph": {
            "semantic_relationship_evidence_ids": ["graph_c"]
        },
        "confidence_evidence": {
            "evidence_ids": ["confidence_d"]
        },
    }
    before = deepcopy(sections)
    result = inventory_cross_intelligence_provenance(
        candidate_index=0, sections=sections
    )
    assert result["status"] == "source_inventory_created"
    assert result["source_count"] == 4
    assert len({x["scope"] for x in result["sources"]}) == 4
    assert result["cross_source_identity_equivalence"] == "not_established"
    assert sections == before


def test_37105_missing_sections_are_not_invented():
    from backend.server.engine.semantic_intelligence_provenance_3710 import (
        inventory_cross_intelligence_provenance,
    )
    result = inventory_cross_intelligence_provenance(
        candidate_index=0, sections={}
    )
    assert result["status"] == "no_sources"
    assert result["sources"] == []


def test_37105_explicit_unavailable_distinguished():
    from backend.server.engine.semantic_intelligence_provenance_3710 import (
        inventory_cross_intelligence_provenance,
    )
    result = inventory_cross_intelligence_provenance(
        candidate_index=0, sections={"reasoning_intelligence": None}
    )
    assert result["sources"][0]["status"] == "unavailable"


def test_37105_unknown_section_rejected():
    from backend.server.engine.semantic_intelligence_provenance_3710 import (
        inventory_cross_intelligence_provenance,
    )
    result = inventory_cross_intelligence_provenance(
        candidate_index=0, sections={"unapproved_source": {}}
    )
    assert result["status"] == "invalid"
    assert result["sources"] == []


def test_37105_malformed_section_rejected_atomically():
    from backend.server.engine.semantic_intelligence_provenance_3710 import (
        inventory_cross_intelligence_provenance,
    )
    result = inventory_cross_intelligence_provenance(
        candidate_index=0,
        sections={
            "explainability": {"evidence_ids": ["a"]},
            "intelligence_graph": "malformed",
        },
    )
    assert result["status"] == "invalid"
    assert result["sources"] == []


def test_37105_source_records_not_promoted_to_authority():
    from backend.server.engine.semantic_intelligence_provenance_3710 import (
        inventory_cross_intelligence_provenance,
    )
    result = inventory_cross_intelligence_provenance(
        candidate_index=0,
        sections={"intelligence_graph": {"evidence_id": "graph_1"}},
    )
    assert result["independent_provenance_verified"] is False
    assert result["semantic_proof_certified"] is False
    assert result["scorer_decision_performed"] is False
    assert result["automatic_linking_authorized"] is False
    assert result["sources"][0]["independently_verified"] is False



def test_37106_missing_source_is_not_unavailable():
    from backend.server.engine.semantic_intelligence_provenance_3710 import (
        inventory_cross_intelligence_provenance,
    )

    result = inventory_cross_intelligence_provenance(
        candidate_index=0, sections={}
    )
    assert result["status"] == "no_sources"
    assert result["source_count"] == 0


def test_37106_explicit_unavailable_source():
    from backend.server.engine.semantic_intelligence_provenance_3710 import (
        inventory_cross_intelligence_provenance,
    )

    result = inventory_cross_intelligence_provenance(
        candidate_index=0,
        sections={"reasoning_intelligence": None},
    )
    assert result["status"] == "source_inventory_created"
    assert result["sources"][0]["status"] == "unavailable"


def test_37106_empty_reference_collection():
    from backend.server.engine.semantic_intelligence_provenance_3710 import (
        inventory_cross_intelligence_provenance,
    )

    result = inventory_cross_intelligence_provenance(
        candidate_index=0,
        sections={"explainability": {"evidence_ids": []}},
    )
    assert result["status"] == "source_inventory_created"
    assert result["sources"][0]["status"] == "no_evidence_references"
    assert result["sources"][0]["reference_fields"] == {
        "evidence_ids": []
    }


def test_37106_malformed_reference_lists_rejected():
    from backend.server.engine.semantic_intelligence_provenance_3710 import (
        inventory_cross_intelligence_provenance,
    )

    for invalid in (None, "e1", [None], [""], ["e1", "e1"]):
        result = inventory_cross_intelligence_provenance(
            candidate_index=0,
            sections={"explainability": {"evidence_ids": invalid}},
        )
        assert result["status"] == "invalid"
        assert result["sources"] == []
        assert result["reason"] == (
            "invalid_provenance_reference:explainability:evidence_ids"
        )


def test_37106_invalid_later_source_rejects_atomically():
    from backend.server.engine.semantic_intelligence_provenance_3710 import (
        inventory_cross_intelligence_provenance,
    )

    result = inventory_cross_intelligence_provenance(
        candidate_index=0,
        sections={
            "explainability": {"evidence_ids": ["e1"]},
            "intelligence_graph": {
                "semantic_relationship_evidence_ids": [15]
            },
        },
    )
    assert result["status"] == "invalid"
    assert result["sources"] == []
    assert result["source_count"] == 0
    assert result["automatic_linking_authorized"] is False


def test_37106_valid_references_preserved_without_mutation():
    from backend.server.engine.semantic_intelligence_provenance_3710 import (
        inventory_cross_intelligence_provenance,
    )

    sections = {
        "explainability": {"evidence_ids": ["e2", "e1"]},
        "reasoning_intelligence": {
            "source_evidence_id": "reason_1"
        },
    }
    before = deepcopy(sections)
    result = inventory_cross_intelligence_provenance(
        candidate_index=0,
        sections=sections,
    )

    assert result["status"] == "source_inventory_created"
    assert sections == before
    assert result["sources"][0]["reference_fields"][
        "evidence_ids"
    ] == ["e2", "e1"]
    assert result["independent_provenance_verified"] is False
    assert result["automatic_linking_authorized"] is False



def consistency_fixture():
    from backend.server.engine.semantic_intelligence_provenance_3710 import (
        inventory_cross_intelligence_provenance,
    )
    candidate, registry, association = fixture()
    provenance = run(
        candidate=candidate,
        registry=registry,
        association=association,
    )
    inventory = inventory_cross_intelligence_provenance(
        candidate_index=0,
        sections={
            "explainability": {
                "evidence_ids": association["evidence_ids"]
            },
            "reasoning_intelligence": {
                "source_evidence_id": "different_reasoning_reference"
            },
        },
    )
    return provenance, association, inventory


def check_consistency(provenance, association, inventory):
    from backend.server.engine.semantic_intelligence_provenance_3710 import (
        validate_provenance_consistency,
    )
    return validate_provenance_consistency(
        candidate_index=0,
        candidate_provenance=provenance,
        evidence_association=association,
        cross_intelligence_provenance=inventory,
    )


def test_37107_shared_evidence_references_consistent():
    p, a, i = consistency_fixture()
    result = check_consistency(p, a, i)
    assert result["status"] == "shared_references_consistent"
    assert result["checked_evidence_ids"] == ["e1"]
    assert result["checked_evidence_count"] == 1


def test_37107_different_reasoning_reference_is_not_equated():
    p, a, i = consistency_fixture()
    result = check_consistency(p, a, i)
    assert result["status"] == "shared_references_consistent"
    assert result["cross_source_identity_equivalence"] == "not_established"


def test_37107_cross_candidate_identity_rejected():
    p, a, i = consistency_fixture()
    p["candidate_index"] = 1
    result = check_consistency(p, a, i)
    assert result["reason"] == "candidate_index_mismatch"


def test_37107_altered_inventory_reference_rejected():
    p, a, i = consistency_fixture()
    i["sources"][0]["reference_fields"]["evidence_ids"] = ["forged"]
    result = check_consistency(p, a, i)
    assert result["reason"] == "explainability_inventory_mismatch"


def test_37107_altered_trace_identity_rejected():
    p, a, i = consistency_fixture()
    a["evidence_trace"][0]["evidence_id"] = "other"
    result = check_consistency(p, a, i)
    assert result["reason"] == "evidence_identity_or_order_mismatch"


def test_37107_altered_lineage_rejected():
    p, a, i = consistency_fixture()
    p["evidence_lineage"][0]["explanation_lineage"][
        "registry_evidence_id"
    ] = "forged"
    result = check_consistency(p, a, i)
    assert result["reason"] == "evidence_lineage_mismatch"


def test_37107_no_evidence_remains_no_evidence():
    from backend.server.engine.semantic_intelligence_provenance_3710 import (
        inventory_cross_intelligence_provenance,
    )
    candidate, registry, _ = fixture()
    a = associate_explanation_evidence(
        candidate_index=0,
        evidence_ids=[],
        evidence_registry=registry,
    )
    p = run(candidate=candidate, registry=registry, association=a)
    i = inventory_cross_intelligence_provenance(
        candidate_index=0,
        sections={"explainability": {"evidence_ids": []}},
    )
    result = check_consistency(p, a, i)
    assert result["status"] == "no_evidence"
    assert result["checked_evidence_count"] == 0


def test_37107_inputs_remain_unchanged_and_no_authority():
    p, a, i = consistency_fixture()
    before = deepcopy((p, a, i))
    result = check_consistency(p, a, i)
    assert (p, a, i) == before
    assert result["independent_provenance_verified"] is False
    assert result["semantic_proof_certified"] is False
    assert result["scorer_decision_performed"] is False
    assert result["automatic_linking_authorized"] is False



def test_37108_main_enricher_provenance_integration_present():
    import inspect
    from backend.server.engine import semantic_intelligence_enricher

    source = inspect.getsource(semantic_intelligence_enricher)
    assert "provenance_main_integration_37108" in source
    assert "associate_candidate_provenance(" in source
    assert "inventory_cross_intelligence_provenance(" in source
    assert "validate_provenance_consistency(" in source
    assert 'section["provenance"] = {' in source


def test_37108_original_explanation_integration_preserved():
    import inspect
    from backend.server.engine import semantic_intelligence_enricher

    source = inspect.getsource(semantic_intelligence_enricher)
    assert "explain_candidate_evidence(" in source
    assert 'section["evidence_association"] = evidence_association' in source

    assert source.index(
        'section["evidence_association"] = evidence_association'
    ) < source.index("provenance_main_integration_37108")
