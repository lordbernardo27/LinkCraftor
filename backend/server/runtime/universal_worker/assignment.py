from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Iterable, Mapping

from backend.server.runtime.universal_worker.registration import (
    UniversalWorkerRegistration,
)


UNIVERSAL_WORKER_ASSIGNMENT_VERSION = (
    "universal_worker_assignment_v4.1.3"
)

UNIVERSAL_WORKER_ASSIGNMENT_RESULT_SCHEMA_VERSION = (
    "universal_worker_assignment_result_schema_v1"
)

MAX_UNIVERSAL_WORKER_ASSIGNMENT_JOB_ID_LENGTH = 200


class UniversalWorkerAssignmentError(
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


class UniversalWorkerAssignmentStatus(
    str,
    Enum,
):

    ASSIGNED = "ASSIGNED"
    NO_ASSIGNMENT = "NO_ASSIGNMENT"


def normalize_universal_worker_assignment_job_id(
    value: Any,
) -> str:

    if not isinstance(
        value,
        str,
    ):

        raise UniversalWorkerAssignmentError(
            "job_id must be a string.",
            code="invalid_assignment_job_id_type",
            value=value,
        )

    normalized = value.strip()

    if not normalized:

        raise UniversalWorkerAssignmentError(
            "job_id must not be empty.",
            code="empty_assignment_job_id",
            value=value,
        )

    if (
        len(normalized)
        > MAX_UNIVERSAL_WORKER_ASSIGNMENT_JOB_ID_LENGTH
    ):

        raise UniversalWorkerAssignmentError(
            (
                "job_id exceeds maximum length "
                f"{MAX_UNIVERSAL_WORKER_ASSIGNMENT_JOB_ID_LENGTH}."
            ),
            code="assignment_job_id_too_long",
            value=value,
        )

    return normalized


def _validate_worker(
    value: Any,
) -> UniversalWorkerRegistration:

    if not isinstance(
        value,
        UniversalWorkerRegistration,
    ):

        raise UniversalWorkerAssignmentError(
            (
                "Every eligible worker must be a "
                "UniversalWorkerRegistration."
            ),
            code="invalid_assignment_worker",
            value=value,
        )

    return value


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalWorkerAssignmentResult:

    job_id: str
    status: UniversalWorkerAssignmentStatus
    worker: UniversalWorkerRegistration | None
    candidate_count: int

    schema_version: str = (
        UNIVERSAL_WORKER_ASSIGNMENT_RESULT_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        object.__setattr__(
            self,
            "job_id",
            normalize_universal_worker_assignment_job_id(
                self.job_id
            ),
        )

        if not isinstance(
            self.status,
            UniversalWorkerAssignmentStatus,
        ):

            raise UniversalWorkerAssignmentError(
                (
                    "status must be a "
                    "UniversalWorkerAssignmentStatus."
                ),
                code="invalid_assignment_status",
                value=self.status,
            )

        if (
            type(self.candidate_count)
            is not int
            or self.candidate_count < 0
        ):

            raise UniversalWorkerAssignmentError(
                (
                    "candidate_count must be a "
                    "non-negative integer."
                ),
                code="invalid_assignment_candidate_count",
                value=self.candidate_count,
            )

        if (
            self.status
            is UniversalWorkerAssignmentStatus.ASSIGNED
        ):

            if self.worker is None:

                raise UniversalWorkerAssignmentError(
                    (
                        "ASSIGNED requires a selected "
                        "worker."
                    ),
                    code="assigned_worker_required",
                    value=self.worker,
                )

            _validate_worker(
                self.worker
            )

            if self.candidate_count < 1:

                raise UniversalWorkerAssignmentError(
                    (
                        "ASSIGNED requires candidate_count "
                        "of at least one."
                    ),
                    code="assigned_candidate_count_invalid",
                    value=self.candidate_count,
                )

        else:

            if self.worker is not None:

                raise UniversalWorkerAssignmentError(
                    (
                        "NO_ASSIGNMENT must not contain "
                        "a worker."
                    ),
                    code="no_assignment_worker_forbidden",
                    value=self.worker,
                )

            if self.candidate_count != 0:

                raise UniversalWorkerAssignmentError(
                    (
                        "NO_ASSIGNMENT requires "
                        "candidate_count=0."
                    ),
                    code=(
                        "no_assignment_candidate_count_"
                        "must_be_zero"
                    ),
                    value=self.candidate_count,
                )

        if (
            self.schema_version
            != UNIVERSAL_WORKER_ASSIGNMENT_RESULT_SCHEMA_VERSION
        ):

            raise UniversalWorkerAssignmentError(
                (
                    "Invalid Worker Assignment "
                    "result schema_version."
                ),
                code=(
                    "invalid_worker_assignment_"
                    "result_schema_version"
                ),
                value=self.schema_version,
            )

    @property
    def assigned(
        self,
    ) -> bool:

        return (
            self.status
            is UniversalWorkerAssignmentStatus.ASSIGNED
        )

    @property
    def worker_id(
        self,
    ) -> str | None:

        if self.worker is None:

            return None

        return self.worker.worker_id

    @property
    def worker_instance_id(
        self,
    ) -> str | None:

        if self.worker is None:

            return None

        return self.worker.worker_instance_id

    @property
    def worker_identity(
        self,
    ) -> tuple[str, str] | None:

        if self.worker is None:

            return None

        return self.worker.canonical_identity


def assign_universal_worker(
    *,
    job_id: str,
    eligible_workers: Iterable[
        UniversalWorkerRegistration
    ],
) -> UniversalWorkerAssignmentResult:

    canonical_job_id = (
        normalize_universal_worker_assignment_job_id(
            job_id
        )
    )

    if isinstance(
        eligible_workers,
        (
            str,
            bytes,
            Mapping,
        ),
    ):

        raise UniversalWorkerAssignmentError(
            (
                "eligible_workers must be an iterable "
                "of UniversalWorkerRegistration records."
            ),
            code="invalid_eligible_workers",
            value=eligible_workers,
        )

    try:

        materialized = tuple(
            eligible_workers
        )

    except TypeError as exc:

        raise UniversalWorkerAssignmentError(
            (
                "eligible_workers must be an iterable "
                "of UniversalWorkerRegistration records."
            ),
            code="invalid_eligible_workers",
            value=eligible_workers,
        ) from exc

    validated = []

    seen_identities = set()

    for worker in materialized:

        validated_worker = (
            _validate_worker(
                worker
            )
        )

        identity = (
            validated_worker.canonical_identity
        )

        if identity in seen_identities:

            raise UniversalWorkerAssignmentError(
                (
                    "Duplicate eligible worker "
                    "identity."
                ),
                code=(
                    "duplicate_eligible_worker_"
                    "identity"
                ),
                value=identity,
            )

        seen_identities.add(
            identity
        )

        validated.append(
            validated_worker
        )

    if not validated:

        return UniversalWorkerAssignmentResult(
            job_id=canonical_job_id,
            status=(
                UniversalWorkerAssignmentStatus.NO_ASSIGNMENT
            ),
            worker=None,
            candidate_count=0,
        )

    ordered = tuple(
        sorted(
            validated,
            key=lambda worker: (
                worker.worker_id,
                worker.worker_instance_id,
            ),
        )
    )

    selected = ordered[0]

    return UniversalWorkerAssignmentResult(
        job_id=canonical_job_id,
        status=(
            UniversalWorkerAssignmentStatus.ASSIGNED
        ),
        worker=selected,
        candidate_count=len(
            ordered
        ),
    )


def explain_universal_worker_assignment_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "4.1.3",

            "component":
                "Universal Worker Assignment",

            "version":
                UNIVERSAL_WORKER_ASSIGNMENT_VERSION,

            "result_schema_version":
                UNIVERSAL_WORKER_ASSIGNMENT_RESULT_SCHEMA_VERSION,

            "input_rule": (
                "4.1.3 consumes a canonical job_id and "
                "caller-supplied already-eligible "
                "UniversalWorkerRegistration records"
            ),

            "eligibility_rule": (
                "4.1.3 does not determine eligibility; "
                "the caller owns construction of the "
                "eligible worker population"
            ),

            "selection_rule": (
                "when eligible workers exist, select the "
                "lexicographically first worker by "
                "worker_id then worker_instance_id"
            ),

            "empty_rule": (
                "an empty eligible worker population "
                "produces NO_ASSIGNMENT"
            ),

            "duplicate_rule": (
                "duplicate (worker_id, worker_instance_id) "
                "eligible worker identities are rejected"
            ),

            "job_evidence_rule": (
                "job_id is the only job evidence consumed "
                "by the assignment authority"
            ),

            "meaning": (
                "ASSIGNED is a deterministic selection "
                "decision only; it does not create runtime "
                "ownership of the job"
            ),

            "purity_rule": (
                "Worker Assignment is deterministic over "
                "caller-supplied evidence and performs no "
                "state lookup, mutation or persistence"
            ),

            "prohibitions": (
                "does not discover workers",
                "does not determine worker health",
                "does not read worker heartbeats",
                "does not detect stale workers",
                "does not inspect worker pools",
                "does not inspect worker capabilities",
                "does not inspect worker capacity",
                "does not maintain round-robin state",
                "does not persist assignments",
                "does not write worker_id into job metadata",
                "does not mutate job status",
                "does not transition jobs to RUNNING",
                "does not claim jobs",
                "does not dequeue jobs",
                "does not acquire leases",
                "does not renew leases",
                "does not release leases",
                "does not dispatch jobs",
                "does not execute jobs",
                "does not access orchestration",
                "does not access Runtime State Store",
                "does not mutate Queue Infrastructure",
                "does not register runtime handlers",
                "does not perform filesystem I/O",
                "does not perform network I/O",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_WORKER_ASSIGNMENT_VERSION",
    "UNIVERSAL_WORKER_ASSIGNMENT_RESULT_SCHEMA_VERSION",
    "MAX_UNIVERSAL_WORKER_ASSIGNMENT_JOB_ID_LENGTH",
    "UniversalWorkerAssignmentError",
    "UniversalWorkerAssignmentStatus",
    "UniversalWorkerAssignmentResult",
    "normalize_universal_worker_assignment_job_id",
    "assign_universal_worker",
    "explain_universal_worker_assignment_v1",
]
