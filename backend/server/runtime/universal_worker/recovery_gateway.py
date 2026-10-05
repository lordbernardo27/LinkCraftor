from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping

from backend.server.orchestration.job_store import (
    load_jobs,
    update_job_status,
)
from backend.server.orchestration.models import (
    JOB_STATUS_FAILED,
    JOB_STATUS_QUEUED,
    JOB_STATUS_RUNNING,
)
from backend.server.runtime.universal_jobs.contract import (
    UniversalJobStatus,
)
from backend.server.runtime.universal_queue.dead_letter import (
    create_universal_dead_letter_evidence,
    evaluate_universal_dead_letter,
)
from backend.server.runtime.universal_queue.recovery import (
    create_universal_queue_recovery_snapshot,
    recover_universal_queue_membership,
)
from backend.server.runtime.universal_worker.leasing import (
    UniversalWorkerLease,
    UniversalWorkerLeaseState,
    evaluate_universal_worker_lease_state,
)
from backend.server.runtime.universal_worker.recovery import (
    UniversalWorkerRecoveryDisposition,
    create_universal_worker_recovery_evidence,
    evaluate_universal_worker_recovery,
)


UNIVERSAL_RUNTIME_RECOVERY_GATEWAY_VERSION = (
    "universal_runtime_recovery_gateway_v1"
)

DEFAULT_RUNTIME_QUEUE_ID = "uq_universal_runtime"

LEASE_FIELDS = (
    "lease_owner",
    "lease_id",
    "lease_started_at",
    "lease_expires_at",
)


class UniversalRuntimeRecoveryGatewayError(RuntimeError):
    pass


def _utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _evaluation_timestamp(
    value: datetime | str | None,
) -> str:
    if value is None:
        return _utc_now()

    if isinstance(value, datetime):
        if value.tzinfo is None:
            raise UniversalRuntimeRecoveryGatewayError(
                "evaluation_at must be timezone-aware."
            )

        return (
            value.astimezone(timezone.utc)
            .isoformat()
            .replace("+00:00", "Z")
        )

    normalized = str(value or "").strip()

    if not normalized:
        raise UniversalRuntimeRecoveryGatewayError(
            "evaluation_at must not be empty."
        )

    return normalized


def _metadata(job: Any) -> dict[str, Any]:
    value = getattr(job, "metadata", None)

    if not isinstance(value, Mapping):
        raise UniversalRuntimeRecoveryGatewayError(
            "Running job metadata must be a mapping."
        )

    return dict(value)


def _canonical_job(
    metadata: Mapping[str, Any],
) -> Mapping[str, Any]:
    direct = metadata.get(
        "canonical_universal_job"
    )

    if isinstance(direct, Mapping):
        return direct

    for value in metadata.values():
        if not isinstance(value, Mapping):
            continue

        candidate = value.get(
            "canonical_job"
        )

        if isinstance(candidate, Mapping):
            return candidate

    return {}


def _read_value(
    metadata: Mapping[str, Any],
    name: str,
    default: Any = None,
) -> Any:
    if name in metadata:
        return metadata[name]

    canonical_job = _canonical_job(
        metadata
    )

    return canonical_job.get(
        name,
        default,
    )


def _integer(
    value: Any,
    *,
    field_name: str,
    minimum: int,
) -> int:
    if isinstance(value, bool):
        raise UniversalRuntimeRecoveryGatewayError(
            f"{field_name} must be an integer."
        )

    try:
        normalized = int(value)
    except (TypeError, ValueError) as exc:
        raise UniversalRuntimeRecoveryGatewayError(
            f"{field_name} must be an integer."
        ) from exc

    if normalized < minimum:
        raise UniversalRuntimeRecoveryGatewayError(
            f"{field_name} must be at least {minimum}."
        )

    return normalized


def _attempt_context(
    metadata: Mapping[str, Any],
) -> tuple[int, int]:
    canonical_job = _canonical_job(
        metadata
    )

    previous_attempts = metadata.get(
        "runtime_failure_attempt_count",
        canonical_job.get(
            "attempts",
            0,
        ),
    )

    maximum_attempts = metadata.get(
        "runtime_maximum_attempts",
        canonical_job.get(
            "maximum_attempts",
            1,
        ),
    )

    previous = _integer(
        previous_attempts,
        field_name="attempts",
        minimum=0,
    )

    maximum = _integer(
        maximum_attempts,
        field_name="maximum_attempts",
        minimum=1,
    )

    interrupted_attempt = previous + 1

    return interrupted_attempt, maximum


