from copy import deepcopy

from backend.server.engine.semantic_intelligence_package_39 import (
    build_semantic_intelligence_package,
)


def fixture():
    selected = [
        {"phrase": "insulin therapy", "id": "occurrence_1"},
        {"phrase": "blood pressure", "id": "occurrence_2"},
    ]
    enriched = [
        {
            "candidate_index": index,
            "original_candidate": deepcopy(candidate),
        }
        for index, candidate in enumerate(selected)
    ]
    registry = {}
    retention = {
        "status": "all_candidates_retained",
        "selected_count": 2,
        "retained_count": 2,
        "retained_candidates": deepcopy(selected),
    }
    advisory = {
        "status": "advisory_handoff_prepared",
        "candidate_count": 2,
        "candidates": [
            {
                "candidate_index": index,
                "original_candidate": deepcopy(candidate),
                "scorer_decision": None,
                "scorer_invoked": False,
                "automatic_linking_authorized": False,
            }
            for index, candidate in enumerate(selected)
        ],
        "scorer_contract_finalized": False,
        "scorer_invoked": False,
        "scorer_decision_performed": False,
        "automatic_linking_authorized": False,
    }
    return selected, enriched, registry, retention, advisory


def build(parts):
    return build_semantic_intelligence_package(
        selected_candidates=parts[0],
        enriched_candidates=parts[1],
        evidence_registry=parts[2],
        sparse_candidate_retention=parts[3],
        sparse_scorer_advisory_handoff=parts[4],
    )


def test_391_versioned_schema():
    result = build(fixture())
    assert result["schema_version"] == "semantic_intelligence_package_v1"
    assert result["status"] == "package_envelope_created"
    assert result["candidate_count"] == 2


def test_391_original_candidates_preserved():
    parts = fixture()
    result = build(parts)
    assert result["original_candidates_preserved"] is True
    assert [e["original_candidate"] for e in
            result["enriched_candidates"]] == parts[0]


def test_391_candidate_count_mismatch():
    parts = list(fixture())
    parts[1] = parts[1][:1]
    result = build(parts)
    assert result["status"] == "invalid"
    assert result["reason"] == "candidate_count_mismatch"


def test_391_candidate_reordering():
    parts = list(fixture())
    parts[1] = list(reversed(parts[1]))
    assert build(parts)["reason"] == "candidate_identity_or_order_mismatch"


def test_391_retention_integrity():
    parts = list(fixture())
    parts[3]["retained_count"] = 1
    assert build(parts)["reason"] == "sparse_retention_contract_mismatch"


def test_391_advisory_integrity():
    parts = list(fixture())
    parts[4]["candidates"][1]["candidate_index"] = 0
    assert build(parts)["reason"] == "sparse_advisory_candidate_mismatch"


def test_391_deep_copy():
    parts = fixture()
    original = deepcopy(parts)
    result = build(parts)
    assert parts == original
    assert result["enriched_candidates"] is not parts[1]
    assert result["evidence_registry"] is not parts[2]


def test_391_no_authorization():
    result = build(fixture())
    for field in (
        "evidence_certification_performed",
        "semantic_certification_performed",
        "scorer_contract_finalized",
        "scorer_invoked",
        "scorer_decision_performed",
        "automatic_linking_authorized",
    ):
        assert result[field] is False



def test_392_identity_record_for_each_candidate():
    parts = fixture()
    result = build(parts)

    assert result["status"] == "package_envelope_created"
    assert len(result["phrase_identity"]) == 2

    for index, record in enumerate(result["phrase_identity"]):
        assert record["candidate_index"] == index
        assert record["original_candidate"] == parts[0][index]
        assert record["identity_status"] == "original_candidate_preserved"
        assert record["identity_modified"] is False
        assert record["identity_invented"] is False


def test_392_duplicate_phrase_occurrences_remain_distinct():
    parts = list(fixture())

    parts[0] = [
        {"phrase": "insulin therapy", "id": "occurrence_1"},
        {"phrase": "insulin therapy", "id": "occurrence_2"},
    ]
    parts[1] = [
        {
            "candidate_index": index,
            "original_candidate": deepcopy(candidate),
        }
        for index, candidate in enumerate(parts[0])
    ]
    parts[3]["retained_candidates"] = deepcopy(parts[0])

    for index, record in enumerate(parts[4]["candidates"]):
        record["original_candidate"] = deepcopy(parts[0][index])

    result = build(parts)

    assert result["status"] == "package_envelope_created"
    identities = result["phrase_identity"]

    assert len(identities) == 2
    assert identities[0]["original_candidate"]["id"] == "occurrence_1"
    assert identities[1]["original_candidate"]["id"] == "occurrence_2"
    assert identities[0]["candidate_index"] == 0
    assert identities[1]["candidate_index"] == 1


