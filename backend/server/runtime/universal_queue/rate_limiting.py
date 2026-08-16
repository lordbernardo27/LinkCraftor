from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from backend.server.runtime.universal_queue.creation import (
    UniversalQueueCreationError,
    normalize_universal_queue_id,
)


UNIVERSAL_QUEUE_RATE_LIMITING_VERSION = (
    "universal_queue_rate_limiting_v3.1.13"
)

UNIVERSAL_QUEUE_RATE_LIMITING_ALGORITHM = (
    "fixed_window_v1"
)

UNIVERSAL_QUEUE_RATE_LIMIT_SNAPSHOT_SCHEMA_VERSION = (
    "universal_queue_rate_limit_snapshot_schema_v1"
)

UNIVERSAL_QUEUE_RATE_LIMIT_DECISION_SCHEMA_VERSION = (
    "universal_queue_rate_limit_decision_schema_v1"
)


class UniversalQueueRateLimitAdmission(
    str,
    Enum,
):

    ALLOW = "allow"
    DENY = "deny"


class UniversalQueueRateLimitError(
    ValueError
):

    def __init__(
        self,
        message: str,
        *,
        code: str,
        value: Any = None,
    ) -> None:

        super().__init__(message)

        self.code = str(code)
        self.value = value


def _normalize_nonblank_string(
    value: Any,
    *,
    field_name: str,
) -> str:

    if not isinstance(value, str):

        raise UniversalQueueRateLimitError(
            f"{field_name} must be a string.",
            code="invalid_" + field_name + "_type",
            value=value,
        )

    normalized = value.strip()

    if not normalized:

        raise UniversalQueueRateLimitError(
            f"{field_name} must not be blank.",
            code="blank_" + field_name,
            value=value,
        )

    return normalized


def _normalize_nonnegative_integer(
    value: Any,
    *,
    field_name: str,
) -> int:

    if (
        isinstance(value, bool)
        or not isinstance(value, int)
    ):

        raise UniversalQueueRateLimitError(
            f"{field_name} must be a non-negative integer.",
            code="invalid_" + field_name + "_type",
            value=value,
        )

    if value < 0:

        raise UniversalQueueRateLimitError(
            f"{field_name} must not be negative.",
            code="negative_" + field_name,
            value=value,
        )

    return value


def normalize_universal_queue_rate_limit_queue_id(
    value: Any,
) -> str:

    try:

        return normalize_universal_queue_id(value)

    except UniversalQueueCreationError as exc:

        raise UniversalQueueRateLimitError(
            "Invalid canonical Universal Queue queue_id.",
            code="invalid_rate_limit_queue_id",
            value=value,
        ) from exc


def normalize_universal_queue_rate_limit_workspace_id(
    value: Any,
) -> str:

    return _normalize_nonblank_string(
        value,
        field_name="workspace_id",
    )


def normalize_universal_queue_rate_limit_window_id(
    value: Any,
) -> str:

    return _normalize_nonblank_string(
        value,
        field_name="window_id",
    )


def normalize_universal_queue_rate_limit_window_seconds(
    value: Any,
) -> int:

    normalized = _normalize_nonnegative_integer(
        value,
        field_name="window_seconds",
    )

    if normalized < 1:

        raise UniversalQueueRateLimitError(
            "window_seconds must be >= 1.",
            code="invalid_window_seconds",
            value=value,
        )

    return normalized


def normalize_universal_queue_rate_limit_allowed_count(
    value: Any,
) -> int:

    return _normalize_nonnegative_integer(
        value,
        field_name="allowed_count_per_window",
    )


def normalize_universal_queue_rate_limit_usage_count(
    value: Any,
) -> int:

    return _normalize_nonnegative_integer(
        value,
        field_name="current_usage_count",
    )


def normalize_universal_queue_rate_limit_requested_count(
    value: Any,
) -> int:

    normalized = _normalize_nonnegative_integer(
        value,
        field_name="requested_admission_count",
    )

    if normalized < 1:

        raise UniversalQueueRateLimitError(
            "requested_admission_count must be >= 1.",
            code="invalid_requested_admission_count",
            value=value,
        )

    return normalized


