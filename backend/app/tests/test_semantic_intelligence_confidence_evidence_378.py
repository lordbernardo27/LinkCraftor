from copy import deepcopy

from backend.server.engine.semantic_intelligence_confidence_evidence_378 import (
    preserve_confidence_evidence,
)


def sample():
    return [{
        "signal_type": "recorded_synonym_observation",
        "recorded_relation_type": "related_to",
        "canonical_phrase": "diabetes treatment",
        "related_phrase": "insulin therapy",
        "source": "semantic_concept_evidence",
        "source_role": "supporting_context",
        "concept_confidence": 0.85,
        "evidence_confidence": 0.70,
        "evidence_id": "semantic_concept_relation_0_0",
        "semantic_equivalence_asserted": False,
        "approved_link_target": False,
        "certified": False,
    }]


def test_source_scores_preserved_separately():
    result = preserve_confidence_evidence(sample())
    assert result["status"] == "source_confidence_preserved"
    assert result["source_count"] == 1
    record = result["confidence_records"][0]
    assert record["concept_confidence"] == 0.85
    assert record["evidence_confidence"] == 0.70
    assert record["phrase_level_semantic_confidence"] is None
    assert result["overall_confidence"] is None


def test_original_signals_unchanged():
    signals = sample()
    before = deepcopy(signals)
    preserve_confidence_evidence(signals)
    assert signals == before


def test_empty_evidence_abstains():
    result = preserve_confidence_evidence([])
    assert result["status"] == "no_evidence"
    assert result["overall_confidence"] is None


def test_invalid_scores_rejected():
    for bad in (-0.1, 1.1, True, "0.7", None,
                float("nan"), float("inf")):
        signals = sample()
        signals[0]["concept_confidence"] = bad
        assert preserve_confidence_evidence(signals)["status"] == "invalid"


def test_duplicate_evidence_ids_rejected():
    signals = sample() * 2
    assert preserve_confidence_evidence(signals)["status"] == "invalid"


def test_uncertified_evidence_required():
    signals = sample()
    signals[0]["certified"] = True
    assert preserve_confidence_evidence(signals)["status"] == "invalid"


def test_no_link_authority():
    result = preserve_confidence_evidence(sample())
    assert result["automatic_linking_authorized"] is False
    assert result["linking_decision_performed"] is False
    assert result["semantic_proof_certified"] is False


def test_zero_and_one_preserved():
    signals = sample()
    signals[0]["concept_confidence"] = 0
    signals[0]["evidence_confidence"] = 1
    result = preserve_confidence_evidence(signals)
    assert result["confidence_records"][0]["concept_confidence"] == 0
    assert result["confidence_records"][0]["evidence_confidence"] == 1



def test_378_valid_source_scope_preserved():
    result = preserve_confidence_evidence(sample())
    assert result["status"] == "source_confidence_preserved"
    record = result["confidence_records"][0]
    assert record["evidence_validity"] == (
        "structurally_valid_unverified"
    )
    assert record["confidence_applicability"] == (
        "source_relationship_only"
    )
    assert record["selected_phrase_confidence_authorized"] is False


def test_378_missing_source_identity_rejected():
    for field in ("source", "source_role"):
        signals = sample()
        signals[0].pop(field)
        result = preserve_confidence_evidence(signals)
        assert result["status"] == "invalid"
        assert result["reason"].startswith(
            "missing_or_invalid_confidence_context:"
        )


def test_378_missing_relationship_identity_rejected():
    for field in (
        "recorded_relation_type",
        "canonical_phrase",
        "related_phrase",
    ):
        signals = sample()
        signals[0][field] = " "
        assert preserve_confidence_evidence(signals)[
            "status"
        ] == "invalid"


def test_378_unsupported_signal_type_rejected():
    signals = sample()
    signals[0]["signal_type"] = "document_relationship"
    result = preserve_confidence_evidence(signals)
    assert result["status"] == "invalid"
    assert result["reason"] == "unsupported_confidence_signal_type"


def test_378_invalid_context_types_rejected():
    for bad in (None, 42, True, [], {}):
        signals = sample()
        signals[0]["canonical_phrase"] = bad
        assert preserve_confidence_evidence(signals)[
            "status"
        ] == "invalid"


def test_378_invalid_later_record_no_partial_acceptance():
    signals = sample()
    second = deepcopy(signals[0])
    second["evidence_id"] = "semantic_concept_relation_0_1"
    second["source_role"] = ""
    signals.append(second)

    result = preserve_confidence_evidence(signals)
    assert result["status"] == "invalid"
    assert result["confidence_records"] == []
    assert result["overall_confidence"] is None
    assert result["automatic_linking_authorized"] is False



def test_378_missing_evidence_distinct():
    result = preserve_confidence_evidence([])
    assert result["status"] == "no_evidence"
    assert result["confidence_records"] == []


def test_378_unknown_state_not_promoted_to_current():
    result = preserve_confidence_evidence(sample())
    assert result["status"] == "source_confidence_preserved"
    record = result["confidence_records"][0]
    assert record["source_declared_evidence_status"] == "unknown"
    assert record["freshness_status"] == (
        "not_independently_established"
    )
    assert record["independently_verified"] is False


