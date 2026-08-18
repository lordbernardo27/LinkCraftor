from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping


UNIVERSAL_WORKER_SCALING_VERSION = (
    "universal_worker_scaling_v4.1.7"
)

UNIVERSAL_WORKER_SCALING_EVIDENCE_SCHEMA_VERSION = (
    "universal_worker_scaling_evidence_schema_v1"
)

UNIVERSAL_WORKER_SCALING_RESULT_SCHEMA_VERSION = (
    "universal_worker_scaling_result_schema_v1"
)

MAX_UNIVERSAL_WORKER_COUNT = 1_000_000
MAX_UNIVERSAL_WORKER_SCALING_WORK_COUNT = 2_147_483_647


class UniversalWorkerScalingError(
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


class UniversalWorkerScalingDecision(
    str,
    Enum,
):

    SCALE_UP = "SCALE_UP"
    HOLD = "HOLD"
    SCALE_DOWN = "SCALE_DOWN"


class UniversalWorkerScalingReason(
    str,
    Enum,
):

    BELOW_MINIMUM = "BELOW_MINIMUM"

    ABOVE_MAXIMUM = "ABOVE_MAXIMUM"

    ABOVE_MAXIMUM_BUT_SCALE_DOWN_UNSAFE = (
        "ABOVE_MAXIMUM_BUT_SCALE_DOWN_UNSAFE"
    )

    DEMAND_EXCEEDS_AVAILABLE_CAPACITY = (
        "DEMAND_EXCEEDS_AVAILABLE_CAPACITY"
    )

    MAXIMUM_REACHED = "MAXIMUM_REACHED"

    ZERO_DEMAND_SCALE_DOWN_SAFE = (
        "ZERO_DEMAND_SCALE_DOWN_SAFE"
    )

    ZERO_DEMAND_SCALE_DOWN_UNSAFE = (
        "ZERO_DEMAND_SCALE_DOWN_UNSAFE"
    )

    MINIMUM_REACHED = "MINIMUM_REACHED"

    AVAILABLE_CAPACITY_SUFFICIENT = (
        "AVAILABLE_CAPACITY_SUFFICIENT"
    )


def _validate_non_negative_int(
    value: Any,
    *,
    field_name: str,
    maximum: int,
) -> int:

    if (
        type(value) is not int
        or
        value < 0
    ):

        raise UniversalWorkerScalingError(
            (
                field_name
                + " must be a non-negative integer."
            ),
            code="invalid_worker_scaling_integer",
            value={
                "field_name":
                    field_name,

                "value":
                    value,
            },
        )

    if value > maximum:

        raise UniversalWorkerScalingError(
            (
                field_name
                + " exceeds the supported maximum."
            ),
            code="worker_scaling_integer_too_large",
            value={
                "field_name":
                    field_name,

                "value":
                    value,

                "maximum":
                    maximum,
            },
        )

    return value


def _validate_strict_bool(
    value: Any,
    *,
    field_name: str,
) -> bool:

    if type(value) is not bool:

        raise UniversalWorkerScalingError(
            (
                field_name
                + " must be bool."
            ),
            code="invalid_worker_scaling_boolean",
            value={
                "field_name":
                    field_name,

                "value":
                    value,
            },
        )

    return value


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalWorkerScalingEvidence:

    current_worker_count: int

    minimum_worker_count: int

    maximum_worker_count: int

    pending_work: int

    available_capacity: int

    scale_down_safe: bool

    schema_version: str = (
        UNIVERSAL_WORKER_SCALING_EVIDENCE_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        object.__setattr__(
            self,
            "current_worker_count",
            _validate_non_negative_int(
                self.current_worker_count,
                field_name="current_worker_count",
                maximum=MAX_UNIVERSAL_WORKER_COUNT,
            ),
        )

        object.__setattr__(
            self,
            "minimum_worker_count",
            _validate_non_negative_int(
                self.minimum_worker_count,
                field_name="minimum_worker_count",
                maximum=MAX_UNIVERSAL_WORKER_COUNT,
            ),
        )

        object.__setattr__(
            self,
            "maximum_worker_count",
            _validate_non_negative_int(
                self.maximum_worker_count,
                field_name="maximum_worker_count",
                maximum=MAX_UNIVERSAL_WORKER_COUNT,
            ),
        )

        object.__setattr__(
            self,
            "pending_work",
            _validate_non_negative_int(
                self.pending_work,
                field_name="pending_work",
                maximum=(
                    MAX_UNIVERSAL_WORKER_SCALING_WORK_COUNT
                ),
            ),
        )

        object.__setattr__(
            self,
            "available_capacity",
            _validate_non_negative_int(
                self.available_capacity,
                field_name="available_capacity",
                maximum=(
                    MAX_UNIVERSAL_WORKER_SCALING_WORK_COUNT
                ),
            ),
        )

        object.__setattr__(
            self,
            "scale_down_safe",
            _validate_strict_bool(
                self.scale_down_safe,
                field_name="scale_down_safe",
            ),
        )

        if (
            self.minimum_worker_count
            > self.maximum_worker_count
        ):

            raise UniversalWorkerScalingError(
                (
                    "minimum_worker_count must not "
                    "exceed maximum_worker_count."
                ),
                code="invalid_worker_scaling_bounds",
                value={
                    "minimum_worker_count":
                        self.minimum_worker_count,

                    "maximum_worker_count":
                        self.maximum_worker_count,
                },
            )

        if (
            self.schema_version
            != UNIVERSAL_WORKER_SCALING_EVIDENCE_SCHEMA_VERSION
        ):

            raise UniversalWorkerScalingError(
                (
                    "Invalid Worker Scaling Evidence "
                    "schema_version."
                ),
                code=(
                    "invalid_worker_scaling_"
                    "evidence_schema_version"
                ),
                value=self.schema_version,
            )


def decide_universal_worker_scaling(
    evidence: UniversalWorkerScalingEvidence,
) -> tuple[
    UniversalWorkerScalingDecision,
    UniversalWorkerScalingReason,
    int,
]:

    if not isinstance(
        evidence,
        UniversalWorkerScalingEvidence,
    ):

        raise UniversalWorkerScalingError(
            (
                "evidence must be "
                "UniversalWorkerScalingEvidence."
            ),
            code="invalid_worker_scaling_evidence",
            value=evidence,
        )

    current = (
        evidence.current_worker_count
    )

    minimum = (
        evidence.minimum_worker_count
    )

    maximum = (
        evidence.maximum_worker_count
    )

    if current < minimum:

        return (
            UniversalWorkerScalingDecision.SCALE_UP,
            UniversalWorkerScalingReason.BELOW_MINIMUM,
            minimum,
        )

    if current > maximum:

        if evidence.scale_down_safe:

            return (
                UniversalWorkerScalingDecision.SCALE_DOWN,
                UniversalWorkerScalingReason.ABOVE_MAXIMUM,
                maximum,
            )

        return (
            UniversalWorkerScalingDecision.HOLD,
            (
                UniversalWorkerScalingReason
                .ABOVE_MAXIMUM_BUT_SCALE_DOWN_UNSAFE
            ),
            current,
        )

    if (
        evidence.pending_work
        > evidence.available_capacity
    ):

        if current < maximum:

            return (
                UniversalWorkerScalingDecision.SCALE_UP,
                (
                    UniversalWorkerScalingReason
                    .DEMAND_EXCEEDS_AVAILABLE_CAPACITY
                ),
                current + 1,
            )

        return (
            UniversalWorkerScalingDecision.HOLD,
            UniversalWorkerScalingReason.MAXIMUM_REACHED,
            current,
        )

    if evidence.pending_work == 0:

        if current <= minimum:

            return (
                UniversalWorkerScalingDecision.HOLD,
                UniversalWorkerScalingReason.MINIMUM_REACHED,
                current,
            )

        if evidence.scale_down_safe:

            return (
                UniversalWorkerScalingDecision.SCALE_DOWN,
                (
                    UniversalWorkerScalingReason
                    .ZERO_DEMAND_SCALE_DOWN_SAFE
                ),
                current - 1,
            )

        return (
            UniversalWorkerScalingDecision.HOLD,
            (
                UniversalWorkerScalingReason
                .ZERO_DEMAND_SCALE_DOWN_UNSAFE
            ),
            current,
        )

    return (
        UniversalWorkerScalingDecision.HOLD,
        (
            UniversalWorkerScalingReason
            .AVAILABLE_CAPACITY_SUFFICIENT
        ),
        current,
    )


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalWorkerScalingResult:

    decision: UniversalWorkerScalingDecision

    reason: UniversalWorkerScalingReason

    current_worker_count: int

    desired_worker_count: int

    minimum_worker_count: int

    maximum_worker_count: int

    pending_work: int

    available_capacity: int

    scale_down_safe: bool

    schema_version: str = (
        UNIVERSAL_WORKER_SCALING_RESULT_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        if not isinstance(
            self.decision,
            UniversalWorkerScalingDecision,
        ):

            raise UniversalWorkerScalingError(
                (
                    "decision must be "
                    "UniversalWorkerScalingDecision."
                ),
                code="invalid_worker_scaling_decision",
                value=self.decision,
            )

        if not isinstance(
            self.reason,
            UniversalWorkerScalingReason,
        ):

            raise UniversalWorkerScalingError(
                (
                    "reason must be "
                    "UniversalWorkerScalingReason."
                ),
                code="invalid_worker_scaling_reason",
                value=self.reason,
            )

        canonical_evidence = (
            UniversalWorkerScalingEvidence(
                current_worker_count=(
                    self.current_worker_count
                ),
                minimum_worker_count=(
                    self.minimum_worker_count
                ),
                maximum_worker_count=(
                    self.maximum_worker_count
                ),
                pending_work=self.pending_work,
                available_capacity=(
                    self.available_capacity
                ),
                scale_down_safe=(
                    self.scale_down_safe
                ),
            )
        )

        desired = (
            _validate_non_negative_int(
                self.desired_worker_count,
                field_name="desired_worker_count",
                maximum=MAX_UNIVERSAL_WORKER_COUNT,
            )
        )

        object.__setattr__(
            self,
            "desired_worker_count",
            desired,
        )

        (
            expected_decision,
            expected_reason,
            expected_desired,
        ) = decide_universal_worker_scaling(
            canonical_evidence
        )

        if (
            self.decision
            is not expected_decision
            or
            self.reason
            is not expected_reason
            or
            self.desired_worker_count
            != expected_desired
        ):

            raise UniversalWorkerScalingError(
                (
                    "Worker Scaling result is "
                    "inconsistent with its evidence."
                ),
                code="inconsistent_worker_scaling_result",
                value={
                    "decision":
                        self.decision.value,

                    "reason":
                        self.reason.value,

                    "desired_worker_count":
                        self.desired_worker_count,

                    "expected_decision":
                        expected_decision.value,

                    "expected_reason":
                        expected_reason.value,

                    "expected_desired_worker_count":
                        expected_desired,
                },
            )

        if (
            self.schema_version
            != UNIVERSAL_WORKER_SCALING_RESULT_SCHEMA_VERSION
        ):

            raise UniversalWorkerScalingError(
                (
                    "Invalid Worker Scaling Result "
                    "schema_version."
                ),
                code=(
                    "invalid_worker_scaling_"
                    "result_schema_version"
                ),
                value=self.schema_version,
            )

    @property
    def delta(
        self,
    ) -> int:

        return (
            self.desired_worker_count
            - self.current_worker_count
        )

    @property
    def scaling_required(
        self,
    ) -> bool:

        return (
            self.decision
            is not UniversalWorkerScalingDecision.HOLD
        )


def create_universal_worker_scaling_evidence(
    *,
    current_worker_count: int,
    minimum_worker_count: int,
    maximum_worker_count: int,
    pending_work: int,
    available_capacity: int,
    scale_down_safe: bool,
) -> UniversalWorkerScalingEvidence:

    return UniversalWorkerScalingEvidence(
        current_worker_count=current_worker_count,
        minimum_worker_count=minimum_worker_count,
        maximum_worker_count=maximum_worker_count,
        pending_work=pending_work,
        available_capacity=available_capacity,
        scale_down_safe=scale_down_safe,
    )


def evaluate_universal_worker_scaling(
    evidence: UniversalWorkerScalingEvidence,
) -> UniversalWorkerScalingResult:

    if not isinstance(
        evidence,
        UniversalWorkerScalingEvidence,
    ):

        raise UniversalWorkerScalingError(
            (
                "evidence must be "
                "UniversalWorkerScalingEvidence."
            ),
            code="invalid_worker_scaling_evidence",
            value=evidence,
        )

    (
        decision,
        reason,
        desired_worker_count,
    ) = decide_universal_worker_scaling(
        evidence
    )

    return UniversalWorkerScalingResult(
        decision=decision,
        reason=reason,
        current_worker_count=(
            evidence.current_worker_count
        ),
        desired_worker_count=(
            desired_worker_count
        ),
        minimum_worker_count=(
            evidence.minimum_worker_count
        ),
        maximum_worker_count=(
            evidence.maximum_worker_count
        ),
        pending_work=evidence.pending_work,
        available_capacity=(
            evidence.available_capacity
        ),
        scale_down_safe=(
            evidence.scale_down_safe
        ),
    )


def explain_universal_worker_scaling_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "4.1.7",

            "component":
                "Universal Worker Scaling",

            "version":
                UNIVERSAL_WORKER_SCALING_VERSION,

            "evidence_schema_version":
                UNIVERSAL_WORKER_SCALING_EVIDENCE_SCHEMA_VERSION,

            "result_schema_version":
                UNIVERSAL_WORKER_SCALING_RESULT_SCHEMA_VERSION,

            "decisions": (
                "SCALE_UP",
                "HOLD",
                "SCALE_DOWN",
            ),

            "input_rule": (
                "4.1.7 consumes caller-supplied "
                "current/minimum/maximum worker counts, "
                "pending work, aggregate available "
                "capacity and scale-down safety evidence"
            ),

            "minimum_rule": (
                "current worker count below configured "
                "minimum scales directly to minimum"
            ),

            "maximum_rule": (
                "current worker count above configured "
                "maximum scales directly to maximum only "
                "when scale_down_safe is true; otherwise "
                "the decision is HOLD"
            ),

            "scale_up_rule": (
                "pending work greater than aggregate "
                "available capacity scales up by exactly "
                "one worker when below maximum"
            ),

            "scale_down_rule": (
                "zero pending work may scale down by "
                "exactly one worker when above minimum "
                "and scale_down_safe is true"
            ),

            "hold_rule": (
                "HOLD preserves current worker count"
            ),

            "capacity_boundary": (
                "available_capacity is caller-composed "
                "aggregate evidence; 4.1.7 does not "
                "calculate per-worker capacity, slots, "
                "concurrency or utilization"
            ),

            "pool_boundary": (
                "4.1.7 does not define worker pools, "
                "membership or select a pool"
            ),

            "drain_shutdown_boundary": (
                "scale_down_safe is caller-supplied; "
                "4.1.7 does not inspect leases, select "
                "workers, drain workers or shut them down"
            ),

            "provisioning_boundary": (
                "scaling decisions and desired counts "
                "are evidence only; 4.1.7 does not "
                "create, start, provision, stop or "
                "terminate workers"
            ),

            "resource_governance_boundary": (
                "CPU, memory, cost, quotas and physical "
                "resource-governance policy remain "
                "outside 4.1.7"
            ),

            "queue_boundary": (
                "pending_work may be composed from Queue "
                "Infrastructure evidence, but 4.1.7 does "
                "not read or mutate queues"
            ),

            "health_boundary": (
                "4.1.7 does not read or classify Worker "
                "Health; callers may compose health into "
                "scaling evidence outside this authority"
            ),

            "purity_rule": (
                "Worker Scaling is deterministic over "
                "caller-supplied evidence and performs "
                "no state lookup, persistence or mutation"
            ),

            "prohibitions": (
                "does not provision workers",
                "does not start worker processes",
                "does not stop worker processes",
                "does not terminate workers",
                "does not register workers",
                "does not discover workers",
                "does not assign workers",
                "does not select workers for removal",
                "does not drain workers",
                "does not shut down workers",
                "does not inspect active leases",
                "does not acquire leases",
                "does not release leases",
                "does not define worker pools",
                "does not modify worker pool membership",
                "does not calculate per-worker capacity",
                "does not calculate worker utilization",
                "does not calculate worker concurrency",
                "does not inspect worker capabilities",
                "does not determine worker health",
                "does not read worker heartbeats",
                "does not detect stale workers",
                "does not recover workers",
                "does not access cloud-provider APIs",
                "does not create containers",
                "does not create pods",
                "does not create virtual machines",
                "does not enforce CPU quotas",
                "does not enforce memory quotas",
                "does not enforce cost budgets",
                "does not mutate Queue Infrastructure",
                "does not apply Queue Backpressure",
                "does not apply Queue Rate Limiting",
                "does not access Runtime State Store",
                "does not access orchestration",
                "does not persist scaling results",
                "does not perform filesystem I/O",
                "does not perform network I/O",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_WORKER_SCALING_VERSION",
    "UNIVERSAL_WORKER_SCALING_EVIDENCE_SCHEMA_VERSION",
    "UNIVERSAL_WORKER_SCALING_RESULT_SCHEMA_VERSION",
    "MAX_UNIVERSAL_WORKER_COUNT",
    "MAX_UNIVERSAL_WORKER_SCALING_WORK_COUNT",
    "UniversalWorkerScalingError",
    "UniversalWorkerScalingDecision",
    "UniversalWorkerScalingReason",
    "UniversalWorkerScalingEvidence",
    "UniversalWorkerScalingResult",
    "create_universal_worker_scaling_evidence",
    "decide_universal_worker_scaling",
    "evaluate_universal_worker_scaling",
    "explain_universal_worker_scaling_v1",
]
