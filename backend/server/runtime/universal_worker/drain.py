from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from backend.server.runtime.universal_worker.registration import (
    UniversalWorkerRegistration,
    normalize_universal_worker_id,
    normalize_universal_worker_instance_id,
    normalize_universal_worker_type,
)


UNIVERSAL_WORKER_DRAIN_VERSION = (
    "universal_worker_drain_v4.1.12"
)

UNIVERSAL_WORKER_DRAIN_EVIDENCE_SCHEMA_VERSION = (
    "universal_worker_drain_evidence_schema_v1"
)

UNIVERSAL_WORKER_DRAIN_RESULT_SCHEMA_VERSION = (
    "universal_worker_drain_result_schema_v1"
)

MAX_UNIVERSAL_WORKER_DRAIN_COUNT = (
    2_147_483_647
)

UNIVERSAL_WORKER_DRAIN_IDENTITY_SEPARATOR = (
    "::"
)


class UniversalWorkerDrainError(
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


class UniversalWorkerDrainState(
    str,
    Enum,
):

    NOT_REQUESTED = "NOT_REQUESTED"

    DRAINING = "DRAINING"

    DRAINED = "DRAINED"


def normalize_universal_worker_drain_requested(
    value: Any,
) -> bool:

    if type(value) is not bool:

        raise UniversalWorkerDrainError(
            "drain_requested must be bool.",
            code="invalid_worker_drain_requested",
            value=value,
        )

    return value


def normalize_universal_worker_drain_count(
    value: Any,
    *,
    field_name: str,
) -> int:

    if (
        type(value) is not int
        or
        value < 0
    ):

        raise UniversalWorkerDrainError(
            (
                field_name
                + " must be an integer "
                "greater than or equal to zero."
            ),
            code="invalid_worker_drain_count",
            value={
                "field_name":
                    field_name,

                "value":
                    value,
            },
        )

    if (
        value
        > MAX_UNIVERSAL_WORKER_DRAIN_COUNT
    ):

        raise UniversalWorkerDrainError(
            (
                field_name
                + " exceeds the supported maximum."
            ),
            code="worker_drain_count_too_large",
            value={
                "field_name":
                    field_name,

                "value":
                    value,
            },
        )

    return value


def _validate_registration(
    value: Any,
) -> UniversalWorkerRegistration:

    if not isinstance(
        value,
        UniversalWorkerRegistration,
    ):

        raise UniversalWorkerDrainError(
            (
                "registration must be canonical "
                "UniversalWorkerRegistration."
            ),
            code="invalid_worker_drain_registration",
            value=value,
        )

    return value


def decide_universal_worker_drain_state(
    *,
    drain_requested: bool,
    active_work_count: int,
    active_lease_count: int,
) -> UniversalWorkerDrainState:

    requested = (
        normalize_universal_worker_drain_requested(
            drain_requested
        )
    )

    work_count = (
        normalize_universal_worker_drain_count(
            active_work_count,
            field_name="active_work_count",
        )
    )

    lease_count = (
        normalize_universal_worker_drain_count(
            active_lease_count,
            field_name="active_lease_count",
        )
    )

    if not requested:

        return (
            UniversalWorkerDrainState.NOT_REQUESTED
        )

    if (
        work_count > 0
        or
        lease_count > 0
    ):

        return (
            UniversalWorkerDrainState.DRAINING
        )

    return (
        UniversalWorkerDrainState.DRAINED
    )


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalWorkerDrainEvidence:

    worker_id: str

    worker_instance_id: str

    worker_type: str

    drain_requested: bool

    active_work_count: int

    active_lease_count: int

    schema_version: str = (
        UNIVERSAL_WORKER_DRAIN_EVIDENCE_SCHEMA_VERSION
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

            worker_instance_id = (
                normalize_universal_worker_instance_id(
                    self.worker_instance_id
                )
            )

            worker_type = (
                normalize_universal_worker_type(
                    self.worker_type
                )
            )

        except Exception as exc:

            raise UniversalWorkerDrainError(
                (
                    "Invalid canonical worker identity "
                    "in drain evidence."
                ),
                code="invalid_worker_drain_identity",
                value={
                    "worker_id":
                        self.worker_id,

                    "worker_instance_id":
                        self.worker_instance_id,

                    "worker_type":
                        self.worker_type,
                },
            ) from exc

        requested = (
            normalize_universal_worker_drain_requested(
                self.drain_requested
            )
        )

        work_count = (
            normalize_universal_worker_drain_count(
                self.active_work_count,
                field_name="active_work_count",
            )
        )

        lease_count = (
            normalize_universal_worker_drain_count(
                self.active_lease_count,
                field_name="active_lease_count",
            )
        )

        if (
            self.schema_version
            != UNIVERSAL_WORKER_DRAIN_EVIDENCE_SCHEMA_VERSION
        ):

            raise UniversalWorkerDrainError(
                (
                    "Invalid Worker Drain Evidence "
                    "schema_version."
                ),
                code=(
                    "invalid_worker_drain_evidence_"
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
            "drain_requested",
            requested,
        )

        object.__setattr__(
            self,
            "active_work_count",
            work_count,
        )

        object.__setattr__(
            self,
            "active_lease_count",
            lease_count,
        )

    @property
    def worker_identity(
        self,
    ) -> str:

        return (
            self.worker_id
            + UNIVERSAL_WORKER_DRAIN_IDENTITY_SEPARATOR
            + self.worker_instance_id
        )


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalWorkerDrainResult:

    worker_id: str

    worker_instance_id: str

    worker_type: str

    drain_requested: bool

    active_work_count: int

    active_lease_count: int

    state: UniversalWorkerDrainState

    schema_version: str = (
        UNIVERSAL_WORKER_DRAIN_RESULT_SCHEMA_VERSION
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

            worker_instance_id = (
                normalize_universal_worker_instance_id(
                    self.worker_instance_id
                )
            )

            worker_type = (
                normalize_universal_worker_type(
                    self.worker_type
                )
            )

        except Exception as exc:

            raise UniversalWorkerDrainError(
                (
                    "Invalid canonical worker identity "
                    "in drain result."
                ),
                code="invalid_worker_drain_result_identity",
                value={
                    "worker_id":
                        self.worker_id,

                    "worker_instance_id":
                        self.worker_instance_id,

                    "worker_type":
                        self.worker_type,
                },
            ) from exc

        requested = (
            normalize_universal_worker_drain_requested(
                self.drain_requested
            )
        )

        work_count = (
            normalize_universal_worker_drain_count(
                self.active_work_count,
                field_name="active_work_count",
            )
        )

        lease_count = (
            normalize_universal_worker_drain_count(
                self.active_lease_count,
                field_name="active_lease_count",
            )
        )

        if not isinstance(
            self.state,
            UniversalWorkerDrainState,
        ):

            raise UniversalWorkerDrainError(
                "Invalid Worker Drain state.",
                code="invalid_worker_drain_state",
                value=self.state,
            )

        expected_state = (
            decide_universal_worker_drain_state(
                drain_requested=requested,
                active_work_count=work_count,
                active_lease_count=lease_count,
            )
        )

        if self.state is not expected_state:

            raise UniversalWorkerDrainError(
                "Inconsistent Worker Drain state.",
                code="inconsistent_worker_drain_state",
                value={
                    "expected":
                        expected_state.value,

                    "actual":
                        self.state.value,
                },
            )

        if (
            self.schema_version
            != UNIVERSAL_WORKER_DRAIN_RESULT_SCHEMA_VERSION
        ):

            raise UniversalWorkerDrainError(
                (
                    "Invalid Worker Drain Result "
                    "schema_version."
                ),
                code=(
                    "invalid_worker_drain_result_"
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
            "drain_requested",
            requested,
        )

        object.__setattr__(
            self,
            "active_work_count",
            work_count,
        )

        object.__setattr__(
            self,
            "active_lease_count",
            lease_count,
        )

    @property
    def worker_identity(
        self,
    ) -> str:

        return (
            self.worker_id
            + UNIVERSAL_WORKER_DRAIN_IDENTITY_SEPARATOR
            + self.worker_instance_id
        )

    @property
    def drain_complete(
        self,
    ) -> bool:

        return (
            self.state
            is UniversalWorkerDrainState.DRAINED
        )

    @property
    def accepts_new_work(
        self,
    ) -> bool:

        return (
            self.state
            is UniversalWorkerDrainState.NOT_REQUESTED
        )

    @property
    def is_draining(
        self,
    ) -> bool:

        return (
            self.state
            is UniversalWorkerDrainState.DRAINING
        )

    @property
    def is_drained(
        self,
    ) -> bool:

        return (
            self.state
            is UniversalWorkerDrainState.DRAINED
        )


def create_universal_worker_drain_evidence(
    *,
    registration: UniversalWorkerRegistration,
    drain_requested: bool,
    active_work_count: int,
    active_lease_count: int,
) -> UniversalWorkerDrainEvidence:

    resolved_registration = (
        _validate_registration(
            registration
        )
    )

    return UniversalWorkerDrainEvidence(
        worker_id=(
            resolved_registration.worker_id
        ),
        worker_instance_id=(
            resolved_registration.worker_instance_id
        ),
        worker_type=(
            resolved_registration.worker_type
        ),
        drain_requested=drain_requested,
        active_work_count=active_work_count,
        active_lease_count=active_lease_count,
    )


def evaluate_universal_worker_drain(
    *,
    evidence: UniversalWorkerDrainEvidence,
) -> UniversalWorkerDrainResult:

    if not isinstance(
        evidence,
        UniversalWorkerDrainEvidence,
    ):

        raise UniversalWorkerDrainError(
            (
                "evidence must be canonical "
                "UniversalWorkerDrainEvidence."
            ),
            code="invalid_worker_drain_evidence",
            value=evidence,
        )

    state = (
        decide_universal_worker_drain_state(
            drain_requested=evidence.drain_requested,
            active_work_count=evidence.active_work_count,
            active_lease_count=evidence.active_lease_count,
        )
    )

    return UniversalWorkerDrainResult(
        worker_id=evidence.worker_id,
        worker_instance_id=evidence.worker_instance_id,
        worker_type=evidence.worker_type,
        drain_requested=evidence.drain_requested,
        active_work_count=evidence.active_work_count,
        active_lease_count=evidence.active_lease_count,
        state=state,
    )


def explain_universal_worker_drain_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "4.1.12",

            "component":
                "Universal Worker Drain",

            "version":
                UNIVERSAL_WORKER_DRAIN_VERSION,

            "evidence_schema_version":
                UNIVERSAL_WORKER_DRAIN_EVIDENCE_SCHEMA_VERSION,

            "result_schema_version":
                UNIVERSAL_WORKER_DRAIN_RESULT_SCHEMA_VERSION,

            "scope_rule": (
                "4.1.12 is individual-worker drain "
                "authority and is separate from whole-"
                "runtime RuntimeLifecyclePhase.DRAINING"
            ),

            "identity_rule": (
                "drain evidence uses canonical Worker "
                "Registration identity "
                "(worker_id, worker_instance_id)"
            ),

            "input_rule": (
                "caller supplies drain_requested, "
                "active_work_count and active_lease_count"
            ),

            "not_requested_rule": (
                "drain_requested=false yields NOT_REQUESTED "
                "regardless of active work or lease counts"
            ),

            "draining_rule": (
                "drain_requested=true with any active work "
                "or active leases yields DRAINING"
            ),

            "drained_rule": (
                "drain_requested=true with zero active work "
                "and zero active leases yields DRAINED"
            ),

            "new_work_rule": (
                "NOT_REQUESTED does not prohibit new work; "
                "DRAINING and DRAINED produce "
                "accepts_new_work=false evidence"
            ),

            "assignment_boundary": (
                "4.1.12 does not modify or invoke Worker "
                "Assignment; callers may use drain evidence "
                "when constructing the eligible worker set"
            ),

            "leasing_boundary": (
                "4.1.12 does not acquire, renew or release "
                "leases; callers may use drain evidence to "
                "prevent new ownership acquisition"
            ),

            "existing_work_rule": (
                "draining preserves existing work and lease "
                "ownership until external completion"
            ),

            "shutdown_boundary": (
                "4.1.8 Worker Shutdown may consume "
                "drain_complete derived from a DRAINED result"
            ),

            "scaling_boundary": (
                "Worker Scaling remains independent; a "
                "drain result does not perform scale-down"
            ),

            "pool_boundary": (
                "draining or drained state does not remove "
                "Worker Pool membership"
            ),

            "health_stale_recovery_boundary": (
                "drain state is independent from Worker "
                "Health, Stale Worker Detection and "
                "Worker Recovery"
            ),

            "persistence_boundary": (
                "4.1.12 does not persist drain state or "
                "access Runtime State Store"
            ),

            "purity_rule": (
                "Worker Drain is deterministic over "
                "caller-supplied evidence and performs "
                "no external mutation or I/O"
            ),

            "prohibitions": (
                "does not use whole-runtime DRAINING as worker drain state",
                "does not mutate Runtime Lifecycle Manager",
                "does not assign workers",
                "does not modify Assignment eligibility directly",
                "does not acquire worker leases",
                "does not renew worker leases",
                "does not release worker leases",
                "does not cancel running work",
                "does not requeue jobs",
                "does not fail jobs",
                "does not terminate workers",
                "does not perform Worker Shutdown",
                "does not perform Worker Scaling",
                "does not modify Worker Registration",
                "does not deregister workers",
                "does not modify Worker Pool membership",
                "does not determine Worker Health",
                "does not detect stale workers",
                "does not initiate Worker Recovery",
                "does not inspect worker capabilities",
                "does not calculate worker capacity",
                "does not access Queue Infrastructure",
                "does not access orchestration",
                "does not access Runtime State Store",
                "does not persist drain state",
                "does not perform filesystem I/O",
                "does not perform network I/O",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_WORKER_DRAIN_VERSION",
    "UNIVERSAL_WORKER_DRAIN_EVIDENCE_SCHEMA_VERSION",
    "UNIVERSAL_WORKER_DRAIN_RESULT_SCHEMA_VERSION",
    "MAX_UNIVERSAL_WORKER_DRAIN_COUNT",
    "UNIVERSAL_WORKER_DRAIN_IDENTITY_SEPARATOR",
    "UniversalWorkerDrainError",
    "UniversalWorkerDrainState",
    "UniversalWorkerDrainEvidence",
    "UniversalWorkerDrainResult",
    "normalize_universal_worker_drain_requested",
    "normalize_universal_worker_drain_count",
    "decide_universal_worker_drain_state",
    "create_universal_worker_drain_evidence",
    "evaluate_universal_worker_drain",
    "explain_universal_worker_drain_v1",
]
