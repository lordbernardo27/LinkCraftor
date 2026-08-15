from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping

from backend.server.runtime.universal_jobs.contract import (
    UniversalJobContractError,
    UniversalJobStatus,
)

from backend.server.runtime.universal_queue.creation import (
    UniversalQueueCreationError,
    normalize_universal_queue_id,
)


UNIVERSAL_QUEUE_RECOVERY_VERSION = (
    "universal_queue_recovery_v3.1.7"
)

UNIVERSAL_QUEUE_RECOVERY_SNAPSHOT_SCHEMA_VERSION = (
    "universal_queue_recovery_snapshot_schema_v1"
)

UNIVERSAL_QUEUE_RECOVERY_DECISION_SCHEMA_VERSION = (
    "universal_queue_recovery_decision_schema_v1"
)


class UniversalQueueRecoveryError(
    ValueError
):
    """
    Raised when Universal Queue Recovery input is invalid.
    """

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


def _normalize_required_text(
    value: Any,
    *,
    field_name: str,
) -> str:

    if not isinstance(
        value,
        str,
    ):
        raise UniversalQueueRecoveryError(
            f"{field_name} must be a string.",
            code=(
                "invalid_"
                + field_name
                + "_type"
            ),
            value=value,
        )

    normalized = value.strip()

    if not normalized:

        raise UniversalQueueRecoveryError(
            f"{field_name} must not be blank.",
            code=(
                "blank_"
                + field_name
            ),
            value=value,
        )

    return normalized


def _normalize_optional_text(
    value: Any,
    *,
    field_name: str,
) -> str | None:

    if value is None:
        return None

    return _normalize_required_text(
        value,
        field_name=field_name,
    )


def normalize_universal_queue_recovery_job_id(
    value: Any,
) -> str:

    return _normalize_required_text(
        value,
        field_name="job_id",
    )


def normalize_universal_queue_recovery_queue_id(
    value: Any,
) -> str:

    try:
        return normalize_universal_queue_id(
            value
        )

    except UniversalQueueCreationError as exc:

        raise UniversalQueueRecoveryError(
            "Invalid canonical Universal Queue queue_id.",
            code="invalid_recovery_queue_id",
            value=value,
        ) from exc


def normalize_universal_queue_recovery_partition_id(
    value: Any,
) -> str | None:

    return _normalize_optional_text(
        value,
        field_name="partition_id",
    )


