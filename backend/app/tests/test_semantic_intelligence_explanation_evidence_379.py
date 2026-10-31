from copy import deepcopy

from backend.server.engine.semantic_intelligence_explanation_evidence_379 import (
    associate_explanation_evidence,
)


def evidence():
    return {
        "e1": {
            "candidate_index": 0,
            "source": "semantic_memory",
            "evidence_type": "semantic_memory_match",
            "certified": False,
        }
    }


def run(ids=None, registry=None):
    return associate_explanation_evidence(
        candidate_index=0,
        evidence_ids=["e1"] if ids is None else ids,
        evidence_registry=evidence() if registry is None else registry,
    )


def test_positive_association_preserves_identity():
    result = run()
    assert result["status"] == "evidence_associated"
    assert result["evidence_ids"] == ["e1"]
    assert result["evidence_trace"][0]["source"] == "semantic_memory"
    assert result["evidence_count"] == 1


def test_no_evidence_abstains():
    result = run(ids=[])
    assert result["status"] == "no_evidence"
    assert result["evidence_trace"] == []


def test_missing_reference_is_invalid():
    result = run(ids=["missing"])
    assert result["status"] == "invalid"
    assert result["evidence_trace"] == []


def test_cross_candidate_evidence_is_rejected():
    registry = evidence()
    registry["e1"]["candidate_index"] = 1
    assert run(registry=registry)["status"] == "invalid"


def test_duplicate_evidence_is_rejected():
    assert run(ids=["e1", "e1"])["status"] == "invalid"


def test_certified_evidence_is_not_promoted():
    registry = evidence()
    registry["e1"]["certified"] = True
    assert run(registry=registry)["status"] == "invalid"


def test_legacy_semantic_memory_type_supported():
    registry = evidence()
    registry["e1"].pop("evidence_type")
    result = run(registry=registry)
    assert result["evidence_trace"][0]["evidence_type"] == (
        "legacy_semantic_memory_record"
    )


def test_registry_not_modified():
    registry = evidence()
    original = deepcopy(registry)
    run(registry=registry)
    assert registry == original


def test_no_linking_or_scorer_authority():
    result = run()
    assert result["independently_verified"] is False
    assert result["semantic_proof_certified"] is False
    assert result["scorer_decision_performed"] is False
    assert result["automatic_linking_authorized"] is False


def test_invalid_later_record_has_no_partial_trace():
    registry = evidence()
    registry["e2"] = {
        "candidate_index": 1,
        "source": "semantic_memory",
        "certified": False,
    }
    result = run(ids=["e1", "e2"], registry=registry)
    assert result["status"] == "invalid"
    assert result["evidence_trace"] == []
    assert result["evidence_count"] == 0



def test_3794_positive_evidence_produces_grounded_signal():
    result = run()
    assert result["explanation_status"] == "observational_signals_found"
    assert result["explanation_signal_count"] == 1
    signal = result["explanation_signals"][0]
    assert signal["evidence_id"] == "e1"
    assert signal["candidate_index"] == 0
    assert signal["source"] == "semantic_memory"
    assert signal["evidence_type"] == "semantic_memory_match"
    assert signal["observation"] == "source_evidence_record_referenced"


def test_3794_no_evidence_no_signals():
    result = run(ids=[])
    assert result["explanation_status"] == "no_evidence"
    assert result["explanation_signal_count"] == 0
    assert result["explanation_signals"] == []


def test_3794_invalid_reference_has_no_partial_signals():
    registry = evidence()
    registry["e2"] = {
        "candidate_index": 1,
        "source": "semantic_memory",
        "evidence_type": "semantic_memory_match",
        "certified": False,
    }
    result = run(ids=["e1", "e2"], registry=registry)
    assert result["status"] == "invalid"
    assert result["explanation_signal_count"] == 0
    assert result["explanation_signals"] == []


def test_3794_semantic_conclusions_not_invented():
    signal = run()["explanation_signals"][0]
    assert signal["observation_scope"] == "evidence_reference_only"
    assert signal["semantic_relationship_asserted"] is False
    assert signal["semantic_equivalence_asserted"] is False
    assert signal["phrase_level_confidence"] is None
    assert signal["independently_verified"] is False