def test_392_identity_preserves_nested_original_metadata():
    parts = list(fixture())
    parts[0][0]["metadata"] = {
        "source": "upload_phrase_pool",
        "location": {"section": 2, "offset": 145},
        "tags": ["clinical", "treatment"],
    }

    parts[1][0]["original_candidate"] = deepcopy(parts[0][0])
    parts[3]["retained_candidates"][0] = deepcopy(parts[0][0])
    parts[4]["candidates"][0]["original_candidate"] = deepcopy(
        parts[0][0]
    )

    result = build(parts)

    assert result["status"] == "package_envelope_created"
    assert result["phrase_identity"][0]["original_candidate"] == parts[0][0]
    assert result["phrase_identity"][0]["original_candidate"] is not parts[0][0]


def test_392_identity_has_no_invented_identifier():
    result = build(fixture())

    for record in result["phrase_identity"]:
        assert set(record) == {
            "candidate_index",
            "original_candidate",
            "identity_status",
            "identity_modified",
            "identity_invented",
        }
        assert record["identity_invented"] is False


def test_392_identity_is_independently_copied():
    parts = fixture()
    before = deepcopy(parts)
    result = build(parts)

    assert result["status"] == "package_envelope_created"
    assert parts == before

    result["phrase_identity"][0]["original_candidate"]["phrase"] = (
        "modified in output"
    )

    assert parts == before
    assert result["enriched_candidates"][0][
        "original_candidate"
    ] == before[0][0]


def test_392_invalid_candidate_order_never_publishes_identity():
    parts = list(fixture())
    parts[1][0]["candidate_index"] = 1

    result = build(parts)

    assert result["status"] == "invalid"
    assert result["phrase_identity"] == []
    assert result["reason"] == "candidate_identity_or_order_mismatch"



def test_393_missing_context():
    result = build(fixture())
    assert result["status"] == "package_envelope_created"
    assert len(result["phrase_context"]) == 2
    assert all(
        row["status"] == "not_provided"
        for row in result["phrase_context"]
    )


def test_393_original_context_preserved():
    parts = fixture()
    parts[0][0]["sentence"] = "Insulin therapy is a treatment."
    parts[0][0]["section"] = "Treatment"
    parts[0][0]["start_offset"] = 12
    parts[1][0]["original_candidate"] = deepcopy(parts[0][0])
    parts[3]["retained_candidates"][0] = deepcopy(parts[0][0])
    parts[4]["candidates"][0]["original_candidate"] = deepcopy(
        parts[0][0]
    )

    result = build(parts)
    context = result["phrase_context"][0]
    assert context["status"] == "context_preserved"
    assert context["original_candidate_context"] == {
        "sentence": "Insulin therapy is a treatment.",
        "section": "Treatment",
        "start_offset": 12,
    }


def test_393_enriched_context_preserved():
    parts = fixture()
    parts[1][0]["semantic_context"] = {
        "topic": "diabetes",
        "evidence_status": "unverified",
    }

    result = build(parts)
    context = result["phrase_context"][0]
    assert context["enriched_candidate_context"] == {
        "semantic_context": {
            "topic": "diabetes",
            "evidence_status": "unverified",
        },
    }
    assert context["context_certified"] is False


def test_393_source_and_enriched_context_separate():
    parts = fixture()
    parts[0][0]["context"] = {"source": "original"}
    parts[1][0]["original_candidate"] = deepcopy(parts[0][0])
    parts[3]["retained_candidates"][0] = deepcopy(parts[0][0])
    parts[4]["candidates"][0]["original_candidate"] = deepcopy(
        parts[0][0]
    )
    parts[1][0]["context"] = {"source": "enriched"}

    context = build(parts)["phrase_context"][0]
    assert context["original_candidate_context"]["context"] == {
        "source": "original",
    }
    assert context["enriched_candidate_context"]["context"] == {
        "source": "enriched",
    }


def test_393_context_isolation_and_no_mutation():
    parts = fixture()
    parts[1][0]["semantic_context"] = {
        "nested": {"value": "original"},
    }
    before = deepcopy(parts)
    result = build(parts)

    result["phrase_context"][0][
        "enriched_candidate_context"
    ]["semantic_context"]["nested"]["value"] = "changed"

    assert parts == before
    assert result["enriched_candidates"][0][
        "semantic_context"
    ]["nested"]["value"] == "original"


def test_393_invalid_package_does_not_publish_context():
    parts = fixture()
    parts[1][1]["candidate_index"] = 0
    result = build(parts)
    assert result["status"] == "invalid"
    assert result["phrase_context"] == []


