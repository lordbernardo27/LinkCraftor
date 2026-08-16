from __future__ import annotations

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
