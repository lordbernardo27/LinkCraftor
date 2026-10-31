"""3.7.4 ? Conservative, provisional sentence interpretation.

Only narrow patterns are recognized. No semantic certification, no
canonical concept resolution, no URL selection or linking decisions.
"""

from __future__ import annotations

import re
from collections.abc import Mapping


# Every intent requires two independent cues in the same sentence.
# These are narrow linguistic heuristics, not universal meaning rules.
PATTERNS = {
    "comparison": (
        r"\b(?:compare|comparing|comparison|differences between)\b",
        r"\b(?:options|alternatives|approaches|methods|treatments)\b",
    ),
    "prevention": (
        r"\b(?:prevent|preventing|prevention|reduce the risk)\b",
        r"\b(?:risk|steps|measures|strategies|ways)\b",
    ),
    "cause_explanation": (
        r"\b(?:causes?|caused by|because of|results from)\b",
        r"\b(?:factors|reasons|mechanisms|conditions)\b",
    ),
}


def interpret_phrase_topic_intent(source_observation):
    """Generate provisional source-grounded findings or abstain."""

    if not isinstance(source_observation, Mapping):
        raise TypeError("Expected source observation mapping")

    base = {
        "status": "insufficient_evidence",
        "source_sentence_id": source_observation.get(
            "source_sentence_id"
        ),
        "source_fingerprint": source_observation.get(
            "source_fingerprint"
        ),
        "provider_id": "conservative_sentence_interpreter_v1",
        "evidence_id": None,
        "evidence_quote": None,
        "detected_topic": None,
        "detected_intent": None,
        "meaning": None,
        "certified": False,
        "method": "two_cue_sentence_heuristics",
        "linking_decision_performed": False,
    }

    if (
        source_observation.get("status") != "source_context_found"
        or source_observation.get(
            "source_phrase_occurrence_verified"
        ) is not True
    ):
        return base

    phrase = source_observation.get("phrase")
    context = source_observation.get("source_context")
    fingerprint = source_observation.get("source_fingerprint")

    if (
        not isinstance(phrase, str)
        or not phrase.strip()
        or not isinstance(context, Mapping)
        or not isinstance(fingerprint, str)
        or not fingerprint
    ):
        return base

    sentence = context.get("sentence")
    if not isinstance(sentence, str) or not sentence.strip():
        return base

    matched = []
    for intent, (cue_a, cue_b) in PATTERNS.items():
        if (
            re.search(cue_a, sentence, re.IGNORECASE)
            and re.search(cue_b, sentence, re.IGNORECASE)
        ):
            matched.append(intent)

    if len(matched) > 1:
        base["status"] = "ambiguous"
        base["competing_intents"] = matched
        return base

    if len(matched) != 1:
        return base

    # Topic is the observed phrase surface, not a resolved concept.
    # Intent is provisional, inferred from limited sentence patterns.
    base.update({
        "status": "supported",
        "detected_topic": phrase.strip(),
        "detected_intent": matched[0],
        "evidence_id": "sentence_context:" + fingerprint,
        "evidence_quote": sentence.strip(),
        "interpretation_scope": "provisional_sentence_only",
    })

    return base


def attach_selector_topic_intent_advisory(enriched_candidates):
    """Attach uncertified interpretation to verified selected occurrences."""
    from backend.server.engine.semantic_phrase_topic_intent_producer import (
        produce_phrase_topic_intent_context,
        accept_phrase_topic_intent_interpretation,
    )

    if not isinstance(enriched_candidates, list):
        raise TypeError("Expected enriched candidate list")

    for index, enriched in enumerate(enriched_candidates):
        if not isinstance(enriched, dict):
            continue

        candidate = enriched.get("original_candidate")
        semantic = enriched.get("semantic_context")

        if not isinstance(candidate, dict) or not isinstance(semantic, dict):
            continue

        if "provisional_topic_intent" in semantic:
            continue

        advisory = {
            "status": "unavailable",
            "reason": "verified_source_occurrence_required",
            "certified": False,
            "automatic_linking_authorized": False,
            "linking_decision_performed": False,
        }
        semantic["provisional_topic_intent"] = advisory

        phrase = candidate.get("phrase")
        occurrence = candidate.get("selection_source_span")
        sentence = candidate.get("selection_sentence_context")

        if (
            candidate.get("selection_source_span_status") != "verified"
            or candidate.get("selection_sentence_context_status")
                != "derived_from_verified_span"
            or not isinstance(phrase, str)
            or not phrase.strip()
            or not isinstance(occurrence, dict)
            or not isinstance(sentence, dict)
        ):
            continue

        if (
            occurrence.get("coordinate_space") != "original_article"
            or sentence.get("coordinate_space") != "original_article"
        ):
            continue

        os_, oe = occurrence.get("start"), occurrence.get("end")
        ss, se = sentence.get("start"), sentence.get("end")
        ot, st = occurrence.get("text"), sentence.get("text")

        if (
            any(type(value) is not int for value in (os_, oe, ss, se))
            or not (0 <= ss <= os_ < oe <= se)
            or not isinstance(ot, str)
            or not isinstance(st, str)
            or len(st) != se - ss
            or len(ot) != oe - os_
            or st[os_ - ss:oe - ss] != ot
            or ot.casefold() != phrase.casefold()
        ):
            continue

        occurrence_id = candidate.get("selection_occurrence_id")
        if (
            not isinstance(occurrence_id, (str, int))
            or not str(occurrence_id).strip()
        ):
            occurrence_id = f"selector_occurrence:{index}:{os_}:{oe}"

        observation = produce_phrase_topic_intent_context(
            phrase=phrase,
            sentence=st,
            source_sentence_id=str(occurrence_id),
        )

        if observation.get("source_phrase_occurrence_verified") is not True:
            continue

        proposal = interpret_phrase_topic_intent(observation)

        result = accept_phrase_topic_intent_interpretation(
            source_observation=observation,
            provider_interpretation=proposal,
        )

        result["selection_occurrence_id"] = str(occurrence_id)
        result["selection_source_span"] = {
            "start": os_,
            "end": oe,
            "coordinate_space": "original_article",
        }
        result["selection_sentence_span"] = {
            "start": ss,
            "end": se,
            "coordinate_space": "original_article",
        }
        result["certified"] = False
        result["automatic_linking_authorized"] = False
        result["linking_decision_performed"] = False

        semantic["provisional_topic_intent"] = result

    return enriched_candidates