def test_393_context_is_never_invented_or_certified():
    parts = fixture()
    parts[0][0]["section"] = None
    parts[1][0]["original_candidate"] = deepcopy(parts[0][0])
    parts[3]["retained_candidates"][0] = deepcopy(parts[0][0])
    parts[4]["candidates"][0]["original_candidate"] = deepcopy(
        parts[0][0]
    )

    result = build(parts)
    context = result["phrase_context"][0]
    assert context["original_candidate_context"]["section"] is None
    assert context["context_inferred"] is False
    assert context["context_certified"] is False
    assert result["automatic_linking_authorized"] is False



def test_394_semantic_sections_preserved():
    parts = fixture()
    parts[1][0]["semantic_memory"] = {
        "status": "observed",
        "concepts": ["insulin", "therapy"],
    }
    parts[1][0]["intelligence_graph"] = {
        "status": "no_evidence",
        "edges": [],
    }

    result = build(parts)
    assert result["status"] == "package_envelope_created"

    row = result["semantic_intelligence"][0]
    assert row["status"] == "semantic_sections_preserved"
    assert row["sections"]["semantic_memory"] == {
        "status": "observed",
        "concepts": ["insulin", "therapy"],
    }
    assert row["sections"]["intelligence_graph"] == {
        "status": "no_evidence",
        "edges": [],
    }


def test_394_missing_semantic_sections_explicit():
    result = build(fixture())
    assert result["status"] == "package_envelope_created"
    assert len(result["semantic_intelligence"]) == 2

    for row in result["semantic_intelligence"]:
        assert row["status"] == "semantic_sections_not_provided"
        assert row["sections"] == {}
        assert "semantic_memory" in row["missing_section_names"]
        assert "intelligence_graph" in row["missing_section_names"]


def test_394_no_evidence_does_not_become_missing():
    parts = fixture()
    parts[1][0]["semantic_memory"] = {
        "status": "no_evidence",
        "observations": [],
    }

    row = build(parts)["semantic_intelligence"][0]

    assert row["status"] == "semantic_sections_preserved"
    assert row["sections"]["semantic_memory"]["status"] == "no_evidence"
    assert "semantic_memory" not in row["missing_section_names"]


def test_394_invalid_and_stale_states_preserved():
    parts = fixture()
    parts[1][0]["semantic_memory"] = {
        "status": "stale",
    }
    parts[1][0]["intelligence_graph"] = {
        "status": "invalid",
        "reason": "source_error",
    }

    row = build(parts)["semantic_intelligence"][0]

    assert row["sections"]["semantic_memory"]["status"] == "stale"
    assert row["sections"]["intelligence_graph"]["status"] == "invalid"
    assert row["semantic_proof_certified"] is False


def test_394_semantic_sections_are_deep_copied():
    parts = fixture()
    parts[1][0]["intelligence_graph"] = {
        "nested": {"edges": [{"id": "edge_1"}]},
    }
    original = deepcopy(parts)

    result = build(parts)
    result["semantic_intelligence"][0]["sections"][
        "intelligence_graph"
    ]["nested"]["edges"][0]["id"] = "modified"

    assert parts == original
    assert result["enriched_candidates"][0][
        "intelligence_graph"
    ]["nested"]["edges"][0]["id"] == "edge_1"


def test_394_candidate_order_and_isolation():
    parts = fixture()
    parts[1][0]["semantic_memory"] = {"concept": "insulin"}
    parts[1][1]["semantic_memory"] = {"concept": "pressure"}

    result = build(parts)

    assert [
        row["candidate_index"]
        for row in result["semantic_intelligence"]
    ] == [0, 1]
    assert result["semantic_intelligence"][0][
        "sections"
    ]["semantic_memory"]["concept"] == "insulin"
    assert result["semantic_intelligence"][1][
        "sections"
    ]["semantic_memory"]["concept"] == "pressure"


def test_394_invalid_package_never_publishes_semantics():
    parts = fixture()
    parts[1][0]["semantic_memory"] = {"concept": "insulin"}
    parts[1][1]["candidate_index"] = 0

    result = build(parts)

    assert result["status"] == "invalid"
    assert result["semantic_intelligence"] == []


def test_394_semantic_packaging_never_authorizes_links():
    parts = fixture()
    parts[1][0]["intelligence_graph"] = {
        "status": "observed",
        "edges": [{"source": "insulin", "target": "diabetes"}],
    }

    result = build(parts)
    row = result["semantic_intelligence"][0]

    assert row["semantic_inference_performed"] is False
    assert row["semantic_proof_certified"] is False
    assert row["scorer_decision_performed"] is False
    assert row["automatic_linking_authorized"] is False
    assert result["automatic_linking_authorized"] is False



def test_395_reasoning_output_preserved():
    parts = fixture()
    parts[1][0]["reasoning_intelligence"] = {
        "status": "observational_signals_found",
        "evidence_ids": ["ev_1"],
        "signals": [
            {"relation": "associated", "target": "diabetes"}
        ],
    }

    result = build(parts)
    assert result["status"] == "package_envelope_created"

    row = result["reasoning"][0]
    assert row["candidate_index"] == 0
    assert row["status"] == "reasoning_preserved"
    assert row["reasoning_output"] == (
        parts[1][0]["reasoning_intelligence"]
    )
    assert row["source_status"] == "observational_signals_found"


