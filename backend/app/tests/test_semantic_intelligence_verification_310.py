"""Phase 3.10 verification ? canonical enrichment package."""

from copy import deepcopy

from backend.app.tests.test_semantic_intelligence_package_39 import (
    confidence_fixture,
    provenance_fixture,
    build,
)


def test_3101_full_intelligence_phrase():
    """Verify a complete evidence-rich, non-certified phrase record."""
    parts = provenance_fixture()
    confidence_parts = confidence_fixture()

    # Combine existing real contract-shaped fixture sections:
    # reasoning, semantic intelligence, confidence, explanation,
    # provenance, context, and certification.
    parts[1][0]["intelligence_graph"] = deepcopy(
        confidence_parts[1][0]["intelligence_graph"]
    )
    parts[1][0]["sparse_intelligence"] = deepcopy(
        confidence_parts[1][0]["sparse_intelligence"]
    )
    parts[1][0]["semantic_memory"] = {
        "status": "observed",
        "concepts": ["insulin therapy", "diabetes treatment"],
        "independently_verified": False,
    }
    parts[1][0]["reasoning_intelligence"] = {
        "status": "observational_signals_found",
        "evidence_ids": ["ev_1"],
        "signals": [{
            "relationship": "associated_with",
            "subject": "insulin therapy",
            "object": "diabetes treatment",
        }],
    }
    parts[1][0]["scorer_readiness"] = {
        "status": "not_certified",
    }

    # Add original text context while preserving every candidate
    # occurrence and the established input contract.
    candidate = parts[0][0]
    candidate["sentence"] = (
        "Insulin therapy is one approach to diabetes treatment."
    )
    candidate["section"] = "Treatment"

    parts[1][0]["original_candidate"] = deepcopy(candidate)
    parts[1][0]["sparse_intelligence"][
        "original_candidate"
    ] = deepcopy(candidate)
    parts[3]["retained_candidates"][0] = deepcopy(candidate)
    parts[4]["candidates"][0]["original_candidate"] = deepcopy(
        candidate
    )

    original_inputs = deepcopy(parts)
    result = build(parts)

    assert result["status"] == "package_envelope_created", (
        f"Full-intelligence package rejected: {result['reason']}"
    )
    assert result["schema_version"] == (
        "semantic_intelligence_package_v1"
    )
    assert result["candidate_count"] == 2
    assert parts == original_inputs

    # Identity and context.
    assert result["phrase_identity"][0]["original_candidate"] == (
        candidate
    )
    assert result["phrase_context"][0][
        "original_candidate_context"
    ]["sentence"] == candidate["sentence"]

    # Semantic observations and reasoning.
    semantic = result["semantic_intelligence"][0]
    assert semantic["sections"]["semantic_memory"]["status"] == (
        "observed"
    )
    assert "intelligence_graph" in semantic["sections"]

    reasoning = result["reasoning"][0]
    assert reasoning["status"] == "reasoning_preserved"
    assert reasoning["reasoning_output"]["evidence_ids"] == [
        "ev_1"
    ]

    # Source-level confidence exists, phrase-level confidence does not.
    confidence = result["confidence"][0]
    assert confidence["status"] == "confidence_evidence_preserved"
    assert confidence["low_confidence_state"] == "unknown"
    assert confidence["source_confidence_evidence"][
        "source_count"
    ] == 1
    assert confidence["phrase_level_confidence"] is None
    assert confidence["phrase_confidence_established"] is False

    # Existing explanation, provenance, and evidence references.
    assert result["explainability"][0]["evidence_ids"] == ["ev_1"]
    assert result["provenance"][0]["evidence_ids"] == ["ev_1"]
    assert result["evidence_registry"]["ev_1"] == parts[2]["ev_1"]

    certification = result["certification_state"][0]
    assert certification["status"] == "evidence_present_uncertified"
    assert certification["candidate_certification"] == (
        "not_established"
    )

    statuses = result["intelligence_status"][0]
    assert statuses["source_statuses"]["semantic_memory"] == (
        "observed"
    )
    assert statuses["source_statuses"][
        "reasoning_intelligence"
    ] == "observational_signals_found"
    assert statuses["overall_intelligence_readiness"] == (
        "not_determined"
    )

    # The second, evidence-sparse candidate remains present.
    assert result["phrase_identity"][1]["original_candidate"] == (
        parts[0][1]
    )
    assert len(result["enriched_candidates"]) == 2

    # No accidental promotion to certification or linking authority.
    assert result["evidence_certification_performed"] is False
    assert result["semantic_certification_performed"] is False
    assert result["scorer_contract_finalized"] is False
    assert result["scorer_invoked"] is False
    assert result["scorer_decision_performed"] is False
    assert result["automatic_linking_authorized"] is False



