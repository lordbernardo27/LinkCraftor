"""3.7.4 real provisional interpretation tests."""

from backend.server.engine.semantic_phrase_topic_intent_producer import (
    produce_phrase_topic_intent_context,
    accept_phrase_topic_intent_interpretation,
)
from backend.server.engine.semantic_phrase_topic_intent_interpreter import (
    interpret_phrase_topic_intent,
)


def evaluate(sentence, phrase="diabetes treatment"):
    observation = produce_phrase_topic_intent_context(
        phrase=phrase,
        sentence=sentence,
        source_sentence_id="sentence_001",
    )
    proposal = interpret_phrase_topic_intent(observation)
    accepted = accept_phrase_topic_intent_interpretation(
        source_observation=observation,
        provider_interpretation=proposal,
    )
    return observation, proposal, accepted


def test_comparison_intent_generated_by_real_provider():
    _, proposal, accepted = evaluate(
        "Patients compare diabetes treatment options."
    )
    assert proposal["detected_intent"] == "comparison"
    assert proposal["detected_topic"] == "diabetes treatment"
    assert accepted["interpretation_status"] == "supported_unverified"
    assert accepted["detected_intent"] == "comparison"
    assert accepted["certified"] is False


def test_prevention_intent():
    _, proposal, accepted = evaluate(
        "Ways to prevent diabetes treatment risks involve careful review."
    )
    assert proposal["detected_intent"] == "prevention"
    assert accepted["certified"] is False


def test_unclear_sentence_abstains():
    _, proposal, accepted = evaluate(
        "Diabetes treatment is discussed in the article."
    )
    assert proposal["status"] == "insufficient_evidence"
    assert accepted["detected_intent"] is None


def test_competing_intents_remain_ambiguous():
    _, proposal, accepted = evaluate(
        "Compare diabetes treatment options and prevent risk "
        "using practical steps."
    )
    assert proposal["status"] == "ambiguous"
    assert accepted["interpretation_status"] == "ambiguous"
    assert accepted["detected_intent"] is None


def test_phrase_absent_cannot_produce_intent():
    _, proposal, accepted = evaluate(
        "Patients compare available medication options."
    )
    assert proposal["status"] == "insufficient_evidence"
    assert accepted["detected_topic"] is None


def test_provider_never_certifies_or_links():
    _, proposal, accepted = evaluate(
        "Patients compare diabetes treatment options."
    )
    assert proposal["certified"] is False
    assert proposal["linking_decision_performed"] is False
    assert accepted["linking_decision_performed"] is False


def test_fingerprint_and_sentence_evidence_retained():
    observation, proposal, accepted = evaluate(
        "Patients compare diabetes treatment options."
    )
    assert (
        proposal["source_fingerprint"]
        == observation["source_fingerprint"]
    )
    assert (
        accepted["interpretation_provenance"]["evidence_quote"]
        == observation["source_context"]["sentence"]
    )


def test_generic_compare_word_not_enough():
    _, proposal, _ = evaluate(
        "We compare diabetes treatment."
    )
    assert proposal["status"] == "insufficient_evidence"



def test_selector_verified_occurrence_integration():
    from copy import deepcopy
    from backend.server.engine.semantic_phrase_topic_intent_interpreter import (
        attach_selector_topic_intent_advisory,
    )

    sentence = "Patients compare diabetes treatment options."
    phrase = "diabetes treatment"
    start = sentence.index(phrase)
    end = start + len(phrase)

    original = {
        "phrase": phrase,
        "selection_occurrence_id": "occ_001",
        "selection_source_span_status": "verified",
        "selection_sentence_context_status": "derived_from_verified_span",
        "selection_source_span": {
            "start": start, "end": end,
            "coordinate_space": "original_article",
            "text": phrase,
        },
        "selection_sentence_context": {
            "start": 0, "end": len(sentence),
            "coordinate_space": "original_article",
            "text": sentence,
        },
    }
    row = {
        "original_candidate": deepcopy(original),
        "semantic_context": {"status": "not_executed"},
    }

    output = attach_selector_topic_intent_advisory([row])
    advisory = output[0]["semantic_context"]["provisional_topic_intent"]

    assert advisory["interpretation_status"] == "supported_unverified"
    assert advisory["detected_intent"] == "comparison"
    assert advisory["certified"] is False
    assert advisory["automatic_linking_authorized"] is False
    assert output[0]["original_candidate"] == original
    assert output[0]["semantic_context"]["status"] == "not_executed"


def test_selector_missing_verification_abstains():
    from backend.server.engine.semantic_phrase_topic_intent_interpreter import (
        attach_selector_topic_intent_advisory,
    )

    row = {
        "original_candidate": {"phrase": "diabetes treatment"},
        "semantic_context": {"detected_topic": "existing"},
    }

    result = attach_selector_topic_intent_advisory([row])
    advisory = result[0]["semantic_context"]["provisional_topic_intent"]

    assert advisory["status"] == "unavailable"
    assert result[0]["semantic_context"]["detected_topic"] == "existing"


def test_selector_wrong_occurrence_abstains():
    from backend.server.engine.semantic_phrase_topic_intent_interpreter import (
        attach_selector_topic_intent_advisory,
    )

    sentence = "Patients compare diabetes treatment options."
    row = {
        "original_candidate": {
            "phrase": "diabetes treatment",
            "selection_source_span_status": "verified",
            "selection_sentence_context_status": "derived_from_verified_span",
            "selection_source_span": {
                "start": 0, "end": 18,
                "coordinate_space": "original_article",
                "text": sentence[:18],
            },
            "selection_sentence_context": {
                "start": 0, "end": len(sentence),
                "coordinate_space": "original_article",
                "text": sentence,
            },
        },
        "semantic_context": {},
    }

    result = attach_selector_topic_intent_advisory([row])
    advisory = result[0]["semantic_context"]["provisional_topic_intent"]

    assert advisory["status"] == "unavailable"


def test_selector_candidate_order_preserved():
    from copy import deepcopy
    from backend.server.engine.semantic_phrase_topic_intent_interpreter import (
        attach_selector_topic_intent_advisory,
    )

    originals = [
        {"phrase": "first"},
        {"phrase": "second"},
    ]
    rows = [
        {
            "original_candidate": deepcopy(item),
            "semantic_context": {},
        }
        for item in originals
    ]

    output = attach_selector_topic_intent_advisory(rows)

    assert len(output) == 2
    assert [r["original_candidate"] for r in output] == originals
    assert all(
        r["semantic_context"]["provisional_topic_intent"]["certified"] is False
        for r in output
    )