def _duplicate_execution_safe(
    metadata: Mapping[str, Any],
) -> bool:
    explicit = _read_value(
        metadata,
        "duplicate_execution_safe",
        None,
    )

    if explicit is not None:
        if type(explicit) is not bool:
            raise UniversalRuntimeRecoveryGatewayError(
                "duplicate_execution_safe must be bool."
            )

        return explicit

    idempotency_key = str(
        _read_value(
            metadata,
            "idempotency_key",
            "",
        )
        or ""
    ).strip()

    return bool(idempotency_key)


def _queue_id(
    metadata: Mapping[str, Any],
) -> str:
    value = str(
        _read_value(
            metadata,
            "queue_id",
            DEFAULT_RUNTIME_QUEUE_ID,
        )
        or DEFAULT_RUNTIME_QUEUE_ID
    ).strip()

    if not value.startswith("uq_"):
        raise UniversalRuntimeRecoveryGatewayError(
            "Canonical queue_id must begin with 'uq_'."
        )

    return value


def _jsonable(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value

    to_dict = getattr(
        value,
        "to_dict",
        None,
    )

    if callable(to_dict):
        return _jsonable(
            to_dict()
        )

    if is_dataclass(value):
        return _jsonable(
            asdict(value)
        )

    if isinstance(value, Mapping):
        return {
            str(key): _jsonable(item)
            for key, item in value.items()
        }

    if isinstance(value, (tuple, list, set)):
        return [
            _jsonable(item)
            for item in value
        ]

    return value


def _previous_lease(
    metadata: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        field_name:
            metadata.get(field_name)
        for field_name in LEASE_FIELDS
    }


def _lease_from_metadata(
    *,
    job_id: str,
    metadata: Mapping[str, Any],
) -> UniversalWorkerLease:
    missing = [
        field_name
        for field_name in LEASE_FIELDS
        if not str(
            metadata.get(
                field_name,
                "",
            )
            or ""
        ).strip()
    ]

    if missing:
        raise UniversalRuntimeRecoveryGatewayError(
            "Running job is missing lease fields: "
            + ", ".join(missing)
        )

    if (
        metadata.get("lease_released") is True
        or metadata.get("lease_active") is False
    ):
        raise UniversalRuntimeRecoveryGatewayError(
            "RUNNING job contains released lease evidence."
        )

    return UniversalWorkerLease(
        job_id=job_id,
        lease_owner=str(
            metadata["lease_owner"]
        ),
        lease_id=str(
            metadata["lease_id"]
        ),
        lease_started_at=str(
            metadata["lease_started_at"]
        ),
        lease_expires_at=str(
            metadata["lease_expires_at"]
        ),
    )


def _released_lease_metadata(
    *,
    metadata: Mapping[str, Any],
    evaluation_at: str,
    recovery_result: Any,
    queue_recovery: Any,
    attempt_number: int,
    maximum_attempts: int,
) -> dict[str, Any]:
    return {
        "runtime_recovery_gateway_version":
            UNIVERSAL_RUNTIME_RECOVERY_GATEWAY_VERSION,

        "runtime_recovery_at":
            evaluation_at,

        "runtime_recovery_disposition":
            recovery_result.disposition.value,

        "runtime_recovery_reason":
            recovery_result.reason.value,

        "runtime_recovery_result":
            _jsonable(recovery_result),

        "runtime_queue_recovery":
            _jsonable(queue_recovery),

        "runtime_recovery_previous_lease":
            _previous_lease(metadata),

        "runtime_failure_attempt_count":
            attempt_number,

        "runtime_maximum_attempts":
            maximum_attempts,

        "runtime_retry_remaining":
            max(
                0,
                maximum_attempts
                - attempt_number,
            ),

        "runtime_retry_scheduled":
            True,

        "canonical_job_id_preserved":
            True,

        "recovery_created_new_job":
            False,

        "lease_owner":
            None,

        "lease_id":
            None,

        "lease_started_at":
            None,

        "lease_expires_at":
            None,

        "lease_active":
            False,

        "lease_released":
            True,

        "lease_released_at":
            evaluation_at,

        "lease_release_reason":
            "interrupted_execution_recovery",
    }


def _dead_letter_metadata(
    *,
    job: Any,
    metadata: Mapping[str, Any],
    evaluation_at: str,
    attempt_number: int,
    maximum_attempts: int,
    eligibility_basis: str,
    recovery_reason: str,
    recovery_result: Any = None,
    boundary_error: str | None = None,
) -> dict[str, Any]:
    evidence = create_universal_dead_letter_evidence(
        job_id=str(job.job_id),
        source_status=UniversalJobStatus.RUNNING,
        queue_id=_queue_id(metadata),
        partition_id=None,
        attempts=attempt_number,
        maximum_attempts=maximum_attempts,
        dead_letter_eligible=True,
        eligibility_basis=eligibility_basis,
        dead_letter_reason=recovery_reason,
        error_code="interrupted_execution",
        error_message=(
            "Interrupted execution cannot be recovered safely."
        ),
        error_details={
            "workspace_id":
                str(
                    getattr(
                        job,
                        "workspace_id",
                        "",
                    )
                ),

            "recovery_gateway_version":
                UNIVERSAL_RUNTIME_RECOVERY_GATEWAY_VERSION,

            "previous_lease":
                _previous_lease(metadata),

            "boundary_error":
                boundary_error,
        },
    )

    decision = evaluate_universal_dead_letter(
        evidence=evidence
    )

    if not decision.dead_letter_required:
        raise UniversalRuntimeRecoveryGatewayError(
            "Canonical Dead-Letter authority did not authorize "
            "the transition."
        )

    if decision.record is None:
        raise UniversalRuntimeRecoveryGatewayError(
            "Canonical Dead-Letter authority created no record."
        )

    return {
        "runtime_recovery_gateway_version":
            UNIVERSAL_RUNTIME_RECOVERY_GATEWAY_VERSION,

        "runtime_recovery_at":
            evaluation_at,

        "runtime_recovery_disposition":
            "NOT_RECOVERABLE",

        "runtime_recovery_reason":
            recovery_reason,

        "runtime_recovery_result":
            _jsonable(recovery_result),

        "runtime_recovery_boundary_error":
            boundary_error,

        "runtime_recovery_previous_lease":
            _previous_lease(metadata),

        "runtime_failure_attempt_count":
            attempt_number,

        "runtime_maximum_attempts":
            maximum_attempts,

        "runtime_retry_remaining":
            0,

        "runtime_retry_scheduled":
            False,

        "canonical_dead_letter_decision":
            _jsonable(decision),

        "canonical_dead_letter_record":
            _jsonable(decision.record),

        "canonical_dead_letter_status":
            UniversalJobStatus.DEAD_LETTER.value,

        "local_dead_letter_status":
            JOB_STATUS_FAILED,

        "canonical_job_id_preserved":
            True,

        "recovery_created_new_job":
            False,

        "lease_owner":
            None,

        "lease_id":
            None,

        "lease_started_at":
            None,

        "lease_expires_at":
            None,

        "lease_active":
            False,

        "lease_released":
            True,

        "lease_released_at":
            evaluation_at,

        "lease_release_reason":
            "interrupted_execution_not_recoverable",
    }


def recover_interrupted_runtime_jobs(
    *,
    evaluation_at: datetime | str | None = None,
) -> Mapping[str, Any]:
    canonical_evaluation_at = (
        _evaluation_timestamp(
            evaluation_at
        )
    )

    jobs = load_jobs()

    if not isinstance(jobs, Mapping):
        raise UniversalRuntimeRecoveryGatewayError(
            "Orchestration Job Store returned a non-mapping."
        )

    summary: dict[str, Any] = {
        "gateway_version":
            UNIVERSAL_RUNTIME_RECOVERY_GATEWAY_VERSION,

        "evaluation_at":
            canonical_evaluation_at,

        "running_jobs_checked":
            0,

        "active_leases_unchanged":
            0,

        "jobs_requeued":
            0,

        "jobs_dead_lettered":
            0,

        "requeued_job_ids":
            [],

        "dead_lettered_job_ids":
            [],
    }

    for job_id in sorted(jobs):
        job = jobs[job_id]

        if getattr(
            job,
            "status",
            None,
        ) != JOB_STATUS_RUNNING:
            continue

        summary[
            "running_jobs_checked"
        ] += 1

        metadata = _metadata(job)

        try:
            attempt_number, maximum_attempts = (
                _attempt_context(
                    metadata
                )
            )
        except UniversalRuntimeRecoveryGatewayError:
            attempt_number = 1
            maximum_attempts = 1

        try:
            lease = _lease_from_metadata(
                job_id=str(job.job_id),
                metadata=metadata,
            )

            lease_state = (
                evaluate_universal_worker_lease_state(
                    lease=lease,
                    evaluation_at=(
                        canonical_evaluation_at
                    ),
                )
            )

            retry_permitted = (
                attempt_number
                < maximum_attempts
            )

            duplicate_safe = (
                _duplicate_execution_safe(
                    metadata
                )
            )

            evidence = (
                create_universal_worker_recovery_evidence(
                    job_id=str(job.job_id),
                    job_status=UniversalJobStatus.LEASED,
                    worker_ownership_lost=(
                        lease_state
                        is UniversalWorkerLeaseState.EXPIRED
                    ),
                    retry_permitted=retry_permitted,
                    duplicate_execution_safe=duplicate_safe,
                    lease_state=lease_state,
                )
            )

            recovery_result = (
                evaluate_universal_worker_recovery(
                    evidence
                )
            )

            if (
                recovery_result.disposition
                is UniversalWorkerRecoveryDisposition.NO_ACTION
            ):
                summary[
                    "active_leases_unchanged"
                ] += 1
                continue

            if (
                recovery_result.disposition
                is UniversalWorkerRecoveryDisposition.RECOVERABLE
            ):
                queue_snapshot = (
                    create_universal_queue_recovery_snapshot(
                        job_id=str(job.job_id),
                        status=UniversalJobStatus.QUEUED,
                        queue_id=_queue_id(metadata),
                        partition_id=None,
                    )
                )

                queue_recovery = (
                    recover_universal_queue_membership(
                        snapshot=queue_snapshot
                    )
                )

                if (
                    not queue_recovery
                    .recoverable_queue_membership
                    or queue_recovery.mutation_required
                ):
                    raise UniversalRuntimeRecoveryGatewayError(
                        "Canonical Queue Recovery did not confirm "
                        "persisted QUEUED membership."
                    )

                recovered = update_job_status(
                    str(job.job_id),
                    JOB_STATUS_QUEUED,
                    metadata=_released_lease_metadata(
                        metadata=metadata,
                        evaluation_at=(
                            canonical_evaluation_at
                        ),
                        recovery_result=(
                            recovery_result
                        ),
                        queue_recovery=queue_recovery,
                        attempt_number=(
                            attempt_number
                        ),
                        maximum_attempts=(
                            maximum_attempts
                        ),
                    ),
                    error_message=None,
                )

                if recovered.job_id != job.job_id:
                    raise UniversalRuntimeRecoveryGatewayError(
                        "Recovery changed canonical job identity."
                    )

                if recovered.status != JOB_STATUS_QUEUED:
                    raise UniversalRuntimeRecoveryGatewayError(
                        "Recoverable job did not enter QUEUED."
                    )

                summary["jobs_requeued"] += 1
                summary["requeued_job_ids"].append(
                    str(job.job_id)
                )
                continue

            if (
                recovery_result.disposition
                is not
                UniversalWorkerRecoveryDisposition.NOT_RECOVERABLE
            ):
                raise UniversalRuntimeRecoveryGatewayError(
                    "Unsupported Worker Recovery disposition."
                )

            dead_letter_metadata = (
                _dead_letter_metadata(
                    job=job,
                    metadata=metadata,
                    evaluation_at=(
                        canonical_evaluation_at
                    ),
                    attempt_number=(
                        attempt_number
                    ),
                    maximum_attempts=(
                        maximum_attempts
                    ),
                    eligibility_basis=(
                        recovery_result.reason.value
                    ),
                    recovery_reason=(
                        "Canonical Worker Recovery classified "
                        "the interrupted execution as "
                        "NOT_RECOVERABLE."
                    ),
                    recovery_result=(
                        recovery_result
                    ),
                )
            )

            failed = update_job_status(
                str(job.job_id),
                JOB_STATUS_FAILED,
                metadata=dead_letter_metadata,
                error_message=(
                    "Interrupted execution is not recoverable."
                ),
            )

            if failed.job_id != job.job_id:
                raise UniversalRuntimeRecoveryGatewayError(
                    "Dead-letter mapping changed job identity."
                )

            if failed.status != JOB_STATUS_FAILED:
                raise UniversalRuntimeRecoveryGatewayError(
                    "Dead-letter mapping did not enter FAILED."
                )

            summary["jobs_dead_lettered"] += 1
            summary[
                "dead_lettered_job_ids"
            ].append(
                str(job.job_id)
            )

        except UniversalRuntimeRecoveryGatewayError as exc:
            dead_letter_metadata = (
                _dead_letter_metadata(
                    job=job,
                    metadata=metadata,
                    evaluation_at=(
                        canonical_evaluation_at
                    ),
                    attempt_number=(
                        attempt_number
                    ),
                    maximum_attempts=(
                        maximum_attempts
                    ),
                    eligibility_basis=(
                        "recovery_boundary_failed_closed"
                    ),
                    recovery_reason=(
                        "Interrupted execution recovery "
                        "evidence failed closed."
                    ),
                    boundary_error=str(exc),
                )
            )

            failed = update_job_status(
                str(job.job_id),
                JOB_STATUS_FAILED,
                metadata=dead_letter_metadata,
                error_message=(
                    "Interrupted execution evidence is "
                    "missing, malformed, or unsafe."
                ),
            )

            if failed.job_id != job.job_id:
                raise UniversalRuntimeRecoveryGatewayError(
                    "Fail-closed recovery changed job identity."
                )

            summary["jobs_dead_lettered"] += 1
            summary[
                "dead_lettered_job_ids"
            ].append(
                str(job.job_id)
            )

    summary["requeued_job_ids"] = tuple(
        summary["requeued_job_ids"]
    )

    summary["dead_lettered_job_ids"] = tuple(
        summary["dead_lettered_job_ids"]
    )

    return summary