def normalize_universal_queue_rate_limit_admission(
    value: Any,
) -> UniversalQueueRateLimitAdmission:

    if isinstance(
        value,
        UniversalQueueRateLimitAdmission,
    ):

        return value

    if not isinstance(value, str):

        raise UniversalQueueRateLimitError(
            "admission must be a supported string.",
            code="invalid_rate_limit_admission_type",
            value=value,
        )

    normalized = value.strip().lower()

    try:

        return UniversalQueueRateLimitAdmission(
            normalized
        )

    except ValueError as exc:

        raise UniversalQueueRateLimitError(
            "Unsupported rate-limit admission.",
            code="unsupported_rate_limit_admission",
            value=value,
        ) from exc


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalQueueRateLimitSnapshot:

    queue_id: str
    workspace_id: str
    window_id: str
    window_seconds: int
    allowed_count_per_window: int
    current_usage_count: int
    requested_admission_count: int
    schema_version: str = (
        UNIVERSAL_QUEUE_RATE_LIMIT_SNAPSHOT_SCHEMA_VERSION
    )

    def __post_init__(self) -> None:

        set_ = object.__setattr__

        set_(
            self,
            "queue_id",
            normalize_universal_queue_rate_limit_queue_id(
                self.queue_id
            ),
        )

        set_(
            self,
            "workspace_id",
            normalize_universal_queue_rate_limit_workspace_id(
                self.workspace_id
            ),
        )

        set_(
            self,
            "window_id",
            normalize_universal_queue_rate_limit_window_id(
                self.window_id
            ),
        )

        set_(
            self,
            "window_seconds",
            normalize_universal_queue_rate_limit_window_seconds(
                self.window_seconds
            ),
        )

        set_(
            self,
            "allowed_count_per_window",
            normalize_universal_queue_rate_limit_allowed_count(
                self.allowed_count_per_window
            ),
        )

        set_(
            self,
            "current_usage_count",
            normalize_universal_queue_rate_limit_usage_count(
                self.current_usage_count
            ),
        )

        set_(
            self,
            "requested_admission_count",
            normalize_universal_queue_rate_limit_requested_count(
                self.requested_admission_count
            ),
        )

        if (
            self.schema_version
            != UNIVERSAL_QUEUE_RATE_LIMIT_SNAPSHOT_SCHEMA_VERSION
        ):

            raise UniversalQueueRateLimitError(
                "Invalid rate-limit snapshot schema_version.",
                code="invalid_rate_limit_snapshot_schema_version",
                value=self.schema_version,
            )

    @property
    def identity(
        self,
    ) -> tuple[str, str]:

        return (
            self.queue_id,
            self.workspace_id,
        )

    @property
    def projected_usage_count(
        self,
    ) -> int:

        return (
            self.current_usage_count
            + self.requested_admission_count
        )

    @property
    def remaining_before(
        self,
    ) -> int:

        return max(
            0,
            self.allowed_count_per_window
            - self.current_usage_count,
        )

    def to_dict(self) -> dict[str, Any]:

        return {
            "schema_version":
                self.schema_version,

            "queue_id":
                self.queue_id,

            "workspace_id":
                self.workspace_id,

            "window_id":
                self.window_id,

            "window_seconds":
                self.window_seconds,

            "allowed_count_per_window":
                self.allowed_count_per_window,

            "current_usage_count":
                self.current_usage_count,

            "requested_admission_count":
                self.requested_admission_count,

            "projected_usage_count":
                self.projected_usage_count,

            "remaining_before":
                self.remaining_before,
        }


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalQueueRateLimitDecision:

    queue_id: str
    workspace_id: str
    window_id: str
    window_seconds: int
    allowed_count_per_window: int
    current_usage_count: int
    requested_admission_count: int
    projected_usage_count: int
    admission: UniversalQueueRateLimitAdmission | str
    limit_exceeded: bool
    counter_mutation_required: bool
    delay_required: bool
    reason: str
    schema_version: str = (
        UNIVERSAL_QUEUE_RATE_LIMIT_DECISION_SCHEMA_VERSION
    )

    def __post_init__(self) -> None:

        set_ = object.__setattr__

        queue_id = (
            normalize_universal_queue_rate_limit_queue_id(
                self.queue_id
            )
        )

        workspace_id = (
            normalize_universal_queue_rate_limit_workspace_id(
                self.workspace_id
            )
        )

        window_id = (
            normalize_universal_queue_rate_limit_window_id(
                self.window_id
            )
        )

        window_seconds = (
            normalize_universal_queue_rate_limit_window_seconds(
                self.window_seconds
            )
        )

        allowed = (
            normalize_universal_queue_rate_limit_allowed_count(
                self.allowed_count_per_window
            )
        )

        current = (
            normalize_universal_queue_rate_limit_usage_count(
                self.current_usage_count
            )
        )

        requested = (
            normalize_universal_queue_rate_limit_requested_count(
                self.requested_admission_count
            )
        )

        projected = (
            _normalize_nonnegative_integer(
                self.projected_usage_count,
                field_name="projected_usage_count",
            )
        )

        admission = (
            normalize_universal_queue_rate_limit_admission(
                self.admission
            )
        )

        if not isinstance(
            self.limit_exceeded,
            bool,
        ):

            raise UniversalQueueRateLimitError(
                "limit_exceeded must be bool.",
                code="invalid_rate_limit_exceeded_flag",
                value=self.limit_exceeded,
            )

        if not isinstance(
            self.counter_mutation_required,
            bool,
        ):

            raise UniversalQueueRateLimitError(
                "counter_mutation_required must be bool.",
                code="invalid_rate_limit_counter_mutation_flag",
                value=self.counter_mutation_required,
            )

        if (
            self.counter_mutation_required
            is not False
        ):

            raise UniversalQueueRateLimitError(
                (
                    "3.1.13 decides rate admission but "
                    "does not mutate usage counters."
                ),
                code="rate_limit_counter_mutation_not_owned",
                value=self.counter_mutation_required,
            )

        if not isinstance(
            self.delay_required,
            bool,
        ):

            raise UniversalQueueRateLimitError(
                "delay_required must be bool.",
                code="invalid_rate_limit_delay_flag",
                value=self.delay_required,
            )

        if self.delay_required is not False:

            raise UniversalQueueRateLimitError(
                (
                    "3.1.13 does not sleep, wait, throttle "
                    "or delay execution."
                ),
                code="rate_limit_delay_not_owned",
                value=self.delay_required,
            )

        if not isinstance(
            self.reason,
            str,
        ):

            raise UniversalQueueRateLimitError(
                "reason must be a string.",
                code="invalid_rate_limit_reason_type",
                value=self.reason,
            )

        reason = self.reason.strip()

        if not reason:

            raise UniversalQueueRateLimitError(
                "reason must not be blank.",
                code="blank_rate_limit_reason",
                value=self.reason,
            )

        expected_projected = (
            current
            + requested
        )

        if projected != expected_projected:

            raise UniversalQueueRateLimitError(
                "projected_usage_count is inconsistent.",
                code="inconsistent_projected_usage_count",
                value=projected,
            )

        expected_exceeded = (
            projected > allowed
        )

        expected_admission = (
            UniversalQueueRateLimitAdmission.DENY
            if expected_exceeded
            else UniversalQueueRateLimitAdmission.ALLOW
        )

        if (
            self.limit_exceeded
            is not expected_exceeded
        ):

            raise UniversalQueueRateLimitError(
                "limit_exceeded is inconsistent.",
                code="inconsistent_rate_limit_exceeded",
                value=self.limit_exceeded,
            )

        if admission is not expected_admission:

            raise UniversalQueueRateLimitError(
                (
                    "admission is inconsistent with "
                    "the canonical fixed-window rule."
                ),
                code="inconsistent_rate_limit_admission",
                value=admission.value,
            )

        set_(self, "queue_id", queue_id)
        set_(self, "workspace_id", workspace_id)
        set_(self, "window_id", window_id)
        set_(self, "window_seconds", window_seconds)

        set_(
            self,
            "allowed_count_per_window",
            allowed,
        )

        set_(
            self,
            "current_usage_count",
            current,
        )

        set_(
            self,
            "requested_admission_count",
            requested,
        )

        set_(
            self,
            "projected_usage_count",
            projected,
        )

        set_(self, "admission", admission)
        set_(self, "reason", reason)

        if (
            self.schema_version
            != UNIVERSAL_QUEUE_RATE_LIMIT_DECISION_SCHEMA_VERSION
        ):

            raise UniversalQueueRateLimitError(
                "Invalid rate-limit decision schema_version.",
                code="invalid_rate_limit_decision_schema_version",
                value=self.schema_version,
            )

    @property
    def identity(
        self,
    ) -> tuple[str, str]:

        return (
            self.queue_id,
            self.workspace_id,
        )

    @property
    def remaining_before(
        self,
    ) -> int:

        return max(
            0,
            self.allowed_count_per_window
            - self.current_usage_count,
        )

    @property
    def remaining_after(
        self,
    ) -> int:

        if self.limit_exceeded:

            return self.remaining_before

        return (
            self.allowed_count_per_window
            - self.projected_usage_count
        )

    def to_dict(self) -> dict[str, Any]:

        return {
            "schema_version":
                self.schema_version,

            "queue_id":
                self.queue_id,

            "workspace_id":
                self.workspace_id,

            "window_id":
                self.window_id,

            "window_seconds":
                self.window_seconds,

            "allowed_count_per_window":
                self.allowed_count_per_window,

            "current_usage_count":
                self.current_usage_count,

            "requested_admission_count":
                self.requested_admission_count,

            "projected_usage_count":
                self.projected_usage_count,

            "remaining_before":
                self.remaining_before,

            "remaining_after":
                self.remaining_after,

            "admission":
                self.admission.value,

            "limit_exceeded":
                self.limit_exceeded,

            "counter_mutation_required":
                self.counter_mutation_required,

            "delay_required":
                self.delay_required,

            "reason":
                self.reason,
        }


