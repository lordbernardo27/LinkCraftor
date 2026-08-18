from __future__ import annotations

import ast
import hashlib
import importlib
import sys
from pathlib import Path


ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
)

SCALING_PATH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_worker"
    / "scaling.py"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_4_1_7_worker_scaling_initial_implementation.txt"
)


# ============================================================
# PROTECTED FROZEN AUTHORITIES
# ============================================================

PROTECTED = {
    "worker_registration": (
        ROOT / "backend/server/runtime/universal_worker/registration.py",
        "00F0D6E620E24A7433C880B722E023AF3C2121563F8E18DFA9979E0F06A36D64",
    ),

    "worker_discovery": (
        ROOT / "backend/server/runtime/universal_worker/discovery.py",
        "DFCAB9080982C8D5E099A40C903F7B4140B0860053DB73CB77B30B966788A228",
    ),

    "worker_assignment": (
        ROOT / "backend/server/runtime/universal_worker/assignment.py",
        "609D3077B84C1791262F8ACA6BD268FD40436DF7775ACB3E9E726BCFC9715F56",
    ),

    "worker_leasing": (
        ROOT / "backend/server/runtime/universal_worker/leasing.py",
        "413B8081D7802211D64B7B811299F9A8A2C54DBAEAB0FC537B1603A3BE397932",
    ),

    "worker_health": (
        ROOT / "backend/server/runtime/universal_worker/health.py",
        "DCC43E77BDC12188DFD15044DA4DA41022B3CEF40F9C4ED06371EE66AA4E5F65",
    ),

    "worker_recovery": (
        ROOT / "backend/server/runtime/universal_worker/recovery.py",
        "C3EF5DBD81205F0087E05F43F6A67A1E0762930DAAD256F957AABC57296D19A5",
    ),

    "queue_certification": (
        ROOT / "backend/server/runtime/universal_queue/certification.py",
        "6ED39655147D2B331E02101F5EA23E68CF71447353C0D294E170281AE40C0D4C",
    ),

    "job_contract": (
        ROOT / "backend/server/runtime/universal_jobs/contract.py",
        "82225461C792EDA7193D2FA3B59E39FF3823906365CD0FBCD5E2915673EE23D1",
    ),

    "existing_runtime_worker": (
        ROOT / "backend/server/runtime/universal_runtime_worker_v1.py",
        "6CC4EC122C6B8D1E21AFF8B55CAA786148D7E1FC75D840DAE9240FFB69634D44",
    ),

    "runtime_registration": (
        ROOT / "backend/server/runtime/universal_runtime_registration.py",
        "CBFBB0DA1E5D05A040AEC6F60B1251331431956106D90335A8C110FDBCA632E5",
    ),

    "runtime_infrastructure": (
        ROOT / "backend/server/runtime/universal_runtime_infrastructure.py",
        "EE6590D044C6AA20762F2A37AE86B7FFD3300B62610BC2B1F2657D9334CB311C",
    ),

    "orchestration_queue": (
        ROOT / "backend/server/orchestration/queue.py",
        "76F8F7E66578E2B8A4A1FF3BB420B6340A7A1D1D661EB66B7C21987CF3845A97",
    ),

    "orchestration_service": (
        ROOT / "backend/server/orchestration/service.py",
        "4C31CFC6FFDC9AFA8EA6AD8F43ADBC117F8A6D0193ABF045DBFBA39D6EB799BA",
    ),
}


def ast_sha(path: Path) -> str:

    source = path.read_text(
        encoding="utf-8-sig"
    )

    tree = ast.parse(source)

    canonical = ast.dump(
        tree,
        annotate_fields=True,
        include_attributes=False,
    )

    return hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest().upper()


for name, (
    path,
    expected,
) in PROTECTED.items():

    actual = ast_sha(path)

    if actual != expected:

        raise SystemExit(
            (
                "Protected authority mismatch before "
                "4.1.7 implementation: "
                + name
                + "\nEXPECTED: "
                + expected
                + "\nACTUAL:   "
                + actual
            )
        )


# ============================================================
# PRODUCTION AUTHORITY
# ============================================================

SOURCE = r'''from __future__ import annotations

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
'''


ast.parse(SOURCE)