def test_3794_multiple_signals_preserve_source_order():
    registry = evidence()
    registry["e2"] = {
        "candidate_index": 0,
        "source": "intelligence_graph",
        "evidence_type": "graph_relationship_observation",
        "certified": False,
    }
    result = run(ids=["e2", "e1"], registry=registry)
    assert result["status"] == "evidence_associated"
    assert result["explanation_signal_count"] == 2
    assert [
        item["evidence_id"]
        for item in result["explanation_signals"]
    ] == ["e2", "e1"]


def test_3794_signals_do_not_modify_registry_or_authorize_links():
    registry = evidence()
    before = deepcopy(registry)
    result = run(registry=registry)

    assert registry == before
    assert result["automatic_linking_authorized"] is False
    assert result["scorer_decision_performed"] is False

    for signal in result["explanation_signals"]:
        assert signal["certified"] is False
        assert signal["scorer_decision_performed"] is False
        assert signal["automatic_linking_authorized"] is False



def test_3795_registry_lineage_preserved():
    result = run()
    lineage = result["evidence_trace"][0]["evidence_lineage"]
    assert lineage["registry_evidence_id"] == "e1"
    assert lineage["candidate_index"] == 0
    assert lineage["source"] == "semantic_memory"
    assert lineage["evidence_type"] == "semantic_memory_match"
    assert lineage["registry_reference_resolved"] is True
    assert lineage["independent_provenance_verified"] is False


def test_3795_source_metadata_preserved_exactly():
    registry = evidence()
    registry["e1"].update({
        "workspace_id": "ws_test",
        "document_id": "doc_123",
        "source_reference": "ref_456",
        "article_sha256": "a" * 64,
    })
    before = deepcopy(registry)
    result = run(registry=registry)
    metadata = result["evidence_trace"][0][
        "evidence_lineage"
    ]["source_metadata"]
    assert metadata == {
        "workspace_id": "ws_test",
        "document_id": "doc_123",
        "source_reference": "ref_456",
        "article_sha256": "a" * 64,
    }
    assert registry == before


def test_3795_missing_metadata_not_invented():
    result = run()
    lineage = result["evidence_trace"][0]["evidence_lineage"]
    assert lineage["source_metadata"] == {}
    assert lineage["source_metadata_status"] == (
        "no_additional_source_metadata"
    )
    assert "document_id" not in lineage["source_metadata"]


def test_3795_explanation_signal_has_matching_lineage():
    result = run()
    signal = result["explanation_signals"][0]
    trace = result["evidence_trace"][0]
    assert signal["evidence_lineage"] == trace["evidence_lineage"]
    assert signal["evidence_lineage"] is not trace["evidence_lineage"]
    assert signal["certified"] is False


def test_3795_invalid_evidence_has_no_lineage():
    registry = evidence()
    registry["e1"]["candidate_index"] = 9
    result = run(registry=registry)
    assert result["status"] == "invalid"
    assert result["evidence_trace"] == []
    assert result["explanation_signals"] == []


def test_3795_multiple_records_keep_lineage_separate():
    registry = evidence()
    registry["e1"]["document_id"] = "doc_A"
    registry["e2"] = {
        "candidate_index": 0,
        "source": "intelligence_graph",
        "evidence_type": "graph_relationship_observation",
        "certified": False,
        "document_id": "doc_B",
    }
    result = run(ids=["e2", "e1"], registry=registry)
    assert result["status"] == "evidence_associated"
    lineages = [
        item["evidence_lineage"]
        for item in result["explanation_signals"]
    ]
    assert [item["registry_evidence_id"] for item in lineages] == [
        "e2", "e1"
    ]
    assert [item["source_metadata"]["document_id"] for item in lineages] == [
        "doc_B", "doc_A"
    ]



def test_3796_no_evidence_is_not_retrieval_failure():
    result = run(ids=[])
    assert result["status"] == "no_evidence"
    assert result["reason"] is None
    assert result["upstream_retrieval_status"] == "not_supplied"
    assert result["source_availability_verified"] is False


def test_3796_unresolved_reference_has_reason():
    result = run(ids=["missing"])
    assert result["status"] == "invalid"
    assert result["reason"] == "unresolved_evidence_reference"
    assert result["evidence_trace"] == []
    assert result["explanation_signals"] == []


def test_3796_cross_candidate_reference_has_reason():
    registry = evidence()
    registry["e1"]["candidate_index"] = 4
    result = run(registry=registry)
    assert result["status"] == "invalid"
    assert result["reason"] == "invalid_evidence_record_or_attribution"


