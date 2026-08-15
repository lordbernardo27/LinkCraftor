"""Canonical Universal Job Creation Engine (Phase 2.1.2).

This module validates and constructs UniversalJob instances. It performs no
queue, worker, dispatch, persistence, ledger, progress-file, or status-file I/O.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Final, Iterable, Mapping, Optional, Sequence, Tuple

from backend.server.runtime.universal_jobs.contract import (
    UNIVERSAL_JOB_CONTRACT_VERSION,
    UniversalJob,
    UniversalJobContractError,
    UniversalJobCostRecord,
    UniversalJobPriority,
    UniversalJobProgress,
    UniversalJobStatus,
    validate_universal_job,
)

from backend.server.runtime.universal_jobs.identity import (
    UNIVERSAL_JOB_ID_PREFIX,
    UniversalJobIdentityError,
    resolve_universal_job_id,
    validate_universal_job_type,
)

from backend.server.runtime.universal_jobs.metadata import (
    UniversalJobMetadataError,
    normalize_universal_job_metadata,
    thaw_universal_job_metadata,
)

from backend.server.runtime.universal_jobs.payload_reference import (
    normalize_universal_job_payload_reference,
)

from backend.server.runtime.universal_jobs.priority import (
    UniversalJobPriorityError,
    normalize_universal_job_priority,
)
UNIVERSAL_JOB_CREATION_ENGINE_VERSION: Final[str] = (
    "universal_job_creation_engine_v2.1.2"
)
UNIVERSAL_JOB_CREATION_RESULT_VERSION: Final[str] = (
    "universal_job_creation_result_v1"
)


class UniversalJobCreationError(ValueError):
    """Raised when a Universal Job cannot be safely created."""

    def __init__(
        self,
        message: str,
        *,
        code: str,
        violations: Sequence[str] = (),
    ) -> None:
        super().__init__(message)
        self.code = str(code or "job_creation_failed")
        self.violations = tuple(str(item) for item in violations)

    def to_dict(self) -> dict[str, Any]:
        return {
            "error": "UniversalJobCreationError",
            "code": self.code,
            "message": str(self),
            "violations": list(self.violations),
            "creation_engine_version": UNIVERSAL_JOB_CREATION_ENGINE_VERSION,
        }


def _utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="microseconds")
        .replace("+00:00", "Z")
    )


def _clean_text(value: Any) -> str:
    return str(value or "").strip()


def _first_text(*values: Any, fallback: str = "") -> str:
    for value in values:
        text = _clean_text(value)
        if text:
            return text
    return fallback


def _validate_json_value(value: Any, *, path: str) -> None:
    if value is None or isinstance(value, (str, int, bool)):
        return

    if isinstance(value, float):
        if not math.isfinite(value):
            raise UniversalJobCreationError(
                f"{path} contains a non-finite float.",
                code="non_json_payload",
                violations=(f"{path} must contain only finite JSON values",),
            )
        return

    if isinstance(value, Mapping):
        for key, item in value.items():
            if not isinstance(key, str):
                raise UniversalJobCreationError(
                    f"{path} contains a non-string mapping key.",
                    code="non_json_payload",
                    violations=(f"{path} mapping keys must be strings",),
                )
            _validate_json_value(item, path=f"{path}.{key}")
        return

    if isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _validate_json_value(item, path=f"{path}[{index}]")
        return

    raise UniversalJobCreationError(
        f"{path} contains unsupported type {type(value).__name__}.",
        code="non_json_payload",
        violations=(f"{path} must be JSON-safe",),
    )


def _freeze_json(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType(
            {str(key): _freeze_json(item) for key, item in value.items()}
        )
    if isinstance(value, (list, tuple)):
        return tuple(_freeze_json(item) for item in value)
    return value


def _thaw_json(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _thaw_json(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw_json(item) for item in value]
    return value


def _normalize_mapping(
    value: Optional[Mapping[str, Any]],
    *,
    field_name: str,
) -> Mapping[str, Any]:
    if value is None:
        return MappingProxyType({})

    if not isinstance(value, Mapping):
        raise UniversalJobCreationError(
            f"{field_name} must be a mapping.",
            code=f"invalid_{field_name}",
            violations=(f"{field_name} must be a mapping",),
        )

    _validate_json_value(value, path=field_name)

    try:
        json.dumps(value, ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise UniversalJobCreationError(
            f"{field_name} is not JSON serializable.",
            code=f"invalid_{field_name}",
            violations=(str(exc),),
        ) from exc

    return _freeze_json(dict(value))


def _normalize_string_tuple(
    value: Optional[Iterable[Any]],
    *,
    field_name: str,
) -> Tuple[str, ...]:
    if value is None:
        return ()

    if isinstance(value, (str, bytes, Mapping)):
        raise UniversalJobCreationError(
            f"{field_name} must be an iterable of identifiers.",
            code=f"invalid_{field_name}",
            violations=(f"{field_name} must not be a string or mapping",),
        )

    normalized: dict[str, None] = {}
    for item in value:
        text = _clean_text(item)
        if not text:
            raise UniversalJobCreationError(
                f"{field_name} contains an empty identifier.",
                code=f"invalid_{field_name}",
                violations=(f"{field_name} must not contain empty values",),
            )
        normalized.setdefault(text, None)

    return tuple(normalized)


def _resolve_priority(
    value: Any,
) -> UniversalJobPriority:
    try:
        return normalize_universal_job_priority(
            value
        )

    except UniversalJobPriorityError as exc:
        raise UniversalJobCreationError(
            "Invalid canonical job priority.",
            code="invalid_priority",
            violations=(str(exc),),
        ) from exc


def _resolve_maximum_attempts(
    explicit_value: Optional[int],
    payload: Mapping[str, Any],
    registration: Optional[Mapping[str, Any]],
) -> int:
    candidate: Any = explicit_value

    if candidate is None:
        candidate = payload.get("maximum_attempts")

    if candidate is None:
        candidate = payload.get("max_attempts")

    if candidate is None and registration:
        retry_policy = registration.get("retry_policy")
        if isinstance(retry_policy, Mapping):
            candidate = (
                retry_policy.get("maximum_attempts")
                if retry_policy.get("maximum_attempts") is not None
                else retry_policy.get("max_attempts")
            )

    if candidate is None:
        candidate = 3

    if isinstance(candidate, bool) or not isinstance(candidate, int):
        raise UniversalJobCreationError(
            "maximum_attempts must be an integer.",
            code="invalid_maximum_attempts",
            violations=("maximum_attempts must be an integer",),
        )

    if candidate < 1:
        raise UniversalJobCreationError(
            "maximum_attempts must be at least 1.",
            code="invalid_maximum_attempts",
            violations=("maximum_attempts must be at least 1",),
        )

    return candidate


def _normalize_supported_job_types(
    values: Optional[Iterable[Any]],
) -> frozenset[str]:
    if values is None:
        return frozenset()

    if isinstance(values, (str, bytes, Mapping)):
        raise UniversalJobCreationError(
            "supported_job_types must be an iterable of job-type strings.",
            code="invalid_supported_job_types",
            violations=(
                "supported_job_types must not be a string, bytes value, or mapping",
            ),
        )

    normalized: dict[str, None] = {}

    for value in values:
        try:
            job_type = validate_universal_job_type(value)
        except UniversalJobIdentityError as exc:
            raise UniversalJobCreationError(
                "supported_job_types contains a non-canonical job type.",
                code="invalid_supported_job_types",
                violations=exc.violations or (str(exc),),
            ) from exc

        normalized.setdefault(job_type, None)

    return frozenset(normalized)


def _resolve_registration(
    *,
    job_type: str,
    supported_job_types: frozenset[str],
    runtime_registration: Optional[Mapping[str, Any]],
) -> tuple[str, Optional[Mapping[str, Any]]]:
    """Resolve job-type support without loading any persistent registry."""

    if job_type in supported_job_types:
        return "static", None

    if runtime_registration is None:
        raise UniversalJobCreationError(
            f"Unsupported Universal Job type: {job_type}",
            code="unsupported_job_type",
            violations=(
                "job_type must be statically supported or supplied through "
                "Runtime Registration metadata",
            ),
        )

    registration = _normalize_mapping(
        runtime_registration,
        field_name="runtime_registration",
    )

    raw_registered_job_type = registration.get("job_type")

    try:
        registered_job_type = validate_universal_job_type(
            raw_registered_job_type
        )
    except UniversalJobIdentityError as exc:
        raise UniversalJobCreationError(
            "Runtime Registration metadata contains an invalid job_type.",
            code="invalid_runtime_registration",
            violations=exc.violations or (str(exc),),
        ) from exc

    if registered_job_type != job_type:
        raise UniversalJobCreationError(
            "Runtime Registration metadata does not match the requested job type.",
            code="runtime_registration_job_type_mismatch",
            violations=(
                "runtime_registration.job_type must match job_type",
            ),
        )

    for field_name in ("pipeline", "stage"):
        field_value = registration.get(field_name)

        if field_value is not None and not isinstance(field_value, str):
            raise UniversalJobCreationError(
                f"Runtime Registration {field_name} must be a string.",
                code="invalid_runtime_registration",
                violations=(
                    f"runtime_registration.{field_name} must be a string when supplied",
                ),
            )

    retry_policy = registration.get("retry_policy")

    if retry_policy is not None and not isinstance(retry_policy, Mapping):
        raise UniversalJobCreationError(
            "Runtime Registration retry_policy must be a mapping.",
            code="invalid_runtime_registration",
            violations=(
                "runtime_registration.retry_policy must be a mapping when supplied",
            ),
        )

    return "runtime_registration", registration


def _validate_registered_payload(
    *,
    registration: Optional[Mapping[str, Any]],
    payload: Mapping[str, Any],
) -> None:
    if not registration:
        return

    required = registration.get("required_payload_fields")

    if required is None:
        required_fields: tuple[str, ...] = ()
    else:
        if not isinstance(required, (list, tuple)):
            raise UniversalJobCreationError(
                "Runtime Registration required_payload_fields is invalid.",
                code="invalid_runtime_registration",
                violations=(
                    "runtime_registration.required_payload_fields must be a list or tuple",
                ),
            )

        normalized_fields: dict[str, None] = {}

        for field_name in required:
            if not isinstance(field_name, str) or not field_name.strip():
                raise UniversalJobCreationError(
                    "Runtime Registration contains an invalid required payload field.",
                    code="invalid_runtime_registration",
                    violations=(
                        "every required_payload_fields entry must be a non-empty string",
                    ),
                )

            normalized_fields.setdefault(
                field_name.strip(),
                None,
            )

        required_fields = tuple(normalized_fields)

    missing = [
        field_name
        for field_name in required_fields
        if (
            field_name not in payload
            or payload.get(field_name) is None
            or payload.get(field_name) == ""
        )
    ]

    if missing:
        raise UniversalJobCreationError(
            "Registered job payload is missing required fields.",
            code="missing_required_payload_fields",
            violations=tuple(
                f"missing required payload field: {field_name}"
                for field_name in missing
            ),
        )


@dataclass(frozen=True)
class UniversalJobCreationRequest:
    workspace_id: str
    job_type: str
    payload: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)
    user_id: str = "system"
    product_id: str = "linkcraftor"
    pipeline: str = ""
    stage: str = ""
    payload_reference: Optional[str] = None
    priority: Any = UniversalJobPriority.NORMAL
    parent_job_id: Optional[str] = None
    dependency_job_ids: Tuple[str, ...] = ()
    batch_id: Optional[str] = None
    pipeline_run_id: Optional[str] = None
    idempotency_key: Optional[str] = None
    maximum_attempts: Optional[int] = None
    enqueue: bool = True
    job_id: Optional[str] = None
    job_id_prefix: str = UNIVERSAL_JOB_ID_PREFIX
    created_at: Optional[str] = None


@dataclass(frozen=True)
class UniversalJobCreationResult:
    job: UniversalJob
    payload: Mapping[str, Any]
    metadata: Mapping[str, Any]
    registration: Optional[Mapping[str, Any]]
    enqueue_requested: bool
    job_type_source: str
    creation_engine_version: str = UNIVERSAL_JOB_CREATION_ENGINE_VERSION

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": UNIVERSAL_JOB_CREATION_RESULT_VERSION,
            "ok": True,
            "creation_engine_version": self.creation_engine_version,
            "contract_version": UNIVERSAL_JOB_CONTRACT_VERSION,
            "enqueue_requested": self.enqueue_requested,
            "job_type_source": self.job_type_source,
            "job": self.job.to_canonical_dict(),
            "payload": _thaw_json(self.payload),
            "metadata": thaw_universal_job_metadata(self.metadata),
            "registration": (
                _thaw_json(self.registration)
                if self.registration is not None
                else None
            ),
            "identity_fingerprint": self.job.identity_fingerprint(),
            "contract_fingerprint": self.job.contract_fingerprint(),
            "content_fingerprint": self.job.content_fingerprint(),
        }


def normalize_universal_job_creation_request(
    request: UniversalJobCreationRequest,
    *,
    supported_job_types: Optional[Iterable[Any]] = None,
    runtime_registration: Optional[Mapping[str, Any]] = None,
) -> tuple[
    UniversalJobCreationRequest,
    str,
    Optional[Mapping[str, Any]],
]:
    if not isinstance(request, UniversalJobCreationRequest):
        raise UniversalJobCreationError(
            "request must be UniversalJobCreationRequest.",
            code="invalid_creation_request",
            violations=("request must be UniversalJobCreationRequest",),
        )

    workspace_id = _clean_text(request.workspace_id)

    if not workspace_id:
        raise UniversalJobCreationError(
            "workspace_id is required.",
            code="missing_workspace_id",
            violations=("workspace_id is required",),
        )

    try:
        job_type = validate_universal_job_type(
            request.job_type
        )
    except UniversalJobIdentityError as exc:
        raise UniversalJobCreationError(
            str(exc),
            code=exc.code,
            violations=exc.violations or (str(exc),),
        ) from exc

    payload = _normalize_mapping(
        request.payload,
        field_name="payload",
    )
    try:
        metadata = normalize_universal_job_metadata(
            request.metadata
        )
    except UniversalJobMetadataError as exc:
        raise UniversalJobCreationError(
            str(exc),
            code=exc.code,
            violations=exc.violations or (str(exc),),
        ) from exc
    dependencies = _normalize_string_tuple(
        request.dependency_job_ids,
        field_name="dependency_job_ids",
    )
    static_job_types = _normalize_supported_job_types(
        supported_job_types,
    )
    source, registration = _resolve_registration(
        job_type=job_type,
        supported_job_types=static_job_types,
        runtime_registration=runtime_registration,
    )
    _validate_registered_payload(
        registration=registration,
        payload=payload,
    )

    registration_pipeline = (
        registration.get("pipeline")
        if registration is not None
        else ""
    )
    registration_stage = (
        registration.get("stage")
        if registration is not None
        else ""
    )

    pipeline = _first_text(
        request.pipeline,
        payload.get("pipeline"),
        payload.get("pipeline_name"),
        registration_pipeline,
        fallback="universal_knowledge",
    )
    stage = _first_text(
        request.stage,
        payload.get("stage"),
        payload.get("stage_name"),
        registration_stage,
        fallback=job_type,
    )
    user_id = _first_text(
        request.user_id,
        payload.get("user_id"),
        fallback="system",
    )
    product_id = _first_text(
        request.product_id,
        payload.get("product_id"),
        fallback="linkcraftor",
    )
    payload_reference = normalize_universal_job_payload_reference(
        request.payload_reference
    )
    priority = _resolve_priority(request.priority)
    maximum_attempts = _resolve_maximum_attempts(
        request.maximum_attempts,
        payload,
        registration,
    )

    if not isinstance(request.enqueue, bool):
        raise UniversalJobCreationError(
            "enqueue must be a boolean.",
            code="invalid_enqueue",
            violations=(
                "enqueue must be either True or False",
            ),
        )

    if (
        not isinstance(request.job_id_prefix, str)
        or request.job_id_prefix != UNIVERSAL_JOB_ID_PREFIX
    ):
        raise UniversalJobCreationError(
            "job_id_prefix is fixed by the Universal Job identity namespace.",
            code="invalid_job_id_prefix",
            violations=(
                f"job_id_prefix must be exactly {UNIVERSAL_JOB_ID_PREFIX!r}",
            ),
        )

    created_at = _clean_text(request.created_at) or _utc_now()

    try:
        job_id = resolve_universal_job_id(
            request.job_id
        )
    except UniversalJobIdentityError as exc:
        raise UniversalJobCreationError(
            str(exc),
            code=exc.code,
            violations=exc.violations or (str(exc),),
        ) from exc

    normalized = UniversalJobCreationRequest(
        workspace_id=workspace_id,
        job_type=job_type,
        payload=payload,
        metadata=metadata,
        user_id=user_id,
        product_id=product_id,
        pipeline=pipeline,
        stage=stage,
        payload_reference=payload_reference,
        priority=priority,
        parent_job_id=_clean_text(request.parent_job_id) or None,
        dependency_job_ids=dependencies,
        batch_id=_clean_text(request.batch_id) or None,
        pipeline_run_id=_clean_text(request.pipeline_run_id) or None,
        idempotency_key=_clean_text(request.idempotency_key) or None,
        maximum_attempts=maximum_attempts,
        enqueue=request.enqueue,
        job_id=job_id,
        job_id_prefix=UNIVERSAL_JOB_ID_PREFIX,
        created_at=created_at,
    )

    return normalized, source, registration


def create_universal_job(
    *,
    workspace_id: str,
    job_type: str,
    payload: Optional[Mapping[str, Any]] = None,
    metadata: Optional[Mapping[str, Any]] = None,
    user_id: str = "system",
    product_id: str = "linkcraftor",
    pipeline: str = "",
    stage: str = "",
    payload_reference: Optional[str] = None,
    priority: Any = UniversalJobPriority.NORMAL,
    parent_job_id: Optional[str] = None,
    dependency_job_ids: Optional[Iterable[Any]] = None,
    batch_id: Optional[str] = None,
    pipeline_run_id: Optional[str] = None,
    idempotency_key: Optional[str] = None,
    maximum_attempts: Optional[int] = None,
    enqueue: bool = True,
    job_id: Optional[str] = None,
    job_id_prefix: str = UNIVERSAL_JOB_ID_PREFIX,
    created_at: Optional[str] = None,
    supported_job_types: Optional[Iterable[Any]] = None,
    runtime_registration: Optional[Mapping[str, Any]] = None,
) -> UniversalJobCreationResult:
    """Validate and construct one canonical Universal Job without I/O."""

    request = UniversalJobCreationRequest(
        workspace_id=workspace_id,
        job_type=job_type,
        payload={} if payload is None else payload,
        metadata={} if metadata is None else metadata,
        user_id=user_id,
        product_id=product_id,
        pipeline=pipeline,
        stage=stage,
        payload_reference=payload_reference,
        priority=priority,
        parent_job_id=parent_job_id,
        dependency_job_ids=(
            ()
            if dependency_job_ids is None
            else dependency_job_ids
        ),
        batch_id=batch_id,
        pipeline_run_id=pipeline_run_id,
        idempotency_key=idempotency_key,
        maximum_attempts=maximum_attempts,
        enqueue=enqueue,
        job_id=job_id,
        job_id_prefix=job_id_prefix,
        created_at=created_at,
    )

    normalized, source, registration = (
        normalize_universal_job_creation_request(
            request,
            supported_job_types=supported_job_types,
            runtime_registration=runtime_registration,
        )
    )

    status = (
        UniversalJobStatus.QUEUED
        if normalized.enqueue
        else UniversalJobStatus.CREATED
    )
    message = (
        "Job queued."
        if normalized.enqueue
        else "Job created without queue dispatch."
    )

    try:
        job = UniversalJob(
            job_id=normalized.job_id or "",
            workspace_id=normalized.workspace_id,
            user_id=normalized.user_id,
            product_id=normalized.product_id,
            pipeline=normalized.pipeline,
            stage=normalized.stage,
            job_type=normalized.job_type,
            payload_reference=normalized.payload_reference,
            priority=normalized.priority,
            status=status,
            attempts=0,
            maximum_attempts=normalized.maximum_attempts or 3,
            lease_owner=None,
            lease_id=None,
            lease_started_at=None,
            lease_expires_at=None,
            parent_job_id=normalized.parent_job_id,
            dependency_job_ids=normalized.dependency_job_ids,
            batch_id=normalized.batch_id,
            pipeline_run_id=normalized.pipeline_run_id,
            progress=UniversalJobProgress(
                percent=0,
                step=normalized.stage,
                message=message,
                updated_at=normalized.created_at,
            ),
            checkpoint_reference=None,
            result_reference=None,
            artifact_references=(),
            idempotency_key=normalized.idempotency_key,
            AU_reserved=0,
            AU_consumed=0,
            cost_record=UniversalJobCostRecord(),
            created_at=normalized.created_at,
            scheduled_at=None,
            started_at=None,
            completed_at=None,
            failed_at=None,
            cancelled_at=None,
            error_code=None,
            error_message=None,
            error_details={},
        )
    except UniversalJobContractError as exc:
        raise UniversalJobCreationError(
            "Universal Job Contract rejected the creation request.",
            code="contract_validation_failed",
            violations=exc.violations or (str(exc),),
        ) from exc

    validation = validate_universal_job(job)
    if not validation.is_valid:
        raise UniversalJobCreationError(
            "Created Universal Job failed final validation.",
            code="final_validation_failed",
            violations=validation.violations,
        )

    return UniversalJobCreationResult(
        job=job,
        payload=normalized.payload,
        metadata=normalized.metadata,
        registration=registration,
        enqueue_requested=normalized.enqueue,
        job_type_source=source,
    )


def explain_universal_job_creation_engine_v1() -> dict[str, Any]:
    return {
        "phase": "2.1.2",
        "component": "Universal Job Creation Engine",
        "creation_engine_version": UNIVERSAL_JOB_CREATION_ENGINE_VERSION,
        "contract_version": UNIVERSAL_JOB_CONTRACT_VERSION,
        "canonical_operation": "create_universal_job",
        "responsibilities": [
            "validate creation inputs",
            "resolve static job types or caller-supplied Runtime Registration metadata",
            "validate registered required payload fields",
            "normalize creation identity and classification",
            "construct the certified Universal Job Contract",
            "return a normalized creation result",
        ],
        "prohibitions": [
            "no queue writes",
            "no persistence writes",
            "no worker execution",
            "no handler dispatch",
            "no ledger writes",
            "no progress-file writes",
            "no persistent Runtime Registration loading",
            "no state transitions beyond initial creation status",
        ],
    }


__all__ = [
    "UNIVERSAL_JOB_CREATION_ENGINE_VERSION",
    "UNIVERSAL_JOB_CREATION_RESULT_VERSION",
    "UniversalJobCreationError",
    "UniversalJobCreationRequest",
    "UniversalJobCreationResult",
    "normalize_universal_job_creation_request",
    "create_universal_job",
    "explain_universal_job_creation_engine_v1",
]
