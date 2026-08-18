from __future__ import annotations

import ast
import hashlib
import importlib
import sys
from pathlib import Path


ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
)

SHUTDOWN_PATH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_worker"
    / "shutdown.py"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_4_1_8_worker_shutdown_initial_implementation.txt"
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

    "worker_scaling": (
        ROOT / "backend/server/runtime/universal_worker/scaling.py",
        "8EC818E4EF4CA7DBCADCFCB93FD99BC80AAD4CE8AEBE1CDE63CCC44FA8488FF6",
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

    "runtime_shutdown_process": (
        ROOT / "backend/server/runtime/runtime_shutdown_process.py",
        None,
    ),

    "runtime_lifecycle_manager": (
        ROOT / "backend/server/runtime/runtime_lifecycle_manager.py",
        None,
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

    tree = ast.parse(source)

    canonical = ast.dump(
        tree,
        annotate_fields=True,
        include_attributes=False,
    )

    return hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest().upper()


# Capture currently-unfrozen integration ASTs so this run can
# certify that we did not modify them.
dynamic_protected_asts = {}


for name in (
    "runtime_shutdown_process",
    "runtime_lifecycle_manager",
):

    path, _ = PROTECTED[name]

    if not path.exists():

        raise SystemExit(
            "Required runtime authority missing: "
            + str(path)
        )

    dynamic_protected_asts[
        name
    ] = ast_sha(path)


for name, (
    path,
    expected,
) in PROTECTED.items():

    if expected is None:

        expected = (
            dynamic_protected_asts[
                name
            ]
        )

    actual = ast_sha(path)

    if actual != expected:

        raise SystemExit(
            (
                "Protected authority mismatch before "
                "4.1.8 implementation: "
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
'''


ast.parse(SOURCE)

SHUTDOWN_PATH.write_text(
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

module_name = (
    "backend.server.runtime."
    "universal_worker.shutdown"
)

sys.modules.pop(
    module_name,
    None,
)

shutdown = importlib.import_module(
    module_name
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
# VERSION / SCHEMAS / ENUMS
# ============================================================

check(
    "version",
    shutdown.UNIVERSAL_WORKER_SHUTDOWN_VERSION
    == "universal_worker_shutdown_v4.1.8",
)

check(
    "evidence_schema",
    shutdown.UNIVERSAL_WORKER_SHUTDOWN_EVIDENCE_SCHEMA_VERSION
    == "universal_worker_shutdown_evidence_schema_v1",
)

check(
    "result_schema",
    shutdown.UNIVERSAL_WORKER_SHUTDOWN_RESULT_SCHEMA_VERSION
    == "universal_worker_shutdown_result_schema_v1",
)

check(
    "max_active_count",
    shutdown.MAX_UNIVERSAL_WORKER_SHUTDOWN_ACTIVE_COUNT
    == 2_147_483_647,
)

check(
    "decisions_exact",
    tuple(
        item.value
        for item in shutdown.UniversalWorkerShutdownDecision
    )
    == (
        "NOT_REQUESTED",
        "BLOCKED",
        "READY",
    ),
)

check(
    "reasons_exact",
    tuple(
        item.value
        for item in shutdown.UniversalWorkerShutdownReason
    )
    == (
        "SHUTDOWN_NOT_REQUESTED",
        "ACTIVE_WORK_PRESENT",
        "ACTIVE_LEASES_PRESENT",
        "DRAIN_INCOMPLETE",
        "SHUTDOWN_READY",
    ),
)


# ============================================================
# NOT REQUESTED PRECEDENCE
# ============================================================

for drain_complete in (
    False,
    True,
):

    # drain_complete=True requires zero ownership evidence.
    work_values = (
        (0,)
        if drain_complete
        else
        (0, 1, 5)
    )

    lease_values = (
        (0,)
        if drain_complete
        else
        (0, 1, 5)
    )

    for active_work_count in work_values:

        for active_lease_count in lease_values:

            evidence = (
                shutdown.create_universal_worker_shutdown_evidence(
                    shutdown_requested=False,
                    drain_complete=drain_complete,
                    active_work_count=active_work_count,
                    active_lease_count=active_lease_count,
                )
            )

            result = (
                shutdown.evaluate_universal_worker_shutdown(
                    evidence
                )
            )

            check(
                (
                    "not_requested_"
                    + str(drain_complete)
                    + "_"
                    + str(active_work_count)
                    + "_"
                    + str(active_lease_count)
                ),
                (
                    result.decision
                    is shutdown.UniversalWorkerShutdownDecision.NOT_REQUESTED
                    and
                    result.reason
                    is (
                        shutdown.UniversalWorkerShutdownReason
                        .SHUTDOWN_NOT_REQUESTED
                    )
                ),
            )


# ============================================================
# ACTIVE WORK BLOCK
# ============================================================

for active_work_count in (
    1,
    2,
    100,
):

    evidence = (
        shutdown.create_universal_worker_shutdown_evidence(
            shutdown_requested=True,
            drain_complete=False,
            active_work_count=active_work_count,
            active_lease_count=0,
        )
    )

    result = (
        shutdown.evaluate_universal_worker_shutdown(
            evidence
        )
    )

    check(
        "active_work_blocks_"
        + str(active_work_count),
        (
            result.decision
            is shutdown.UniversalWorkerShutdownDecision.BLOCKED
            and
            result.reason
            is (
                shutdown.UniversalWorkerShutdownReason
                .ACTIVE_WORK_PRESENT
            )
        ),
    )


# ============================================================
# ACTIVE LEASE BLOCK
# ============================================================

for active_lease_count in (
    1,
    2,
    100,
):

    evidence = (
        shutdown.create_universal_worker_shutdown_evidence(
            shutdown_requested=True,
            drain_complete=False,
            active_work_count=0,
            active_lease_count=active_lease_count,
        )
    )

    result = (
        shutdown.evaluate_universal_worker_shutdown(
            evidence
        )
    )

    check(
        "active_lease_blocks_"
        + str(active_lease_count),
        (
            result.decision
            is shutdown.UniversalWorkerShutdownDecision.BLOCKED
            and
            result.reason
            is (
                shutdown.UniversalWorkerShutdownReason
                .ACTIVE_LEASES_PRESENT
            )
        ),
    )


# ============================================================
# ACTIVE WORK PRECEDES ACTIVE LEASE
# ============================================================

both_active = (
    shutdown.create_universal_worker_shutdown_evidence(
        shutdown_requested=True,
        drain_complete=False,
        active_work_count=3,
        active_lease_count=4,
    )
)

both_active_result = (
    shutdown.evaluate_universal_worker_shutdown(
        both_active
    )
)

check(
    "active_work_precedes_active_lease",
    (
        both_active_result.decision
        is shutdown.UniversalWorkerShutdownDecision.BLOCKED
        and
        both_active_result.reason
        is (
            shutdown.UniversalWorkerShutdownReason
            .ACTIVE_WORK_PRESENT
        )
    ),
)


# ============================================================
# DRAIN INCOMPLETE
# ============================================================

drain_incomplete = (
    shutdown.create_universal_worker_shutdown_evidence(
        shutdown_requested=True,
        drain_complete=False,
        active_work_count=0,
        active_lease_count=0,
    )
)

drain_incomplete_result = (
    shutdown.evaluate_universal_worker_shutdown(
        drain_incomplete
    )
)

check(
    "drain_incomplete_blocks",
    (
        drain_incomplete_result.decision
        is shutdown.UniversalWorkerShutdownDecision.BLOCKED
        and
        drain_incomplete_result.reason
        is (
            shutdown.UniversalWorkerShutdownReason
            .DRAIN_INCOMPLETE
        )
    ),
)


# ============================================================
# READY
# ============================================================

ready_evidence = (
    shutdown.create_universal_worker_shutdown_evidence(
        shutdown_requested=True,
        drain_complete=True,
        active_work_count=0,
        active_lease_count=0,
    )
)

ready_result = (
    shutdown.evaluate_universal_worker_shutdown(
        ready_evidence
    )
)

check(
    "ready_decision",
    ready_result.decision
    is shutdown.UniversalWorkerShutdownDecision.READY,
)

check(
    "ready_reason",
    ready_result.reason
    is shutdown.UniversalWorkerShutdownReason.SHUTDOWN_READY,
)

check(
    "shutdown_ready_property",
    ready_result.shutdown_ready
    is True,
)

check(
    "shutdown_blocked_property_false",
    ready_result.shutdown_blocked
    is False,
)


# ============================================================
# CONTRADICTION REJECTION
# ============================================================

try:

    shutdown.create_universal_worker_shutdown_evidence(
        shutdown_requested=True,
        drain_complete=True,
        active_work_count=1,
        active_lease_count=0,
    )

except shutdown.UniversalWorkerShutdownError as exc:

    rejected = (
        exc.code
        == "drain_complete_active_work_contradiction"
    )

else:

    rejected = False


check(
    "drain_complete_active_work_contradiction",
    rejected,
)


try:

    shutdown.create_universal_worker_shutdown_evidence(
        shutdown_requested=True,
        drain_complete=True,
        active_work_count=0,
        active_lease_count=1,
    )

except shutdown.UniversalWorkerShutdownError as exc:

    rejected = (
        exc.code
        == "drain_complete_active_lease_contradiction"
    )

else:

    rejected = False


check(
    "drain_complete_active_lease_contradiction",
    rejected,
)


# ============================================================
# STRICT BOOLEAN VALIDATION
# ============================================================

for field_name in (
    "shutdown_requested",
    "drain_complete",
):

    for bad in (
        None,
        0,
        1,
        -1,
        0.0,
        1.0,
        "",
        "true",
        "false",
        [],
        {},
        (),
    ):

        kwargs = {
            "shutdown_requested": False,
            "drain_complete": False,
            "active_work_count": 0,
            "active_lease_count": 0,
        }

        kwargs[
            field_name
        ] = bad

        try:

            shutdown.create_universal_worker_shutdown_evidence(
                **kwargs
            )

        except shutdown.UniversalWorkerShutdownError as exc:

            rejected = (
                exc.code
                == "invalid_worker_shutdown_boolean"
            )

        else:

            rejected = False

        check(
            (
                "strict_boolean_"
                + field_name
                + "_"
                + type(bad).__name__
                + "_"
                + repr(bad)
            ),
            rejected,
        )


# ============================================================
# STRICT COUNT VALIDATION
# ============================================================

for field_name in (
    "active_work_count",
    "active_lease_count",
):

    for bad in (
        None,
        True,
        False,
        -1,
        -10,
        0.0,
        1.0,
        "",
        "1",
        [],
        {},
        (),
    ):

        kwargs = {
            "shutdown_requested": False,
            "drain_complete": False,
            "active_work_count": 0,
            "active_lease_count": 0,
        }

        kwargs[
            field_name
        ] = bad

        try:

            shutdown.create_universal_worker_shutdown_evidence(
                **kwargs
            )

        except shutdown.UniversalWorkerShutdownError as exc:

            rejected = (
                exc.code
                == "invalid_worker_shutdown_count"
            )

        else:

            rejected = False

        check(
            (
                "strict_count_"
                + field_name
                + "_"
                + type(bad).__name__
                + "_"
                + repr(bad)
            ),
            rejected,
        )


# ============================================================
# COUNT MAXIMUM
# ============================================================

maximum = (
    shutdown.MAX_UNIVERSAL_WORKER_SHUTDOWN_ACTIVE_COUNT
)

max_evidence = (
    shutdown.create_universal_worker_shutdown_evidence(
        shutdown_requested=False,
        drain_complete=False,
        active_work_count=maximum,
        active_lease_count=maximum,
    )
)

check(
    "maximum_active_work_count_accepted",
    max_evidence.active_work_count
    == maximum,
)

check(
    "maximum_active_lease_count_accepted",
    max_evidence.active_lease_count
    == maximum,
)


for field_name in (
    "active_work_count",
    "active_lease_count",
):

    kwargs = {
        "shutdown_requested": False,
        "drain_complete": False,
        "active_work_count": 0,
        "active_lease_count": 0,
    }

    kwargs[
        field_name
    ] = maximum + 1

    try:

        shutdown.create_universal_worker_shutdown_evidence(
            **kwargs
        )

    except shutdown.UniversalWorkerShutdownError as exc:

        rejected = (
            exc.code
            == "worker_shutdown_count_too_large"
        )

    else:

        rejected = False

    check(
        "count_overflow_"
        + field_name,
        rejected,
    )


# ============================================================
# INVALID EVIDENCE
# ============================================================

for bad in (
    None,
    True,
    False,
    0,
    1,
    "",
    [],
    {},
    (),
):

    try:

        shutdown.decide_universal_worker_shutdown(
            bad
        )

    except shutdown.UniversalWorkerShutdownError as exc:

        rejected_decision = (
            exc.code
            == "invalid_worker_shutdown_evidence"
        )

    else:

        rejected_decision = False

    check(
        "invalid_decision_evidence_"
        + type(bad).__name__
        + "_"
        + repr(bad),
        rejected_decision,
    )

    try:

        shutdown.evaluate_universal_worker_shutdown(
            bad
        )

    except shutdown.UniversalWorkerShutdownError as exc:

        rejected_evaluation = (
            exc.code
            == "invalid_worker_shutdown_evidence"
        )

    else:

        rejected_evaluation = False

    check(
        "invalid_evaluation_evidence_"
        + type(bad).__name__
        + "_"
        + repr(bad),
        rejected_evaluation,
    )


# ============================================================
# RESULT FORGERY
# ============================================================

try:

    shutdown.UniversalWorkerShutdownResult(
        decision=(
            shutdown.UniversalWorkerShutdownDecision.READY
        ),
        reason=(
            shutdown.UniversalWorkerShutdownReason.SHUTDOWN_READY
        ),
        shutdown_requested=True,
        drain_complete=False,
        active_work_count=0,
        active_lease_count=0,
    )

except shutdown.UniversalWorkerShutdownError as exc:

    rejected = (
        exc.code
        == "inconsistent_worker_shutdown_result"
    )

else:

    rejected = False


check(
    "forged_ready_result_rejected",
    rejected,
)


try:

    shutdown.UniversalWorkerShutdownResult(
        decision="READY",
        reason=(
            shutdown.UniversalWorkerShutdownReason.SHUTDOWN_READY
        ),
        shutdown_requested=True,
        drain_complete=True,
        active_work_count=0,
        active_lease_count=0,
    )

except shutdown.UniversalWorkerShutdownError as exc:

    rejected = (
        exc.code
        == "invalid_worker_shutdown_decision"
    )

else:

    rejected = False


check(
    "raw_decision_rejected",
    rejected,
)


try:

    shutdown.UniversalWorkerShutdownResult(
        decision=(
            shutdown.UniversalWorkerShutdownDecision.READY
        ),
        reason="SHUTDOWN_READY",
        shutdown_requested=True,
        drain_complete=True,
        active_work_count=0,
        active_lease_count=0,
    )

except shutdown.UniversalWorkerShutdownError as exc:

    rejected = (
        exc.code
        == "invalid_worker_shutdown_reason"
    )

else:

    rejected = False


check(
    "raw_reason_rejected",
    rejected,
)


# ============================================================
# SCHEMA TAMPERING
# ============================================================

try:

    shutdown.UniversalWorkerShutdownEvidence(
        shutdown_requested=False,
        drain_complete=False,
        active_work_count=0,
        active_lease_count=0,
        schema_version="tampered",
    )

except shutdown.UniversalWorkerShutdownError as exc:

    rejected = (
        exc.code
        == "invalid_worker_shutdown_evidence_schema_version"
    )

else:

    rejected = False


check(
    "evidence_schema_tamper_rejected",
    rejected,
)


try:

    shutdown.UniversalWorkerShutdownResult(
        decision=ready_result.decision,
        reason=ready_result.reason,
        shutdown_requested=True,
        drain_complete=True,
        active_work_count=0,
        active_lease_count=0,
        schema_version="tampered",
    )

except shutdown.UniversalWorkerShutdownError as exc:

    rejected = (
        exc.code
        == "invalid_worker_shutdown_result_schema_version"
    )

else:

    rejected = False


check(
    "result_schema_tamper_rejected",
    rejected,
)


# ============================================================
# IMMUTABILITY
# ============================================================

for obj, field_name in (
    (
        ready_evidence,
        "shutdown_requested",
    ),
    (
        ready_evidence,
        "drain_complete",
    ),
    (
        ready_evidence,
        "active_work_count",
    ),
    (
        ready_evidence,
        "active_lease_count",
    ),
    (
        ready_evidence,
        "schema_version",
    ),
    (
        ready_result,
        "decision",
    ),
    (
        ready_result,
        "reason",
    ),
    (
        ready_result,
        "shutdown_requested",
    ),
    (
        ready_result,
        "drain_complete",
    ),
    (
        ready_result,
        "active_work_count",
    ),
    (
        ready_result,
        "active_lease_count",
    ),
    (
        ready_result,
        "schema_version",
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


# ============================================================
# DETERMINISM
# ============================================================

check(
    "deterministic_decision",
    shutdown.decide_universal_worker_shutdown(
        ready_evidence
    )
    ==
    shutdown.decide_universal_worker_shutdown(
        ready_evidence
    ),
)

check(
    "deterministic_result",
    shutdown.evaluate_universal_worker_shutdown(
        ready_evidence
    )
    ==
    shutdown.evaluate_universal_worker_shutdown(
        ready_evidence
    ),
)


# ============================================================
# RESULT PROPERTIES
# ============================================================

blocked_result = (
    shutdown.evaluate_universal_worker_shutdown(
        drain_incomplete
    )
)

not_requested_result = (
    shutdown.evaluate_universal_worker_shutdown(
        shutdown.create_universal_worker_shutdown_evidence(
            shutdown_requested=False,
            drain_complete=False,
            active_work_count=0,
            active_lease_count=0,
        )
    )
)

check(
    "blocked_shutdown_ready_false",
    blocked_result.shutdown_ready
    is False,
)

check(
    "blocked_shutdown_blocked_true",
    blocked_result.shutdown_blocked
    is True,
)

check(
    "not_requested_ready_false",
    not_requested_result.shutdown_ready
    is False,
)

check(
    "not_requested_blocked_false",
    not_requested_result.shutdown_blocked
    is False,
)


# ============================================================
# EXPLANATION CONTRACT
# ============================================================

explanation = (
    shutdown.explain_universal_worker_shutdown_v1()
)


check(
    "explanation_phase",
    explanation.get(
        "phase"
    )
    == "4.1.8",
)

check(
    "explanation_component",
    explanation.get(
        "component"
    )
    == "Universal Worker Shutdown",
)

check(
    "decisions_explained",
    tuple(
        explanation.get(
            "decisions"
        )
    )
    == (
        "NOT_REQUESTED",
        "BLOCKED",
        "READY",
    ),
)

check(
    "caller_supplied_input",
    "caller-supplied"
    in explanation.get(
        "input_rule",
        "",
    ),
)

check(
    "not_requested_rule",
    "NOT_REQUESTED"
    in explanation.get(
        "not_requested_rule",
        "",
    ),
)

check(
    "active_work_rule",
    "active work"
    in explanation.get(
        "active_work_rule",
        "",
    ),
)

check(
    "active_lease_rule",
    "active lease"
    in explanation.get(
        "active_lease_rule",
        "",
    ),
)

check(
    "drain_rule",
    "drain_complete"
    in explanation.get(
        "drain_rule",
        "",
    ),
)

check(
    "ready_rule",
    (
        "zero active work"
        in explanation.get(
            "ready_rule",
            "",
        )
        and
        "zero active leases"
        in explanation.get(
            "ready_rule",
            "",
        )
    ),
)

check(
    "drain_boundary",
    "4.1.12 Worker Drain"
    in explanation.get(
        "drain_boundary",
        "",
    ),
)

check(
    "runtime_shutdown_boundary",
    "whole-runtime shutdown"
    in explanation.get(
        "runtime_shutdown_boundary",
        "",
    ),
)

check(
    "termination_boundary",
    "permission"
    in explanation.get(
        "termination_boundary",
        "",
    ),
)

check(
    "lease_boundary",
    "caller-supplied"
    in explanation.get(
        "lease_boundary",
        "",
    ),
)

check(
    "work_boundary",
    "caller-supplied"
    in explanation.get(
        "work_boundary",
        "",
    ),
)

check(
    "registration_pool_boundary",
    "does not deregister"
    in explanation.get(
        "registration_pool_boundary",
        "",
    ),
)

check(
    "heartbeat_boundary",
    "does not emit"
    in explanation.get(
        "heartbeat_boundary",
        "",
    ),
)

check(
    "health_scaling_boundary",
    "do not automatically imply shutdown"
    in explanation.get(
        "health_scaling_boundary",
        "",
    ),
)

check(
    "forced_shutdown_boundary",
    "outside"
    in explanation.get(
        "forced_shutdown_boundary",
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

source = SHUTDOWN_PATH.read_text(
    encoding="utf-8-sig"
)

tree = ast.parse(source)

backend_imports = []


for node in ast.walk(tree):

    if isinstance(
        node,
        ast.ImportFrom,
    ):

        module = (
            node.module
            or ""
        )

        if module.startswith(
            "backend.server"
        ):

            backend_imports.append(
                module
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
    "no_backend_imports",
    backend_imports
    == [],
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
    "sleep",
    "shutdown_runtime",
    "shutdown",
    "stop",
    "terminate",
    "kill",
    "signal",
    "drain",
    "release_universal_worker_lease",
    "renew_universal_worker_lease",
    "acquire_universal_worker_lease",
    "dequeue_job",
    "enqueue_job",
    "requeue_job",
    "cancel_job",
    "mark_job_failed",
    "evaluate_universal_worker_recovery",
    "evaluate_universal_worker_scaling",
    "evaluate_universal_worker_health",
    "worker_heartbeat",
    "get_latest_worker_statuses",
    "get_runtime_state_store_registry",
    "assign_universal_worker",
    "dispatch_job",
    "execute_job",
    "unregister",
}


forbidden_calls = []


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
# PROTECTED AUTHORITY MATRIX
# ============================================================

for name, (
    path,
    expected,
) in PROTECTED.items():

    if expected is None:

        expected = (
            dynamic_protected_asts[
                name
            ]
        )

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
# SHUTDOWN AST
# ============================================================

shutdown_ast = ast_sha(
    SHUTDOWN_PATH
)


check(
    "shutdown_ast_generated",
    len(
        shutdown_ast
    )
    == 64,
    shutdown_ast,
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
        "PHASE 4.1.8 — UNIVERSAL WORKER "
        "SHUTDOWN INITIAL IMPLEMENTATION"
    ),
    "=" * 112,
    "",
    (
        "WORKER SHUTDOWN AST SHA256: "
        + shutdown_ast
    ),
    (
        "RUNTIME SHUTDOWN PROCESS AST OBSERVED: "
        + dynamic_protected_asts[
            "runtime_shutdown_process"
        ]
    ),
    (
        "RUNTIME LIFECYCLE MANAGER AST OBSERVED: "
        + dynamic_protected_asts[
            "runtime_lifecycle_manager"
        ]
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
            "INITIAL WORKER SHUTDOWN RESULT: "
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
        "4.1.7 WORKER SCALING MODIFIED: NO",
        "QUEUE INFRASTRUCTURE MODIFIED: NO",
        "UNIVERSAL JOB CONTRACT MODIFIED: NO",
        "EXISTING UNIVERSAL RUNTIME WORKER MODIFIED: NO",
        "RUNTIME REGISTRATION MODIFIED: NO",
        "RUNTIME INFRASTRUCTURE MODIFIED: NO",
        "WHOLE-RUNTIME SHUTDOWN PROCESS MODIFIED: NO",
        "RUNTIME LIFECYCLE MANAGER MODIFIED: NO",
        "ORCHESTRATION MODIFIED: NO",
        "WORKER PROCESS STOPPED: NO",
        "WORKER PROCESS KILLED: NO",
        "WORKER PROCESS TERMINATED: NO",
        "OPERATING-SYSTEM SIGNAL SENT: NO",
        "WHOLE-RUNTIME SHUTDOWN INVOKED: NO",
        "WORKER DRAINED: NO",
        "DRAIN STATE DETERMINED: NO",
        "ACTIVE JOBS INSPECTED: NO",
        "ACTIVE LEASES INSPECTED: NO",
        "LEASE ACQUIRED/RENEWED/RELEASED: NO",
        "JOB CANCELLED: NO",
        "JOB FAILED: NO",
        "JOB REQUEUED: NO",
        "JOB/WORKER RECOVERY PERFORMED: NO",
        "WORKER DEREGISTERED: NO",
        "WORKER REGISTRATION DELETED: NO",
        "WORKER POOL MEMBERSHIP MODIFIED: NO",
        "WORKER HEARTBEAT EMITTED/DELETED/READ: NO",
        "WORKER HEALTH DECIDED: NO",
        "WORKER SCALING PERFORMED: NO",
        "WORKER ASSIGNED: NO",
        "REPLACEMENT WORKER PROVISIONED: NO",
        "QUEUE MUTATED: NO",
        "RUNTIME STATE STORE ACCESSED: NO",
        "SHUTDOWN RESULT PERSISTED: NO",
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
        "Phase 4.1.8 Worker Shutdown initial implementation failed."
    )