SCALING_PATH.write_text(
    SOURCE,
    encoding="utf-8",
)


# ============================================================
# IMPORT
# ============================================================

sys.path.insert(
    0,
    str(ROOT),
)

scaling_name = (
    "backend.server.runtime."
    "universal_worker.scaling"
)

sys.modules.pop(
    scaling_name,
    None,
)

scaling = importlib.import_module(
    scaling_name
)


checks = []


def check(
    name,
    condition,
    detail="",
):

    checks.append(
        (
            name,
            bool(condition),
            str(detail),
        )
    )


# ============================================================
# VERSION / SURFACE
# ============================================================

check(
    "version",
    scaling.UNIVERSAL_WORKER_SCALING_VERSION
    == "universal_worker_scaling_v4.1.7",
)

check(
    "evidence_schema",
    scaling.UNIVERSAL_WORKER_SCALING_EVIDENCE_SCHEMA_VERSION
    == "universal_worker_scaling_evidence_schema_v1",
)

check(
    "result_schema",
    scaling.UNIVERSAL_WORKER_SCALING_RESULT_SCHEMA_VERSION
    == "universal_worker_scaling_result_schema_v1",
)

check(
    "decisions_exact",
    tuple(
        x.value
        for x in scaling.UniversalWorkerScalingDecision
    )
    == (
        "SCALE_UP",
        "HOLD",
        "SCALE_DOWN",
    ),
)


# ============================================================
# MINIMUM / MAXIMUM
# ============================================================

below_minimum = (
    scaling.create_universal_worker_scaling_evidence(
        current_worker_count=1,
        minimum_worker_count=3,
        maximum_worker_count=10,
        pending_work=0,
        available_capacity=100,
        scale_down_safe=False,
    )
)

result = (
    scaling.evaluate_universal_worker_scaling(
        below_minimum
    )
)

check(
    "below_minimum_scale_up",
    result.decision
    is scaling.UniversalWorkerScalingDecision.SCALE_UP,
)

check(
    "below_minimum_target",
    result.desired_worker_count
    == 3,
)

check(
    "below_minimum_delta",
    result.delta
    == 2,
)


above_max_safe = (
    scaling.create_universal_worker_scaling_evidence(
        current_worker_count=12,
        minimum_worker_count=2,
        maximum_worker_count=10,
        pending_work=100,
        available_capacity=0,
        scale_down_safe=True,
    )
)

result_above_max_safe = (
    scaling.evaluate_universal_worker_scaling(
        above_max_safe
    )
)

check(
    "above_max_scale_down",
    result_above_max_safe.decision
    is scaling.UniversalWorkerScalingDecision.SCALE_DOWN,
)

check(
    "above_max_target",
    result_above_max_safe.desired_worker_count
    == 10,
)


above_max_unsafe = (
    scaling.create_universal_worker_scaling_evidence(
        current_worker_count=12,
        minimum_worker_count=2,
        maximum_worker_count=10,
        pending_work=0,
        available_capacity=0,
        scale_down_safe=False,
    )
)

result_above_max_unsafe = (
    scaling.evaluate_universal_worker_scaling(
        above_max_unsafe
    )
)

check(
    "above_max_unsafe_hold",
    result_above_max_unsafe.decision
    is scaling.UniversalWorkerScalingDecision.HOLD,
)

check(
    "above_max_unsafe_preserves_current",
    result_above_max_unsafe.desired_worker_count
    == 12,
)


# ============================================================
# DEMAND SCALE-UP
# ============================================================

demand = (
    scaling.create_universal_worker_scaling_evidence(
        current_worker_count=4,
        minimum_worker_count=2,
        maximum_worker_count=10,
        pending_work=21,
        available_capacity=20,
        scale_down_safe=False,
    )
)

demand_result = (
    scaling.evaluate_universal_worker_scaling(
        demand
    )
)

check(
    "demand_exceeds_capacity_scale_up",
    demand_result.decision
    is scaling.UniversalWorkerScalingDecision.SCALE_UP,
)

check(
    "demand_scale_up_one",
    demand_result.desired_worker_count
    == 5,
)

check(
    "demand_scale_up_delta_one",
    demand_result.delta
    == 1,
)