def create_universal_queue_rate_limit_snapshot(
    *,
    queue_id: str,
    workspace_id: str,
    window_id: str,
    window_seconds: int,
    allowed_count_per_window: int,
    current_usage_count: int,
    requested_admission_count: int,
) -> UniversalQueueRateLimitSnapshot:

    return UniversalQueueRateLimitSnapshot(
        queue_id=queue_id,
        workspace_id=workspace_id,
        window_id=window_id,
        window_seconds=window_seconds,
        allowed_count_per_window=allowed_count_per_window,
        current_usage_count=current_usage_count,
        requested_admission_count=requested_admission_count,
    )


def evaluate_universal_queue_rate_limit(
    *,
    snapshot: UniversalQueueRateLimitSnapshot,
) -> UniversalQueueRateLimitDecision:

    if not isinstance(
        snapshot,
        UniversalQueueRateLimitSnapshot,
    ):

        raise UniversalQueueRateLimitError(
            (
                "snapshot must be a "
                "UniversalQueueRateLimitSnapshot."
            ),
            code="invalid_rate_limit_snapshot",
            value=snapshot,
        )

    projected = (
        snapshot.projected_usage_count
    )

    exceeded = (
        projected
        > snapshot.allowed_count_per_window
    )

    if exceeded:

        admission = (
            UniversalQueueRateLimitAdmission.DENY
        )

        reason = (
            "projected_usage_count_exceeds_rate_limit"
        )

    else:

        admission = (
            UniversalQueueRateLimitAdmission.ALLOW
        )

        reason = (
            "projected_usage_count_within_rate_limit"
        )

    return UniversalQueueRateLimitDecision(
        queue_id=snapshot.queue_id,
        workspace_id=snapshot.workspace_id,
        window_id=snapshot.window_id,
        window_seconds=snapshot.window_seconds,
        allowed_count_per_window=snapshot.allowed_count_per_window,
        current_usage_count=snapshot.current_usage_count,
        requested_admission_count=snapshot.requested_admission_count,
        projected_usage_count=projected,
        admission=admission,
        limit_exceeded=exceeded,
        counter_mutation_required=False,
        delay_required=False,
        reason=reason,
    )


