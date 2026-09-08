from __future__ import annotations

from pathlib import Path


ROOT = Path.cwd()

TARGET = (
    ROOT
    / "backend/server/coordination/runtime_integration/"
      "runtime_completion_intake.py"
)


SOURCE = r'''from __future__ import annotations

"""
LinkCraftor Universal Coordination Framework
Phase 5.4 — Runtime Completion Intake

Responsibility:
    Convert one authoritative successful Runtime completion into one
    canonical UniversalStageResult.

Canonical authorities:
    - completion status:
        canonical orchestration persisted job

    - completion timing:
        orchestration JobStatusEvent trail

    - coordination identity:
        frozen Phase 5.3 WorkflowJobCorrelation

    - output:
        completed orchestration job metadata["runtime_dispatch_result"]

Rules:
    - latest COMPLETED event is the completion event
    - latest RUNNING event preceding that COMPLETED event is started_at
    - completion event.event_id becomes result_id
    - completion event.created_at becomes finished_at
    - RUNNING event.created_at becomes started_at

This component is READ-ONLY with respect to Runtime/orchestration.

It does NOT:
    - create or submit Runtime jobs
    - mark jobs running/completed/failed
    - update Runtime status/progress
    - dispatch or execute handlers
    - generate job_id
    - rewrite job_id
    - generate random result_id
    - fabricate timestamps
    - persist completion
    - process Runtime failures
    - create another workflow/job correlation authority
"""

from collections.abc import Callable, Mapping, Sequence
from copy import deepcopy
from dataclasses import asdict, is_dataclass
from datetime import datetime
from types import MappingProxyType
from typing import Any

from backend.server.coordination.runtime_integration.workflow_job_correlation import (
    WorkflowJobCorrelation,
    WorkflowJobCorrelationRegistry,
    get_workflow_job_correlation_registry,
)

from backend.server.coordination.universal_stages.result_contract import (
    UniversalStageResult,
    UniversalStageResultStatus,
)

from backend.server.orchestration.job_store import (
    list_job_events,
)

from backend.server.orchestration.service import (
    get_orchestration_job,
)


RUNTIME_COMPLETION_INTAKE_VERSION = (
    "runtime_completion_intake_v5.4.0"
)

RUNTIME_COMPLETION_INTAKE_SCHEMA_VERSION = (
    "runtime_completion_intake_schema_v1"
)


class RuntimeCompletionIntakeError(
    ValueError
):
    pass


class RuntimeCompletionValidationError(
    RuntimeCompletionIntakeError
):
    def __init__(
        self,
        message: str,
        *,
        violations: tuple[str, ...] = (),
    ) -> None:

        super().__init__(
            message
        )

        self.violations = tuple(
            str(item)
            for item
            in violations
        )


class RuntimeCompletionNotReadyError(
    RuntimeCompletionValidationError
):
    pass


def _required_text(
    value: Any,
    *,
    name: str,
) -> str:

    normalized = str(
        value
        or ""
    ).strip()

    if not normalized:
        raise RuntimeCompletionValidationError(
            f"{name} is required.",
            violations=(
                f"{name} is required",
            ),
        )

    return normalized


def _status_text(
    value: Any,
) -> str:

    raw = getattr(
        value,
        "value",
        value,
    )

    return str(
        raw
        or ""
    ).strip().lower()


def _timestamp_text(
    value: Any,
    *,
    name: str,
) -> str:

    if isinstance(
        value,
        datetime,
    ):
        normalized = value.isoformat()

    else:
        normalized = str(
            value
            or ""
        ).strip()

    if not normalized:
        raise RuntimeCompletionValidationError(
            f"{name} is required.",
            violations=(
                f"{name} is required",
            ),
        )

    return normalized


def _mapping_copy(
    value: Any,
    *,
    name: str,
) -> dict[str, Any]:

    if value is None:
        return {}

    if isinstance(
        value,
        Mapping,
    ):
        return deepcopy(
            dict(
                value
            )
        )

    if is_dataclass(
        value
    ):
        return deepcopy(
            asdict(
                value
            )
        )

    raise RuntimeCompletionValidationError(
        f"{name} must be a mapping.",
        violations=(
            f"{name} must be a mapping",
        ),
    )


def _object_value(
    value: Any,
    name: str,
    default: Any = None,
) -> Any:

    if isinstance(
        value,
        Mapping,
    ):
        return value.get(
            name,
            default,
        )

    return getattr(
        value,
        name,
        default,
    )


def _normalize_events(
    events: Any,
) -> tuple[
    dict[str, Any],
    ...,
]:

    if events is None:
        return ()

    if isinstance(
        events,
        (
            str,
            bytes,
            bytearray,
        ),
    ):
        raise RuntimeCompletionValidationError(
            "completion events must be a sequence.",
            violations=(
                "completion events must be a sequence",
            ),
        )

    if not isinstance(
        events,
        Sequence,
    ):
        raise RuntimeCompletionValidationError(
            "completion events must be a sequence.",
            violations=(
                "completion events must be a sequence",
            ),
        )

    normalized = []

    for index, event in enumerate(
        events
    ):
        normalized.append(
            _mapping_copy(
                event,
                name=f"events[{index}]",
            )
        )

    return tuple(
        normalized
    )


def _resolve_job_and_events(
    *,
    job_id: str,
    completion_reader: Callable[
        [str],
        Any,
    ],
    events_reader: Callable[
        [str],
        Any,
    ],
) -> tuple[
    Any,
    tuple[
        dict[str, Any],
        ...,
    ],
]:

    completion_document = completion_reader(
        job_id
    )

    if completion_document is None:
        raise RuntimeCompletionNotReadyError(
            "No orchestration completion record exists for job_id.",
            violations=(
                "completion job does not exist",
            ),
        )

    job = completion_document

    embedded_events = None

    if isinstance(
        completion_document,
        Mapping,
    ):
        if (
            "job"
            in completion_document
        ):
            job = completion_document[
                "job"
            ]

        embedded_events = (
            completion_document.get(
                "events"
            )
        )

    if job is None:
        raise RuntimeCompletionNotReadyError(
            "Completion document contains no orchestration job.",
            violations=(
                "completion job is missing",
            ),
        )

    if embedded_events is None:
        embedded_events = events_reader(
            job_id
        )

    return (
        job,
        _normalize_events(
            embedded_events
        ),
    )


def _select_completion_attempt(
    *,
    canonical_job_id: str,
    events: tuple[
        dict[str, Any],
        ...,
    ],
) -> tuple[
    dict[str, Any],
    dict[str, Any],
]:

    completion_index = None

    for index in range(
        len(events) - 1,
        -1,
        -1,
    ):
        event = events[
            index
        ]

        event_job_id = _required_text(
            event.get(
                "job_id"
            ),
            name=(
                f"events[{index}].job_id"
            ),
        )

        if (
            event_job_id
            != canonical_job_id
        ):
            raise RuntimeCompletionValidationError(
                (
                    "Completion event trail contains "
                    "a foreign job_id."
                ),
                violations=(
                    "event job_id mismatch",
                ),
            )

        if (
            _status_text(
                event.get(
                    "new_status"
                )
            )
            == "completed"
        ):
            completion_index = index
            break

    if completion_index is None:
        raise RuntimeCompletionNotReadyError(
            "No COMPLETED orchestration event exists for job_id.",
            violations=(
                "completed event is missing",
            ),
        )

    started_index = None

    for index in range(
        completion_index - 1,
        -1,
        -1,
    ):
        event = events[
            index
        ]

        event_job_id = _required_text(
            event.get(
                "job_id"
            ),
            name=(
                f"events[{index}].job_id"
            ),
        )

        if (
            event_job_id
            != canonical_job_id
        ):
            raise RuntimeCompletionValidationError(
                (
                    "Runtime attempt event contains "
                    "a foreign job_id."
                ),
                violations=(
                    "started event job_id mismatch",
                ),
            )

        if (
            _status_text(
                event.get(
                    "new_status"
                )
            )
            == "running"
        ):
            started_index = index
            break

    if started_index is None:
        raise RuntimeCompletionValidationError(
            (
                "No RUNNING event precedes the "
                "selected COMPLETED event."
            ),
            violations=(
                "started event is missing",
            ),
        )

    return (
        events[
            started_index
        ],
        events[
            completion_index
        ],
    )


def _extract_result_reference(
    *,
    output: Mapping[
        str,
        Any,
    ],
    metadata: Mapping[
        str,
        Any,
    ],
) -> str:

    for source in (
        output,
        metadata,
    ):
        value = source.get(
            "result_reference"
        )

        if value is None:
            continue

        normalized = str(
            value
        ).strip()

        if normalized:
            return normalized

    return ""


def _extract_artifact_references(
    *,
    output: Mapping[
        str,
        Any,
    ],
    metadata: Mapping[
        str,
        Any,
    ],
) -> tuple[
    str,
    ...,
]:

    candidate = None

    for source in (
        output,
        metadata,
    ):
        if (
            "artifact_references"
            in source
        ):
            candidate = source.get(
                "artifact_references"
            )
            break

    if candidate is None:
        return ()

    if isinstance(
        candidate,
        str,
    ):
        normalized = candidate.strip()

        return (
            (normalized,)
            if normalized
            else ()
        )

    if not isinstance(
        candidate,
        Sequence,
    ):
        raise RuntimeCompletionValidationError(
            (
                "artifact_references must be "
                "a sequence when supplied."
            ),
            violations=(
                "artifact_references must be a sequence",
            ),
        )

    result = []

    for item in candidate:
        normalized = str(
            item
            or ""
        ).strip()

        if not normalized:
            raise RuntimeCompletionValidationError(
                (
                    "artifact_references cannot "
                    "contain empty values."
                ),
                violations=(
                    "artifact_references contains empty value",
                ),
            )

        result.append(
            normalized
        )

    return tuple(
        result
    )


def build_runtime_completion_stage_result(
    *,
    correlation: WorkflowJobCorrelation,
    completion_job: Any,
    events: Sequence[
        Mapping[
            str,
            Any,
        ]
    ],
) -> UniversalStageResult:

    if not isinstance(
        correlation,
        WorkflowJobCorrelation,
    ):
        raise RuntimeCompletionValidationError(
            (
                "correlation must be "
                "WorkflowJobCorrelation."
            ),
            violations=(
                "Phase 5.4 requires frozen Phase 5.3 correlation",
            ),
        )

    canonical_job_id = _required_text(
        _object_value(
            completion_job,
            "job_id",
        ),
        name="completion_job.job_id",
    )

    workspace_id = _required_text(
        _object_value(
            completion_job,
            "workspace_id",
        ),
        name="completion_job.workspace_id",
    )

    job_type = _required_text(
        _object_value(
            completion_job,
            "job_type",
        ),
        name="completion_job.job_type",
    )

    status = _status_text(
        _object_value(
            completion_job,
            "status",
        )
    )

    violations = []

    if (
        canonical_job_id
        != correlation.job_id
    ):
        violations.append(
            "job_id mismatch"
        )

    if (
        workspace_id
        != correlation.workspace_id
    ):
        violations.append(
            "workspace_id mismatch"
        )

    if (
        job_type
        != correlation.job_type
    ):
        violations.append(
            "job_type mismatch"
        )

    if status != "completed":
        violations.append(
            "completion job status is not completed"
        )

    if violations:
        raise RuntimeCompletionValidationError(
            (
                "Runtime completion does not match "
                "the frozen Phase 5.3 correlation."
            ),
            violations=tuple(
                violations
            ),
        )

    metadata = _mapping_copy(
        _object_value(
            completion_job,
            "metadata",
            {},
        ),
        name="completion_job.metadata",
    )

    if (
        metadata.get(
            "runtime_dispatch_completed"
        )
        is not True
    ):
        raise RuntimeCompletionValidationError(
            (
                "Runtime completion evidence does not "
                "prove successful dispatch completion."
            ),
            violations=(
                "runtime_dispatch_completed must be True",
            ),
        )

    if (
        metadata.get(
            "canonical_job_id_preserved"
        )
        is not True
    ):
        raise RuntimeCompletionValidationError(
            (
                "Runtime completion evidence does not "
                "prove canonical job identity preservation."
            ),
            violations=(
                "canonical_job_id_preserved must be True",
            ),
        )

    if (
        "runtime_dispatch_result"
        not in metadata
    ):
        raise RuntimeCompletionValidationError(
            (
                "Runtime completion evidence contains "
                "no runtime_dispatch_result."
            ),
            violations=(
                "runtime_dispatch_result is required",
            ),
        )

    output = _mapping_copy(
        metadata.get(
            "runtime_dispatch_result"
        ),
        name="runtime_dispatch_result",
    )

    normalized_events = _normalize_events(
        events
    )

    (
        started_event,
        completion_event,
    ) = _select_completion_attempt(
        canonical_job_id=
            canonical_job_id,

        events=
            normalized_events,
    )

    result_id = _required_text(
        completion_event.get(
            "event_id"
        ),
        name="completion_event.event_id",
    )

    started_at = _timestamp_text(
        started_event.get(
            "created_at"
        ),
        name="started_event.created_at",
    )

    finished_at = _timestamp_text(
        completion_event.get(
            "created_at"
        ),
        name="completion_event.created_at",
    )

    result_reference = (
        _extract_result_reference(
            output=output,
            metadata=metadata,
        )
    )

    artifact_references = (
        _extract_artifact_references(
            output=output,
            metadata=metadata,
        )
    )

    return UniversalStageResult(
        result_id=
            result_id,

        workflow_id=
            correlation.workflow_id,

        correlation_id=
            correlation.correlation_id,

        stage_id=
            correlation.stage_id,

        stage_version=
            correlation.stage_version,

        pipeline_id=
            correlation.pipeline_id,

        workflow_type=
            correlation.workflow_type,

        workspace_id=
            workspace_id,

        execution_target=
            "universal_runtime",

        job_id=
            canonical_job_id,

        job_type=
            job_type,

        status=
            UniversalStageResultStatus.COMPLETED,

        output=
            output,

        result_reference=
            result_reference,

        artifact_references=
            artifact_references,

        started_at=
            started_at,

        finished_at=
            finished_at,

        failure_code=
            "",

        failure_message=
            "",

        failure_details=
            {},

        metadata={
            "runtime_completion_intake_version":
                RUNTIME_COMPLETION_INTAKE_VERSION,

            "runtime_completion_intake_schema_version":
                RUNTIME_COMPLETION_INTAKE_SCHEMA_VERSION,

            "runtime_completion_event_id":
                result_id,

            "runtime_completion_timing_source":
                "orchestration_status_events",

            "runtime_output_source":
                "runtime_dispatch_result",

            "canonical_job_id_preserved":
                True,
        },
    )


def intake_runtime_completion(
    *,
    job_id: str,
    registry: (
        WorkflowJobCorrelationRegistry
        | None
    ) = None,
    completion_reader: Callable[
        [str],
        Any,
    ] = get_orchestration_job,
    events_reader: Callable[
        [str],
        Any,
    ] = list_job_events,
) -> UniversalStageResult:

    canonical_job_id = _required_text(
        job_id,
        name="job_id",
    )

    effective_registry = (
        registry
        if registry is not None
        else get_workflow_job_correlation_registry()
    )

    if not isinstance(
        effective_registry,
        WorkflowJobCorrelationRegistry,
    ):
        raise RuntimeCompletionValidationError(
            (
                "registry must be "
                "WorkflowJobCorrelationRegistry."
            ),
            violations=(
                "invalid correlation registry",
            ),
        )

    if not callable(
        completion_reader
    ):
        raise RuntimeCompletionValidationError(
            "completion_reader must be callable.",
            violations=(
                "completion_reader must be callable",
            ),
        )

    if not callable(
        events_reader
    ):
        raise RuntimeCompletionValidationError(
            "events_reader must be callable.",
            violations=(
                "events_reader must be callable",
            ),
        )

    correlation = (
        effective_registry.require_by_job_id(
            canonical_job_id
        )
    )

    (
        completion_job,
        events,
    ) = _resolve_job_and_events(
        job_id=
            canonical_job_id,

        completion_reader=
            completion_reader,

        events_reader=
            events_reader,
    )

    return build_runtime_completion_stage_result(
        correlation=
            correlation,

        completion_job=
            completion_job,

        events=
            events,
    )


def explain_runtime_completion_intake_v5_4(
) -> Mapping[
    str,
    Any,
]:

    return MappingProxyType(
        {
            "phase":
                "5.4",

            "component":
                "Runtime Completion Intake",

            "version":
                RUNTIME_COMPLETION_INTAKE_VERSION,

            "schema_version":
                RUNTIME_COMPLETION_INTAKE_SCHEMA_VERSION,

            "scope":
                "successful Runtime completion only",

            "coordination_identity_authority":
                "Phase 5.3 WorkflowJobCorrelation",

            "completion_status_authority":
                "canonical orchestration persisted job",

            "completion_event_authority":
                "orchestration JobStatusEvent trail",

            "result_id_authority":
                "COMPLETED JobStatusEvent.event_id",

            "started_at_authority":
                (
                    "latest RUNNING event preceding "
                    "selected COMPLETED event"
                ),

            "finished_at_authority":
                "selected COMPLETED event.created_at",

            "output_authority":
                "runtime_dispatch_result",

            "execution_target":
                "universal_runtime",

            "failure_processing_owner":
                "Phase 5.5 Runtime Failure Intake",

            "execution_properties":
                MappingProxyType(
                    {
                        "runtime_job_creation":
                            False,

                        "runtime_submission":
                            False,

                        "runtime_status_mutation":
                            False,

                        "runtime_progress_mutation":
                            False,

                        "runtime_dispatch":
                            False,

                        "handler_execution":
                            False,

                        "completion_persistence":
                            False,

                        "failure_processing":
                            False,

                        "random_result_id_generation":
                            False,

                        "wall_clock_timestamp_generation":
                            False,

                        "correlation_creation":
                            False,
                    }
                ),
        }
    )


__all__ = (
    "RUNTIME_COMPLETION_INTAKE_VERSION",
    "RUNTIME_COMPLETION_INTAKE_SCHEMA_VERSION",
    "RuntimeCompletionIntakeError",
    "RuntimeCompletionValidationError",
    "RuntimeCompletionNotReadyError",
    "build_runtime_completion_stage_result",
    "intake_runtime_completion",
    "explain_runtime_completion_intake_v5_4",
)
'''


if TARGET.exists():
    raise SystemExit(
        (
            "INSTALLATION REFUSED: "
            "runtime_completion_intake.py already exists."
        )
    )


TARGET.write_text(
    SOURCE,
    encoding="utf-8",
)


print()
print("=" * 120)
print("PHASE 5.4 — RUNTIME COMPLETION INTAKE INSTALLED")
print("=" * 120)
print(
    "Created:",
    TARGET.relative_to(ROOT),
)
print("Phase 5.3 frozen production unchanged.")
print("StageResult contract unchanged.")
print("Orchestration production unchanged.")
print("Universal Runtime Worker unchanged.")
print("Runtime production patch performed: False")
print("=" * 120)