def normalize_universal_queue_recovery_status(
    value: Any,
) -> UniversalJobStatus:

    try:
        return UniversalJobStatus.coerce(
            value
        )

    except UniversalJobContractError as exc:

        raise UniversalQueueRecoveryError(
            "Invalid Universal Job status.",
            code="invalid_recovery_job_status",
            value=value,
        ) from exc


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalQueueRecoverySnapshot:
    """
    Caller-supplied persisted queue-state observation.

    This is not a Job Store reader.
    """

    job_id: str
    status: UniversalJobStatus | str
    queue_id: str
    partition_id: str | None = None
    schema_version: str = (
        UNIVERSAL_QUEUE_RECOVERY_SNAPSHOT_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        set_ = object.__setattr__

        set_(
            self,
            "job_id",
            normalize_universal_queue_recovery_job_id(
                self.job_id
            ),
        )

        set_(
            self,
            "status",
            normalize_universal_queue_recovery_status(
                self.status
            ),
        )

        set_(
            self,
            "queue_id",
            normalize_universal_queue_recovery_queue_id(
                self.queue_id
            ),
        )

        set_(
            self,
            "partition_id",
            normalize_universal_queue_recovery_partition_id(
                self.partition_id
            ),
        )

        if (
            self.schema_version
            != UNIVERSAL_QUEUE_RECOVERY_SNAPSHOT_SCHEMA_VERSION
        ):
            raise UniversalQueueRecoveryError(
                "Invalid recovery snapshot schema_version.",
                code="invalid_recovery_snapshot_schema_version",
                value=self.schema_version,
            )

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "schema_version":
                self.schema_version,

            "job_id":
                self.job_id,

            "status":
                self.status.value,

            "queue_id":
                self.queue_id,

            "partition_id":
                self.partition_id,
        }


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalQueueRecoveryDecision:
    """
    Immutable Queue Recovery decision.

    The decision does not mutate the Universal Job.
    """

    job_id: str
    observed_status: UniversalJobStatus | str
    queue_id: str
    partition_id: str | None
    recoverable_queue_membership: bool
    recovery_action: str
    owning_authority: str
    mutation_required: bool
    reason: str
    schema_version: str = (
        UNIVERSAL_QUEUE_RECOVERY_DECISION_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        set_ = object.__setattr__

        set_(
            self,
            "job_id",
            normalize_universal_queue_recovery_job_id(
                self.job_id
            ),
        )

        set_(
            self,
            "observed_status",
            normalize_universal_queue_recovery_status(
                self.observed_status
            ),
        )

        set_(
            self,
            "queue_id",
            normalize_universal_queue_recovery_queue_id(
                self.queue_id
            ),
        )

        set_(
            self,
            "partition_id",
            normalize_universal_queue_recovery_partition_id(
                self.partition_id
            ),
        )

        if not isinstance(
            self.recoverable_queue_membership,
            bool,
        ):
            raise UniversalQueueRecoveryError(
                "recoverable_queue_membership must be bool.",
                code="invalid_recoverable_membership_flag",
                value=self.recoverable_queue_membership,
            )

        if not isinstance(
            self.mutation_required,
            bool,
        ):
            raise UniversalQueueRecoveryError(
                "mutation_required must be bool.",
                code="invalid_mutation_required_flag",
                value=self.mutation_required,
            )

        action = _normalize_required_text(
            self.recovery_action,
            field_name="recovery_action",
        )

        authority = _normalize_required_text(
            self.owning_authority,
            field_name="owning_authority",
        )

        reason = _normalize_required_text(
            self.reason,
            field_name="reason",
        )

        set_(
            self,
            "recovery_action",
            action,
        )

        set_(
            self,
            "owning_authority",
            authority,
        )

        set_(
            self,
            "reason",
            reason,
        )

        if (
            self.schema_version
            != UNIVERSAL_QUEUE_RECOVERY_DECISION_SCHEMA_VERSION
        ):
            raise UniversalQueueRecoveryError(
                "Invalid recovery decision schema_version.",
                code="invalid_recovery_decision_schema_version",
                value=self.schema_version,
            )

        if self.observed_status is UniversalJobStatus.QUEUED:

            if (
                self.recoverable_queue_membership
                is not True
                or self.recovery_action
                != "preserve_persisted_membership"
                or self.owning_authority
                != "3.1.7 Queue Recovery"
                or self.mutation_required
                is not False
            ):
                raise UniversalQueueRecoveryError(
                    (
                        "QUEUED recovery decision is "
                        "internally inconsistent."
                    ),
                    code="inconsistent_queued_recovery_decision",
                    value=self.to_dict(),
                )

        else:

            if self.recoverable_queue_membership is not False:

                raise UniversalQueueRecoveryError(
                    (
                        "Only persisted QUEUED status may be "
                        "queue-recoverable in Phase 3.1.7."
                    ),
                    code="inconsistent_nonqueued_recovery_decision",
                    value=self.observed_status.value,
                )

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "schema_version":
                self.schema_version,

            "job_id":
                self.job_id,

            "observed_status":
                self.observed_status.value,

            "queue_id":
                self.queue_id,

            "partition_id":
                self.partition_id,

            "recoverable_queue_membership":
                self.recoverable_queue_membership,

            "recovery_action":
                self.recovery_action,

            "owning_authority":
                self.owning_authority,

            "mutation_required":
                self.mutation_required,

            "reason":
                self.reason,
        }


def create_universal_queue_recovery_snapshot(
    *,
    job_id: str,
    status: UniversalJobStatus | str,
    queue_id: str,
    partition_id: str | None = None,
) -> UniversalQueueRecoverySnapshot:

    return UniversalQueueRecoverySnapshot(
        job_id=job_id,
        status=status,
        queue_id=queue_id,
        partition_id=partition_id,
    )


