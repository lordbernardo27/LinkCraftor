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


UNIVERSAL_QUEUE_CLEANUP_VERSION = (
    "universal_queue_cleanup_v3.1.9"
)

UNIVERSAL_QUEUE_CLEANUP_SNAPSHOT_SCHEMA_VERSION = (
    "universal_queue_cleanup_snapshot_schema_v1"
)

UNIVERSAL_QUEUE_CLEANUP_DECISION_SCHEMA_VERSION = (
    "universal_queue_cleanup_decision_schema_v1"
)


ORDINARY_QUEUE_CLEANUP_TERMINAL_STATUSES = frozenset(
    {
        UniversalJobStatus.SUCCEEDED,
        UniversalJobStatus.FAILED,
        UniversalJobStatus.CANCELLED,
        UniversalJobStatus.EXPIRED,
    }
)


class UniversalQueueCleanupError(
    ValueError
):
    """
    Raised when Universal Queue Cleanup evidence is invalid.
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
        raise UniversalQueueCleanupError(
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

        raise UniversalQueueCleanupError(
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


def normalize_universal_queue_cleanup_job_id(
    value: Any,
) -> str:

    return _normalize_required_text(
        value,
        field_name="job_id",
    )


def normalize_universal_queue_cleanup_queue_id(
    value: Any,
) -> str:

    try:

        return normalize_universal_queue_id(
            value
        )

    except UniversalQueueCreationError as exc:

        raise UniversalQueueCleanupError(
            "Invalid canonical Universal Queue queue_id.",
            code="invalid_cleanup_queue_id",
            value=value,
        ) from exc


def normalize_universal_queue_cleanup_partition_id(
    value: Any,
) -> str | None:

    return _normalize_optional_text(
        value,
        field_name="partition_id",
    )


def normalize_universal_queue_cleanup_status(
    value: Any,
) -> UniversalJobStatus:

    try:

        return UniversalJobStatus.coerce(
            value
        )

    except UniversalJobContractError as exc:

        raise UniversalQueueCleanupError(
            "Invalid Universal Job status.",
            code="invalid_cleanup_status",
            value=value,
        ) from exc


def _require_boolean(
    value: Any,
    *,
    field_name: str,
) -> bool:

    if not isinstance(
        value,
        bool,
    ):
        raise UniversalQueueCleanupError(
            f"{field_name} must be bool.",
            code=(
                "invalid_"
                + field_name
                + "_flag"
            ),
            value=value,
        )

    return value


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalQueueCleanupSnapshot:
    """
    Caller-supplied logical queue cleanup evidence.

    Phase 3.1.9 does not read queue or persistence state itself.
    """

    job_id: str
    status: UniversalJobStatus | str
    queue_id: str
    partition_id: str | None
    cleanup_authorized: bool
    retention_satisfied: bool
    authorization_basis: str
    schema_version: str = (
        UNIVERSAL_QUEUE_CLEANUP_SNAPSHOT_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        set_ = object.__setattr__

        set_(
            self,
            "job_id",
            normalize_universal_queue_cleanup_job_id(
                self.job_id
            ),
        )

        set_(
            self,
            "status",
            normalize_universal_queue_cleanup_status(
                self.status
            ),
        )

        set_(
            self,
            "queue_id",
            normalize_universal_queue_cleanup_queue_id(
                self.queue_id
            ),
        )

        set_(
            self,
            "partition_id",
            normalize_universal_queue_cleanup_partition_id(
                self.partition_id
            ),
        )

        set_(
            self,
            "cleanup_authorized",
            _require_boolean(
                self.cleanup_authorized,
                field_name="cleanup_authorized",
            ),
        )

        set_(
            self,
            "retention_satisfied",
            _require_boolean(
                self.retention_satisfied,
                field_name="retention_satisfied",
            ),
        )

        set_(
            self,
            "authorization_basis",
            _normalize_required_text(
                self.authorization_basis,
                field_name="authorization_basis",
            ),
        )

        if (
            self.schema_version
            != UNIVERSAL_QUEUE_CLEANUP_SNAPSHOT_SCHEMA_VERSION
        ):
            raise UniversalQueueCleanupError(
                "Invalid Queue Cleanup snapshot schema_version.",
                code="invalid_cleanup_snapshot_schema_version",
                value=self.schema_version,
            )

    @property
    def ordinary_terminal_candidate(
        self,
    ) -> bool:

        return (
            self.status
            in ORDINARY_QUEUE_CLEANUP_TERMINAL_STATUSES
        )

    @property
    def dead_letter_deferred(
        self,
    ) -> bool:

        return (
            self.status
            is UniversalJobStatus.DEAD_LETTER
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

            "cleanup_authorized":
                self.cleanup_authorized,

            "retention_satisfied":
                self.retention_satisfied,

            "authorization_basis":
                self.authorization_basis,

            "ordinary_terminal_candidate":
                self.ordinary_terminal_candidate,

            "dead_letter_deferred":
                self.dead_letter_deferred,
        }


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalQueueCleanupDecision:
    """
    Immutable logical Queue Cleanup decision.

    This decision does not perform deletion or persistence mutation.
    """

    job_id: str
    observed_status: UniversalJobStatus | str
    queue_id: str
    partition_id: str | None
    cleanup_eligible: bool
    cleanup_action: str
    owning_authority: str
    mutation_required: bool
    authorization_basis: str
    reason: str
    schema_version: str = (
        UNIVERSAL_QUEUE_CLEANUP_DECISION_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        set_ = object.__setattr__

        set_(
            self,
            "job_id",
            normalize_universal_queue_cleanup_job_id(
                self.job_id
            ),
        )

        status = (
            normalize_universal_queue_cleanup_status(
                self.observed_status
            )
        )

        set_(
            self,
            "observed_status",
            status,
        )

        set_(
            self,
            "queue_id",
            normalize_universal_queue_cleanup_queue_id(
                self.queue_id
            ),
        )

        set_(
            self,
            "partition_id",
            normalize_universal_queue_cleanup_partition_id(
                self.partition_id
            ),
        )

        set_(
            self,
            "cleanup_eligible",
            _require_boolean(
                self.cleanup_eligible,
                field_name="cleanup_eligible",
            ),
        )

        set_(
            self,
            "mutation_required",
            _require_boolean(
                self.mutation_required,
                field_name="mutation_required",
            ),
        )

        if self.mutation_required is not False:

            raise UniversalQueueCleanupError(
                (
                    "Phase 3.1.9 decisions must not perform "
                    "queue or persistence mutation."
                ),
                code="cleanup_mutation_not_owned",
                value=self.mutation_required,
            )

        set_(
            self,
            "cleanup_action",
            _normalize_required_text(
                self.cleanup_action,
                field_name="cleanup_action",
            ),
        )

        set_(
            self,
            "owning_authority",
            _normalize_required_text(
                self.owning_authority,
                field_name="owning_authority",
            ),
        )

        set_(
            self,
            "authorization_basis",
            _normalize_required_text(
                self.authorization_basis,
                field_name="authorization_basis",
            ),
        )

        set_(
            self,
            "reason",
            _normalize_required_text(
                self.reason,
                field_name="reason",
            ),
        )

        if self.cleanup_eligible:

            if (
                status
                not in ORDINARY_QUEUE_CLEANUP_TERMINAL_STATUSES
            ):
                raise UniversalQueueCleanupError(
                    (
                        "Only ordinary terminal statuses may be "
                        "cleanup-eligible under Phase 3.1.9."
                    ),
                    code="invalid_cleanup_eligible_status",
                    value=status.value,
                )

            if (
                self.cleanup_action
                != "authorize_logical_queue_cleanup"
            ):
                raise UniversalQueueCleanupError(
                    "Invalid cleanup-eligible action.",
                    code="invalid_cleanup_eligible_action",
                    value=self.cleanup_action,
                )

            if (
                self.owning_authority
                != "3.1.9 Queue Cleanup"
            ):
                raise UniversalQueueCleanupError(
                    "Invalid cleanup-eligible authority.",
                    code="invalid_cleanup_eligible_authority",
                    value=self.owning_authority,
                )

        elif (
            status
            is UniversalJobStatus.DEAD_LETTER
        ):

            if (
                self.cleanup_action
                != "defer_dead_letter_retention"
            ):
                raise UniversalQueueCleanupError(
                    "Invalid DEAD_LETTER cleanup action.",
                    code="invalid_dead_letter_cleanup_action",
                    value=self.cleanup_action,
                )

            if (
                self.owning_authority
                != "Dead Letter retention / lifecycle authority"
            ):
                raise UniversalQueueCleanupError(
                    "Invalid DEAD_LETTER cleanup authority.",
                    code="invalid_dead_letter_cleanup_authority",
                    value=self.owning_authority,
                )

        else:

            if (
                self.cleanup_action
                != "retain_queue_state"
            ):
                raise UniversalQueueCleanupError(
                    (
                        "A non-cleanup-eligible ordinary decision "
                        "must retain queue state."
                    ),
                    code="invalid_cleanup_retained_action",
                    value=self.cleanup_action,
                )

            if (
                self.owning_authority
                != "3.1.9 Queue Cleanup"
            ):
                raise UniversalQueueCleanupError(
                    (
                        "A retained ordinary queue decision must "
                        "remain owned by 3.1.9 Queue Cleanup."
                    ),
                    code="invalid_cleanup_retained_authority",
                    value=self.owning_authority,
                )

        if (
            self.schema_version
            != UNIVERSAL_QUEUE_CLEANUP_DECISION_SCHEMA_VERSION
        ):
            raise UniversalQueueCleanupError(
                "Invalid Queue Cleanup decision schema_version.",
                code="invalid_cleanup_decision_schema_version",
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

            "observed_status":
                self.observed_status.value,

            "queue_id":
                self.queue_id,

            "partition_id":
                self.partition_id,

            "cleanup_eligible":
                self.cleanup_eligible,

            "cleanup_action":
                self.cleanup_action,

            "owning_authority":
                self.owning_authority,

            "mutation_required":
                self.mutation_required,

            "authorization_basis":
                self.authorization_basis,

            "reason":
                self.reason,
        }


def create_universal_queue_cleanup_snapshot(
    *,
    job_id: str,
    status: UniversalJobStatus | str,
    queue_id: str,
    partition_id: str | None = None,
    cleanup_authorized: bool,
    retention_satisfied: bool,
    authorization_basis: str,
) -> UniversalQueueCleanupSnapshot:

    return UniversalQueueCleanupSnapshot(
        job_id=job_id,
        status=status,
        queue_id=queue_id,
        partition_id=partition_id,
        cleanup_authorized=cleanup_authorized,
        retention_satisfied=retention_satisfied,
        authorization_basis=authorization_basis,
    )


def evaluate_universal_queue_cleanup(
    *,
    snapshot: UniversalQueueCleanupSnapshot,
) -> UniversalQueueCleanupDecision:
    """
    Evaluate logical cleanup eligibility from caller-supplied evidence.

    No deletion, retention calculation or persistence access occurs here.
    """

    if not isinstance(
        snapshot,
        UniversalQueueCleanupSnapshot,
    ):
        raise UniversalQueueCleanupError(
            (
                "snapshot must be a "
                "UniversalQueueCleanupSnapshot instance."
            ),
            code="invalid_cleanup_snapshot",
            value=snapshot,
        )

    if (
        snapshot.status
        is UniversalJobStatus.DEAD_LETTER
    ):

        return UniversalQueueCleanupDecision(
            job_id=snapshot.job_id,
            observed_status=snapshot.status,
            queue_id=snapshot.queue_id,
            partition_id=snapshot.partition_id,
            cleanup_eligible=False,
            cleanup_action="defer_dead_letter_retention",
            owning_authority=(
                "Dead Letter retention / lifecycle authority"
            ),
            mutation_required=False,
            authorization_basis=snapshot.authorization_basis,
            reason=(
                "DEAD_LETTER retention and deletion are outside "
                "ordinary Queue Cleanup."
            ),
        )

    if not snapshot.ordinary_terminal_candidate:

        return UniversalQueueCleanupDecision(
            job_id=snapshot.job_id,
            observed_status=snapshot.status,
            queue_id=snapshot.queue_id,
            partition_id=snapshot.partition_id,
            cleanup_eligible=False,
            cleanup_action="retain_queue_state",
            owning_authority="3.1.9 Queue Cleanup",
            mutation_required=False,
            authorization_basis=snapshot.authorization_basis,
            reason=(
                "Non-terminal state is not eligible for "
                "ordinary queue cleanup."
            ),
        )

    if not snapshot.cleanup_authorized:

        return UniversalQueueCleanupDecision(
            job_id=snapshot.job_id,
            observed_status=snapshot.status,
            queue_id=snapshot.queue_id,
            partition_id=snapshot.partition_id,
            cleanup_eligible=False,
            cleanup_action="retain_queue_state",
            owning_authority="3.1.9 Queue Cleanup",
            mutation_required=False,
            authorization_basis=snapshot.authorization_basis,
            reason=(
                "Caller has not authorized logical queue cleanup."
            ),
        )

    if not snapshot.retention_satisfied:

        return UniversalQueueCleanupDecision(
            job_id=snapshot.job_id,
            observed_status=snapshot.status,
            queue_id=snapshot.queue_id,
            partition_id=snapshot.partition_id,
            cleanup_eligible=False,
            cleanup_action="retain_queue_state",
            owning_authority="3.1.9 Queue Cleanup",
            mutation_required=False,
            authorization_basis=snapshot.authorization_basis,
            reason=(
                "Caller-supplied retention requirement is "
                "not yet satisfied."
            ),
        )

    return UniversalQueueCleanupDecision(
        job_id=snapshot.job_id,
        observed_status=snapshot.status,
        queue_id=snapshot.queue_id,
        partition_id=snapshot.partition_id,
        cleanup_eligible=True,
        cleanup_action="authorize_logical_queue_cleanup",
        owning_authority="3.1.9 Queue Cleanup",
        mutation_required=False,
        authorization_basis=snapshot.authorization_basis,
        reason=(
            "Ordinary terminal state has explicit cleanup "
            "authorization and satisfied retention evidence."
        ),
    )


def explain_universal_queue_cleanup_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "3.1.9",

            "component":
                "Universal Queue Cleanup",

            "version":
                UNIVERSAL_QUEUE_CLEANUP_VERSION,

            "snapshot_schema":
                UNIVERSAL_QUEUE_CLEANUP_SNAPSHOT_SCHEMA_VERSION,

            "decision_schema":
                UNIVERSAL_QUEUE_CLEANUP_DECISION_SCHEMA_VERSION,

            "scope":
                "LinkCraftor-wide",

            "queue_model": (
                "Universal Queue membership remains status-backed; "
                "Phase 3.1.9 does not assume a second persisted "
                "queue-membership record exists"
            ),

            "ordinary_terminal_statuses": tuple(
                sorted(
                    status.value
                    for status
                    in ORDINARY_QUEUE_CLEANUP_TERMINAL_STATUSES
                )
            ),

            "eligibility_rule": (
                "ordinary terminal status plus explicit "
                "cleanup_authorized plus caller-supplied "
                "retention_satisfied is required"
            ),

            "active_state_rule": (
                "non-terminal Universal Job states are never "
                "ordinary queue-cleanup eligible"
            ),

            "retention_rule": (
                "retention_satisfied is caller-supplied; 3.1.9 "
                "does not calculate retention age, TTL or timestamps"
            ),

            "job_history_rule": (
                "Universal Job history survives Queue Cleanup; "
                "cleanup eligibility never means delete the job record"
            ),

            "dead_letter_boundary": (
                "DEAD_LETTER retention and deletion remain outside "
                "ordinary 3.1.9 Queue Cleanup"
            ),

            "physical_cleanup_boundary": (
                "physical broker, filesystem, database, Redis, SQS "
                "or Kafka cleanup belongs to persistence/backend "
                "authorities"
            ),

            "archive_boundary": (
                "archive and compaction operations remain separate "
                "persistence responsibilities"
            ),

            "decision_rule": (
                "3.1.9 produces an immutable logical cleanup "
                "authorization decision only"
            ),

            "prohibitions": (
                "does not create Universal Jobs",
                "does not delete Universal Jobs",
                "does not mutate Universal Jobs",
                "does not mutate job status",
                "does not enqueue jobs",
                "does not dequeue jobs",
                "does not claim jobs",
                "does not requeue jobs",
                "does not delete queue records",
                "does not physically remove queue records",
                "does not calculate retention age",
                "does not calculate TTL",
                "does not read timestamps from storage",
                "does not archive jobs",
                "does not compact storage",
                "does not delete dead-letter records",
                "does not apply dead-letter retention",
                "does not access the Job Store",
                "does not access Runtime State Store",
                "does not access orchestration",
                "does not read live queue state",
                "does not create physical queues",
                "does not delete physical queues",
                "does not delete filesystem queue files",
                "does not delete Redis queue entries",
                "does not delete cloud queue messages",
                "does not delete Kafka records",
                "does not perform filesystem I/O",
                "does not perform network I/O",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_QUEUE_CLEANUP_VERSION",
    "UNIVERSAL_QUEUE_CLEANUP_SNAPSHOT_SCHEMA_VERSION",
    "UNIVERSAL_QUEUE_CLEANUP_DECISION_SCHEMA_VERSION",
    "ORDINARY_QUEUE_CLEANUP_TERMINAL_STATUSES",
    "UniversalQueueCleanupError",
    "UniversalQueueCleanupSnapshot",
    "UniversalQueueCleanupDecision",
    "normalize_universal_queue_cleanup_job_id",
    "normalize_universal_queue_cleanup_queue_id",
    "normalize_universal_queue_cleanup_partition_id",
    "normalize_universal_queue_cleanup_status",
    "create_universal_queue_cleanup_snapshot",
    "evaluate_universal_queue_cleanup",
    "explain_universal_queue_cleanup_v1",
]