def explain_universal_queue_rate_limiting_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "3.1.13",

            "component":
                "Universal Queue Rate Limiting",

            "version":
                UNIVERSAL_QUEUE_RATE_LIMITING_VERSION,

            "algorithm":
                UNIVERSAL_QUEUE_RATE_LIMITING_ALGORITHM,

            "snapshot_schema":
                UNIVERSAL_QUEUE_RATE_LIMIT_SNAPSHOT_SCHEMA_VERSION,

            "decision_schema":
                UNIVERSAL_QUEUE_RATE_LIMIT_DECISION_SCHEMA_VERSION,

            "scope":
                "LinkCraftor-wide",

            "canonical_rate_limit_identity":
                "[queue_id, workspace_id]",

            "algorithm_rule": (
                "v1 uses a stateless fixed window; it does not "
                "maintain token-bucket, leaky-bucket, sliding-window "
                "or burst-credit state"
            ),

            "window_rule": (
                "window_id and window_seconds are explicit "
                "caller-supplied window evidence; 3.1.13 does not "
                "read the current clock or calculate window boundaries"
            ),

            "policy_rule": (
                "allowed_count_per_window is explicit caller-supplied "
                "rate policy and may be zero"
            ),

            "usage_rule": (
                "current_usage_count is explicit caller-supplied "
                "usage evidence; 3.1.13 does not increment or persist it"
            ),

            "requested_rule": (
                "requested_admission_count is always explicit "
                "and must be an integer >= 1"
            ),

            "projection_rule": (
                "projected_usage_count equals current_usage_count "
                "plus requested_admission_count"
            ),

            "admission_rule": (
                "projected_usage_count <= allowed_count_per_window "
                "is ALLOW; projected_usage_count greater than "
                "allowed_count_per_window is DENY"
            ),

            "equality_rule": (
                "an admission that exactly fills the rate window "
                "is ALLOW"
            ),

            "enforcement_rule": (
                "ALLOW and DENY are authoritative logical rate "
                "admission decisions; actual enqueue rejection, "
                "waiting, throttling or API behavior is downstream"
            ),

            "http_boundary": (
                "HTTP 429 and Retry-After generation belong to "
                "API/transport enforcement and are not produced here"
            ),

            "backpressure_boundary": (
                "queue pressure classification belongs to "
                "3.1.10 Queue Backpressure"
            ),

            "capacity_boundary": (
                "hard queue depth capacity belongs to "
                "3.1.11 Queue Capacity Limits"
            ),

            "fairness_boundary": (
                "workspace starvation prevention belongs to "
                "3.1.12 Queue Fairness"
            ),

            "quota_boundary": (
                "billing quotas, subscription limits, product limits "
                "and Batch Upload limits are outside Queue Rate Limiting"
            ),

            "prohibitions": (
                "does not read the current clock",
                "does not calculate rate windows",
                "does not maintain window counters",
                "does not increment current_usage_count",
                "does not persist current_usage_count",
                "does not maintain token buckets",
                "does not maintain leaky buckets",
                "does not maintain sliding-window state",
                "does not maintain burst credits",
                "does not sleep or delay execution",
                "does not throttle producers",
                "does not pause producers",
                "does not resume producers",
                "does not return HTTP 429",
                "does not calculate Retry-After",
                "does not perform API rejection",
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
                "does not apply Queue Backpressure",
                "does not enforce queue depth capacity",
                "does not implement Queue Fairness",
                "does not apply billing quotas",
                "does not apply subscription limits",
                "does not apply Batch Upload limits",
                "does not create physical queues",
                "does not perform filesystem I/O",
                "does not perform network I/O",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_QUEUE_RATE_LIMITING_VERSION",
    "UNIVERSAL_QUEUE_RATE_LIMITING_ALGORITHM",
    "UNIVERSAL_QUEUE_RATE_LIMIT_SNAPSHOT_SCHEMA_VERSION",
    "UNIVERSAL_QUEUE_RATE_LIMIT_DECISION_SCHEMA_VERSION",
    "UniversalQueueRateLimitAdmission",
    "UniversalQueueRateLimitError",
    "UniversalQueueRateLimitSnapshot",
    "UniversalQueueRateLimitDecision",
    "normalize_universal_queue_rate_limit_queue_id",
    "normalize_universal_queue_rate_limit_workspace_id",
    "normalize_universal_queue_rate_limit_window_id",
    "normalize_universal_queue_rate_limit_window_seconds",
    "normalize_universal_queue_rate_limit_allowed_count",
    "normalize_universal_queue_rate_limit_usage_count",
    "normalize_universal_queue_rate_limit_requested_count",
    "normalize_universal_queue_rate_limit_admission",
    "create_universal_queue_rate_limit_snapshot",
    "evaluate_universal_queue_rate_limit",
    "explain_universal_queue_rate_limiting_v1",
]
