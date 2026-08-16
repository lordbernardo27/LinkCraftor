from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from backend.server.runtime.universal_queue.creation import (
    UniversalQueueCreationError,
    normalize_universal_queue_id,
)

from backend.server.runtime.universal_queue.balancing import (
    UniversalQueueBalancingError,
    normalize_universal_queue_depth,
)


UNIVERSAL_QUEUE_CAPACITY_LIMITS_VERSION = (
    "universal_queue_capacity_limits_v3.1.11"
)

UNIVERSAL_QUEUE_CAPACITY_SNAPSHOT_SCHEMA_VERSION = (
    "universal_queue_capacity_snapshot_schema_v1"
)

UNIVERSAL_QUEUE_CAPACITY_DECISION_SCHEMA_VERSION = (
    "universal_queue_capacity_decision_schema_v1"
)


class UniversalQueueCapacityAdmission(
    str,
    Enum,
):

    ALLOW = "allow"
    DENY = "deny"


class UniversalQueueCapacityError(
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


def normalize_universal_queue_capacity_queue_id(
    value: Any,
) -> str:

    try:

        return normalize_universal_queue_id(
            value
        )

    except UniversalQueueCreationError as exc:

        raise UniversalQueueCapacityError(
            "Invalid canonical Universal Queue queue_id.",
            code="invalid_capacity_queue_id",
            value=value,
        ) from exc


def normalize_universal_queue_capacity_depth(
    value: Any,
) -> int:

    try:

        return normalize_universal_queue_depth(
            value
        )

    except UniversalQueueBalancingError as exc:

        raise UniversalQueueCapacityError(
            "queue_depth must be a non-negative integer.",
            code="invalid_capacity_queue_depth",
            value=value,
        ) from exc


def normalize_universal_queue_maximum_depth(
    value: Any,
) -> int:

    if (
        isinstance(
            value,
            bool,
        )
        or not isinstance(
            value,
            int,
        )
    ):

        raise UniversalQueueCapacityError(
            (
                "maximum_queue_depth must be "
                "a non-negative integer."
            ),
            code="invalid_maximum_queue_depth_type",
            value=value,
        )

    if value < 0:

        raise UniversalQueueCapacityError(
            "maximum_queue_depth must not be negative.",
            code="negative_maximum_queue_depth",
            value=value,
        )

    return value


def normalize_universal_queue_requested_admission_count(
    value: Any,
) -> int:

    if (
        isinstance(
            value,
            bool,
        )
        or not isinstance(
            value,
            int,
        )
    ):

        raise UniversalQueueCapacityError(
            (
                "requested_admission_count must be "
                "an integer >= 1."
            ),
            code="invalid_requested_admission_count_type",
            value=value,
        )

    if value < 1:

        raise UniversalQueueCapacityError(
            "requested_admission_count must be >= 1.",
            code="invalid_requested_admission_count",
            value=value,
        )

    return value


def normalize_universal_queue_capacity_admission(
    value: Any,
) -> UniversalQueueCapacityAdmission:

    if isinstance(
        value,
        UniversalQueueCapacityAdmission,
    ):

        return value

    if not isinstance(
        value,
        str,
    ):

        raise UniversalQueueCapacityError(
            "admission must be a supported string.",
            code="invalid_capacity_admission_type",
            value=value,
        )

    normalized = (
        value.strip().lower()
    )

    try:

        return UniversalQueueCapacityAdmission(
            normalized
        )

    except ValueError as exc:

        raise UniversalQueueCapacityError(
            "Unsupported capacity admission decision.",
            code="unsupported_capacity_admission",
            value=value,
        ) from exc


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalQueueCapacitySnapshot:

    queue_id: str
    queue_depth: int
    maximum_queue_depth: int
    requested_admission_count: int
    schema_version: str = (
        UNIVERSAL_QUEUE_CAPACITY_SNAPSHOT_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        set_ = object.__setattr__

        set_(
            self,
            "queue_id",
            normalize_universal_queue_capacity_queue_id(
                self.queue_id
            ),
        )

        set_(
            self,
            "queue_depth",
            normalize_universal_queue_capacity_depth(
                self.queue_depth
            ),
        )

        set_(
            self,
            "maximum_queue_depth",
            normalize_universal_queue_maximum_depth(
                self.maximum_queue_depth
            ),
        )

        set_(
            self,
            "requested_admission_count",
            normalize_universal_queue_requested_admission_count(
                self.requested_admission_count
            ),
        )

        if (
            self.schema_version
            != UNIVERSAL_QUEUE_CAPACITY_SNAPSHOT_SCHEMA_VERSION
        ):

            raise UniversalQueueCapacityError(
                "Invalid capacity snapshot schema_version.",
                code="invalid_capacity_snapshot_schema_version",
                value=self.schema_version,
            )

    @property
    def projected_queue_depth(
        self,
    ) -> int:

        return (
            self.queue_depth
            + self.requested_admission_count
        )

    @property
    def capacity_remaining_before(
        self,
    ) -> int:

        return max(
            0,
            self.maximum_queue_depth
            - self.queue_depth,
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "schema_version":
                self.schema_version,

            "queue_id":
                self.queue_id,

            "queue_depth":
                self.queue_depth,

            "maximum_queue_depth":
                self.maximum_queue_depth,

            "requested_admission_count":
                self.requested_admission_count,

            "projected_queue_depth":
                self.projected_queue_depth,

            "capacity_remaining_before":
                self.capacity_remaining_before,
        }


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalQueueCapacityDecision:

    queue_id: str
    queue_depth: int
    maximum_queue_depth: int
    requested_admission_count: int
    projected_queue_depth: int
    admission: UniversalQueueCapacityAdmission | str
    capacity_exceeded: bool
    mutation_required: bool
    reason: str
    schema_version: str = (
        UNIVERSAL_QUEUE_CAPACITY_DECISION_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        set_ = object.__setattr__

        queue_id = (
            normalize_universal_queue_capacity_queue_id(
                self.queue_id
            )
        )

        queue_depth = (
            normalize_universal_queue_capacity_depth(
                self.queue_depth
            )
        )

        maximum = (
            normalize_universal_queue_maximum_depth(
                self.maximum_queue_depth
            )
        )

        requested = (
            normalize_universal_queue_requested_admission_count(
                self.requested_admission_count
            )
        )

        projected = (
            normalize_universal_queue_capacity_depth(
                self.projected_queue_depth
            )
        )

        admission = (
            normalize_universal_queue_capacity_admission(
                self.admission
            )
        )

        if not isinstance(
            self.capacity_exceeded,
            bool,
        ):

            raise UniversalQueueCapacityError(
                "capacity_exceeded must be bool.",
                code="invalid_capacity_exceeded_flag",
                value=self.capacity_exceeded,
            )

        if not isinstance(
            self.mutation_required,
            bool,
        ):

            raise UniversalQueueCapacityError(
                "mutation_required must be bool.",
                code="invalid_capacity_mutation_flag",
                value=self.mutation_required,
            )

        if self.mutation_required is not False:

            raise UniversalQueueCapacityError(
                (
                    "3.1.11 makes an admission decision "
                    "but does not mutate queue state."
                ),
                code="capacity_queue_mutation_not_owned",
                value=self.mutation_required,
            )

        if not isinstance(
            self.reason,
            str,
        ):

            raise UniversalQueueCapacityError(
                "reason must be a string.",
                code="invalid_capacity_reason_type",
                value=self.reason,
            )

        reason = (
            self.reason.strip()
        )

        if not reason:

            raise UniversalQueueCapacityError(
                "reason must not be blank.",
                code="blank_capacity_reason",
                value=self.reason,
            )

        expected_projected = (
            queue_depth
            + requested
        )

        if projected != expected_projected:

            raise UniversalQueueCapacityError(
                (
                    "projected_queue_depth is inconsistent "
                    "with queue_depth and requested_admission_count."
                ),
                code="inconsistent_projected_queue_depth",
                value=projected,
            )

        expected_exceeded = (
            projected > maximum
        )

        expected_admission = (
            UniversalQueueCapacityAdmission.DENY
            if expected_exceeded
            else UniversalQueueCapacityAdmission.ALLOW
        )

        if (
            self.capacity_exceeded
            is not expected_exceeded
        ):

            raise UniversalQueueCapacityError(
                "capacity_exceeded is inconsistent.",
                code="inconsistent_capacity_exceeded",
                value=self.capacity_exceeded,
            )

        if admission is not expected_admission:

            raise UniversalQueueCapacityError(
                (
                    "admission is inconsistent with "
                    "the canonical capacity rule."
                ),
                code="inconsistent_capacity_admission",
                value=admission.value,
            )

        set_(
            self,
            "queue_id",
            queue_id,
        )

        set_(
            self,
            "queue_depth",
            queue_depth,
        )

        set_(
            self,
            "maximum_queue_depth",
            maximum,
        )

        set_(
            self,
            "requested_admission_count",
            requested,
        )

        set_(
            self,
            "projected_queue_depth",
            projected,
        )

        set_(
            self,
            "admission",
            admission,
        )

        set_(
            self,
            "reason",
            reason,
        )

        if (
            self.schema_version
            != UNIVERSAL_QUEUE_CAPACITY_DECISION_SCHEMA_VERSION
        ):

            raise UniversalQueueCapacityError(
                "Invalid capacity decision schema_version.",
                code="invalid_capacity_decision_schema_version",
                value=self.schema_version,
            )

    @property
    def capacity_remaining_before(
        self,
    ) -> int:

        return max(
            0,
            self.maximum_queue_depth
            - self.queue_depth,
        )

    @property
    def capacity_remaining_after(
        self,
    ) -> int:

        if self.capacity_exceeded:

            return (
                self.capacity_remaining_before
            )

        return (
            self.maximum_queue_depth
            - self.projected_queue_depth
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "schema_version":
                self.schema_version,

            "queue_id":
                self.queue_id,

            "queue_depth":
                self.queue_depth,

            "maximum_queue_depth":
                self.maximum_queue_depth,

            "requested_admission_count":
                self.requested_admission_count,

            "projected_queue_depth":
                self.projected_queue_depth,

            "capacity_remaining_before":
                self.capacity_remaining_before,

            "capacity_remaining_after":
                self.capacity_remaining_after,

            "admission":
                self.admission.value,

            "capacity_exceeded":
                self.capacity_exceeded,

            "mutation_required":
                self.mutation_required,

            "reason":
                self.reason,
        }


def create_universal_queue_capacity_snapshot(
    *,
    queue_id: str,
    queue_depth: int,
    maximum_queue_depth: int,
    requested_admission_count: int,
) -> UniversalQueueCapacitySnapshot:

    return UniversalQueueCapacitySnapshot(
        queue_id=queue_id,
        queue_depth=queue_depth,
        maximum_queue_depth=maximum_queue_depth,
        requested_admission_count=requested_admission_count,
    )


def evaluate_universal_queue_capacity(
    *,
    snapshot: UniversalQueueCapacitySnapshot,
) -> UniversalQueueCapacityDecision:

    if not isinstance(
        snapshot,
        UniversalQueueCapacitySnapshot,
    ):

        raise UniversalQueueCapacityError(
            (
                "snapshot must be a "
                "UniversalQueueCapacitySnapshot instance."
            ),
            code="invalid_capacity_snapshot",
            value=snapshot,
        )

    projected = (
        snapshot.projected_queue_depth
    )

    exceeded = (
        projected
        > snapshot.maximum_queue_depth
    )

    if exceeded:

        admission = (
            UniversalQueueCapacityAdmission.DENY
        )

        reason = (
            "projected_queue_depth_exceeds_capacity"
        )

    else:

        admission = (
            UniversalQueueCapacityAdmission.ALLOW
        )

        reason = (
            "projected_queue_depth_within_capacity"
        )

    return UniversalQueueCapacityDecision(
        queue_id=snapshot.queue_id,
        queue_depth=snapshot.queue_depth,
        maximum_queue_depth=snapshot.maximum_queue_depth,
        requested_admission_count=snapshot.requested_admission_count,
        projected_queue_depth=projected,
        admission=admission,
        capacity_exceeded=exceeded,
        mutation_required=False,
        reason=reason,
    )


def explain_universal_queue_capacity_limits_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "3.1.11",

            "component":
                "Universal Queue Capacity Limits",

            "version":
                UNIVERSAL_QUEUE_CAPACITY_LIMITS_VERSION,

            "snapshot_schema":
                UNIVERSAL_QUEUE_CAPACITY_SNAPSHOT_SCHEMA_VERSION,

            "decision_schema":
                UNIVERSAL_QUEUE_CAPACITY_DECISION_SCHEMA_VERSION,

            "scope":
                "LinkCraftor-wide",

            "canonical_capacity_signal":
                "queue_depth",

            "snapshot_rule": (
                "queue_depth, maximum_queue_depth and "
                "requested_admission_count are caller-supplied; "
                "3.1.11 does not read live queue state"
            ),

            "maximum_capacity_rule": (
                "maximum_queue_depth is explicit hard capacity "
                "policy and may be zero"
            ),

            "requested_admission_rule": (
                "requested_admission_count is always explicit "
                "and must be an integer >= 1"
            ),

            "projected_depth_rule": (
                "projected_queue_depth equals queue_depth plus "
                "requested_admission_count"
            ),

            "admission_rule": (
                "projected_queue_depth <= maximum_queue_depth "
                "is ALLOW; projected_queue_depth greater than "
                "maximum_queue_depth is DENY"
            ),

            "equality_rule": (
                "an admission that exactly fills capacity is ALLOW"
            ),

            "enforcement_rule": (
                "ALLOW and DENY are authoritative logical queue "
                "capacity admission decisions; actual enqueue or "
                "API rejection is performed by downstream callers"
            ),

            "backpressure_boundary": (
                "pressure classification and DEFER guidance belong "
                "to 3.1.10 Queue Backpressure"
            ),

            "fairness_boundary": (
                "fairness and starvation policy belong to "
                "3.1.12 Queue Fairness"
            ),

            "rate_limit_boundary": (
                "rate-based admission policy belongs to "
                "3.1.13 Queue Rate Limiting"
            ),

            "quota_boundary": (
                "billing quotas, subscription limits, product "
                "limits and Batch Upload limits are outside "
                "Universal Queue Capacity Limits"
            ),

            "worker_boundary": (
                "worker concurrency, worker scaling and worker "
                "capacity remain Worker Infrastructure concerns"
            ),

            "physical_capacity_boundary": (
                "broker, Redis, database, filesystem and cloud "
                "service physical capacity remain backend/"
                "infrastructure concerns"
            ),

            "prohibitions": (
                "does not create Universal Queues",
                "does not create Universal Jobs",
                "does not mutate Universal Jobs",
                "does not mutate queues",
                "does not enqueue jobs",
                "does not dequeue jobs",
                "does not claim jobs",
                "does not requeue jobs",
                "does not read live queue state",
                "does not access orchestration",
                "does not access the Job Store",
                "does not access Runtime State Store",
                "does not perform API rejection",
                "does not return HTTP 429",
                "does not calculate Retry-After",
                "does not implement rate limiting",
                "does not implement Queue Backpressure",
                "does not pause producers",
                "does not throttle producers",
                "does not sleep or delay execution",
                "does not implement queue fairness",
                "does not implement priority aging",
                "does not apply billing quotas",
                "does not apply subscription limits",
                "does not apply Batch Upload limits",
                "does not scale workers",
                "does not select workers",
                "does not inspect worker capability",
                "does not enforce physical broker capacity",
                "does not create physical queues",
                "does not perform filesystem I/O",
                "does not perform network I/O",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_QUEUE_CAPACITY_LIMITS_VERSION",
    "UNIVERSAL_QUEUE_CAPACITY_SNAPSHOT_SCHEMA_VERSION",
    "UNIVERSAL_QUEUE_CAPACITY_DECISION_SCHEMA_VERSION",
    "UniversalQueueCapacityAdmission",
    "UniversalQueueCapacityError",
    "UniversalQueueCapacitySnapshot",
    "UniversalQueueCapacityDecision",
    "normalize_universal_queue_capacity_queue_id",
    "normalize_universal_queue_capacity_depth",
    "normalize_universal_queue_maximum_depth",
    "normalize_universal_queue_requested_admission_count",
    "normalize_universal_queue_capacity_admission",
    "create_universal_queue_capacity_snapshot",
    "evaluate_universal_queue_capacity",
    "explain_universal_queue_capacity_limits_v1",
]