def sparse_fixture():
    from backend.app.tests.test_semantic_intelligence_package_39 import (
        fixture,
    )

    parts = fixture()
    candidate = parts[0][0]

    parts[1][0]["sparse_intelligence"] = {
        "candidate_index": 0,
        "original_candidate": deepcopy(candidate),
        "candidate_retained": True,
        "status": "INSUFFICIENT_INTELLIGENCE",
        "intelligence_status": "INSUFFICIENT_INTELLIGENCE",
        "evidence_ids": [],
        "evidence_count": 0,
        "confidence_score": None,
        "confidence_evidence_context": None,
        "low_confidence_state": "not_assessable",
        "phrase_confidence_established": False,
        "scorer_decision_performed": False,
        "automatic_linking_authorized": False,
    }

    parts[1][0]["explainability"] = {
        "status": "no_evidence",
        "evidence_association": {
            "evidence_ids": [],
            "evidence_count": 0,
        },
    }

    return parts


def test_3102_sparse_phrase_retained():
    parts = sparse_fixture()
    result = build(parts)

    assert result["status"] == "package_envelope_created", (
        result["reason"]
    )
    assert result["candidate_count"] == len(parts[0]) == 2
    assert result["original_candidates_preserved"] is True
    assert result["phrase_identity"][0][
        "original_candidate"
    ] == parts[0][0]
    assert result["enriched_candidates"][0][
        "original_candidate"
    ] == parts[0][0]
    assert result["sparse_candidate_retention"][
        "retained_candidates"
    ] == parts[0]
    assert result["sparse_scorer_advisory_handoff"][
        "candidate_count"
    ] == 2


def test_3102_sparse_missing_evidence_and_confidence():
    result = build(sparse_fixture())
    assert result["status"] == "package_envelope_created"

    confidence = result["confidence"][0]
    explanation = result["explainability"][0]
    certification = result["certification_state"][0]

    assert confidence["low_confidence_state"] == "not_assessable"
    assert confidence["phrase_level_confidence"] is None
    assert confidence["phrase_confidence_established"] is False
    assert confidence["source_confidence_evidence"] is None

    assert explanation["source_status"] == "no_evidence"
    assert explanation["evidence_ids"] == []
    assert certification["status"] == "no_evidence"
    assert certification["candidate_certification"] == (
        "not_established"
    )


def test_3102_sparse_status_and_candidate_isolation():
    parts = sparse_fixture()
    before = deepcopy(parts)
    result = build(parts)

    assert result["status"] == "package_envelope_created"
    assert result["intelligence_status"][0][
        "sparse_intelligence_classification"
    ] == "INSUFFICIENT_INTELLIGENCE"

    assert result["intelligence_status"][0][
        "source_statuses"
    ]["sparse_intelligence"] == "INSUFFICIENT_INTELLIGENCE"

    assert result["phrase_identity"][1][
        "original_candidate"
    ] == parts[0][1]

    result["phrase_identity"][0][
        "original_candidate"
    ]["phrase"] = "changed"

    assert parts == before
    assert result["phrase_identity"][1][
        "original_candidate"
    ] == before[0][1]


def test_3102_sparse_does_not_certify_score_or_link():
    result = build(sparse_fixture())
    assert result["status"] == "package_envelope_created"

    assert result["intelligence_status"][0][
        "overall_intelligence_readiness"
    ] == "not_determined"
    assert result["evidence_certification_performed"] is False
    assert result["semantic_certification_performed"] is False
    assert result["scorer_contract_finalized"] is False
    assert result["scorer_invoked"] is False
    assert result["scorer_decision_performed"] is False
    assert result["automatic_linking_authorized"] is False

    for record in result["certification_state"]:
        assert record["certification_performed_by_package"] is False
        assert record["automatic_linking_authorized"] is False



