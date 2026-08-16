from __future__ import annotations

import ast
import hashlib
import importlib
import sys
from pathlib import Path


ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
)

LEASING_PATH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_worker"
    / "leasing.py"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_4_1_4_worker_leasing_initial_implementation.txt"
)


PROTECTED = {
    "worker_registration": (
        ROOT / "backend/server/runtime/universal_worker/registration.py",
        "00F0D6E620E24A7433C880B722E023AF3C2121563F8E18DFA9979E0F06A36D64",
    ),

    "worker_discovery": (
        ROOT / "backend/server/runtime/universal_worker/discovery.py",
        "DFCAB9080982C8D5E099A40C903F7B4140B0860053DB73CB77B30B966788A228",
    ),

    "worker_assignment": (
        ROOT / "backend/server/runtime/universal_worker/assignment.py",
        "609D3077B84C1791262F8ACA6BD268FD40436DF7775ACB3E9E726BCFC9715F56",
    ),

    "queue_certification": (
        ROOT / "backend/server/runtime/universal_queue/certification.py",
        "6ED39655147D2B331E02101F5EA23E68CF71447353C0D294E170281AE40C0D4C",
    ),

    "job_contract": (
        ROOT / "backend/server/runtime/universal_jobs/contract.py",
        "82225461C792EDA7193D2FA3B59E39FF3823906365CD0FBCD5E2915673EE23D1",
    ),

    "job_status": (
        ROOT / "backend/server/runtime/universal_jobs/status.py",
        "4636EF770005A6CCC84A37596622880C2244D4C12FFDEDAAC02078C20AA29EEE",
    ),

    "existing_runtime_worker": (
        ROOT / "backend/server/runtime/universal_runtime_worker_v1.py",
        "6CC4EC122C6B8D1E21AFF8B55CAA786148D7E1FC75D840DAE9240FFB69634D44",
    ),

    "runtime_registration": (
        ROOT / "backend/server/runtime/universal_runtime_registration.py",
        "CBFBB0DA1E5D05A040AEC6F60B1251331431956106D90335A8C110FDBCA632E5",
    ),

    "runtime_infrastructure": (
        ROOT / "backend/server/runtime/universal_runtime_infrastructure.py",
        "EE6590D044C6AA20762F2A37AE86B7FFD3300B62610BC2B1F2657D9334CB311C",
    ),

    "orchestration_queue": (
        ROOT / "backend/server/orchestration/queue.py",
        "76F8F7E66578E2B8A4A1FF3BB420B6340A7A1D1D661EB66B7C21987CF3845A97",
    ),

    "orchestration_service": (
        ROOT / "backend/server/orchestration/service.py",
        "4C31CFC6FFDC9AFA8EA6AD8F43ADBC117F8A6D0193ABF045DBFBA39D6EB799BA",
    ),
}


def ast_sha(
    path: Path,
) -> str:

    source = path.read_text(
        encoding="utf-8-sig"
    )

    tree = ast.parse(source)

    canonical = ast.dump(
        tree,
        annotate_fields=True,
        include_attributes=False,
    )

    return hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest().upper()


for name, (
    path,
    expected,
) in PROTECTED.items():

    actual = ast_sha(
        path
    )

    if actual != expected:

        raise SystemExit(
            (
                "Protected authority mismatch before "
                "4.1.4 implementation: "
                + name
                + "\nEXPECTED: "
                + expected
                + "\nACTUAL:   "
                + actual
            )
        )


SOURCE = r'''from __future__ import annotations

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
'''


ast.parse(
    SOURCE
)

LEASING_PATH.write_text(
    SOURCE,
    encoding="utf-8",
)


sys.path.insert(
    0,
    str(ROOT),
)

registration = importlib.import_module(
    "backend.server.runtime.universal_worker.registration"
)

assignment = importlib.import_module(
    "backend.server.runtime.universal_worker.assignment"
)

leasing_name = (
    "backend.server.runtime."
    "universal_worker.leasing"
)

sys.modules.pop(
    leasing_name,
    None,
)

leasing = importlib.import_module(
    leasing_name
)


checks = []


def check(
    name,
    condition,
    detail="",
):

    checks.append(
        (
            name,
            bool(condition),
            str(detail),
        )
    )


check(
    "version",
    leasing.UNIVERSAL_WORKER_LEASING_VERSION
    == "universal_worker_leasing_v4.1.4",
)

check(
    "lease_schema",
    leasing.UNIVERSAL_WORKER_LEASE_SCHEMA_VERSION
    == "universal_worker_lease_schema_v1",
)