def _nonqueued_authority(
    status: UniversalJobStatus,
) -> tuple[str, str, str]:

    if status is UniversalJobStatus.CREATED:

        return (
            "no_queue_recovery",
            "Universal Job creation/submission authority",
            "CREATED does not represent queue membership.",
        )

    if status is UniversalJobStatus.SCHEDULED:

        return (
            "defer_scheduled_state",
            "Queue Scheduling / lifecycle transition authority",
            (
                "SCHEDULED is not persisted QUEUED membership; "
                "Queue Recovery does not transition it."
            ),
        )

    if status is UniversalJobStatus.LEASED:

        return (
            "defer_lease_recovery",
            "Worker / Lease Recovery infrastructure",
            (
                "LEASED recovery requires lease ownership and "
                "expiration semantics outside Queue Recovery."
            ),
        )

    if status is UniversalJobStatus.RUNNING:

        return (
            "defer_running_recovery",
            "Worker / Reliability Recovery infrastructure",
            (
                "RUNNING recovery requires stale-worker or "
                "execution-state recovery outside Queue Recovery."
            ),
        )

    if status is UniversalJobStatus.SUSPENDED:

        return (
            "defer_resume",
            "Execution / Pause-Resume authority",
            (
                "SUSPENDED recovery requires resume semantics "
                "outside Queue Recovery."
            ),
        )

    if status is UniversalJobStatus.FAILED:

        return (
            "defer_retry",
            "Retry / Reliability authority",
            (
                "FAILED recovery requires retryability and "
                "attempt-policy semantics outside Queue Recovery."
            ),
        )

    if status is UniversalJobStatus.DEAD_LETTER:

        return (
            "defer_dead_letter",
            "3.1.8 Dead Letter Queues",
            (
                "DEAD_LETTER handling is reserved for "
                "Phase 3.1.8."
            ),
        )

    if status is UniversalJobStatus.SUCCEEDED:

        return (
            "no_queue_recovery",
            "none",
            "SUCCEEDED is terminal and has no queue membership to recover.",
        )

    if status is UniversalJobStatus.CANCELLED:

        return (
            "no_queue_recovery",
            "none",
            "CANCELLED is terminal and has no queue membership to recover.",
        )

    if status is UniversalJobStatus.EXPIRED:

        return (
            "no_queue_recovery",
            "Reliability / lifecycle authority",
            (
                "EXPIRED is terminal; any higher-level recovery "
                "policy is outside Queue Recovery."
            ),
        )

    raise UniversalQueueRecoveryError(
        "Unsupported Universal Job status.",
        code="unsupported_recovery_job_status",
        value=status.value,
    )


def recover_universal_queue_membership(
    *,
    snapshot: UniversalQueueRecoverySnapshot,
) -> UniversalQueueRecoveryDecision:
    """
    Evaluate persisted logical queue membership.

    Persisted QUEUED state already expresses queue membership.
    Therefore Phase 3.1.7 preserves that membership and requires
    no job-status mutation.

    All other states are delegated to their owning authorities.
    """

    if not isinstance(
        snapshot,
        UniversalQueueRecoverySnapshot,
    ):
        raise UniversalQueueRecoveryError(
            (
                "snapshot must be a "
                "UniversalQueueRecoverySnapshot."
            ),
            code="invalid_recovery_snapshot",
            value=snapshot,
        )

    if snapshot.status is UniversalJobStatus.QUEUED:

        return UniversalQueueRecoveryDecision(
            job_id=snapshot.job_id,
            observed_status=snapshot.status,
            queue_id=snapshot.queue_id,
            partition_id=snapshot.partition_id,
            recoverable_queue_membership=True,
            recovery_action="preserve_persisted_membership",
            owning_authority="3.1.7 Queue Recovery",
            mutation_required=False,
            reason=(
                "Persisted QUEUED status already expresses "
                "logical queue membership."
            ),
        )

    (
        action,
        authority,
        reason,
    ) = _nonqueued_authority(
        snapshot.status
    )

    return UniversalQueueRecoveryDecision(
        job_id=snapshot.job_id,
        observed_status=snapshot.status,
        queue_id=snapshot.queue_id,
        partition_id=snapshot.partition_id,
        recoverable_queue_membership=False,
        recovery_action=action,
        owning_authority=authority,
        mutation_required=False,
        reason=reason,
    )