maxed = (
    scaling.create_universal_worker_scaling_evidence(
        current_worker_count=10,
        minimum_worker_count=2,
        maximum_worker_count=10,
        pending_work=100,
        available_capacity=0,
        scale_down_safe=False,
    )
)

maxed_result = (
    scaling.evaluate_universal_worker_scaling(
        maxed
    )
)

check(
    "maximum_reached_hold",
    maxed_result.decision
    is scaling.UniversalWorkerScalingDecision.HOLD,
)


# ============================================================
# ZERO-DEMAND SCALE-DOWN
# ============================================================

zero_safe = (
    scaling.create_universal_worker_scaling_evidence(
        current_worker_count=5,
        minimum_worker_count=2,
        maximum_worker_count=10,
        pending_work=0,
        available_capacity=20,
        scale_down_safe=True,
    )
)

zero_safe_result = (
    scaling.evaluate_universal_worker_scaling(
        zero_safe
    )
)

check(
    "zero_demand_scale_down",
    zero_safe_result.decision
    is scaling.UniversalWorkerScalingDecision.SCALE_DOWN,
)

check(
    "zero_demand_scale_down_one",
    zero_safe_result.desired_worker_count
    == 4,
)

check(
    "zero_demand_delta_minus_one",
    zero_safe_result.delta
    == -1,
)


zero_unsafe = (
    scaling.create_universal_worker_scaling_evidence(
        current_worker_count=5,
        minimum_worker_count=2,
        maximum_worker_count=10,
        pending_work=0,
        available_capacity=20,
        scale_down_safe=False,
    )
)

zero_unsafe_result = (
    scaling.evaluate_universal_worker_scaling(
        zero_unsafe
    )
)

check(
    "unsafe_scale_down_hold",
    zero_unsafe_result.decision
    is scaling.UniversalWorkerScalingDecision.HOLD,
)


at_minimum = (
    scaling.create_universal_worker_scaling_evidence(
        current_worker_count=2,
        minimum_worker_count=2,
        maximum_worker_count=10,
        pending_work=0,
        available_capacity=20,
        scale_down_safe=True,
    )
)

at_minimum_result = (
    scaling.evaluate_universal_worker_scaling(
        at_minimum
    )
)

check(
    "minimum_reached_hold",
    at_minimum_result.decision
    is scaling.UniversalWorkerScalingDecision.HOLD,
)


# ============================================================
# SUFFICIENT CAPACITY DOES NOT SCALE DOWN
# ============================================================

sufficient = (
    scaling.create_universal_worker_scaling_evidence(
        current_worker_count=8,
        minimum_worker_count=2,
        maximum_worker_count=10,
        pending_work=1,
        available_capacity=500,
        scale_down_safe=True,
    )
)

sufficient_result = (
    scaling.evaluate_universal_worker_scaling(
        sufficient
    )
)

check(
    "positive_demand_sufficient_capacity_hold",
    sufficient_result.decision
    is scaling.UniversalWorkerScalingDecision.HOLD,
)

check(
    "positive_demand_preserves_current",
    sufficient_result.desired_worker_count
    == 8,
)


# ============================================================
# ZERO-WORKER EDGE
# ============================================================

zero_workers_demand = (
    scaling.create_universal_worker_scaling_evidence(
        current_worker_count=0,
        minimum_worker_count=0,
        maximum_worker_count=5,
        pending_work=1,
        available_capacity=0,
        scale_down_safe=False,
    )
)

zero_workers_result = (
    scaling.evaluate_universal_worker_scaling(
        zero_workers_demand
    )
)

check(
    "zero_workers_with_demand_scale_up",
    zero_workers_result.decision
    is scaling.UniversalWorkerScalingDecision.SCALE_UP,
)

check(
    "zero_workers_target_one",
    zero_workers_result.desired_worker_count
    == 1,
)


# ============================================================
# STRICT INTEGER VALIDATION
# ============================================================

