"""Preliminary Domain/Topic Orientation v1.

Phase 4.6.1F.

Provides lightweight, deterministic orientation from canonical article
title and section headings before deeper semantic intelligence begins.

This component does not perform entity extraction, concept extraction,
topic-intent reasoning, semantic similarity, ontology alignment,
knowledge retrieval, learning, or semantic-memory writes.
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Any, Mapping, Sequence


PRELIMINARY_DOMAIN_TOPIC_ORIENTATION_VERSION = (
    "preliminary_domain_topic_orientation_v1"
)

_WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9'-]*")

_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "because", "been",
    "but", "by", "can", "for", "from", "has", "have", "how", "in",
    "into", "is", "it", "its", "may", "of", "on", "or", "our",
    "that", "the", "their", "these", "they", "this", "to", "too",
    "use", "used", "using", "what", "when", "where", "which", "with",
}


class PreliminaryDomainTopicOrientationError(RuntimeError):
    """Raised when preliminary orientation cannot be produced safely."""


def _terms(text: str) -> list[str]:
    return [
        token.casefold()
        for token in _WORD_RE.findall(text or "")
        if len(token) > 2
        and token.casefold() not in _STOPWORDS
    ]


def build_preliminary_domain_topic_orientation_v1(
    *,
    title: str,
    sections: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Build lightweight orientation from title and canonical headings."""

    if not isinstance(title, str) or not title.strip():
        raise PreliminaryDomainTopicOrientationError(
            "title must be a non-empty string."
        )

    if not isinstance(sections, Sequence) or isinstance(
        sections,
        (str, bytes),
    ):
        raise PreliminaryDomainTopicOrientationError(
            "sections must be a sequence."
        )

    canonical_headings: list[str] = []

    for section in sections:
        if not isinstance(section, Mapping):
            continue

        section_title = section.get("section_title")

        if isinstance(section_title, str) and section_title.strip():
            canonical_headings.append(section_title.strip())

    if not canonical_headings:
        raise PreliminaryDomainTopicOrientationError(
            "No canonical section headings are available."
        )

    title_terms = _terms(title)
    heading_terms = [
        term
        for heading in canonical_headings
        for term in _terms(heading)
    ]

    weighted_terms = (
        title_terms
        + title_terms
        + title_terms
        + heading_terms
    )

    frequencies = Counter(weighted_terms)

    first_evidence_position: dict[str, int] = {}

    for index, term in enumerate(weighted_terms):
        first_evidence_position.setdefault(term, index)

    ranked_topic_terms = [
        {
            "term": term,
            "orientation_weight": count,
        }
        for term, count in sorted(
            frequencies.items(),
            key=lambda item: (
                -item[1],
                first_evidence_position[item[0]],
            ),
        )[:12]
    ]

    primary_topic_hint = (
        ranked_topic_terms[0]["term"]
        if ranked_topic_terms
        else None
    )

    return {
        "schema_version":
            "preliminary_domain_topic_orientation_result_v1",
        "orientation_version":
            PRELIMINARY_DOMAIN_TOPIC_ORIENTATION_VERSION,
        "status":
            "PRELIMINARY_ORIENTATION_COMPLETE",
        "orientation_scope":
            "title_and_canonical_headings_only",
        "title":
            title.strip(),
        "canonical_heading_count":
            len(canonical_headings),
        "canonical_headings":
            canonical_headings,
        "primary_topic_hint":
            primary_topic_hint,
        "ranked_topic_terms":
            ranked_topic_terms,
        "domain_hint":
            None,
        "domain_classification_status":
            "DEFERRED_TO_DEEPER_SEMANTIC_INTELLIGENCE",
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
    "PRELIMINARY_DOMAIN_TOPIC_ORIENTATION_VERSION",
    "PreliminaryDomainTopicOrientationError",
    "build_preliminary_domain_topic_orientation_v1",
]