def test_3103_missing_all_optional_sources():
    """No optional intelligence source may cause candidate deletion."""
    from backend.app.tests.test_semantic_intelligence_package_39 import (
        fixture,
    )

    parts = fixture()
    original = deepcopy(parts)
    result = build(parts)

    assert result["status"] == "package_envelope_created"
    assert result["candidate_count"] == len(parts[0]) == 2
    assert result["original_candidates_preserved"] is True
    assert parts == original

    assert all(
        row["status"] == "semantic_sections_not_provided"
        for row in result["semantic_intelligence"]
    )
    assert all(
        row["status"] == "reasoning_not_provided"
        for row in result["reasoning"]
    )
    assert all(
        row["status"] == "confidence_not_provided"
        for row in result["confidence"]
    )
    assert all(
        row["status"] == "explainability_not_provided"
        for row in result["explainability"]
    )
    assert all(
        row["status"] == "provenance_not_provided"
        for row in result["provenance"]
    )
    assert all(
        row["status"] == "certification_not_established"
        for row in result["certification_state"]
    )


def test_3103_unavailable_sources_remain_unavailable():
    """Source failure and absence are different conditions."""
    from backend.app.tests.test_semantic_intelligence_package_39 import (
        fixture,
    )

    parts = fixture()
    entry = parts[1][0]

    entry["semantic_memory"] = {
        "status": "unavailable",
        "reason": "source_not_connected",
    }
    entry["reasoning_intelligence"] = {
        "status": "error",
        "reason": "upstream_failure",
    }
    entry["intelligence_graph"] = {
        "status": "stale",
    }
    entry["explainability"] = {
        "status": "no_evidence",
        "evidence_association": {
            "evidence_ids": [],
            "evidence_count": 0,
        },
    }

    result = build(parts)
    assert result["status"] == "package_envelope_created", result["reason"]

    statuses = result["intelligence_status"][0]["source_statuses"]
    assert statuses["semantic_memory"] == "unavailable"
    assert statuses["reasoning_intelligence"] == "error"
    assert statuses["intelligence_graph"] == "stale"
    assert statuses["explainability"] == "no_evidence"

    assert result["reasoning"][0]["source_status"] == "error"
    assert result["certification_state"][0]["status"] == "no_evidence"
    assert result["automatic_linking_authorized"] is False


def test_3103_missing_evidence_record_rejected():
    """An explanation cannot cite a nonexistent evidence record."""
    parts = provenance_fixture()
    del parts[2]["ev_1"]

    result = build(parts)

    assert result["status"] == "invalid"
    assert result["reason"] == "unresolved_explainability_evidence"
    assert result["candidate_count"] == 0
    assert result["enriched_candidates"] == []
    assert result["explainability"] == []
    assert result["provenance"] == []
    assert result["automatic_linking_authorized"] is False


def test_3103_invalid_source_structure_rejected():
    """Malformed reasoning cannot masquerade as unavailable reasoning."""
    from backend.app.tests.test_semantic_intelligence_package_39 import (
        fixture,
    )

    parts = fixture()
    parts[1][0]["reasoning_intelligence"] = "unavailable"

    result = build(parts)

    assert result["status"] == "invalid"
    assert result["reason"] == "invalid_reasoning_section"
    assert result["reasoning"] == []
    assert result["intelligence_status"] == []
    assert result["scorer_invoked"] is False


def test_3103_source_failure_is_candidate_isolated():
    """One candidate's unavailable source does not alter another."""
    from backend.app.tests.test_semantic_intelligence_package_39 import (
        fixture,
    )

    parts = fixture()
    parts[1][0]["semantic_memory"] = {
        "status": "unavailable",
    }
    parts[1][1]["semantic_memory"] = {
        "status": "observed",
        "observations": ["independent_candidate"],
    }

    before = deepcopy(parts)
    result = build(parts)

    assert result["status"] == "package_envelope_created"
    assert result["candidate_count"] == 2
    assert result["intelligence_status"][0][
        "source_statuses"
    ]["semantic_memory"] == "unavailable"
    assert result["intelligence_status"][1][
        "source_statuses"
    ]["semantic_memory"] == "observed"

    result["semantic_intelligence"][0][
        "sections"
    ]["semantic_memory"]["status"] = "modified"

    assert parts == before
    assert result["semantic_intelligence"][1][
        "sections"
    ]["semantic_memory"]["observations"] == [
        "independent_candidate"
    ]
    assert result["automatic_linking_authorized"] is False



def assert_certification_failure(result):
    assert result["status"] == "invalid"
    assert result["candidate_count"] == 0
    assert result["enriched_candidates"] == []
    assert result["certification_state"] == []
    assert result["intelligence_status"] == []
    assert result["evidence_certification_performed"] is False
    assert result["semantic_certification_performed"] is False
    assert result["scorer_invoked"] is False
    assert result["scorer_decision_performed"] is False
    assert result["automatic_linking_authorized"] is False


