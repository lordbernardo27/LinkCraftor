from __future__ import annotations

import ast
import hashlib
import importlib
import sys
from pathlib import Path


ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
)

HEALTH_PATH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_worker"
    / "health.py"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_4_1_5_worker_health_initial_implementation.txt"
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


def ast_sha(
    path: Path,
) -> str:

    source = path.read_text(
        encoding="utf-8-sig"
    )

    tree = ast.parse(
        source
    )

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

    actual = ast_sha(
        path
    )

    if actual != expected:

        raise SystemExit(
            (
                "Protected authority mismatch before "
                "4.1.5 implementation: "
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
'''


ast.parse(
    SOURCE
)

HEALTH_PATH.write_text(
    SOURCE,
    encoding="utf-8",
)


# ============================================================
# IMPORT NEW AUTHORITY
# ============================================================

sys.path.insert(
    0,
    str(ROOT),
)

registration = importlib.import_module(
    "backend.server.runtime.universal_worker.registration"
)

health_name = (
    "backend.server.runtime."
    "universal_worker.health"
)

sys.modules.pop(
    health_name,
    None,
)

health = importlib.import_module(
    health_name
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
# VERSION / SCHEMAS / STATES
# ============================================================

check(
    "version",
    health.UNIVERSAL_WORKER_HEALTH_VERSION
    == "universal_worker_health_v4.1.5",
)

check(
    "evidence_schema",
    health.UNIVERSAL_WORKER_HEALTH_EVIDENCE_SCHEMA_VERSION
    == "universal_worker_health_evidence_schema_v1",
)

check(
    "result_schema",
    health.UNIVERSAL_WORKER_HEALTH_RESULT_SCHEMA_VERSION
    == "universal_worker_health_result_schema_v1",
)

check(
    "states_exact",
    tuple(
        item.value
        for item in health.UniversalWorkerHealthState
    )
    == (
        "HEALTHY",
        "DEGRADED",
        "UNHEALTHY",
        "UNKNOWN",
    ),
)


# ============================================================
# WORKER FIXTURE
# ============================================================

worker = (
    registration.create_universal_worker_registration(
        worker_id="worker-a",
        worker_type="general",
        worker_instance_id="instance-001",
        runtime_version="runtime-v1",
        host_id="host-a",
        registered_at="2026-08-15T20:00:00Z",
    )
)


# ============================================================
# CANONICAL CLASSIFICATION MATRIX
# ============================================================

healthy_evidence = (
    health.create_universal_worker_health_evidence(
        health_check_passed=True,
    )
)

degraded_evidence = (
    health.create_universal_worker_health_evidence(
        health_check_passed=True,
        degraded_condition_present=True,
    )
)

critical_evidence = (
    health.create_universal_worker_health_evidence(
        health_check_passed=True,
        critical_failure_present=True,
        degraded_condition_present=True,
    )
)

failed_check_evidence = (
    health.create_universal_worker_health_evidence(
        health_check_passed=False,
    )
)

unknown_evidence = (
    health.create_universal_worker_health_evidence()
)


check(
    "healthy_classification",
    health.classify_universal_worker_health_evidence(
        healthy_evidence
    )
    is health.UniversalWorkerHealthState.HEALTHY,
)

check(
    "degraded_precedence",
    health.classify_universal_worker_health_evidence(
        degraded_evidence
    )
    is health.UniversalWorkerHealthState.DEGRADED,
)

check(
    "critical_precedence",
    health.classify_universal_worker_health_evidence(
        critical_evidence
    )
    is health.UniversalWorkerHealthState.UNHEALTHY,
)

check(
    "failed_check_unhealthy",
    health.classify_universal_worker_health_evidence(
        failed_check_evidence
    )
    is health.UniversalWorkerHealthState.UNHEALTHY,
)

check(
    "empty_evidence_unknown",
    health.classify_universal_worker_health_evidence(
        unknown_evidence
    )
    is health.UniversalWorkerHealthState.UNKNOWN,
)


negative_only_evidence = (
    health.create_universal_worker_health_evidence(
        critical_failure_present=False,
        degraded_condition_present=False,
    )
)


check(
    "negative_only_unknown",
    health.classify_universal_worker_health_evidence(
        negative_only_evidence
    )
    is health.UniversalWorkerHealthState.UNKNOWN,
)


# ============================================================
# EVIDENCE COUNTS
# ============================================================

check(
    "unknown_signal_count",
    unknown_evidence.supplied_signal_count
    == 0,
)

check(
    "healthy_signal_count",
    healthy_evidence.supplied_signal_count
    == 1,
)

check(
    "critical_signal_count",
    critical_evidence.supplied_signal_count
    == 3,
)


# ============================================================
# RESULT
# ============================================================

result = (
    health.evaluate_universal_worker_health(
        worker=worker,
        evidence=degraded_evidence,
    )
)


check(
    "result_identity",
    result.worker_identity
    == (
        "worker-a",
        "instance-001",
    ),
)

check(
    "result_state",
    result.state
    is health.UniversalWorkerHealthState.DEGRADED,
)

check(
    "result_healthy_false",
    result.healthy
    is False,
)

check(
    "result_evidence_identity",
    result.evidence
    is degraded_evidence,
)


healthy_result = (
    health.evaluate_universal_worker_health(
        worker=worker,
        evidence=healthy_evidence,
    )
)


check(
    "healthy_result_boolean",
    healthy_result.healthy
    is True,
)


# ============================================================
# STRICT OPTIONAL BOOL
# ============================================================

for field_name in (
    "health_check_passed",
    "critical_failure_present",
    "degraded_condition_present",
):

    for bad in (
        0,
        1,
        "",
        "true",
        [],
        {},
        (),
    ):

        kwargs = {
            "health_check_passed": None,
            "critical_failure_present": None,
            "degraded_condition_present": None,
        }

        kwargs[
            field_name
        ] = bad

        try:

            health.create_universal_worker_health_evidence(
                **kwargs
            )

        except health.UniversalWorkerHealthError as exc:

            rejected = (
                exc.code
                == "invalid_worker_health_signal"
            )

        else:

            rejected = False

        check(
            (
                "strict_signal_"
                + field_name
                + "_"
                + type(bad).__name__
                + "_"
                + repr(bad)
            ),
            rejected,
        )


# ============================================================
# INVALID WORKER
# ============================================================

for bad in (
    None,
    True,
    0,
    "",
    {},
    [],
):

    try:

        health.evaluate_universal_worker_health(
            worker=bad,
            evidence=healthy_evidence,
        )

    except health.UniversalWorkerHealthError as exc:

        rejected = (
            exc.code
            == "invalid_worker_registration"
        )

    else:

        rejected = False

    check(
        "invalid_worker_"
        + type(bad).__name__,
        rejected,
    )


# ============================================================
# INVALID EVIDENCE
# ============================================================

for bad in (
    None,
    True,
    0,
    "",
    {},
    [],
):

    try:

        health.classify_universal_worker_health_evidence(
            bad
        )

    except health.UniversalWorkerHealthError as exc:

        rejected = (
            exc.code
            == "invalid_worker_health_evidence"
        )

    else:

        rejected = False

    check(
        "invalid_evidence_"
        + type(bad).__name__,
        rejected,
    )


# ============================================================
# SCHEMA TAMPERING
# ============================================================

try:

    health.UniversalWorkerHealthEvidence(
        health_check_passed=True,
        schema_version="wrong",
    )

except health.UniversalWorkerHealthError as exc:

    rejected = (
        exc.code
        == "invalid_worker_health_evidence_schema_version"
    )

else:

    rejected = False


check(
    "evidence_schema_tamper_rejected",
    rejected,
)


try:

    health.UniversalWorkerHealthResult(
        worker_id="worker-a",
        worker_instance_id="instance-001",
        state=(
            health.UniversalWorkerHealthState.HEALTHY
        ),
        evidence=healthy_evidence,
        schema_version="wrong",
    )

except health.UniversalWorkerHealthError as exc:

    rejected = (
        exc.code
        == "invalid_worker_health_result_schema_version"
    )

else:

    rejected = False


check(
    "result_schema_tamper_rejected",
    rejected,
)


# ============================================================
# INCONSISTENT RESULT ATTACK
# ============================================================

try:

    health.UniversalWorkerHealthResult(
        worker_id="worker-a",
        worker_instance_id="instance-001",
        state=(
            health.UniversalWorkerHealthState.HEALTHY
        ),
        evidence=critical_evidence,
    )

except health.UniversalWorkerHealthError as exc:

    rejected = (
        exc.code
        == "inconsistent_worker_health_result"
    )

else:

    rejected = False


check(
    "inconsistent_result_rejected",
    rejected,
)


# ============================================================
# IMMUTABILITY
# ============================================================

for obj, field_name in (
    (
        healthy_evidence,
        "health_check_passed",
    ),
    (
        result,
        "state",
    ),
    (
        result,
        "evidence",
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
        "immutable_"
        + type(obj).__name__,
        immutable,
    )


# ============================================================
# REGISTRATION NOT MUTATED
# ============================================================

before_worker = (
    worker.to_dict()
)


health.evaluate_universal_worker_health(
    worker=worker,
    evidence=critical_evidence,
)


after_worker = (
    worker.to_dict()
)


check(
    "worker_registration_not_mutated",
    before_worker
    == after_worker,
)


# ============================================================
# EXPLANATION CONTRACT
# ============================================================

explanation = (
    health.explain_universal_worker_health_v1()
)


check(
    "explanation_phase",
    explanation.get(
        "phase"
    )
    == "4.1.5",
)

check(
    "explanation_component",
    explanation.get(
        "component"
    )
    == "Universal Worker Health",
)

check(
    "states_explained",
    tuple(
        explanation.get(
            "states"
        )
    )
    == (
        "HEALTHY",
        "DEGRADED",
        "UNHEALTHY",
        "UNKNOWN",
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
    "none_means_unsupplied",
    "None means evidence not supplied"
    in explanation.get(
        "evidence_rule",
        "",
    ),
)

check(
    "precedence_explained",
    (
        "critical failure -> UNHEALTHY"
        in explanation.get(
            "precedence_rule",
            "",
        )
        and
        "degraded condition -> DEGRADED"
        in explanation.get(
            "precedence_rule",
            "",
        )
    ),
)

check(
    "unknown_not_healthy",
    "must not be interpreted as HEALTHY"
    in explanation.get(
        "unknown_rule",
        "",
    ),
)

check(
    "operational_status_separate",
    "not Worker Health states"
    in explanation.get(
        "operational_status_boundary",
        "",
    ),
)

check(
    "heartbeat_separate",
    "outside 4.1.5"
    in explanation.get(
        "heartbeat_boundary",
        "",
    ),
)

check(
    "availability_separate",
    "does not decide"
    in explanation.get(
        "availability_boundary",
        "",
    ),
)

check(
    "no_threshold_invention",
    "does not invent"
    in explanation.get(
        "telemetry_boundary",
        "",
    ),
)

check(
    "recovery_separate",
    "does not"
    in explanation.get(
        "recovery_boundary",
        "",
    ),
)

check(
    "pure_no_state",
    (
        "no state lookup"
        in explanation.get(
            "purity_rule",
            "",
        )
        and
        "no state lookup, persistence or mutation"
        in explanation.get(
            "purity_rule",
            "",
        )
    ),
)


# ============================================================
# PROHIBITIONS
# ============================================================

required_prohibitions = (
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
# STATIC IMPORT BOUNDARY
# ============================================================

source = HEALTH_PATH.read_text(
    encoding="utf-8-sig"
)

tree = ast.parse(
    source
)


backend_imports = []


for node in ast.walk(
    tree
):

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

    elif isinstance(
        node,
        ast.Import,
    ):

        for alias in node.names:

            if alias.name.startswith(
                "backend.server"
            ):

                backend_imports.append(
                    alias.name
                )


check(
    "only_registration_backend_import",
    backend_imports
    == [
        "backend.server.runtime.universal_worker.registration"
    ],
    backend_imports,
)


# ============================================================
# FORBIDDEN CALL BOUNDARY
# ============================================================

forbidden_names = {
    "open",
    "read_text",
    "write_text",
    "mkdir",
    "unlink",
    "remove",
    "now",
    "utcnow",
    "time",
    "worker_heartbeat",
    "inspect_workers",
    "get_latest_worker_statuses",
    "get_runtime_state_store_registry",
    "assign_universal_worker",
    "acquire_universal_worker_lease",
    "renew_universal_worker_lease",
    "release_universal_worker_lease",
    "dispatch_job",
    "execute_job",
    "recover_worker",
    "restart_worker",
    "save_job",
    "get_job",
}


forbidden_calls = []


for node in ast.walk(
    tree
):

    if not isinstance(
        node,
        ast.Call,
    ):

        continue

    if isinstance(
        node.func,
        ast.Name,
    ):

        call_name = (
            node.func.id
        )

    elif isinstance(
        node.func,
        ast.Attribute,
    ):

        call_name = (
            node.func.attr
        )

    else:

        continue

    if call_name in forbidden_names:

        forbidden_calls.append(
            (
                call_name,
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

    actual = ast_sha(
        path
    )

    check(
        "protected_"
        + name,
        actual
        == expected,
        actual,
    )


# ============================================================
# HEALTH AST
# ============================================================

health_ast = ast_sha(
    HEALTH_PATH
)


check(
    "health_ast_generated",
    len(
        health_ast
    )
    == 64,
    health_ast,
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

total = len(
    checks
)


lines = [
    (
        "PHASE 4.1.5 — UNIVERSAL WORKER "
        "HEALTH INITIAL IMPLEMENTATION"
    ),
    "=" * 112,
    "",
    (
        "WORKER HEALTH AST SHA256: "
        + health_ast
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
            "INITIAL WORKER HEALTH RESULT: "
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
        "QUEUE INFRASTRUCTURE MODIFIED: NO",
        "UNIVERSAL JOB CONTRACT MODIFIED: NO",
        "EXISTING UNIVERSAL RUNTIME WORKER MODIFIED: NO",
        "RUNTIME REGISTRATION MODIFIED: NO",
        "RUNTIME INFRASTRUCTURE MODIFIED: NO",
        "ORCHESTRATION MODIFIED: NO",
        "WORKER HEARTBEAT READ OR WRITTEN: NO",
        "HEARTBEAT FRESHNESS CALCULATED: NO",
        "STALE WORKER DETECTION PERFORMED: NO",
        "WORKER LIVENESS DECIDED: NO",
        "WORKER READINESS DECIDED: NO",
        "WORKER AVAILABILITY DECIDED: NO",
        "WORKER ASSIGNMENT ELIGIBILITY DECIDED: NO",
        "WORKER CAPACITY INSPECTED: NO",
        "WORKER CAPABILITY INSPECTED: NO",
        "WORKER POOL INSPECTED: NO",
        "WORKER RECOVERY PERFORMED: NO",
        "WORKER RESTARTED: NO",
        "WORKER SCALED: NO",
        "WORKER DRAINED: NO",
        "WORKER SHUT DOWN: NO",
        "RUNTIME STATE STORE ACCESSED: NO",
        "HEALTH RESULT PERSISTED: NO",
        "TELEMETRY THRESHOLDS INVENTED: NO",
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
        "Phase 4.1.5 Worker Health initial implementation failed."
    )
