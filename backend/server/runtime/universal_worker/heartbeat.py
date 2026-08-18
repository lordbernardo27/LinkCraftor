from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from types import MappingProxyType
from typing import Any, Mapping

from backend.server.runtime.universal_worker.registration import (
    UniversalWorkerRegistration,
    normalize_universal_worker_id,
    normalize_universal_worker_instance_id,
    normalize_universal_worker_type,
)


UNIVERSAL_WORKER_HEARTBEAT_VERSION = (
    "universal_worker_heartbeat_v4.1.10"
)

UNIVERSAL_WORKER_HEARTBEAT_SCHEMA_VERSION = (
    "universal_worker_heartbeat_schema_v1"
)

MAX_UNIVERSAL_WORKER_HEARTBEAT_SEQUENCE = (
    2_147_483_647
)

UNIVERSAL_WORKER_HEARTBEAT_IDENTITY_SEPARATOR = (
    "::"
)


class UniversalWorkerHeartbeatError(
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


def normalize_universal_worker_heartbeat_timestamp(
    value: Any,
) -> str:

    if not isinstance(
        value,
        str,
    ):

        raise UniversalWorkerHeartbeatError(
            "heartbeat_at must be str.",
            code="invalid_worker_heartbeat_timestamp_type",
            value=value,
        )

    normalized = value.strip()

    if not normalized:

        raise UniversalWorkerHeartbeatError(
            "heartbeat_at must not be empty.",
            code="empty_worker_heartbeat_timestamp",
            value=value,
        )

    parse_value = normalized

    if parse_value.endswith(
        "Z"
    ):

        parse_value = (
            parse_value[:-1]
            + "+00:00"
        )

    try:

        parsed = datetime.fromisoformat(
            parse_value
        )

    except ValueError as exc:

        raise UniversalWorkerHeartbeatError(
            (
                "heartbeat_at must be a valid "
                "ISO-8601 timestamp."
            ),
            code="invalid_worker_heartbeat_timestamp",
            value=value,
        ) from exc

    if (
        parsed.tzinfo is None
        or
        parsed.utcoffset() is None
    ):

        raise UniversalWorkerHeartbeatError(
            (
                "heartbeat_at must be "
                "timezone-aware UTC."
            ),
            code="naive_worker_heartbeat_timestamp",
            value=value,
        )

    if parsed.utcoffset() != timedelta(0):

        raise UniversalWorkerHeartbeatError(
            (
                "heartbeat_at must use UTC."
            ),
            code="non_utc_worker_heartbeat_timestamp",
            value=value,
        )

    canonical = (
        parsed.astimezone(
            timezone.utc
        )
        .isoformat()
    )

    return canonical


def _parse_canonical_heartbeat_timestamp(
    value: str,
) -> datetime:

    return datetime.fromisoformat(
        value
    )


def normalize_universal_worker_heartbeat_sequence(
    value: Any,
) -> int:

    if (
        type(value) is not int
        or
        value < 1
    ):

        raise UniversalWorkerHeartbeatError(
            (
                "sequence must be an integer "
                "greater than or equal to 1."
            ),
            code="invalid_worker_heartbeat_sequence",
            value=value,
        )

    if (
        value
        > MAX_UNIVERSAL_WORKER_HEARTBEAT_SEQUENCE
    ):

        raise UniversalWorkerHeartbeatError(
            (
                "sequence exceeds the supported "
                "maximum."
            ),
            code="worker_heartbeat_sequence_too_large",
            value=value,
        )

    return value


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalWorkerHeartbeat:

    worker_id: str

    worker_instance_id: str

    worker_type: str

    heartbeat_at: str

    sequence: int

    schema_version: str = (
        UNIVERSAL_WORKER_HEARTBEAT_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        object.__setattr__(
            self,
            "worker_id",
            normalize_universal_worker_id(
                self.worker_id
            ),
        )

        object.__setattr__(
            self,
            "worker_instance_id",
            normalize_universal_worker_instance_id(
                self.worker_instance_id
            ),
        )

        object.__setattr__(
            self,
            "worker_type",
            normalize_universal_worker_type(
                self.worker_type
            ),
        )

        object.__setattr__(
            self,
            "heartbeat_at",
            normalize_universal_worker_heartbeat_timestamp(
                self.heartbeat_at
            ),
        )

        object.__setattr__(
            self,
            "sequence",
            normalize_universal_worker_heartbeat_sequence(
                self.sequence
            ),
        )

        if (
            self.schema_version
            != UNIVERSAL_WORKER_HEARTBEAT_SCHEMA_VERSION
        ):

            raise UniversalWorkerHeartbeatError(
                (
                    "Invalid Universal Worker "
                    "Heartbeat schema_version."
                ),
                code=(
                    "invalid_worker_heartbeat_"
                    "schema_version"
                ),
                value=self.schema_version,
            )

    @property
    def worker_identity(
        self,
    ) -> str:

        return (
            self.worker_id
            + UNIVERSAL_WORKER_HEARTBEAT_IDENTITY_SEPARATOR
            + self.worker_instance_id
        )


def validate_universal_worker_heartbeat_progression(
    *,
    previous: UniversalWorkerHeartbeat,
    current: UniversalWorkerHeartbeat,
) -> None:

    if not isinstance(
        previous,
        UniversalWorkerHeartbeat,
    ):

        raise UniversalWorkerHeartbeatError(
            (
                "previous must be "
                "UniversalWorkerHeartbeat."
            ),
            code="invalid_previous_worker_heartbeat",
            value=previous,
        )

    if not isinstance(
        current,
        UniversalWorkerHeartbeat,
    ):

        raise UniversalWorkerHeartbeatError(
            (
                "current must be "
                "UniversalWorkerHeartbeat."
            ),
            code="invalid_current_worker_heartbeat",
            value=current,
        )

    if (
        previous.worker_identity
        != current.worker_identity
    ):

        raise UniversalWorkerHeartbeatError(
            (
                "Heartbeat progression requires "
                "the same worker identity."
            ),
            code="worker_heartbeat_identity_mismatch",
            value={
                "previous":
                    previous.worker_identity,

                "current":
                    current.worker_identity,
            },
        )

    if (
        previous.worker_type
        != current.worker_type
    ):

        raise UniversalWorkerHeartbeatError(
            (
                "Heartbeat progression requires "
                "the same worker_type."
            ),
            code="worker_heartbeat_type_mismatch",
            value={
                "previous":
                    previous.worker_type,

                "current":
                    current.worker_type,
            },
        )

    if (
        current.sequence
        == previous.sequence
    ):

        raise UniversalWorkerHeartbeatError(
            "Duplicate heartbeat sequence.",
            code="duplicate_worker_heartbeat_sequence",
            value=current.sequence,
        )

    if (
        current.sequence
        < previous.sequence
    ):

        raise UniversalWorkerHeartbeatError(
            "Out-of-order heartbeat sequence.",
            code="out_of_order_worker_heartbeat_sequence",
            value={
                "previous":
                    previous.sequence,

                "current":
                    current.sequence,
            },
        )

    previous_at = (
        _parse_canonical_heartbeat_timestamp(
            previous.heartbeat_at
        )
    )

    current_at = (
        _parse_canonical_heartbeat_timestamp(
            current.heartbeat_at
        )
    )

    if (
        current_at
        <= previous_at
    ):

        raise UniversalWorkerHeartbeatError(
            (
                "heartbeat_at must increase "
                "across heartbeat progression."
            ),
            code="non_increasing_worker_heartbeat_timestamp",
            value={
                "previous":
                    previous.heartbeat_at,

                "current":
                    current.heartbeat_at,
            },
        )


def create_universal_worker_heartbeat(
    *,
    registration: UniversalWorkerRegistration,
    heartbeat_at: str,
    sequence: int,
    previous_heartbeat: UniversalWorkerHeartbeat | None = None,
) -> UniversalWorkerHeartbeat:

    if not isinstance(
        registration,
        UniversalWorkerRegistration,
    ):

        raise UniversalWorkerHeartbeatError(
            (
                "registration must be "
                "UniversalWorkerRegistration."
            ),
            code="invalid_worker_heartbeat_registration",
            value=registration,
        )

    heartbeat = (
        UniversalWorkerHeartbeat(
            worker_id=(
                registration.worker_id
            ),
            worker_instance_id=(
                registration.worker_instance_id
            ),
            worker_type=(
                registration.worker_type
            ),
            heartbeat_at=heartbeat_at,
            sequence=sequence,
        )
    )

    if previous_heartbeat is not None:

        validate_universal_worker_heartbeat_progression(
            previous=previous_heartbeat,
            current=heartbeat,
        )

    return heartbeat


def explain_universal_worker_heartbeat_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "4.1.10",

            "component":
                "Universal Worker Heartbeats",

            "version":
                UNIVERSAL_WORKER_HEARTBEAT_VERSION,

            "schema_version":
                UNIVERSAL_WORKER_HEARTBEAT_SCHEMA_VERSION,

            "identity_rule": (
                "heartbeat identity is the canonical "
                "Worker Registration identity "
                "(worker_id, worker_instance_id)"
            ),

            "registration_rule": (
                "canonical heartbeat creation consumes "
                "immutable UniversalWorkerRegistration "
                "identity evidence"
            ),

            "timestamp_rule": (
                "heartbeat_at is caller-supplied, "
                "timezone-aware UTC and deterministic; "
                "4.1.10 does not read the wall clock"
            ),

            "sequence_rule": (
                "heartbeat sequence is caller-supplied "
                "and strictly increases when prior "
                "heartbeat evidence is supplied"
            ),

            "duplicate_rule": (
                "an equal sequence relative to the "
                "supplied prior heartbeat is rejected "
                "as duplicate"
            ),

            "ordering_rule": (
                "a lower sequence or non-increasing "
                "heartbeat timestamp relative to the "
                "supplied prior heartbeat is rejected"
            ),

            "prior_evidence_rule": (
                "progression validation occurs only "
                "against caller-supplied prior heartbeat "
                "evidence for the same worker identity"
            ),

            "interval_boundary": (
                "heartbeat emission interval and "
                "frequency configuration remain "
                "outside 4.1.10"
            ),

            "freshness_boundary": (
                "4.1.11 Stale Worker Detection owns "
                "heartbeat age, freshness and stale "
                "classification"
            ),

            "health_boundary": (
                "4.1.5 Worker Health remains separate; "
                "heartbeat evidence does not classify "
                "HEALTHY, DEGRADED, UNHEALTHY or UNKNOWN"
            ),

            "recovery_boundary": (
                "4.1.6 Worker Recovery remains separate; "
                "heartbeat evidence does not authorize "
                "or initiate recovery"
            ),

            "legacy_runtime_boundary": (
                "4.1.10 does not replace or invoke the "
                "existing universal_runtime_infrastructure "
                "worker_heartbeat filesystem publisher"
            ),

            "orchestration_boundary": (
                "4.1.10 does not replace or mutate "
                "existing orchestration WorkerHeartbeat "
                "or TMS WorkerStatus mechanisms"
            ),

            "payload_boundary": (
                "canonical heartbeat evidence does not "
                "carry workspace, current job, lease, "
                "pool, health, capability or capacity "
                "state"
            ),

            "persistence_boundary": (
                "4.1.10 does not persist heartbeat "
                "evidence or access Runtime State Store"
            ),

            "purity_rule": (
                "Worker Heartbeats is deterministic over "
                "caller-supplied evidence and performs "
                "no filesystem, network, clock, thread, "
                "persistence or runtime mutation"
            ),

            "prohibitions": (
                "does not generate heartbeat timestamps",
                "does not read the wall clock",
                "does not define heartbeat interval",
                "does not sleep between heartbeats",
                "does not run a heartbeat loop",
                "does not start heartbeat threads",
                "does not publish heartbeat over network",
                "does not write heartbeat files",
                "does not access Runtime State Store",
                "does not persist heartbeat evidence",
                "does not calculate heartbeat age",
                "does not calculate heartbeat freshness",
                "does not detect stale workers",
                "does not determine worker liveness",
                "does not determine worker health",
                "does not initiate worker recovery",
                "does not release worker leases",
                "does not requeue jobs",
                "does not cancel jobs",
                "does not mutate Worker Registration",
                "does not modify Worker Pool membership",
                "does not discover workers",
                "does not assign workers",
                "does not scale workers",
                "does not shut down workers",
                "does not drain workers",
                "does not inspect worker capabilities",
                "does not calculate worker capacity",
                "does not include current job state",
                "does not include workspace state",
                "does not invoke legacy runtime heartbeat publisher",
                "does not mutate orchestration heartbeat models",
                "does not perform filesystem I/O",
                "does not perform network I/O",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_WORKER_HEARTBEAT_VERSION",
    "UNIVERSAL_WORKER_HEARTBEAT_SCHEMA_VERSION",
    "MAX_UNIVERSAL_WORKER_HEARTBEAT_SEQUENCE",
    "UNIVERSAL_WORKER_HEARTBEAT_IDENTITY_SEPARATOR",
    "UniversalWorkerHeartbeatError",
    "UniversalWorkerHeartbeat",
    "normalize_universal_worker_heartbeat_timestamp",
    "normalize_universal_worker_heartbeat_sequence",
    "validate_universal_worker_heartbeat_progression",
    "create_universal_worker_heartbeat",
    "explain_universal_worker_heartbeat_v1",
]