check(
    "release_schema",
    leasing.UNIVERSAL_WORKER_LEASE_RELEASE_SCHEMA_VERSION
    == "universal_worker_lease_release_schema_v1",
)


def worker(
    worker_id,
    instance_id,
):

    return (
        registration.create_universal_worker_registration(
            worker_id=worker_id,
            worker_type="general",
            worker_instance_id=instance_id,
            runtime_version="runtime-v1",
            host_id="host-a",
            registered_at="2026-08-15T20:00:00Z",
        )
    )


assigned = assignment.assign_universal_worker(
    job_id="job-001",
    eligible_workers=(
        worker(
            "worker-a",
            "instance-001",
        ),
    ),
)


lease = leasing.acquire_universal_worker_lease(
    assignment=assigned,
    lease_id=" lease-001 ",
    lease_started_at="2026-08-15T20:00:00Z",
    lease_expires_at="2026-08-15T20:05:00Z",
)


check(
    "lease_job_id",
    lease.job_id
    == "job-001",
)

check(
    "lease_owner",
    lease.lease_owner
    == "worker-a::instance-001",
)

check(
    "lease_identity",
    lease.worker_identity
    == (
        "worker-a",
        "instance-001",
    ),
)

check(
    "lease_id",
    lease.lease_id
    == "lease-001",
)

check(
    "started_at",
    lease.lease_started_at
    == "2026-08-15T20:00:00.000000Z",
)

check(
    "expires_at",
    lease.lease_expires_at
    == "2026-08-15T20:05:00.000000Z",
)

check(
    "job_fields_exact",
    dict(
        lease.to_job_lease_fields()
    )
    == {
        "lease_owner":
            "worker-a::instance-001",
        "lease_id":
            "lease-001",
        "lease_started_at":
            "2026-08-15T20:00:00.000000Z",
        "lease_expires_at":
            "2026-08-15T20:05:00.000000Z",
    },
)


check(
    "active_before_expiration",
    leasing.evaluate_universal_worker_lease_state(
        lease=lease,
        evaluation_at="2026-08-15T20:04:59Z",
    )
    is leasing.UniversalWorkerLeaseState.ACTIVE,
)

check(
    "expired_at_boundary",
    leasing.evaluate_universal_worker_lease_state(
        lease=lease,
        evaluation_at="2026-08-15T20:05:00Z",
    )
    is leasing.UniversalWorkerLeaseState.EXPIRED,
)

check(
    "expired_after_boundary",
    leasing.evaluate_universal_worker_lease_state(
        lease=lease,
        evaluation_at="2026-08-15T20:05:01Z",
    )
    is leasing.UniversalWorkerLeaseState.EXPIRED,
)


renewed = leasing.renew_universal_worker_lease(
    lease=lease,
    expected_lease_owner=lease.lease_owner,
    expected_lease_id=lease.lease_id,
    renewed_at="2026-08-15T20:04:00Z",
    new_lease_expires_at="2026-08-15T20:10:00Z",
)


check(
    "renewal_same_job",
    renewed.job_id
    == lease.job_id,
)

check(
    "renewal_same_owner",
    renewed.lease_owner
    == lease.lease_owner,
)

check(
    "renewal_same_lease_id",
    renewed.lease_id
    == lease.lease_id,
)

check(
    "renewal_same_started_at",
    renewed.lease_started_at
    == lease.lease_started_at,
)

check(
    "renewal_extended",
    renewed.lease_expires_at
    == "2026-08-15T20:10:00.000000Z",
)


release = leasing.release_universal_worker_lease(
    lease=renewed,
    expected_lease_owner=renewed.lease_owner,
    expected_lease_id=renewed.lease_id,
    released_at="2026-08-15T20:06:00Z",
)


check(
    "release_job",
    release.job_id
    == "job-001",
)

check(
    "release_owner",
    release.lease_owner
    == renewed.lease_owner,
)

check(
    "release_id",
    release.lease_id
    == renewed.lease_id,
)

check(
    "release_time",
    release.released_at
    == "2026-08-15T20:06:00.000000Z",
)


# NO_ASSIGNMENT cannot lease.

no_assignment = (
    assignment.assign_universal_worker(
        job_id="job-empty",
        eligible_workers=(),
    )
)


try:

    leasing.acquire_universal_worker_lease(
        assignment=no_assignment,
        lease_id="lease-x",
        lease_started_at="2026-08-15T20:00:00Z",
        lease_expires_at="2026-08-15T20:05:00Z",
    )

except leasing.UniversalWorkerLeasingError as exc:

    rejected = (
        exc.code
        == "worker_assignment_required"
    )

