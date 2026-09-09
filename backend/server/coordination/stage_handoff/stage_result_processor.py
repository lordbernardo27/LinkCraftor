"""
LinkCraftor
Universal Coordination Framework

PHASE 6.1 ? Stage Result Processor

Responsibility
--------------
Consume one canonical UniversalStageResult and convert it into a
coordination-facing processed result suitable for later Stage Handoff
phases.

This component:

- validates the canonical UniversalStageResult,
- confirms terminality,
- classifies the terminal disposition,
- preserves canonical workflow/stage/job identity,
- preserves output, result reference and artifact references,
- preserves failure evidence,
- indicates whether normal downstream handoff is allowed.

This component does NOT:

- map stage output into downstream input (Phase 6.2),
- propagate workflow context (Phase 6.3),
- hand off artifact references (Phase 6.4),
- perform handoff validation across stages (Phase 6.5),
- implement advanced skip semantics (Phase 7.7),
- invoke pipeline coordinator implementations,
- submit Runtime jobs,
- execute business logic,
- mutate Phase 4 dependency/planning state,
- mutate Phase 5 Runtime Integration state,
- mutate workflow lifecycle state.

Canonical upstream authority:
backend.server.coordination.universal_stages.result_contract
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Final, Mapping, Tuple

from backend.server.coordination.universal_stages.result_contract import (
    UniversalStageResult,
    UniversalStageResultStatus,
)


STAGE_RESULT_PROCESSOR_VERSION: Final[str] = (
    "stage_result_processor_v6.1.0"
)

STAGE_RESULT_PROCESSOR_SCHEMA_VERSION: Final[str] = (
    "stage_result_processor_schema_v1"
)


class StageResultProcessorError(
    ValueError
):
    """
    Raised when a stage result cannot be safely processed.
    """


class StageResultDisposition(
    str,
    Enum,
):
    """
    Coordination-facing terminal classification.

    COMPLETED
        Successful stage execution. Normal downstream handoff may
        proceed.

    FAILED
        Unsuccessful terminal stage execution. Normal downstream
        handoff must not proceed.

    SKIPPED
        Stage was deliberately not executed. SKIPPED does not satisfy
        prerequisites. Advanced skip semantics remain Phase 7.7.

    CANCELLED
        Stage execution / coordination was cancelled. Workflow
        lifecycle cancellation semantics remain owned by the workflow
        lifecycle subsystem.
    """

    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


_EMPTY_MAPPING: Final[Mapping[str, Any]] = (
    MappingProxyType({})
)


def _freeze(
    value: Any,
) -> Any:

    if isinstance(
        value,
        Mapping,
    ):
        return MappingProxyType(
            {
                str(key): _freeze(item)
                for key, item in value.items()
            }
        )

    if isinstance(
        value,
        list,
    ):
        return tuple(
            _freeze(item)
            for item in value
        )

    if isinstance(
        value,
        tuple,
    ):
        return tuple(
            _freeze(item)
            for item in value
        )

    if isinstance(
        value,
        set,
    ):
        return tuple(
            sorted(
                (
                    _freeze(item)
                    for item in value
                ),
                key=repr,
            )
        )

    return value


def _thaw(
    value: Any,
) -> Any:

    if isinstance(
        value,
        Mapping,
    ):
        return {
            str(key): _thaw(item)
            for key, item in value.items()
        }

    if isinstance(
        value,
        tuple,
    ):
        return [
            _thaw(item)
            for item in value
        ]

    return value


@dataclass(
    frozen=True,
    slots=True,
)
class ProcessedStageResult:
    """
    Immutable coordination-facing representation of one validated
    terminal UniversalStageResult.
    """

    result_id: str
    workflow_id: str
    correlation_id: str

    stage_id: str
    stage_version: str
    pipeline_id: str
    workflow_type: str
    workspace_id: str

    job_id: str
    job_type: str

    disposition: StageResultDisposition

    normal_handoff_allowed: bool
    prerequisite_satisfied: bool

    output: Mapping[str, Any]
    result_reference: str
    artifact_references: Tuple[str, ...]

    failure_code: str
    failure_message: str
    failure_details: Mapping[str, Any]

    metadata: Mapping[str, Any]

    source_result_contract_version: str
    processor_version: str = (
        STAGE_RESULT_PROCESSOR_VERSION
    )
    schema_version: str = (
        STAGE_RESULT_PROCESSOR_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        object.__setattr__(
            self,
            "output",
            _freeze(
                self.output
            ),
        )

        object.__setattr__(
            self,
            "failure_details",
            _freeze(
                self.failure_details
            ),
        )

        object.__setattr__(
            self,
            "metadata",
            _freeze(
                self.metadata
            ),
        )

        object.__setattr__(
            self,
            "artifact_references",
            tuple(
                self.artifact_references
            ),
        )

    @property
    def completed(
        self,
    ) -> bool:

        return (
            self.disposition
            == StageResultDisposition.COMPLETED
        )

    @property
    def failed(
        self,
    ) -> bool:

        return (
            self.disposition
            == StageResultDisposition.FAILED
        )

    @property
    def skipped(
        self,
    ) -> bool:

        return (
            self.disposition
            == StageResultDisposition.SKIPPED
        )

    @property
    def cancelled(
        self,
    ) -> bool:

        return (
            self.disposition
            == StageResultDisposition.CANCELLED
        )

    @property
    def terminal(
        self,
    ) -> bool:

        return True

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

            "stage_id":
                self.stage_id,

            "stage_version":
                self.stage_version,

            "pipeline_id":
                self.pipeline_id,

            "workflow_type":
                self.workflow_type,

            "workspace_id":
                self.workspace_id,

            "job_id":
                self.job_id,

            "job_type":
                self.job_type,

            "disposition":
                self.disposition.value,

            "normal_handoff_allowed":
                self.normal_handoff_allowed,

            "prerequisite_satisfied":
                self.prerequisite_satisfied,

            "output":
                _thaw(
                    self.output
                ),

            "result_reference":
                self.result_reference,

            "artifact_references":
                list(
                    self.artifact_references
                ),

            "failure_code":
                self.failure_code,

            "failure_message":
                self.failure_message,

            "failure_details":
                _thaw(
                    self.failure_details
                ),

            "metadata":
                _thaw(
                    self.metadata
                ),

            "source_result_contract_version":
                self.source_result_contract_version,

            "processor_version":
                self.processor_version,

            "schema_version":
                self.schema_version,
        }


def _validate_source_result(
    result: UniversalStageResult,
) -> None:

    if not isinstance(
        result,
        UniversalStageResult,
    ):
        raise StageResultProcessorError(
            "result must be a UniversalStageResult"
        )

    report = result.validate()

    valid = getattr(
        report,
        "valid",
        None,
    )

    if valid is None:
        valid = getattr(
            report,
            "is_valid",
            None,
        )

    if valid is False:
        raise StageResultProcessorError(
            "UniversalStageResult validation failed"
        )

    if not result.terminal:
        raise StageResultProcessorError(
            "UniversalStageResult must be terminal"
        )


def _classify(
    result: UniversalStageResult,
) -> tuple[
    StageResultDisposition,
    bool,
    bool,
]:

    status = result.status

    if (
        status
        == UniversalStageResultStatus.COMPLETED
    ):
        return (
            StageResultDisposition.COMPLETED,
            True,
            True,
        )

    if (
        status
        == UniversalStageResultStatus.FAILED
    ):
        return (
            StageResultDisposition.FAILED,
            False,
            False,
        )

    if (
        status
        == UniversalStageResultStatus.SKIPPED
    ):
        return (
            StageResultDisposition.SKIPPED,
            False,
            False,
        )

    if (
        status
        == UniversalStageResultStatus.CANCELLED
    ):
        return (
            StageResultDisposition.CANCELLED,
            False,
            False,
        )

    raise StageResultProcessorError(
        f"unsupported stage result status: {status!r}"
    )


def process_stage_result(
    result: UniversalStageResult,
) -> ProcessedStageResult:
    """
    Validate and normalize one terminal UniversalStageResult.

    No orchestration mutation, Runtime mutation, coordinator invocation,
    downstream payload mapping or lifecycle transition occurs here.
    """

    _validate_source_result(
        result
    )

    (
        disposition,
        normal_handoff_allowed,
        prerequisite_satisfied,
    ) = _classify(
        result
    )

    return ProcessedStageResult(
        result_id=
            result.result_id,

        workflow_id=
            result.workflow_id,

        correlation_id=
            result.correlation_id,

        stage_id=
            result.stage_id,

        stage_version=
            result.stage_version,

        pipeline_id=
            result.pipeline_id,

        workflow_type=
            result.workflow_type,

        workspace_id=
            result.workspace_id,

        job_id=
            result.job_id,

        job_type=
            result.job_type,

        disposition=
            disposition,

        normal_handoff_allowed=
            normal_handoff_allowed,

        prerequisite_satisfied=
            prerequisite_satisfied,

        output=
            result.output,

        result_reference=
            result.result_reference,

        artifact_references=
            tuple(
                result.artifact_references
            ),

        failure_code=
            result.failure_code,

        failure_message=
            result.failure_message,

        failure_details=
            result.failure_details,

        metadata=
            result.metadata,

        source_result_contract_version=
            result.contract_version,
    )


__all__ = [
    "STAGE_RESULT_PROCESSOR_VERSION",
    "STAGE_RESULT_PROCESSOR_SCHEMA_VERSION",
    "StageResultProcessorError",
    "StageResultDisposition",
    "ProcessedStageResult",
    "process_stage_result",
]
