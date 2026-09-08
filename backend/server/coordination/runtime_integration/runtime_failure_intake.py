from __future__ import annotations

"""
LinkCraftor Universal Coordination Framework
Phase 5.5 — Runtime Failure Intake

Responsibility:
    Convert one authoritative terminal Runtime failure into one
    canonical UniversalStageResult(status=FAILED).

Canonical authorities:
    - terminal status:
        persisted orchestration job.status == failed

    - terminal event:
        RUNNING -> FAILED JobStatusEvent

    - attempt start:
        final QUEUED -> RUNNING JobStatusEvent preceding terminal event

    - coordination identity:
        frozen Phase 5.3 WorkflowJobCorrelation

    - failure code:
        persisted metadata["runtime_dispatch_error_type"]

    - failure message:
        persisted orchestration job.error_message

Retryable Runtime failures remain Runtime-owned:
    RUNNING -> QUEUED
    must NOT produce a FAILED StageResult.

This component is read-only.

It does NOT:
    - execute or dispatch Runtime handlers
    - mark jobs failed
    - requeue jobs
    - choose or recalculate retry policy
    - increment attempt counters
    - persist Runtime failure
    - mutate orchestration
    - create or submit jobs
    - generate or rewrite job_id
    - process successful completion
    - own workflow recovery or compensation
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


RUNTIME_FAILURE_INTAKE_VERSION = (
    "runtime_failure_intake_v5.5.0"
)

RUNTIME_FAILURE_INTAKE_SCHEMA_VERSION = (
    "runtime_failure_intake_schema_v1"
)


_RUNTIME_FAILURE_DETAIL_KEYS = (
    "runtime_dispatch_completed",
    "runtime_dispatch_failed",
    "runtime_retry_scheduled",
    "runtime_failure_attempt_count",
    "runtime_maximum_attempts",
    "runtime_retry_type_allowed",
    "runtime_retry_exhausted",
    "runtime_contract_error",
    "runtime_dispatch_error_type",
    "canonical_job_id_preserved",
    "retry_created_new_job",
    "runtime_worker_version",
)


class RuntimeFailureIntakeError(
    ValueError
):
    pass


class RuntimeFailureValidationError(
    RuntimeFailureIntakeError
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


class RuntimeFailureNotReadyError(
    RuntimeFailureValidationError
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
        raise RuntimeFailureValidationError(
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

    raise RuntimeFailureValidationError(
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
        raise RuntimeFailureValidationError(
            f"{name} is required.",
            violations=(
                f"{name} is required",
            ),
        )

    return normalized


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
        raise RuntimeFailureValidationError(
            "failure events must be a sequence.",
            violations=(
                "failure events must be a sequence",
            ),
        )

    if not isinstance(
        events,
        Sequence,
    ):
        raise RuntimeFailureValidationError(
            "failure events must be a sequence.",
            violations=(
                "failure events must be a sequence",
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
    failure_reader: Callable[
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

    failure_document = failure_reader(
        job_id
    )

    if failure_document is None:
        raise RuntimeFailureNotReadyError(
            "No orchestration failure record exists for job_id.",
            violations=(
                "failure job does not exist",
            ),
        )

    job = failure_document
    embedded_events = None

    if isinstance(
        failure_document,
        Mapping,
    ):
        if "job" in failure_document:
            job = failure_document[
                "job"
            ]

        embedded_events = failure_document.get(
            "events"
        )

    if job is None:
        raise RuntimeFailureNotReadyError(
            "Failure document contains no orchestration job.",
            violations=(
                "failure job is missing",
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


def _select_terminal_failure_attempt(
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

    failed_index = None

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
            name=f"events[{index}].job_id",
        )

        if event_job_id != canonical_job_id:
            raise RuntimeFailureValidationError(
                "Failure event trail contains a foreign job_id.",
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
            == "failed"
        ):
            if (
                _status_text(
                    event.get(
                        "old_status"
                    )
                )
                != "running"
            ):
                raise RuntimeFailureValidationError(
                    (
                        "Selected FAILED event must represent "
                        "RUNNING -> FAILED."
                    ),
                    violations=(
                        "failure transition must be running -> failed",
                    ),
                )

            failed_index = index
            break

    if failed_index is None:
        raise RuntimeFailureNotReadyError(
            "No terminal FAILED event exists for job_id.",
            violations=(
                "failed event is missing",
            ),
        )

    running_index = None

    for index in range(
        failed_index - 1,
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
            name=f"events[{index}].job_id",
        )

        if event_job_id != canonical_job_id:
            raise RuntimeFailureValidationError(
                "Runtime attempt event contains a foreign job_id.",
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
            if (
                _status_text(
                    event.get(
                        "old_status"
                    )
                )
                != "queued"
            ):
                raise RuntimeFailureValidationError(
                    (
                        "Selected RUNNING event must represent "
                        "QUEUED -> RUNNING."
                    ),
                    violations=(
                        "started transition must be queued -> running",
                    ),
                )

            running_index = index
            break

    if running_index is None:
        raise RuntimeFailureValidationError(
            (
                "No QUEUED -> RUNNING event precedes "
                "the selected FAILED event."
            ),
            violations=(
                "started event is missing",
            ),
        )

    return (
        events[
            running_index
        ],
        events[
            failed_index
        ],
    )


def _extract_failure_details(
    metadata: Mapping[
        str,
        Any,
    ],
) -> dict[str, Any]:

    return {
        key:
            deepcopy(
                metadata[
                    key
                ]
            )
        for key
        in _RUNTIME_FAILURE_DETAIL_KEYS
        if key in metadata
    }


def build_runtime_failure_stage_result(
    *,
    correlation: WorkflowJobCorrelation,
    failure_job: Any,
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
        raise RuntimeFailureValidationError(
            (
                "correlation must be "
                "WorkflowJobCorrelation."
            ),
            violations=(
                "Phase 5.5 requires frozen Phase 5.3 correlation",
            ),
        )

    canonical_job_id = _required_text(
        _object_value(
            failure_job,
            "job_id",
        ),
        name="failure_job.job_id",
    )

    workspace_id = _required_text(
        _object_value(
            failure_job,
            "workspace_id",
        ),
        name="failure_job.workspace_id",
    )

    job_type = _required_text(
        _object_value(
            failure_job,
            "job_type",
        ),
        name="failure_job.job_type",
    )

    status = _status_text(
        _object_value(
            failure_job,
            "status",
        )
    )

    violations = []

    if canonical_job_id != correlation.job_id:
        violations.append(
            "job_id mismatch"
        )

    if workspace_id != correlation.workspace_id:
        violations.append(
            "workspace_id mismatch"
        )

    if job_type != correlation.job_type:
        violations.append(
            "job_type mismatch"
        )

    if status != "failed":
        violations.append(
            "failure job status is not failed"
        )

    if violations:
        raise RuntimeFailureValidationError(
            (
                "Runtime failure does not match "
                "the frozen Phase 5.3 correlation."
            ),
            violations=tuple(
                violations
            ),
        )

    metadata = _mapping_copy(
        _object_value(
            failure_job,
            "metadata",
            {},
        ),
        name="failure_job.metadata",
    )

    if (
        metadata.get(
            "runtime_dispatch_failed"
        )
        is not True
    ):
        raise RuntimeFailureValidationError(
            (
                "Runtime failure evidence does not prove "
                "dispatch failure."
            ),
            violations=(
                "runtime_dispatch_failed must be True",
            ),
        )

    if (
        metadata.get(
            "runtime_dispatch_completed"
        )
        is not False
    ):
        raise RuntimeFailureValidationError(
            (
                "Runtime failure evidence must prove "
                "dispatch was not completed."
            ),
            violations=(
                "runtime_dispatch_completed must be False",
            ),
        )

    if (
        metadata.get(
            "runtime_retry_scheduled"
        )
        is not False
    ):
        raise RuntimeFailureNotReadyError(
            (
                "Runtime failure is not terminal because "
                "retry is scheduled or terminal proof is absent."
            ),
            violations=(
                "runtime_retry_scheduled must be False",
            ),
        )

    if (
        metadata.get(
            "canonical_job_id_preserved"
        )
        is not True
    ):
        raise RuntimeFailureValidationError(
            (
                "Runtime failure evidence does not prove "
                "canonical job identity preservation."
            ),
            violations=(
                "canonical_job_id_preserved must be True",
            ),
        )

    if (
        metadata.get(
            "retry_created_new_job"
        )
        is not False
    ):
        raise RuntimeFailureValidationError(
            (
                "Runtime failure evidence does not prove "
                "same-job retry/failure semantics."
            ),
            violations=(
                "retry_created_new_job must be False",
            ),
        )

    missing_failure_detail_keys = tuple(
        key
        for key
        in _RUNTIME_FAILURE_DETAIL_KEYS
        if key not in metadata
    )

    if missing_failure_detail_keys:
        raise RuntimeFailureValidationError(
            (
                "Runtime terminal failure evidence is incomplete."
            ),
            violations=tuple(
                (
                    "missing canonical Runtime failure detail: "
                    + key
                )
                for key
                in missing_failure_detail_keys
            ),
        )

    failure_code = _required_text(
        metadata.get(
            "runtime_dispatch_error_type"
        ),
        name=(
            "metadata.runtime_dispatch_error_type"
        ),
    )

    failure_message = _required_text(
        _object_value(
            failure_job,
            "error_message",
        ),
        name="failure_job.error_message",
    )

    normalized_events = _normalize_events(
        events
    )

    (
        started_event,
        failed_event,
    ) = _select_terminal_failure_attempt(
        canonical_job_id=
            canonical_job_id,

        events=
            normalized_events,
    )

    result_id = _required_text(
        failed_event.get(
            "event_id"
        ),
        name="failed_event.event_id",
    )

    started_at = _timestamp_text(
        started_event.get(
            "created_at"
        ),
        name="started_event.created_at",
    )

    finished_at = _timestamp_text(
        failed_event.get(
            "created_at"
        ),
        name="failed_event.created_at",
    )

    try:
        started_dt = datetime.fromisoformat(
            started_at.replace(
                "Z",
                "+00:00",
            )
        )

        finished_dt = datetime.fromisoformat(
            finished_at.replace(
                "Z",
                "+00:00",
            )
        )

    except ValueError as exc:
        raise RuntimeFailureValidationError(
            "Runtime failure event timestamp is invalid.",
            violations=(
                "invalid Runtime failure timestamp",
            ),
        ) from exc

    if (
        started_dt.tzinfo is not None
        and finished_dt.tzinfo is not None
        and finished_dt < started_dt
    ):
        raise RuntimeFailureValidationError(
            "Runtime failure timestamp ordering is invalid.",
            violations=(
                "finished_at cannot be earlier than started_at",
            ),
        )

    failure_details = _extract_failure_details(
        metadata
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
            UniversalStageResultStatus.FAILED,

        output=
            {},

        result_reference=
            "",

        artifact_references=
            (),

        started_at=
            started_at,

        finished_at=
            finished_at,

        failure_code=
            failure_code,

        failure_message=
            failure_message,

        failure_details=
            failure_details,

        metadata={
            "runtime_failure_intake_version":
                RUNTIME_FAILURE_INTAKE_VERSION,

            "runtime_failure_intake_schema_version":
                RUNTIME_FAILURE_INTAKE_SCHEMA_VERSION,

            "runtime_failure_event_id":
                result_id,

            "runtime_failure_timing_source":
                "orchestration_status_events",

            "runtime_failure_source":
                "persisted_orchestration_failure",

            "canonical_job_id_preserved":
                True,
        },
    )


def intake_runtime_failure(
    *,
    job_id: str,
    registry: (
        WorkflowJobCorrelationRegistry
        | None
    ) = None,
    failure_reader: Callable[
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
        raise RuntimeFailureValidationError(
            (
                "registry must be "
                "WorkflowJobCorrelationRegistry."
            ),
            violations=(
                "invalid correlation registry",
            ),
        )

    if not callable(
        failure_reader
    ):
        raise RuntimeFailureValidationError(
            "failure_reader must be callable.",
            violations=(
                "failure_reader must be callable",
            ),
        )

    if not callable(
        events_reader
    ):
        raise RuntimeFailureValidationError(
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
        failure_job,
        events,
    ) = _resolve_job_and_events(
        job_id=
            canonical_job_id,

        failure_reader=
            failure_reader,

        events_reader=
            events_reader,
    )

    return build_runtime_failure_stage_result(
        correlation=
            correlation,

        failure_job=
            failure_job,

        events=
            events,
    )


def explain_runtime_failure_intake_v5_5(
) -> Mapping[
    str,
    Any,
]:

    return MappingProxyType(
        {
            "phase":
                "5.5",

            "component":
                "Runtime Failure Intake",

            "version":
                RUNTIME_FAILURE_INTAKE_VERSION,

            "schema_version":
                RUNTIME_FAILURE_INTAKE_SCHEMA_VERSION,

            "scope":
                "terminal Runtime failure only",

            "coordination_identity_authority":
                "Phase 5.3 WorkflowJobCorrelation",

            "terminal_status_authority":
                "canonical orchestration persisted job",

            "terminal_event_authority":
                "RUNNING -> FAILED JobStatusEvent",

            "attempt_start_authority":
                "QUEUED -> RUNNING JobStatusEvent",

            "result_id_authority":
                "FAILED JobStatusEvent.event_id",

            "failure_code_authority":
                "runtime_dispatch_error_type",

            "failure_message_authority":
                "persisted orchestration job.error_message",

            "retryable_failure_behavior":
                "RUNNING -> QUEUED remains Runtime-owned",

            "execution_target":
                "universal_runtime",

            "workflow_recovery_owner":
                "Phase 9 Coordination Recovery",

            "execution_properties":
                MappingProxyType(
                    {
                        "runtime_job_creation":
                            False,

                        "runtime_submission":
                            False,

                        "runtime_status_mutation":
                            False,

                        "runtime_requeue":
                            False,

                        "retry_policy_decision":
                            False,

                        "attempt_count_mutation":
                            False,

                        "runtime_dispatch":
                            False,

                        "handler_execution":
                            False,

                        "failure_persistence":
                            False,

                        "success_processing":
                            False,

                        "workflow_recovery":
                            False,

                        "workflow_compensation":
                            False,

                        "correlation_creation":
                            False,
                    }
                ),
        }
    )


__all__ = (
    "RUNTIME_FAILURE_INTAKE_VERSION",
    "RUNTIME_FAILURE_INTAKE_SCHEMA_VERSION",
    "RuntimeFailureIntakeError",
    "RuntimeFailureValidationError",
    "RuntimeFailureNotReadyError",
    "build_runtime_failure_stage_result",
    "intake_runtime_failure",
    "explain_runtime_failure_intake_v5_5",
)
