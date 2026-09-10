"""
LinkCraftor
Universal Coordination Framework

PHASE 6.5 — Handoff Validation

Validates the complete Stage Handoff evidence chain produced by:

6.1 ProcessedStageResult
6.2 OutputInputMappingResult
6.3 RuntimeHandoffContext
6.4 ArtifactReferenceHandoffResult

The validator is evidence-only.

It does not:
- submit Runtime jobs,
- execute business logic,
- invoke coordinators,
- advance workflow state,
- mutate planning,
- mutate payloads,
- mutate RuntimeHandoffContext,
- mutate artifact references,
- perform Phase 6.6 certification.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Final, Tuple

from backend.server.coordination.runtime_integration.coordination_runtime_bridge import (
    RuntimeHandoffContext,
)

from backend.server.coordination.stage_handoff.artifact_reference_handoff import (
    ARTIFACT_REFERENCE_HANDOFF_VERSION,
    ArtifactReferenceHandoffResult,
)

from backend.server.coordination.stage_handoff.context_propagation import (
    CONTEXT_PROPAGATION_VERSION,
)

from backend.server.coordination.stage_handoff.output_input_mapping import (
    OUTPUT_INPUT_MAPPING_VERSION,
    OutputInputMappingResult,
)

from backend.server.coordination.stage_handoff.stage_result_processor import (
    STAGE_RESULT_PROCESSOR_VERSION,
    ProcessedStageResult,
)


HANDOFF_VALIDATION_VERSION: Final[str] = (
    "handoff_validation_v6.5.0"
)

HANDOFF_VALIDATION_SCHEMA_VERSION: Final[str] = (
    "handoff_validation_schema_v1"
)


@dataclass(
    frozen=True,
    slots=True,
)
class HandoffValidationResult:
    workflow_id: str
    correlation_id: str
    workspace_id: str

    source_stage_id: str
    target_stage_id: str

    is_valid: bool
    violations: Tuple[str, ...]

    source_processor_version: str
    mapping_version: str
    context_propagation_version: str
    artifact_handoff_version: str

    validation_version: str = (
        HANDOFF_VALIDATION_VERSION
    )

    schema_version: str = (
        HANDOFF_VALIDATION_SCHEMA_VERSION
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "correlation_id": self.correlation_id,
            "workspace_id": self.workspace_id,
            "source_stage_id": self.source_stage_id,
            "target_stage_id": self.target_stage_id,
            "is_valid": self.is_valid,
            "violations": list(self.violations),
            "source_processor_version": self.source_processor_version,
            "mapping_version": self.mapping_version,
            "context_propagation_version": self.context_propagation_version,
            "artifact_handoff_version": self.artifact_handoff_version,
            "validation_version": self.validation_version,
            "schema_version": self.schema_version,
        }


def _payload_plain(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            str(key): _payload_plain(item)
            for key, item in value.items()
        }

    if isinstance(value, tuple):
        return tuple(
            _payload_plain(item)
            for item in value
        )

    if isinstance(value, list):
        return [
            _payload_plain(item)
            for item in value
        ]

    return value


def validate_stage_handoff(
    source: ProcessedStageResult,
    mapping: OutputInputMappingResult,
    context: RuntimeHandoffContext,
    artifacts: ArtifactReferenceHandoffResult,
) -> HandoffValidationResult:

    type_violations: list[str] = []

    if not isinstance(source, ProcessedStageResult):
        type_violations.append(
            "source must be ProcessedStageResult"
        )

    if not isinstance(mapping, OutputInputMappingResult):
        type_violations.append(
            "mapping must be OutputInputMappingResult"
        )

    if not isinstance(context, RuntimeHandoffContext):
        type_violations.append(
            "context must be RuntimeHandoffContext"
        )

    if not isinstance(artifacts, ArtifactReferenceHandoffResult):
        type_violations.append(
            "artifacts must be ArtifactReferenceHandoffResult"
        )

    if type_violations:
        return HandoffValidationResult(
            workflow_id="",
            correlation_id="",
            workspace_id="",
            source_stage_id="",
            target_stage_id="",
            is_valid=False,
            violations=tuple(type_violations),
            source_processor_version="",
            mapping_version="",
            context_propagation_version=CONTEXT_PROPAGATION_VERSION,
            artifact_handoff_version="",
        )

    violations: list[str] = []

    # --------------------------------------------------------------
    # Source eligibility
    # --------------------------------------------------------------

    if not source.terminal:
        violations.append(
            "source must be terminal"
        )

    if not source.completed:
        violations.append(
            "source must be completed"
        )

    if not source.normal_handoff_allowed:
        violations.append(
            "source normal_handoff_allowed must be true"
        )

    if not source.prerequisite_satisfied:
        violations.append(
            "source prerequisite_satisfied must be true"
        )

    # --------------------------------------------------------------
    # 6.1 -> 6.2 identity continuity
    # --------------------------------------------------------------

    identity_pairs = (
        (
            "mapping source_result_id",
            mapping.source_result_id,
            source.result_id,
        ),
        (
            "mapping source_workflow_id",
            mapping.source_workflow_id,
            source.workflow_id,
        ),
        (
            "mapping source_correlation_id",
            mapping.source_correlation_id,
            source.correlation_id,
        ),
        (
            "mapping source_stage_id",
            mapping.source_stage_id,
            source.stage_id,
        ),
        (
            "mapping source_stage_version",
            mapping.source_stage_version,
            source.stage_version,
        ),
        (
            "mapping source_pipeline_id",
            mapping.source_pipeline_id,
            source.pipeline_id,
        ),
        (
            "mapping source_workspace_id",
            mapping.source_workspace_id,
            source.workspace_id,
        ),
        (
            "mapping source_job_id",
            mapping.source_job_id,
            source.job_id,
        ),
    )

    for name, actual, expected in identity_pairs:
        if actual != expected:
            violations.append(
                f"{name} mismatch"
            )

    # --------------------------------------------------------------
    # Mapping completeness
    # --------------------------------------------------------------

    if not mapping.complete:
        violations.append(
            "output-to-input mapping must be complete"
        )

    if mapping.missing_payload_fields:
        violations.append(
            "output-to-input mapping contains missing payload fields"
        )

    if (
        tuple(mapping.satisfied_payload_fields)
        != tuple(mapping.required_payload_fields)
    ):
        violations.append(
            "mapping satisfied fields do not exactly match required fields"
        )

    # --------------------------------------------------------------
    # 6.3 context identity continuity
    # --------------------------------------------------------------

    if context.workflow_id != source.workflow_id:
        violations.append(
            "context workflow_id mismatch"
        )

    if context.workspace_id != source.workspace_id:
        violations.append(
            "context workspace_id mismatch"
        )

    if context.correlation_id != source.correlation_id:
        violations.append(
            "context correlation_id mismatch"
        )

    # --------------------------------------------------------------
    # Target payload installation
    # --------------------------------------------------------------

    if mapping.target_stage_id not in context.payload_by_stage:
        violations.append(
            "target stage payload missing from propagated context"
        )
    else:
        context_payload = (
            context.payload_by_stage[
                mapping.target_stage_id
            ]
        )

        if (
            _payload_plain(context_payload)
            != _payload_plain(mapping.payload)
        ):
            violations.append(
                "target stage context payload does not match mapped payload"
            )

    # --------------------------------------------------------------
    # 6.4 artifact/result lineage
    # --------------------------------------------------------------

    artifact_identity_pairs = (
        (
            "artifact result_id",
            artifacts.result_id,
            source.result_id,
        ),
        (
            "artifact workflow_id",
            artifacts.workflow_id,
            source.workflow_id,
        ),
        (
            "artifact correlation_id",
            artifacts.correlation_id,
            source.correlation_id,
        ),
        (
            "artifact source_stage_id",
            artifacts.source_stage_id,
            source.stage_id,
        ),
        (
            "artifact source_stage_version",
            artifacts.source_stage_version,
            source.stage_version,
        ),
        (
            "artifact source_pipeline_id",
            artifacts.source_pipeline_id,
            source.pipeline_id,
        ),
        (
            "artifact workspace_id",
            artifacts.workspace_id,
            source.workspace_id,
        ),
        (
            "artifact source_job_id",
            artifacts.source_job_id,
            source.job_id,
        ),
    )

    for name, actual, expected in artifact_identity_pairs:
        if actual != expected:
            violations.append(
                f"{name} mismatch"
            )

    if artifacts.result_reference != source.result_reference:
        violations.append(
            "artifact handoff result_reference mismatch"
        )

    if (
        tuple(artifacts.artifact_references)
        != tuple(source.artifact_references)
    ):
        violations.append(
            "artifact handoff artifact_references mismatch"
        )

    if artifacts.artifact_count != len(
        artifacts.artifact_references
    ):
        violations.append(
            "artifact_count mismatch"
        )

    if artifacts.has_artifacts != bool(
        artifacts.artifact_references
    ):
        violations.append(
            "has_artifacts mismatch"
        )

    # --------------------------------------------------------------
    # Version lineage
    # --------------------------------------------------------------

    if (
        source.processor_version
        != STAGE_RESULT_PROCESSOR_VERSION
    ):
        violations.append(
            "source processor version mismatch"
        )

    if (
        mapping.mapper_version
        != OUTPUT_INPUT_MAPPING_VERSION
    ):
        violations.append(
            "mapping version mismatch"
        )

    if (
        artifacts.handoff_version
        != ARTIFACT_REFERENCE_HANDOFF_VERSION
    ):
        violations.append(
            "artifact handoff version mismatch"
        )

    canonical_violations = tuple(
        violations
    )

    return HandoffValidationResult(
        workflow_id=source.workflow_id,
        correlation_id=source.correlation_id,
        workspace_id=source.workspace_id,
        source_stage_id=source.stage_id,
        target_stage_id=mapping.target_stage_id,
        is_valid=not canonical_violations,
        violations=canonical_violations,
        source_processor_version=source.processor_version,
        mapping_version=mapping.mapper_version,
        context_propagation_version=CONTEXT_PROPAGATION_VERSION,
        artifact_handoff_version=artifacts.handoff_version,
    )


__all__ = [
    "HANDOFF_VALIDATION_VERSION",
    "HANDOFF_VALIDATION_SCHEMA_VERSION",
    "HandoffValidationResult",
    "validate_stage_handoff",
]
