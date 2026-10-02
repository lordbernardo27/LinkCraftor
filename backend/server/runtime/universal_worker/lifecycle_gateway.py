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
