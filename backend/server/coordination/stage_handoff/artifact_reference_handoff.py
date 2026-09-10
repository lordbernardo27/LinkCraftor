"""
LinkCraftor
Universal Coordination Framework

PHASE 6.4 — Artifact Reference Handoff

Purpose
-------
Preserve and hand off canonical references produced by one successfully
completed stage.

Canonical source
----------------
ProcessedStageResult.result_reference
ProcessedStageResult.artifact_references

Canonical validation / normalization authorities
------------------------------------------------
backend.server.runtime.universal_jobs.result_reference
backend.server.runtime.universal_jobs.artifact_references

Meaning
-------
result_reference identifies the primary logical stage result.

artifact_references identify zero or more supporting/generated resources.

Phase 6.4 performs reference handoff only.

It does NOT:
- create artifacts,
- open/read artifact contents,
- write artifacts,
- copy artifact bytes,
- persist artifacts,
- delete artifacts,
- resolve storage locations,
- submit Runtime jobs,
- invoke coordinators,
- mutate RuntimeHandoffContext,
- mutate Phase 6.2 payload mapping,
- mutate workflow lifecycle state,
- perform final Stage Handoff validation (Phase 6.5).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final, Tuple

from backend.server.coordination.stage_handoff.stage_result_processor import (
    ProcessedStageResult,
)

from backend.server.runtime.universal_jobs.artifact_references import (
    UNIVERSAL_JOB_ARTIFACT_REFERENCES_SCHEMA_VERSION,
    UNIVERSAL_JOB_ARTIFACT_REFERENCES_VERSION,
    normalize_universal_job_artifact_references,
)

from backend.server.runtime.universal_jobs.result_reference import (
    UNIVERSAL_JOB_RESULT_REFERENCE_SCHEMA_VERSION,
    UNIVERSAL_JOB_RESULT_REFERENCE_VERSION,
    normalize_universal_job_result_reference,
)


ARTIFACT_REFERENCE_HANDOFF_VERSION: Final[str] = (
    "artifact_reference_handoff_v6.4.0"
)

ARTIFACT_REFERENCE_HANDOFF_SCHEMA_VERSION: Final[str] = (
    "artifact_reference_handoff_schema_v1"
)


class ArtifactReferenceHandoffError(
    ValueError
):
    """
    Raised when canonical reference handoff cannot safely be produced.
    """


@dataclass(
    frozen=True,
    slots=True,
)
class ArtifactReferenceHandoffResult:
    """
    Immutable Phase 6.4 reference-only Stage Handoff evidence.
    """

    result_id: str
    workflow_id: str
    correlation_id: str

    source_stage_id: str
    source_stage_version: str
    source_pipeline_id: str
    workspace_id: str
    source_job_id: str

    result_reference: str
    artifact_references: Tuple[str, ...]

    artifact_count: int
    has_artifacts: bool

    source_processor_version: str

    result_reference_authority_version: str
    result_reference_authority_schema_version: str

    artifact_reference_authority_version: str
    artifact_reference_authority_schema_version: str

    handoff_version: str = (
        ARTIFACT_REFERENCE_HANDOFF_VERSION
    )

    schema_version: str = (
        ARTIFACT_REFERENCE_HANDOFF_SCHEMA_VERSION
    )

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "result_id":
                self.result_id,

            "workflow_id":
                self.workflow_id,

            "correlation_id":
                self.correlation_id,

            "source_stage_id":
                self.source_stage_id,

            "source_stage_version":
                self.source_stage_version,

            "source_pipeline_id":
                self.source_pipeline_id,

            "workspace_id":
                self.workspace_id,

            "source_job_id":
                self.source_job_id,

            "result_reference":
                self.result_reference,

            "artifact_references":
                list(
                    self.artifact_references
                ),

            "artifact_count":
                self.artifact_count,

            "has_artifacts":
                self.has_artifacts,

            "source_processor_version":
                self.source_processor_version,

            "result_reference_authority_version":
                self.result_reference_authority_version,

            "result_reference_authority_schema_version":
                self.result_reference_authority_schema_version,

            "artifact_reference_authority_version":
                self.artifact_reference_authority_version,

            "artifact_reference_authority_schema_version":
                self.artifact_reference_authority_schema_version,

            "handoff_version":
                self.handoff_version,

            "schema_version":
                self.schema_version,
        }


def _validate_source(
    source: ProcessedStageResult,
) -> None:

    if not isinstance(
        source,
        ProcessedStageResult,
    ):
        raise ArtifactReferenceHandoffError(
            "source must be a ProcessedStageResult"
        )

    if not source.terminal:
        raise ArtifactReferenceHandoffError(
            "source must be terminal"
        )

    if not source.completed:
        raise ArtifactReferenceHandoffError(
            "artifact reference handoff requires a completed source"
        )

    if not source.normal_handoff_allowed:
        raise ArtifactReferenceHandoffError(
            "normal handoff must be allowed before artifact reference handoff"
        )


def handoff_artifact_references(
    source: ProcessedStageResult,
) -> ArtifactReferenceHandoffResult:
    """
    Produce immutable canonical reference-only handoff evidence.

    No artifact storage or artifact contents are accessed.
    """

    _validate_source(
        source
    )

    try:
        result_reference = (
            normalize_universal_job_result_reference(
                source.result_reference
            )
        )
    except Exception as exc:
        raise ArtifactReferenceHandoffError(
            "result_reference failed canonical Runtime normalization"
        ) from exc

    try:
        artifact_references = (
            normalize_universal_job_artifact_references(
                source.artifact_references
            )
        )
    except Exception as exc:
        raise ArtifactReferenceHandoffError(
            "artifact_references failed canonical Runtime normalization"
        ) from exc

    if result_reference is None:
        raise ArtifactReferenceHandoffError(
            "completed Stage Handoff requires a canonical result_reference"
        )

    if not isinstance(
        result_reference,
        str,
    ):
        raise ArtifactReferenceHandoffError(
            "canonical result_reference must be a string"
        )

    if not isinstance(
        artifact_references,
        tuple,
    ):
        artifact_references = tuple(
            artifact_references
        )

    return ArtifactReferenceHandoffResult(
        result_id=
            source.result_id,

        workflow_id=
            source.workflow_id,

        correlation_id=
            source.correlation_id,

        source_stage_id=
            source.stage_id,

        source_stage_version=
            source.stage_version,

        source_pipeline_id=
            source.pipeline_id,

        workspace_id=
            source.workspace_id,

        source_job_id=
            source.job_id,

        result_reference=
            result_reference,

        artifact_references=
            tuple(
                artifact_references
            ),

        artifact_count=
            len(
                artifact_references
            ),

        has_artifacts=
            bool(
                artifact_references
            ),

        source_processor_version=
            source.processor_version,

        result_reference_authority_version=
            UNIVERSAL_JOB_RESULT_REFERENCE_VERSION,

        result_reference_authority_schema_version=
            UNIVERSAL_JOB_RESULT_REFERENCE_SCHEMA_VERSION,

        artifact_reference_authority_version=
            UNIVERSAL_JOB_ARTIFACT_REFERENCES_VERSION,

        artifact_reference_authority_schema_version=
            UNIVERSAL_JOB_ARTIFACT_REFERENCES_SCHEMA_VERSION,
    )


__all__ = [
    "ARTIFACT_REFERENCE_HANDOFF_VERSION",
    "ARTIFACT_REFERENCE_HANDOFF_SCHEMA_VERSION",
    "ArtifactReferenceHandoffError",
    "ArtifactReferenceHandoffResult",
    "handoff_artifact_references",
]