else:

    rejected = False


check(
    "no_assignment_cannot_lease",
    rejected,
)


# Existing lease conflict.

try:

    leasing.acquire_universal_worker_lease(
        assignment=assigned,
        lease_id="lease-002",
        lease_started_at="2026-08-15T20:06:00Z",
        lease_expires_at="2026-08-15T20:11:00Z",
        existing_lease=lease,
    )

except leasing.UniversalWorkerLeasingError as exc:

    conflict = (
        exc.code
        == "lease_conflict"
    )

else:

    conflict = False


check(
    "existing_lease_conflict",
    conflict,
)


# Renewal mismatch.

try:

    leasing.renew_universal_worker_lease(
        lease=lease,
        expected_lease_owner="worker-x::instance-x",
        expected_lease_id=lease.lease_id,
        renewed_at="2026-08-15T20:04:00Z",
        new_lease_expires_at="2026-08-15T20:10:00Z",
    )

except leasing.UniversalWorkerLeasingError as exc:

    rejected = (
        exc.code
        == "lease_owner_mismatch"
    )

else:

    rejected = False


check(
    "renew_owner_mismatch",
    rejected,
)


try:

    leasing.renew_universal_worker_lease(
        lease=lease,
        expected_lease_owner=lease.lease_owner,
        expected_lease_id="wrong",
        renewed_at="2026-08-15T20:04:00Z",
        new_lease_expires_at="2026-08-15T20:10:00Z",
    )

except leasing.UniversalWorkerLeasingError as exc:

    rejected = (
        exc.code
        == "lease_id_mismatch"
    )

else:

    rejected = False


check(
    "renew_id_mismatch",
    rejected,
)


# Expired lease cannot renew.

try:

    leasing.renew_universal_worker_lease(
        lease=lease,
        expected_lease_owner=lease.lease_owner,
        expected_lease_id=lease.lease_id,
        renewed_at="2026-08-15T20:05:00Z",
        new_lease_expires_at="2026-08-15T20:10:00Z",
    )

except leasing.UniversalWorkerLeasingError as exc:

    rejected = (
        exc.code
        == "expired_lease_cannot_renew"
    )

else:

    rejected = False


check(
    "expired_cannot_renew",
    rejected,
)


# Release mismatch.

try:

    leasing.release_universal_worker_lease(
        lease=lease,
        expected_lease_owner="worker-x::instance-x",
        expected_lease_id=lease.lease_id,
        released_at="2026-08-15T20:03:00Z",
    )

except leasing.UniversalWorkerLeasingError as exc:

    rejected = (
        exc.code
        == "lease_owner_mismatch"
    )

else:

    rejected = False


check(
    "release_owner_mismatch",
    rejected,
)


# Immutability.

for obj, field_name in (
    (
        lease,
        "lease_id",
    ),
    (
        release,
        "released_at",
    ),
):

    try:

        setattr(
            obj,
            field_name,
            None,
        )

    except Exception:

        immutable = True

    else:

        immutable = False

    check(
        "immutable_"
        + type(obj).__name__,
        immutable,
    )


# Explanation.

explanation = (
    leasing.explain_universal_worker_leasing_v1()
)


check(
    "explanation_phase",
    explanation.get("phase")
    == "4.1.4",
)

check(
    "canonical_fields",
    tuple(
        explanation.get(
            "canonical_job_fields"
        )
    )
    == (
        "lease_owner",
        "lease_id",
        "lease_started_at",
        "lease_expires_at",
    ),
)

check(
    "owner_identity_rule",
    "worker_id::worker_instance_id"
    in explanation.get(
        "owner_rule",
        "",
    ),
)

check(
    "caller_timestamp_rule",
    "caller-supplied"
    in explanation.get(
        "timestamp_rule",
        "",
    ),
)

check(
    "no_job_mutation_rule",
    "never mutates or persists UniversalJob"
    in explanation.get(
        "persistence_rule",
        "",
    ),
)

check(
    "recovery_separate",
    "does not"
    in explanation.get(
        "recovery_boundary",
        "",
    ),
)


required_prohibitions = (
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
)


prohibitions = tuple(
    explanation.get(
        "prohibitions"
    )
    or ()
)


for index, item in enumerate(
    required_prohibitions,
    start=1,
):

    check(
        "prohibition_"
        + str(index),
        item in prohibitions,
        item,
    )


source = LEASING_PATH.read_text(
    encoding="utf-8-sig"
)

tree = ast.parse(
    source
)


backend_imports = []


