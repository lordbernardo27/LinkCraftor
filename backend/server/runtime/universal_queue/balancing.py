from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Iterable, Mapping

from backend.server.runtime.universal_queue.creation import (
    UniversalQueueCreationError,
    normalize_universal_queue_id,
)


UNIVERSAL_QUEUE_BALANCING_VERSION = (
    "universal_queue_balancing_v3.1.5"
)

UNIVERSAL_QUEUE_LOAD_SNAPSHOT_SCHEMA_VERSION = (
    "universal_queue_load_snapshot_schema_v1"
)

UNIVERSAL_QUEUE_BALANCE_DECISION_SCHEMA_VERSION = (
    "universal_queue_balance_decision_schema_v1"
)


class UniversalQueueBalancingError(
    ValueError
):
    """Raised when Universal Queue balancing input is invalid."""

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


def normalize_universal_queue_balance_queue_id(
    value: Any,
) -> str:

    try:
        return normalize_universal_queue_id(
            value
        )

    except UniversalQueueCreationError as exc:

        raise UniversalQueueBalancingError(
            "Invalid canonical Universal Queue queue_id.",
            code="invalid_balance_queue_id",
            value=value,
        ) from exc


def normalize_universal_queue_depth(
    value: Any,
) -> int:
    """
    Normalize one explicit queued-job count.

    Queue depth is a non-negative integer.

    bool is rejected even though bool is an int subclass.
    """

    if isinstance(
        value,
        bool,
    ):
        raise UniversalQueueBalancingError(
            "queue_depth must be a non-negative integer.",
            code="invalid_queue_depth_type",
            value=value,
        )

    if not isinstance(
        value,
        int,
    ):
        raise UniversalQueueBalancingError(
            "queue_depth must be a non-negative integer.",
            code="invalid_queue_depth_type",
            value=value,
        )

    if value < 0:

        raise UniversalQueueBalancingError(
            "queue_depth must not be negative.",
            code="negative_queue_depth",
            value=value,
        )

    return value


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalQueueLoadSnapshot:
    """
    Immutable caller-supplied logical queue-load observation.

    Phase 3.1.5 does not read live queue state itself.
    """

    queue_id: str
    queue_depth: int
    schema_version: str = (
        UNIVERSAL_QUEUE_LOAD_SNAPSHOT_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        set_ = object.__setattr__

        set_(
            self,
            "queue_id",
            normalize_universal_queue_balance_queue_id(
                self.queue_id
            ),
        )

        set_(
            self,
            "queue_depth",
            normalize_universal_queue_depth(
                self.queue_depth
            ),
        )

        if (
            self.schema_version
            != UNIVERSAL_QUEUE_LOAD_SNAPSHOT_SCHEMA_VERSION
        ):
            raise UniversalQueueBalancingError(
                "Invalid queue-load snapshot schema_version.",
                code="invalid_queue_load_snapshot_schema_version",
                value=self.schema_version,
            )

    @property
    def balance_key(
        self,
    ) -> tuple[int, str]:
        """
        Least queue depth wins.

        queue_id is the deterministic tie-break.
        """

        return (
            self.queue_depth,
            self.queue_id,
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "schema_version":
                self.schema_version,

            "queue_id":
                self.queue_id,

            "queue_depth":
                self.queue_depth,

            "balance_key": [
                self.queue_depth,
                self.queue_id,
            ],
        }


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalQueueBalanceDecision:
    """
    Immutable logical queue-balancing decision.
    """

    selected_queue_id: str
    selected_queue_depth: int
    candidate_count: int
    reason: str
    schema_version: str = (
        UNIVERSAL_QUEUE_BALANCE_DECISION_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        set_ = object.__setattr__

        set_(
            self,
            "selected_queue_id",
            normalize_universal_queue_balance_queue_id(
                self.selected_queue_id
            ),
        )

        set_(
            self,
            "selected_queue_depth",
            normalize_universal_queue_depth(
                self.selected_queue_depth
            ),
        )

        if (
            isinstance(
                self.candidate_count,
                bool,
            )
            or not isinstance(
                self.candidate_count,
                int,
            )
            or self.candidate_count < 1
        ):
            raise UniversalQueueBalancingError(
                "candidate_count must be an integer >= 1.",
                code="invalid_candidate_count",
                value=self.candidate_count,
            )

        reason = str(
            self.reason
            if self.reason is not None
            else ""
        ).strip()

        if not reason:

            raise UniversalQueueBalancingError(
                "reason must not be blank.",
                code="blank_balance_reason",
                value=self.reason,
            )

        set_(
            self,
            "reason",
            reason,
        )

        if (
            self.schema_version
            != UNIVERSAL_QUEUE_BALANCE_DECISION_SCHEMA_VERSION
        ):
            raise UniversalQueueBalancingError(
                "Invalid balance-decision schema_version.",
                code="invalid_balance_decision_schema_version",
                value=self.schema_version,
            )

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "schema_version":
                self.schema_version,

            "selected_queue_id":
                self.selected_queue_id,

            "selected_queue_depth":
                self.selected_queue_depth,

            "candidate_count":
                self.candidate_count,

            "reason":
                self.reason,
        }


def create_universal_queue_load_snapshot(
    *,
    queue_id: str,
    queue_depth: int,
) -> UniversalQueueLoadSnapshot:

    return UniversalQueueLoadSnapshot(
        queue_id=queue_id,
        queue_depth=queue_depth,
    )


def balance_universal_queues(
    *,
    candidates: Iterable[
        UniversalQueueLoadSnapshot
    ],
) -> UniversalQueueBalanceDecision:
    """
    Select one logical queue from explicit load snapshots.

    Canonical rule:
        lowest queue_depth
        then queue_id ascending

    No queue state is read and no job is moved.
    """

    if isinstance(
        candidates,
        (
            str,
            bytes,
            bytearray,
        ),
    ):
        raise UniversalQueueBalancingError(
            "candidates must be an iterable of queue-load snapshots.",
            code="invalid_balance_candidate_collection",
            value=candidates,
        )

    try:
        materialized = tuple(
            candidates
        )

    except TypeError as exc:

        raise UniversalQueueBalancingError(
            "candidates must be iterable.",
            code="invalid_balance_candidate_collection",
            value=candidates,
        ) from exc

    if not materialized:

        raise UniversalQueueBalancingError(
            "At least one queue-load candidate is required.",
            code="empty_balance_candidate_collection",
            value=materialized,
        )

    seen_queue_ids: set[str] = set()

    for candidate in materialized:

        if not isinstance(
            candidate,
            UniversalQueueLoadSnapshot,
        ):
            raise UniversalQueueBalancingError(
                (
                    "candidates must contain only "
                    "UniversalQueueLoadSnapshot members."
                ),
                code="invalid_balance_candidate_member",
                value=candidate,
            )

        if candidate.queue_id in seen_queue_ids:

            raise UniversalQueueBalancingError(
                "Duplicate queue_id in balance candidates.",
                code="duplicate_balance_queue_id",
                value=candidate.queue_id,
            )

        seen_queue_ids.add(
            candidate.queue_id
        )

    selected = min(
        materialized,
        key=lambda item: item.balance_key,
    )

    reason = (
        "single_candidate"
        if len(materialized) == 1
        else "least_queue_depth"
    )

    return UniversalQueueBalanceDecision(
        selected_queue_id=selected.queue_id,
        selected_queue_depth=selected.queue_depth,
        candidate_count=len(
            materialized
        ),
        reason=reason,
    )


def explain_universal_queue_balancing_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "3.1.5",

            "component":
                "Universal Queue Balancing",

            "version":
                UNIVERSAL_QUEUE_BALANCING_VERSION,

            "load_snapshot_schema":
                UNIVERSAL_QUEUE_LOAD_SNAPSHOT_SCHEMA_VERSION,

            "decision_schema":
                UNIVERSAL_QUEUE_BALANCE_DECISION_SCHEMA_VERSION,

            "scope":
                "LinkCraftor-wide",

            "canonical_load_signal":
                "queue_depth",

            "selection_rule": (
                "select the candidate with the lowest "
                "explicit queue_depth"
            ),

            "tie_break_rule": (
                "equal queue_depth uses queue_id ascending "
                "for deterministic selection"
            ),

            "snapshot_rule": (
                "queue-load snapshots are caller-supplied; "
                "3.1.5 does not read live queue state"
            ),

            "routing_relationship": (
                "3.1.4 determines logical routing; 3.1.5 "
                "may choose among explicitly supplied "
                "equivalent logical queue candidates"
            ),

            "partition_boundary": (
                "workspace, shard and partition distribution "
                "belong to 3.1.6 Queue Partitioning"
            ),

            "capacity_boundary": (
                "capacity enforcement belongs to "
                "3.1.11 Queue Capacity Limits"
            ),

            "fairness_boundary": (
                "starvation prevention and fairness policy "
                "belong to 3.1.12 Queue Fairness"
            ),

            "worker_boundary": (
                "worker load, worker capability and worker "
                "assignment belong to Worker Infrastructure"
            ),

            "prohibitions": (
                "does not create Universal Queues",
                "does not create Universal Jobs",
                "does not mutate jobs",
                "does not mutate queues",
                "does not move jobs between queues",
                "does not enqueue jobs",
                "does not dequeue jobs",
                "does not claim jobs",
                "does not read live queue state",
                "does not access orchestration",
                "does not access the job store",
                "does not evaluate Queue Routing rules",
                "does not schedule jobs",
                "does not prioritize jobs",
                "does not partition queues",
                "does not select shards",
                "does not distribute by workspace_id",
                "does not select workers",
                "does not inspect worker capability",
                "does not balance worker load",
                "does not enforce queue capacity",
                "does not apply backpressure",
                "does not implement queue fairness",
                "does not prevent starvation",
                "does not implement priority aging",
                "does not maintain round-robin state",
                "does not implement weighted balancing",
                "does not implement retry routing",
                "does not create physical queues",
                "does not perform filesystem I/O",
                "does not perform network I/O",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_QUEUE_BALANCING_VERSION",
    "UNIVERSAL_QUEUE_LOAD_SNAPSHOT_SCHEMA_VERSION",
    "UNIVERSAL_QUEUE_BALANCE_DECISION_SCHEMA_VERSION",
    "UniversalQueueBalancingError",
    "UniversalQueueLoadSnapshot",
    "UniversalQueueBalanceDecision",
    "normalize_universal_queue_balance_queue_id",
    "normalize_universal_queue_depth",
    "create_universal_queue_load_snapshot",
    "balance_universal_queues",
    "explain_universal_queue_balancing_v1",
]
