"""Phase 3.7.4 ? Source-grounded phrase interpretation contract.

This first stage establishes source occurrence and contextual provenance.
It does not infer or certify topic, intent, or link eligibility.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping


def _normalize(value):
    return " ".join(value.casefold().split())


def _occurs(phrase, sentence):
    pattern = (
        r"(?<!\w)"
        + r"\s+".join(re.escape(term) for term in phrase.split())
        + r"(?!\w)"
    )
    return re.search(pattern, sentence, flags=re.IGNORECASE) is not None


def produce_phrase_topic_intent_context(
    *,
    phrase,
    sentence,
    previous_sentence="",
    next_sentence="",
    heading="",
    document_title="",
    source_sentence_id=None,
):
    """Return a source-grounded observation, never an invented conclusion."""

    fields = (
        phrase, sentence, previous_sentence, next_sentence,
        heading, document_title,
    )

    if not all(isinstance(value, str) for value in fields):
        raise TypeError("Phrase and context fields must be strings")

    if not phrase.strip():
        raise ValueError("Selected phrase must not be empty")

    if source_sentence_id is not None and (
        not isinstance(source_sentence_id, str)
        or not source_sentence_id.strip()
    ):
        raise ValueError("Invalid source sentence ID")

    found = bool(sentence.strip()) and _occurs(
        phrase.strip(), sentence
    )

    fingerprint = hashlib.sha256(
        (
            "\\x1f".join(fields)
            + "\\x1f" + str(source_sentence_id or "")
        ).encode("utf-8")
    ).hexdigest()

    return {
        "schema_version": "phrase_topic_intent_source_v1",
        "status": (
            "source_context_found"
            if found
            else "no_source_occurrence"
        ),
        "phrase": phrase,
        "source_sentence_id": source_sentence_id,
        "source_fingerprint": fingerprint,
        "source_context": {
            "sentence": sentence,
            "previous_sentence": previous_sentence,
            "next_sentence": next_sentence,
            "heading": heading,
            "document_title": document_title,
        },
        "source_phrase_occurrence_verified": found,
        "detected_topic": None,
        "detected_intent": None,
        "meaning": None,
        "interpretation_status": "not_evaluated",
        "interpretation_evidence_ids": [],
        "certified": False,
        "linking_decision_performed": False,
    }


def accept_phrase_topic_intent_interpretation(
    *,
    source_observation,
    provider_interpretation,
):
    """Validate an explicitly supplied interpretation against its source.

    This function does not generate or certify an interpretation.
    """
    from copy import deepcopy

    if not isinstance(source_observation, Mapping):
        raise TypeError("Invalid source observation")
    if not isinstance(provider_interpretation, Mapping):
        raise TypeError("Invalid provider interpretation")

    result = deepcopy(source_observation)
    result["detected_topic"] = None
    result["detected_intent"] = None
    result["meaning"] = None
    result["interpretation_status"] = "insufficient_evidence"
    result["interpretation_evidence_ids"] = []
    result["certified"] = False
    result["linking_decision_performed"] = False

    if (
        result.get("source_phrase_occurrence_verified") is not True
        or result.get("status") != "source_context_found"
    ):
        return result

    if (
        provider_interpretation.get("source_fingerprint")
        != result.get("source_fingerprint")
        or provider_interpretation.get("source_sentence_id")
        != result.get("source_sentence_id")
    ):
        result["interpretation_status"] = "invalid"
        return result

    if provider_interpretation.get("status") == "ambiguous":
        result["interpretation_status"] = "ambiguous"
        return result

    if provider_interpretation.get("status") != "supported":
        return result

    provider_id = provider_interpretation.get("provider_id")
    evidence_id = provider_interpretation.get("evidence_id")
    quotation = provider_interpretation.get("evidence_quote")

    if not all(
        isinstance(value, str) and value.strip()
        for value in (provider_id, evidence_id, quotation)
    ):
        result["interpretation_status"] = "invalid"
        return result

    sentence = result.get("source_context", {}).get("sentence", "")
    if quotation.casefold() not in sentence.casefold():
        result["interpretation_status"] = "invalid"
        return result

    topic = provider_interpretation.get("detected_topic")
    intent = provider_interpretation.get("detected_intent")
    meaning = provider_interpretation.get("meaning")

    claims = (topic, intent, meaning)
    if any(
        value is not None
        and (not isinstance(value, str) or not value.strip())
        for value in claims
    ):
        result["interpretation_status"] = "invalid"
        return result

    if topic is None and intent is None and meaning is None:
        return result

    result["detected_topic"] = topic
    result["detected_intent"] = intent
    result["meaning"] = meaning
    result["interpretation_status"] = "supported_unverified"
    result["interpretation_evidence_ids"] = [evidence_id]
    result["interpretation_provenance"] = {
        "provider_id": provider_id,
        "evidence_id": evidence_id,
        "evidence_quote": quotation,
        "source_fingerprint": result["source_fingerprint"],
    }

    return result
