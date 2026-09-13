from __future__ import annotations

import hashlib

from dataclasses import dataclass
from types import MappingProxyType
from typing import (
    Any,
    Final,
    Mapping,
    Protocol,
    runtime_checkable,
)

from backend.server.runtime.universal_orchestration.state_model import (
    UniversalOrchestrationState,
    UniversalOrchestrationStateSnapshot,
)

from backend.server.runtime.universal_orchestration.progress_tracking import (
    UniversalOrchestrationProgressSnapshot,
)


UNIVERSAL_ORCHESTRATION_PERSISTENCE_INTERFACE_VERSION: Final[str] = (
    "universal_orchestration_persistence_interface_v5.1.14"
)

UNIVERSAL_ORCHESTRATION_PERSISTENCE_RECORD_SCHEMA_VERSION: Final[str] = (
    "universal_orchestration_persistence_record_schema_v1"
)

UNIVERSAL_ORCHESTRATION_PERSISTENCE_RECORD_HASH_ALGORITHM: Final[str] = (
    "sha256"
)


class UniversalOrchestrationPersistenceError(
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


def _require_state_snapshot(
    value: Any,
) -> UniversalOrchestrationStateSnapshot:

    if not isinstance(
        value,
        UniversalOrchestrationStateSnapshot,
    ):

        raise UniversalOrchestrationPersistenceError(
            (
                "state_snapshot must be a "
                "UniversalOrchestrationStateSnapshot."
            ),
            code="invalid_persistence_state_snapshot",
            value=value,
        )

    return value


def _require_progress_snapshot(
    value: Any,
) -> UniversalOrchestrationProgressSnapshot:

    if not isinstance(
        value,
        UniversalOrchestrationProgressSnapshot,
    ):

        raise UniversalOrchestrationPersistenceError(
            (
                "progress_snapshot must be a "
                "UniversalOrchestrationProgressSnapshot."
            ),
            code="invalid_persistence_progress_snapshot",
            value=value,
        )

    return value


def _identity_fingerprint(
    identity: Any,
) -> str:

    fingerprint = getattr(
        identity,
        "identity_fingerprint",
        None,
    )

    if (
        not isinstance(
            fingerprint,
            str,
        )
        or
        not fingerprint.strip()
    ):

        raise UniversalOrchestrationPersistenceError(
            "Orchestration identity fingerprint is invalid.",
            code="invalid_persistence_identity_fingerprint",
            value=fingerprint,
        )

    return (
        fingerprint
        .strip()
        .upper()
    )


def _normalize_optional_record_id(
    value: Any,
) -> str | None:

    if value is None:

        return None

    if not isinstance(
        value,
        str,
    ):

        raise UniversalOrchestrationPersistenceError(
            (
                "previous_record_id must be None or a "
                "64-character SHA-256 hexadecimal string."
            ),
            code="invalid_previous_persistence_record_id",
            value=value,
        )

    normalized = (
        value
        .strip()
        .upper()
    )

    if (
        len(
            normalized
        )
        != 64
        or
        any(
            character
            not in "0123456789ABCDEF"
            for character
            in normalized
        )
    ):

        raise UniversalOrchestrationPersistenceError(
            (
                "previous_record_id must be None or a "
                "64-character SHA-256 hexadecimal string."
            ),
            code="invalid_previous_persistence_record_id",
            value=value,
        )

    return normalized


def _validate_identity_alignment(
    *,
    state_snapshot: UniversalOrchestrationStateSnapshot,
    progress_snapshot: UniversalOrchestrationProgressSnapshot,
) -> None:

    state_identity = (
        _identity_fingerprint(
            state_snapshot.identity
        )
    )

    progress_identity = (
        _identity_fingerprint(
            progress_snapshot.identity
        )
    )

    if (
        state_identity
        !=
        progress_identity
    ):

        raise UniversalOrchestrationPersistenceError(
            (
                "state_snapshot and progress_snapshot must "
                "belong to the same orchestration identity."
            ),
            code="persistence_identity_mismatch",
            value=(
                state_identity,
                progress_identity,
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalOrchestrationPersistenceRecord:

    state_snapshot: UniversalOrchestrationStateSnapshot

    progress_snapshot: UniversalOrchestrationProgressSnapshot

    previous_record_id: str | None = None

    schema_version: str = (
        UNIVERSAL_ORCHESTRATION_PERSISTENCE_RECORD_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        state_snapshot = (
            _require_state_snapshot(
                self.state_snapshot
            )
        )

        progress_snapshot = (
            _require_progress_snapshot(
                self.progress_snapshot
            )
        )

        _validate_identity_alignment(
            state_snapshot=state_snapshot,
            progress_snapshot=progress_snapshot,
        )

        normalized_previous = (
            _normalize_optional_record_id(
                self.previous_record_id
            )
        )

        object.__setattr__(
            self,
            "previous_record_id",
            normalized_previous,
        )

        if (
            self.schema_version
            !=
            UNIVERSAL_ORCHESTRATION_PERSISTENCE_RECORD_SCHEMA_VERSION
        ):

            raise UniversalOrchestrationPersistenceError(
                "Invalid orchestration persistence schema_version.",
                code="invalid_persistence_schema_version",
                value=self.schema_version,
            )

    @property
    def identity(
        self,
    ):

        return (
            self.progress_snapshot.identity
        )

    @property
    def identity_fingerprint(
        self,
    ) -> str:

        return (
            _identity_fingerprint(
                self.identity
            )
        )

    @property
    def orchestration_state(
        self,
    ) -> UniversalOrchestrationState:

        return (
            self.state_snapshot.state
        )

    @property
    def progress_snapshot_id(
        self,
    ) -> str:

        value = (
            self.progress_snapshot.progress_snapshot_id
        )

        if (
            not isinstance(
                value,
                str,
            )
            or
            len(
                value
            )
            != 64
        ):

            raise UniversalOrchestrationPersistenceError(
                "progress_snapshot_id is invalid.",
                code="invalid_persistence_progress_snapshot_id",
                value=value,
            )

        return (
            value.upper()
        )

    @property
    def persistence_record_id(
        self,
    ) -> str:

        previous = (
            self.previous_record_id
            or
            "ROOT"
        )

        material = "|".join(
            (
                "universal_orchestration_persistence_record_v1",
                self.identity_fingerprint,
                self.orchestration_state.value,
                self.progress_snapshot_id,
                previous,
                self.schema_version,
            )
        )

        return hashlib.sha256(
            material.encode(
                "utf-8"
            )
        ).hexdigest().upper()

    @property
    def is_root_record(
        self,
    ) -> bool:

        return (
            self.previous_record_id
            is None
        )

    @property
    def manifest(
        self,
    ) -> Mapping[
        str,
        Any,
    ]:

        return MappingProxyType(
            {
                "persistence_record_id":
                    self.persistence_record_id,

                "previous_record_id":
                    self.previous_record_id,

                "identity_fingerprint":
                    self.identity_fingerprint,

                "orchestration_state":
                    self.orchestration_state.value,

                "progress_snapshot_id":
                    self.progress_snapshot_id,

                "schema_version":
                    self.schema_version,
            }
        )


def create_universal_orchestration_persistence_record(
    *,
    state_snapshot: Any,
    progress_snapshot: Any,
    previous_record_id: Any = None,
) -> UniversalOrchestrationPersistenceRecord:

    state = (
        _require_state_snapshot(
            state_snapshot
        )
    )

    progress = (
        _require_progress_snapshot(
            progress_snapshot
        )
    )

    return (
        UniversalOrchestrationPersistenceRecord(
            state_snapshot=state,
            progress_snapshot=progress,
            previous_record_id=previous_record_id,
        )
    )


def validate_universal_orchestration_persistence_successor(
    *,
    previous_record: Any,
    next_record: Any,
) -> bool:

    if not isinstance(
        previous_record,
        UniversalOrchestrationPersistenceRecord,
    ):

        raise UniversalOrchestrationPersistenceError(
            (
                "previous_record must be a "
                "UniversalOrchestrationPersistenceRecord."
            ),
            code="invalid_previous_persistence_record",
            value=previous_record,
        )

    if not isinstance(
        next_record,
        UniversalOrchestrationPersistenceRecord,
    ):

        raise UniversalOrchestrationPersistenceError(
            (
                "next_record must be a "
                "UniversalOrchestrationPersistenceRecord."
            ),
            code="invalid_next_persistence_record",
            value=next_record,
        )

    if (
        previous_record.identity_fingerprint
        !=
        next_record.identity_fingerprint
    ):

        raise UniversalOrchestrationPersistenceError(
            (
                "Persistence successor records must belong "
                "to the same orchestration identity."
            ),
            code="persistence_successor_identity_mismatch",
            value=(
                previous_record.identity_fingerprint,
                next_record.identity_fingerprint,
            ),
        )

    if (
        next_record.previous_record_id
        !=
        previous_record.persistence_record_id
    ):

        raise UniversalOrchestrationPersistenceError(
            (
                "next_record.previous_record_id must equal "
                "previous_record.persistence_record_id."
            ),
            code="persistence_successor_link_mismatch",
            value=(
                previous_record.persistence_record_id,
                next_record.previous_record_id,
            ),
        )

    return True


@runtime_checkable
class UniversalOrchestrationPersistencePort(
    Protocol
):

    def append_record(
        self,
        record: UniversalOrchestrationPersistenceRecord,
    ) -> UniversalOrchestrationPersistenceRecord:
        ...

    def load_latest_record(
        self,
        *,
        identity_fingerprint: str,
    ) -> UniversalOrchestrationPersistenceRecord | None:
        ...

    def load_record(
        self,
        *,
        persistence_record_id: str,
    ) -> UniversalOrchestrationPersistenceRecord | None:
        ...

    def list_record_history(
        self,
        *,
        identity_fingerprint: str,
    ) -> tuple[
        UniversalOrchestrationPersistenceRecord,
        ...,
    ]:
        ...


def explain_universal_orchestration_persistence_interface_v1(
) -> Mapping[
    str,
    Any,
]:

    return MappingProxyType(
        {
            "phase":
                "5.1.14",

            "component":
                "Universal Orchestration Persistence Interface",

            "version":
                UNIVERSAL_ORCHESTRATION_PERSISTENCE_INTERFACE_VERSION,

            "schema_version":
                UNIVERSAL_ORCHESTRATION_PERSISTENCE_RECORD_SCHEMA_VERSION,

            "stored_fields": (
                "state_snapshot",
                "progress_snapshot",
                "previous_record_id",
                "schema_version",
            ),

            "state_authority": (
                "Frozen 5.1.3 supplies authoritative "
                "orchestration lifecycle state."
            ),

            "progress_authority": (
                "Frozen 5.1.11 supplies canonical execution-plan, "
                "status, conditional-branch and effective-progress evidence."
            ),

            "derived_decision_rule": (
                "Frozen 5.1.12 suspension/resume eligibility and "
                "5.1.13 recovery decisions are deterministic derived "
                "projections and are not duplicated as stored fields."
            ),

            "record_rule": (
                "Persistence records are immutable, deterministic "
                "and append-only through previous_record_id lineage."
            ),

            "latest_pointer_rule": (
                "A concrete persistence backend may maintain a latest "
                "record pointer; 5.1.14 does not mutate one."
            ),

            "port_rule": (
                "5.1.14 defines the orchestration persistence port "
                "but does not implement a concrete storage backend."
            ),

            "serialization_boundary": (
                "5.1.14 exposes canonical Python records and a "
                "JSON-native manifest but does not own external "
                "serialization or deserialization."
            ),

            "concurrency_boundary": (
                "Transactions, locking, optimistic concurrency and "
                "compare-and-swap enforcement belong to the concrete "
                "Runtime State Store / persistence infrastructure."
            ),

            "completion_boundary": (
                "5.1.15 owns orchestration completion resolution."
            ),

            "termination_boundary": (
                "5.1.16 owns cancellation and termination resolution."
            ),

            "evidence_boundary": (
                "5.1.17 owns permanent orchestration evidence and "
                "decision records."
            ),

            "prohibitions": (
                "does not perform filesystem I/O",
                "does not perform database I/O",
                "does not perform network I/O",
                "does not choose a production storage backend",
                "does not import Runtime State Store",
                "does not import Runtime Persistence",
                "does not execute persistence transactions",
                "does not acquire persistence locks",
                "does not perform compare-and-swap",
                "does not update latest pointers",
                "does not delete orchestration history",
                "does not mutate previous persistence records",
                "does not use wall clock",
                "does not generate timestamps",
                "does not serialize external storage payloads",
                "does not deserialize external storage payloads",
                "does not transition orchestration state",
                "does not recompute progress",
                "does not reevaluate conditional branches",
                "does not reevaluate suspension/resume eligibility",
                "does not rerun orchestration recovery",
                "does not determine orchestration completion",
                "does not determine orchestration success",
                "does not determine orchestration failure",
                "does not cancel orchestration",
                "does not terminate orchestration",
                "does not record permanent audit evidence",
                "does not enqueue jobs",
                "does not dequeue jobs",
                "does not assign workers",
                "does not manipulate leases",
                "does not dispatch runtime handlers",
                "does not execute jobs",
                "does not import Universal Coordination Framework",
                "does not invoke pipeline coordinators",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_ORCHESTRATION_PERSISTENCE_INTERFACE_VERSION",
    "UNIVERSAL_ORCHESTRATION_PERSISTENCE_RECORD_SCHEMA_VERSION",
    "UNIVERSAL_ORCHESTRATION_PERSISTENCE_RECORD_HASH_ALGORITHM",
    "UniversalOrchestrationPersistenceError",
    "UniversalOrchestrationPersistenceRecord",
    "UniversalOrchestrationPersistencePort",
    "create_universal_orchestration_persistence_record",
    "validate_universal_orchestration_persistence_successor",
    "explain_universal_orchestration_persistence_interface_v1",
]