def test_3104_registry_certification_failure():
    parts = provenance_fixture()
    parts[2]["ev_1"]["certified"] = True

    result = build(parts)

    assert_certification_failure(result)
    assert result["reason"] == "unsupported_evidence_certification"


def test_3104_explanation_certification_failure():
    parts = provenance_fixture()
    parts[1][0]["explainability"]["evidence_association"][
        "semantic_proof_certified"
    ] = True

    result = build(parts)

    assert_certification_failure(result)
    assert result["reason"] == "unsupported_certification_authority"


def test_3104_provenance_verification_failure():
    parts = provenance_fixture()
    parts[1][0]["explainability"]["provenance"][
        "independent_provenance_verified"
    ] = True

    result = build(parts)

    assert_certification_failure(result)
    assert result["reason"] == "unsupported_provenance_authority"


def test_3104_sparse_certification_failure():
    parts = sparse_fixture()
    parts[1][0]["sparse_intelligence"][
        "semantic_proof_certified"
    ] = True

    result = build(parts)

    assert_certification_failure(result)
    assert result["reason"] == "unsupported_certification_authority"


def test_3104_failed_certification_does_not_mutate_inputs():
    parts = provenance_fixture()
    parts[2]["ev_1"]["certified"] = True
    before = deepcopy(parts)

    result = build(parts)

    assert_certification_failure(result)
    assert parts == before
    assert result["phrase_identity"] == []
    assert result["phrase_context"] == []
    assert result["semantic_intelligence"] == []
    assert result["reasoning"] == []
    assert result["confidence"] == []
    assert result["explainability"] == []
    assert result["provenance"] == []