for node in ast.walk(
    tree
):

    if isinstance(
        node,
        ast.ImportFrom,
    ):

        module_name = (
            node.module
            or ""
        )

        if module_name.startswith(
            "backend.server"
        ):

            backend_imports.append(
                module_name
            )


check(
    "only_assignment_backend_import",
    backend_imports
    == [
        "backend.server.runtime.universal_worker.assignment"
    ],
    backend_imports,
)


forbidden_names = {
    "open",
    "read_text",
    "write_text",
    "mkdir",
    "unlink",
    "remove",
    "uuid4",
    "datetime.now",
    "utcnow",
    "dequeue_job",
    "claim_job",
    "enqueue_job",
    "save_job",
    "get_job",
    "dispatch_job",
    "execute_job",
    "dispatch_registered_runtime_handler",
    "get_runtime_state_store_registry",
    "worker_heartbeat",
}


forbidden_calls = []


for node in ast.walk(
    tree
):

    if not isinstance(
        node,
        ast.Call,
    ):

        continue

    if isinstance(
        node.func,
        ast.Name,
    ):

        name = (
            node.func.id
        )

    elif isinstance(
        node.func,
        ast.Attribute,
    ):

        name = (
            node.func.attr
        )

    else:

        continue

    if name in forbidden_names:

        forbidden_calls.append(
            (
                name,
                getattr(
                    node,
                    "lineno",
                    0,
                ),
            )
        )


check(
    "no_forbidden_calls",
    not forbidden_calls,
    forbidden_calls,
)


for name, (
    path,
    expected,
) in PROTECTED.items():

    actual = ast_sha(
        path
    )

    check(
        "protected_"
        + name,
        actual
        == expected,
        actual,
    )


leasing_ast = ast_sha(
    LEASING_PATH
)


check(
    "leasing_ast_generated",
    len(
        leasing_ast
    )
    == 64,
    leasing_ast,
)


passed = sum(
    1
    for _, ok, _
    in checks
    if ok
)

total = len(
    checks
)


lines = [
    (
        "PHASE 4.1.4 — UNIVERSAL WORKER "
        "LEASING INITIAL IMPLEMENTATION"
    ),
    "=" * 112,
    "",
    (
        "WORKER LEASING AST SHA256: "
        + leasing_ast
    ),
    "",
]


for index, (
    name,
    ok,
    detail,
) in enumerate(
    checks,
    start=1,
):

    lines.append(
        (
            f"{index}. {name}: "
            f"{'PASS' if ok else 'FAIL'}"
        )
    )

    if detail:

        lines.append(
            "   "
            + detail
        )


lines.extend(
    [
        "",
        "=" * 112,
        (
            "INITIAL WORKER LEASING RESULT: "
            + (
                "PASS"
                if passed == total
                else "FAIL"
            )
        ),
        (
            "CHECKS PASSED: "
            + str(passed)
            + "/"
            + str(total)
        ),
        "",
        "4.1.1 WORKER REGISTRATION MODIFIED: NO",
        "4.1.2 WORKER DISCOVERY MODIFIED: NO",
        "4.1.3 WORKER ASSIGNMENT MODIFIED: NO",
        "QUEUE INFRASTRUCTURE MODIFIED: NO",
        "UNIVERSAL JOB CONTRACT MODIFIED: NO",
        "UNIVERSAL JOB STATUS MODIFIED: NO",
        "BODY STORE LEASING MODIFIED: NO",
        "EXISTING UNIVERSAL RUNTIME WORKER MODIFIED: NO",
        "RUNTIME STATE STORE ACCESSED: NO",
        "ORCHESTRATION MODIFIED: NO",
        "LEASE PERSISTED: NO",
        "LEASE_ID GENERATED INTERNALLY: NO",
        "WALL-CLOCK TIME READ: NO",
        "UNIVERSAL JOB MUTATED: NO",
        "JOB STATUS MUTATED: NO",
        "JOB DEQUEUED: NO",
        "JOB CLAIMED: NO",
        "JOB DISPATCHED: NO",
        "JOB EXECUTED: NO",
        "EXPIRED JOB REQUEUED: NO",
        "WORKER RECOVERY PERFORMED: NO",
        "",
        (
            "STATUS: INITIAL IMPLEMENTATION PASS "
            "— ADVERSARIAL REGRESSION REQUIRED"
            if passed == total
            else
            "STATUS: INITIAL IMPLEMENTATION FAILED"
        ),
    ]
)


REPORT_PATH.write_text(
    "\n".join(lines),
    encoding="utf-8",
)

print(
    "\n".join(lines)
)


if passed != total:

    raise SystemExit(
        "Phase 4.1.4 Worker Leasing initial implementation failed."
    )