for field_name in (
    "current_worker_count",
    "minimum_worker_count",
    "maximum_worker_count",
    "pending_work",
    "available_capacity",
):

    for bad in (
        None,
        True,
        False,
        -1,
        1.0,
        "",
        [],
        {},
    ):

        kwargs = {
            "current_worker_count": 2,
            "minimum_worker_count": 1,
            "maximum_worker_count": 5,
            "pending_work": 1,
            "available_capacity": 1,
            "scale_down_safe": True,
        }

        kwargs[
            field_name
        ] = bad

        try:

            scaling.create_universal_worker_scaling_evidence(
                **kwargs
            )

        except scaling.UniversalWorkerScalingError as exc:

            rejected = (
                exc.code
                == "invalid_worker_scaling_integer"
            )

        else:

            rejected = False

        check(
            (
                "strict_integer_"
                + field_name
                + "_"
                + type(bad).__name__
                + "_"
                + repr(bad)
            ),
            rejected,
        )


# ============================================================
# BOUNDS
# ============================================================

try:

    scaling.create_universal_worker_scaling_evidence(
        current_worker_count=2,
        minimum_worker_count=6,
        maximum_worker_count=5,
        pending_work=0,
        available_capacity=0,
        scale_down_safe=True,
    )

except scaling.UniversalWorkerScalingError as exc:

    rejected = (
        exc.code
        == "invalid_worker_scaling_bounds"
    )

else:

    rejected = False


check(
    "invalid_min_max_rejected",
    rejected,
)


# ============================================================
# STRICT SCALE-DOWN BOOL
# ============================================================

for bad in (
    None,
    0,
    1,
    "",
    "true",
    [],
    {},
):

    try:

        scaling.create_universal_worker_scaling_evidence(
            current_worker_count=2,
            minimum_worker_count=1,
            maximum_worker_count=5,
            pending_work=0,
            available_capacity=10,
            scale_down_safe=bad,
        )

    except scaling.UniversalWorkerScalingError as exc:

        rejected = (
            exc.code
            == "invalid_worker_scaling_boolean"
        )

    else:

        rejected = False

    check(
        "strict_scale_down_safe_"
        + repr(bad),
        rejected,
    )


# ============================================================
# RESULT FORGERY
# ============================================================

canonical = (
    scaling.create_universal_worker_scaling_evidence(
        current_worker_count=4,
        minimum_worker_count=2,
        maximum_worker_count=10,
        pending_work=20,
        available_capacity=5,
        scale_down_safe=False,
    )
)

canonical_result = (
    scaling.evaluate_universal_worker_scaling(
        canonical
    )
)


try:

    scaling.UniversalWorkerScalingResult(
        decision=(
            scaling.UniversalWorkerScalingDecision.HOLD
        ),
        reason=(
            scaling.UniversalWorkerScalingReason
            .AVAILABLE_CAPACITY_SUFFICIENT
        ),
        current_worker_count=4,
        desired_worker_count=4,
        minimum_worker_count=2,
        maximum_worker_count=10,
        pending_work=20,
        available_capacity=5,
        scale_down_safe=False,
    )

except scaling.UniversalWorkerScalingError as exc:

    rejected = (
        exc.code
        == "inconsistent_worker_scaling_result"
    )

else:

    rejected = False


check(
    "forged_result_rejected",
    rejected,
)


# ============================================================
# IMMUTABILITY / DETERMINISM
# ============================================================

for obj, field_name in (
    (
        canonical,
        "current_worker_count",
    ),
    (
        canonical,
        "pending_work",
    ),
    (
        canonical_result,
        "decision",
    ),
    (
        canonical_result,
        "desired_worker_count",
    ),
):

    try:

        setattr(
            obj,
            field_name,
            None,
        )

    except Exception:

        immutable = True

    else:

        immutable = False

    check(
        (
            "immutable_"
            + type(obj).__name__
            + "_"
            + field_name
        ),
        immutable,
    )


check(
    "deterministic_decision",
    scaling.decide_universal_worker_scaling(
        canonical
    )
    ==
    scaling.decide_universal_worker_scaling(
        canonical
    ),
)

check(
    "deterministic_result",
    scaling.evaluate_universal_worker_scaling(
        canonical
    )
    ==
    scaling.evaluate_universal_worker_scaling(
        canonical
    ),
)


# ============================================================
# EXPLANATION
# ============================================================

explanation = (
    scaling.explain_universal_worker_scaling_v1()
)


check(
    "explanation_phase",
    explanation.get(
        "phase"
    )
    == "4.1.7",
)

