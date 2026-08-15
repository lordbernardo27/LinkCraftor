from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping


UNIVERSAL_QUEUE_SCHEDULING_VERSION = (
    "universal_queue_scheduling_v3.1.2"
)

UNIVERSAL_QUEUE_SCHEDULE_SCHEMA_VERSION = (
    "universal_queue_schedule_schema_v1"
)

UNIVERSAL_QUEUE_READINESS_SCHEMA_VERSION = (
    "universal_queue_readiness_schema_v1"
)


class UniversalQueueSchedulingError(
    ValueError
):
    """Raised when queue scheduling input is invalid."""

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


def _parse_aware_timestamp(
    value: Any,
    *,
    field_name: str,
) -> datetime:

    if not isinstance(
        value,
        str,
    ):
        raise UniversalQueueSchedulingError(
            f"{field_name} must be a string.",
            code=(
                "invalid_"
                + field_name
                + "_type"
            ),
            value=value,
        )

    text = (
        value.strip()
    )

    if not text:
        raise UniversalQueueSchedulingError(
            f"{field_name} must not be blank.",
            code=(
                "blank_"
                + field_name
            ),
            value=value,
        )

    parse_text = (
        text[:-1]
        + "+00:00"
        if text.endswith(
            "Z"
        )
        else text
    )

    try:
        parsed = (
            datetime.fromisoformat(
                parse_text
            )
        )

    except ValueError as exc:
        raise UniversalQueueSchedulingError(
            (
                f"{field_name} must be a valid "
                "ISO-8601 timestamp."
            ),
            code=(
                "invalid_"
                + field_name
            ),
            value=value,
        ) from exc

    if (
        parsed.tzinfo
        is None
        or parsed.utcoffset()
        is None
    ):
        raise UniversalQueueSchedulingError(
            (
                f"{field_name} must include "
                "an explicit UTC offset."
            ),
            code=(
                field_name
                + "_must_be_timezone_aware"
            ),
            value=value,
        )

    return parsed


def _canonical_utc_timestamp(
    value: datetime,
) -> str:

    utc_value = (
        value.astimezone(
            timezone.utc
        )
    )

    text = (
        utc_value.isoformat(
            timespec="microseconds"
        )
    )

    if text.endswith(
        "+00:00"
    ):
        text = (
            text[:-6]
            + "Z"
        )

    return text


def normalize_universal_queue_scheduled_at(
    value: Any,
) -> str | None:
    """
    Normalize one optional scheduling timestamp.

    None means there is no deferred execution boundary and the
    item is immediately time-eligible.
    """

    if value is None:
        return None

    parsed = (
        _parse_aware_timestamp(
            value,
            field_name="scheduled_at",
        )
    )

    return _canonical_utc_timestamp(
        parsed
    )


def normalize_universal_queue_evaluation_time(
    value: Any,
) -> str:

    parsed = (
        _parse_aware_timestamp(
            value,
            field_name="evaluation_time",
        )
    )

    return _canonical_utc_timestamp(
        parsed
    )


