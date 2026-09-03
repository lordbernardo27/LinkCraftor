"""Final Domain/Topic Reconciliation v1.

Phase 4.6.1H.

Reconciles preliminary title/heading orientation against the complete
hierarchical Semantic Reading Model.

This remains article-orientation intelligence. It does not perform
Entity & Concept Intelligence, Topic Intent Intelligence, ontology
alignment, reasoning, learning, or Semantic Memory writes.
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Any, Mapping


FINAL_DOMAIN_TOPIC_RECONCILIATION_VERSION = (
    "final_domain_topic_reconciliation_v1"
)

_WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9'-]*")

_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "because", "been",
    "but", "by", "can", "for", "from", "has", "have", "how", "in",
    "into", "is", "it", "its", "may", "of", "on", "or", "our",
    "that", "the", "their", "these", "they", "this", "to", "too",
    "use", "used", "using", "what", "when", "where", "which", "with",
}


class FinalDomainTopicReconciliationError(RuntimeError):
    """Raised when article-orientation reconciliation cannot complete."""


def _terms(text: str) -> list[str]:
    return [
        token.casefold()
        for token in _WORD_RE.findall(text or "")
        if len(token) > 2
        and token.casefold() not in _STOPWORDS
    ]


def reconcile_final_domain_topic_v1(
    *,
    preliminary_orientation: Mapping[str, Any],
    semantic_reading_model: Mapping[str, Any],
) -> dict[str, Any]:
    """Reconcile preliminary orientation with complete article evidence."""

    if not isinstance(preliminary_orientation, Mapping):
        raise FinalDomainTopicReconciliationError(
            "preliminary_orientation must be a mapping."
        )

    if (
        preliminary_orientation.get("status")
        != "PRELIMINARY_ORIENTATION_COMPLETE"
    ):
        raise FinalDomainTopicReconciliationError(
            "Preliminary orientation is not complete."
        )

    if not isinstance(semantic_reading_model, Mapping):
        raise FinalDomainTopicReconciliationError(
            "semantic_reading_model must be a mapping."
        )

    validation = semantic_reading_model.get("validation")

    if (
        not isinstance(validation, Mapping)
        or validation.get("valid") is not True
    ):
        raise FinalDomainTopicReconciliationError(
            "Semantic Reading Model is not structurally valid."
        )

    preliminary_terms = preliminary_orientation.get(
        "ranked_topic_terms"
    ) or []

    preliminary_weights: dict[str, int] = {}

    for item in preliminary_terms:
        if not isinstance(item, Mapping):
            continue

        term = item.get("term")
        weight = item.get("orientation_weight")

        if (
            isinstance(term, str)
            and term.strip()
            and isinstance(weight, int)
            and weight > 0
        ):
            preliminary_weights[term.casefold()] = weight

    body_terms: list[str] = []

    for block in semantic_reading_model.get("blocks") or []:
        if not isinstance(block, Mapping):
            continue

        text = block.get("text")

        if isinstance(text, str):
            body_terms.extend(_terms(text))

    if not body_terms:
        raise FinalDomainTopicReconciliationError(
            "No hierarchical article text evidence is available."
        )

    body_frequencies = Counter(body_terms)

    evidence_order: dict[str, int] = {}

    for index, term in enumerate(body_terms):
        evidence_order.setdefault(term, index)

    candidate_terms = set(body_frequencies) | set(preliminary_weights)

    reconciled = []

    for term in candidate_terms:
        preliminary_weight = preliminary_weights.get(term, 0)
        full_article_frequency = body_frequencies.get(term, 0)

        reconciliation_score = (
            preliminary_weight * 3
            + full_article_frequency
        )

        reconciled.append({
            "term": term,
            "preliminary_weight": preliminary_weight,
            "full_article_frequency": full_article_frequency,
            "reconciliation_score": reconciliation_score,
        })

    reconciled.sort(
        key=lambda item: (
            -item["reconciliation_score"],
            -item["preliminary_weight"],
            evidence_order.get(item["term"], 10**9),
            item["term"],
        )
    )

    reconciled = reconciled[:12]

    final_primary_topic = (
        reconciled[0]["term"]
        if reconciled
        else None
    )

    preliminary_primary_topic = preliminary_orientation.get(
        "primary_topic_hint"
    )

    topic_reconciled = (
        isinstance(final_primary_topic, str)
        and bool(final_primary_topic)
    )

    return {
        "schema_version":
            "final_domain_topic_reconciliation_result_v1",
        "reconciliation_version":
            FINAL_DOMAIN_TOPIC_RECONCILIATION_VERSION,
        "status":
            "FINAL_ORIENTATION_RECONCILED",
        "evidence_scope":
            "preliminary_orientation_plus_full_hierarchical_article",
        "preliminary_primary_topic":
            preliminary_primary_topic,
        "final_primary_topic":
            final_primary_topic,
        "primary_topic_confirmed":
            final_primary_topic == preliminary_primary_topic,
        "topic_reconciled":
            topic_reconciled,
        "reconciled_topic_terms":
            reconciled,
        "domain_hint":
            None,
        "domain_reconciliation_status":
            "UNCLASSIFIED_NO_CANONICAL_DOMAIN_TAXONOMY",
        "entity_concept_intelligence_performed":
            False,
        "topic_intent_intelligence_performed":
            False,
        "reasoning_performed":
            False,
        "ontology_alignment_performed":
            False,
        "learning_performed":
            False,
        "memory_written":
            False,
    }


__all__ = [
    "FINAL_DOMAIN_TOPIC_RECONCILIATION_VERSION",
    "FinalDomainTopicReconciliationError",
    "reconcile_final_domain_topic_v1",
]
