from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from socket import gethostname
from typing import Any, Iterable, Mapping

from backend.server.runtime.universal_worker.capacity import (
    calculate_universal_worker_available_capacity,
    create_universal_worker_capacity_snapshot,
)
from backend.server.runtime.universal_worker.health import (
    UniversalWorkerHealthState,
    create_universal_worker_health_evidence,
    evaluate_universal_worker_health,
)
from backend.server.runtime.universal_worker.heartbeat import (
    create_universal_worker_heartbeat,
)
from backend.server.runtime.universal_worker.registration import (
    create_universal_worker_registration,
)
from backend.server.runtime.universal_worker.assignment import (
    UniversalWorkerAssignmentStatus,
    assign_universal_worker,
)
from backend.server.runtime.universal_worker.leasing import (
    UniversalWorkerLease,
    acquire_universal_worker_lease,
    release_universal_worker_lease,
)
from backend.server.runtime.universal_worker.pool import (
    create_universal_worker_pool_from_registrations,
)


WORKER_LIFECYCLE_GATEWAY_VERSION = (
    "universal_worker_lifecycle_gateway_v1"
)


class UniversalWorkerLifecycleAdmissionError(RuntimeError):
    pass


def _utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )


def admit_universal_runtime_worker(
    *,
    worker_id: str,
    worker_instance_id: str | None = None,
    worker_type: str = "universal_runtime_worker",
    runtime_version: str,
    host_id: str | None = None,
    capabilities: Iterable[Any] = (),
    capacity_limit: int = 1,
    active_work_count: int = 0,
    heartbeat_sequence: int = 1,
) -> Mapping[str, Any]:
    instance_id = str(
        worker_instance_id or worker_id
    ).strip()

    canonical_host_id = str(
        host_id or gethostname()
    ).strip()

    now = _utc_now()

    registration = create_universal_worker_registration(
        worker_id=worker_id,
        worker_type=worker_type,
        worker_instance_id=instance_id,
        runtime_version=runtime_version,
        host_id=canonical_host_id,
        registered_at=now,
    )

    health_evidence = (
        create_universal_worker_health_evidence(
            health_check_passed=True,
            critical_failure_present=False,
            degraded_condition_present=False,
        )
    )

    health = evaluate_universal_worker_health(
        worker=registration,
        evidence=health_evidence,
    )

    if health.state is not UniversalWorkerHealthState.HEALTHY:
        raise UniversalWorkerLifecycleAdmissionError(
            "Worker is not healthy."
        )

    capacity = create_universal_worker_capacity_snapshot(
        registration=registration,
        capacity_limit=capacity_limit,
        active_work_count=active_work_count,
    )

    available_capacity = (
        calculate_universal_worker_available_capacity(
            capacity_limit=capacity.capacity_limit,
            active_work_count=capacity.active_work_count,
        )
    )

    if available_capacity < 1:
        raise UniversalWorkerLifecycleAdmissionError(
            "Worker has no available execution capacity."
        )

    heartbeat = create_universal_worker_heartbeat(
        registration=registration,
        heartbeat_at=now,
        sequence=heartbeat_sequence,
    )

    return {
        "gateway_version":
            WORKER_LIFECYCLE_GATEWAY_VERSION,

        "admitted":
            True,

        "registration":
            asdict(registration),

        "health":
            asdict(health),

        "heartbeat":
            asdict(heartbeat),

        "capacity":
            asdict(capacity),

        "available_capacity":
            available_capacity,

        "capabilities":
            tuple(
                str(item)
                for item in capabilities
            ),
    }


UNIVERSAL_RUNTIME_JOB_LEASE_GATEWAY_VERSION = (
    "universal_runtime_job_lease_gateway_v1"
)


class UniversalRuntimeJobLeaseGatewayError(RuntimeError):
    pass


def _worker_registration_from_mapping(
    value: Mapping[str, Any],
):
    if not isinstance(value, Mapping):
        raise UniversalRuntimeJobLeaseGatewayError(
            "Worker registration must be a mapping."
        )

    fields = (
        "worker_id",
        "worker_type",
        "worker_instance_id",
        "runtime_version",
        "host_id",
        "registered_at",
    )

    missing = [
        field
        for field in fields
        if not str(value.get(field, "") or "").strip()
    ]

    if missing:
        raise UniversalRuntimeJobLeaseGatewayError(
            "Worker registration is missing: "
            + ", ".join(missing)
        )

    return create_universal_worker_registration(
        worker_id=str(value["worker_id"]),
        worker_type=str(value["worker_type"]),
        worker_instance_id=str(
            value["worker_instance_id"]
        ),
        runtime_version=str(value["runtime_version"]),
        host_id=str(value["host_id"]),
        registered_at=str(value["registered_at"]),
    )


