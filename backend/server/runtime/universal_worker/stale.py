from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from backend.server.runtime.universal_worker.heartbeat import (
    UniversalWorkerHeartbeat,
    normalize_universal_worker_heartbeat_sequence,
    normalize_universal_worker_heartbeat_timestamp,
)
from backend.server.runtime.universal_worker.registration import (
    normalize_universal_worker_id,
    normalize_universal_worker_instance_id,
    normalize_universal_worker_type,
)


UNIVERSAL_STALE_WORKER_DETECTION_VERSION = (
    "universal_stale_worker_detection_v4.1.11"
)

UNIVERSAL_STALE_WORKER_RESULT_SCHEMA_VERSION = (
    "universal_stale_worker_result_schema_v1"
)

MAX_UNIVERSAL_STALE_WORKER_THRESHOLD_SECONDS = (
    2_147_483_647
)


class UniversalStaleWorkerError(
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


class UniversalWorkerStalenessState(
    str,
    Enum,
):

    ACTIVE = "ACTIVE"

    STALE = "STALE"


def normalize_universal_stale_worker_threshold_seconds(
    value: Any,
) -> int:

    if (
        type(value) is not int
        or
        value <= 0
    ):

        raise UniversalStaleWorkerError(
            (
                "stale_threshold_seconds must be "
                "an integer greater than zero."
            ),
            code="invalid_stale_worker_threshold",
            value=value,
        )

    if (
        value
        > MAX_UNIVERSAL_STALE_WORKER_THRESHOLD_SECONDS
    ):

        raise UniversalStaleWorkerError(
            (
                "stale_threshold_seconds exceeds "
                "the supported maximum."
            ),
            code="stale_worker_threshold_too_large",
            value=value,
        )

    return value


def normalize_universal_stale_worker_evaluated_at(
    value: Any,
) -> str:

    try:

        return (
            normalize_universal_worker_heartbeat_timestamp(
                value
            )
        )

    except Exception as exc:

        code = getattr(
            exc,
            "code",
            "invalid_stale_worker_evaluated_at",
        )

        raise UniversalStaleWorkerError(
            (
                "evaluated_at must be a valid "
                "timezone-aware UTC timestamp."
            ),
            code=(
                "invalid_stale_worker_evaluated_at_"
                + str(code)
            ),
            value=value,
        ) from exc


def _parse_timestamp(
    value: str,
) -> datetime:

    return datetime.fromisoformat(
        value
    )


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalStaleWorkerResult:

    worker_id: str

    worker_instance_id: str

    worker_type: str

    heartbeat_at: str

    heartbeat_sequence: int

    evaluated_at: str

    stale_threshold_seconds: int

    age_seconds: float

    state: UniversalWorkerStalenessState

    schema_version: str = (
        UNIVERSAL_STALE_WORKER_RESULT_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        try:

            worker_id = (
                normalize_universal_worker_id(
                    self.worker_id
                )
            )

        except Exception as exc:

            raise UniversalStaleWorkerError(
                "Invalid worker_id in stale result.",
                code="invalid_stale_worker_result_worker_id",
                value=self.worker_id,
            ) from exc

        try:

            worker_instance_id = (
                normalize_universal_worker_instance_id(
                    self.worker_instance_id
                )
            )

        except Exception as exc:

            raise UniversalStaleWorkerError(
                (
                    "Invalid worker_instance_id "
                    "in stale result."
                ),
                code=(
                    "invalid_stale_worker_result_"
                    "worker_instance_id"
                ),
                value=self.worker_instance_id,
            ) from exc

        try:

            worker_type = (
                normalize_universal_worker_type(
                    self.worker_type
                )
            )

        except Exception as exc:

            raise UniversalStaleWorkerError(
                "Invalid worker_type in stale result.",
                code="invalid_stale_worker_result_worker_type",
                value=self.worker_type,
            ) from exc

        heartbeat_at = (
            normalize_universal_worker_heartbeat_timestamp(
                self.heartbeat_at
            )
        )

        evaluated_at = (
            normalize_universal_worker_heartbeat_timestamp(
                self.evaluated_at
            )
        )

        threshold = (
            normalize_universal_stale_worker_threshold_seconds(
                self.stale_threshold_seconds
            )
        )

        try:

            heartbeat_sequence = (
                normalize_universal_worker_heartbeat_sequence(
                    self.heartbeat_sequence
                )
            )

        except Exception as exc:

            raise UniversalStaleWorkerError(
                (
                    "Invalid heartbeat_sequence "
                    "in stale result."
                ),
                code=(
                    "invalid_stale_worker_result_"
                    "heartbeat_sequence"
                ),
                value=self.heartbeat_sequence,
            ) from exc

        if not isinstance(
            self.age_seconds,
            float,
        ):

            raise UniversalStaleWorkerError(
                "age_seconds must be float.",
                code="invalid_stale_worker_result_age",
                value=self.age_seconds,
            )

        if self.age_seconds < 0.0:

            raise UniversalStaleWorkerError(
                "age_seconds must not be negative.",
                code="negative_stale_worker_result_age",
                value=self.age_seconds,
            )

        if not isinstance(
            self.state,
            UniversalWorkerStalenessState,
        ):

            raise UniversalStaleWorkerError(
                "Invalid staleness state.",
                code="invalid_stale_worker_state",
                value=self.state,
            )

        expected_age = (
            _parse_timestamp(
                evaluated_at
            )
            -
            _parse_timestamp(
                heartbeat_at
            )
        ).total_seconds()

        if expected_age < 0:

            raise UniversalStaleWorkerError(
                (
                    "heartbeat_at must not be later "
                    "than evaluated_at."
                ),
                code="future_worker_heartbeat",
                value={
                    "heartbeat_at":
                        heartbeat_at,
                    "evaluated_at":
                        evaluated_at,
                },
            )

        if self.age_seconds != float(
            expected_age
        ):

            raise UniversalStaleWorkerError(
                "Inconsistent stale-worker age.",
                code="inconsistent_stale_worker_age",
                value=self.age_seconds,
            )

        expected_state = (
            UniversalWorkerStalenessState.STALE
            if expected_age >= threshold
            else
            UniversalWorkerStalenessState.ACTIVE
        )

        if self.state is not expected_state:

            raise UniversalStaleWorkerError(
                "Inconsistent stale-worker state.",
                code="inconsistent_stale_worker_state",
                value=self.state,
            )

        if (
            self.schema_version
            != UNIVERSAL_STALE_WORKER_RESULT_SCHEMA_VERSION
        ):

            raise UniversalStaleWorkerError(
                (
                    "Invalid Stale Worker Result "
                    "schema_version."
                ),
                code=(
                    "invalid_stale_worker_result_"
                    "schema_version"
                ),
                value=self.schema_version,
            )

        object.__setattr__(
            self,
            "worker_id",
            worker_id,
        )

        object.__setattr__(
            self,
            "worker_instance_id",
            worker_instance_id,
        )

        object.__setattr__(
            self,
            "worker_type",
            worker_type,
        )

        object.__setattr__(
            self,
            "heartbeat_at",
            heartbeat_at,
        )

        object.__setattr__(
            self,
            "heartbeat_sequence",
            heartbeat_sequence,
        )

        object.__setattr__(
            self,
            "evaluated_at",
            evaluated_at,
        )

        object.__setattr__(
            self,
            "stale_threshold_seconds",
            threshold,
        )

    @property
    def worker_identity(
        self,
    ) -> str:

        return (
            self.worker_id
            + "::"
            + self.worker_instance_id
        )

    @property
    def is_stale(
        self,
    ) -> bool:

        return (
            self.state
            is UniversalWorkerStalenessState.STALE
        )

    @property
    def is_active(
        self,
    ) -> bool:

        return (
            self.state
            is UniversalWorkerStalenessState.ACTIVE
        )


def evaluate_universal_stale_worker(
    *,
    heartbeat: UniversalWorkerHeartbeat,
    evaluated_at: str,
    stale_threshold_seconds: int,
) -> UniversalStaleWorkerResult:

    if not isinstance(
        heartbeat,
        UniversalWorkerHeartbeat,
    ):

        raise UniversalStaleWorkerError(
            (
                "heartbeat must be canonical "
                "UniversalWorkerHeartbeat evidence."
            ),
            code="invalid_stale_worker_heartbeat",
            value=heartbeat,
        )

    normalized_evaluated_at = (
        normalize_universal_stale_worker_evaluated_at(
            evaluated_at
        )
    )

    threshold = (
        normalize_universal_stale_worker_threshold_seconds(
            stale_threshold_seconds
        )
    )

    heartbeat_time = (
        _parse_timestamp(
            heartbeat.heartbeat_at
        )
    )

    evaluation_time = (
        _parse_timestamp(
            normalized_evaluated_at
        )
    )

    if heartbeat_time > evaluation_time:

        raise UniversalStaleWorkerError(
            (
                "heartbeat_at must not be later "
                "than evaluated_at."
            ),
            code="future_worker_heartbeat",
            value={
                "heartbeat_at":
                    heartbeat.heartbeat_at,
                "evaluated_at":
                    normalized_evaluated_at,
            },
        )

    age_seconds = (
        evaluation_time
        - heartbeat_time
    ).total_seconds()

    state = (
        UniversalWorkerStalenessState.STALE
        if age_seconds >= threshold
        else
        UniversalWorkerStalenessState.ACTIVE
    )

    return UniversalStaleWorkerResult(
        worker_id=heartbeat.worker_id,
        worker_instance_id=heartbeat.worker_instance_id,
        worker_type=heartbeat.worker_type,
        heartbeat_at=heartbeat.heartbeat_at,
        heartbeat_sequence=heartbeat.sequence,
        evaluated_at=normalized_evaluated_at,
        stale_threshold_seconds=threshold,
        age_seconds=float(
            age_seconds
        ),
        state=state,
    )


def explain_universal_stale_worker_detection_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "4.1.11",

            "component":
                "Universal Stale Worker Detection",

            "version":
                UNIVERSAL_STALE_WORKER_DETECTION_VERSION,

            "result_schema_version":
                UNIVERSAL_STALE_WORKER_RESULT_SCHEMA_VERSION,

            "input_rule": (
                "4.1.11 consumes canonical 4.1.10 "
                "UniversalWorkerHeartbeat evidence plus "
                "caller-supplied evaluated_at and "
                "stale_threshold_seconds"
            ),

            "time_rule": (
                "evaluated_at is caller-supplied, "
                "timezone-aware UTC; 4.1.11 does not "
                "read the wall clock"
            ),

            "threshold_rule": (
                "stale_threshold_seconds is a positive "
                "caller-supplied integer"
            ),

            "active_rule": (
                "heartbeat age strictly less than the "
                "threshold is ACTIVE"
            ),

            "stale_rule": (
                "heartbeat age greater than or equal "
                "to the threshold is STALE"
            ),

            "equality_rule": (
                "age equal to stale_threshold_seconds "
                "is STALE"
            ),

            "future_heartbeat_rule": (
                "heartbeat_at later than evaluated_at "
                "is contradictory evidence and is rejected"
            ),

            "missing_heartbeat_rule": (
                "missing heartbeat evidence is invalid "
                "input rather than ACTIVE, STALE or UNKNOWN"
            ),

            "age_rule": (
                "4.1.11 owns deterministic heartbeat "
                "age calculation"
            ),

            "health_boundary": (
                "STALE is not UNHEALTHY and 4.1.11 does "
                "not invoke or mutate 4.1.5 Worker Health"
            ),

            "lease_boundary": (
                "STALE is independent from ACTIVE or "
                "EXPIRED Worker Leasing state"
            ),

            "recovery_boundary": (
                "STALE is evidence only; 4.1.11 does not "
                "authorize or initiate Worker Recovery"
            ),

            "queue_recovery_boundary": (
                "Queue Recovery may later consume "
                "stale-worker evidence but 4.1.11 does "
                "not requeue, fail or mutate jobs"
            ),

            "registration_pool_boundary": (
                "STALE does not deregister workers or "
                "remove Worker Pool membership"
            ),

            "shutdown_drain_boundary": (
                "STALE does not automatically shut down "
                "or drain workers"
            ),

            "persistence_boundary": (
                "4.1.11 does not persist stale state or "
                "access Runtime State Store"
            ),

            "purity_rule": (
                "Stale Worker Detection is deterministic "
                "over caller-supplied evidence and "
                "performs no external mutation or I/O"
            ),

            "prohibitions": (
                "does not read the wall clock",
                "does not generate evaluation timestamps",
                "does not define a global stale threshold",
                "does not define heartbeat interval",
                "does not accept missing heartbeat as STALE",
                "does not accept missing heartbeat as ACTIVE",
                "does not create UNKNOWN staleness",
                "does not determine Worker Health",
                "does not mark workers UNHEALTHY",
                "does not initiate Worker Recovery",
                "does not mark jobs FAILED",
                "does not requeue jobs",
                "does not cancel jobs",
                "does not acquire leases",
                "does not renew leases",
                "does not release leases",
                "does not equate stale worker with expired lease",
                "does not modify Worker Registration",
                "does not deregister workers",
                "does not modify Worker Pool membership",
                "does not discover workers",
                "does not assign workers",
                "does not scale workers",
                "does not shut down workers",
                "does not drain workers",
                "does not inspect worker capabilities",
                "does not calculate worker capacity",
                "does not access Runtime State Store",
                "does not access orchestration",
                "does not persist stale state",
                "does not perform filesystem I/O",
                "does not perform network I/O",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_STALE_WORKER_DETECTION_VERSION",
    "UNIVERSAL_STALE_WORKER_RESULT_SCHEMA_VERSION",
    "MAX_UNIVERSAL_STALE_WORKER_THRESHOLD_SECONDS",
    "UniversalStaleWorkerError",
    "UniversalWorkerStalenessState",
    "UniversalStaleWorkerResult",
    "normalize_universal_stale_worker_threshold_seconds",
    "normalize_universal_stale_worker_evaluated_at",
    "evaluate_universal_stale_worker",
    "explain_universal_stale_worker_detection_v1",
]