def test_395_missing_reasoning_explicit():
    result = build(fixture())

    assert len(result["reasoning"]) == 2
    for row in result["reasoning"]:
        assert row["status"] == "reasoning_not_provided"
        assert row["reasoning_available"] is False
        assert row["reasoning_output"] is None
        assert row["source_status"] is None


def test_395_no_evidence_preserved_without_inference():
    parts = fixture()
    parts[1][0]["reasoning_intelligence"] = {
        "status": "no_evidence",
        "signals": [],
    }

    row = build(parts)["reasoning"][0]

    assert row["status"] == "reasoning_preserved"
    assert row["source_status"] == "no_evidence"
    assert row["reasoning_output"]["signals"] == []
    assert row["independent_reasoning_verified"] is False


def test_395_error_stale_and_invalid_states_preserved():
    for status in ("unavailable", "error", "stale", "invalid"):
        parts = fixture()
        parts[1][0]["reasoning_intelligence"] = {
            "status": status,
            "reason": "source_reported_state",
        }

        result = build(parts)
        assert result["status"] == "package_envelope_created"
        row = result["reasoning"][0]
        assert row["source_status"] == status
        assert row["reasoning_output"]["reason"] == (
            "source_reported_state"
        )
        assert row["semantic_proof_certified"] is False


def test_395_reasoning_isolation_and_deep_copy():
    parts = fixture()
    parts[1][0]["reasoning_intelligence"] = {
        "status": "observed",
        "nested": {"items": [{"value": "insulin"}]},
    }
    parts[1][1]["reasoning_intelligence"] = {
        "status": "observed",
        "nested": {"items": [{"value": "pressure"}]},
    }

    before = deepcopy(parts)
    result = build(parts)

    result["reasoning"][0]["reasoning_output"][
        "nested"
    ]["items"][0]["value"] = "modified"

    assert parts == before
    assert result["enriched_candidates"][0][
        "reasoning_intelligence"
    ]["nested"]["items"][0]["value"] == "insulin"
    assert result["reasoning"][1]["reasoning_output"][
        "nested"
    ]["items"][0]["value"] == "pressure"


def test_395_malformed_reasoning_fails_closed():
    for malformed in (None, [], "observed", 0):
        parts = fixture()
        parts[1][0]["reasoning_intelligence"] = malformed

        result = build(parts)
        assert result["status"] == "invalid"
        assert result["reason"] == "invalid_reasoning_section"
        assert result["reasoning"] == []
        assert result["automatic_linking_authorized"] is False

    parts = fixture()
    parts[1][0]["reasoning_intelligence"] = {
        "status": 123,
    }
    result = build(parts)
    assert result["reason"] == "invalid_reasoning_status"
    assert result["reasoning"] == []


def test_395_reasoning_does_not_make_linking_decisions():
    parts = fixture()
    parts[1][0]["reasoning_intelligence"] = {
        "status": "observed",
        "signals": [{"relation": "related"}],
    }

    result = build(parts)
    row = result["reasoning"][0]

    assert row["reasoning_executed_by_package"] is False
    assert row["independent_reasoning_verified"] is False
    assert row["semantic_proof_certified"] is False
    assert row["scorer_decision_performed"] is False
    assert row["automatic_linking_authorized"] is False
    assert result["scorer_invoked"] is False
    assert result["automatic_linking_authorized"] is False



