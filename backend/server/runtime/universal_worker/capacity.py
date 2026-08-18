from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping

from backend.server.runtime.universal_worker.registration import (
    UniversalWorkerRegistration,
    normalize_universal_worker_id,
    normalize_universal_worker_instance_id,
    normalize_universal_worker_type,
)


UNIVERSAL_WORKER_CAPACITY_VERSION = (
    "universal_worker_capacity_v4.1.14"
)

UNIVERSAL_WORKER_CAPACITY_SNAPSHOT_SCHEMA_VERSION = (
    "universal_worker_capacity_snapshot_schema_v1"
)

MAX_UNIVERSAL_WORKER_CAPACITY_COUNT = 2_147_483_647

UNIVERSAL_WORKER_CAPACITY_IDENTITY_SEPARATOR = "::"


class UniversalWorkerCapacityError(
    ValueError
):

    def __init__(
        self,
        message: str,
        *,
        code: str,
        value: Any = None,
    ) -> None:

        super().__init__(
            message
        )

        self.code = str(
            code
        )

        self.value = value


def normalize_universal_worker_capacity_count(
    value: Any,
    *,
    field_name: str,
) -> int:

    if type(
        value
    ) is not int:

        raise UniversalWorkerCapacityError(
            (
                field_name
                + " must be an exact integer."
            ),
            code="invalid_worker_capacity_count",
            value=value,
        )

    if value < 0:

        raise UniversalWorkerCapacityError(
            (
                field_name
                + " must be greater than or equal to zero."
            ),
            code="invalid_worker_capacity_count",
            value=value,
        )

    if (
        value
        > MAX_UNIVERSAL_WORKER_CAPACITY_COUNT
    ):

        raise UniversalWorkerCapacityError(
            (
                field_name
                + " exceeds the supported worker "
                "capacity count."
            ),
            code="worker_capacity_count_too_large",
            value=value,
        )

    return value


def _normalize_worker_identity(
    *,
    worker_id: Any,
    worker_instance_id: Any,
    worker_type: Any,
) -> tuple[str, str, str]:

    try:

        normalized_worker_id = (
            normalize_universal_worker_id(
                worker_id
            )
        )

        normalized_instance_id = (
            normalize_universal_worker_instance_id(
                worker_instance_id
            )
        )

        normalized_worker_type = (
            normalize_universal_worker_type(
                worker_type
            )
        )

    except Exception as exc:

        raise UniversalWorkerCapacityError(
            (
                "Invalid canonical worker identity "
                "for Worker Capacity."
            ),
            code="invalid_worker_capacity_identity",
            value={
                "worker_id":
                    worker_id,

                "worker_instance_id":
                    worker_instance_id,

                "worker_type":
                    worker_type,
            },
        ) from exc

    return (
        normalized_worker_id,
        normalized_instance_id,
        normalized_worker_type,
    )


def _validate_registration(
    value: Any,
) -> UniversalWorkerRegistration:

    if not isinstance(
        value,
        UniversalWorkerRegistration,
    ):

        raise UniversalWorkerCapacityError(
            (
                "registration must be canonical "
                "UniversalWorkerRegistration."
            ),
            code="invalid_worker_capacity_registration",
            value=value,
        )

    return value