check(
    "explanation_component",
    explanation.get(
        "component"
    )
    == "Universal Worker Scaling",
)

check(
    "decisions_explained",
    tuple(
        explanation.get(
            "decisions"
        )
    )
    == (
        "SCALE_UP",
        "HOLD",
        "SCALE_DOWN",
    ),
)

check(
    "caller_supplied_evidence",
    "caller-supplied"
    in explanation.get(
        "input_rule",
        "",
    ),
)

check(
    "scale_up_one_rule",
    "exactly one worker"
    in explanation.get(
        "scale_up_rule",
        "",
    ),
)

check(
    "scale_down_one_rule",
    "exactly one worker"
    in explanation.get(
        "scale_down_rule",
        "",
    ),
)

check(
    "capacity_boundary",
    "does not calculate per-worker capacity"
    in explanation.get(
        "capacity_boundary",
        "",
    ),
)

check(
    "pool_boundary",
    "does not define worker pools"
    in explanation.get(
        "pool_boundary",
        "",
    ),
)

check(
    "drain_shutdown_boundary",
    "scale_down_safe is caller-supplied"
    in explanation.get(
        "drain_shutdown_boundary",
        "",
    ),
)

check(
    "provisioning_boundary",
    "does not"
    in explanation.get(
        "provisioning_boundary",
        "",
    ),
)

check(
    "resource_boundary",
    "outside 4.1.7"
    in explanation.get(
        "resource_governance_boundary",
        "",
    ),
)

check(
    "queue_boundary",
    "does not read or mutate queues"
    in explanation.get(
        "queue_boundary",
        "",
    ),
)

check(
    "health_boundary",
    "does not read or classify Worker Health"
    in explanation.get(
        "health_boundary",
        "",
    ),
)

check(
    "purity_rule",
    "no state lookup, persistence or mutation"
    in explanation.get(
        "purity_rule",
        "",
    ),
)


# ============================================================
# PROHIBITIONS
# ============================================================

required_prohibitions = (
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
)


prohibitions = tuple(
    explanation.get(
        "prohibitions"
    )
    or ()
)


for index, item in enumerate(
    required_prohibitions,
    start=1,
):

    check(
        "prohibition_"
        + str(index),
        item in prohibitions,
        item,
    )


# ============================================================
# IMPORT BOUNDARY / FORBIDDEN CALLS
# ============================================================

source = SCALING_PATH.read_text(
    encoding="utf-8-sig"
)

tree = ast.parse(source)

backend_imports = []


for node in ast.walk(tree):

    if isinstance(
        node,
        ast.ImportFrom,
    ):

        module_name = (
            node.module
            or ""
        )

        if module_name.startswith(
            "backend.server"
        ):

            backend_imports.append(
                module_name
            )


check(
    "no_backend_imports",
    backend_imports
    == [],
    backend_imports,
)


forbidden_calls = []


forbidden_names = {
    "open",
    "write_text",
    "mkdir",
    "unlink",
    "remove",
    "now",
    "utcnow",
    "time",
    "sleep",
    "worker_heartbeat",
    "inspect_workers",
    "assign_universal_worker",
    "acquire_universal_worker_lease",
    "release_universal_worker_lease",
    "evaluate_universal_worker_health",
    "evaluate_universal_worker_recovery",
    "get_runtime_state_store_registry",
    "dispatch_job",
    "execute_job",
    "shutdown",
    "terminate",
    "spawn",
    "provision",
}


for node in ast.walk(tree):

    if not isinstance(
        node,
        ast.Call,
    ):

        continue

    if isinstance(
        node.func,
        ast.Name,
    ):

        name = (
            node.func.id
        )

    elif isinstance(
        node.func,
        ast.Attribute,
    ):

        name = (
            node.func.attr
        )

    else:

        continue

    if name in forbidden_names:

        forbidden_calls.append(
            (
                name,
                getattr(
                    node,
                    "lineno",
                    0,
                ),
            )
        )


check(
    "no_forbidden_calls",
    not forbidden_calls,
    forbidden_calls,
)


# ============================================================
# PROTECTED AUTHORITIES
# ============================================================

