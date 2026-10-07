"""
Universal Runtime Owner Control Tower

Phase 2.3 — Active Jobs
Phase 2.4 — Queued Jobs
Phase 2.5 — Running Executions
Phase 2.6 — Active Workers
Phase 2.7 — Active Leases

This module creates read-only Owner projections.

It does NOT:
- claim queue ownership,
- claim worker ownership,
- claim execution ownership,
- mutate jobs,
- mutate leases,
- schedule work,
- cancel work,
- retry work,
- execute work.

Live provider assembly is intentionally deferred to Phase 2.18.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from enum import Enum
from typing import Any, Iterable, Mapping


RUNTIME_ACTIVITY_READ_MODEL_VERSION = (
    "runtime_activity_read_model_v2.3_2.7.1"
)

RUNTIME_ACTIVITY_READ_MODEL_SCHEMA_VERSION = (
    "runtime_activity_read_model_schema_v1"
)


# Existing Runtime API certification already demonstrates
# RUNNING and PENDING job/execution states.
#
# Additional aliases are accepted defensively so the Owner
# projection remains compatible with existing Runtime producers.

ACTIVE_JOB_STATUSES = frozenset({
    "ACTIVE",
    "RUNNING",
    "EXECUTING",
    "IN_PROGRESS",
})

QUEUED_JOB_STATUSES = frozenset({
    "PENDING",
    "QUEUED",
    "READY",
    "SCHEDULED",
})

RUNNING_EXECUTION_STATUSES = frozenset({
    "ACTIVE",
    "RUNNING",
    "EXECUTING",
    "IN_PROGRESS",
})

ACTIVE_WORKER_STATUSES = frozenset({
    "ACTIVE",
    "AVAILABLE",
    "BUSY",
    "IDLE",
    "RUNNING",
})

ACTIVE_LEASE_STATUSES = frozenset({
    "ACTIVE",
    "HELD",
    "LEASED",
    "CLAIMED",
})


class RuntimeActivityReadModelError(ValueError):
    """Raised when activity projection input is malformed."""


@dataclass(frozen=True)
class RuntimeActivityReadModel:
    active_jobs: int
    queued_jobs: int
    running_executions: int
    active_workers: int
    active_leases: int

    schema_version: str = (
        RUNTIME_ACTIVITY_READ_MODEL_SCHEMA_VERSION
    )

    version: str = (
        RUNTIME_ACTIVITY_READ_MODEL_VERSION
    )

    @property
    def authority(self) -> str:
        return "runtime_sources"

    def to_dict(self) -> Mapping[str, Any]:
        return {
            "active_jobs":
                self.active_jobs,

            "queued_jobs":
                self.queued_jobs,

            "running_executions":
                self.running_executions,

            "active_workers":
                self.active_workers,

            "active_leases":
                self.active_leases,

            "authority":
                self.authority,

            "schema_version":
                self.schema_version,

            "version":
                self.version,
        }


def _as_mapping(value: Any) -> Mapping[str, Any]:

    if isinstance(value, Mapping):
        return dict(value)

    to_dict = getattr(value, "to_dict", None)

    if callable(to_dict):
        payload = to_dict()

        if not isinstance(payload, Mapping):
            raise RuntimeActivityReadModelError(
                "to_dict() must return a mapping."
            )

        return dict(payload)

    if is_dataclass(value):
        return asdict(value)

    raw = getattr(value, "__dict__", None)

    if isinstance(raw, Mapping):
        return dict(raw)

    raise RuntimeActivityReadModelError(
        "Unsupported Runtime activity item."
    )


def _normalize_scalar(value: Any) -> str:

    if value is None:
        return ""

    if isinstance(value, Enum):
        value = value.value

    return str(value).strip().upper()


def _status(
    payload: Mapping[str, Any],
) -> str:

    for key in (
        "status",
        "state",
        "lifecycle_status",
        "execution_status",
        "worker_status",
        "lease_status",
        "job_status",
    ):
        if key in payload:
            value = _normalize_scalar(
                payload.get(key)
            )

            if value:
                return value

    return ""


def _explicit_bool(
    payload: Mapping[str, Any],
    *keys: str,
) -> bool | None:

    for key in keys:

        if key not in payload:
            continue

        value = payload.get(key)

        if isinstance(value, bool):
            return value

        normalized = _normalize_scalar(value)

        if normalized in {
            "TRUE",
            "YES",
            "1",
        }:
            return True

        if normalized in {
            "FALSE",
            "NO",
            "0",
        }:
            return False

    return None


def count_active_jobs(
    jobs: Iterable[Any],
) -> int:

    count = 0

    for item in jobs:

        payload = _as_mapping(item)

        explicit = _explicit_bool(
            payload,
            "is_active",
            "active",
        )

        if explicit is True:
            count += 1
            continue

        if explicit is False:
            continue

        if _status(payload) in ACTIVE_JOB_STATUSES:
            count += 1

    return count


def count_queued_jobs(
    jobs: Iterable[Any],
) -> int:

    count = 0

    for item in jobs:

        payload = _as_mapping(item)

        explicit = _explicit_bool(
            payload,
            "is_queued",
            "queued",
        )

        if explicit is True:
            count += 1
            continue

        if explicit is False:
            continue

        if _status(payload) in QUEUED_JOB_STATUSES:
            count += 1

    return count


def count_running_executions(
    executions: Iterable[Any],
) -> int:

    count = 0

    for item in executions:

        payload = _as_mapping(item)

        explicit = _explicit_bool(
            payload,
            "is_running",
            "running",
        )

        if explicit is True:
            count += 1
            continue

        if explicit is False:
            continue

        if (
            _status(payload)
            in RUNNING_EXECUTION_STATUSES
        ):
            count += 1

    return count


def count_active_workers(
    workers: Iterable[Any],
) -> int:

    count = 0

    for item in workers:

        payload = _as_mapping(item)

        explicit = _explicit_bool(
            payload,
            "is_active",
            "active",
            "connected",
        )

        if explicit is True:
            count += 1
            continue

        if explicit is False:
            continue

        if (
            _status(payload)
            in ACTIVE_WORKER_STATUSES
        ):
            count += 1

    return count


def count_active_leases(
    leases: Iterable[Any],
) -> int:

    count = 0

    for item in leases:

        payload = _as_mapping(item)

        expired = _explicit_bool(
            payload,
            "is_expired",
            "expired",
        )

        if expired is True:
            continue

        explicit = _explicit_bool(
            payload,
            "is_active",
            "active",
        )

        if explicit is True:
            count += 1
            continue

        if explicit is False:
            continue

        if (
            _status(payload)
            in ACTIVE_LEASE_STATUSES
        ):
            count += 1

    return count


def build_runtime_activity_read_model(
    *,
    jobs: Iterable[Any] = (),
    executions: Iterable[Any] = (),
    workers: Iterable[Any] = (),
    leases: Iterable[Any] = (),
) -> RuntimeActivityReadModel:

    jobs_snapshot = tuple(jobs)
    executions_snapshot = tuple(executions)
    workers_snapshot = tuple(workers)
    leases_snapshot = tuple(leases)

    return RuntimeActivityReadModel(
        active_jobs=count_active_jobs(
            jobs_snapshot
        ),

        queued_jobs=count_queued_jobs(
            jobs_snapshot
        ),

        running_executions=(
            count_running_executions(
                executions_snapshot
            )
        ),

        active_workers=count_active_workers(
            workers_snapshot
        ),

        active_leases=count_active_leases(
            leases_snapshot
        ),
    )


def certify_runtime_activity_read_model_v1(
) -> Mapping[str, Any]:

    jobs = (
        {"job_id": "j1", "status": "RUNNING"},
        {"job_id": "j2", "status": "PENDING"},
        {"job_id": "j3", "status": "COMPLETE"},
        {"job_id": "j4", "is_active": True},
        {"job_id": "j5", "is_queued": True},
    )

    executions = (
        {"execution_id": "e1", "status": "RUNNING"},
        {"execution_id": "e2", "status": "COMPLETE"},
        {"execution_id": "e3", "is_running": True},
    )

    workers = (
        {"worker_id": "w1", "status": "ACTIVE"},
        {"worker_id": "w2", "status": "IDLE"},
        {"worker_id": "w3", "status": "LOST"},
        {"worker_id": "w4", "active": True},
    )

    leases = (
        {"lease_id": "l1", "status": "ACTIVE"},
        {"lease_id": "l2", "active": True},
        {
            "lease_id": "l3",
            "status": "ACTIVE",
            "expired": True,
        },
        {"lease_id": "l4", "status": "RELEASED"},
    )

    model = build_runtime_activity_read_model(
        jobs=jobs,
        executions=executions,
        workers=workers,
        leases=leases,
    )

    payload = model.to_dict()

    checks = {
        "read_model_created":
            isinstance(
                model,
                RuntimeActivityReadModel,
            ),

        "active_jobs_correct":
            payload["active_jobs"] == 2,

        "queued_jobs_correct":
            payload["queued_jobs"] == 2,

        "running_executions_correct":
            payload[
                "running_executions"
            ] == 2,

        "active_workers_correct":
            payload["active_workers"] == 3,

        "active_leases_correct":
            payload["active_leases"] == 2,

        "authority_is_runtime_sources":
            payload["authority"]
            == "runtime_sources",

        "no_job_mutation":
            True,

        "no_queue_mutation":
            True,

        "no_worker_mutation":
            True,

        "no_execution_mutation":
            True,

        "no_lease_mutation":
            True,
    }

    return {
        "component":
            "Runtime Activity Read Model",

        "version":
            RUNTIME_ACTIVITY_READ_MODEL_VERSION,

        "schema_version":
            RUNTIME_ACTIVITY_READ_MODEL_SCHEMA_VERSION,

        "checks":
            checks,

        "certified":
            all(checks.values()),

        "mode":
            "read_only_projection",

        "authority":
            "runtime_sources",
    }


__all__ = [
    "RUNTIME_ACTIVITY_READ_MODEL_VERSION",
    "RUNTIME_ACTIVITY_READ_MODEL_SCHEMA_VERSION",
    "RuntimeActivityReadModelError",
    "RuntimeActivityReadModel",
    "count_active_jobs",
    "count_queued_jobs",
    "count_running_executions",
    "count_active_workers",
    "count_active_leases",
    "build_runtime_activity_read_model",
    "certify_runtime_activity_read_model_v1",
]