def prepare_universal_runtime_job_lease(
    *,
    job_id: str,
    registration: Mapping[str, Any],
    lease_seconds: int = 1800,
) -> Mapping[str, Any]:
    from datetime import timedelta
    from uuid import uuid4

    canonical_job_id = str(job_id or "").strip()

    if not canonical_job_id:
        raise UniversalRuntimeJobLeaseGatewayError(
            "job_id must not be empty."
        )

    if (
        isinstance(lease_seconds, bool)
        or not isinstance(lease_seconds, int)
        or lease_seconds < 1
    ):
        raise UniversalRuntimeJobLeaseGatewayError(
            "lease_seconds must be a positive integer."
        )

    worker = _worker_registration_from_mapping(
        registration
    )

    pool = create_universal_worker_pool_from_registrations(
        pool_id=(
            "universal_runtime_pool_"
            + worker.worker_type
        ),
        worker_type=worker.worker_type,
        registrations=(worker,),
    )

    if len(pool.members) != 1:
        raise UniversalRuntimeJobLeaseGatewayError(
            "Eligible worker pool is invalid."
        )

    assignment = assign_universal_worker(
        job_id=canonical_job_id,
        eligible_workers=(worker,),
    )

    if (
        assignment.status
        is not UniversalWorkerAssignmentStatus.ASSIGNED
        or assignment.worker is None
    ):
        raise UniversalRuntimeJobLeaseGatewayError(
            "No eligible worker was assigned."
        )

    now = datetime.now(timezone.utc)

    started = (
        now.isoformat()
        .replace("+00:00", "Z")
    )

    expires = (
        (
            now
            + timedelta(seconds=lease_seconds)
        )
        .isoformat()
        .replace("+00:00", "Z")
    )

    lease = acquire_universal_worker_lease(
        assignment=assignment,
        lease_id="lease_" + uuid4().hex,
        lease_started_at=started,
        lease_expires_at=expires,
        existing_lease=None,
    )

    if lease.job_id != canonical_job_id:
        raise UniversalRuntimeJobLeaseGatewayError(
            "Lease changed canonical job identity."
        )

    return {
        "job_id":
            canonical_job_id,

        "worker_assignment_status":
            str(
                getattr(
                    assignment.status,
                    "value",
                    assignment.status,
                )
            ),

        "worker_assignment_candidate_count":
            assignment.candidate_count,

        "assigned_worker_id":
            assignment.worker.worker_id,

        "assigned_worker_instance_id":
            assignment.worker.worker_instance_id,

        "worker_pool_id":
            pool.pool_id,

        "lease_owner":
            lease.lease_owner,

        "lease_id":
            lease.lease_id,

        "lease_started_at":
            lease.lease_started_at,

        "lease_expires_at":
            lease.lease_expires_at,

        "lease_active":
            True,

        "lease_released":
            False,

        "lease_gateway_version":
            UNIVERSAL_RUNTIME_JOB_LEASE_GATEWAY_VERSION,
    }


def release_universal_runtime_job_lease(
    *,
    job_id: str,
    metadata: Mapping[str, Any],
) -> Mapping[str, Any]:
    canonical_job_id = str(job_id or "").strip()

    if not canonical_job_id:
        raise UniversalRuntimeJobLeaseGatewayError(
            "job_id must not be empty."
        )

    if not isinstance(metadata, Mapping):
        raise UniversalRuntimeJobLeaseGatewayError(
            "Lease metadata must be a mapping."
        )

    fields = (
        "lease_owner",
        "lease_id",
        "lease_started_at",
        "lease_expires_at",
    )

    missing = [
        field
        for field in fields
        if not str(metadata.get(field, "") or "").strip()
    ]

    if missing:
        raise UniversalRuntimeJobLeaseGatewayError(
            "Claimed job is missing lease fields: "
            + ", ".join(missing)
        )

    lease = UniversalWorkerLease(
        job_id=canonical_job_id,
        lease_owner=str(metadata["lease_owner"]),
        lease_id=str(metadata["lease_id"]),
        lease_started_at=str(
            metadata["lease_started_at"]
        ),
        lease_expires_at=str(
            metadata["lease_expires_at"]
        ),
    )

    release = release_universal_worker_lease(
        lease=lease,
        expected_lease_owner=lease.lease_owner,
        expected_lease_id=lease.lease_id,
        released_at=_utc_now(),
    )

    if release.job_id != canonical_job_id:
        raise UniversalRuntimeJobLeaseGatewayError(
            "Lease release changed job identity."
        )

    return {
        "lease_owner":
            lease.lease_owner,

        "lease_id":
            lease.lease_id,

        "lease_started_at":
            lease.lease_started_at,

        "lease_expires_at":
            lease.lease_expires_at,

        "lease_released_at":
            release.released_at,

        "lease_active":
            False,

        "lease_released":
            True,

        "lease_release_gateway_version":
            UNIVERSAL_RUNTIME_JOB_LEASE_GATEWAY_VERSION,
    }

