from copy import deepcopy

from backend.server.engine.semantic_intelligence_explanation_evidence_379 import (
    associate_explanation_evidence,
)
from backend.server.engine.semantic_intelligence_sparse_38 import (
    assess_sparse_intelligence,
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


def run(ids=None, index=0, candidate=None, association=None):
    if ids is None:
        ids = ["e1"]
    if association is None:
        association = associate_explanation_evidence(
            candidate_index=0,
            evidence_ids=ids,
            evidence_registry=evidence(),
        )
    return assess_sparse_intelligence(
        candidate_index=index,
        original_candidate=(
            {"phrase": "insulin therapy", "occurrence": 1}
            if candidate is None else candidate
        ),
        evidence_association=association,
    )


def test_381_no_evidence_is_insufficient():
    result = run(ids=[])
    assert result["status"] == "INSUFFICIENT_INTELLIGENCE"
    assert result["reason"] == "no_associated_evidence"
    assert result["candidate_retained"] is True
    assert result["evidence_count"] == 0


def test_381_evidence_present_does_not_prove_sufficiency():
    result = run()
    assert result["status"] == "EVIDENCE_PRESENT_UNVERIFIED"
    assert result["evidence_ids"] == ["e1"]
    assert result["confidence_status"] == "not_assessed"


def test_381_never_fabricates_confidence():
    for ids in ([], ["e1"]):
        result = run(ids=ids)
        assert result["confidence_score"] is None
        assert result["semantic_certification_performed"] is False


def test_381_selected_candidate_is_preserved():
    candidate = {"phrase": "blood pressure", "metadata": {"x": 1}}
    before = deepcopy(candidate)
    result = run(ids=[], candidate=candidate)
    assert result["original_candidate"] == before
    assert candidate == before


def test_381_cross_candidate_rejected():
    result = run(index=2)
    assert result["status"] == "invalid"
    assert result["reason"] == "candidate_attribution_mismatch"
    assert result["candidate_retained"] is False


def test_381_bad_association_rejected():
    association = associate_explanation_evidence(
        candidate_index=0,
        evidence_ids=["missing"],
        evidence_registry=evidence(),
    )
    result = run(association=association)
    assert result["status"] == "invalid"


def test_381_count_mismatch_rejected():
    association = associate_explanation_evidence(
        candidate_index=0,
        evidence_ids=["e1"],
        evidence_registry=evidence(),
    )
    association["evidence_count"] = 3
    result = run(association=association)
    assert result["reason"] == "invalid_evidence_association_contract"


def test_381_no_linking_or_scorer_decision():
    for ids in ([], ["e1"]):
        result = run(ids=ids)
        assert result["scorer_handoff_status"] == "advisory_only"
        assert result["scorer_decision_performed"] is False
        assert result["automatic_linking_authorized"] is False
        assert result["source_availability"] == "not_assessed"



def test_383_absent_source_states_not_inferred():
    result = run(ids=[])
    assert result["source_states"] == {}
    assert result["source_issues"] == []
    assert result["source_availability"] == "not_assessed"


def test_383_explicit_no_evidence_not_source_failure():
    result = assess_sparse_intelligence(
        candidate_index=0,
        original_candidate={"phrase": "diabetes treatment"},
        evidence_association=associate_explanation_evidence(
            candidate_index=0,
            evidence_ids=[],
            evidence_registry=evidence(),
        ),
        source_states={"semantic_memory": "no_evidence"},
    )
    assert result["status"] == "INSUFFICIENT_INTELLIGENCE"
    assert result["source_issue_count"] == 0
    assert result["source_availability"] == "reported_no_issues"


def test_383_unavailable_source_is_not_fabricated_no_evidence():
    association = associate_explanation_evidence(
        candidate_index=0,
        evidence_ids=[],
        evidence_registry=evidence(),
    )
    result = assess_sparse_intelligence(
        candidate_index=0,
        original_candidate={"phrase": "insulin therapy"},
        evidence_association=association,
        source_states={"intelligence_graph": "unavailable"},
    )
    assert result["status"] == "INSUFFICIENT_INTELLIGENCE"
    assert result["source_issues"][0]["state"] == "unavailable"
    assert result["source_availability"] == "issues_reported"
    assert result["confidence_score"] is None


def test_383_errors_and_stale_sources_remain_distinct():
    association = associate_explanation_evidence(
        candidate_index=0,
        evidence_ids=["e1"],
        evidence_registry=evidence(),
    )
    result = assess_sparse_intelligence(
        candidate_index=0,
        original_candidate={"phrase": "blood pressure"},
        evidence_association=association,
        source_states={
            "semantic_memory": "stale",
            "intelligence_graph": "error",
            "reasoning_intelligence": "available",
        },
    )
    assert result["status"] == "EVIDENCE_PRESENT_UNVERIFIED"
    assert result["source_issue_count"] == 2
    assert [item["state"] for item in result["source_issues"]] == [
        "stale", "error"
    ]


def test_383_unknown_states_fail_closed():
    association = associate_explanation_evidence(
        candidate_index=0,
        evidence_ids=[],
        evidence_registry=evidence(),
    )
    for invalid in (
        {"unknown_provider": "available"},
        {"semantic_memory": "verified"},
        {"semantic_memory": None},
    ):
        result = assess_sparse_intelligence(
            candidate_index=0,
            original_candidate={"phrase": "example"},
            evidence_association=association,
            source_states=invalid,
        )
        assert result["status"] == "invalid"
        assert result["reason"] == "unknown_or_invalid_source_state"
        assert result["candidate_retained"] is False


def test_383_source_input_preserved_and_no_authority():
    association = associate_explanation_evidence(
        candidate_index=0,
        evidence_ids=[],
        evidence_registry=evidence(),
    )
    states = {
        "semantic_memory": "unavailable",
        "intelligence_graph": "no_evidence",
    }
    original = deepcopy(states)
    result = assess_sparse_intelligence(
        candidate_index=0,
        original_candidate={"phrase": "insulin therapy"},
        evidence_association=association,
        source_states=states,
    )
    assert states == original
    assert result["source_states"] == original
    assert result["candidate_retained"] is True
    assert result["scorer_decision_performed"] is False
    assert result["automatic_linking_authorized"] is False



def retention_fixture():
    from backend.server.engine.semantic_intelligence_sparse_38 import (
        validate_sparse_candidate_retention,
    )

    selected = [
        {"phrase": "insulin therapy", "selection_occurrence_id": "o1"},
        {"phrase": "blood pressure", "selection_occurrence_id": "o2"},
    ]
    assessments = []

    for index, candidate in enumerate(selected):
        ids = [] if index == 0 else ["e1"]
        registry = {
            "e1": {
                "candidate_index": index,
                "source": "semantic_memory",
                "evidence_type": "semantic_memory_match",
                "certified": False,
            }
        }
        association = associate_explanation_evidence(
            candidate_index=index,
            evidence_ids=ids,
            evidence_registry=registry,
        )
        assessments.append(
            assess_sparse_intelligence(
                candidate_index=index,
                original_candidate=candidate,
                evidence_association=association,
            )
        )

    return selected, assessments, validate_sparse_candidate_retention


def test_384_all_selected_candidates_retained():
    selected, assessments, validate = retention_fixture()
    result = validate(
        selected_candidates=selected,
        sparse_assessments=assessments,
    )
    assert result["status"] == "all_candidates_retained"
    assert result["selected_count"] == 2
    assert result["retained_count"] == 2
    assert result["retained_candidates"] == selected


def test_384_insufficient_candidate_not_discarded():
    selected, assessments, validate = retention_fixture()
    result = validate(
        selected_candidates=selected,
        sparse_assessments=assessments,
    )
    assert result["sparse_count"] == 1
    assert result["evidence_present_count"] == 1
    assert result["retained_candidates"][0] == selected[0]


def test_384_missing_assessment_rejected():
    selected, assessments, validate = retention_fixture()
    result = validate(
        selected_candidates=selected,
        sparse_assessments=assessments[:1],
    )
    assert result["reason"] == "candidate_count_mismatch"
    assert result["retained_candidates"] == []


def test_384_reordered_assessment_rejected():
    selected, assessments, validate = retention_fixture()
    result = validate(
        selected_candidates=selected,
        sparse_assessments=list(reversed(assessments)),
    )
    assert result["reason"] == "candidate_identity_or_order_mismatch"


def test_384_changed_candidate_rejected():
    selected, assessments, validate = retention_fixture()
    assessments[1]["original_candidate"]["phrase"] = "changed"
    result = validate(
        selected_candidates=selected,
        sparse_assessments=assessments,
    )
    assert result["reason"] == "candidate_not_preserved"


def test_384_duplicate_index_rejected():
    selected, assessments, validate = retention_fixture()
    assessments[1]["candidate_index"] = 0
    result = validate(
        selected_candidates=selected,
        sparse_assessments=assessments,
    )
    assert result["reason"] == "candidate_identity_or_order_mismatch"


def test_384_no_mutation_or_link_authorization():
    selected, assessments, validate = retention_fixture()
    original = deepcopy((selected, assessments))
    result = validate(
        selected_candidates=selected,
        sparse_assessments=assessments,
    )
    assert (selected, assessments) == original
    assert result["candidate_deletion_performed"] is False
    assert result["candidate_reordering_performed"] is False
    assert result["scorer_decision_performed"] is False
    assert result["automatic_linking_authorized"] is False



def test_385_all_candidates_prepared_in_original_order():
    from backend.server.engine.semantic_intelligence_sparse_38 import (
        prepare_sparse_scorer_handoff,
    )
    selected, assessments, _ = retention_fixture()
    result = prepare_sparse_scorer_handoff(
        selected_candidates=selected,
        sparse_assessments=assessments,
    )
    assert result["status"] == "advisory_handoff_prepared"
    assert result["candidate_count"] == 2
    assert [x["candidate_index"] for x in result["candidates"]] == [0, 1]
    assert [x["original_candidate"] for x in result["candidates"]] == selected


def test_385_insufficient_candidate_is_not_discarded():
    from backend.server.engine.semantic_intelligence_sparse_38 import (
        prepare_sparse_scorer_handoff,
    )
    selected, assessments, _ = retention_fixture()
    result = prepare_sparse_scorer_handoff(
        selected_candidates=selected,
        sparse_assessments=assessments,
    )
    assert result["insufficient_intelligence_count"] == 1
    assert result["evidence_present_count"] == 1
    assert result["candidates"][0]["intelligence_status"] == (
        "INSUFFICIENT_INTELLIGENCE"
    )
    assert result["candidates"][0]["evidence_ids"] == []
    assert result["candidates"][1]["evidence_ids"] == ["e1"]


def test_385_source_issues_preserved_without_inference():
    from backend.server.engine.semantic_intelligence_sparse_38 import (
        prepare_sparse_scorer_handoff,
    )
    selected, assessments, _ = retention_fixture()
    association = associate_explanation_evidence(
        candidate_index=0,
        evidence_ids=[],
        evidence_registry=evidence(),
    )
    assessments[0] = assess_sparse_intelligence(
        candidate_index=0,
        original_candidate=selected[0],
        evidence_association=association,
        source_states={"semantic_memory": "unavailable"},
    )
    result = prepare_sparse_scorer_handoff(
        selected_candidates=selected,
        sparse_assessments=assessments,
    )
    assert result["status"] == "advisory_handoff_prepared"
    assert result["candidates"][0]["source_states"] == {
        "semantic_memory": "unavailable"
    }
    assert result["candidates"][0]["source_issues"][0]["state"] == (
        "unavailable"
    )


def test_385_missing_assessment_fails_closed():
    from backend.server.engine.semantic_intelligence_sparse_38 import (
        prepare_sparse_scorer_handoff,
    )
    selected, assessments, _ = retention_fixture()
    result = prepare_sparse_scorer_handoff(
        selected_candidates=selected,
        sparse_assessments=assessments[:1],
    )
    assert result["status"] == "invalid"
    assert result["candidates"] == []
    assert result["candidate_count"] == 0


def test_385_invalid_later_candidate_prevents_partial_handoff():
    from backend.server.engine.semantic_intelligence_sparse_38 import (
        prepare_sparse_scorer_handoff,
    )
    selected, assessments, _ = retention_fixture()
    assessments[1]["scorer_handoff_status"] = "authorized"
    result = prepare_sparse_scorer_handoff(
        selected_candidates=selected,
        sparse_assessments=assessments,
    )
    assert result["status"] == "invalid"
    assert result["reason"] == "invalid_advisory_assessment"
    assert result["candidates"] == []


def test_385_no_mutation_scoring_or_link_authorization():
    from backend.server.engine.semantic_intelligence_sparse_38 import (
        prepare_sparse_scorer_handoff,
    )
    selected, assessments, _ = retention_fixture()
    before = deepcopy((selected, assessments))
    result = prepare_sparse_scorer_handoff(
        selected_candidates=selected,
        sparse_assessments=assessments,
    )
    assert (selected, assessments) == before
    assert result["scorer_contract_finalized"] is False
    assert result["scorer_invoked"] is False
    assert result["scorer_decision_performed"] is False
    assert result["automatic_linking_authorized"] is False
    assert all(
        item["scorer_decision"] is None
        and item["confidence_score"] is None
        and item["automatic_linking_authorized"] is False
        for item in result["candidates"]
    )



def test_386_main_enricher_sparse_integration_present():
    import inspect
    from backend.server.engine import semantic_intelligence_enricher

    source = inspect.getsource(semantic_intelligence_enricher)
    assert "sparse_main_integration_386" in source
    assert "assess_sparse_intelligence(" in source
    assert 'entry["sparse_intelligence"] = sparse_assessment' in source


def test_386_existing_explainability_and_provenance_preserved():
    import inspect
    from backend.server.engine import semantic_intelligence_enricher

    source = inspect.getsource(semantic_intelligence_enricher)

    assert "explain_candidate_evidence(" in source
    assert 'section["evidence_association"] = evidence_association' in source
    assert "provenance_main_integration_37108" in source

    assert source.index(
        'section["evidence_association"] = evidence_association'
    ) < source.index("sparse_main_integration_386")

    assert source.index(
        "sparse_main_integration_386"
    ) < source.index("provenance_main_integration_37108")


def test_386_main_enricher_does_not_infer_source_availability():
    import inspect
    from backend.server.engine import semantic_intelligence_enricher

    source = inspect.getsource(semantic_intelligence_enricher)
    start = source.index("sparse_main_integration_386")
    end = source.index("provenance_main_integration_37108")
    integration = source[start:end]

    assert "source_states=" not in integration
    assert "scorer_decision" not in integration
    assert "automatic_linking_authorized = True" not in integration



def test_386b_batch_integration_is_at_final_return():
    import ast
    import inspect
    from backend.server.engine import semantic_intelligence_enricher

    source = inspect.getsource(
        semantic_intelligence_enricher.enrich_selected_phrase_candidates
    )
    tree = ast.parse(source)
    fn = tree.body[0]

    assert isinstance(fn.body[-1], ast.Return)
    assert fn.body[-1].value.id == "package"
    assert "sparse_batch_integration_386b" in source
    assert "validate_sparse_candidate_retention(" in source
    assert "prepare_sparse_scorer_handoff(" in source


def test_386b_batch_handoff_preserves_existing_outputs():
    import inspect
    from backend.server.engine import semantic_intelligence_enricher

    source = inspect.getsource(
        semantic_intelligence_enricher.enrich_selected_phrase_candidates
    )

    assert 'package["sparse_candidate_retention"]' in source
    assert 'package["sparse_scorer_advisory_handoff"]' in source
    assert 'entry["sparse_intelligence"] = sparse_assessment' in source
    assert 'section["provenance"]' in source
    assert "sparse_main_integration_386" in source



def confidence_assessment(ids, signal):
    association = associate_explanation_evidence(
        candidate_index=0,
        evidence_ids=ids,
        evidence_registry=evidence(),
    )
    return assess_sparse_intelligence(
        candidate_index=0,
        original_candidate={"phrase": "insulin therapy"},
        evidence_association=association,
        confidence_signal=signal,
    )


def test_382_missing_evidence_is_not_low_confidence():
    result = confidence_assessment([], None)
    assert result["status"] == "INSUFFICIENT_INTELLIGENCE"
    assert result["low_confidence_state"] == "not_assessable"
    assert result["confidence_score"] is None


def test_382_evidence_without_indicator_is_unknown():
    result = confidence_assessment(["e1"], None)
    assert result["status"] == "EVIDENCE_PRESENT_UNVERIFIED"
    assert result["low_confidence_state"] == "unknown"
    assert result["confidence_signal_source"] is None


def test_382_explicit_low_confidence():
    result = confidence_assessment(
        ["e1"],
        {"state": "low_confidence", "source": "confidence_evidence"},
    )
    assert result["low_confidence_state"] == "low_confidence"
    assert result["candidate_retained"] is True
    assert result["confidence_signal_verified"] is False


def test_382_explicit_not_low_confidence():
    result = confidence_assessment(
        ["e1"],
        {
            "state": "not_low_confidence",
            "source": "reasoning_intelligence",
        },
    )
    assert result["low_confidence_state"] == "not_low_confidence"
    assert result["semantic_certification_performed"] is False


def test_382_missing_evidence_rejects_confidence_claim():
    result = confidence_assessment(
        [],
        {"state": "low_confidence", "source": "confidence_evidence"},
    )
    assert result["status"] == "invalid"
    assert result["reason"] == "confidence_without_associated_evidence"


def test_382_invalid_signal_fails_closed():
    for signal in (
        {},
        {"state": "high", "source": "confidence_evidence"},
        {"state": "low_confidence", "source": "unknown"},
        {"state": "low_confidence"},
        {"state": 0.2, "source": "confidence_evidence"},
        {
            "state": "low_confidence",
            "source": "confidence_evidence",
            "certified": True,
        },
    ):
        result = confidence_assessment(["e1"], signal)
        assert result["status"] == "invalid"
        assert result["reason"] == "invalid_confidence_signal"
        assert result["candidate_retained"] is False


def test_382_confidence_input_not_mutated():
    signal = {
        "state": "low_confidence",
        "source": "intelligence_graph",
    }
    before = deepcopy(signal)
    result = confidence_assessment(["e1"], signal)
    assert signal == before
    assert result["confidence_score"] is None


def test_382_low_confidence_is_non_authorizing():
    for state in ("low_confidence", "not_low_confidence"):
        result = confidence_assessment(
            ["e1"],
            {"state": state, "source": "confidence_evidence"},
        )
        assert result["candidate_retained"] is True
        assert result["scorer_decision_performed"] is False
        assert result["automatic_linking_authorized"] is False
        assert result["semantic_certification_performed"] is False



def test_382_producer_context_preserved_without_calibration():
    from copy import deepcopy

    data = {
        "schema_version": "confidence_evidence_v1",
        "status": "source_confidence_preserved",
        "source_count": 1,
        "confidence_records": [{
            "evidence_id": "e1",
            "concept_confidence": 0.21,
            "evidence_confidence": 0.31,
            "phrase_level_semantic_confidence": None,
            "selected_phrase_confidence_authorized": False,
            "confidence_calibrated": False,
            "independently_verified": False,
            "certified": False,
        }],
        "overall_confidence": None,
        "overall_confidence_status": "not_established",
        "aggregation_authorized": False,
        "aggregation_performed": False,
        "aggregate_confidence_calibrated": False,
        "semantic_proof_certified": False,
        "linking_decision_performed": False,
        "automatic_linking_authorized": False,
    }

    original = deepcopy(data)
    association = associate_explanation_evidence(
        candidate_index=0,
        evidence_ids=["e1"],
        evidence_registry=evidence(),
    )

    result = assess_sparse_intelligence(
        candidate_index=0,
        original_candidate={"phrase": "insulin therapy"},
        evidence_association=association,
        confidence_evidence=data,
    )
    assert result["status"] == "EVIDENCE_PRESENT_UNVERIFIED"
    assert result["low_confidence_state"] == "unknown"
    assert result["confidence_score"] is None
    assert result["phrase_confidence_established"] is False
    assert result["confidence_evidence_context"] == original
    assert result["confidence_evidence_context"] is not data
    assert data == original


def test_382_rejects_producer_aggregation_claim():
    data = {
        "schema_version": "confidence_evidence_v1",
        "status": "source_confidence_preserved",
        "source_count": 0,
        "confidence_records": [],
        "overall_confidence": 0.8,
        "overall_confidence_status": "not_established",
        "aggregation_authorized": False,
        "aggregation_performed": False,
        "aggregate_confidence_calibrated": False,
        "semantic_proof_certified": False,
        "linking_decision_performed": False,
        "automatic_linking_authorized": False,
    }
    association = associate_explanation_evidence(
        candidate_index=0,
        evidence_ids=["e1"],
        evidence_registry=evidence(),
    )
    result = assess_sparse_intelligence(
        candidate_index=0,
        original_candidate={"phrase": "insulin therapy"},
        evidence_association=association,
        confidence_evidence=data,
    )
    assert result["status"] == "invalid"
    assert result["reason"] == "unsupported_confidence_evidence_contract"


def test_382_conflicting_signal_and_unverified_producer_rejected():
    data = {
        "schema_version": "confidence_evidence_v1",
        "status": "source_confidence_preserved",
        "source_count": 0,
        "confidence_records": [],
        "overall_confidence": None,
        "overall_confidence_status": "not_established",
        "aggregation_authorized": False,
        "aggregation_performed": False,
        "aggregate_confidence_calibrated": False,
        "semantic_proof_certified": False,
        "linking_decision_performed": False,
        "automatic_linking_authorized": False,
    }
    association = associate_explanation_evidence(
        candidate_index=0,
        evidence_ids=["e1"],
        evidence_registry=evidence(),
    )
    result = assess_sparse_intelligence(
        candidate_index=0,
        original_candidate={"phrase": "insulin therapy"},
        evidence_association=association,
        confidence_evidence=data,
        confidence_signal={
            "source": "confidence_evidence",
            "state": "low_confidence",
        },
    )
    assert result["status"] == "invalid"
    assert result["reason"] == "unverified_confidence_signal_conflict"


def test_382_main_enricher_passes_real_confidence_output():
    import inspect
    from backend.server.engine import semantic_intelligence_enricher

    source = inspect.getsource(
        semantic_intelligence_enricher.enrich_selected_phrase_candidates
    )
    assert "sparse_confidence_producer_connection_382" in source
    assert "confidence_evidence=sparse_confidence_evidence" in source
    assert "semantic_relationship_confidence_evidence" in source
