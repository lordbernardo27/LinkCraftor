"""
Registration concurrency and idempotency queue admission.

This authority is side-effect-free. The orchestration queue invokes it
while holding the existing canonical cross-process dequeue lock.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Iterable, Mapping

from backend.server.runtime.universal_jobs.duplicate_detection import (
    UniversalJobDuplicateCandidate,
    detect_universal_job_duplicate,
)
from backend.server.runtime.universal_jobs.duplicate_handling import (
    UniversalJobDuplicateHandlingAction,
    decide_universal_job_duplicate_handling,
)


SCHEMA_VERSION = "runtime_registration_execution_policy_v1"


class RuntimeRegistrationExecutionPolicyError(RuntimeError):
    pass


class RuntimeRegistrationQueueAction(str, Enum):
    CLAIM = "claim"
    DEFER = "defer"
    REUSE_EXISTING = "reuse_existing"


@dataclass(frozen=True, slots=True)
class RuntimeRegistrationQueueAdmission:
    action: RuntimeRegistrationQueueAction
    reason: str
    registration_job_type: str
    concurrency_limit: int | None = None
    active_count: int = 0
    existing_job_id: str | None = None
    evidence: Mapping[str, Any] = field(default_factory=dict)
    schema_version: str = field(default=SCHEMA_VERSION, init=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "evidence",
            MappingProxyType(dict(self.evidence)),
        )

    def to_metadata(self) -> dict[str, Any]:
        return {
            "runtime_registration_policy_schema_version":
                self.schema_version,
            "runtime_registration_queue_action":
                self.action.value,
            "runtime_registration_policy_reason":
                self.reason,
            "runtime_registration_job_type":
                self.registration_job_type,
            "runtime_registration_concurrency_limit":
                self.concurrency_limit,
            "runtime_registration_active_count":
                self.active_count,
            "runtime_registration_existing_job_id":
                self.existing_job_id,
            "runtime_registration_policy_evidence":
                dict(self.evidence),
        }


def _read(
    value: Any,
    field_name: str,
    default: Any = None,
) -> Any:
    if isinstance(value, Mapping):
        return value.get(field_name, default)

    return getattr(value, field_name, default)


def _text(value: Any) -> str:
    return str(
        value if value is not None else ""
    ).strip()


def _job_id(job: Any) -> str:
    return _text(_read(job, "job_id"))


def _workspace_id(job: Any) -> str:
    return _text(_read(job, "workspace_id"))


def _job_type(job: Any) -> str:
    return _text(_read(job, "job_type"))


def _status(job: Any) -> str:
    return _text(
        _read(job, "status")
    ).lower()


def _payload(job: Any) -> dict[str, Any]:
    value = _read(job, "payload", {})

    return (
        dict(value)
        if isinstance(value, Mapping)
        else {}
    )


def _metadata(job: Any) -> dict[str, Any]:
    value = _read(job, "metadata", {})

    return (
        dict(value)
        if isinstance(value, Mapping)
        else {}
    )


def _job_mapping(job: Any) -> dict[str, Any]:
    if isinstance(job, Mapping):
        return dict(job)

    if is_dataclass(job):
        value = asdict(job)

        if isinstance(value, Mapping):
            return dict(value)

    result: dict[str, Any] = {}

    for name in (
        "job_id",
        "workspace_id",
        "job_type",
        "status",
        "priority",
        "payload",
        "metadata",
        "created_at",
        "updated_at",
    ):
        value = getattr(job, name, None)

        if value is not None:
            result[name] = value

    return result


def _idempotency_key(job: Any) -> str | None:
    direct = _text(
        _read(job, "idempotency_key")
    )

    if direct:
        return direct

    metadata = _metadata(job)
    candidates: list[Mapping[str, Any]] = [metadata]

    for name in (
        "universal_job",
        "runtime_job",
        "universal_job_record",
        "runtime_job_record",
        "job",
    ):
        nested = metadata.get(name)

        if isinstance(nested, Mapping):
            candidates.append(nested)

    for candidate in candidates:
        value = _text(
            candidate.get("idempotency_key")
        )

        if value:
            return value

    return None


def _order(job: Any) -> tuple[str, str]:
    return (
        _text(_read(job, "created_at")),
        _job_id(job),
    )


def _registration(
    value: Any,
) -> Mapping[str, Any] | None:
    if value is None:
        return None

    if isinstance(value, Mapping):
        return value

    public = getattr(
        value,
        "to_public_dict",
        None,
    )

    if callable(public):
        result = public()

        if isinstance(result, Mapping):
            return result

    raise RuntimeRegistrationExecutionPolicyError(
        "registration must be a mapping or expose to_public_dict()."
    )


def _idempotency_fields(
    registration: Mapping[str, Any],
) -> tuple[str, ...]:
    value = registration.get(
        "idempotency_fields",
        (),
    )

    if value is None:
        return ()

    if isinstance(value, (str, bytes)):
        raise RuntimeRegistrationExecutionPolicyError(
            "idempotency_fields must be a collection."
        )

    fields: list[str] = []

    for item in value:
        name = _text(item)

        if not name:
            raise RuntimeRegistrationExecutionPolicyError(
                "idempotency_fields contains an empty name."
            )

        if name in fields:
            raise RuntimeRegistrationExecutionPolicyError(
                "Duplicate idempotency field: " + name
            )

        fields.append(name)

    return tuple(fields)


def _concurrency_policy(
    registration: Mapping[str, Any],
) -> tuple[int | None, str]:
    value = registration.get(
        "concurrency_policy",
        {},
    )

    if value is None:
        return None, "workspace_job_type"

    if not isinstance(value, Mapping):
        raise RuntimeRegistrationExecutionPolicyError(
            "concurrency_policy must be a mapping."
        )

    policy = dict(value)

    if not policy:
        return None, "workspace_job_type"

    limit_keys = (
        "max_active_jobs",
        "maximum_active_jobs",
        "max_concurrent_jobs",
        "limit",
    )

    allowed = set(limit_keys) | {"scope"}
    unknown = sorted(set(policy) - allowed)

    if unknown:
        raise RuntimeRegistrationExecutionPolicyError(
            "Unsupported concurrency_policy keys: "
            + ", ".join(unknown)
        )

    limits: list[int] = []

    for key in limit_keys:
        if key not in policy:
            continue

        limit = policy[key]

        if (
            isinstance(limit, bool)
            or not isinstance(limit, int)
            or limit < 1
        ):
            raise RuntimeRegistrationExecutionPolicyError(
                f"{key} must be a positive integer."
            )

        limits.append(limit)

    if not limits:
        raise RuntimeRegistrationExecutionPolicyError(
            "A concurrency limit is required."
        )

    if len(set(limits)) != 1:
        raise RuntimeRegistrationExecutionPolicyError(
            "Conflicting concurrency limits were declared."
        )

    scope = _text(
        policy.get(
            "scope",
            "workspace_job_type",
        )
    ).lower()

    aliases = {
        "global": "global",
        "workspace": "workspace",
        "job_type": "job_type",
        "workspace_job_type": "workspace_job_type",
        "workspace+job_type": "workspace_job_type",
    }

    if scope not in aliases:
        raise RuntimeRegistrationExecutionPolicyError(
            "Unsupported concurrency scope."
        )

    return limits[0], aliases[scope]


def _same_scope(
    candidate: Any,
    existing: Any,
    scope: str,
) -> bool:
    if scope == "global":
        return True

    if scope == "workspace":
        return _workspace_id(candidate) == _workspace_id(existing)

    if scope == "job_type":
        return _job_type(candidate) == _job_type(existing)

    return (
        _workspace_id(candidate) == _workspace_id(existing)
        and
        _job_type(candidate) == _job_type(existing)
    )


def _duplicate_candidate(
    job: Any,
) -> UniversalJobDuplicateCandidate:
    return UniversalJobDuplicateCandidate.from_values(
        workspace_id=_workspace_id(job),
        job_type=_job_type(job),
        idempotency_key=_idempotency_key(job),
        job=_job_mapping(job),
        payload=_payload(job),
    )


def evaluate_runtime_registration_queue_candidate(
    *,
    candidate: Any,
    existing_jobs: Iterable[Any],
    registration: Any,
) -> RuntimeRegistrationQueueAdmission:
    candidate_id = _job_id(candidate)
    workspace_id = _workspace_id(candidate)
    job_type = _job_type(candidate)

    if not candidate_id:
        raise RuntimeRegistrationExecutionPolicyError(
            "candidate.job_id is required."
        )

    if not workspace_id:
        raise RuntimeRegistrationExecutionPolicyError(
            "candidate.workspace_id is required."
        )

    if not job_type:
        raise RuntimeRegistrationExecutionPolicyError(
            "candidate.job_type is required."
        )

    public = _registration(registration)

    if public is None:
        return RuntimeRegistrationQueueAdmission(
            action=RuntimeRegistrationQueueAction.CLAIM,
            reason="no_runtime_registration",
            registration_job_type=job_type,
        )

    registered_type = _text(public.get("job_type"))

    if registered_type and registered_type != job_type:
        raise RuntimeRegistrationExecutionPolicyError(
            "Registration job_type does not match candidate."
        )

    jobs = tuple(existing_jobs)
    fields = _idempotency_fields(public)
    explicit_key = _idempotency_key(candidate)

    if fields or explicit_key is not None:
        candidate_view = _duplicate_candidate(candidate)

        earlier = sorted(
            (
                job
                for job in jobs
                if (
                    _job_id(job)
                    and _job_id(job) != candidate_id
                    and _order(job) < _order(candidate)
                )
            ),
            key=_order,
        )

        for existing in earlier:
            detection = detect_universal_job_duplicate(
                candidate_view,
                _duplicate_candidate(existing),
                idempotency_fields=fields,
            )

            if not detection.is_duplicate:
                continue

            handling = decide_universal_job_duplicate_handling(
                detection,
                existing_job_id=_job_id(existing),
            )

            if (
                handling.action
                is not
                UniversalJobDuplicateHandlingAction.REUSE_EXISTING
            ):
                continue

            existing_status = _status(existing)

            evidence = {
                "duplicate_detection": detection.to_dict(),
                "duplicate_handling_action":
                    handling.action.value,
                "existing_status": existing_status,
            }

            if existing_status in {"queued", "running"}:
                return RuntimeRegistrationQueueAdmission(
                    action=RuntimeRegistrationQueueAction.DEFER,
                    reason="matching_job_is_not_terminal",
                    registration_job_type=job_type,
                    existing_job_id=_job_id(existing),
                    evidence=evidence,
                )

            if existing_status in {
                "completed",
                "succeeded",
                "success",
            }:
                return RuntimeRegistrationQueueAdmission(
                    action=(
                        RuntimeRegistrationQueueAction
                        .REUSE_EXISTING
                    ),
                    reason="matching_job_completed",
                    registration_job_type=job_type,
                    existing_job_id=_job_id(existing),
                    evidence=evidence,
                )

    limit, scope = _concurrency_policy(public)

    if limit is None:
        return RuntimeRegistrationQueueAdmission(
            action=RuntimeRegistrationQueueAction.CLAIM,
            reason="registration_policy_admitted",
            registration_job_type=job_type,
        )

    active = tuple(
        job
        for job in jobs
        if (
            _job_id(job) != candidate_id
            and _status(job) == "running"
            and _same_scope(candidate, job, scope)
        )
    )

    if len(active) >= limit:
        return RuntimeRegistrationQueueAdmission(
            action=RuntimeRegistrationQueueAction.DEFER,
            reason="concurrency_limit_reached",
            registration_job_type=job_type,
            concurrency_limit=limit,
            active_count=len(active),
            evidence={
                "scope": scope,
                "active_job_ids": [
                    _job_id(job)
                    for job in active
                ],
            },
        )

    return RuntimeRegistrationQueueAdmission(
        action=RuntimeRegistrationQueueAction.CLAIM,
        reason="concurrency_capacity_available",
        registration_job_type=job_type,
        concurrency_limit=limit,
        active_count=len(active),
        evidence={"scope": scope},
    )
