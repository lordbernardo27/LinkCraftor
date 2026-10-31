"""Tests for 3.7.4 source-grounding producer contract."""

import pytest

from backend.server.engine.semantic_phrase_topic_intent_producer import (
    produce_phrase_topic_intent_context,
)


def make(**overrides):
    values = {
        "phrase": "type 2 diabetes",
        "sentence": (
            "Patients with type 2 diabetes should compare "
            "available treatment options."
        ),
        "heading": "Treatment options",
        "source_sentence_id": "s1",
    }
    values.update(overrides)
    return produce_phrase_topic_intent_context(**values)


def test_exact_phrase_occurrence():
    result = make()
    assert result["status"] == "source_context_found"
    assert result["source_phrase_occurrence_verified"] is True


def test_phrase_not_in_sentence():
    result = make(sentence="Patients should compare their options.")
    assert result["status"] == "no_source_occurrence"
    assert result["source_phrase_occurrence_verified"] is False


def test_no_generated_topic_or_intent():
    result = make()
    assert result["detected_topic"] is None
    assert result["detected_intent"] is None
    assert result["interpretation_status"] == "not_evaluated"
    assert result["certified"] is False


def test_source_context_preserved():
    result = make(previous_sentence="The diagnosis was confirmed.")
    assert result["source_context"]["previous_sentence"] == (
        "The diagnosis was confirmed."
    )
    assert result["source_sentence_id"] == "s1"


def test_fingerprint_is_deterministic_and_context_sensitive():
    first = make()["source_fingerprint"]
    assert first == make()["source_fingerprint"]
    assert first != make(heading="Prevention")["source_fingerprint"]


def test_no_linking_authorization():
    assert make()["linking_decision_performed"] is False


def test_missing_source_is_not_evidence():
    result = make(sentence="")
    assert result["status"] == "no_source_occurrence"


def test_invalid_phrase_rejected():
    with pytest.raises(ValueError):
        make(phrase="   ")


def test_substring_not_accepted_as_phrase():
    result = make(
        phrase="diabetes",
        sentence="The term prediabetes appears here."
    )
    assert result["source_phrase_occurrence_verified"] is False


from backend.server.engine.semantic_phrase_topic_intent_producer import (
    accept_phrase_topic_intent_interpretation,
)


def interpretation(source, **overrides):
    values = {
        "status": "supported",
        "source_sentence_id": source["source_sentence_id"],
        "source_fingerprint": source["source_fingerprint"],
        "provider_id": "test_interpretation_provider",
        "evidence_id": "evidence_001",
        "evidence_quote": "compare available treatment options",
        "detected_topic": "type 2 diabetes treatment",
        "detected_intent": "comparison of treatment options",
        "meaning": None,
    }
    values.update(overrides)
    return values


def test_supported_provider_handoff_remains_uncertified():
    source = make()
    result = accept_phrase_topic_intent_interpretation(
        source_observation=source,
        provider_interpretation=interpretation(source),
    )
    assert result["interpretation_status"] == "supported_unverified"
    assert result["detected_topic"] == "type 2 diabetes treatment"
    assert result["certified"] is False
    assert result["linking_decision_performed"] is False


def test_wrong_fingerprint_rejected():
    source = make()
    result = accept_phrase_topic_intent_interpretation(
        source_observation=source,
        provider_interpretation=interpretation(
            source, source_fingerprint="incorrect"
        ),
    )
    assert result["interpretation_status"] == "invalid"


def test_ambiguous_provider_result_preserved():
    source = make()
    result = accept_phrase_topic_intent_interpretation(
        source_observation=source,
        provider_interpretation=interpretation(source, status="ambiguous"),
    )
    assert result["interpretation_status"] == "ambiguous"
    assert result["detected_topic"] is None


def test_unrelated_quote_rejected():
    source = make()
    result = accept_phrase_topic_intent_interpretation(
        source_observation=source,
        provider_interpretation=interpretation(
            source, evidence_quote="completely unrelated wording"
        ),
    )
    assert result["interpretation_status"] == "invalid"


def test_no_occurrence_rejects_provider():
    source = make(sentence="Another medical sentence.")
    result = accept_phrase_topic_intent_interpretation(
        source_observation=source,
        provider_interpretation=interpretation(source),
    )
    assert result["interpretation_status"] == "insufficient_evidence"


def test_missing_claims_do_not_establish_interpretation():
    source = make()
    result = accept_phrase_topic_intent_interpretation(
        source_observation=source,
        provider_interpretation=interpretation(
            source, detected_topic=None, detected_intent=None
        ),
    )
    assert result["interpretation_status"] == "insufficient_evidence"