def confidence_fixture():
    parts = fixture()
    producer = {
        "schema_version": "confidence_evidence_v1",
        "status": "source_confidence_preserved",
        "source_count": 1,
        "confidence_records": [{
            "evidence_id": "ev_1",
            "concept_confidence": 0.35,
            "evidence_confidence": 0.42,
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
        "automatic_linking_authorized": False,
    }
    parts[1][0]["intelligence_graph"] = {
        "semantic_relationship_confidence_evidence": deepcopy(producer),
    }
    parts[1][0]["sparse_intelligence"] = {
        "candidate_index": 0,
        "original_candidate": deepcopy(parts[0][0]),
        "candidate_retained": True,
        "confidence_score": None,
        "low_confidence_state": "unknown",
        "confidence_evidence_context": deepcopy(producer),
        "phrase_confidence_established": False,
        "scorer_decision_performed": False,
        "automatic_linking_authorized": False,
    }
    return parts


def test_396_confidence_evidence_preserved():
    parts = confidence_fixture()
    result = build(parts)
    assert result["status"] == "package_envelope_created"
    row = result["confidence"][0]
    assert row["status"] == "confidence_evidence_preserved"
    assert row["source_confidence_evidence"] == (
        parts[1][0]["intelligence_graph"][
            "semantic_relationship_confidence_evidence"
        ]
    )
    assert row["low_confidence_state"] == "unknown"
    assert row["phrase_level_confidence"] is None


def test_396_missing_confidence_explicit():
    result = build(fixture())
    assert result["status"] == "package_envelope_created"
    assert len(result["confidence"]) == 2
    assert all(
        row["status"] == "confidence_not_provided"
        and row["low_confidence_state"] == "not_provided"
        and row["source_confidence_evidence"] is None
        for row in result["confidence"]
    )


def test_396_low_confidence_without_producer_preserved():
    parts = fixture()
    parts[1][0]["sparse_intelligence"] = {
        "candidate_index": 0,
        "original_candidate": deepcopy(parts[0][0]),
        "candidate_retained": True,
        "confidence_score": None,
        "low_confidence_state": "not_assessable",
        "confidence_evidence_context": None,
        "phrase_confidence_established": False,
        "scorer_decision_performed": False,
        "automatic_linking_authorized": False,
    }
    row = build(parts)["confidence"][0]
    assert row["status"] == "sparse_confidence_preserved"
    assert row["low_confidence_state"] == "not_assessable"


def test_396_no_aggregation_or_threshold_invention():
    result = build(confidence_fixture())
    row = result["confidence"][0]
    assert row["phrase_level_confidence"] is None
    assert row["phrase_confidence_established"] is False
    assert row["source_confidence_aggregated_by_package"] is False
    assert row["confidence_calibrated_by_package"] is False
    assert row["semantic_proof_certified"] is False


def test_396_mismatched_producer_context_fails_closed():
    parts = confidence_fixture()
    parts[1][0]["sparse_intelligence"][
        "confidence_evidence_context"
    ]["confidence_records"][0]["evidence_id"] = "wrong"
    result = build(parts)
    assert result["status"] == "invalid"
    assert result["reason"] == "confidence_producer_handoff_mismatch"
    assert result["confidence"] == []


def test_396_unauthorized_phrase_confidence_rejected():
    parts = confidence_fixture()
    producer = parts[1][0]["intelligence_graph"][
        "semantic_relationship_confidence_evidence"
    ]
    producer["confidence_records"][0][
        "phrase_level_semantic_confidence"
    ] = 0.91
    result = build(parts)
    assert result["reason"] == "unsupported_phrase_confidence_claim"

    parts = confidence_fixture()
    parts[1][0]["sparse_intelligence"][
        "low_confidence_state"
    ] = "low_confidence"
    result = build(parts)
    assert result["reason"] == "unverified_confidence_classification"


def test_396_confidence_records_are_isolated():
    parts = confidence_fixture()
    before = deepcopy(parts)
    result = build(parts)
    result["confidence"][0]["source_confidence_evidence"][
        "confidence_records"
    ][0]["concept_confidence"] = 0.99

    assert parts == before
    assert result["enriched_candidates"][0][
        "intelligence_graph"
    ]["semantic_relationship_confidence_evidence"][
        "confidence_records"
    ][0]["concept_confidence"] == 0.35


def test_396_candidate_order_and_no_linking_authority():
    result = build(confidence_fixture())
    assert [r["candidate_index"] for r in result["confidence"]] == [0, 1]
    assert all(
        r["scorer_decision_performed"] is False
        and r["automatic_linking_authorized"] is False
        for r in result["confidence"]
    )
    assert result["scorer_invoked"] is False
    assert result["automatic_linking_authorized"] is False



def explainability_fixture():
    parts = fixture()
    parts[2]["ev_1"] = {
        "candidate_index": 0,
        "source": "existing_evidence",
        "certified": False,
    }
    parts[1][0]["explainability"] = {
        "status": "evidence_explained",
        "evidence_association": {
            "evidence_ids": ["ev_1"],
            "evidence_count": 1,
            "independently_verified": False,
            "semantic_proof_certified": False,
            "automatic_linking_authorized": False,
        },
        "explanation_signals": [
            {"source": "semantic_relationship", "status": "observed"}
        ],
    }
    return parts


def test_397_explainability_preserved():
    parts = explainability_fixture()
    result = build(parts)

    assert result["status"] == "package_envelope_created"
    row = result["explainability"][0]
    assert row["candidate_index"] == 0
    assert row["status"] == "explainability_preserved"
    assert row["source_status"] == "evidence_explained"
    assert row["explanation_output"] == parts[1][0]["explainability"]
    assert row["evidence_ids"] == ["ev_1"]
    assert row["evidence_count"] == 1


def test_397_missing_explainability_explicit():
    result = build(fixture())
    assert len(result["explainability"]) == 2

    for row in result["explainability"]:
        assert row["status"] == "explainability_not_provided"
        assert row["explanation_output"] is None
        assert row["evidence_association"] is None
        assert row["evidence_ids"] == []


def test_397_no_evidence_preserved():
    parts = fixture()
    parts[1][0]["explainability"] = {
        "status": "no_evidence",
        "evidence_association": {
            "evidence_ids": [],
            "evidence_count": 0,
        },
    }
    result = build(parts)
    row = result["explainability"][0]

    assert row["source_status"] == "no_evidence"
    assert row["evidence_count"] == 0
    assert row["status"] == "explainability_preserved"


def test_397_source_failure_states_preserved():
    for state in ("unavailable", "error", "stale", "invalid"):
        parts = fixture()
        parts[1][0]["explainability"] = {
            "status": state,
            "reason": "source_reported_state",
        }
        result = build(parts)
        assert result["status"] == "package_envelope_created"
        assert result["explainability"][0]["source_status"] == state
        assert result["explainability"][0][
            "semantic_proof_certified"
        ] is False


def test_397_unresolved_evidence_fails_closed():
    parts = explainability_fixture()
    del parts[2]["ev_1"]
    result = build(parts)

    assert result["status"] == "invalid"
    assert result["reason"] == "unresolved_explainability_evidence"
    assert result["explainability"] == []


def test_397_cross_candidate_reference_fails_closed():
    parts = explainability_fixture()
    parts[2]["ev_1"]["candidate_index"] = 1
    result = build(parts)

    assert result["status"] == "invalid"
    assert result["reason"] == (
        "cross_candidate_explainability_evidence"
    )
    assert result["explainability"] == []


def test_397_invalid_association_fails_closed():
    parts = explainability_fixture()
    parts[1][0]["explainability"][
        "evidence_association"
    ]["evidence_count"] = 2

    result = build(parts)
    assert result["status"] == "invalid"
    assert result["reason"] == "invalid_explainability_evidence_ids"

    parts = fixture()
    parts[1][0]["explainability"] = None
    result = build(parts)
    assert result["reason"] == "invalid_explainability_section"


def test_397_explainability_isolation_and_no_authorization():
    parts = explainability_fixture()
    before = deepcopy(parts)
    result = build(parts)

    row = result["explainability"][0]
    row["explanation_output"][
        "explanation_signals"
    ][0]["status"] = "changed"

    assert parts == before
    assert result["enriched_candidates"][0][
        "explainability"
    ]["explanation_signals"][0]["status"] == "observed"

    assert [
        record["candidate_index"]
        for record in result["explainability"]
    ] == [0, 1]

    assert row["explanation_generated_by_package"] is False
    assert row["evidence_independently_verified_by_package"] is False
    assert row["semantic_proof_certified"] is False
    assert row["scorer_decision_performed"] is False
    assert row["automatic_linking_authorized"] is False
    assert result["automatic_linking_authorized"] is False



def provenance_fixture():
    parts = explainability_fixture()

    parts[1][0]["explainability"]["provenance"] = {
        "schema_version": "semantic_provenance_bundle_v1",
        "candidate": {
            "evidence_ids": ["ev_1"],
            "status": "evidence_associated",
        },
        "cross_intelligence": {
            "explainability": {"evidence_ids": ["ev_1"]},
        },
        "consistency": {
            "checked_evidence_ids": ["ev_1"],
            "status": "observationally_consistent",
        },
        "independent_provenance_verified": False,
        "semantic_proof_certified": False,
        "scorer_decision_performed": False,
        "automatic_linking_authorized": False,
    }
    return parts


def test_398_existing_provenance_preserved():
    parts = provenance_fixture()
    result = build(parts)

    assert result["status"] == "package_envelope_created"
    record = result["provenance"][0]

    assert record["candidate_index"] == 0
    assert record["status"] == "provenance_preserved"
    assert record["provenance_output"] == (
        parts[1][0]["explainability"]["provenance"]
    )
    assert record["evidence_ids"] == ["ev_1"]
    assert record["evidence_count"] == 1


def test_398_missing_provenance_explicit():
    result = build(fixture())

    assert len(result["provenance"]) == 2
    assert all(
        record["status"] == "provenance_not_provided"
        and record["provenance_output"] is None
        and record["evidence_ids"] == []
        for record in result["provenance"]
    )


def test_398_explanation_without_provenance_not_invented():
    parts = explainability_fixture()
    result = build(parts)

    assert result["status"] == "package_envelope_created"
    assert result["provenance"][0]["status"] == (
        "provenance_not_provided"
    )
    assert result["explainability"][0]["evidence_ids"] == ["ev_1"]


def test_398_provenance_evidence_mismatch_rejected():
    parts = provenance_fixture()
    parts[1][0]["explainability"]["provenance"][
        "consistency"
    ]["checked_evidence_ids"] = ["wrong_id"]

    result = build(parts)
    assert result["status"] == "invalid"
    assert result["reason"] == "provenance_evidence_mismatch"
    assert result["provenance"] == []


def test_398_cross_candidate_provenance_rejected():
    parts = provenance_fixture()
    parts[2]["ev_1"]["candidate_index"] = 1

    result = build(parts)
    assert result["status"] == "invalid"
    assert result["provenance"] == []
    assert result["automatic_linking_authorized"] is False


def test_398_invalid_or_authorizing_provenance_rejected():
    parts = provenance_fixture()
    parts[1][0]["explainability"]["provenance"][
        "independent_provenance_verified"
    ] = True

    result = build(parts)
    assert result["status"] == "invalid"
    assert result["reason"] == "unsupported_provenance_authority"

    parts = provenance_fixture()
    parts[1][0]["explainability"]["provenance"][
        "candidate"
    ] = None

    result = build(parts)
    assert result["reason"] == "invalid_provenance_components"


def test_398_provenance_deep_copy_and_isolation():
    parts = provenance_fixture()
    before = deepcopy(parts)

    result = build(parts)
    result["provenance"][0]["provenance_output"][
        "candidate"
    ]["status"] = "modified"

    assert parts == before
    assert result["enriched_candidates"][0][
        "explainability"
    ]["provenance"]["candidate"]["status"] == (
        "evidence_associated"
    )
    assert result["provenance"][1]["provenance_output"] is None


def test_398_provenance_never_certifies_or_links():
    result = build(provenance_fixture())
    row = result["provenance"][0]

    assert row["provenance_generated_by_package"] is False
    assert row["independent_provenance_verified_by_package"] is False
    assert row["semantic_proof_certified"] is False
    assert row["scorer_decision_performed"] is False
    assert row["automatic_linking_authorized"] is False
    assert result["scorer_invoked"] is False
    assert result["automatic_linking_authorized"] is False



def test_399_uncertified_evidence():
    parts = provenance_fixture()
    result = build(parts)
    assert result["status"] == "package_envelope_created"

    record = result["certification_state"][0]
    assert record["status"] == "evidence_present_uncertified"
    assert record["evidence_ids"] == ["ev_1"]
    assert record["evidence_count"] == 1
    assert record["candidate_certification"] == "not_established"


def test_399_no_evidence_state():
    parts = fixture()
    parts[1][0]["explainability"] = {
        "status": "no_evidence",
        "evidence_association": {
            "evidence_ids": [],
            "evidence_count": 0,
        },
    }
    result = build(parts)
    assert result["status"] == "package_envelope_created"
    assert result["certification_state"][0]["status"] == "no_evidence"


def test_399_missing_certification_not_invented():
    result = build(fixture())
    assert result["status"] == "package_envelope_created"
    assert len(result["certification_state"]) == 2
    assert all(
        row["status"] == "certification_not_established"
        for row in result["certification_state"]
    )


def test_399_certified_registry_claim_fails_closed():
    parts = provenance_fixture()
    parts[2]["ev_1"]["certified"] = True
    result = build(parts)

    assert result["status"] == "invalid"
    assert result["reason"] == "unsupported_evidence_certification"
    assert result["certification_state"] == []


def test_399_association_cannot_claim_certification():
    parts = provenance_fixture()
    parts[1][0]["explainability"][
        "evidence_association"
    ]["semantic_proof_certified"] = True

    result = build(parts)
    assert result["status"] == "invalid"
    assert result["reason"] == "unsupported_certification_authority"


def test_399_sparse_evidence_mismatch_rejected():
    parts = provenance_fixture()
    parts[1][0]["sparse_intelligence"] = {
        "candidate_index": 0,
        "original_candidate": deepcopy(parts[0][0]),
        "candidate_retained": True,
        "confidence_score": None,
        "low_confidence_state": "unknown",
        "confidence_evidence_context": None,
        "phrase_confidence_established": False,
        "scorer_decision_performed": False,
        "automatic_linking_authorized": False,
        "evidence_ids": [],
        "evidence_count": 0,
    }

    result = build(parts)
    assert result["status"] == "invalid"
    assert result["reason"] == "certification_sparse_evidence_mismatch"
    assert result["certification_state"] == []


def test_399_candidate_isolation_and_input_preservation():
    parts = provenance_fixture()
    before = deepcopy(parts)
    result = build(parts)

    assert result["status"] == "package_envelope_created"
    assert [r["candidate_index"] for r in
            result["certification_state"]] == [0, 1]
    assert result["certification_state"][0]["evidence_ids"] == ["ev_1"]
    assert result["certification_state"][1]["evidence_ids"] == []

    result["certification_state"][0]["evidence_ids"].append("changed")
    assert parts == before
    assert result["explainability"][0]["evidence_ids"] == ["ev_1"]


def test_399_package_never_certifies_or_links():
    result = build(provenance_fixture())
    assert result["status"] == "package_envelope_created"

    for record in result["certification_state"]:
        assert record["independent_evidence_verification"] == (
            "not_established"
        )
        assert record["semantic_proof_certification"] == (
            "not_established"
        )
        assert record["candidate_certification"] == "not_established"
        assert record["certification_performed_by_package"] is False
        assert record["scorer_decision_performed"] is False
        assert record["automatic_linking_authorized"] is False

    assert result["semantic_certification_performed"] is False
    assert result["scorer_invoked"] is False
    assert result["automatic_linking_authorized"] is False


def test_399_partial_sparse_inventory_fails_closed():
    parts = confidence_fixture()
    parts[1][0]["sparse_intelligence"]["evidence_ids"] = ["ev_1"]

    result = build(parts)
    assert result["status"] == "invalid"
    assert result["reason"] == "incomplete_sparse_evidence_inventory"



def test_3910_sparse_status_preserved():
    parts = confidence_fixture()
    parts[1][0]["sparse_intelligence"]["status"] = (
        "INSUFFICIENT_INTELLIGENCE"
    )
    result = build(parts)

    assert result["status"] == "package_envelope_created"
    row = result["intelligence_status"][0]
    assert row["source_statuses"]["sparse_intelligence"] == (
        "INSUFFICIENT_INTELLIGENCE"
    )
    assert row["overall_intelligence_readiness"] == "not_determined"


def test_3910_missing_status_sources_explicit():
    result = build(fixture())
    assert result["status"] == "package_envelope_created"
    assert len(result["intelligence_status"]) == 2

    for row in result["intelligence_status"]:
        assert row["status"] == "source_statuses_not_provided"
        assert row["source_statuses"] == {}
        assert "sparse_intelligence" in row["missing_source_sections"]
        assert "reasoning_intelligence" in row["missing_source_sections"]


def test_3910_distinct_source_failure_states_preserved():
    parts = fixture()
    parts[1][0]["reasoning_intelligence"] = {"status": "error"}
    parts[1][0]["semantic_memory"] = {"status": "stale"}
    parts[1][0]["intelligence_graph"] = {"status": "no_evidence"}
    parts[1][0]["scorer_readiness"] = {"status": "invalid"}

    result = build(parts)
    assert result["status"] == "package_envelope_created"

    states = result["intelligence_status"][0]["source_statuses"]
    assert states["reasoning_intelligence"] == "error"
    assert states["semantic_memory"] == "stale"
    assert states["intelligence_graph"] == "no_evidence"
    assert states["scorer_readiness"] == "invalid"


def test_3910_absent_status_distinct_from_missing_section():
    parts = fixture()
    parts[1][0]["semantic_memory"] = {
        "observations": [],
    }

    result = build(parts)
    row = result["intelligence_status"][0]

    assert row["source_statuses"]["semantic_memory"] is None
    assert "semantic_memory" not in row["missing_source_sections"]
    assert row["overall_intelligence_readiness"] == "not_determined"


def test_3910_package_statuses_match_existing_sections():
    result = build(provenance_fixture())
    assert result["status"] == "package_envelope_created"

    sections = (
        "phrase_context",
        "semantic_intelligence",
        "reasoning",
        "confidence",
        "explainability",
        "provenance",
        "certification_state",
    )

    for index, row in enumerate(result["intelligence_status"]):
        for section in sections:
            assert row["packaged_section_statuses"][section] == (
                result[section][index]["status"]
            )


def test_3910_invalid_source_status_fails_closed():
    parts = fixture()
    parts[1][0]["scorer_readiness"] = {"status": True}

    result = build(parts)
    assert result["status"] == "invalid"
    assert result["reason"] == "invalid_intelligence_source_status"
    assert result["intelligence_status"] == []


def test_3910_status_records_independently_copied():
    parts = fixture()
    parts[1][0]["semantic_memory"] = {
        "status": "unavailable",
    }
    before = deepcopy(parts)
    result = build(parts)

    assert result["status"] == "package_envelope_created"
    result["intelligence_status"][0][
        "source_statuses"
    ]["semantic_memory"] = "modified"

    assert parts == before
    assert result["enriched_candidates"][0][
        "semantic_memory"
    ]["status"] == "unavailable"
    assert result["intelligence_status"][1][
        "source_statuses"
    ] == {}


def test_3910_status_packaging_never_authorizes_linking():
    result = build(provenance_fixture())
    assert result["status"] == "package_envelope_created"

    assert [
        record["candidate_index"]
        for record in result["intelligence_status"]
    ] == [0, 1]

    for row in result["intelligence_status"]:
        assert row["overall_intelligence_readiness"] == "not_determined"
        assert row["semantic_validity_certified"] is False
        assert row["status_inference_performed_by_package"] is False
        assert row["scorer_decision_performed"] is False
        assert row["automatic_linking_authorized"] is False

    assert result["scorer_invoked"] is False
    assert result["automatic_linking_authorized"] is False
