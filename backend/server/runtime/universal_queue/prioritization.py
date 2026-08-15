from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Iterable, Mapping, Sequence

from backend.server.runtime.universal_jobs.priority import (
    UniversalJobPriorityError,
    normalize_universal_job_priority,
    universal_job_priority_order,
)


UNIVERSAL_QUEUE_PRIORITIZATION_VERSION = (
    "universal_queue_prioritization_v3.1.3"
)

UNIVERSAL_QUEUE_PRIORITY_RANK_SCHEMA_VERSION = (
    "universal_queue_priority_rank_schema_v1"
)


class UniversalQueuePrioritizationError(
    ValueError
):
    """Raised when queue-prioritization input is invalid."""

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
        raise UniversalQueuePrioritizationError(
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
        raise UniversalQueuePrioritizationError(
            f"{field_name} must not be blank.",
            code=(
                "blank_"
                + field_name
            ),
            value=value,
        )

    return normalized


def _normalize_created_at(
    value: Any,
) -> str:

    text = _normalize_required_text(
        value,
        field_name="created_at",
    )

    parse_text = (
        text[:-1] + "+00:00"
        if text.endswith("Z")
        else text
    )

    try:
        parsed = datetime.fromisoformat(
            parse_text
        )

    except ValueError as exc:
        raise UniversalQueuePrioritizationError(
            "created_at must be a valid ISO-8601 timestamp.",
            code="invalid_created_at",
            value=value,
        ) from exc

    if (
        parsed.tzinfo is None
        or parsed.utcoffset() is None
    ):
        raise UniversalQueuePrioritizationError(
            "created_at must be timezone-aware.",
            code="created_at_must_be_timezone_aware",
            value=value,
        )

    utc_value = parsed.astimezone(
        timezone.utc
    )

    canonical = utc_value.isoformat(
        timespec="microseconds"
    )

    if canonical.endswith("+00:00"):
        canonical = (
            canonical[:-6]
            + "Z"
        )

    return canonical


def _normalize_job_id(
    value: Any,
) -> str:

    return _normalize_required_text(
        value,
        field_name="job_id",
    )


def normalize_universal_queue_priority(
    value: Any,
):
    """
    Consume the already-frozen Universal Job Priority authority.

    Queue Prioritization does not define a second priority scale.
    """

    try:
        return normalize_universal_job_priority(
            value
        )

    except UniversalJobPriorityError as exc:
        raise UniversalQueuePrioritizationError(
            "Invalid canonical Universal Job priority.",
            code="invalid_queue_priority",
            value=value,
        ) from exc


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalQueuePriorityRank:
    """
    Immutable deterministic queue ranking representation.

    Ordering:
        priority ascending
        created_at ascending
        job_id ascending
    """

    priority: Any
    created_at: str
    job_id: str
    schema_version: str = (
        UNIVERSAL_QUEUE_PRIORITY_RANK_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        canonical_priority = (
            normalize_universal_queue_priority(
                self.priority
            )
        )

        object.__setattr__(
            self,
            "priority",
            canonical_priority,
        )

        object.__setattr__(
            self,
            "created_at",
            _normalize_created_at(
                self.created_at
            ),
        )

        object.__setattr__(
            self,
            "job_id",
            _normalize_job_id(
                self.job_id
            ),
        )

        if (
            self.schema_version
            != UNIVERSAL_QUEUE_PRIORITY_RANK_SCHEMA_VERSION
        ):
            raise UniversalQueuePrioritizationError(
                "Invalid priority-rank schema_version.",
                code="invalid_priority_rank_schema_version",
                value=self.schema_version,
            )

    @property
    def priority_order(
        self,
    ) -> int:

        return universal_job_priority_order(
            self.priority
        )

    @property
    def sort_key(
        self,
    ) -> tuple[int, str, str]:

        return (
            self.priority_order,
            self.created_at,
            self.job_id,
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "schema_version":
                self.schema_version,

            "priority":
                str(
                    self.priority
                ),

            "priority_order":
                self.priority_order,

            "created_at":
                self.created_at,

            "job_id":
                self.job_id,

            "sort_key": [
                self.priority_order,
                self.created_at,
                self.job_id,
            ],
        }


def create_universal_queue_priority_rank(
    *,
    priority: Any,
    created_at: str,
    job_id: str,
) -> UniversalQueuePriorityRank:

    return UniversalQueuePriorityRank(
        priority=priority,
        created_at=created_at,
        job_id=job_id,
    )


def universal_queue_priority_sort_key(
    *,
    priority: Any,
    created_at: str,
    job_id: str,
) -> tuple[int, str, str]:

    return (
        create_universal_queue_priority_rank(
            priority=priority,
            created_at=created_at,
            job_id=job_id,
        ).sort_key
    )


def order_universal_queue_priority_ranks(
    values: Iterable[
        UniversalQueuePriorityRank
    ],
) -> tuple[
    UniversalQueuePriorityRank,
    ...
]:
    """
    Return a deterministically ordered immutable tuple.

    This performs no queue mutation.
    """

    if isinstance(
        values,
        (
            str,
            bytes,
            bytearray,
        ),
    ):
        raise UniversalQueuePrioritizationError(
            "values must be an iterable of priority ranks.",
            code="invalid_priority_rank_collection",
            value=values,
        )

    try:
        materialized = tuple(
            values
        )

    except TypeError as exc:
        raise UniversalQueuePrioritizationError(
            "values must be iterable.",
            code="invalid_priority_rank_collection",
            value=values,
        ) from exc

    for value in materialized:

        if not isinstance(
            value,
            UniversalQueuePriorityRank,
        ):
            raise UniversalQueuePrioritizationError(
                (
                    "values must contain only "
                    "UniversalQueuePriorityRank members."
                ),
                code="invalid_priority_rank_member",
                value=value,
            )

    return tuple(
        sorted(
            materialized,
            key=lambda item: item.sort_key,
        )
    )


def explain_universal_queue_prioritization_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "3.1.3",

            "component":
                "Universal Queue Prioritization",

            "version":
                UNIVERSAL_QUEUE_PRIORITIZATION_VERSION,

            "schema_version":
                UNIVERSAL_QUEUE_PRIORITY_RANK_SCHEMA_VERSION,

            "scope":
                "LinkCraftor-wide",

            "priority_authority":
                "Universal Job Priority v2.1.6",

            "ordering_rule": (
                "priority ascending, then created_at "
                "ascending, then job_id ascending"
            ),

            "priority_rule": (
                "lower canonical Universal Job priority "
                "number ranks ahead of larger numbers"
            ),

            "scheduling_relationship": (
                "3.1.2 determines time eligibility before "
                "3.1.3 ranking; scheduled_at is not part "
                "of the priority sort key"
            ),

            "tie_break_rules": (
                "equal priority uses created_at FIFO",
                (
                    "equal priority and created_at uses "
                    "job_id deterministic ordering"
                ),
            ),

            "legacy_compatibility": (
                "legacy orchestration priority values such "
                "as 1/3/5/7/9 are not a second canonical "
                "Universal Queue priority scale"
            ),

            "prohibitions": (
                "does not redefine Universal Job Priority",
                "does not create jobs",
                "does not mutate jobs",
                "does not mutate priority",
                "does not mutate queues",
                "does not assign persisted queue position",
                "does not perform scheduling eligibility",
                "does not use scheduled_at in ranking",
                "does not enqueue jobs",
                "does not dequeue jobs",
                "does not claim jobs",
                "does not select workers",
                "does not route jobs",
                "does not balance queues",
                "does not partition queues",
                "does not implement starvation prevention",
                "does not implement priority aging",
                "does not implement queue fairness",
                "does not enforce SLA policy",
                "does not enforce subscription entitlement",
                "does not enforce workspace quotas",
                "does not enforce resource governance",
                "does not adjust priority for retries",
                "does not access orchestration",
                "does not access the job store",
                "does not perform filesystem I/O",
                "does not perform network I/O",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_QUEUE_PRIORITIZATION_VERSION",
    "UNIVERSAL_QUEUE_PRIORITY_RANK_SCHEMA_VERSION",
    "UniversalQueuePrioritizationError",
    "UniversalQueuePriorityRank",
    "normalize_universal_queue_priority",
    "create_universal_queue_priority_rank",
    "universal_queue_priority_sort_key",
    "order_universal_queue_priority_ranks",
    "explain_universal_queue_prioritization_v1",
]
