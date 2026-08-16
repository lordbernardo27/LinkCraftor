from __future__ import annotations

import ast
import hashlib
import importlib
import sys
from pathlib import Path


ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
)

RECOVERY_PATH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_worker"
    / "recovery.py"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_4_1_6_worker_recovery_initial_implementation.txt"
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

    "queue_certification": (
        ROOT / "backend/server/runtime/universal_queue/certification.py",
        "6ED39655147D2B331E02101F5EA23E68CF71447353C0D294E170281AE40C0D4C",
    ),

    "queue_recovery": (
        ROOT / "backend/server/runtime/universal_queue/recovery.py",
        "D7AA19721DEFB1D40A24A22EBA04BDA776216520CFB31B9FAA1309242F1CF650",
    ),

    "job_contract": (
        ROOT / "backend/server/runtime/universal_jobs/contract.py",
        "82225461C792EDA7193D2FA3B59E39FF3823906365CD0FBCD5E2915673EE23D1",
    ),

    "job_attempts": (
        ROOT / "backend/server/runtime/universal_jobs/attempts.py",
        "2662BC9A968D3F37B9072FA9551A70681E5CE9BEB78E65DAF6550580893DEE24",
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
                "4.1.6 implementation: "
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

from backend.server.runtime.universal_jobs.contract import (
    UniversalJobStatus,
)

from backend.server.runtime.universal_worker.leasing import (
    UniversalWorkerLeaseState,
)


UNIVERSAL_WORKER_RECOVERY_VERSION = (
    "universal_worker_recovery_v4.1.6"
)

UNIVERSAL_WORKER_RECOVERY_EVIDENCE_SCHEMA_VERSION = (
    "universal_worker_recovery_evidence_schema_v1"
)

UNIVERSAL_WORKER_RECOVERY_RESULT_SCHEMA_VERSION = (
    "universal_worker_recovery_result_schema_v1"
)

MAX_UNIVERSAL_WORKER_RECOVERY_JOB_ID_LENGTH = 200


class UniversalWorkerRecoveryError(
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


class UniversalWorkerRecoveryDisposition(
    str,
    Enum,
):

    RECOVERABLE = "RECOVERABLE"

    NOT_RECOVERABLE = "NOT_RECOVERABLE"

    NO_ACTION = "NO_ACTION"


class UniversalWorkerRecoveryReason(
    str,
    Enum,
):

    STATUS_NOT_WORKER_OWNED = (
        "STATUS_NOT_WORKER_OWNED"
    )

    OWNERSHIP_STILL_VALID = (
        "OWNERSHIP_STILL_VALID"
    )

    ACTIVE_LEASE = (
        "ACTIVE_LEASE"
    )

    OWNERSHIP_LOST_RETRY_PERMITTED = (
        "OWNERSHIP_LOST_RETRY_PERMITTED"
    )

    RETRY_NOT_PERMITTED = (
        "RETRY_NOT_PERMITTED"
    )

    DUPLICATE_EXECUTION_NOT_SAFE = (
        "DUPLICATE_EXECUTION_NOT_SAFE"
    )


def normalize_universal_worker_recovery_job_id(
    value: Any,
) -> str:

    if not isinstance(
        value,
        str,
    ):

        raise UniversalWorkerRecoveryError(
            "job_id must be a string.",
            code="invalid_recovery_job_id_type",
            value=value,
        )

    normalized = value.strip()

    if not normalized:

        raise UniversalWorkerRecoveryError(
            "job_id must not be empty.",
            code="empty_recovery_job_id",
            value=value,
        )

    if (
        len(normalized)
        > MAX_UNIVERSAL_WORKER_RECOVERY_JOB_ID_LENGTH
    ):

        raise UniversalWorkerRecoveryError(
            (
                "job_id exceeds maximum supported "
                "Worker Recovery length."
            ),
            code="recovery_job_id_too_long",
            value=value,
        )

    return normalized


def _validate_strict_bool(
    value: Any,
    *,
    field_name: str,
) -> bool:

    if type(value) is not bool:

        raise UniversalWorkerRecoveryError(
            (
                field_name
                + " must be bool."
            ),
            code="invalid_worker_recovery_signal",
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
class UniversalWorkerRecoveryEvidence:

    job_id: str

    job_status: UniversalJobStatus

    worker_ownership_lost: bool

    retry_permitted: bool

    duplicate_execution_safe: bool

    lease_state: UniversalWorkerLeaseState | None = None

    schema_version: str = (
        UNIVERSAL_WORKER_RECOVERY_EVIDENCE_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        object.__setattr__(
            self,
            "job_id",
            normalize_universal_worker_recovery_job_id(
                self.job_id
            ),
        )

        if not isinstance(
            self.job_status,
            UniversalJobStatus,
        ):

            raise UniversalWorkerRecoveryError(
                (
                    "job_status must be "
                    "UniversalJobStatus."
                ),
                code="invalid_worker_recovery_job_status",
                value=self.job_status,
            )

        object.__setattr__(
            self,
            "worker_ownership_lost",
            _validate_strict_bool(
                self.worker_ownership_lost,
                field_name="worker_ownership_lost",
            ),
        )

        object.__setattr__(
            self,
            "retry_permitted",
            _validate_strict_bool(
                self.retry_permitted,
                field_name="retry_permitted",
            ),
        )

        object.__setattr__(
            self,
            "duplicate_execution_safe",
            _validate_strict_bool(
                self.duplicate_execution_safe,
                field_name="duplicate_execution_safe",
            ),
        )

        if (
            self.lease_state is not None
            and
            not isinstance(
                self.lease_state,
                UniversalWorkerLeaseState,
            )
        ):

            raise UniversalWorkerRecoveryError(
                (
                    "lease_state must be "
                    "UniversalWorkerLeaseState or None."
                ),
                code="invalid_worker_recovery_lease_state",
                value=self.lease_state,
            )

        if (
            self.job_status
            is UniversalJobStatus.LEASED
        ):

            if self.lease_state is None:

                raise UniversalWorkerRecoveryError(
                    (
                        "LEASED Worker Recovery evidence "
                        "requires lease_state."
                    ),
                    code="leased_recovery_requires_lease_state",
                    value=None,
                )

            if (
                self.lease_state
                is UniversalWorkerLeaseState.ACTIVE
                and
                self.worker_ownership_lost
                is True
            ):

                raise UniversalWorkerRecoveryError(
                    (
                        "ACTIVE lease contradicts "
                        "worker_ownership_lost=True."
                    ),
                    code="active_lease_ownership_contradiction",
                    value=True,
                )

            if (
                self.lease_state
                is UniversalWorkerLeaseState.EXPIRED
                and
                self.worker_ownership_lost
                is False
            ):

                raise UniversalWorkerRecoveryError(
                    (
                        "EXPIRED lease requires "
                        "worker_ownership_lost=True."
                    ),
                    code="expired_lease_ownership_contradiction",
                    value=False,
                )

        elif self.lease_state is not None:

            raise UniversalWorkerRecoveryError(
                (
                    "lease_state is only accepted for "
                    "LEASED Worker Recovery evidence."
                ),
                code="lease_state_requires_leased_status",
                value=self.job_status,
            )

        if (
            self.schema_version
            != UNIVERSAL_WORKER_RECOVERY_EVIDENCE_SCHEMA_VERSION
        ):

            raise UniversalWorkerRecoveryError(
                (
                    "Invalid Worker Recovery Evidence "
                    "schema_version."
                ),
                code=(
                    "invalid_worker_recovery_"
                    "evidence_schema_version"
                ),
                value=self.schema_version,
            )


def decide_universal_worker_recovery(
    evidence: UniversalWorkerRecoveryEvidence,
) -> tuple[
    UniversalWorkerRecoveryDisposition,
    UniversalWorkerRecoveryReason,
]:

    if not isinstance(
        evidence,
        UniversalWorkerRecoveryEvidence,
    ):

        raise UniversalWorkerRecoveryError(
            (
                "evidence must be "
                "UniversalWorkerRecoveryEvidence."
            ),
            code="invalid_worker_recovery_evidence",
            value=evidence,
        )

    if evidence.job_status not in {
        UniversalJobStatus.LEASED,
        UniversalJobStatus.RUNNING,
    }:

        return (
            UniversalWorkerRecoveryDisposition.NO_ACTION,
            UniversalWorkerRecoveryReason.STATUS_NOT_WORKER_OWNED,
        )

    if (
        evidence.job_status
        is UniversalJobStatus.LEASED
        and
        evidence.lease_state
        is UniversalWorkerLeaseState.ACTIVE
    ):

        return (
            UniversalWorkerRecoveryDisposition.NO_ACTION,
            UniversalWorkerRecoveryReason.ACTIVE_LEASE,
        )

    if (
        evidence.worker_ownership_lost
        is False
    ):

        return (
            UniversalWorkerRecoveryDisposition.NO_ACTION,
            UniversalWorkerRecoveryReason.OWNERSHIP_STILL_VALID,
        )

    if (
        evidence.retry_permitted
        is False
    ):

        return (
            UniversalWorkerRecoveryDisposition.NOT_RECOVERABLE,
            UniversalWorkerRecoveryReason.RETRY_NOT_PERMITTED,
        )

    if (
        evidence.duplicate_execution_safe
        is False
    ):

        return (
            UniversalWorkerRecoveryDisposition.NOT_RECOVERABLE,
            UniversalWorkerRecoveryReason.DUPLICATE_EXECUTION_NOT_SAFE,
        )

    return (
        UniversalWorkerRecoveryDisposition.RECOVERABLE,
        UniversalWorkerRecoveryReason.OWNERSHIP_LOST_RETRY_PERMITTED,
    )


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalWorkerRecoveryResult:

    job_id: str

    original_status: UniversalJobStatus

    disposition: UniversalWorkerRecoveryDisposition

    reason: UniversalWorkerRecoveryReason

    worker_ownership_lost: bool

    retry_permitted: bool

    duplicate_execution_safe: bool

    lease_state: UniversalWorkerLeaseState | None

    schema_version: str = (
        UNIVERSAL_WORKER_RECOVERY_RESULT_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        object.__setattr__(
            self,
            "job_id",
            normalize_universal_worker_recovery_job_id(
                self.job_id
            ),
        )

        if not isinstance(
            self.original_status,
            UniversalJobStatus,
        ):

            raise UniversalWorkerRecoveryError(
                (
                    "original_status must be "
                    "UniversalJobStatus."
                ),
                code="invalid_recovery_result_status",
                value=self.original_status,
            )

        if not isinstance(
            self.disposition,
            UniversalWorkerRecoveryDisposition,
        ):

            raise UniversalWorkerRecoveryError(
                (
                    "disposition must be "
                    "UniversalWorkerRecoveryDisposition."
                ),
                code="invalid_recovery_disposition",
                value=self.disposition,
            )

        if not isinstance(
            self.reason,
            UniversalWorkerRecoveryReason,
        ):

            raise UniversalWorkerRecoveryError(
                (
                    "reason must be "
                    "UniversalWorkerRecoveryReason."
                ),
                code="invalid_recovery_reason",
                value=self.reason,
            )

        object.__setattr__(
            self,
            "worker_ownership_lost",
            _validate_strict_bool(
                self.worker_ownership_lost,
                field_name="worker_ownership_lost",
            ),
        )

        object.__setattr__(
            self,
            "retry_permitted",
            _validate_strict_bool(
                self.retry_permitted,
                field_name="retry_permitted",
            ),
        )

        object.__setattr__(
            self,
            "duplicate_execution_safe",
            _validate_strict_bool(
                self.duplicate_execution_safe,
                field_name="duplicate_execution_safe",
            ),
        )

        if (
            self.lease_state is not None
            and
            not isinstance(
                self.lease_state,
                UniversalWorkerLeaseState,
            )
        ):

            raise UniversalWorkerRecoveryError(
                (
                    "lease_state must be "
                    "UniversalWorkerLeaseState or None."
                ),
                code="invalid_recovery_result_lease_state",
                value=self.lease_state,
            )

        if (
            self.schema_version
            != UNIVERSAL_WORKER_RECOVERY_RESULT_SCHEMA_VERSION
        ):

            raise UniversalWorkerRecoveryError(
                (
                    "Invalid Worker Recovery Result "
                    "schema_version."
                ),
                code=(
                    "invalid_worker_recovery_"
                    "result_schema_version"
                ),
                value=self.schema_version,
            )

        canonical_evidence = (
            UniversalWorkerRecoveryEvidence(
                job_id=self.job_id,
                job_status=self.original_status,
                worker_ownership_lost=(
                    self.worker_ownership_lost
                ),
                retry_permitted=(
                    self.retry_permitted
                ),
                duplicate_execution_safe=(
                    self.duplicate_execution_safe
                ),
                lease_state=self.lease_state,
            )
        )

        (
            expected_disposition,
            expected_reason,
        ) = decide_universal_worker_recovery(
            canonical_evidence
        )

        if (
            self.disposition
            is not expected_disposition
            or
            self.reason
            is not expected_reason
        ):

            raise UniversalWorkerRecoveryError(
                (
                    "Worker Recovery result is "
                    "inconsistent with its evidence."
                ),
                code="inconsistent_worker_recovery_result",
                value={
                    "disposition":
                        self.disposition.value,

                    "reason":
                        self.reason.value,

                    "expected_disposition":
                        expected_disposition.value,

                    "expected_reason":
                        expected_reason.value,
                },
            )

    @property
    def recoverable(
        self,
    ) -> bool:

        return (
            self.disposition
            is UniversalWorkerRecoveryDisposition.RECOVERABLE
        )

    @property
    def action_required(
        self,
    ) -> bool:

        return (
            self.disposition
            is not UniversalWorkerRecoveryDisposition.NO_ACTION
        )


def create_universal_worker_recovery_evidence(
    *,
    job_id: str,
    job_status: UniversalJobStatus,
    worker_ownership_lost: bool,
    retry_permitted: bool,
    duplicate_execution_safe: bool,
    lease_state: UniversalWorkerLeaseState | None = None,
) -> UniversalWorkerRecoveryEvidence:

    return UniversalWorkerRecoveryEvidence(
        job_id=job_id,
        job_status=job_status,
        worker_ownership_lost=worker_ownership_lost,
        retry_permitted=retry_permitted,
        duplicate_execution_safe=duplicate_execution_safe,
        lease_state=lease_state,
    )


def evaluate_universal_worker_recovery(
    evidence: UniversalWorkerRecoveryEvidence,
) -> UniversalWorkerRecoveryResult:

    if not isinstance(
        evidence,
        UniversalWorkerRecoveryEvidence,
    ):

        raise UniversalWorkerRecoveryError(
            (
                "evidence must be "
                "UniversalWorkerRecoveryEvidence."
            ),
            code="invalid_worker_recovery_evidence",
            value=evidence,
        )

    (
        disposition,
        reason,
    ) = decide_universal_worker_recovery(
        evidence
    )

    return UniversalWorkerRecoveryResult(
        job_id=evidence.job_id,
        original_status=evidence.job_status,
        disposition=disposition,
        reason=reason,
        worker_ownership_lost=(
            evidence.worker_ownership_lost
        ),
        retry_permitted=(
            evidence.retry_permitted
        ),
        duplicate_execution_safe=(
            evidence.duplicate_execution_safe
        ),
        lease_state=evidence.lease_state,
    )


def explain_universal_worker_recovery_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "4.1.6",

            "component":
                "Universal Worker Recovery",

            "version":
                UNIVERSAL_WORKER_RECOVERY_VERSION,

            "evidence_schema_version":
                UNIVERSAL_WORKER_RECOVERY_EVIDENCE_SCHEMA_VERSION,

            "result_schema_version":
                UNIVERSAL_WORKER_RECOVERY_RESULT_SCHEMA_VERSION,

            "dispositions": (
                "RECOVERABLE",
                "NOT_RECOVERABLE",
                "NO_ACTION",
            ),

            "worker_owned_statuses": (
                "LEASED",
                "RUNNING",
            ),

            "input_rule": (
                "4.1.6 consumes caller-supplied "
                "worker-ownership-loss, retry-permission "
                "and duplicate-execution-safety evidence"
            ),

            "leased_rule": (
                "LEASED recovery requires canonical "
                "4.1.4 lease state; ACTIVE means "
                "ownership is still valid and EXPIRED "
                "means worker ownership is lost"
            ),

            "running_rule": (
                "RUNNING recovery requires explicit "
                "caller-supplied worker_ownership_lost "
                "evidence"
            ),

            "recovery_gate_rule": (
                "RECOVERABLE requires worker ownership "
                "lost, retry permitted and duplicate "
                "execution safe"
            ),

            "retry_boundary": (
                "4.1.6 consumes retry_permitted as "
                "caller evidence and does not calculate "
                "attempt ceilings, increment attempts, "
                "backoff or retry scheduling"
            ),

            "duplicate_execution_boundary": (
                "4.1.6 requires caller-supplied "
                "duplicate_execution_safe evidence and "
                "does not invent idempotency or fencing "
                "policy"
            ),

            "queue_boundary": (
                "4.1.6 decides Worker Recovery "
                "permission but does not restore queue "
                "membership or requeue a job"
            ),

            "lease_boundary": (
                "4.1.6 consumes lease state but does "
                "not acquire, renew, release or persist "
                "leases"
            ),

            "health_heartbeat_boundary": (
                "4.1.6 does not classify worker health, "
                "read heartbeats or detect stale workers"
            ),

            "dead_letter_boundary": (
                "DEAD_LETTER recovery remains outside "
                "4.1.6"
            ),

            "execution_boundary": (
                "RECOVERABLE is authorization evidence "
                "only and does not dispatch or execute "
                "the job"
            ),

            "purity_rule": (
                "Worker Recovery is deterministic over "
                "caller-supplied evidence and performs "
                "no state lookup, persistence or "
                "mutation"
            ),

            "prohibitions": (
                "does not requeue jobs",
                "does not restore queue membership",
                "does not increment attempts",
                "does not calculate maximum attempts",
                "does not calculate retry backoff",
                "does not schedule retries",
                "does not transition jobs to QUEUED",
                "does not transition jobs to FAILED",
                "does not transition jobs to DEAD_LETTER",
                "does not recover dead-letter jobs",
                "does not acquire leases",
                "does not renew leases",
                "does not release leases",
                "does not persist leases",
                "does not classify lease expiration",
                "does not determine worker health",
                "does not read worker heartbeats",
                "does not calculate heartbeat freshness",
                "does not detect stale workers",
                "does not restart workers",
                "does not terminate workers",
                "does not assign replacement workers",
                "does not dispatch jobs",
                "does not execute jobs",
                "does not invent idempotency policy",
                "does not invent fencing policy",
                "does not access Runtime State Store",
                "does not access orchestration",
                "does not mutate Queue Infrastructure",
                "does not persist recovery results",
                "does not perform filesystem I/O",
                "does not perform network I/O",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_WORKER_RECOVERY_VERSION",
    "UNIVERSAL_WORKER_RECOVERY_EVIDENCE_SCHEMA_VERSION",
    "UNIVERSAL_WORKER_RECOVERY_RESULT_SCHEMA_VERSION",
    "MAX_UNIVERSAL_WORKER_RECOVERY_JOB_ID_LENGTH",
    "UniversalWorkerRecoveryError",
    "UniversalWorkerRecoveryDisposition",
    "UniversalWorkerRecoveryReason",
    "UniversalWorkerRecoveryEvidence",
    "UniversalWorkerRecoveryResult",
    "normalize_universal_worker_recovery_job_id",
    "create_universal_worker_recovery_evidence",
    "decide_universal_worker_recovery",
    "evaluate_universal_worker_recovery",
    "explain_universal_worker_recovery_v1",
]
'''


ast.parse(
    SOURCE
)

RECOVERY_PATH.write_text(
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

contract = importlib.import_module(
    "backend.server.runtime.universal_jobs.contract"
)

leasing = importlib.import_module(
    "backend.server.runtime.universal_worker.leasing"
)

recovery_name = (
    "backend.server.runtime."
    "universal_worker.recovery"
)

sys.modules.pop(
    recovery_name,
    None,
)

recovery = importlib.import_module(
    recovery_name
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
    recovery.UNIVERSAL_WORKER_RECOVERY_VERSION
    == "universal_worker_recovery_v4.1.6",
)

check(
    "evidence_schema",
    recovery.UNIVERSAL_WORKER_RECOVERY_EVIDENCE_SCHEMA_VERSION
    == "universal_worker_recovery_evidence_schema_v1",
)

check(
    "result_schema",
    recovery.UNIVERSAL_WORKER_RECOVERY_RESULT_SCHEMA_VERSION
    == "universal_worker_recovery_result_schema_v1",
)

check(
    "job_id_max_length",
    recovery.MAX_UNIVERSAL_WORKER_RECOVERY_JOB_ID_LENGTH
    == 200,
)

check(
    "dispositions_exact",
    tuple(
        item.value
        for item in recovery.UniversalWorkerRecoveryDisposition
    )
    == (
        "RECOVERABLE",
        "NOT_RECOVERABLE",
        "NO_ACTION",
    ),
)


# ============================================================
# RUNNING RECOVERY MATRIX
# ============================================================

running_no_loss = (
    recovery.create_universal_worker_recovery_evidence(
        job_id="job-running-no-loss",
        job_status=contract.UniversalJobStatus.RUNNING,
        worker_ownership_lost=False,
        retry_permitted=True,
        duplicate_execution_safe=True,
    )
)

running_recoverable = (
    recovery.create_universal_worker_recovery_evidence(
        job_id="job-running-recover",
        job_status=contract.UniversalJobStatus.RUNNING,
        worker_ownership_lost=True,
        retry_permitted=True,
        duplicate_execution_safe=True,
    )
)

running_retry_blocked = (
    recovery.create_universal_worker_recovery_evidence(
        job_id="job-running-no-retry",
        job_status=contract.UniversalJobStatus.RUNNING,
        worker_ownership_lost=True,
        retry_permitted=False,
        duplicate_execution_safe=True,
    )
)

running_duplicate_blocked = (
    recovery.create_universal_worker_recovery_evidence(
        job_id="job-running-unsafe",
        job_status=contract.UniversalJobStatus.RUNNING,
        worker_ownership_lost=True,
        retry_permitted=True,
        duplicate_execution_safe=False,
    )
)


result_no_loss = (
    recovery.evaluate_universal_worker_recovery(
        running_no_loss
    )
)

result_recoverable = (
    recovery.evaluate_universal_worker_recovery(
        running_recoverable
    )
)

result_retry_blocked = (
    recovery.evaluate_universal_worker_recovery(
        running_retry_blocked
    )
)

result_duplicate_blocked = (
    recovery.evaluate_universal_worker_recovery(
        running_duplicate_blocked
    )
)


check(
    "running_no_loss_no_action",
    result_no_loss.disposition
    is recovery.UniversalWorkerRecoveryDisposition.NO_ACTION,
)

check(
    "running_no_loss_reason",
    result_no_loss.reason
    is recovery.UniversalWorkerRecoveryReason.OWNERSHIP_STILL_VALID,
)

check(
    "running_recoverable",
    result_recoverable.disposition
    is recovery.UniversalWorkerRecoveryDisposition.RECOVERABLE,
)

check(
    "running_recoverable_reason",
    result_recoverable.reason
    is recovery.UniversalWorkerRecoveryReason.OWNERSHIP_LOST_RETRY_PERMITTED,
)

check(
    "running_retry_blocked",
    result_retry_blocked.disposition
    is recovery.UniversalWorkerRecoveryDisposition.NOT_RECOVERABLE,
)

check(
    "running_retry_blocked_reason",
    result_retry_blocked.reason
    is recovery.UniversalWorkerRecoveryReason.RETRY_NOT_PERMITTED,
)

check(
    "running_duplicate_blocked",
    result_duplicate_blocked.disposition
    is recovery.UniversalWorkerRecoveryDisposition.NOT_RECOVERABLE,
)

check(
    "running_duplicate_blocked_reason",
    result_duplicate_blocked.reason
    is recovery.UniversalWorkerRecoveryReason.DUPLICATE_EXECUTION_NOT_SAFE,
)


# ============================================================
# LEASED RECOVERY
# ============================================================

leased_active = (
    recovery.create_universal_worker_recovery_evidence(
        job_id="job-leased-active",
        job_status=contract.UniversalJobStatus.LEASED,
        worker_ownership_lost=False,
        retry_permitted=True,
        duplicate_execution_safe=True,
        lease_state=leasing.UniversalWorkerLeaseState.ACTIVE,
    )
)

leased_expired = (
    recovery.create_universal_worker_recovery_evidence(
        job_id="job-leased-expired",
        job_status=contract.UniversalJobStatus.LEASED,
        worker_ownership_lost=True,
        retry_permitted=True,
        duplicate_execution_safe=True,
        lease_state=leasing.UniversalWorkerLeaseState.EXPIRED,
    )
)


active_result = (
    recovery.evaluate_universal_worker_recovery(
        leased_active
    )
)

expired_result = (
    recovery.evaluate_universal_worker_recovery(
        leased_expired
    )
)


check(
    "active_lease_no_action",
    active_result.disposition
    is recovery.UniversalWorkerRecoveryDisposition.NO_ACTION,
)

check(
    "active_lease_reason",
    active_result.reason
    is recovery.UniversalWorkerRecoveryReason.ACTIVE_LEASE,
)

check(
    "expired_lease_recoverable",
    expired_result.disposition
    is recovery.UniversalWorkerRecoveryDisposition.RECOVERABLE,
)


# ============================================================
# CONTRADICTORY LEASE EVIDENCE
# ============================================================

try:

    recovery.create_universal_worker_recovery_evidence(
        job_id="job-active-contradiction",
        job_status=contract.UniversalJobStatus.LEASED,
        worker_ownership_lost=True,
        retry_permitted=True,
        duplicate_execution_safe=True,
        lease_state=leasing.UniversalWorkerLeaseState.ACTIVE,
    )

except recovery.UniversalWorkerRecoveryError as exc:

    rejected = (
        exc.code
        == "active_lease_ownership_contradiction"
    )

else:

    rejected = False


check(
    "active_lease_contradiction_rejected",
    rejected,
)


try:

    recovery.create_universal_worker_recovery_evidence(
        job_id="job-expired-contradiction",
        job_status=contract.UniversalJobStatus.LEASED,
        worker_ownership_lost=False,
        retry_permitted=True,
        duplicate_execution_safe=True,
        lease_state=leasing.UniversalWorkerLeaseState.EXPIRED,
    )

except recovery.UniversalWorkerRecoveryError as exc:

    rejected = (
        exc.code
        == "expired_lease_ownership_contradiction"
    )

else:

    rejected = False


check(
    "expired_lease_contradiction_rejected",
    rejected,
)


# ============================================================
# LEASE STATE REQUIREMENTS
# ============================================================

try:

    recovery.create_universal_worker_recovery_evidence(
        job_id="job-leased-missing-state",
        job_status=contract.UniversalJobStatus.LEASED,
        worker_ownership_lost=True,
        retry_permitted=True,
        duplicate_execution_safe=True,
    )

except recovery.UniversalWorkerRecoveryError as exc:

    rejected = (
        exc.code
        == "leased_recovery_requires_lease_state"
    )

else:

    rejected = False


check(
    "leased_requires_lease_state",
    rejected,
)


try:

    recovery.create_universal_worker_recovery_evidence(
        job_id="job-running-with-lease-state",
        job_status=contract.UniversalJobStatus.RUNNING,
        worker_ownership_lost=True,
        retry_permitted=True,
        duplicate_execution_safe=True,
        lease_state=leasing.UniversalWorkerLeaseState.EXPIRED,
    )

except recovery.UniversalWorkerRecoveryError as exc:

    rejected = (
        exc.code
        == "lease_state_requires_leased_status"
    )

else:

    rejected = False


check(
    "running_rejects_lease_state",
    rejected,
)


# ============================================================
# NON-WORKER-OWNED STATUSES
# ============================================================

for status in (
    contract.UniversalJobStatus.CREATED,
    contract.UniversalJobStatus.QUEUED,
    contract.UniversalJobStatus.SCHEDULED,
    contract.UniversalJobStatus.SUSPENDED,
    contract.UniversalJobStatus.SUCCEEDED,
    contract.UniversalJobStatus.FAILED,
    contract.UniversalJobStatus.CANCELLED,
    contract.UniversalJobStatus.DEAD_LETTER,
    contract.UniversalJobStatus.EXPIRED,
):

    evidence = (
        recovery.create_universal_worker_recovery_evidence(
            job_id=(
                "job-"
                + status.value
            ),
            job_status=status,
            worker_ownership_lost=False,
            retry_permitted=False,
            duplicate_execution_safe=False,
        )
    )

    result = (
        recovery.evaluate_universal_worker_recovery(
            evidence
        )
    )

    check(
        "non_worker_owned_"
        + status.value,
        (
            result.disposition
            is recovery.UniversalWorkerRecoveryDisposition.NO_ACTION
            and
            result.reason
            is recovery.UniversalWorkerRecoveryReason.STATUS_NOT_WORKER_OWNED
        ),
    )


# ============================================================
# STRICT BOOL VALIDATION
# ============================================================

for field_name in (
    "worker_ownership_lost",
    "retry_permitted",
    "duplicate_execution_safe",
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
        [],
        {},
        (),
    ):

        kwargs = {
            "job_id":
                "job-strict",

            "job_status":
                contract.UniversalJobStatus.RUNNING,

            "worker_ownership_lost":
                False,

            "retry_permitted":
                False,

            "duplicate_execution_safe":
                False,
        }

        kwargs[
            field_name
        ] = bad

        try:

            recovery.create_universal_worker_recovery_evidence(
                **kwargs
            )

        except recovery.UniversalWorkerRecoveryError as exc:

            rejected = (
                exc.code
                == "invalid_worker_recovery_signal"
            )

        else:

            rejected = False

        check(
            (
                "strict_"
                + field_name
                + "_"
                + type(bad).__name__
                + "_"
                + repr(bad)
            ),
            rejected,
        )


# ============================================================
# JOB ID VALIDATION
# ============================================================

check(
    "job_id_normalized",
    recovery.normalize_universal_worker_recovery_job_id(
        " job-001 "
    )
    == "job-001",
)


for bad in (
    None,
    True,
    0,
    [],
    {},
):

    try:

        recovery.normalize_universal_worker_recovery_job_id(
            bad
        )

    except recovery.UniversalWorkerRecoveryError as exc:

        rejected = (
            exc.code
            == "invalid_recovery_job_id_type"
        )

    else:

        rejected = False

    check(
        "bad_job_id_"
        + type(bad).__name__,
        rejected,
    )


for bad in (
    "",
    " ",
    "\t",
    "\n",
):

    try:

        recovery.normalize_universal_worker_recovery_job_id(
            bad
        )

    except recovery.UniversalWorkerRecoveryError as exc:

        rejected = (
            exc.code
            == "empty_recovery_job_id"
        )

    else:

        rejected = False

    check(
        "blank_job_id_"
        + repr(bad),
        rejected,
    )


exact_max = (
    "j"
    * recovery.MAX_UNIVERSAL_WORKER_RECOVERY_JOB_ID_LENGTH
)


check(
    "exact_max_job_id_accepted",
    recovery.normalize_universal_worker_recovery_job_id(
        exact_max
    )
    == exact_max,
)


try:

    recovery.normalize_universal_worker_recovery_job_id(
        exact_max
        + "x"
    )

except recovery.UniversalWorkerRecoveryError as exc:

    rejected = (
        exc.code
        == "recovery_job_id_too_long"
    )

else:

    rejected = False


check(
    "job_id_overflow_rejected",
    rejected,
)


# ============================================================
# INVALID STATUS / LEASE STATE
# ============================================================

try:

    recovery.create_universal_worker_recovery_evidence(
        job_id="job-status",
        job_status="RUNNING",
        worker_ownership_lost=True,
        retry_permitted=True,
        duplicate_execution_safe=True,
    )

except recovery.UniversalWorkerRecoveryError as exc:

    rejected = (
        exc.code
        == "invalid_worker_recovery_job_status"
    )

else:

    rejected = False


check(
    "raw_status_string_rejected",
    rejected,
)


try:

    recovery.create_universal_worker_recovery_evidence(
        job_id="job-lease-state",
        job_status=contract.UniversalJobStatus.LEASED,
        worker_ownership_lost=True,
        retry_permitted=True,
        duplicate_execution_safe=True,
        lease_state="EXPIRED",
    )

except recovery.UniversalWorkerRecoveryError as exc:

    rejected = (
        exc.code
        == "invalid_worker_recovery_lease_state"
    )

else:

    rejected = False


check(
    "raw_lease_state_string_rejected",
    rejected,
)


# ============================================================
# RESULT PROPERTIES
# ============================================================

check(
    "recoverable_property_true",
    result_recoverable.recoverable
    is True,
)

check(
    "recoverable_property_false_no_action",
    result_no_loss.recoverable
    is False,
)

check(
    "action_required_recoverable",
    result_recoverable.action_required
    is True,
)

check(
    "action_required_not_recoverable",
    result_retry_blocked.action_required
    is True,
)

check(
    "action_required_no_action_false",
    result_no_loss.action_required
    is False,
)


# ============================================================
# RESULT FORGERY PROTECTION
# ============================================================

try:

    recovery.UniversalWorkerRecoveryResult(
        job_id=running_recoverable.job_id,
        original_status=running_recoverable.job_status,
        disposition=(
            recovery.UniversalWorkerRecoveryDisposition.NO_ACTION
        ),
        reason=(
            recovery.UniversalWorkerRecoveryReason.OWNERSHIP_STILL_VALID
        ),
        worker_ownership_lost=True,
        retry_permitted=True,
        duplicate_execution_safe=True,
        lease_state=None,
    )

except recovery.UniversalWorkerRecoveryError as exc:

    rejected = (
        exc.code
        == "inconsistent_worker_recovery_result"
    )

else:

    rejected = False


check(
    "forged_result_rejected",
    rejected,
)


# ============================================================
# SCHEMA TAMPERING
# ============================================================

try:

    recovery.UniversalWorkerRecoveryEvidence(
        job_id="job-schema",
        job_status=contract.UniversalJobStatus.RUNNING,
        worker_ownership_lost=True,
        retry_permitted=True,
        duplicate_execution_safe=True,
        schema_version="wrong",
    )

except recovery.UniversalWorkerRecoveryError as exc:

    rejected = (
        exc.code
        == "invalid_worker_recovery_evidence_schema_version"
    )

else:

    rejected = False


check(
    "evidence_schema_tamper_rejected",
    rejected,
)


try:

    recovery.UniversalWorkerRecoveryResult(
        job_id=running_recoverable.job_id,
        original_status=running_recoverable.job_status,
        disposition=result_recoverable.disposition,
        reason=result_recoverable.reason,
        worker_ownership_lost=True,
        retry_permitted=True,
        duplicate_execution_safe=True,
        lease_state=None,
        schema_version="wrong",
    )

except recovery.UniversalWorkerRecoveryError as exc:

    rejected = (
        exc.code
        == "invalid_worker_recovery_result_schema_version"
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
        running_recoverable,
        "worker_ownership_lost",
    ),
    (
        running_recoverable,
        "retry_permitted",
    ),
    (
        running_recoverable,
        "duplicate_execution_safe",
    ),
    (
        result_recoverable,
        "disposition",
    ),
    (
        result_recoverable,
        "reason",
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

repeat = (
    recovery.evaluate_universal_worker_recovery(
        running_recoverable
    )
)


check(
    "deterministic_result",
    repeat
    == result_recoverable,
)


# ============================================================
# EXPLANATION CONTRACT
# ============================================================

explanation = (
    recovery.explain_universal_worker_recovery_v1()
)


check(
    "explanation_phase",
    explanation.get(
        "phase"
    )
    == "4.1.6",
)

check(
    "explanation_component",
    explanation.get(
        "component"
    )
    == "Universal Worker Recovery",
)

check(
    "dispositions_explained",
    tuple(
        explanation.get(
            "dispositions"
        )
    )
    == (
        "RECOVERABLE",
        "NOT_RECOVERABLE",
        "NO_ACTION",
    ),
)

check(
    "worker_owned_statuses",
    tuple(
        explanation.get(
            "worker_owned_statuses"
        )
    )
    == (
        "LEASED",
        "RUNNING",
    ),
)

check(
    "caller_supplied_rule",
    "caller-supplied"
    in explanation.get(
        "input_rule",
        "",
    ),
)

check(
    "lease_rule",
    (
        "ACTIVE"
        in explanation.get(
            "leased_rule",
            "",
        )
        and
        "EXPIRED"
        in explanation.get(
            "leased_rule",
            "",
        )
    ),
)

check(
    "running_ownership_rule",
    "worker_ownership_lost"
    in explanation.get(
        "running_rule",
        "",
    ),
)

check(
    "three_gate_rule",
    (
        "worker ownership lost"
        in explanation.get(
            "recovery_gate_rule",
            "",
        )
        and
        "retry permitted"
        in explanation.get(
            "recovery_gate_rule",
            "",
        )
        and
        "duplicate execution safe"
        in explanation.get(
            "recovery_gate_rule",
            "",
        )
    ),
)

check(
    "attempt_boundary",
    (
        "does not calculate"
        in explanation.get(
            "retry_boundary",
            "",
        )
        and
        "increment attempts"
        in explanation.get(
            "retry_boundary",
            "",
        )
    ),
)

check(
    "duplicate_boundary",
    "caller-supplied"
    in explanation.get(
        "duplicate_execution_boundary",
        "",
    ),
)

check(
    "queue_boundary",
    "does not restore queue membership"
    in explanation.get(
        "queue_boundary",
        "",
    ),
)

check(
    "lease_boundary",
    "does not acquire"
    in explanation.get(
        "lease_boundary",
        "",
    ),
)

check(
    "health_heartbeat_boundary",
    (
        "does not classify worker health"
        in explanation.get(
            "health_heartbeat_boundary",
            "",
        )
        and
        "detect stale workers"
        in explanation.get(
            "health_heartbeat_boundary",
            "",
        )
    ),
)

check(
    "dead_letter_boundary",
    "outside"
    in explanation.get(
        "dead_letter_boundary",
        "",
    ),
)

check(
    "execution_boundary",
    "authorization evidence only"
    in explanation.get(
        "execution_boundary",
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
    "does not requeue jobs",
    "does not restore queue membership",
    "does not increment attempts",
    "does not calculate maximum attempts",
    "does not calculate retry backoff",
    "does not schedule retries",
    "does not transition jobs to QUEUED",
    "does not transition jobs to FAILED",
    "does not transition jobs to DEAD_LETTER",
    "does not recover dead-letter jobs",
    "does not acquire leases",
    "does not renew leases",
    "does not release leases",
    "does not persist leases",
    "does not classify lease expiration",
    "does not determine worker health",
    "does not read worker heartbeats",
    "does not calculate heartbeat freshness",
    "does not detect stale workers",
    "does not restart workers",
    "does not terminate workers",
    "does not assign replacement workers",
    "does not dispatch jobs",
    "does not execute jobs",
    "does not invent idempotency policy",
    "does not invent fencing policy",
    "does not access Runtime State Store",
    "does not access orchestration",
    "does not mutate Queue Infrastructure",
    "does not persist recovery results",
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

source = RECOVERY_PATH.read_text(
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
    "backend_imports_exact",
    backend_imports
    == [
        "backend.server.runtime.universal_jobs.contract",
        "backend.server.runtime.universal_worker.leasing",
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
    "sleep",
    "worker_heartbeat",
    "get_latest_worker_statuses",
    "get_runtime_state_store_registry",
    "recover_universal_queue_membership",
    "retry_job",
    "retry_exhausted",
    "dequeue_job",
    "enqueue_job",
    "requeue_job",
    "assign_universal_worker",
    "acquire_universal_worker_lease",
    "renew_universal_worker_lease",
    "release_universal_worker_lease",
    "evaluate_universal_worker_lease_state",
    "evaluate_universal_worker_health",
    "dispatch_job",
    "execute_job",
    "dispatch_registered_runtime_handler",
    "mark_job_failed",
    "mark_job_completed",
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
# PROTECTED AUTHORITY MATRIX
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
# RECOVERY AST
# ============================================================

recovery_ast = ast_sha(
    RECOVERY_PATH
)


check(
    "recovery_ast_generated",
    len(
        recovery_ast
    )
    == 64,
    recovery_ast,
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
        "PHASE 4.1.6 — UNIVERSAL WORKER "
        "RECOVERY INITIAL IMPLEMENTATION"
    ),
    "=" * 112,
    "",
    (
        "WORKER RECOVERY AST SHA256: "
        + recovery_ast
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
            "INITIAL WORKER RECOVERY RESULT: "
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
        "QUEUE INFRASTRUCTURE MODIFIED: NO",
        "QUEUE RECOVERY MODIFIED: NO",
        "UNIVERSAL JOB CONTRACT MODIFIED: NO",
        "UNIVERSAL JOB ATTEMPTS MODIFIED: NO",
        "EXISTING UNIVERSAL RUNTIME WORKER MODIFIED: NO",
        "RUNTIME REGISTRATION MODIFIED: NO",
        "RUNTIME INFRASTRUCTURE MODIFIED: NO",
        "ORCHESTRATION MODIFIED: NO",
        "JOB REQUEUED: NO",
        "QUEUE MEMBERSHIP RESTORED: NO",
        "JOB ATTEMPTS INCREMENTED: NO",
        "RETRY BACKOFF CALCULATED: NO",
        "JOB STATUS MUTATED: NO",
        "LEASE ACQUIRED/RENEWED/RELEASED: NO",
        "LEASE EXPIRATION CLASSIFIED: NO",
        "WORKER HEALTH DECIDED: NO",
        "WORKER HEARTBEAT READ: NO",
        "STALE WORKER DETECTED: NO",
        "WORKER RESTARTED/TERMINATED: NO",
        "REPLACEMENT WORKER ASSIGNED: NO",
        "JOB DEAD-LETTERED: NO",
        "DEAD-LETTER JOB RECOVERED: NO",
        "JOB DISPATCHED: NO",
        "JOB EXECUTED: NO",
        "RUNTIME STATE STORE ACCESSED: NO",
        "RECOVERY RESULT PERSISTED: NO",
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
        "Phase 4.1.6 Worker Recovery initial implementation failed."
    )
