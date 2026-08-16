from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from backend.server.runtime.universal_worker.assignment import (
    UniversalWorkerAssignmentResult,
    UniversalWorkerAssignmentStatus,
)


UNIVERSAL_WORKER_LEASING_VERSION = (
    "universal_worker_leasing_v4.1.4"
)

UNIVERSAL_WORKER_LEASE_SCHEMA_VERSION = (
    "universal_worker_lease_schema_v1"
)

UNIVERSAL_WORKER_LEASE_RELEASE_SCHEMA_VERSION = (
    "universal_worker_lease_release_schema_v1"
)

MAX_UNIVERSAL_WORKER_LEASE_ID_LENGTH = 200

UNIVERSAL_WORKER_LEASE_OWNER_SEPARATOR = "::"


class UniversalWorkerLeasingError(
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


class UniversalWorkerLeaseState(
    str,
    Enum,
):

    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"


def normalize_universal_worker_lease_id(
    value: Any,
) -> str:

    if not isinstance(
        value,
        str,
    ):

        raise UniversalWorkerLeasingError(
            "lease_id must be a string.",
            code="invalid_lease_id_type",
            value=value,
        )

    normalized = value.strip()

    if not normalized:

        raise UniversalWorkerLeasingError(
            "lease_id must not be empty.",
            code="empty_lease_id",
            value=value,
        )

    if (
        len(normalized)
        > MAX_UNIVERSAL_WORKER_LEASE_ID_LENGTH
    ):

        raise UniversalWorkerLeasingError(
            (
                "lease_id exceeds maximum "
                "supported length."
            ),
            code="lease_id_too_long",
            value=value,
        )

    return normalized


def normalize_universal_worker_lease_timestamp(
    value: Any,
    *,
    field_name: str,
) -> str:

    if not isinstance(
        value,
        str,
    ):

        raise UniversalWorkerLeasingError(
            (
                field_name
                + " must be an ISO-8601 timestamp string."
            ),
            code="invalid_lease_timestamp_type",
            value=value,
        )

    raw = value.strip()

    if not raw:

        raise UniversalWorkerLeasingError(
            (
                field_name
                + " must not be empty."
            ),
            code="empty_lease_timestamp",
            value=value,
        )

    candidate = raw

    if candidate.endswith(
        "Z"
    ):

        candidate = (
            candidate[:-1]
            + "+00:00"
        )

    try:

        parsed = datetime.fromisoformat(
            candidate
        )

    except ValueError as exc:

        raise UniversalWorkerLeasingError(
            (
                field_name
                + " must be a valid ISO-8601 timestamp."
            ),
            code="invalid_lease_timestamp",
            value=value,
        ) from exc

    if parsed.tzinfo is None:

        raise UniversalWorkerLeasingError(
            (
                field_name
                + " must include timezone information."
            ),
            code="naive_lease_timestamp",
            value=value,
        )

    canonical = (
        parsed.astimezone(
            timezone.utc
        )
        .isoformat(
            timespec="microseconds"
        )
        .replace(
            "+00:00",
            "Z",
        )
    )

    return canonical


def _timestamp_key(
    value: str,
) -> datetime:

    return datetime.fromisoformat(
        value.replace(
            "Z",
            "+00:00",
        )
    )


def create_universal_worker_lease_owner(
    assignment: UniversalWorkerAssignmentResult,
) -> str:

    if not isinstance(
        assignment,
        UniversalWorkerAssignmentResult,
    ):

        raise UniversalWorkerLeasingError(
            (
                "assignment must be a "
                "UniversalWorkerAssignmentResult."
            ),
            code="invalid_worker_assignment",
            value=assignment,
        )

    if (
        assignment.status
        is not UniversalWorkerAssignmentStatus.ASSIGNED
        or assignment.worker is None
    ):

        raise UniversalWorkerLeasingError(
            (
                "A worker lease requires an "
                "ASSIGNED Worker Assignment result."
            ),
            code="worker_assignment_required",
            value=assignment.status,
        )

    worker_id = (
        assignment.worker.worker_id
    )

    worker_instance_id = (
        assignment.worker.worker_instance_id
    )

    if (
        UNIVERSAL_WORKER_LEASE_OWNER_SEPARATOR
        in worker_id
        or
        UNIVERSAL_WORKER_LEASE_OWNER_SEPARATOR
        in worker_instance_id
    ):

        raise UniversalWorkerLeasingError(
            (
                "worker identity contains the "
                "reserved lease-owner separator."
            ),
            code="invalid_lease_owner_identity",
            value=(
                worker_id,
                worker_instance_id,
            ),
        )

    return (
        worker_id
        + UNIVERSAL_WORKER_LEASE_OWNER_SEPARATOR
        + worker_instance_id
    )


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalWorkerLease:

    job_id: str
    lease_owner: str
    lease_id: str
    lease_started_at: str
    lease_expires_at: str

    schema_version: str = (
        UNIVERSAL_WORKER_LEASE_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        if not isinstance(
            self.job_id,
            str,
        ):

            raise UniversalWorkerLeasingError(
                "job_id must be a string.",
                code="invalid_lease_job_id_type",
                value=self.job_id,
            )

        canonical_job_id = (
            self.job_id.strip()
        )

        if not canonical_job_id:

            raise UniversalWorkerLeasingError(
                "job_id must not be empty.",
                code="empty_lease_job_id",
                value=self.job_id,
            )

        object.__setattr__(
            self,
            "job_id",
            canonical_job_id,
        )

        if not isinstance(
            self.lease_owner,
            str,
        ):

            raise UniversalWorkerLeasingError(
                "lease_owner must be a string.",
                code="invalid_lease_owner_type",
                value=self.lease_owner,
            )

        canonical_owner = (
            self.lease_owner.strip()
        )

        if not canonical_owner:

            raise UniversalWorkerLeasingError(
                "lease_owner must not be empty.",
                code="empty_lease_owner",
                value=self.lease_owner,
            )

        if (
            canonical_owner.count(
                UNIVERSAL_WORKER_LEASE_OWNER_SEPARATOR
            )
            != 1
        ):

            raise UniversalWorkerLeasingError(
                (
                    "lease_owner must encode exactly "
                    "one worker_id and worker_instance_id."
                ),
                code="invalid_lease_owner",
                value=self.lease_owner,
            )

        left, right = canonical_owner.split(
            UNIVERSAL_WORKER_LEASE_OWNER_SEPARATOR,
            1,
        )

        if (
            not left
            or not right
        ):

            raise UniversalWorkerLeasingError(
                (
                    "lease_owner contains an "
                    "invalid worker identity."
                ),
                code="invalid_lease_owner",
                value=self.lease_owner,
            )

        object.__setattr__(
            self,
            "lease_owner",
            canonical_owner,
        )

        object.__setattr__(
            self,
            "lease_id",
            normalize_universal_worker_lease_id(
                self.lease_id
            ),
        )

        canonical_started = (
            normalize_universal_worker_lease_timestamp(
                self.lease_started_at,
                field_name="lease_started_at",
            )
        )

        canonical_expires = (
            normalize_universal_worker_lease_timestamp(
                self.lease_expires_at,
                field_name="lease_expires_at",
            )
        )

        if (
            _timestamp_key(
                canonical_expires
            )
            <=
            _timestamp_key(
                canonical_started
            )
        ):

            raise UniversalWorkerLeasingError(
                (
                    "lease_expires_at must be "
                    "strictly later than lease_started_at."
                ),
                code="invalid_lease_interval",
                value=(
                    canonical_started,
                    canonical_expires,
                ),
            )

        object.__setattr__(
            self,
            "lease_started_at",
            canonical_started,
        )

        object.__setattr__(
            self,
            "lease_expires_at",
            canonical_expires,
        )

        if (
            self.schema_version
            != UNIVERSAL_WORKER_LEASE_SCHEMA_VERSION
        ):

            raise UniversalWorkerLeasingError(
                (
                    "Invalid Worker Lease "
                    "schema_version."
                ),
                code=(
                    "invalid_worker_lease_"
                    "schema_version"
                ),
                value=self.schema_version,
            )

    @property
    def worker_identity(
        self,
    ) -> tuple[str, str]:

        worker_id, worker_instance_id = (
            self.lease_owner.split(
                UNIVERSAL_WORKER_LEASE_OWNER_SEPARATOR,
                1,
            )
        )

        return (
            worker_id,
            worker_instance_id,
        )

    def to_job_lease_fields(
        self,
    ) -> Mapping[str, str]:

        return MappingProxyType(
            {
                "lease_owner":
                    self.lease_owner,

                "lease_id":
                    self.lease_id,

                "lease_started_at":
                    self.lease_started_at,

                "lease_expires_at":
                    self.lease_expires_at,
            }
        )


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalWorkerLeaseRelease:

    job_id: str
    lease_owner: str
    lease_id: str
    released_at: str

    schema_version: str = (
        UNIVERSAL_WORKER_LEASE_RELEASE_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        if not isinstance(
            self.job_id,
            str,
        ) or not self.job_id.strip():

            raise UniversalWorkerLeasingError(
                "job_id must be a non-empty string.",
                code="invalid_release_job_id",
                value=self.job_id,
            )

        object.__setattr__(
            self,
            "job_id",
            self.job_id.strip(),
        )

        if not isinstance(
            self.lease_owner,
            str,
        ) or not self.lease_owner.strip():

            raise UniversalWorkerLeasingError(
                (
                    "lease_owner must be "
                    "a non-empty string."
                ),
                code="invalid_release_lease_owner",
                value=self.lease_owner,
            )

        object.__setattr__(
            self,
            "lease_owner",
            self.lease_owner.strip(),
        )

        object.__setattr__(
            self,
            "lease_id",
            normalize_universal_worker_lease_id(
                self.lease_id
            ),
        )

        object.__setattr__(
            self,
            "released_at",
            normalize_universal_worker_lease_timestamp(
                self.released_at,
                field_name="released_at",
            ),
        )

        if (
            self.schema_version
            != UNIVERSAL_WORKER_LEASE_RELEASE_SCHEMA_VERSION
        ):

            raise UniversalWorkerLeasingError(
                (
                    "Invalid Worker Lease Release "
                    "schema_version."
                ),
                code=(
                    "invalid_worker_lease_release_"
                    "schema_version"
                ),
                value=self.schema_version,
            )


def acquire_universal_worker_lease(
    *,
    assignment: UniversalWorkerAssignmentResult,
    lease_id: str,
    lease_started_at: str,
    lease_expires_at: str,
    existing_lease: UniversalWorkerLease | None = None,
) -> UniversalWorkerLease:

    if not isinstance(
        assignment,
        UniversalWorkerAssignmentResult,
    ):

        raise UniversalWorkerLeasingError(
            (
                "assignment must be a "
                "UniversalWorkerAssignmentResult."
            ),
            code="invalid_worker_assignment",
            value=assignment,
        )

    if (
        assignment.status
        is not UniversalWorkerAssignmentStatus.ASSIGNED
        or assignment.worker is None
    ):

        raise UniversalWorkerLeasingError(
            (
                "A worker lease requires an "
                "ASSIGNED Worker Assignment result."
            ),
            code="worker_assignment_required",
            value=assignment.status,
        )

    if existing_lease is not None:

        if not isinstance(
            existing_lease,
            UniversalWorkerLease,
        ):

            raise UniversalWorkerLeasingError(
                (
                    "existing_lease must be a "
                    "UniversalWorkerLease or None."
                ),
                code="invalid_existing_lease",
                value=existing_lease,
            )

        raise UniversalWorkerLeasingError(
            (
                "A lease already exists for this "
                "acquisition boundary and must be "
                "resolved before another lease "
                "can be acquired."
            ),
            code="lease_conflict",
            value=existing_lease.lease_id,
        )

    owner = (
        create_universal_worker_lease_owner(
            assignment
        )
    )

    return UniversalWorkerLease(
        job_id=assignment.job_id,
        lease_owner=owner,
        lease_id=lease_id,
        lease_started_at=lease_started_at,
        lease_expires_at=lease_expires_at,
    )


def evaluate_universal_worker_lease_state(
    *,
    lease: UniversalWorkerLease,
    evaluation_at: str,
) -> UniversalWorkerLeaseState:

    if not isinstance(
        lease,
        UniversalWorkerLease,
    ):

        raise UniversalWorkerLeasingError(
            "lease must be a UniversalWorkerLease.",
            code="invalid_worker_lease",
            value=lease,
        )

    canonical_evaluation = (
        normalize_universal_worker_lease_timestamp(
            evaluation_at,
            field_name="evaluation_at",
        )
    )

    if (
        _timestamp_key(
            canonical_evaluation
        )
        <
        _timestamp_key(
            lease.lease_expires_at
        )
    ):

        return (
            UniversalWorkerLeaseState.ACTIVE
        )

    return (
        UniversalWorkerLeaseState.EXPIRED
    )


def renew_universal_worker_lease(
    *,
    lease: UniversalWorkerLease,
    expected_lease_owner: str,
    expected_lease_id: str,
    renewed_at: str,
    new_lease_expires_at: str,
) -> UniversalWorkerLease:

    if not isinstance(
        lease,
        UniversalWorkerLease,
    ):

        raise UniversalWorkerLeasingError(
            "lease must be a UniversalWorkerLease.",
            code="invalid_worker_lease",
            value=lease,
        )

    if (
        not isinstance(
            expected_lease_owner,
            str,
        )
        or
        expected_lease_owner.strip()
        != lease.lease_owner
    ):

        raise UniversalWorkerLeasingError(
            (
                "Lease renewal owner does not "
                "match the current lease owner."
            ),
            code="lease_owner_mismatch",
            value=expected_lease_owner,
        )

    canonical_lease_id = (
        normalize_universal_worker_lease_id(
            expected_lease_id
        )
    )

    if (
        canonical_lease_id
        != lease.lease_id
    ):

        raise UniversalWorkerLeasingError(
            (
                "Lease renewal lease_id does not "
                "match the current lease."
            ),
            code="lease_id_mismatch",
            value=expected_lease_id,
        )

    canonical_renewed_at = (
        normalize_universal_worker_lease_timestamp(
            renewed_at,
            field_name="renewed_at",
        )
    )

    if (
        evaluate_universal_worker_lease_state(
            lease=lease,
            evaluation_at=canonical_renewed_at,
        )
        is not UniversalWorkerLeaseState.ACTIVE
    ):

        raise UniversalWorkerLeasingError(
            (
                "An expired lease cannot "
                "be renewed."
            ),
            code="expired_lease_cannot_renew",
            value=lease.lease_id,
        )

    canonical_new_expiry = (
        normalize_universal_worker_lease_timestamp(
            new_lease_expires_at,
            field_name="new_lease_expires_at",
        )
    )

    if (
        _timestamp_key(
            canonical_new_expiry
        )
        <=
        _timestamp_key(
            canonical_renewed_at
        )
    ):

        raise UniversalWorkerLeasingError(
            (
                "new_lease_expires_at must be "
                "later than renewed_at."
            ),
            code="invalid_renewal_interval",
            value=canonical_new_expiry,
        )

    if (
        _timestamp_key(
            canonical_new_expiry
        )
        <=
        _timestamp_key(
            lease.lease_expires_at
        )
    ):

        raise UniversalWorkerLeasingError(
            (
                "Lease renewal must extend "
                "the current expiration."
            ),
            code="lease_renewal_not_extended",
            value=canonical_new_expiry,
        )

    return UniversalWorkerLease(
        job_id=lease.job_id,
        lease_owner=lease.lease_owner,
        lease_id=lease.lease_id,
        lease_started_at=lease.lease_started_at,
        lease_expires_at=canonical_new_expiry,
    )


def release_universal_worker_lease(
    *,
    lease: UniversalWorkerLease,
    expected_lease_owner: str,
    expected_lease_id: str,
    released_at: str,
) -> UniversalWorkerLeaseRelease:

    if not isinstance(
        lease,
        UniversalWorkerLease,
    ):

        raise UniversalWorkerLeasingError(
            "lease must be a UniversalWorkerLease.",
            code="invalid_worker_lease",
            value=lease,
        )

    if (
        not isinstance(
            expected_lease_owner,
            str,
        )
        or
        expected_lease_owner.strip()
        != lease.lease_owner
    ):

        raise UniversalWorkerLeasingError(
            (
                "Lease release owner does not "
                "match the current lease owner."
            ),
            code="lease_owner_mismatch",
            value=expected_lease_owner,
        )

    canonical_lease_id = (
        normalize_universal_worker_lease_id(
            expected_lease_id
        )
    )

    if (
        canonical_lease_id
        != lease.lease_id
    ):

        raise UniversalWorkerLeasingError(
            (
                "Lease release lease_id does not "
                "match the current lease."
            ),
            code="lease_id_mismatch",
            value=expected_lease_id,
        )

    canonical_released_at = (
        normalize_universal_worker_lease_timestamp(
            released_at,
            field_name="released_at",
        )
    )

    if (
        _timestamp_key(
            canonical_released_at
        )
        <
        _timestamp_key(
            lease.lease_started_at
        )
    ):

        raise UniversalWorkerLeasingError(
            (
                "released_at must not precede "
                "lease_started_at."
            ),
            code="release_precedes_lease",
            value=canonical_released_at,
        )

    return UniversalWorkerLeaseRelease(
        job_id=lease.job_id,
        lease_owner=lease.lease_owner,
        lease_id=lease.lease_id,
        released_at=canonical_released_at,
    )


def explain_universal_worker_leasing_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "4.1.4",

            "component":
                "Universal Worker Leasing",

            "version":
                UNIVERSAL_WORKER_LEASING_VERSION,

            "lease_schema_version":
                UNIVERSAL_WORKER_LEASE_SCHEMA_VERSION,

            "release_schema_version":
                UNIVERSAL_WORKER_LEASE_RELEASE_SCHEMA_VERSION,

            "canonical_job_fields": (
                "lease_owner",
                "lease_id",
                "lease_started_at",
                "lease_expires_at",
            ),

            "owner_rule": (
                "lease_owner deterministically encodes "
                "worker_id::worker_instance_id"
            ),

            "acquisition_rule": (
                "lease acquisition requires an ASSIGNED "
                "Worker Assignment and no unresolved "
                "existing lease"
            ),

            "timestamp_rule": (
                "lease timestamps are caller-supplied "
                "timezone-aware evidence normalized to UTC"
            ),

            "expiration_rule": (
                "lease state is evaluated using "
                "caller-supplied evaluation_at; "
                "evaluation_at before lease_expires_at "
                "is ACTIVE, otherwise EXPIRED"
            ),

            "renewal_rule": (
                "renewal requires matching owner and "
                "lease_id, an ACTIVE lease, and a new "
                "expiration later than both renewed_at "
                "and the current expiration"
            ),

            "release_rule": (
                "release requires matching owner and "
                "lease_id and produces immutable "
                "release evidence"
            ),

            "persistence_rule": (
                "4.1.4 produces immutable lease evidence "
                "and never mutates or persists UniversalJob"
            ),

            "recovery_boundary": (
                "expiration classification does not "
                "requeue, recover, reassign or otherwise "
                "repair the job"
            ),

            "prohibitions": (
                "does not generate lease_id",
                "does not use wall-clock time",
                "does not mutate UniversalJob",
                "does not persist leases",
                "does not access Runtime State Store",
                "does not mutate Queue Infrastructure",
                "does not dequeue jobs",
                "does not claim jobs",
                "does not assign workers",
                "does not discover workers",
                "does not transition jobs to LEASED",
                "does not transition jobs to RUNNING",
                "does not dispatch jobs",
                "does not execute jobs",
                "does not requeue expired leases",
                "does not recover workers",
                "does not dead-letter jobs",
                "does not determine worker health",
                "does not read worker heartbeats",
                "does not determine worker capability",
                "does not determine worker capacity",
                "does not manage worker pools",
                "does not access orchestration",
                "does not perform filesystem I/O",
                "does not perform network I/O",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_WORKER_LEASING_VERSION",
    "UNIVERSAL_WORKER_LEASE_SCHEMA_VERSION",
    "UNIVERSAL_WORKER_LEASE_RELEASE_SCHEMA_VERSION",
    "MAX_UNIVERSAL_WORKER_LEASE_ID_LENGTH",
    "UNIVERSAL_WORKER_LEASE_OWNER_SEPARATOR",
    "UniversalWorkerLeasingError",
    "UniversalWorkerLeaseState",
    "UniversalWorkerLease",
    "UniversalWorkerLeaseRelease",
    "normalize_universal_worker_lease_id",
    "normalize_universal_worker_lease_timestamp",
    "create_universal_worker_lease_owner",
    "acquire_universal_worker_lease",
    "evaluate_universal_worker_lease_state",
    "renew_universal_worker_lease",
    "release_universal_worker_lease",
    "explain_universal_worker_leasing_v1",
]