def test_378_source_available_does_not_certify():
    signals = sample()
    signals[0]["evidence_status"] = "available"
    result = preserve_confidence_evidence(signals)
    assert result["status"] == "source_confidence_preserved"
    record = result["confidence_records"][0]
    assert record["source_availability_status"] == (
        "source_reported_available"
    )
    assert record["confidence_calibrated"] is False
    assert record["certified"] is False


def test_378_stale_source_abstains():
    signals = sample()
    signals[0]["evidence_status"] = "stale"
    result = preserve_confidence_evidence(signals)
    assert result["status"] == "stale_evidence"
    assert result["confidence_records"] == []
    assert result["overall_confidence"] is None


def test_378_invalid_source_abstains():
    signals = sample()
    signals[0]["evidence_status"] = "invalid"
    result = preserve_confidence_evidence(signals)
    assert result["status"] == "invalid"
    assert result["confidence_records"] == []


def test_378_malformed_source_state_rejected():
    for state in ("fresh", "expired", "", None, True, 1):
        signals = sample()
        signals[0]["evidence_status"] = state
        result = preserve_confidence_evidence(signals)
        assert result["status"] == "invalid"
        assert result["reason"] == "invalid_evidence_status"


def test_378_mixed_stale_source_no_partial_acceptance():
    signals = sample()
    second = deepcopy(signals[0])
    second["evidence_id"] = "semantic_concept_relation_0_1"
    second["evidence_status"] = "stale"
    signals.append(second)

    result = preserve_confidence_evidence(signals)
    assert result["status"] == "stale_evidence"
    assert result["confidence_records"] == []
    assert result["source_count"] == 0
    assert result["automatic_linking_authorized"] is False



def test_378_aggregation_explicitly_prohibited():
    result = preserve_confidence_evidence(sample())
    assert result["aggregation_authorized"] is False
    assert result["aggregation_performed"] is False
    assert result["aggregation_method"] is None
    assert result["aggregate_confidence_calibrated"] is False
    assert result["overall_confidence"] is None


def test_378_confidence_inventory_preserves_metric_types():
    result = preserve_confidence_evidence(sample())
    inventory = result["confidence_inventory"]

    assert inventory["scope"] == "source_concept_relationship"
    assert inventory["concept_confidence_count"] == 1
    assert inventory["evidence_confidence_count"] == 1
    assert inventory["distinct_evidence_count"] == 1
    assert inventory["metric_types"] == [
        "concept_confidence", "evidence_confidence"
    ]
    assert inventory["cross_source_comparability"] == "not_established"


def test_378_multiple_sources_do_not_create_average():
    signals = sample()
    second = deepcopy(signals[0])
    second["evidence_id"] = "semantic_concept_relation_0_1"
    second["concept_confidence"] = 0.20
    second["evidence_confidence"] = 0.95
    signals.append(second)

    result = preserve_confidence_evidence(signals)

    assert result["status"] == "source_confidence_preserved"
    assert result["source_count"] == 2
    assert result["confidence_inventory"]["distinct_evidence_count"] == 2
    assert result["confidence_records"][0]["concept_confidence"] == 0.85
    assert result["confidence_records"][1]["concept_confidence"] == 0.20
    assert result["overall_confidence"] is None
    assert result["aggregation_performed"] is False


def test_378_empty_inventory_has_no_confidence():
    result = preserve_confidence_evidence([])
    assert result["status"] == "no_evidence"
    assert result["confidence_inventory"]["distinct_evidence_count"] == 0
    assert result["confidence_inventory"]["phrase_level_confidence"] is None
    assert result["overall_confidence"] is None


def test_378_invalid_or_stale_evidence_cannot_aggregate():
    for state, expected in (
        ("invalid", "invalid"),
        ("stale", "stale_evidence"),
    ):
        signals = sample()
        signals[0]["evidence_status"] = state
        result = preserve_confidence_evidence(signals)

        assert result["status"] == expected
        assert result["confidence_records"] == []
        assert result["confidence_inventory"]["distinct_evidence_count"] == 0
        assert result["aggregation_performed"] is False
        assert result["overall_confidence"] is None


def test_378_source_records_remain_unchanged():
    signals = sample()
    original = deepcopy(signals)

    result = preserve_confidence_evidence(signals)

    assert signals == original
    assert result["confidence_records"][0]["evidence_id"] == (
        original[0]["evidence_id"]
    )
    assert result["confidence_records"][0]["evidence_confidence"] == (
        original[0]["evidence_confidence"]
    )



def test_378_production_signal_types_supported():
    for kind in (
        "recorded_synonym_observation",
        "recorded_topical_association",
    ):
        signals = sample()
        signals[0]["signal_type"] = kind
        result = preserve_confidence_evidence(signals)
        assert result["status"] == "source_confidence_preserved"
        assert result["confidence_records"][0]["signal_type"] == kind


def test_378_main_enricher_integration_present():
    import inspect
    from backend.server.engine import semantic_intelligence_enricher

    source = inspect.getsource(semantic_intelligence_enricher)
    assert "confidence_evidence_main_integration_378" in source
    assert "preserve_confidence_evidence(signals)" in source
    assert 'section["semantic_relationship_confidence_evidence"]' in source
