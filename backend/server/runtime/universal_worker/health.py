from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from backend.server.runtime.universal_worker.registration import (
    UniversalWorkerRegistration,
)


UNIVERSAL_WORKER_HEALTH_VERSION = (
    "universal_worker_health_v4.1.5"
)

UNIVERSAL_WORKER_HEALTH_EVIDENCE_SCHEMA_VERSION = (
    "universal_worker_health_evidence_schema_v1"
)

UNIVERSAL_WORKER_HEALTH_RESULT_SCHEMA_VERSION = (
    "universal_worker_health_result_schema_v1"
)


class UniversalWorkerHealthError(
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


class UniversalWorkerHealthState(
    str,
    Enum,
):

    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"
    UNKNOWN = "UNKNOWN"


def _validate_optional_health_bool(
    value: Any,
    *,
    field_name: str,
) -> bool | None:

    if value is None:

        return None

    if type(value) is not bool:

        raise UniversalWorkerHealthError(
            (
                field_name
                + " must be bool or None."
            ),
            code="invalid_worker_health_signal",
            value={
                "field_name": field_name,
                "value": value,
            },
        )

    return value


def _validate_worker_registration(
    value: Any,
) -> UniversalWorkerRegistration:

    if not isinstance(
        value,
        UniversalWorkerRegistration,
    ):

        raise UniversalWorkerHealthError(
            (
                "worker must be a "
                "UniversalWorkerRegistration."
            ),
            code="invalid_worker_registration",
            value=value,
        )

    return value


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalWorkerHealthEvidence:

    health_check_passed: bool | None = None

    critical_failure_present: bool | None = None

    degraded_condition_present: bool | None = None

    schema_version: str = (
        UNIVERSAL_WORKER_HEALTH_EVIDENCE_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        object.__setattr__(
            self,
            "health_check_passed",
            _validate_optional_health_bool(
                self.health_check_passed,
                field_name="health_check_passed",
            ),
        )

        object.__setattr__(
            self,
            "critical_failure_present",
            _validate_optional_health_bool(
                self.critical_failure_present,
                field_name="critical_failure_present",
            ),
        )

        object.__setattr__(
            self,
            "degraded_condition_present",
            _validate_optional_health_bool(
                self.degraded_condition_present,
                field_name="degraded_condition_present",
            ),
        )

        if (
            self.schema_version
            != UNIVERSAL_WORKER_HEALTH_EVIDENCE_SCHEMA_VERSION
        ):

            raise UniversalWorkerHealthError(
                (
                    "Invalid Worker Health Evidence "
                    "schema_version."
                ),
                code=(
                    "invalid_worker_health_"
                    "evidence_schema_version"
                ),
                value=self.schema_version,
            )

    @property
    def supplied_signal_count(
        self,
    ) -> int:

        return sum(
            value is not None
            for value in (
                self.health_check_passed,
                self.critical_failure_present,
                self.degraded_condition_present,
            )
        )


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalWorkerHealthResult:

    worker_id: str

    worker_instance_id: str

    state: UniversalWorkerHealthState

    evidence: UniversalWorkerHealthEvidence

    schema_version: str = (
        UNIVERSAL_WORKER_HEALTH_RESULT_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        if (
            not isinstance(
                self.worker_id,
                str,
            )
            or
            not self.worker_id
        ):

            raise UniversalWorkerHealthError(
                (
                    "worker_id must be a "
                    "non-empty string."
                ),
                code="invalid_health_worker_id",
                value=self.worker_id,
            )

        if (
            not isinstance(
                self.worker_instance_id,
                str,
            )
            or
            not self.worker_instance_id
        ):

            raise UniversalWorkerHealthError(
                (
                    "worker_instance_id must be a "
                    "non-empty string."
                ),
                code=(
                    "invalid_health_"
                    "worker_instance_id"
                ),
                value=self.worker_instance_id,
            )

        if not isinstance(
            self.state,
            UniversalWorkerHealthState,
        ):

            raise UniversalWorkerHealthError(
                (
                    "state must be a "
                    "UniversalWorkerHealthState."
                ),
                code="invalid_worker_health_state",
                value=self.state,
            )

        if not isinstance(
            self.evidence,
            UniversalWorkerHealthEvidence,
        ):

            raise UniversalWorkerHealthError(
                (
                    "evidence must be "
                    "UniversalWorkerHealthEvidence."
                ),
                code="invalid_worker_health_evidence",
                value=self.evidence,
            )

        expected_state = (
            classify_universal_worker_health_evidence(
                self.evidence
            )
        )

        if self.state is not expected_state:

            raise UniversalWorkerHealthError(
                (
                    "Worker Health result state is "
                    "inconsistent with its evidence."
                ),
                code=(
                    "inconsistent_worker_"
                    "health_result"
                ),
                value={
                    "state":
                        self.state.value,

                    "expected_state":
                        expected_state.value,
                },
            )

        if (
            self.schema_version
            != UNIVERSAL_WORKER_HEALTH_RESULT_SCHEMA_VERSION
        ):

            raise UniversalWorkerHealthError(
                (
                    "Invalid Worker Health Result "
                    "schema_version."
                ),
                code=(
                    "invalid_worker_health_"
                    "result_schema_version"
                ),
                value=self.schema_version,
            )

    @property
    def worker_identity(
        self,
    ) -> tuple[str, str]:

        return (
            self.worker_id,
            self.worker_instance_id,
        )

    @property
    def healthy(
        self,
    ) -> bool:

        return (
            self.state
            is UniversalWorkerHealthState.HEALTHY
        )


def create_universal_worker_health_evidence(
    *,
    health_check_passed: bool | None = None,
    critical_failure_present: bool | None = None,
    degraded_condition_present: bool | None = None,
) -> UniversalWorkerHealthEvidence:

    return UniversalWorkerHealthEvidence(
        health_check_passed=health_check_passed,
        critical_failure_present=critical_failure_present,
        degraded_condition_present=degraded_condition_present,
    )


def classify_universal_worker_health_evidence(
    evidence: UniversalWorkerHealthEvidence,
) -> UniversalWorkerHealthState:

    if not isinstance(
        evidence,
        UniversalWorkerHealthEvidence,
    ):

        raise UniversalWorkerHealthError(
            (
                "evidence must be "
                "UniversalWorkerHealthEvidence."
            ),
            code="invalid_worker_health_evidence",
            value=evidence,
        )

    if (
        evidence.critical_failure_present
        is True
    ):

        return (
            UniversalWorkerHealthState.UNHEALTHY
        )

    if (
        evidence.health_check_passed
        is False
    ):

        return (
            UniversalWorkerHealthState.UNHEALTHY
        )

    if (
        evidence.degraded_condition_present
        is True
    ):

        return (
            UniversalWorkerHealthState.DEGRADED
        )

    if (
        evidence.health_check_passed
        is True
    ):

        return (
            UniversalWorkerHealthState.HEALTHY
        )

    return (
        UniversalWorkerHealthState.UNKNOWN
    )


def evaluate_universal_worker_health(
    *,
    worker: UniversalWorkerRegistration,
    evidence: UniversalWorkerHealthEvidence,
) -> UniversalWorkerHealthResult:

    canonical_worker = (
        _validate_worker_registration(
            worker
        )
    )

    if not isinstance(
        evidence,
        UniversalWorkerHealthEvidence,
    ):

        raise UniversalWorkerHealthError(
            (
                "evidence must be "
                "UniversalWorkerHealthEvidence."
            ),
            code="invalid_worker_health_evidence",
            value=evidence,
        )

    state = (
        classify_universal_worker_health_evidence(
            evidence
        )
    )

    return UniversalWorkerHealthResult(
        worker_id=canonical_worker.worker_id,
        worker_instance_id=(
            canonical_worker.worker_instance_id
        ),
        state=state,
        evidence=evidence,
    )


def explain_universal_worker_health_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "4.1.5",

            "component":
                "Universal Worker Health",

            "version":
                UNIVERSAL_WORKER_HEALTH_VERSION,

            "evidence_schema_version":
                UNIVERSAL_WORKER_HEALTH_EVIDENCE_SCHEMA_VERSION,

            "result_schema_version":
                UNIVERSAL_WORKER_HEALTH_RESULT_SCHEMA_VERSION,

            "states": (
                "HEALTHY",
                "DEGRADED",
                "UNHEALTHY",
                "UNKNOWN",
            ),

            "input_rule": (
                "4.1.5 consumes a canonical "
                "UniversalWorkerRegistration and "
                "caller-supplied health evidence"
            ),

            "evidence_rule": (
                "health_check_passed, "
                "critical_failure_present and "
                "degraded_condition_present are "
                "independent optional bool signals; "
                "None means evidence not supplied"
            ),

            "precedence_rule": (
                "critical failure -> UNHEALTHY; "
                "failed health check -> UNHEALTHY; "
                "degraded condition -> DEGRADED; "
                "passed health check -> HEALTHY; "
                "otherwise -> UNKNOWN"
            ),

            "unknown_rule": (
                "absence of positive health evidence "
                "must not be interpreted as HEALTHY"
            ),

            "operational_status_boundary": (
                "ACTIVE, IDLE, BUSY, OFFLINE and FAILED "
                "operational states are not Worker "
                "Health states"
            ),

            "heartbeat_boundary": (
                "heartbeat production, freshness, "
                "liveness and stale-worker detection "
                "belong outside 4.1.5"
            ),

            "availability_boundary": (
                "Worker Health does not decide whether "
                "a worker is available, eligible or "
                "assignable"
            ),

            "telemetry_boundary": (
                "4.1.5 does not invent worker CPU, "
                "memory, latency, error-rate or other "
                "telemetry thresholds"
            ),

            "recovery_boundary": (
                "UNHEALTHY classification does not "
                "restart, recover, drain, shut down or "
                "replace a worker"
            ),

            "purity_rule": (
                "Worker Health is deterministic over "
                "caller-supplied evidence and performs "
                "no state lookup, persistence or "
                "mutation"
            ),

            "prohibitions": (
                "does not emit worker heartbeats",
                "does not read worker heartbeats",
                "does not calculate heartbeat freshness",
                "does not detect stale workers",
                "does not determine worker liveness",
                "does not determine worker readiness",
                "does not inspect ACTIVE IDLE BUSY OFFLINE FAILED operational status",
                "does not determine worker availability",
                "does not determine assignment eligibility",
                "does not assign workers",
                "does not acquire leases",
                "does not renew leases",
                "does not release leases",
                "does not inspect worker capacity",
                "does not inspect worker capabilities",
                "does not inspect worker pools",
                "does not invent CPU thresholds",
                "does not invent memory thresholds",
                "does not invent latency thresholds",
                "does not invent error-rate thresholds",
                "does not restart workers",
                "does not recover workers",
                "does not scale workers",
                "does not drain workers",
                "does not shut down workers",
                "does not access Runtime State Store",
                "does not access orchestration",
                "does not mutate Queue Infrastructure",
                "does not persist health results",
                "does not perform filesystem I/O",
                "does not perform network I/O",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_WORKER_HEALTH_VERSION",
    "UNIVERSAL_WORKER_HEALTH_EVIDENCE_SCHEMA_VERSION",
    "UNIVERSAL_WORKER_HEALTH_RESULT_SCHEMA_VERSION",
    "UniversalWorkerHealthError",
    "UniversalWorkerHealthState",
    "UniversalWorkerHealthEvidence",
    "UniversalWorkerHealthResult",
    "create_universal_worker_health_evidence",
    "classify_universal_worker_health_evidence",
    "evaluate_universal_worker_health",
    "explain_universal_worker_health_v1",
]