def batch_fixture(count):
    """Build a valid multi-candidate package input without source inference."""
    from backend.app.tests.test_semantic_intelligence_package_39 import (
        fixture,
    )

    parts = list(fixture())

    selected = [
        {
            "phrase": f"clinical phrase {index % 7}",
            "id": f"occurrence_{index}",
            "position": index * 20,
        }
        for index in range(count)
    ]

    parts[0] = selected
    parts[1] = [
        {
            "candidate_index": index,
            "original_candidate": deepcopy(candidate),
        }
        for index, candidate in enumerate(selected)
    ]

    parts[2] = {}
    parts[3] = {
        "status": "all_candidates_retained",
        "selected_count": count,
        "retained_count": count,
        "retained_candidates": deepcopy(selected),
    }

    parts[4] = {
        "status": "advisory_handoff_prepared",
        "candidate_count": count,
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

    return parts


def test_3105_batch_of_thirty_retains_every_candidate():
    parts = batch_fixture(30)
    original = deepcopy(parts)
    result = build(parts)

    assert result["status"] == "package_envelope_created", result["reason"]
    assert result["candidate_count"] == 30
    assert parts == original

    for key in (
        "phrase_identity",
        "phrase_context",
        "semantic_intelligence",
        "reasoning",
        "confidence",
        "explainability",
        "provenance",
        "certification_state",
        "intelligence_status",
    ):
        assert len(result[key]) == 30
        assert [row["candidate_index"] for row in result[key]] == (
            list(range(30))
        )

    assert [
        row["original_candidate"]
        for row in result["enriched_candidates"]
    ] == parts[0]


def test_3105_batch_of_one_hundred():
    parts = batch_fixture(100)
    result = build(parts)

    assert result["status"] == "package_envelope_created", result["reason"]
    assert result["candidate_count"] == 100
    assert len(result["phrase_identity"]) == 100
    assert len(result["intelligence_status"]) == 100
    assert result["sparse_scorer_advisory_handoff"][
        "candidate_count"
    ] == 100
    assert result["automatic_linking_authorized"] is False


def test_3105_repeated_phrase_occurrences_remain_distinct():
    parts = batch_fixture(30)
    result = build(parts)

    assert result["status"] == "package_envelope_created"
    first = result["phrase_identity"][0]["original_candidate"]
    eighth = result["phrase_identity"][7]["original_candidate"]

    assert first["phrase"] == eighth["phrase"]
    assert first["id"] != eighth["id"]
    assert first["position"] != eighth["position"]
    assert result["phrase_identity"][0]["candidate_index"] == 0
    assert result["phrase_identity"][7]["candidate_index"] == 7


def test_3105_mixed_evidence_and_sparse_batch():
    parts = batch_fixture(30)

    # One evidence-rich candidate; other candidates remain sparse.
    parts[2]["batch_ev_5"] = {
        "candidate_index": 5,
        "certified": False,
    }
    parts[1][5]["reasoning_intelligence"] = {
        "status": "observed",
        "evidence_ids": ["batch_ev_5"],
    }
    parts[1][5]["explainability"] = {
        "status": "evidence_explained",
        "evidence_association": {
            "evidence_ids": ["batch_ev_5"],
            "evidence_count": 1,
        },
    }
    parts[1][6]["explainability"] = {
        "status": "no_evidence",
        "evidence_association": {
            "evidence_ids": [],
            "evidence_count": 0,
        },
    }

    result = build(parts)

    assert result["status"] == "package_envelope_created", result["reason"]
    assert result["certification_state"][5]["status"] == (
        "evidence_present_uncertified"
    )
    assert result["explainability"][5]["evidence_ids"] == [
        "batch_ev_5"
    ]
    assert result["certification_state"][6]["status"] == "no_evidence"
    assert result["explainability"][4]["evidence_ids"] == []
    assert result["explainability"][7]["evidence_ids"] == []
    assert result["candidate_count"] == 30


def test_3105_batch_reordering_rejected_without_partial_output():
    parts = batch_fixture(30)
    parts[1][12], parts[1][13] = parts[1][13], parts[1][12]

    result = build(parts)

    assert result["status"] == "invalid"
    assert result["reason"] == "candidate_identity_or_order_mismatch"
    assert result["candidate_count"] == 0
    assert result["enriched_candidates"] == []
    assert result["phrase_identity"] == []
    assert result["intelligence_status"] == []
    assert result["automatic_linking_authorized"] is False



def test_3106_cross_candidate_evidence_rejected():
    parts = batch_fixture(30)
    parts[2]["isolated_evidence"] = {
        "candidate_index": 11,
        "certified": False,
    }
    parts[1][12]["explainability"] = {
        "status": "evidence_explained",
        "evidence_association": {
            "evidence_ids": ["isolated_evidence"],
            "evidence_count": 1,
        },
    }

    result = build(parts)
    assert result["status"] == "invalid"
    assert result["reason"] == "cross_candidate_explainability_evidence"
    assert result["candidate_count"] == 0
    assert result["enriched_candidates"] == []
    assert result["explainability"] == []
    assert result["automatic_linking_authorized"] is False


def test_3106_corrupted_advisory_candidate_identity_rejected():
    parts = batch_fixture(30)
    parts[4]["candidates"][17]["original_candidate"] = deepcopy(
        parts[0][18]
    )

    result = build(parts)
    assert result["status"] == "invalid"
    assert result["reason"] == "sparse_advisory_candidate_mismatch"
    assert result["candidate_count"] == 0
    assert result["phrase_identity"] == []
    assert result["intelligence_status"] == []
    assert result["scorer_invoked"] is False


def test_3106_malformed_one_candidate_fails_closed():
    parts = batch_fixture(30)
    parts[1][21]["reasoning_intelligence"] = "malformed"
    original = deepcopy(parts)

    result = build(parts)
    assert result["status"] == "invalid"
    assert result["reason"] == "invalid_reasoning_section"
    assert result["candidate_count"] == 0

    for section in (
        "enriched_candidates",
        "phrase_identity",
        "phrase_context",
        "semantic_intelligence",
        "reasoning",
        "confidence",
        "explainability",
        "provenance",
        "certification_state",
        "intelligence_status",
    ):
        assert result[section] == []

    assert parts == original
    assert result["automatic_linking_authorized"] is False


def test_3106_nested_candidate_outputs_independently_isolated():
    parts = batch_fixture(30)
    for index in (4, 5, 6):
        parts[1][index]["semantic_memory"] = {
            "status": "observed",
            "nested": {"candidate_id": f"occurrence_{index}"},
        }

    original = deepcopy(parts)
    result = build(parts)

    assert result["status"] == "package_envelope_created"
    result["semantic_intelligence"][5]["sections"][
        "semantic_memory"
    ]["nested"]["candidate_id"] = "tampered"

    assert parts == original
    assert result["semantic_intelligence"][4]["sections"][
        "semantic_memory"
    ]["nested"]["candidate_id"] == "occurrence_4"
    assert result["semantic_intelligence"][6]["sections"][
        "semantic_memory"
    ]["nested"]["candidate_id"] == "occurrence_6"
    assert result["enriched_candidates"][5][
        "semantic_memory"
    ]["nested"]["candidate_id"] == "occurrence_5"


def test_3106_duplicate_phrase_text_never_merges_identities():
    parts = batch_fixture(30)
    parts[1][0]["reasoning_intelligence"] = {
        "status": "observed",
        "signals": [{"candidate": "occurrence_0"}],
    }
    parts[1][7]["reasoning_intelligence"] = {
        "status": "unavailable",
        "signals": [],
    }

    result = build(parts)
    assert result["status"] == "package_envelope_created"

    first = result["phrase_identity"][0]["original_candidate"]
    repeated = result["phrase_identity"][7]["original_candidate"]

    assert first["phrase"] == repeated["phrase"]
    assert first["id"] == "occurrence_0"
    assert repeated["id"] == "occurrence_7"

    assert result["reasoning"][0]["source_status"] == "observed"
    assert result["reasoning"][7]["source_status"] == "unavailable"
    assert result["reasoning"][0]["reasoning_output"]["signals"] == [
        {"candidate": "occurrence_0"}
    ]
    assert result["reasoning"][7]["reasoning_output"]["signals"] == []
    assert result["candidate_count"] == 30
    assert result["scorer_invoked"] is False
    assert result["automatic_linking_authorized"] is False



def test_3107_provenance_evidence_lineage_preserved():
    parts = provenance_fixture()
    original = deepcopy(parts)

    result = build(parts)

    assert result["status"] == "package_envelope_created", result["reason"]
    assert parts == original

    explanation = result["explainability"][0]
    provenance = result["provenance"][0]
    certification = result["certification_state"][0]

    assert explanation["evidence_ids"] == ["ev_1"]
    assert provenance["evidence_ids"] == ["ev_1"]
    assert certification["evidence_ids"] == ["ev_1"]
    assert provenance["provenance_output"]["candidate"][
        "evidence_ids"
    ] == ["ev_1"]
    assert provenance["provenance_output"]["consistency"][
        "checked_evidence_ids"
    ] == ["ev_1"]

    assert result["evidence_registry"]["ev_1"] == parts[2]["ev_1"]
    assert result["evidence_registry"]["ev_1"]["candidate_index"] == 0
    assert result["automatic_linking_authorized"] is False


def test_3107_corrupted_candidate_provenance_rejected():
    parts = provenance_fixture()

    parts[1][0]["explainability"]["provenance"][
        "candidate"
    ]["evidence_ids"] = ["unknown_evidence"]

    result = build(parts)

    assert result["status"] == "invalid"
    assert result["reason"] == "provenance_evidence_mismatch"
    assert result["candidate_count"] == 0
    assert result["provenance"] == []
    assert result["certification_state"] == []
    assert result["automatic_linking_authorized"] is False


def test_3107_provenance_does_not_cross_candidate_boundary():
    parts = provenance_fixture()

    # The registry record belongs to candidate 1, while the
    # explanation and provenance belong to candidate 0.
    parts[2]["ev_1"]["candidate_index"] = 1

    result = build(parts)

    assert result["status"] == "invalid"
    assert result["reason"] == (
        "cross_candidate_explainability_evidence"
    )
    assert result["enriched_candidates"] == []
    assert result["provenance"] == []
    assert result["scorer_invoked"] is False


def test_3107_provenance_must_not_claim_verification():
    parts = provenance_fixture()
    parts[1][0]["explainability"]["provenance"][
        "independent_provenance_verified"
    ] = True

    result = build(parts)

    assert result["status"] == "invalid"
    assert result["reason"] == "unsupported_provenance_authority"
    assert result["provenance"] == []
    assert result["semantic_certification_performed"] is False
    assert result["automatic_linking_authorized"] is False


def test_3107_provenance_integrity_and_output_isolation():
    parts = provenance_fixture()
    before = deepcopy(parts)

    result = build(parts)
    assert result["status"] == "package_envelope_created"

    result["provenance"][0]["provenance_output"][
        "cross_intelligence"
    ]["explainability"]["evidence_ids"][0] = "tampered"

    assert parts == before
    assert result["enriched_candidates"][0][
        "explainability"
    ]["provenance"]["cross_intelligence"][
        "explainability"
    ]["evidence_ids"] == ["ev_1"]

    assert result["evidence_registry"]["ev_1"] == before[2]["ev_1"]
    assert result["explainability"][0]["evidence_ids"] == ["ev_1"]
    assert result["provenance"][1]["status"] == (
        "provenance_not_provided"
    )
    assert result["original_candidates_preserved"] is True