for name, (
    path,
    expected,
) in PROTECTED.items():

    actual = ast_sha(path)

    check(
        "protected_"
        + name,
        actual
        == expected,
        actual,
    )


# ============================================================
# AST
# ============================================================

scaling_ast = ast_sha(
    SCALING_PATH
)


check(
    "scaling_ast_generated",
    len(
        scaling_ast
    )
    == 64,
    scaling_ast,
)


# ============================================================
# REPORT
# ============================================================

passed = sum(
    1
    for _, ok, _
    in checks
    if ok
)

total = len(checks)


lines = [
    (
        "PHASE 4.1.7 — UNIVERSAL WORKER "
        "SCALING INITIAL IMPLEMENTATION"
    ),
    "=" * 112,
    "",
    (
        "WORKER SCALING AST SHA256: "
        + scaling_ast
    ),
    "",
]


for index, (
    name,
    ok,
    detail,
) in enumerate(
    checks,
    start=1,
):

    lines.append(
        (
            f"{index}. {name}: "
            f"{'PASS' if ok else 'FAIL'}"
        )
    )

    if detail:

        lines.append(
            "   "
            + detail
        )


lines.extend(
    [
        "",
        "=" * 112,
        (
            "INITIAL WORKER SCALING RESULT: "
            + (
                "PASS"
                if passed == total
                else "FAIL"
            )
        ),
        (
            "CHECKS PASSED: "
            + str(passed)
            + "/"
            + str(total)
        ),
        "",
        "4.1.1 WORKER REGISTRATION MODIFIED: NO",
        "4.1.2 WORKER DISCOVERY MODIFIED: NO",
        "4.1.3 WORKER ASSIGNMENT MODIFIED: NO",
        "4.1.4 WORKER LEASING MODIFIED: NO",
        "4.1.5 WORKER HEALTH MODIFIED: NO",
        "4.1.6 WORKER RECOVERY MODIFIED: NO",
        "QUEUE INFRASTRUCTURE MODIFIED: NO",
        "UNIVERSAL JOB CONTRACT MODIFIED: NO",
        "EXISTING UNIVERSAL RUNTIME WORKER MODIFIED: NO",
        "RUNTIME REGISTRATION MODIFIED: NO",
        "RUNTIME INFRASTRUCTURE MODIFIED: NO",
        "ORCHESTRATION MODIFIED: NO",
        "WORKER PROVISIONED: NO",
        "WORKER STARTED: NO",
        "WORKER STOPPED: NO",
        "WORKER TERMINATED: NO",
        "WORKER REGISTERED: NO",
        "WORKER ASSIGNED: NO",
        "WORKER SELECTED FOR REMOVAL: NO",
        "WORKER DRAINED: NO",
        "WORKER SHUT DOWN: NO",
        "LEASE INSPECTED OR MUTATED: NO",
        "WORKER POOL DEFINED OR MUTATED: NO",
        "PER-WORKER CAPACITY CALCULATED: NO",
        "WORKER UTILIZATION CALCULATED: NO",
        "WORKER CAPABILITY INSPECTED: NO",
        "WORKER HEALTH INSPECTED: NO",
        "WORKER HEARTBEAT READ: NO",
        "STALE WORKER DETECTED: NO",
        "WORKER RECOVERY PERFORMED: NO",
        "CLOUD PROVIDER ACCESSED: NO",
        "CONTAINER/POD/VM CREATED: NO",
        "CPU/MEMORY/COST GOVERNANCE APPLIED: NO",
        "QUEUE MUTATED: NO",
        "BACKPRESSURE APPLIED: NO",
        "RATE LIMIT APPLIED: NO",
        "RUNTIME STATE STORE ACCESSED: NO",
        "SCALING RESULT PERSISTED: NO",
        "",
        (
            "STATUS: INITIAL IMPLEMENTATION PASS "
            "— ADVERSARIAL REGRESSION REQUIRED"
            if passed == total
            else
            "STATUS: INITIAL IMPLEMENTATION FAILED"
        ),
    ]
)


REPORT_PATH.write_text(
    "\n".join(lines),
    encoding="utf-8",
)

print(
    "\n".join(lines)
)


if passed != total:

    raise SystemExit(
        "Phase 4.1.7 Worker Scaling initial implementation failed."
    )