def _canonical_to_datetime(
    value: str,
) -> datetime:

    return datetime.fromisoformat(
        value[:-1]
        + "+00:00"
        if value.endswith(
            "Z"
        )
        else value
    )


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalQueueSchedule:
    """
    Immutable scheduling representation.

    scheduled_at=None means immediately time-eligible.
    """

    scheduled_at: str | None
    schema_version: str = (
        UNIVERSAL_QUEUE_SCHEDULE_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        object.__setattr__(
            self,
            "scheduled_at",
            normalize_universal_queue_scheduled_at(
                self.scheduled_at
            ),
        )

        if (
            self.schema_version
            != UNIVERSAL_QUEUE_SCHEDULE_SCHEMA_VERSION
        ):
            raise UniversalQueueSchedulingError(
                "Invalid schedule schema_version.",
                code="invalid_schedule_schema_version",
                value=self.schema_version,
            )

    @property
    def is_immediate(
        self,
    ) -> bool:

        return (
            self.scheduled_at
            is None
        )

    @property
    def is_deferred(
        self,
    ) -> bool:

        return (
            self.scheduled_at
            is not None
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "schema_version":
                self.schema_version,

            "scheduled_at":
                self.scheduled_at,

            "is_immediate":
                self.is_immediate,

            "is_deferred":
                self.is_deferred,
        }


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalQueueReadiness:
    """
    Pure time-readiness decision.

    This object does not mutate Universal Job status.
    """

    scheduled_at: str | None
    evaluation_time: str
    eligible: bool
    immediate: bool
    seconds_until_eligible: float
    reason: str
    schema_version: str = (
        UNIVERSAL_QUEUE_READINESS_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        object.__setattr__(
            self,
            "scheduled_at",
            normalize_universal_queue_scheduled_at(
                self.scheduled_at
            ),
        )

        object.__setattr__(
            self,
            "evaluation_time",
            normalize_universal_queue_evaluation_time(
                self.evaluation_time
            ),
        )

        if not isinstance(
            self.eligible,
            bool,
        ):
            raise UniversalQueueSchedulingError(
                "eligible must be bool.",
                code="invalid_eligible_type",
                value=self.eligible,
            )

        if not isinstance(
            self.immediate,
            bool,
        ):
            raise UniversalQueueSchedulingError(
                "immediate must be bool.",
                code="invalid_immediate_type",
                value=self.immediate,
            )

        seconds = (
            self.seconds_until_eligible
        )

        if (
            isinstance(
                seconds,
                bool,
            )
            or not isinstance(
                seconds,
                (
                    int,
                    float,
                ),
            )
        ):
            raise UniversalQueueSchedulingError(
                (
                    "seconds_until_eligible "
                    "must be numeric."
                ),
                code=(
                    "invalid_seconds_until_eligible"
                ),
                value=seconds,
            )

        normalized_seconds = (
            max(
                0.0,
                float(
                    seconds
                ),
            )
        )

        object.__setattr__(
            self,
            "seconds_until_eligible",
            normalized_seconds,
        )

        if not isinstance(
            self.reason,
            str,
        ) or not self.reason.strip():
            raise UniversalQueueSchedulingError(
                "reason must be a nonblank string.",
                code="invalid_readiness_reason",
                value=self.reason,
            )

        object.__setattr__(
            self,
            "reason",
            self.reason.strip(),
        )

        if (
            self.schema_version
            != UNIVERSAL_QUEUE_READINESS_SCHEMA_VERSION
        ):
            raise UniversalQueueSchedulingError(
                "Invalid readiness schema_version.",
                code="invalid_readiness_schema_version",
                value=self.schema_version,
            )

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "schema_version":
                self.schema_version,

            "scheduled_at":
                self.scheduled_at,

            "evaluation_time":
                self.evaluation_time,

            "eligible":
                self.eligible,

            "immediate":
                self.immediate,

            "seconds_until_eligible":
                self.seconds_until_eligible,

            "reason":
                self.reason,
        }


def create_universal_queue_schedule(
    *,
    scheduled_at: str | None = None,
) -> UniversalQueueSchedule:

    return UniversalQueueSchedule(
        scheduled_at=scheduled_at
    )


def evaluate_universal_queue_readiness(
    *,
    scheduled_at: str | None,
    evaluation_time: str,
) -> UniversalQueueReadiness:
    """
    Evaluate time eligibility only.

    No sleeping, persistence, queue mutation or status transition
    is performed.
    """

    canonical_scheduled = (
        normalize_universal_queue_scheduled_at(
            scheduled_at
        )
    )

    canonical_evaluation = (
        normalize_universal_queue_evaluation_time(
            evaluation_time
        )
    )

    if canonical_scheduled is None:

        return UniversalQueueReadiness(
            scheduled_at=None,
            evaluation_time=canonical_evaluation,
            eligible=True,
            immediate=True,
            seconds_until_eligible=0.0,
            reason="immediate",
        )

    scheduled_dt = (
        _canonical_to_datetime(
            canonical_scheduled
        )
    )

    evaluation_dt = (
        _canonical_to_datetime(
            canonical_evaluation
        )
    )

    delta = (
        scheduled_dt
        - evaluation_dt
    ).total_seconds()

    if delta <= 0:

        return UniversalQueueReadiness(
            scheduled_at=canonical_scheduled,
            evaluation_time=canonical_evaluation,
            eligible=True,
            immediate=False,
            seconds_until_eligible=0.0,
            reason="scheduled_time_reached",
        )

    return UniversalQueueReadiness(
        scheduled_at=canonical_scheduled,
        evaluation_time=canonical_evaluation,
        eligible=False,
        immediate=False,
        seconds_until_eligible=delta,
        reason="scheduled_for_future",
    )


def is_universal_queue_time_eligible(
    *,
    scheduled_at: str | None,
    evaluation_time: str,
) -> bool:

    return (
        evaluate_universal_queue_readiness(
            scheduled_at=scheduled_at,
            evaluation_time=evaluation_time,
        ).eligible
    )


def explain_universal_queue_scheduling_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "3.1.2",

            "component":
                "Universal Queue Scheduling",

            "version":
                UNIVERSAL_QUEUE_SCHEDULING_VERSION,

            "schedule_schema":
                UNIVERSAL_QUEUE_SCHEDULE_SCHEMA_VERSION,

            "readiness_schema":
                UNIVERSAL_QUEUE_READINESS_SCHEMA_VERSION,

            "scope":
                "LinkCraftor-wide",

            "canonical_field":
                "scheduled_at",

            "rules": (
                (
                    "scheduled_at=None means immediately "
                    "time-eligible"
                ),
                (
                    "scheduled_at <= evaluation_time "
                    "means time-eligible"
                ),
                (
                    "scheduled_at > evaluation_time "
                    "means deferred"
                ),
                (
                    "timestamps must be timezone-aware"
                ),
                (
                    "timestamps normalize to UTC"
                ),
                (
                    "eligibility evaluation is deterministic "
                    "for explicit inputs"
                ),
            ),

            "prohibitions": (
                "does not create Universal Jobs",
                "does not mutate Universal Jobs",
                "does not mutate scheduled_at on a job",
                "does not mutate job status",
                "does not define lifecycle transitions",
                "does not transition SCHEDULED to QUEUED",
                "does not enqueue jobs",
                "does not dequeue jobs",
                "does not claim jobs",
                "does not prioritize jobs",
                "does not route jobs",
                "does not balance queues",
                "does not partition queues",
                "does not lease jobs",
                "does not start workers",
                "does not sleep or poll",
                "does not schedule retries",
                "does not calculate retry backoff",
                "does not decide retryability",
                "does not create dead-letter queues",
                "does not implement recurrence or cron",
                "does not access orchestration",
                "does not access the job store",
                "does not persist schedule state",
                "does not perform filesystem I/O",
                "does not perform network I/O",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_QUEUE_SCHEDULING_VERSION",
    "UNIVERSAL_QUEUE_SCHEDULE_SCHEMA_VERSION",
    "UNIVERSAL_QUEUE_READINESS_SCHEMA_VERSION",
    "UniversalQueueSchedulingError",
    "UniversalQueueSchedule",
    "UniversalQueueReadiness",
    "normalize_universal_queue_scheduled_at",
    "normalize_universal_queue_evaluation_time",
    "create_universal_queue_schedule",
    "evaluate_universal_queue_readiness",
    "is_universal_queue_time_eligible",
    "explain_universal_queue_scheduling_v1",
]
