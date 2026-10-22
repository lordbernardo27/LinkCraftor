"""Canonical Universal Coordination to Universal Runtime submission gateway."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, fields, is_dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any

from backend.server.coordination.runtime_integration.runtime_job_mapping import (
    RuntimeJobMapping,
)
from backend.server.coordination.runtime_integration.workflow_job_correlation import (
    WorkflowJobCorrelation,
    WorkflowJobCorrelationRegistry,
    correlate_submitted_job,
    get_workflow_job_correlation_registry,
)
from backend.server.runtime.universal_job_submission import (
    submit_universal_job,
)
from backend.server.runtime.universal_jobs.creation_engine import (
    UniversalJobCreationRequest,
)
from backend.server.runtime.universal_runtime_registration import (
    ensure_persisted_runtime_registrations_loaded,
    get_runtime_registration,
)


RUNTIME_EXECUTION_GATEWAY_CONTRACT_VERSION = (
    "runtime_execution_gateway_contract_v1"
)
RUNTIME_EXECUTION_GATEWAY_VERSION = (
    "runtime_execution_gateway_v1.0.0"
)


class RuntimeExecutionGatewayError(RuntimeError):
    """Fail-closed gateway contract violation."""

    def __init__(
        self,
        message: str,
        *,
        code: str,
        violations: tuple[str, ...] = (),
    ) -> None:
        super().__init__(message)

        self.code = (
            str(code).strip()
            or "runtime_execution_gateway_error"
        )

        self.violations = tuple(
            str(value)
            for value in violations
        )


def _plain(value: Any) -> Any:
    if (
        is_dataclass(value)
        and not isinstance(value, type)
    ):
        return {
            item.name: _plain(
                getattr(
                    value,
                    item.name,
                )
            )
            for item in fields(value)
        }

    if isinstance(value, Mapping):
        return {
            str(key): _plain(item)
            for key, item in value.items()
        }

    if isinstance(
        value,
        (
            tuple,
            list,
            set,
            frozenset,
        ),
    ):
        return [
            _plain(item)
            for item in value
        ]

    if isinstance(value, Enum):
        return _plain(value.value)

    return value


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType(
            {
                str(key): _freeze(item)
                for key, item in value.items()
            }
        )

    if isinstance(
        value,
        (
            tuple,
            list,
            set,
            frozenset,
        ),
    ):
        return tuple(
            _freeze(item)
            for item in value
        )

    return value


def _text(value: Any) -> str:
    return str(
        value or ""
    ).strip()


def _registration_value(
    registration: Mapping[str, Any],
    name: str,
) -> str:
    return _text(
        registration.get(name)
    )


@dataclass(
    frozen=True,
    slots=True,
)
class RuntimeExecutionGatewayResult:
    contract_version: str
    submission_outcome: str
    created: bool
    reused_existing_job: bool
    queued: bool
    job_id: str
    job_type: str
    workflow_id: str
    workspace_id: str
    correlation_id: str
    stage_id: str
    runtime_stage: str
    dependency_job_ids: tuple[str, ...]
    idempotency_key: str | None
    mapping: RuntimeJobMapping
    submitted_job: Mapping[str, Any]
    correlation: WorkflowJobCorrelation
    evidence: Mapping[str, Any]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "dependency_job_ids",
            tuple(
                _text(value)
                for value in self.dependency_job_ids
                if _text(value)
            ),
        )

        object.__setattr__(
            self,
            "submitted_job",
            _freeze(
                self.submitted_job
            ),
        )

        object.__setattr__(
            self,
            "evidence",
            _freeze(
                self.evidence
            ),
        )

        required_values = {
            "contract_version": (
                self.contract_version
            ),
            "submission_outcome": (
                self.submission_outcome
            ),
            "job_id": self.job_id,
            "job_type": self.job_type,
            "workflow_id": self.workflow_id,
            "workspace_id": self.workspace_id,
            "correlation_id": (
                self.correlation_id
            ),
            "stage_id": self.stage_id,
            "runtime_stage": (
                self.runtime_stage
            ),
        }

        missing = tuple(
            name
            for name, value
            in required_values.items()
            if not _text(value)
        )

        if missing:
            raise RuntimeExecutionGatewayError(
                (
                    "Runtime gateway result is missing "
                    "required identity evidence."
                ),
                code="invalid_gateway_result",
                violations=missing,
            )

        if self.submission_outcome not in {
            "created",
            "reused",
        }:
            raise RuntimeExecutionGatewayError(
                (
                    "Runtime gateway result has an "
                    "invalid submission outcome."
                ),
                code="invalid_gateway_result",
                violations=(
                    "submission_outcome",
                ),
            )

        if (
            self.created
            == self.reused_existing_job
        ):
            raise RuntimeExecutionGatewayError(
                (
                    "Exactly one submission outcome "
                    "flag must be true."
                ),
                code="invalid_gateway_result",
                violations=(
                    "created",
                    "reused_existing_job",
                ),
            )

        if not self.queued:
            raise RuntimeExecutionGatewayError(
                (
                    "A successful runtime gateway "
                    "result must be queued."
                ),
                code="invalid_gateway_result",
                violations=("queued",),
            )

    def to_dict(self) -> dict[str, Any]:
        return _plain(self)


def _validate_mapping(
    mapping: RuntimeJobMapping,
) -> UniversalJobCreationRequest:
    if not isinstance(
        mapping,
        RuntimeJobMapping,
    ):
        raise RuntimeExecutionGatewayError(
            "mapping must be RuntimeJobMapping.",
            code="invalid_mapping",
            violations=("mapping",),
        )

    request = mapping.creation_request

    if not isinstance(
        request,
        UniversalJobCreationRequest,
    ):
        raise RuntimeExecutionGatewayError(
            (
                "mapping.creation_request must be "
                "UniversalJobCreationRequest."
            ),
            code="invalid_mapping",
            violations=(
                "creation_request",
            ),
        )

    required = {
        "workflow_id": mapping.workflow_id,
        "correlation_id": (
            mapping.correlation_id
        ),
        "stage_id": mapping.stage_id,
        "workspace_id": (
            request.workspace_id
        ),
        "job_type": request.job_type,
        "pipeline": request.pipeline,
        "stage": request.stage,
    }

    missing = tuple(
        name
        for name, value
        in required.items()
        if not _text(value)
    )

    if missing:
        raise RuntimeExecutionGatewayError(
            "Runtime job mapping is incomplete.",
            code="invalid_mapping",
            violations=missing,
        )

    if request.enqueue is not True:
        raise RuntimeExecutionGatewayError(
            (
                "Runtime execution gateway "
                "requires enqueue=True."
            ),
            code="invalid_mapping",
            violations=("enqueue",),
        )

    return request


def _resolve_registration(
    request: UniversalJobCreationRequest,
) -> Mapping[str, Any]:
    ensure_persisted_runtime_registrations_loaded()

    registration = get_runtime_registration(
        _text(
            request.job_type
        )
    )

    if not isinstance(
        registration,
        Mapping,
    ):
        raise RuntimeExecutionGatewayError(
            (
                "No runtime registration exists for "
                f"{request.job_type!r}."
            ),
            code="missing_runtime_registration",
            violations=("job_type",),
        )

    mismatches: list[str] = []

    expected = {
        "job_type": _text(
            request.job_type
        ),
        "pipeline": _text(
            request.pipeline
        ),
        "stage": _text(
            request.stage
        ),
    }

    for name, value in expected.items():
        registered_value = (
            _registration_value(
                registration,
                name,
            )
        )

        if (
            value
            and registered_value != value
        ):
            mismatches.append(name)

    if mismatches:
        raise RuntimeExecutionGatewayError(
            (
                "Runtime registration does not "
                "match the mapped request."
            ),
            code="registration_mismatch",
            violations=tuple(mismatches),
        )

    return registration


def _submitter_arguments(
    request: UniversalJobCreationRequest,
    registration: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "workspace_id": request.workspace_id,
        "job_type": request.job_type,
        "payload": request.payload,
        "metadata": request.metadata,
        "user_id": request.user_id,
        "product_id": request.product_id,
        "pipeline": request.pipeline,
        "stage": request.stage,
        "payload_reference": (
            request.payload_reference
        ),
        "priority": request.priority,
        "parent_job_id": (
            request.parent_job_id
        ),
        "dependency_job_ids": (
            request.dependency_job_ids
        ),
        "batch_id": request.batch_id,
        "pipeline_run_id": (
            request.pipeline_run_id
        ),
        "idempotency_key": (
            request.idempotency_key
        ),
        "maximum_attempts": (
            request.maximum_attempts
        ),
        "job_id": request.job_id,
        "created_at": request.created_at,
        "scheduled_at": (
            request.scheduled_at
        ),
        "supported_job_types": (
            request.job_type,
        ),
        "runtime_registration": (
            registration
        ),
        "enqueue": True,
    }


def _submission_flags(
    submitted_job: Mapping[str, Any],
) -> tuple[
    bool,
    bool,
    bool,
    str,
]:
    submission = submitted_job.get(
        "submission"
    )

    submission = (
        submission
        if isinstance(
            submission,
            Mapping,
        )
        else {}
    )

    reused = bool(
        submitted_job.get(
            "reused_existing_job"
        )
        or submitted_job.get(
            "reused"
        )
        or submission.get(
            "reused_existing_job"
        )
        or submission.get(
            "reused"
        )
    )

    created_marker = (
        submitted_job.get(
            "created"
        )
    )

    if created_marker is None:
        created_marker = submission.get(
            "created"
        )

    created = (
        bool(created_marker)
        if created_marker is not None
        else not reused
    )

    queued = bool(
        submission.get(
            "queued"
        )
        or submitted_job.get(
            "queued"
        )
        or _text(
            submitted_job.get(
                "status"
            )
        ).lower()
        == "queued"
    )

    outcome = (
        "reused"
        if reused
        else "created"
    )

    return (
        created,
        reused,
        queued,
        outcome,
    )


def _validate_submitted_identity(
    *,
    request: UniversalJobCreationRequest,
    submitted_job: Mapping[str, Any],
) -> str:
    job_id = _text(
        submitted_job.get(
            "job_id"
        )
        or submitted_job.get(
            "id"
        )
    )

    if not job_id:
        raise RuntimeExecutionGatewayError(
            (
                "Universal Job submission "
                "returned no job_id."
            ),
            code="job_submission_failure",
            violations=("job_id",),
        )

    mismatches: list[str] = []

    comparisons = {
        "job_type": (
            _text(
                request.job_type
            ),
            _text(
                submitted_job.get(
                    "job_type"
                )
            ),
        ),
        "workspace_id": (
            _text(
                request.workspace_id
            ),
            _text(
                submitted_job.get(
                    "workspace_id"
                )
            ),
        ),
        "pipeline": (
            _text(
                request.pipeline
            ),
            _text(
                submitted_job.get(
                    "pipeline"
                )
            ),
        ),
        "stage": (
            _text(
                request.stage
            ),
            _text(
                submitted_job.get(
                    "stage"
                )
            ),
        ),
    }

    for name, (
        expected,
        actual,
    ) in comparisons.items():
        if expected != actual:
            mismatches.append(name)

    if mismatches:
        raise RuntimeExecutionGatewayError(
            (
                "Submitted Universal Job identity "
                "differs from its mapping."
            ),
            code="job_submission_failure",
            violations=tuple(mismatches),
        )

    return job_id


def submit_runtime_job_mapping(
    *,
    mapping: RuntimeJobMapping,
    submitter: Callable[
        ...,
        Mapping[str, Any],
    ] = submit_universal_job,
    correlation_registry: (
        WorkflowJobCorrelationRegistry
        | None
    ) = None,
) -> RuntimeExecutionGatewayResult:
    """
    Submit one mapped registered stage and
    correlate its canonical job identity.
    """

    request = _validate_mapping(
        mapping
    )

    registration = (
        _resolve_registration(
            request
        )
    )

    if not callable(submitter):
        raise RuntimeExecutionGatewayError(
            "submitter must be callable.",
            code="job_submission_failure",
            violations=("submitter",),
        )

    submitted_job = submitter(
        **_submitter_arguments(
            request,
            registration,
        )
    )

    if not isinstance(
        submitted_job,
        Mapping,
    ):
        raise RuntimeExecutionGatewayError(
            (
                "Universal Job submitter "
                "must return a mapping."
            ),
            code="job_submission_failure",
            violations=(
                "submitted_job",
            ),
        )

    job_id = (
        _validate_submitted_identity(
            request=request,
            submitted_job=submitted_job,
        )
    )

    (
        created,
        reused,
        queued,
        outcome,
    ) = _submission_flags(
        submitted_job
    )

    if (
        created == reused
        or not queued
    ):
        raise RuntimeExecutionGatewayError(
            (
                "Universal Job submission did not "
                "provide a valid queued outcome."
            ),
            code="job_submission_failure",
            violations=(
                "created",
                "reused_existing_job",
                "queued",
            ),
        )

    effective_registry = (
        correlation_registry
        if correlation_registry is not None
        else (
            get_workflow_job_correlation_registry()
        )
    )

    if not isinstance(
        effective_registry,
        WorkflowJobCorrelationRegistry,
    ):
        raise RuntimeExecutionGatewayError(
            (
                "correlation_registry must be "
                "WorkflowJobCorrelationRegistry."
            ),
            code="correlation_failure",
            violations=(
                "correlation_registry",
            ),
        )

    correlation = correlate_submitted_job(
        mapping=mapping,
        submitted_job=submitted_job,
        registry=effective_registry,
    )

    registration_fingerprint = _text(
        registration.get(
            "registration_fingerprint"
        )
    )

    evidence = {
        "gateway_version": (
            RUNTIME_EXECUTION_GATEWAY_VERSION
        ),
        "mapping_version": (
            mapping.mapping_version
        ),
        "registration_fingerprint": (
            registration_fingerprint
        ),
        "registration_resolved": True,
        "canonical_submitter": (
            "submit_universal_job"
        ),
        "correlation_registered": True,
        "handler_dispatched": False,
    }

    return RuntimeExecutionGatewayResult(
        contract_version=(
            RUNTIME_EXECUTION_GATEWAY_CONTRACT_VERSION
        ),
        submission_outcome=outcome,
        created=created,
        reused_existing_job=reused,
        queued=queued,
        job_id=job_id,
        job_type=_text(
            request.job_type
        ),
        workflow_id=_text(
            mapping.workflow_id
        ),
        workspace_id=_text(
            request.workspace_id
        ),
        correlation_id=_text(
            mapping.correlation_id
        ),
        stage_id=_text(
            mapping.stage_id
        ),
        runtime_stage=_text(
            request.stage
        ),
        dependency_job_ids=tuple(
            request.dependency_job_ids
        ),
        idempotency_key=(
            _text(
                request.idempotency_key
            )
            if request.idempotency_key
            else None
        ),
        mapping=mapping,
        submitted_job=submitted_job,
        correlation=correlation,
        evidence=evidence,
    )


def explain_runtime_execution_gateway_v1(
) -> dict[str, Any]:
    return {
        "component": (
            "Universal Coordination "
            "Runtime Execution Gateway"
        ),
        "version": (
            RUNTIME_EXECUTION_GATEWAY_VERSION
        ),
        "contract_version": (
            RUNTIME_EXECUTION_GATEWAY_CONTRACT_VERSION
        ),
        "canonical_request": (
            "RuntimeJobMapping"
        ),
        "canonical_submitter": (
            "submit_universal_job"
        ),
        "canonical_correlation": (
            "correlate_submitted_job"
        ),
        "direct_handler_dispatch": False,
    }


__all__ = [
    (
        "RUNTIME_EXECUTION_GATEWAY_"
        "CONTRACT_VERSION"
    ),
    "RUNTIME_EXECUTION_GATEWAY_VERSION",
    "RuntimeExecutionGatewayError",
    "RuntimeExecutionGatewayResult",
    "submit_runtime_job_mapping",
    "explain_runtime_execution_gateway_v1",
]

# === PART C 8-D EXECUTION WAVE GATEWAY START ===
from dataclasses import dataclass as _wave_dataclass
from dataclasses import replace as _wave_replace
from types import MappingProxyType as _WaveMappingProxyType

from backend.server.coordination.runtime_integration.runtime_job_mapping import (
    RuntimeJobMappingResult,
)


RUNTIME_EXECUTION_WAVE_GATEWAY_VERSION = (
    "runtime_execution_wave_gateway_v1.0.0"
)
RUNTIME_EXECUTION_WAVE_GATEWAY_CONTRACT_VERSION = (
    "runtime_execution_wave_gateway_contract_v1"
)


def _freeze_wave_value(
    value: Any,
) -> Any:
    if isinstance(value, Mapping):
        return _WaveMappingProxyType(
            {
                str(key): _freeze_wave_value(item)
                for key, item in value.items()
            }
        )

    if isinstance(value, (tuple, list)):
        return tuple(
            _freeze_wave_value(item)
            for item in value
        )

    if isinstance(value, (set, frozenset)):
        return tuple(
            sorted(
                _freeze_wave_value(item)
                for item in value
            )
        )

    return value


def _plain_wave_value(
    value: Any,
) -> Any:
    if isinstance(value, Mapping):
        return {
            str(key): _plain_wave_value(item)
            for key, item in value.items()
        }

    if isinstance(value, (tuple, list)):
        return [
            _plain_wave_value(item)
            for item in value
        ]

    to_dict = getattr(
        value,
        "to_dict",
        None,
    )

    if callable(to_dict):
        return _plain_wave_value(
            to_dict()
        )

    return value


class RuntimeExecutionWaveGatewayError(
    RuntimeExecutionGatewayError,
):
    """Fail-closed aggregate submission error with partial evidence."""

    def __init__(
        self,
        message: str,
        *,
        code: str,
        violations: tuple[str, ...] = (),
        workflow_id: str = "",
        wave_index: int | None = None,
        failed_stage_id: str | None = None,
        submitted_results: tuple[
            RuntimeExecutionGatewayResult,
            ...,
        ] = (),
    ) -> None:
        super().__init__(
            message,
            code=code,
            violations=violations,
        )

        self.workflow_id = str(
            workflow_id
            or ""
        ).strip()
        self.wave_index = wave_index
        self.failed_stage_id = (
            str(failed_stage_id).strip()
            if failed_stage_id
            else None
        )
        self.submitted_results = tuple(
            submitted_results
        )
        self.submitted_job_ids = tuple(
            result.job_id
            for result in self.submitted_results
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "message": str(self),
            "code": self.code,
            "violations": list(
                self.violations
            ),
            "workflow_id": self.workflow_id,
            "wave_index": self.wave_index,
            "failed_stage_id": (
                self.failed_stage_id
            ),
            "submitted_count": len(
                self.submitted_results
            ),
            "submitted_job_ids": list(
                self.submitted_job_ids
            ),
            "submitted_results": [
                result.to_dict()
                for result
                in self.submitted_results
            ],
        }


@_wave_dataclass(
    frozen=True,
    slots=True,
)
class RuntimeExecutionWaveGatewayResult:
    contract_version: str
    gateway_version: str
    workflow_id: str
    wave_index: int
    execution_semantics: str
    stage_ids: tuple[str, ...]
    submission_count: int
    created_count: int
    reused_existing_count: int
    queued_count: int
    job_ids: tuple[str, ...]
    dependency_job_ids_by_stage: Mapping[
        str,
        tuple[str, ...],
    ]
    mappings: tuple[
        RuntimeJobMapping,
        ...,
    ]
    submissions: tuple[
        RuntimeExecutionGatewayResult,
        ...,
    ]
    evidence: Mapping[str, Any]

    def __post_init__(
        self,
    ) -> None:
        object.__setattr__(
            self,
            "stage_ids",
            tuple(self.stage_ids),
        )
        object.__setattr__(
            self,
            "job_ids",
            tuple(self.job_ids),
        )
        object.__setattr__(
            self,
            "mappings",
            tuple(self.mappings),
        )
        object.__setattr__(
            self,
            "submissions",
            tuple(self.submissions),
        )
        object.__setattr__(
            self,
            "dependency_job_ids_by_stage",
            _freeze_wave_value(
                self.dependency_job_ids_by_stage
            ),
        )
        object.__setattr__(
            self,
            "evidence",
            _freeze_wave_value(
                self.evidence
            ),
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "contract_version": (
                self.contract_version
            ),
            "gateway_version": (
                self.gateway_version
            ),
            "workflow_id": self.workflow_id,
            "wave_index": self.wave_index,
            "execution_semantics": (
                self.execution_semantics
            ),
            "stage_ids": list(
                self.stage_ids
            ),
            "submission_count": (
                self.submission_count
            ),
            "created_count": (
                self.created_count
            ),
            "reused_existing_count": (
                self.reused_existing_count
            ),
            "queued_count": (
                self.queued_count
            ),
            "job_ids": list(
                self.job_ids
            ),
            "dependency_job_ids_by_stage": (
                _plain_wave_value(
                    self.dependency_job_ids_by_stage
                )
            ),
            "mappings": [
                _plain_wave_value(mapping)
                for mapping in self.mappings
            ],
            "submissions": [
                submission.to_dict()
                for submission
                in self.submissions
            ],
            "evidence": _plain_wave_value(
                self.evidence
            ),
        }


def _wave_error(
    message: str,
    *,
    code: str,
    violations: tuple[str, ...],
    workflow_id: str = "",
    wave_index: int | None = None,
    failed_stage_id: str | None = None,
    submitted_results: tuple[
        RuntimeExecutionGatewayResult,
        ...,
    ] = (),
) -> RuntimeExecutionWaveGatewayError:
    return RuntimeExecutionWaveGatewayError(
        message,
        code=code,
        violations=violations,
        workflow_id=workflow_id,
        wave_index=wave_index,
        failed_stage_id=failed_stage_id,
        submitted_results=submitted_results,
    )


def _normalize_wave_dependencies(
    value: Mapping[
        str,
        Any,
    ] | None,
    *,
    stage_ids: tuple[str, ...],
) -> dict[str, tuple[str, ...]]:
    if value is None:
        return {}

    if not isinstance(value, Mapping):
        raise _wave_error(
            (
                "dependency_job_ids_by_stage "
                "must be a mapping."
            ),
            code="invalid_wave_dependencies",
            violations=(
                "dependency_job_ids_by_stage",
            ),
        )

    normalized: dict[
        str,
        tuple[str, ...],
    ] = {}

    allowed = set(stage_ids)

    for raw_stage_id, raw_ids in value.items():
        stage_id = str(
            raw_stage_id
            or ""
        ).strip()

        if not stage_id or stage_id not in allowed:
            raise _wave_error(
                (
                    "Dependency override references "
                    "an unknown wave stage."
                ),
                code="invalid_wave_dependencies",
                violations=(
                    f"unknown stage_id: {stage_id!r}",
                ),
            )

        if (
            isinstance(
                raw_ids,
                (str, bytes),
            )
            or not isinstance(
                raw_ids,
                (tuple, list),
            )
        ):
            raise _wave_error(
                (
                    "Stage dependency IDs must be "
                    "a tuple or list."
                ),
                code="invalid_wave_dependencies",
                violations=(stage_id,),
            )

        dependency_ids = tuple(
            str(item or "").strip()
            for item in raw_ids
        )

        if any(
            not item
            for item in dependency_ids
        ):
            raise _wave_error(
                "Dependency job IDs must be non-empty.",
                code="invalid_wave_dependencies",
                violations=(stage_id,),
            )

        if len(set(dependency_ids)) != len(
            dependency_ids
        ):
            raise _wave_error(
                "Dependency job IDs must be unique.",
                code="invalid_wave_dependencies",
                violations=(stage_id,),
            )

        normalized[stage_id] = (
            dependency_ids
        )

    return normalized


def _preflight_execution_wave(
    *,
    mapping_result: RuntimeJobMappingResult,
    dependency_job_ids_by_stage: Mapping[
        str,
        Any,
    ] | None,
    execution_semantics: str,
    submitter: Callable[
        ...,
        Mapping[str, Any],
    ],
    correlation_registry: (
        WorkflowJobCorrelationRegistry
        | None
    ),
) -> tuple[
    str,
    int,
    str,
    tuple[str, ...],
    tuple[RuntimeJobMapping, ...],
    dict[str, tuple[str, ...]],
    WorkflowJobCorrelationRegistry,
]:
    if not isinstance(
        mapping_result,
        RuntimeJobMappingResult,
    ):
        raise _wave_error(
            (
                "mapping_result must be "
                "RuntimeJobMappingResult."
            ),
            code="invalid_wave_mapping",
            violations=("mapping_result",),
        )

    workflow_id = str(
        mapping_result.workflow_id
        or ""
    ).strip()

    mappings = tuple(
        mapping_result.mappings
    )
    stage_ids = tuple(
        str(item or "").strip()
        for item
        in mapping_result.stage_ids
    )

    if not workflow_id:
        raise _wave_error(
            "Wave workflow_id is required.",
            code="invalid_wave_mapping",
            violations=("workflow_id",),
        )

    if not mappings:
        raise _wave_error(
            (
                "An execution wave must contain "
                "at least one mapping."
            ),
            code="empty_execution_wave",
            violations=("mappings",),
            workflow_id=workflow_id,
        )

    if (
        mapping_result.mapping_count
        != len(mappings)
        or len(stage_ids) != len(mappings)
    ):
        raise _wave_error(
            "Wave mapping counts are inconsistent.",
            code="invalid_wave_mapping",
            violations=(
                "mapping_count",
                "stage_ids",
            ),
            workflow_id=workflow_id,
        )

    actual_stage_ids = tuple(
        str(mapping.stage_id or "").strip()
        if isinstance(mapping, RuntimeJobMapping)
        else ""
        for mapping in mappings
    )

    if (
        stage_ids != actual_stage_ids
        or any(not item for item in stage_ids)
        or len(set(stage_ids)) != len(stage_ids)
    ):
        raise _wave_error(
            (
                "Wave stage identities are invalid "
                "or inconsistent."
            ),
            code="invalid_wave_mapping",
            violations=("stage_ids",),
            workflow_id=workflow_id,
        )

    if any(
        not isinstance(
            mapping,
            RuntimeJobMapping,
        )
        for mapping in mappings
    ):
        raise _wave_error(
            (
                "Execution wave contains a "
                "non-RuntimeJobMapping value."
            ),
            code="invalid_wave_mapping",
            violations=("mappings",),
            workflow_id=workflow_id,
        )

    wave_indexes = {
        mapping.wave_index
        for mapping in mappings
    }

    if len(wave_indexes) != 1:
        raise _wave_error(
            (
                "All mappings must belong to one "
                "execution wave."
            ),
            code="mixed_execution_waves",
            violations=("wave_index",),
            workflow_id=workflow_id,
        )

    wave_index = next(
        iter(wave_indexes)
    )

    if (
        not isinstance(wave_index, int)
        or isinstance(wave_index, bool)
        or wave_index < 0
    ):
        raise _wave_error(
            "wave_index must be non-negative.",
            code="invalid_wave_mapping",
            violations=("wave_index",),
            workflow_id=workflow_id,
        )

    semantics = str(
        execution_semantics
        or ""
    ).strip()

    if not semantics:
        raise _wave_error(
            "execution_semantics is required.",
            code="invalid_execution_semantics",
            violations=(
                "execution_semantics",
            ),
            workflow_id=workflow_id,
            wave_index=wave_index,
        )

    if not callable(submitter):
        raise _wave_error(
            "submitter must be callable.",
            code="job_submission_failure",
            violations=("submitter",),
            workflow_id=workflow_id,
            wave_index=wave_index,
        )

    effective_registry = (
        correlation_registry
        if correlation_registry is not None
        else get_workflow_job_correlation_registry()
    )

    if not isinstance(
        effective_registry,
        WorkflowJobCorrelationRegistry,
    ):
        raise _wave_error(
            (
                "correlation_registry must be "
                "WorkflowJobCorrelationRegistry."
            ),
            code="correlation_failure",
            violations=(
                "correlation_registry",
            ),
            workflow_id=workflow_id,
            wave_index=wave_index,
        )

    normalized_overrides = (
        _normalize_wave_dependencies(
            dependency_job_ids_by_stage,
            stage_ids=stage_ids,
        )
    )

    enriched_mappings: list[
        RuntimeJobMapping
    ] = []
    effective_dependencies: dict[
        str,
        tuple[str, ...],
    ] = {}

    for mapping in mappings:
        if not isinstance(
            mapping,
            RuntimeJobMapping,
        ):
            raise _wave_error(
                (
                    "Execution wave contains a "
                    "non-RuntimeJobMapping value."
                ),
                code="invalid_wave_mapping",
                violations=("mappings",),
                workflow_id=workflow_id,
                wave_index=wave_index,
            )

        if mapping.workflow_id != workflow_id:
            raise _wave_error(
                (
                    "Mapping workflow identity does "
                    "not match the wave."
                ),
                code="invalid_wave_mapping",
                violations=(
                    mapping.stage_id,
                ),
                workflow_id=workflow_id,
                wave_index=wave_index,
            )

        request = mapping.creation_request

        if request.idempotency_key is not None:
            raise _wave_error(
                (
                    "Part C 8-D must not generate "
                    "idempotency identity."
                ),
                code="idempotency_authority_deferred",
                violations=(
                    mapping.stage_id,
                ),
                workflow_id=workflow_id,
                wave_index=wave_index,
            )

        dependency_ids = (
            normalized_overrides.get(
                mapping.stage_id,
                tuple(
                    request.dependency_job_ids
                ),
            )
        )

        enriched_request = _wave_replace(
            request,
            dependency_job_ids=dependency_ids,
        )
        enriched_mapping = _wave_replace(
            mapping,
            creation_request=(
                enriched_request
            ),
        )

        # Preflight the complete wave before the first submission.
        validated_request = _validate_mapping(
            enriched_mapping
        )
        _resolve_registration(
            validated_request
        )

        enriched_mappings.append(
            enriched_mapping
        )
        effective_dependencies[
            mapping.stage_id
        ] = tuple(
            dependency_ids
        )

    return (
        workflow_id,
        wave_index,
        semantics,
        stage_ids,
        tuple(enriched_mappings),
        effective_dependencies,
        effective_registry,
    )


def submit_runtime_execution_wave(
    *,
    mapping_result: RuntimeJobMappingResult,
    dependency_job_ids_by_stage: Mapping[
        str,
        Any,
    ] | None = None,
    execution_semantics: str = (
        "parallel_eligible"
    ),
    submitter: Callable[
        ...,
        Mapping[str, Any],
    ] = submit_universal_job,
    correlation_registry: (
        WorkflowJobCorrelationRegistry
        | None
    ) = None,
) -> RuntimeExecutionWaveGatewayResult:
    """
    Submit one certified immediate execution wave.

    Every mapping and Runtime Registration is preflighted before the first
    job submission. Dependency job identities may enrich the canonical
    creation requests. Idempotency identity remains owned by Part C 8-E.
    No dependency is generated between parallel-eligible wave members.
    """

    (
        workflow_id,
        wave_index,
        semantics,
        stage_ids,
        mappings,
        effective_dependencies,
        effective_registry,
    ) = _preflight_execution_wave(
        mapping_result=mapping_result,
        dependency_job_ids_by_stage=(
            dependency_job_ids_by_stage
        ),
        execution_semantics=(
            execution_semantics
        ),
        submitter=submitter,
        correlation_registry=(
            correlation_registry
        ),
    )

    submitted: list[
        RuntimeExecutionGatewayResult
    ] = []

    for mapping in mappings:
        try:
            result = submit_runtime_job_mapping(
                mapping=mapping,
                submitter=submitter,
                correlation_registry=(
                    effective_registry
                ),
            )
        except Exception as error:
            raise _wave_error(
                (
                    "Execution-wave submission failed "
                    f"at stage {mapping.stage_id!r}: "
                    f"{type(error).__name__}: {error}"
                ),
                code="wave_submission_failure",
                violations=(
                    mapping.stage_id,
                ),
                workflow_id=workflow_id,
                wave_index=wave_index,
                failed_stage_id=(
                    mapping.stage_id
                ),
                submitted_results=tuple(
                    submitted
                ),
            ) from error

        submitted.append(result)

    submissions = tuple(
        submitted
    )

    evidence = {
        "preflight_complete": True,
        "all_registrations_resolved": True,
        "canonical_single_mapping_gateway": (
            "submit_runtime_job_mapping"
        ),
        "dependency_strategy": (
            "enrich_canonical_mapping_request"
        ),
        "idempotency_strategy": (
            "defer_to_part_c_8_e_"
            "reconciliation_authority"
        ),
        "artificial_intra_wave_dependencies": (
            False
        ),
        "partial_failure_evidence_retained": (
            True
        ),
        "handler_dispatched": False,
    }

    return RuntimeExecutionWaveGatewayResult(
        contract_version=(
            RUNTIME_EXECUTION_WAVE_GATEWAY_CONTRACT_VERSION
        ),
        gateway_version=(
            RUNTIME_EXECUTION_WAVE_GATEWAY_VERSION
        ),
        workflow_id=workflow_id,
        wave_index=wave_index,
        execution_semantics=semantics,
        stage_ids=stage_ids,
        submission_count=len(
            submissions
        ),
        created_count=sum(
            1
            for item in submissions
            if item.created
        ),
        reused_existing_count=sum(
            1
            for item in submissions
            if item.reused_existing_job
        ),
        queued_count=sum(
            1
            for item in submissions
            if item.queued
        ),
        job_ids=tuple(
            item.job_id
            for item in submissions
        ),
        dependency_job_ids_by_stage=(
            effective_dependencies
        ),
        mappings=mappings,
        submissions=submissions,
        evidence=evidence,
    )


def explain_runtime_execution_wave_gateway_v1(
) -> dict[str, Any]:
    return {
        "component": (
            "Runtime Execution Wave Gateway"
        ),
        "version": (
            RUNTIME_EXECUTION_WAVE_GATEWAY_VERSION
        ),
        "contract_version": (
            RUNTIME_EXECUTION_WAVE_GATEWAY_CONTRACT_VERSION
        ),
        "canonical_single_mapping_gateway": (
            "submit_runtime_job_mapping"
        ),
        "preflight_scope": (
            "complete_wave_before_first_submission"
        ),
        "dependency_strategy": (
            "enrich_canonical_mapping_request"
        ),
        "idempotency_strategy": (
            "defer_to_part_c_8_e_"
            "reconciliation_authority"
        ),
        "artificial_intra_wave_dependencies": False,
        "partial_failure_evidence": True,
        "handler_dispatch": False,
    }
# === PART C 8-D EXECUTION WAVE GATEWAY END ===