def explain_universal_queue_recovery_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "3.1.7",

            "component":
                "Universal Queue Recovery",

            "version":
                UNIVERSAL_QUEUE_RECOVERY_VERSION,

            "snapshot_schema":
                UNIVERSAL_QUEUE_RECOVERY_SNAPSHOT_SCHEMA_VERSION,

            "decision_schema":
                UNIVERSAL_QUEUE_RECOVERY_DECISION_SCHEMA_VERSION,

            "scope":
                "LinkCraftor-wide",

            "canonical_recovery_state":
                "queued",

            "queue_membership_rule": (
                "persisted QUEUED Universal Job status already "
                "expresses logical queue membership"
            ),

            "recovery_rule": (
                "QUEUED membership is preserved without status "
                "mutation or re-enqueue"
            ),

            "snapshot_rule": (
                "persisted state is caller-supplied; Phase 3.1.7 "
                "does not read the Job Store or queue directly"
            ),

            "identity_rule": (
                "queue_id and optional partition_id are preserved "
                "exactly from the supplied persisted-state snapshot"
            ),

            "scheduled_boundary": (
                "SCHEDULED transition to QUEUED belongs to "
                "scheduling/lifecycle transition authority"
            ),

            "lease_boundary": (
                "LEASED recovery belongs to Worker / Lease "
                "Recovery infrastructure"
            ),

            "running_boundary": (
                "RUNNING stale-worker recovery belongs to "
                "Worker / Reliability Recovery infrastructure"
            ),

            "retry_boundary": (
                "FAILED retryability, attempts and backoff remain "
                "outside Queue Recovery"
            ),

            "checkpoint_boundary": (
                "checkpoint resume belongs to Execution / "
                "Reliability infrastructure"
            ),

            "dead_letter_boundary": (
                "DEAD_LETTER handling belongs to "
                "3.1.8 Dead Letter Queues"
            ),

            "prohibitions": (
                "does not create Universal Queues",
                "does not create Universal Jobs",
                "does not mutate Universal Jobs",
                "does not mutate job status",
                "does not transition jobs to QUEUED",
                "does not enqueue jobs",
                "does not dequeue jobs",
                "does not claim jobs",
                "does not requeue jobs",
                "does not read live queue state",
                "does not access the Job Store",
                "does not access orchestration",
                "does not detect stale workers",
                "does not detect expired leases",
                "does not recover leases",
                "does not recover RUNNING jobs",
                "does not increment attempts",
                "does not decide retryability",
                "does not calculate retry backoff",
                "does not schedule retries",
                "does not resume checkpoints",
                "does not move jobs to dead letter",
                "does not recover dead-letter jobs",
                "does not reroute jobs",
                "does not rebalance queues",
                "does not repartition jobs",
                "does not select workers",
                "does not create physical queues",
                "does not perform filesystem I/O",
                "does not perform network I/O",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_QUEUE_RECOVERY_VERSION",
    "UNIVERSAL_QUEUE_RECOVERY_SNAPSHOT_SCHEMA_VERSION",
    "UNIVERSAL_QUEUE_RECOVERY_DECISION_SCHEMA_VERSION",
    "UniversalQueueRecoveryError",
    "UniversalQueueRecoverySnapshot",
    "UniversalQueueRecoveryDecision",
    "normalize_universal_queue_recovery_job_id",
    "normalize_universal_queue_recovery_queue_id",
    "normalize_universal_queue_recovery_partition_id",
    "normalize_universal_queue_recovery_status",
    "create_universal_queue_recovery_snapshot",
    "recover_universal_queue_membership",
    "explain_universal_queue_recovery_v1",
]
