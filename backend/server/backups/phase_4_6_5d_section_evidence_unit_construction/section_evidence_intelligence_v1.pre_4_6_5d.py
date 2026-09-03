from __future__ import annotations

import hashlib
import re
from collections import Counter, defaultdict
from typing import Any, Mapping


SECTION_EVIDENCE_INTELLIGENCE_VERSION = (
    "section_evidence_intelligence_v1"
)


class SectionEvidenceIntelligenceError(ValueError):
    """Raised when canonical Section Evidence Intelligence cannot proceed."""


def _stable_id(prefix: str, *parts: Any) -> str:
    raw = "|".join(str(part) for part in parts)
    digest = hashlib.sha1(
        raw.encode("utf-8")
    ).hexdigest()[:12]
    return f"{prefix}_{digest}"


def validate_section_evidence_intake_v1(
    topic_intent_result: Mapping[str, Any],
    phrase_neighborhood_result: Mapping[str, Any],
    entity_concept_result: Mapping[str, Any],
    runtime_reader_result: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate the certified 4.6.1-4.6.4 -> 4.6.5 handoff."""

    if not isinstance(topic_intent_result, Mapping):
        raise SectionEvidenceIntelligenceError(
            "topic_intent_result must be a mapping."
        )

    if not isinstance(phrase_neighborhood_result, Mapping):
        raise SectionEvidenceIntelligenceError(
            "phrase_neighborhood_result must be a mapping."
        )

    if not isinstance(entity_concept_result, Mapping):
        raise SectionEvidenceIntelligenceError(
            "entity_concept_result must be a mapping."
        )

    if not isinstance(runtime_reader_result, Mapping):
        raise SectionEvidenceIntelligenceError(
            "runtime_reader_result must be a mapping."
        )

    if (
        topic_intent_result.get("schema_version")
        != "topic_intent_intelligence_result_v1"
    ):
        raise SectionEvidenceIntelligenceError(
            "Unsupported Topic Intent Intelligence result schema."
        )

    if (
        topic_intent_result.get("status")
        != "TOPIC_INTENT_INTELLIGENCE_COMPLETE"
    ):
        raise SectionEvidenceIntelligenceError(
            "Topic Intent Intelligence is not complete."
        )

    if topic_intent_result.get("phase") != "4.6.4":
        raise SectionEvidenceIntelligenceError(
            "Topic Intent Intelligence phase is invalid."
        )

    if (
        topic_intent_result.get("next_stage")
        != "section_evidence_intelligence"
    ):
        raise SectionEvidenceIntelligenceError(
            "Topic Intent Intelligence is not authorized to hand off "
            "to Section Evidence Intelligence."
        )

    boundaries = topic_intent_result.get(
        "processing_boundaries"
    )

    if not isinstance(boundaries, Mapping):
        raise SectionEvidenceIntelligenceError(
            "Topic Intent Intelligence boundary evidence is missing."
        )

    if boundaries.get("article_local_only") is not True:
        raise SectionEvidenceIntelligenceError(
            "Topic Intent Intelligence is not article-local."
        )

    if (
        boundaries.get(
            "section_evidence_intelligence_performed"
        )
        is not False
    ):
        raise SectionEvidenceIntelligenceError(
            "Section Evidence Intelligence was already performed."
        )

    if (
        topic_intent_result.get("persistence_policy")
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise SectionEvidenceIntelligenceError(
            "Unsupported Topic Intent persistence policy."
        )

    if (
        phrase_neighborhood_result.get("schema_version")
        != "phrase_neighborhood_intelligence_result_v1"
    ):
        raise SectionEvidenceIntelligenceError(
            "Unsupported Phrase Neighborhood Intelligence result schema."
        )

    if (
        phrase_neighborhood_result.get("status")
        != "PHRASE_NEIGHBORHOOD_INTELLIGENCE_COMPLETE"
    ):
        raise SectionEvidenceIntelligenceError(
            "Phrase Neighborhood Intelligence is not complete."
        )

    if (
        entity_concept_result.get("schema_version")
        != "entity_concept_intelligence_result_v1"
    ):
        raise SectionEvidenceIntelligenceError(
            "Unsupported Entity & Concept Intelligence result schema."
        )

    if (
        entity_concept_result.get("status")
        != "ENTITY_CONCEPT_INTELLIGENCE_COMPLETE"
    ):
        raise SectionEvidenceIntelligenceError(
            "Entity & Concept Intelligence is not complete."
        )

    if (
        runtime_reader_result.get("schema_version")
        != "semantic_intelligence_runtime_reader_result_v1"
    ):
        raise SectionEvidenceIntelligenceError(
            "Unsupported Runtime Reader result schema."
        )

    if (
        runtime_reader_result.get("status")
        != "SEMANTIC_RUNTIME_READING_COMPLETE"
    ):
        raise SectionEvidenceIntelligenceError(
            "Semantic Intelligence Runtime Reader is not complete."
        )

    runtime_model = runtime_reader_result.get(
        "semantic_reading_model"
    )

    if not isinstance(runtime_model, Mapping):
        raise SectionEvidenceIntelligenceError(
            "Semantic reading model is missing."
        )

    if runtime_model.get("structure_source") != "canonical_uucd":
        raise SectionEvidenceIntelligenceError(
            "Semantic reading model is not based on canonical UUCD structure."
        )

    validation = runtime_model.get("validation")

    if (
        not isinstance(validation, Mapping)
        or validation.get("valid") is not True
    ):
        raise SectionEvidenceIntelligenceError(
            "Semantic reading structure is not certified valid."
        )

    sections = runtime_model.get("sections")

    if not isinstance(sections, list) or not sections:
        raise SectionEvidenceIntelligenceError(
            "Canonical section structure is missing."
        )

    identity_fields = (
        "workspace_id",
        "document_id",
        "source_type",
        "source_id",
        "content_hash",
        "body_ref",
    )

    for field in identity_fields:
        expected = topic_intent_result.get(field)

        for name, model in (
            ("phrase_neighborhood", phrase_neighborhood_result),
            ("entity_concept", entity_concept_result),
            ("runtime_reader", runtime_reader_result),
        ):
            if model.get(field) != expected:
                raise SectionEvidenceIntelligenceError(
                    f"Identity mismatch for {field} in {name}."
                )

    article_id = str(
        topic_intent_result.get("article_id") or ""
    ).strip()

    runtime_article = runtime_model.get("article")

    if not isinstance(runtime_article, Mapping):
        raise SectionEvidenceIntelligenceError(
            "Runtime article identity is missing."
        )

    runtime_article_id = str(
        runtime_article.get("article_id") or ""
    ).strip()

    if (
        not article_id
        or not runtime_article_id
        or article_id != runtime_article_id
    ):
        raise SectionEvidenceIntelligenceError(
            "Topic Intent and Runtime Reader article identities "
            "do not match."
        )

    section_intents = topic_intent_result.get(
        "section_content_intents"
    )

    if (
        not isinstance(section_intents, list)
        or len(section_intents) != len(sections)
    ):
        raise SectionEvidenceIntelligenceError(
            "Topic Intent section coverage does not match "
            "canonical section structure."
        )

    return {
        "schema_version":
            "section_evidence_intake_v1",
        "phase":
            "4.6.5",
        "status":
            "SECTION_EVIDENCE_INTAKE_ACCEPTED",
        "workspace_id":
            topic_intent_result.get("workspace_id"),
        "document_id":
            topic_intent_result.get("document_id"),
        "source_type":
            topic_intent_result.get("source_type"),
        "source_id":
            topic_intent_result.get("source_id"),
        "content_hash":
            topic_intent_result.get("content_hash"),
        "body_ref":
            topic_intent_result.get("body_ref"),
        "article_id":
            article_id,
        "title":
            topic_intent_result.get("title"),
        "section_count":
            len(sections),
        "intake_authorized":
            True,
        "next_stage":
            "section_evidence_unit_construction",
    }


__all__ = [
    "SECTION_EVIDENCE_INTELLIGENCE_VERSION",
    "SectionEvidenceIntelligenceError",
    "validate_section_evidence_intake_v1",
]
