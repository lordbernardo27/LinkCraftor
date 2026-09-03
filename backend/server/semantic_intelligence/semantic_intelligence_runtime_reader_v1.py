"""Canonical Semantic Intelligence Runtime Reader v1.

Phase 4.6.1 foundation.

Current responsibility:
- accept one persisted canonical UUCD record;
- enforce the Semantic Readiness Gate;
- verify the canonical Universal Article Body Store body;
- read the exact canonical body;
- build the canonical structural Semantic Reading Model.

Domain/topic orientation and reconciliation are added in later
4.6.1 substages. This component does not perform Entity & Concept
Intelligence, Phrase Neighborhood Intelligence, reasoning, learning,
memory, scoring, linking, queue creation, or worker execution.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from backend.server.stores.semantic_article_reader import (
    read_semantic_article_v1,
)
from backend.server.semantic_intelligence.preliminary_domain_topic_orientation_v1 import (
    build_preliminary_domain_topic_orientation_v1,
)
from backend.server.semantic_intelligence.final_domain_topic_reconciliation_v1 import (
    reconcile_final_domain_topic_v1,
)
from backend.server.stores.source_lifecycle_control import (
    evaluate_source_semantic_readiness,
)
from backend.server.universal_article_body_store.body_store_repository_v1 import (
    read_body,
    verify_body,
)


SEMANTIC_INTELLIGENCE_RUNTIME_READER_VERSION = (
    "semantic_intelligence_runtime_reader_v1"
)


class SemanticIntelligenceRuntimeReaderError(RuntimeError):
    """Base error for Semantic Intelligence Runtime Reader failures."""


class SemanticReadinessBlockedError(
    SemanticIntelligenceRuntimeReaderError
):
    """Raised when the source has not passed Semantic Readiness."""


class SemanticBodyVerificationError(
    SemanticIntelligenceRuntimeReaderError
):
    """Raised when the canonical Body Store body is not verified."""


def _require_text(
    value: Any,
    *,
    field_name: str,
) -> str:
    if not isinstance(value, str):
        raise SemanticIntelligenceRuntimeReaderError(
            field_name + " must be a string."
        )

    normalized = value.strip()

    if not normalized:
        raise SemanticIntelligenceRuntimeReaderError(
            field_name + " must not be empty."
        )

    return normalized


def read_semantic_ready_article_v1(
    persisted_uucd_record: Mapping[str, Any],
    *,
    project_root: str | Path,
) -> dict[str, Any]:
    """Read one semantically eligible canonical article."""

    if not isinstance(persisted_uucd_record, Mapping):
        raise SemanticIntelligenceRuntimeReaderError(
            "persisted_uucd_record must be a mapping."
        )

    if (
        persisted_uucd_record.get("schema_version")
        != "universal_unified_content_document_v2"
    ):
        raise SemanticIntelligenceRuntimeReaderError(
            "Unsupported or non-canonical persisted UUCD schema."
        )

    if persisted_uucd_record.get("body_status") != "STORED_AND_VERIFIED":
        raise SemanticIntelligenceRuntimeReaderError(
            "Persisted UUCD body_status must be STORED_AND_VERIFIED."
        )

    persistence = persisted_uucd_record.get("persistence")

    if not isinstance(persistence, Mapping):
        raise SemanticIntelligenceRuntimeReaderError(
            "Persisted UUCD is missing canonical persistence evidence."
        )

    if (
        persistence.get("persistence_status")
        != "PERSISTED_AND_VERIFIED"
    ):
        raise SemanticIntelligenceRuntimeReaderError(
            "Persisted UUCD must be PERSISTED_AND_VERIFIED."
        )

    if persistence.get("content_body_stored_here") is not False:
        raise SemanticIntelligenceRuntimeReaderError(
            "Persisted UUCD violates the bodyless persistence contract."
        )

    if "content_body" in persisted_uucd_record:
        raise SemanticIntelligenceRuntimeReaderError(
            "Persisted UUCD must not contain content_body."
        )

    workspace_id = _require_text(
        persisted_uucd_record.get("workspace_id"),
        field_name="persisted_uucd_record.workspace_id",
    )
    source_type = _require_text(
        persisted_uucd_record.get("source_type"),
        field_name="persisted_uucd_record.source_type",
    )
    source_id = _require_text(
        persisted_uucd_record.get("source_id"),
        field_name="persisted_uucd_record.source_id",
    )
    document_id = _require_text(
        persisted_uucd_record.get("document_id"),
        field_name="persisted_uucd_record.document_id",
    )
    content_hash = _require_text(
        persisted_uucd_record.get("content_hash"),
        field_name="persisted_uucd_record.content_hash",
    )
    body_ref = _require_text(
        persisted_uucd_record.get("body_ref"),
        field_name="persisted_uucd_record.body_ref",
    )

    readiness = evaluate_source_semantic_readiness(
        workspace_id=workspace_id,
        source_type=source_type,
        source_id=source_id,
        document_id=document_id,
        content_hash=content_hash,
    )

    if (
        readiness.get("eligible") is not True
        or readiness.get("readiness_status") != "READY"
    ):
        reasons = readiness.get("reasons") or []
        raise SemanticReadinessBlockedError(
            "Semantic Readiness Gate blocked article: "
            + ", ".join(str(reason) for reason in reasons)
        )

    expected_body_length = persisted_uucd_record.get(
        "body_length"
    )
    expected_body_word_count = persisted_uucd_record.get(
        "body_word_count"
    )

    body_verification = verify_body(
        project_root=project_root,
        workspace_id=workspace_id,
        body_ref=body_ref,
        expected_content_hash=content_hash,
        expected_body_length=expected_body_length,
        expected_body_word_count=expected_body_word_count,
    )

    if body_verification.get("verification_status") != "VERIFIED":
        raise SemanticBodyVerificationError(
            "Canonical body did not return VERIFIED status."
        )

    canonical_body = read_body(
        project_root=project_root,
        workspace_id=workspace_id,
        body_ref=body_ref,
    )

    if not canonical_body.strip():
        raise SemanticBodyVerificationError(
            "Canonical Body Store returned an empty article body."
        )

    semantic_reading_model = read_semantic_article_v1(
        canonical_body,
        article_id=document_id,
        source_url=persisted_uucd_record.get("canonical_url"),
        title=persisted_uucd_record.get("title"),
        canonical_structure=persisted_uucd_record.get("structure"),
        canonical_h1=persisted_uucd_record.get("h1"),
    )

    validation = semantic_reading_model.get("validation")

    if not isinstance(validation, Mapping):
        raise SemanticIntelligenceRuntimeReaderError(
            "Semantic Reading Model is missing validation evidence."
        )

    if validation.get("valid") is not True:
        raise SemanticIntelligenceRuntimeReaderError(
            "Semantic Reading Model failed structural validation."
        )

    preliminary_orientation = (
        build_preliminary_domain_topic_orientation_v1(
            title=_require_text(
                persisted_uucd_record.get("title"),
                field_name="persisted_uucd_record.title",
            ),
            sections=semantic_reading_model.get("sections") or [],
        )
    )

    final_orientation = reconcile_final_domain_topic_v1(
        preliminary_orientation=preliminary_orientation,
        semantic_reading_model=semantic_reading_model,
    )

    return {
        "schema_version":
            "semantic_intelligence_runtime_reader_result_v1",
        "reader_version":
            SEMANTIC_INTELLIGENCE_RUNTIME_READER_VERSION,
        "phase":
            "4.6.1",
        "status":
            "SEMANTIC_RUNTIME_READING_COMPLETE",
        "workspace_id":
            workspace_id,
        "document_id":
            document_id,
        "source_type":
            source_type,
        "source_id":
            source_id,
        "content_hash":
            content_hash,
        "body_ref":
            body_ref,
        "semantic_readiness":
            readiness,
        "body_verification":
            body_verification,
        "semantic_reading_model":
            semantic_reading_model,
        "preliminary_domain_topic_orientation":
            preliminary_orientation,
        "final_domain_topic_reconciliation":
            final_orientation,
        "canonical_body_source":
            "universal_article_body_store",
        "raw_uucd_body_used":
            False,
        "semantic_processing_started":
            True,
        "entity_concept_intelligence_performed":
            False,
        "phrase_neighborhood_intelligence_performed":
            False,
        "reasoning_performed":
            False,
        "learning_performed":
            False,
        "memory_written":
            False,
        "next_stage":
            "entity_and_concept_intelligence",
    }


__all__ = [
    "SEMANTIC_INTELLIGENCE_RUNTIME_READER_VERSION",
    "SemanticIntelligenceRuntimeReaderError",
    "SemanticReadinessBlockedError",
    "SemanticBodyVerificationError",
    "read_semantic_ready_article_v1",
]