def test_3796_missing_source_and_type_distinguished():
    registry = evidence()
    registry["e1"]["source"] = " "
    result = run(registry=registry)
    assert result["reason"] == "missing_evidence_source"

    registry = evidence()
    registry["e1"]["evidence_type"] = " "
    result = run(registry=registry)
    assert result["reason"] == "missing_evidence_type"


def test_3796_bad_inputs_do_not_produce_partial_trace():
    for ids, registry in (
        (["e1", "e1"], evidence()),
        (["e1", 12], evidence()),
        (["e1"], []),
    ):
        result = associate_explanation_evidence(
            candidate_index=0,
            evidence_ids=ids,
            evidence_registry=registry,
        )
        assert result["status"] == "invalid"
        assert result["reason"] is not None
        assert result["evidence_count"] == 0
        assert result["explanation_signal_count"] == 0
        assert result["automatic_linking_authorized"] is False


def test_3796_valid_evidence_remains_observational():
    result = run()
    assert result["status"] == "evidence_associated"
    assert result["reason"] is None
    assert result["source_availability_verified"] is False
    assert result["independently_verified"] is False
    assert result["scorer_decision_performed"] is False



def test_3797_positive_evidence_handoff():
    result = run()
    handoff = result["scorer_evidence_handoff"]
    assert handoff["status"] == "advisory_evidence_available"
    assert handoff["candidate_index"] == 0
    assert handoff["evidence_ids"] == ["e1"]
    assert handoff["evidence_count"] == 1
    assert handoff["evidence_sources"] == ["semantic_memory"]


def test_3797_no_evidence_handoff_abstains():
    handoff = run(ids=[])["scorer_evidence_handoff"]
    assert handoff["status"] == "no_evidence"
    assert handoff["evidence_ids"] == []
    assert handoff["evidence_count"] == 0
    assert handoff["candidate_score"] is None


def test_3797_invalid_evidence_not_handed_off():
    result = run(ids=["missing"])
    handoff = result["scorer_evidence_handoff"]
    assert result["status"] == "invalid"
    assert handoff["evidence_count"] == 0
    assert handoff["evidence_ids"] == []
    assert handoff["status"] == "no_evidence"


def test_3797_multiple_evidence_sources_ordered():
    registry = evidence()
    registry["e2"] = {
        "candidate_index": 0,
        "source": "intelligence_graph",
        "evidence_type": "graph_relationship_observation",
        "certified": False,
    }
    result = run(ids=["e2", "e1"], registry=registry)
    handoff = result["scorer_evidence_handoff"]
    assert handoff["evidence_ids"] == ["e2", "e1"]
    assert handoff["evidence_sources"] == [
        "intelligence_graph", "semantic_memory"
    ]


def test_3797_handoff_never_decides_links():
    handoff = run()["scorer_evidence_handoff"]
    assert handoff["candidate_score"] is None
    assert handoff["link_target"] is None
    assert handoff["scorer_decision"] is None
    assert handoff["scorer_decision_performed"] is False
    assert handoff["automatic_linking_authorized"] is False
    assert handoff["semantic_evidence_verified"] is False
    assert handoff["independent_validation_required"] is True


def test_3797_no_registry_mutation():
    registry = evidence()
    before = deepcopy(registry)
    result = run(registry=registry)
    assert registry == before
    assert result["scorer_evidence_handoff"]["traceability"] == (
        "registry_references_resolved_unverified"
    )



def test_3798_main_enricher_integration_present():
    import inspect
    from backend.server.engine import semantic_intelligence_enricher

    source = inspect.getsource(semantic_intelligence_enricher)
    assert "explanation_evidence_main_integration_3798" in source
    assert "associate_explanation_evidence(" in source
    assert 'section["evidence_association"] = evidence_association' in source


def test_3798_integration_preserves_existing_explainer_call():
    import inspect
    from backend.server.engine import semantic_intelligence_enricher

    source = inspect.getsource(semantic_intelligence_enricher)
    assert "explain_candidate_evidence(" in source
    assert "section.update(deepcopy(explanation))" in source
    assert source.index(
        "section.update(deepcopy(explanation))"
    ) < source.index("explanation_evidence_main_integration_3798")
