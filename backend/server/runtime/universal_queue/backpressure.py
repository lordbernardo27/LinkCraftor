from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from backend.server.runtime.universal_queue.creation import (
    UniversalQueueCreationError,
    normalize_universal_queue_id,
)

from backend.server.runtime.universal_queue.balancing import (
    UniversalQueueBalancingError,
    normalize_universal_queue_depth,
)


UNIVERSAL_QUEUE_BACKPRESSURE_VERSION = (
    "universal_queue_backpressure_v3.1.10"
)

UNIVERSAL_QUEUE_BACKPRESSURE_SNAPSHOT_SCHEMA_VERSION = (
    "universal_queue_backpressure_snapshot_schema_v1"
)

UNIVERSAL_QUEUE_BACKPRESSURE_DECISION_SCHEMA_VERSION = (
    "universal_queue_backpressure_decision_schema_v1"
)


class UniversalQueuePressureLevel(
    str,
    Enum,
):
    NORMAL = "normal"
    ELEVATED = "elevated"
    HIGH = "high"


class UniversalQueueBackpressureRecommendation(
    str,
    Enum,
):
    ALLOW = "allow"
    DEFER_PREFERRED = "defer_preferred"
    DEFER = "defer"


class UniversalQueueBackpressureError(
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


def normalize_universal_queue_backpressure_queue_id(
    value: Any,
) -> str:

    try:

        return normalize_universal_queue_id(
            value
        )

    except UniversalQueueCreationError as exc:

        raise UniversalQueueBackpressureError(
            "Invalid canonical Universal Queue queue_id.",
            code="invalid_backpressure_queue_id",
            value=value,
        ) from exc


def normalize_universal_queue_backpressure_depth(
    value: Any,
) -> int:

    try:

        return normalize_universal_queue_depth(
            value
        )

    except UniversalQueueBalancingError as exc:

        raise UniversalQueueBackpressureError(
            "queue_depth must be a non-negative integer.",
            code="invalid_backpressure_queue_depth",
            value=value,
        ) from exc


def _normalize_watermark(
    value: Any,
    *,
    field_name: str,
) -> int:

    if isinstance(
        value,
        bool,
    ) or not isinstance(
        value,
        int,
    ):

        raise UniversalQueueBackpressureError(
            f"{field_name} must be a non-negative integer.",
            code="invalid_" + field_name + "_type",
            value=value,
        )

    if value < 0:

        raise UniversalQueueBackpressureError(
            f"{field_name} must not be negative.",
            code="negative_" + field_name,
            value=value,
        )

    return value


def normalize_universal_queue_low_watermark(
    value: Any,
) -> int:

    return _normalize_watermark(
        value,
        field_name="low_watermark",
    )


def normalize_universal_queue_high_watermark(
    value: Any,
) -> int:

    return _normalize_watermark(
        value,
        field_name="high_watermark",
    )


def _validate_watermark_order(
    *,
    low_watermark: int,
    high_watermark: int,
) -> None:

    if low_watermark >= high_watermark:

        raise UniversalQueueBackpressureError(
            (
                "low_watermark must be strictly less "
                "than high_watermark."
            ),
            code="invalid_backpressure_watermark_order",
            value={
                "low_watermark":
                    low_watermark,

                "high_watermark":
                    high_watermark,
            },
        )


def normalize_universal_queue_pressure_level(
    value: Any,
) -> UniversalQueuePressureLevel:

    if isinstance(
        value,
        UniversalQueuePressureLevel,
    ):

        return value

    if not isinstance(
        value,
        str,
    ):

        raise UniversalQueueBackpressureError(
            "pressure_level must be a supported string.",
            code="invalid_pressure_level_type",
            value=value,
        )

    normalized = value.strip().lower()

    try:

        return UniversalQueuePressureLevel(
            normalized
        )

    except ValueError as exc:

        raise UniversalQueueBackpressureError(
            "Unsupported pressure_level.",
            code="unsupported_pressure_level",
            value=value,
        ) from exc


def normalize_universal_queue_backpressure_recommendation(
    value: Any,
) -> UniversalQueueBackpressureRecommendation:

    if isinstance(
        value,
        UniversalQueueBackpressureRecommendation,
    ):

        return value

    if not isinstance(
        value,
        str,
    ):

        raise UniversalQueueBackpressureError(
            "recommendation must be a supported string.",
            code="invalid_backpressure_recommendation_type",
            value=value,
        )

    normalized = value.strip().lower()

    try:

        return UniversalQueueBackpressureRecommendation(
            normalized
        )

    except ValueError as exc:

        raise UniversalQueueBackpressureError(
            "Unsupported backpressure recommendation.",
            code="unsupported_backpressure_recommendation",
            value=value,
        ) from exc


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalQueueBackpressureSnapshot:

    queue_id: str
    queue_depth: int
    low_watermark: int
    high_watermark: int
    schema_version: str = (
        UNIVERSAL_QUEUE_BACKPRESSURE_SNAPSHOT_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        set_ = object.__setattr__

        set_(
            self,
            "queue_id",
            normalize_universal_queue_backpressure_queue_id(
                self.queue_id
            ),
        )

        set_(
            self,
            "queue_depth",
            normalize_universal_queue_backpressure_depth(
                self.queue_depth
            ),
        )

        low = normalize_universal_queue_low_watermark(
            self.low_watermark
        )

        high = normalize_universal_queue_high_watermark(
            self.high_watermark
        )

        _validate_watermark_order(
            low_watermark=low,
            high_watermark=high,
        )

        set_(
            self,
            "low_watermark",
            low,
        )

        set_(
            self,
            "high_watermark",
            high,
        )

        if (
            self.schema_version
            != UNIVERSAL_QUEUE_BACKPRESSURE_SNAPSHOT_SCHEMA_VERSION
        ):

            raise UniversalQueueBackpressureError(
                "Invalid Backpressure snapshot schema_version.",
                code="invalid_backpressure_snapshot_schema_version",
                value=self.schema_version,
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

            "low_watermark":
                self.low_watermark,

            "high_watermark":
                self.high_watermark,
        }


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalQueueBackpressureDecision:

    queue_id: str
    queue_depth: int
    low_watermark: int
    high_watermark: int
    pressure_level: UniversalQueuePressureLevel | str
    recommendation: UniversalQueueBackpressureRecommendation | str
    enforcement_required: bool
    reason: str
    schema_version: str = (
        UNIVERSAL_QUEUE_BACKPRESSURE_DECISION_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        set_ = object.__setattr__

        queue_id = (
            normalize_universal_queue_backpressure_queue_id(
                self.queue_id
            )
        )

        queue_depth = (
            normalize_universal_queue_backpressure_depth(
                self.queue_depth
            )
        )

        low = normalize_universal_queue_low_watermark(
            self.low_watermark
        )

        high = normalize_universal_queue_high_watermark(
            self.high_watermark
        )

        _validate_watermark_order(
            low_watermark=low,
            high_watermark=high,
        )

        level = normalize_universal_queue_pressure_level(
            self.pressure_level
        )

        recommendation = (
            normalize_universal_queue_backpressure_recommendation(
                self.recommendation
            )
        )

        if not isinstance(
            self.enforcement_required,
            bool,
        ):

            raise UniversalQueueBackpressureError(
                "enforcement_required must be bool.",
                code="invalid_backpressure_enforcement_flag",
                value=self.enforcement_required,
            )

        if self.enforcement_required is not False:

            raise UniversalQueueBackpressureError(
                (
                    "Phase 3.1.10 classifies and recommends "
                    "but does not enforce backpressure."
                ),
                code="backpressure_enforcement_not_owned",
                value=self.enforcement_required,
            )

        if not isinstance(
            self.reason,
            str,
        ):

            raise UniversalQueueBackpressureError(
                "reason must be a string.",
                code="invalid_backpressure_reason_type",
                value=self.reason,
            )

        reason = self.reason.strip()

        if not reason:

            raise UniversalQueueBackpressureError(
                "reason must not be blank.",
                code="blank_backpressure_reason",
                value=self.reason,
            )

        expected_level: UniversalQueuePressureLevel
        expected_recommendation: UniversalQueueBackpressureRecommendation

        if queue_depth < low:

            expected_level = (
                UniversalQueuePressureLevel.NORMAL
            )

            expected_recommendation = (
                UniversalQueueBackpressureRecommendation.ALLOW
            )

        elif queue_depth < high:

            expected_level = (
                UniversalQueuePressureLevel.ELEVATED
            )

            expected_recommendation = (
                UniversalQueueBackpressureRecommendation.DEFER_PREFERRED
            )

        else:

            expected_level = (
                UniversalQueuePressureLevel.HIGH
            )

            expected_recommendation = (
                UniversalQueueBackpressureRecommendation.DEFER
            )

        if level is not expected_level:

            raise UniversalQueueBackpressureError(
                "pressure_level is inconsistent with queue depth.",
                code="inconsistent_backpressure_pressure_level",
                value=level.value,
            )

        if recommendation is not expected_recommendation:

            raise UniversalQueueBackpressureError(
                (
                    "recommendation is inconsistent with "
                    "the canonical pressure level."
                ),
                code="inconsistent_backpressure_recommendation",
                value=recommendation.value,
            )

        set_(
            self,
            "queue_id",
            queue_id,
        )

        set_(
            self,
            "queue_depth",
            queue_depth,
        )

        set_(
            self,
            "low_watermark",
            low,
        )

        set_(
            self,
            "high_watermark",
            high,
        )

        set_(
            self,
            "pressure_level",
            level,
        )

        set_(
            self,
            "recommendation",
            recommendation,
        )

        set_(
            self,
            "reason",
            reason,
        )

        if (
            self.schema_version
            != UNIVERSAL_QUEUE_BACKPRESSURE_DECISION_SCHEMA_VERSION
        ):

            raise UniversalQueueBackpressureError(
                "Invalid Backpressure decision schema_version.",
                code="invalid_backpressure_decision_schema_version",
                value=self.schema_version,
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

            "low_watermark":
                self.low_watermark,

            "high_watermark":
                self.high_watermark,

            "pressure_level":
                self.pressure_level.value,

            "recommendation":
                self.recommendation.value,

            "enforcement_required":
                self.enforcement_required,

            "reason":
                self.reason,
        }


def create_universal_queue_backpressure_snapshot(
    *,
    queue_id: str,
    queue_depth: int,
    low_watermark: int,
    high_watermark: int,
) -> UniversalQueueBackpressureSnapshot:

    return UniversalQueueBackpressureSnapshot(
        queue_id=queue_id,
        queue_depth=queue_depth,
        low_watermark=low_watermark,
        high_watermark=high_watermark,
    )


def evaluate_universal_queue_backpressure(
    *,
    snapshot: UniversalQueueBackpressureSnapshot,
) -> UniversalQueueBackpressureDecision:

    if not isinstance(
        snapshot,
        UniversalQueueBackpressureSnapshot,
    ):

        raise UniversalQueueBackpressureError(
            (
                "snapshot must be a "
                "UniversalQueueBackpressureSnapshot instance."
            ),
            code="invalid_backpressure_snapshot",
            value=snapshot,
        )

    if snapshot.queue_depth < snapshot.low_watermark:

        level = UniversalQueuePressureLevel.NORMAL

        recommendation = (
            UniversalQueueBackpressureRecommendation.ALLOW
        )

        reason = "queue_depth_below_low_watermark"

    elif snapshot.queue_depth < snapshot.high_watermark:

        level = UniversalQueuePressureLevel.ELEVATED

        recommendation = (
            UniversalQueueBackpressureRecommendation.DEFER_PREFERRED
        )

        reason = "queue_depth_at_or_above_low_watermark"

    else:

        level = UniversalQueuePressureLevel.HIGH

        recommendation = (
            UniversalQueueBackpressureRecommendation.DEFER
        )

        reason = "queue_depth_at_or_above_high_watermark"

    return UniversalQueueBackpressureDecision(
        queue_id=snapshot.queue_id,
        queue_depth=snapshot.queue_depth,
        low_watermark=snapshot.low_watermark,
        high_watermark=snapshot.high_watermark,
        pressure_level=level,
        recommendation=recommendation,
        enforcement_required=False,
        reason=reason,
    )


def explain_universal_queue_backpressure_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "3.1.10",

            "component":
                "Universal Queue Backpressure",

            "version":
                UNIVERSAL_QUEUE_BACKPRESSURE_VERSION,

            "snapshot_schema":
                UNIVERSAL_QUEUE_BACKPRESSURE_SNAPSHOT_SCHEMA_VERSION,

            "decision_schema":
                UNIVERSAL_QUEUE_BACKPRESSURE_DECISION_SCHEMA_VERSION,

            "scope":
                "LinkCraftor-wide",

            "canonical_pressure_signal":
                "queue_depth",

            "snapshot_rule": (
                "queue depth and pressure watermarks are "
                "caller-supplied; 3.1.10 does not read "
                "live queue state"
            ),

            "watermark_rule": (
                "0 <= low_watermark < high_watermark; "
                "watermarks are explicit policy inputs "
                "and are not hard-coded by 3.1.10"
            ),

            "classification_rule": (
                "queue_depth below low watermark is NORMAL; "
                "from low watermark to below high watermark "
                "is ELEVATED; at or above high watermark is HIGH"
            ),

            "recommendation_rule": (
                "NORMAL recommends ALLOW; ELEVATED recommends "
                "DEFER_PREFERRED; HIGH recommends DEFER"
            ),

            "enforcement_rule": (
                "recommendations are logical guidance only; "
                "3.1.10 does not pause, reject, throttle, sleep "
                "or otherwise enforce producer behavior"
            ),

            "capacity_boundary": (
                "hard queue capacity and admission enforcement "
                "belong to 3.1.11 Queue Capacity Limits"
            ),

            "fairness_boundary": (
                "fairness and starvation policy belong to "
                "3.1.12 Queue Fairness"
            ),

            "rate_limit_boundary": (
                "rate limiting belongs to "
                "3.1.13 Queue Rate Limiting"
            ),

            "worker_boundary": (
                "worker scaling, worker assignment and worker "
                "capacity remain Worker Infrastructure concerns"
            ),

            "prohibitions": (
                "does not create Universal Queues",
                "does not create Universal Jobs",
                "does not mutate Universal Jobs",
                "does not mutate queues",
                "does not enqueue jobs",
                "does not dequeue jobs",
                "does not claim jobs",
                "does not requeue jobs",
                "does not read live queue state",
                "does not access orchestration",
                "does not access the Job Store",
                "does not access Runtime State Store",
                "does not enforce hard queue capacity",
                "does not reject job admission",
                "does not return HTTP 429",
                "does not calculate Retry-After",
                "does not implement rate limiting",
                "does not pause producers",
                "does not resume producers",
                "does not sleep or delay execution",
                "does not throttle producers",
                "does not shed load",
                "does not scale workers",
                "does not select workers",
                "does not inspect worker capability",
                "does not implement queue fairness",
                "does not implement priority aging",
                "does not deduplicate queued jobs",
                "does not create physical queues",
                "does not perform filesystem I/O",
                "does not perform network I/O",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_QUEUE_BACKPRESSURE_VERSION",
    "UNIVERSAL_QUEUE_BACKPRESSURE_SNAPSHOT_SCHEMA_VERSION",
    "UNIVERSAL_QUEUE_BACKPRESSURE_DECISION_SCHEMA_VERSION",
    "UniversalQueuePressureLevel",
    "UniversalQueueBackpressureRecommendation",
    "UniversalQueueBackpressureError",
    "UniversalQueueBackpressureSnapshot",
    "UniversalQueueBackpressureDecision",
    "normalize_universal_queue_backpressure_queue_id",
    "normalize_universal_queue_backpressure_depth",
    "normalize_universal_queue_low_watermark",
    "normalize_universal_queue_high_watermark",
    "normalize_universal_queue_pressure_level",
    "normalize_universal_queue_backpressure_recommendation",
    "create_universal_queue_backpressure_snapshot",
    "evaluate_universal_queue_backpressure",
    "explain_universal_queue_backpressure_v1",
]
