from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping


UNIVERSAL_WORKER_SHUTDOWN_VERSION = (
    "universal_worker_shutdown_v4.1.8"
)

UNIVERSAL_WORKER_SHUTDOWN_EVIDENCE_SCHEMA_VERSION = (
    "universal_worker_shutdown_evidence_schema_v1"
)

UNIVERSAL_WORKER_SHUTDOWN_RESULT_SCHEMA_VERSION = (
    "universal_worker_shutdown_result_schema_v1"
)

MAX_UNIVERSAL_WORKER_SHUTDOWN_ACTIVE_COUNT = (
    2_147_483_647
)


class UniversalWorkerShutdownError(
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


class UniversalWorkerShutdownDecision(
    str,
    Enum,
):

    NOT_REQUESTED = "NOT_REQUESTED"

    BLOCKED = "BLOCKED"

    READY = "READY"


class UniversalWorkerShutdownReason(
    str,
    Enum,
):

    SHUTDOWN_NOT_REQUESTED = (
        "SHUTDOWN_NOT_REQUESTED"
    )

    ACTIVE_WORK_PRESENT = (
        "ACTIVE_WORK_PRESENT"
    )

    ACTIVE_LEASES_PRESENT = (
        "ACTIVE_LEASES_PRESENT"
    )

    DRAIN_INCOMPLETE = (
        "DRAIN_INCOMPLETE"
    )

    SHUTDOWN_READY = (
        "SHUTDOWN_READY"
    )


def _validate_strict_bool(
    value: Any,
    *,
    field_name: str,
) -> bool:

    if type(value) is not bool:

        raise UniversalWorkerShutdownError(
            (
                field_name
                + " must be bool."
            ),
            code="invalid_worker_shutdown_boolean",
            value={
                "field_name":
                    field_name,

                "value":
                    value,
            },
        )

    return value


def _validate_non_negative_count(
    value: Any,
    *,
    field_name: str,
) -> int:

    if (
        type(value) is not int
        or
        value < 0
    ):

        raise UniversalWorkerShutdownError(
            (
                field_name
                + " must be a non-negative integer."
            ),
            code="invalid_worker_shutdown_count",
            value={
                "field_name":
                    field_name,

                "value":
                    value,
            },
        )

    if (
        value
        > MAX_UNIVERSAL_WORKER_SHUTDOWN_ACTIVE_COUNT
    ):

        raise UniversalWorkerShutdownError(
            (
                field_name
                + " exceeds the supported maximum."
            ),
            code="worker_shutdown_count_too_large",
            value={
                "field_name":
                    field_name,

                "value":
                    value,

                "maximum":
                    (
                        MAX_UNIVERSAL_WORKER_SHUTDOWN_ACTIVE_COUNT
                    ),
            },
        )

    return value


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalWorkerShutdownEvidence:

    shutdown_requested: bool

    drain_complete: bool

    active_work_count: int

    active_lease_count: int

    schema_version: str = (
        UNIVERSAL_WORKER_SHUTDOWN_EVIDENCE_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        object.__setattr__(
            self,
            "shutdown_requested",
            _validate_strict_bool(
                self.shutdown_requested,
                field_name="shutdown_requested",
            ),
        )

        object.__setattr__(
            self,
            "drain_complete",
            _validate_strict_bool(
                self.drain_complete,
                field_name="drain_complete",
            ),
        )

        object.__setattr__(
            self,
            "active_work_count",
            _validate_non_negative_count(
                self.active_work_count,
                field_name="active_work_count",
            ),
        )

        object.__setattr__(
            self,
            "active_lease_count",
            _validate_non_negative_count(
                self.active_lease_count,
                field_name="active_lease_count",
            ),
        )

        if (
            self.drain_complete
            and
            self.active_work_count != 0
        ):

            raise UniversalWorkerShutdownError(
                (
                    "drain_complete=True contradicts "
                    "active_work_count > 0."
                ),
                code=(
                    "drain_complete_active_work_"
                    "contradiction"
                ),
                value=self.active_work_count,
            )

        if (
            self.drain_complete
            and
            self.active_lease_count != 0
        ):

            raise UniversalWorkerShutdownError(
                (
                    "drain_complete=True contradicts "
                    "active_lease_count > 0."
                ),
                code=(
                    "drain_complete_active_lease_"
                    "contradiction"
                ),
                value=self.active_lease_count,
            )

        if (
            self.schema_version
            != UNIVERSAL_WORKER_SHUTDOWN_EVIDENCE_SCHEMA_VERSION
        ):

            raise UniversalWorkerShutdownError(
                (
                    "Invalid Worker Shutdown Evidence "
                    "schema_version."
                ),
                code=(
                    "invalid_worker_shutdown_"
                    "evidence_schema_version"
                ),
                value=self.schema_version,
            )


def decide_universal_worker_shutdown(
    evidence: UniversalWorkerShutdownEvidence,
) -> tuple[
    UniversalWorkerShutdownDecision,
    UniversalWorkerShutdownReason,
]:

    if not isinstance(
        evidence,
        UniversalWorkerShutdownEvidence,
    ):

        raise UniversalWorkerShutdownError(
            (
                "evidence must be "
                "UniversalWorkerShutdownEvidence."
            ),
            code="invalid_worker_shutdown_evidence",
            value=evidence,
        )

    if not evidence.shutdown_requested:

        return (
            UniversalWorkerShutdownDecision.NOT_REQUESTED,
            UniversalWorkerShutdownReason.SHUTDOWN_NOT_REQUESTED,
        )

    if (
        evidence.active_work_count
        > 0
    ):

        return (
            UniversalWorkerShutdownDecision.BLOCKED,
            UniversalWorkerShutdownReason.ACTIVE_WORK_PRESENT,
        )

    if (
        evidence.active_lease_count
        > 0
    ):

        return (
            UniversalWorkerShutdownDecision.BLOCKED,
            UniversalWorkerShutdownReason.ACTIVE_LEASES_PRESENT,
        )

    if not evidence.drain_complete:

        return (
            UniversalWorkerShutdownDecision.BLOCKED,
            UniversalWorkerShutdownReason.DRAIN_INCOMPLETE,
        )

    return (
        UniversalWorkerShutdownDecision.READY,
        UniversalWorkerShutdownReason.SHUTDOWN_READY,
    )


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalWorkerShutdownResult:

    decision: UniversalWorkerShutdownDecision

    reason: UniversalWorkerShutdownReason

    shutdown_requested: bool

    drain_complete: bool

    active_work_count: int

    active_lease_count: int

    schema_version: str = (
        UNIVERSAL_WORKER_SHUTDOWN_RESULT_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        if not isinstance(
            self.decision,
            UniversalWorkerShutdownDecision,
        ):

            raise UniversalWorkerShutdownError(
                (
                    "decision must be "
                    "UniversalWorkerShutdownDecision."
                ),
                code="invalid_worker_shutdown_decision",
                value=self.decision,
            )

        if not isinstance(
            self.reason,
            UniversalWorkerShutdownReason,
        ):

            raise UniversalWorkerShutdownError(
                (
                    "reason must be "
                    "UniversalWorkerShutdownReason."
                ),
                code="invalid_worker_shutdown_reason",
                value=self.reason,
            )

        canonical_evidence = (
            UniversalWorkerShutdownEvidence(
                shutdown_requested=(
                    self.shutdown_requested
                ),
                drain_complete=(
                    self.drain_complete
                ),
                active_work_count=(
                    self.active_work_count
                ),
                active_lease_count=(
                    self.active_lease_count
                ),
            )
        )

        if (
            self.schema_version
            != UNIVERSAL_WORKER_SHUTDOWN_RESULT_SCHEMA_VERSION
        ):

            raise UniversalWorkerShutdownError(
                (
                    "Invalid Worker Shutdown Result "
                    "schema_version."
                ),
                code=(
                    "invalid_worker_shutdown_"
                    "result_schema_version"
                ),
                value=self.schema_version,
            )

        (
            expected_decision,
            expected_reason,
        ) = decide_universal_worker_shutdown(
            canonical_evidence
        )

        if (
            self.decision
            is not expected_decision
            or
            self.reason
            is not expected_reason
        ):

            raise UniversalWorkerShutdownError(
                (
                    "Worker Shutdown result is "
                    "inconsistent with its evidence."
                ),
                code="inconsistent_worker_shutdown_result",
                value={
                    "decision":
                        self.decision.value,

                    "reason":
                        self.reason.value,

                    "expected_decision":
                        expected_decision.value,

                    "expected_reason":
                        expected_reason.value,
                },
            )

    @property
    def shutdown_ready(
        self,
    ) -> bool:

        return (
            self.decision
            is UniversalWorkerShutdownDecision.READY
        )

    @property
    def shutdown_blocked(
        self,
    ) -> bool:

        return (
            self.decision
            is UniversalWorkerShutdownDecision.BLOCKED
        )


def create_universal_worker_shutdown_evidence(
    *,
    shutdown_requested: bool,
    drain_complete: bool,
    active_work_count: int,
    active_lease_count: int,
) -> UniversalWorkerShutdownEvidence:

    return UniversalWorkerShutdownEvidence(
        shutdown_requested=shutdown_requested,
        drain_complete=drain_complete,
        active_work_count=active_work_count,
        active_lease_count=active_lease_count,
    )


def evaluate_universal_worker_shutdown(
    evidence: UniversalWorkerShutdownEvidence,
) -> UniversalWorkerShutdownResult:

    if not isinstance(
        evidence,
        UniversalWorkerShutdownEvidence,
    ):

        raise UniversalWorkerShutdownError(
            (
                "evidence must be "
                "UniversalWorkerShutdownEvidence."
            ),
            code="invalid_worker_shutdown_evidence",
            value=evidence,
        )

    (
        decision,
        reason,
    ) = decide_universal_worker_shutdown(
        evidence
    )

    return UniversalWorkerShutdownResult(
        decision=decision,
        reason=reason,
        shutdown_requested=(
            evidence.shutdown_requested
        ),
        drain_complete=(
            evidence.drain_complete
        ),
        active_work_count=(
            evidence.active_work_count
        ),
        active_lease_count=(
            evidence.active_lease_count
        ),
    )


def explain_universal_worker_shutdown_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "4.1.8",

            "component":
                "Universal Worker Shutdown",

            "version":
                UNIVERSAL_WORKER_SHUTDOWN_VERSION,

            "evidence_schema_version":
                UNIVERSAL_WORKER_SHUTDOWN_EVIDENCE_SCHEMA_VERSION,

            "result_schema_version":
                UNIVERSAL_WORKER_SHUTDOWN_RESULT_SCHEMA_VERSION,

            "decisions": (
                "NOT_REQUESTED",
                "BLOCKED",
                "READY",
            ),

            "input_rule": (
                "4.1.8 consumes caller-supplied "
                "shutdown-request, drain-completion, "
                "active-work-count and active-lease-"
                "count evidence"
            ),

            "not_requested_rule": (
                "without an explicit shutdown request "
                "the worker shutdown decision is "
                "NOT_REQUESTED"
            ),

            "active_work_rule": (
                "a requested shutdown is BLOCKED while "
                "active work remains"
            ),

            "active_lease_rule": (
                "a requested shutdown is BLOCKED while "
                "active lease ownership remains"
            ),

            "drain_rule": (
                "when no active work or leases remain, "
                "a requested shutdown is BLOCKED until "
                "caller-supplied drain_complete is true"
            ),

            "ready_rule": (
                "READY requires shutdown requested, "
                "drain complete, zero active work and "
                "zero active leases"
            ),

            "drain_boundary": (
                "4.1.12 Worker Drain owns worker drain "
                "state and behavior; 4.1.8 only consumes "
                "caller-supplied drain completion"
            ),

            "runtime_shutdown_boundary": (
                "4.1.8 is an individual-worker "
                "permission authority and does not "
                "replace or invoke the existing "
                "whole-runtime shutdown process"
            ),

            "termination_boundary": (
                "READY is termination-permission "
                "evidence only; 4.1.8 does not stop, "
                "kill or terminate a worker process"
            ),

            "lease_boundary": (
                "active_lease_count is caller-supplied; "
                "4.1.8 does not inspect, acquire, renew "
                "or release leases"
            ),

            "work_boundary": (
                "active_work_count is caller-supplied; "
                "4.1.8 does not inspect, cancel, fail, "
                "recover or requeue jobs"
            ),

            "registration_pool_boundary": (
                "4.1.8 does not deregister workers or "
                "remove Worker Pool membership"
            ),

            "heartbeat_boundary": (
                "4.1.8 does not emit, delete or inspect "
                "worker heartbeats"
            ),

            "health_scaling_boundary": (
                "Worker Health and Worker Scaling do "
                "not automatically imply shutdown; "
                "shutdown_requested remains explicit "
                "caller evidence"
            ),

            "forced_shutdown_boundary": (
                "forced termination and emergency "
                "recovery remain outside this "
                "permission authority"
            ),

            "purity_rule": (
                "Worker Shutdown is deterministic over "
                "caller-supplied evidence and performs "
                "no state lookup, persistence or mutation"
            ),

            "prohibitions": (
                "does not stop worker processes",
                "does not kill workers",
                "does not terminate workers",
                "does not send operating-system signals",
                "does not invoke whole-runtime shutdown",
                "does not drain workers",
                "does not determine drain state",
                "does not inspect active jobs",
                "does not inspect active leases",
                "does not acquire leases",
                "does not renew leases",
                "does not release leases",
                "does not cancel jobs",
                "does not fail jobs",
                "does not requeue jobs",
                "does not recover jobs",
                "does not recover workers",
                "does not deregister workers",
                "does not delete worker registrations",
                "does not modify Worker Pool membership",
                "does not emit worker heartbeats",
                "does not delete worker heartbeats",
                "does not inspect worker heartbeats",
                "does not determine Worker Health",
                "does not perform Worker Scaling",
                "does not assign workers",
                "does not provision replacement workers",
                "does not mutate Queue Infrastructure",
                "does not access Runtime State Store",
                "does not access orchestration",
                "does not persist shutdown results",
                "does not perform filesystem I/O",
                "does not perform network I/O",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_WORKER_SHUTDOWN_VERSION",
    "UNIVERSAL_WORKER_SHUTDOWN_EVIDENCE_SCHEMA_VERSION",
    "UNIVERSAL_WORKER_SHUTDOWN_RESULT_SCHEMA_VERSION",
    "MAX_UNIVERSAL_WORKER_SHUTDOWN_ACTIVE_COUNT",
    "UniversalWorkerShutdownError",
    "UniversalWorkerShutdownDecision",
    "UniversalWorkerShutdownReason",
    "UniversalWorkerShutdownEvidence",
    "UniversalWorkerShutdownResult",
    "create_universal_worker_shutdown_evidence",
    "decide_universal_worker_shutdown",
    "evaluate_universal_worker_shutdown",
    "explain_universal_worker_shutdown_v1",
]
