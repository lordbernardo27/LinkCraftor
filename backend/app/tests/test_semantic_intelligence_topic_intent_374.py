"""3.7.4 semantic context evidence-boundary regressions."""

from copy import deepcopy

import pytest

from backend.server.engine.semantic_intelligence_enricher import (
    enrich_selected_phrase_candidates,
)
from backend.server.engine.semantic_intelligence_topic_intent_validation import (
    validate_phrase_topic_intent,
)


def package(status="not_executed", topic=None, intent=None):
    return {
        "enriched_candidates": [{
            "candidate_index": 0,
            "original_candidate": {"phrase": "diabetes treatment"},
            "semantic_context": {
                "status": status,
                "detected_topic": topic,
                "detected_intent": intent,
                "meaning": None,
                "ambiguity_status": "not_evaluated",
                "related_concepts": [],
            },
        }],
        "evidence_registry": {},
    }


def attach(data, source="existing_phrase_intelligence"):
    data["enriched_candidates"][0]["semantic_context"][
        "evidence_ids"
    ] = ["semantic_0"]
    data["evidence_registry"]["semantic_0"] = {
        "candidate_index": 0,
        "source": source,
        "evidence_type": "phrase_semantic_context",
        "detected_topic": "diabetes treatment",
        "detected_intent": "treatment options",
        "certified": True,
        "validity_status": "valid",
        "stale": False,
    }


@pytest.mark.parametrize("workspace", [None, "ws_topic_intent_test"])
def test_existing_runtime_paths(workspace):
    candidate = {
        "phrase": "diabetes treatment",
        "upstream_candidate_id": "topic_intent_test_001",
    }
    original = deepcopy(candidate)

    result = enrich_selected_phrase_candidates(
        selected_candidates=[candidate],
        workspace_id=workspace,
    )
    entry = result["enriched_candidates"][0]
    context = entry["semantic_context"]

    assert candidate == original
    assert entry["original_candidate"] == original
    assert context["detected_topic"] is None
    assert context["detected_intent"] is None
    assert context["evidence_validation"]["status"] == "not_executed"
    assert context["evidence_validation"][
        "automatic_linking_authorized"
    ] is False


def test_valid_explicit_topic_and_intent():
    data = package(
        "evidence_found",
        "diabetes treatment",
        "treatment options",
    )
    attach(data)
    result = validate_phrase_topic_intent(data)
    evidence = result["enriched_candidates"][0][
        "semantic_context"
    ]["evidence_validation"]

    assert evidence["status"] == "evidence_validated"
    assert evidence["topic_verified"] is True
    assert evidence["intent_verified"] is True
    assert evidence["certified"] is False
    assert evidence["automatic_linking_authorized"] is False


def test_unreferenced_claim_cannot_be_verified():
    data = package("evidence_found", "diabetes treatment")
    result = validate_phrase_topic_intent(data)
    assert result["enriched_candidates"][0][
        "semantic_context"
    ]["evidence_validation"]["status"] == "no_evidence"


def test_mismatched_claim_is_invalid():
    data = package("evidence_found", "cardiology")
    attach(data)
    result = validate_phrase_topic_intent(data)
    assert result["enriched_candidates"][0][
        "semantic_context"
    ]["evidence_validation"]["status"] == "invalid"


def test_resolver_evidence_not_authoritative():
    data = package("evidence_found", "diabetes treatment")
    attach(data, source="workspace_topic_cluster_resolver")
    result = validate_phrase_topic_intent(data)
    assert result["enriched_candidates"][0][
        "semantic_context"
    ]["evidence_validation"]["status"] == "invalid"


def test_wrong_candidate_rejected():
    data = package("evidence_found", "diabetes treatment")
    attach(data)
    data["evidence_registry"]["semantic_0"]["candidate_index"] = 1
    result = validate_phrase_topic_intent(data)
    assert result["enriched_candidates"][0][
        "semantic_context"
    ]["evidence_validation"]["status"] == "invalid"


def test_ambiguous_context_stays_ambiguous():
    data = package("evidence_found", "Apple")
    data["enriched_candidates"][0]["semantic_context"][
        "ambiguity_status"
    ] = "ambiguous"
    result = validate_phrase_topic_intent(data)
    assert result["enriched_candidates"][0][
        "semantic_context"
    ]["evidence_validation"]["status"] == "ambiguous"


def test_existing_context_and_registry_preserved():
    data = package("evidence_found", "diabetes treatment")
    attach(data)
    original = deepcopy(data)
    validate_phrase_topic_intent(data)

    assert data["evidence_registry"] == original["evidence_registry"]
    context = data["enriched_candidates"][0]["semantic_context"]
    context.pop("evidence_validation")
    assert context == original["enriched_candidates"][0]["semantic_context"]


def test_empty_batch():
    result = validate_phrase_topic_intent({
        "enriched_candidates": [],
        "evidence_registry": {},
    })
    assert result["enriched_candidates"] == []


def test_invalid_candidate_sequence_rejected():
    data = package()
    data["enriched_candidates"][0]["candidate_index"] = 4
    with pytest.raises(ValueError):
        validate_phrase_topic_intent(data)