def calculate_universal_worker_available_capacity(
    *,
    capacity_limit: Any,
    active_work_count: Any,
) -> int:

    limit = (
        normalize_universal_worker_capacity_count(
            capacity_limit,
            field_name="capacity_limit",
        )
    )

    active = (
        normalize_universal_worker_capacity_count(
            active_work_count,
            field_name="active_work_count",
        )
    )

    if active > limit:

        raise UniversalWorkerCapacityError(
            (
                "active_work_count cannot exceed "
                "capacity_limit."
            ),
            code="worker_capacity_active_work_exceeds_limit",
            value={
                "capacity_limit":
                    limit,

                "active_work_count":
                    active,
            },
        )

    return (
        limit
        - active
    )


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalWorkerCapacitySnapshot:

    worker_id: str

    worker_instance_id: str

    worker_type: str

    capacity_limit: int

    active_work_count: int

    schema_version: str = (
        UNIVERSAL_WORKER_CAPACITY_SNAPSHOT_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        (
            worker_id,
            worker_instance_id,
            worker_type,
        ) = _normalize_worker_identity(
            worker_id=self.worker_id,
            worker_instance_id=self.worker_instance_id,
            worker_type=self.worker_type,
        )

        capacity_limit = (
            normalize_universal_worker_capacity_count(
                self.capacity_limit,
                field_name="capacity_limit",
            )
        )

        active_work_count = (
            normalize_universal_worker_capacity_count(
                self.active_work_count,
                field_name="active_work_count",
            )
        )

        calculate_universal_worker_available_capacity(
            capacity_limit=capacity_limit,
            active_work_count=active_work_count,
        )

        if (
            self.schema_version
            != UNIVERSAL_WORKER_CAPACITY_SNAPSHOT_SCHEMA_VERSION
        ):

            raise UniversalWorkerCapacityError(
                (
                    "Invalid Worker Capacity Snapshot "
                    "schema_version."
                ),
                code=(
                    "invalid_worker_capacity_"
                    "snapshot_schema_version"
                ),
                value=self.schema_version,
            )

        object.__setattr__(
            self,
            "worker_id",
            worker_id,
        )

        object.__setattr__(
            self,
            "worker_instance_id",
            worker_instance_id,
        )

        object.__setattr__(
            self,
            "worker_type",
            worker_type,
        )

        object.__setattr__(
            self,
            "capacity_limit",
            capacity_limit,
        )

        object.__setattr__(
            self,
            "active_work_count",
            active_work_count,
        )

    @property
    def worker_identity(
        self,
    ) -> str:

        return (
            self.worker_id
            + UNIVERSAL_WORKER_CAPACITY_IDENTITY_SEPARATOR
            + self.worker_instance_id
        )

    @property
    def available_capacity(
        self,
    ) -> int:

        return (
            self.capacity_limit
            - self.active_work_count
        )

    @property
    def has_available_capacity(
        self,
    ) -> bool:

        return (
            self.available_capacity
            > 0
        )

    @property
    def is_saturated(
        self,
    ) -> bool:

        return (
            self.available_capacity
            == 0
        )


def create_universal_worker_capacity_snapshot(
    *,
    registration: UniversalWorkerRegistration,
    capacity_limit: Any,
    active_work_count: Any,
) -> UniversalWorkerCapacitySnapshot:

    resolved_registration = (
        _validate_registration(
            registration
        )
    )

    return UniversalWorkerCapacitySnapshot(
        worker_id=(
            resolved_registration.worker_id
        ),
        worker_instance_id=(
            resolved_registration.worker_instance_id
        ),
        worker_type=(
            resolved_registration.worker_type
        ),
        capacity_limit=capacity_limit,
        active_work_count=active_work_count,
    )


def explain_universal_worker_capacity_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "4.1.14",

            "component":
                "Universal Worker Capacity Management",

            "version":
                UNIVERSAL_WORKER_CAPACITY_VERSION,

            "snapshot_schema_version":
                UNIVERSAL_WORKER_CAPACITY_SNAPSHOT_SCHEMA_VERSION,

            "scope_rule": (
                "4.1.14 owns immutable individual-worker "
                "generic work-slot capacity evidence"
            ),

            "identity_rule": (
                "Worker Capacity preserves canonical "
                "Worker Registration identity "
                "(worker_id, worker_instance_id)"
            ),

            "capacity_limit_rule": (
                "capacity_limit is caller-supplied maximum "
                "simultaneous capacity-consuming work units "
                "for this worker snapshot"
            ),

            "active_work_rule": (
                "active_work_count is caller-supplied "
                "already-composed capacity-consuming work "
                "evidence; 4.1.14 does not determine which "
                "job statuses count as active work"
            ),

            "available_capacity_rule": (
                "available_capacity equals capacity_limit "
                "minus active_work_count and can never "
                "be negative"
            ),

            "zero_capacity_rule": (
                "capacity_limit=0 with active_work_count=0 "
                "is valid and represents a saturated worker "
                "with zero available capacity"
            ),

            "contradiction_rule": (
                "active_work_count greater than "
                "capacity_limit is contradictory evidence "
                "and is rejected"
            ),

            "lease_boundary": (
                "active leases are separate ownership "
                "evidence and do not independently consume "
                "Worker Capacity inside 4.1.14"
            ),

            "assignment_boundary": (
                "capacity evidence does not perform Worker "
                "Assignment; callers may compose capacity "
                "before supplying eligible workers to 4.1.3"
            ),

            "scaling_boundary": (
                "4.1.14 does not scale workers; callers may "
                "aggregate Worker Capacity evidence into the "
                "caller-composed available_capacity consumed "
                "by 4.1.7 Worker Scaling"
            ),

            "runtime_concurrency_boundary": (
                "runtime/workspace max_concurrency settings "
                "are separate configuration/concurrency "
                "authorities and are not read by 4.1.14"
            ),

            "queue_capacity_boundary": (
                "3.1.11 Queue Capacity Limits is separate "
                "queue-depth admission authority"
            ),

            "capability_boundary": (
                "Worker Capability defines what a worker can "
                "perform; Worker Capacity defines how much "
                "capacity-consuming work it can accept"
            ),

            "drain_boundary": (
                "Worker Drain determines new-work acceptance; "
                "Capacity does not inspect or apply drain state"
            ),

            "resource_boundary": (
                "CPU, memory, GPU, throughput and resource "
                "scheduling are outside 4.1.14"
            ),

            "utilization_boundary": (
                "utilization and historical worker-load "
                "analytics remain observability concerns"
            ),

            "persistence_boundary": (
                "4.1.14 does not persist capacity state or "
                "access Runtime State Store"
            ),

            "purity_rule": (
                "Worker Capacity is deterministic over "
                "caller-supplied evidence and performs no "
                "external mutation, wall-clock access or I/O"
            ),

            "prohibitions": (
                "does not mutate Worker Registration",
                "does not inspect Worker Capability",
                "does not inspect Worker Pool membership",
                "does not inspect Worker Health",
                "does not inspect Stale Worker Detection",
                "does not inspect Worker Drain",
                "does not inspect active worker leases",
                "does not infer active work from leases",
                "does not acquire worker leases",
                "does not renew worker leases",
                "does not release worker leases",
                "does not perform Worker Assignment",
                "does not perform Worker Scaling",
                "does not perform Worker Shutdown",
                "does not initiate Worker Recovery",
                "does not read runtime max_concurrency",
                "does not read workspace concurrency policy",
                "does not calculate utilization",
                "does not calculate CPU capacity",
                "does not calculate memory capacity",
                "does not calculate GPU capacity",
                "does not enforce Queue Capacity Limits",
                "does not access Queue Infrastructure",
                "does not access orchestration",
                "does not access Runtime State Store",
                "does not persist capacity state",
                "does not maintain capacity history",
                "does not use wall clock",
                "does not perform filesystem I/O",
                "does not perform network I/O",
                "does not dispatch jobs",
                "does not execute jobs",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_WORKER_CAPACITY_VERSION",
    "UNIVERSAL_WORKER_CAPACITY_SNAPSHOT_SCHEMA_VERSION",
    "MAX_UNIVERSAL_WORKER_CAPACITY_COUNT",
    "UNIVERSAL_WORKER_CAPACITY_IDENTITY_SEPARATOR",
    "UniversalWorkerCapacityError",
    "UniversalWorkerCapacitySnapshot",
    "normalize_universal_worker_capacity_count",
    "calculate_universal_worker_available_capacity",
    "create_universal_worker_capacity_snapshot",
    "explain_universal_worker_capacity_v1",
]
