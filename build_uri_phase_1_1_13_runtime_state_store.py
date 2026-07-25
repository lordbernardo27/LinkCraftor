from __future__ import annotations

import ast
import hashlib
import importlib
import json
import py_compile
import shutil
import sys
import threading
import traceback
from datetime import datetime, timedelta, timezone
from pathlib import Path


PROJECT_ROOT = Path.cwd().resolve()

RUNTIME_DIR = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "runtime"
)

TARGET = (
    RUNTIME_DIR
    / "runtime_state_store.py"
)

PERSISTENCE_MODULE = (
    RUNTIME_DIR
    / "runtime_persistence.py"
)

EVIDENCE_DIR = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime"
    / "uri_phase_1"
    / "1_1_13_runtime_state_store_abstraction"
)

BACKUP_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime_backups"
)

TIMESTAMP = datetime.now(timezone.utc).strftime(
    "%Y%m%dT%H%M%SZ"
)

BACKUP_DIR = (
    BACKUP_ROOT
    / f"uri_phase1_1_13_runtime_state_store_{TIMESTAMP}"
)

BACKUP_FILE = BACKUP_DIR / TARGET.name

EVIDENCE_JSON = (
    EVIDENCE_DIR
    / f"runtime_state_store_build_{TIMESTAMP}.json"
)

EVIDENCE_TEXT = (
    EVIDENCE_DIR
    / f"runtime_state_store_build_{TIMESTAMP}.txt"
)


MODULE_SOURCE = r'''from __future__ import annotations

"""
Universal Runtime Infrastructure
Phase 1.1.13 — Runtime State Store Abstraction

This module defines logical, business-logic-agnostic state-store abstractions
for runtime-owned state.

It sits above runtime_persistence.py and below concrete job, queue, worker,
pipeline, lease, checkpoint, event, billing, and recovery infrastructure.

It does not choose a production database and does not contain product-pipeline
business logic.
"""

import hashlib
import json
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import Any, Iterable, Mapping

from runtime_persistence import (
    RuntimePersistenceBackend,
    RuntimePersistenceConflictError,
    RuntimePersistenceKey,
    RuntimePersistenceNotFoundError,
    RuntimePersistenceOperation,
    RuntimePersistenceOperationType,
    RuntimePersistencePage,
    RuntimePersistenceRecord,
    RuntimePersistenceTransactionResult,
    RuntimePersistenceValidationError,
    RuntimePersistenceWriteCondition,
    RuntimePersistenceWriteMode,
)


class RuntimeStateStoreError(RuntimeError):
    """Base exception for logical runtime state-store failures."""


class RuntimeStateStoreValidationError(RuntimeStateStoreError):
    """Raised when a state-store contract is invalid."""


class RuntimeStateStoreNotFoundError(RuntimeStateStoreError):
    """Raised when a logical state record or store cannot be found."""


class RuntimeStateStoreConflictError(RuntimeStateStoreError):
    """Raised when state revision or ownership constraints fail."""


class RuntimeStateStoreRegistrationError(RuntimeStateStoreError):
    """Raised when logical store registration fails."""


class RuntimeStateDomain(str, Enum):
    JOBS = "jobs"
    QUEUES = "queues"
    WORKERS = "workers"
    LEASES = "leases"
    PIPELINES = "pipelines"
    PIPELINE_RUNS = "pipeline_runs"
    BATCHES = "batches"
    CHECKPOINTS = "checkpoints"
    EVENTS = "events"
    DEAD_LETTERS = "dead_letters"
    RESOURCE_RESERVATIONS = "resource_reservations"
    AU_RECORDS = "au_records"
    COST_RECORDS = "cost_records"
    FEATURE_FLAGS = "feature_flags"
    CAPABILITY_MANIFESTS = "capability_manifests"
    RUNTIME_VERSIONS = "runtime_versions"
    RUNTIME_MIGRATIONS = "runtime_migrations"
    RUNTIME_CERTIFICATES = "runtime_certificates"


class RuntimeStateLifecycle(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    TOMBSTONED = "tombstoned"
    ARCHIVED = "archived"


class RuntimeStateMutationMode(str, Enum):
    UPSERT = "upsert"
    CREATE_ONLY = "create_only"
    UPDATE_ONLY = "update_only"
    COMPARE_AND_SET = "compare_and_set"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _normalise_text(
    value: str,
    *,
    field_name: str,
) -> str:
    if not isinstance(value, str):
        raise RuntimeStateStoreValidationError(
            f"{field_name} must be a string."
        )

    normalised = value.strip()

    if not normalised:
        raise RuntimeStateStoreValidationError(
            f"{field_name} must not be empty."
        )

    return normalised


def _normalise_optional_text(
    value: str | None,
    *,
    field_name: str,
) -> str | None:
    if value is None:
        return None

    return _normalise_text(
        value,
        field_name=field_name,
    )


def _normalise_datetime(
    value: datetime | None,
    *,
    field_name: str,
) -> datetime | None:
    if value is None:
        return None

    if not isinstance(value, datetime):
        raise RuntimeStateStoreValidationError(
            f"{field_name} must be a datetime."
        )

    if value.tzinfo is None:
        raise RuntimeStateStoreValidationError(
            f"{field_name} must be timezone-aware."
        )

    return value.astimezone(timezone.utc)


def _freeze_mapping(
    value: Mapping[str, Any] | None,
) -> Mapping[str, Any]:
    return MappingProxyType(
        dict(value or {})
    )


def _canonical_json(
    value: Mapping[str, Any],
) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )


def _fingerprint(
    value: Mapping[str, Any],
) -> str:
    return hashlib.sha256(
        _canonical_json(value).encode("utf-8")
    ).hexdigest()


def _state_namespace(
    domain: RuntimeStateDomain,
    *,
    partition: str | None = None,
) -> str:
    base = f"runtime.state.{domain.value}"

    if partition is None:
        return base

    return (
        base
        + "."
        + _normalise_text(
            partition,
            field_name="partition",
        )
    )


@dataclass(frozen=True, slots=True)
class RuntimeStateIdentity:
    domain: RuntimeStateDomain
    state_id: str
    partition: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(
            self.domain,
            RuntimeStateDomain,
        ):
            try:
                object.__setattr__(
                    self,
                    "domain",
                    RuntimeStateDomain(
                        self.domain
                    ),
                )
            except Exception as exc:
                raise RuntimeStateStoreValidationError(
                    "domain is invalid."
                ) from exc

        object.__setattr__(
            self,
            "state_id",
            _normalise_text(
                self.state_id,
                field_name="state_id",
            ),
        )

        object.__setattr__(
            self,
            "partition",
            _normalise_optional_text(
                self.partition,
                field_name="partition",
            ),
        )

    @property
    def namespace(self) -> str:
        return _state_namespace(
            self.domain,
            partition=self.partition,
        )

    @property
    def persistence_key(
        self,
    ) -> RuntimePersistenceKey:
        return RuntimePersistenceKey(
            namespace=self.namespace,
            key=self.state_id,
        )

    @property
    def canonical(self) -> str:
        return (
            f"{self.domain.value}:"
            f"{self.partition or '_'}:"
            f"{self.state_id}"
        )


@dataclass(frozen=True, slots=True)
class RuntimeStateEnvelope:
    identity: RuntimeStateIdentity
    schema_name: str
    schema_version: str
    state: Mapping[str, Any]
    lifecycle: RuntimeStateLifecycle = (
        RuntimeStateLifecycle.ACTIVE
    )
    owner_workspace_id: str | None = None
    owner_organization_id: str | None = None
    owner_user_id: str | None = None
    correlation_id: str | None = None
    trace_id: str | None = None
    created_at: datetime = field(
        default_factory=_utc_now
    )
    updated_at: datetime = field(
        default_factory=_utc_now
    )
    expires_at: datetime | None = None
    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        if not isinstance(
            self.identity,
            RuntimeStateIdentity,
        ):
            raise RuntimeStateStoreValidationError(
                "identity must be a RuntimeStateIdentity."
            )

        object.__setattr__(
            self,
            "schema_name",
            _normalise_text(
                self.schema_name,
                field_name="schema_name",
            ),
        )

        object.__setattr__(
            self,
            "schema_version",
            _normalise_text(
                self.schema_version,
                field_name="schema_version",
            ),
        )

        if not isinstance(
            self.lifecycle,
            RuntimeStateLifecycle,
        ):
            try:
                object.__setattr__(
                    self,
                    "lifecycle",
                    RuntimeStateLifecycle(
                        self.lifecycle
                    ),
                )
            except Exception as exc:
                raise RuntimeStateStoreValidationError(
                    "lifecycle is invalid."
                ) from exc

        object.__setattr__(
            self,
            "owner_workspace_id",
            _normalise_optional_text(
                self.owner_workspace_id,
                field_name="owner_workspace_id",
            ),
        )

        object.__setattr__(
            self,
            "owner_organization_id",
            _normalise_optional_text(
                self.owner_organization_id,
                field_name="owner_organization_id",
            ),
        )

        object.__setattr__(
            self,
            "owner_user_id",
            _normalise_optional_text(
                self.owner_user_id,
                field_name="owner_user_id",
            ),
        )

        object.__setattr__(
            self,
            "correlation_id",
            _normalise_optional_text(
                self.correlation_id,
                field_name="correlation_id",
            ),
        )

        object.__setattr__(
            self,
            "trace_id",
            _normalise_optional_text(
                self.trace_id,
                field_name="trace_id",
            ),
        )

        created_at = _normalise_datetime(
            self.created_at,
            field_name="created_at",
        )

        updated_at = _normalise_datetime(
            self.updated_at,
            field_name="updated_at",
        )

        expires_at = _normalise_datetime(
            self.expires_at,
            field_name="expires_at",
        )

        if created_at is None or updated_at is None:
            raise RuntimeStateStoreValidationError(
                "created_at and updated_at are required."
            )

        if updated_at < created_at:
            raise RuntimeStateStoreValidationError(
                "updated_at must not be earlier than created_at."
            )

        if (
            expires_at is not None
            and expires_at <= created_at
        ):
            raise RuntimeStateStoreValidationError(
                "expires_at must be later than created_at."
            )

        object.__setattr__(
            self,
            "created_at",
            created_at,
        )

        object.__setattr__(
            self,
            "updated_at",
            updated_at,
        )

        object.__setattr__(
            self,
            "expires_at",
            expires_at,
        )

        object.__setattr__(
            self,
            "state",
            _freeze_mapping(
                self.state
            ),
        )

        object.__setattr__(
            self,
            "metadata",
            _freeze_mapping(
                self.metadata
            ),
        )

    @property
    def fingerprint(self) -> str:
        return _fingerprint(
            self.to_dict()
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "identity": {
                "domain": self.identity.domain.value,
                "state_id": self.identity.state_id,
                "partition": self.identity.partition,
            },
            "schema_name": self.schema_name,
            "schema_version": self.schema_version,
            "state": dict(self.state),
            "lifecycle": self.lifecycle.value,
            "owner_workspace_id": (
                self.owner_workspace_id
            ),
            "owner_organization_id": (
                self.owner_organization_id
            ),
            "owner_user_id": (
                self.owner_user_id
            ),
            "correlation_id": self.correlation_id,
            "trace_id": self.trace_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "expires_at": (
                self.expires_at.isoformat()
                if self.expires_at is not None
                else None
            ),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(
        cls,
        value: Mapping[str, Any],
    ) -> RuntimeStateEnvelope:
        try:
            identity_value = value["identity"]

            return cls(
                identity=RuntimeStateIdentity(
                    domain=identity_value["domain"],
                    state_id=identity_value["state_id"],
                    partition=identity_value.get(
                        "partition"
                    ),
                ),
                schema_name=value["schema_name"],
                schema_version=value[
                    "schema_version"
                ],
                state=value["state"],
                lifecycle=value.get(
                    "lifecycle",
                    RuntimeStateLifecycle.ACTIVE.value,
                ),
                owner_workspace_id=value.get(
                    "owner_workspace_id"
                ),
                owner_organization_id=value.get(
                    "owner_organization_id"
                ),
                owner_user_id=value.get(
                    "owner_user_id"
                ),
                correlation_id=value.get(
                    "correlation_id"
                ),
                trace_id=value.get(
                    "trace_id"
                ),
                created_at=datetime.fromisoformat(
                    value["created_at"]
                ),
                updated_at=datetime.fromisoformat(
                    value["updated_at"]
                ),
                expires_at=(
                    datetime.fromisoformat(
                        value["expires_at"]
                    )
                    if value.get("expires_at")
                    else None
                ),
                metadata=value.get(
                    "metadata",
                    {},
                ),
            )
        except (
            KeyError,
            TypeError,
            ValueError,
        ) as exc:
            raise RuntimeStateStoreValidationError(
                "Stored state envelope is invalid."
            ) from exc


@dataclass(frozen=True, slots=True)
class RuntimeStoredState:
    envelope: RuntimeStateEnvelope
    revision: int
    persistence_fingerprint: str
    persisted_at: datetime

    def __post_init__(self) -> None:
        if not isinstance(
            self.envelope,
            RuntimeStateEnvelope,
        ):
            raise RuntimeStateStoreValidationError(
                "envelope must be a RuntimeStateEnvelope."
            )

        if (
            not isinstance(self.revision, int)
            or self.revision < 1
        ):
            raise RuntimeStateStoreValidationError(
                "revision must be at least 1."
            )

        object.__setattr__(
            self,
            "persistence_fingerprint",
            _normalise_text(
                self.persistence_fingerprint,
                field_name=(
                    "persistence_fingerprint"
                ),
            ),
        )

        persisted_at = _normalise_datetime(
            self.persisted_at,
            field_name="persisted_at",
        )

        if persisted_at is None:
            raise RuntimeStateStoreValidationError(
                "persisted_at is required."
            )

        object.__setattr__(
            self,
            "persisted_at",
            persisted_at,
        )


@dataclass(frozen=True, slots=True)
class RuntimeStateMutation:
    envelope: RuntimeStateEnvelope
    mode: RuntimeStateMutationMode = (
        RuntimeStateMutationMode.UPSERT
    )
    expected_revision: int | None = None
    expected_fingerprint: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(
            self.envelope,
            RuntimeStateEnvelope,
        ):
            raise RuntimeStateStoreValidationError(
                "envelope must be a RuntimeStateEnvelope."
            )

        if not isinstance(
            self.mode,
            RuntimeStateMutationMode,
        ):
            try:
                object.__setattr__(
                    self,
                    "mode",
                    RuntimeStateMutationMode(
                        self.mode
                    ),
                )
            except Exception as exc:
                raise RuntimeStateStoreValidationError(
                    "mode is invalid."
                ) from exc

        if (
            self.expected_revision is not None
            and (
                not isinstance(
                    self.expected_revision,
                    int,
                )
                or self.expected_revision < 1
            )
        ):
            raise RuntimeStateStoreValidationError(
                "expected_revision must be at least 1."
            )

        object.__setattr__(
            self,
            "expected_fingerprint",
            _normalise_optional_text(
                self.expected_fingerprint,
                field_name="expected_fingerprint",
            ),
        )

        if (
            self.mode
            is RuntimeStateMutationMode.COMPARE_AND_SET
            and self.expected_revision is None
            and self.expected_fingerprint is None
        ):
            raise RuntimeStateStoreValidationError(
                "COMPARE_AND_SET requires an expected revision "
                "or expected fingerprint."
            )


@dataclass(frozen=True, slots=True)
class RuntimeStateDelete:
    identity: RuntimeStateIdentity
    expected_revision: int | None = None
    expected_fingerprint: str | None = None
    require_exists: bool = False

    def __post_init__(self) -> None:
        if not isinstance(
            self.identity,
            RuntimeStateIdentity,
        ):
            raise RuntimeStateStoreValidationError(
                "identity must be a RuntimeStateIdentity."
            )

        if (
            self.expected_revision is not None
            and (
                not isinstance(
                    self.expected_revision,
                    int,
                )
                or self.expected_revision < 1
            )
        ):
            raise RuntimeStateStoreValidationError(
                "expected_revision must be at least 1."
            )

        object.__setattr__(
            self,
            "expected_fingerprint",
            _normalise_optional_text(
                self.expected_fingerprint,
                field_name="expected_fingerprint",
            ),
        )


@dataclass(frozen=True, slots=True)
class RuntimeStatePage:
    states: tuple[RuntimeStoredState, ...]
    next_cursor: str | None
    domain: RuntimeStateDomain
    partition: str | None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "states",
            tuple(self.states),
        )

        object.__setattr__(
            self,
            "next_cursor",
            _normalise_optional_text(
                self.next_cursor,
                field_name="next_cursor",
            ),
        )

        if not isinstance(
            self.domain,
            RuntimeStateDomain,
        ):
            try:
                object.__setattr__(
                    self,
                    "domain",
                    RuntimeStateDomain(
                        self.domain
                    ),
                )
            except Exception as exc:
                raise RuntimeStateStoreValidationError(
                    "domain is invalid."
                ) from exc

        object.__setattr__(
            self,
            "partition",
            _normalise_optional_text(
                self.partition,
                field_name="partition",
            ),
        )


@dataclass(frozen=True, slots=True)
class RuntimeStateStoreSnapshot:
    store_id: str
    domain: RuntimeStateDomain
    partition: str | None
    record_count: int
    captured_at: datetime
    fingerprint: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "store_id",
            _normalise_text(
                self.store_id,
                field_name="store_id",
            ),
        )

        if self.record_count < 0:
            raise RuntimeStateStoreValidationError(
                "record_count must not be negative."
            )

        captured_at = _normalise_datetime(
            self.captured_at,
            field_name="captured_at",
        )

        if captured_at is None:
            raise RuntimeStateStoreValidationError(
                "captured_at is required."
            )

        object.__setattr__(
            self,
            "captured_at",
            captured_at,
        )


@dataclass(frozen=True, slots=True)
class RuntimeStateTransactionResult:
    committed: bool
    writes: tuple[RuntimeStoredState, ...]
    deleted_ids: tuple[str, ...]
    persistence_result: (
        RuntimePersistenceTransactionResult
    )
    fingerprint: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "writes",
            tuple(self.writes),
        )

        object.__setattr__(
            self,
            "deleted_ids",
            tuple(self.deleted_ids),
        )

        if not isinstance(
            self.persistence_result,
            RuntimePersistenceTransactionResult,
        ):
            raise RuntimeStateStoreValidationError(
                "persistence_result must be a "
                "RuntimePersistenceTransactionResult."
            )


def _persistence_condition(
    *,
    mode: RuntimeStateMutationMode,
    expected_revision: int | None,
    expected_fingerprint: str | None,
) -> RuntimePersistenceWriteCondition:
    mode_map = {
        RuntimeStateMutationMode.UPSERT: (
            RuntimePersistenceWriteMode.UPSERT
        ),
        RuntimeStateMutationMode.CREATE_ONLY: (
            RuntimePersistenceWriteMode.CREATE_ONLY
        ),
        RuntimeStateMutationMode.UPDATE_ONLY: (
            RuntimePersistenceWriteMode.UPDATE_ONLY
        ),
        RuntimeStateMutationMode.COMPARE_AND_SET: (
            RuntimePersistenceWriteMode.COMPARE_AND_SET
        ),
    }

    return RuntimePersistenceWriteCondition(
        mode=mode_map[mode],
        expected_revision=expected_revision,
        expected_fingerprint=expected_fingerprint,
    )


def _stored_state_from_record(
    record: RuntimePersistenceRecord,
) -> RuntimeStoredState:
    envelope = RuntimeStateEnvelope.from_dict(
        record.value
    )

    if (
        envelope.identity.persistence_key
        != record.key
    ):
        raise RuntimeStateStoreValidationError(
            "Stored envelope identity does not match "
            "its persistence key."
        )

    return RuntimeStoredState(
        envelope=envelope,
        revision=record.revision,
        persistence_fingerprint=(
            record.fingerprint
        ),
        persisted_at=record.updated_at,
    )


class RuntimeStateStore:
    """
    Logical store for one runtime state domain and optional partition.

    The store delegates durable operations to RuntimePersistenceBackend while
    enforcing namespace isolation and runtime-state envelope validation.
    """

    def __init__(
        self,
        *,
        store_id: str,
        domain: RuntimeStateDomain,
        backend: RuntimePersistenceBackend,
        partition: str | None = None,
    ) -> None:
        self._store_id = _normalise_text(
            store_id,
            field_name="store_id",
        )

        if not isinstance(
            domain,
            RuntimeStateDomain,
        ):
            try:
                domain = RuntimeStateDomain(
                    domain
                )
            except Exception as exc:
                raise RuntimeStateStoreValidationError(
                    "domain is invalid."
                ) from exc

        if not isinstance(
            backend,
            RuntimePersistenceBackend,
        ):
            raise RuntimeStateStoreValidationError(
                "backend must implement "
                "RuntimePersistenceBackend."
            )

        self._domain = domain
        self._partition = (
            _normalise_optional_text(
                partition,
                field_name="partition",
            )
        )
        self._backend = backend
        self._lock = threading.RLock()

    @property
    def store_id(self) -> str:
        return self._store_id

    @property
    def domain(self) -> RuntimeStateDomain:
        return self._domain

    @property
    def partition(self) -> str | None:
        return self._partition

    @property
    def namespace(self) -> str:
        return _state_namespace(
            self.domain,
            partition=self.partition,
        )

    @property
    def backend(
        self,
    ) -> RuntimePersistenceBackend:
        return self._backend

    def create(
        self,
        envelope: RuntimeStateEnvelope,
    ) -> RuntimeStoredState:
        return self.write(
            RuntimeStateMutation(
                envelope=envelope,
                mode=(
                    RuntimeStateMutationMode.CREATE_ONLY
                ),
            )
        )

    def upsert(
        self,
        envelope: RuntimeStateEnvelope,
    ) -> RuntimeStoredState:
        return self.write(
            RuntimeStateMutation(
                envelope=envelope,
                mode=RuntimeStateMutationMode.UPSERT,
            )
        )

    def update(
        self,
        envelope: RuntimeStateEnvelope,
        *,
        expected_revision: int | None = None,
        expected_fingerprint: str | None = None,
    ) -> RuntimeStoredState:
        mode = (
            RuntimeStateMutationMode.COMPARE_AND_SET
            if (
                expected_revision is not None
                or expected_fingerprint is not None
            )
            else RuntimeStateMutationMode.UPDATE_ONLY
        )

        return self.write(
            RuntimeStateMutation(
                envelope=envelope,
                mode=mode,
                expected_revision=expected_revision,
                expected_fingerprint=(
                    expected_fingerprint
                ),
            )
        )

    def write(
        self,
        mutation: RuntimeStateMutation,
    ) -> RuntimeStoredState:
        if not isinstance(
            mutation,
            RuntimeStateMutation,
        ):
            raise RuntimeStateStoreValidationError(
                "mutation must be a RuntimeStateMutation."
            )

        self._validate_identity(
            mutation.envelope.identity
        )

        condition = _persistence_condition(
            mode=mutation.mode,
            expected_revision=(
                mutation.expected_revision
            ),
            expected_fingerprint=(
                mutation.expected_fingerprint
            ),
        )

        try:
            result = self.backend.put(
                mutation.envelope.identity.persistence_key,
                mutation.envelope.to_dict(),
                condition=condition,
                expires_at=(
                    mutation.envelope.expires_at
                ),
                metadata={
                    "store_id": self.store_id,
                    "domain": self.domain.value,
                    "partition": self.partition,
                    "schema_name": (
                        mutation.envelope.schema_name
                    ),
                    "schema_version": (
                        mutation.envelope.schema_version
                    ),
                    "state_fingerprint": (
                        mutation.envelope.fingerprint
                    ),
                },
            )
        except RuntimePersistenceConflictError as exc:
            raise RuntimeStateStoreConflictError(
                str(exc)
            ) from exc
        except RuntimePersistenceValidationError as exc:
            raise RuntimeStateStoreValidationError(
                str(exc)
            ) from exc

        return _stored_state_from_record(
            result.record
        )

    def get(
        self,
        state_id: str,
        *,
        include_expired: bool = False,
    ) -> RuntimeStoredState | None:
        identity = RuntimeStateIdentity(
            domain=self.domain,
            state_id=state_id,
            partition=self.partition,
        )

        record = self.backend.get(
            identity.persistence_key,
            include_expired=include_expired,
        )

        if record is None:
            return None

        stored = _stored_state_from_record(
            record
        )

        self._validate_identity(
            stored.envelope.identity
        )

        return stored

    def require(
        self,
        state_id: str,
        *,
        include_expired: bool = False,
    ) -> RuntimeStoredState:
        stored = self.get(
            state_id,
            include_expired=include_expired,
        )

        if stored is None:
            raise RuntimeStateStoreNotFoundError(
                f"Runtime state not found: {state_id}"
            )

        return stored

    def delete(
        self,
        deletion: RuntimeStateDelete,
    ) -> bool:
        if not isinstance(
            deletion,
            RuntimeStateDelete,
        ):
            raise RuntimeStateStoreValidationError(
                "deletion must be a RuntimeStateDelete."
            )

        self._validate_identity(
            deletion.identity
        )

        if (
            deletion.expected_revision is not None
            or deletion.expected_fingerprint
            is not None
        ):
            condition = (
                RuntimePersistenceWriteCondition(
                    mode=(
                        RuntimePersistenceWriteMode.COMPARE_AND_SET
                    ),
                    expected_revision=(
                        deletion.expected_revision
                    ),
                    expected_fingerprint=(
                        deletion.expected_fingerprint
                    ),
                )
            )
        elif deletion.require_exists:
            condition = (
                RuntimePersistenceWriteCondition(
                    mode=(
                        RuntimePersistenceWriteMode.UPDATE_ONLY
                    )
                )
            )
        else:
            condition = (
                RuntimePersistenceWriteCondition()
            )

        try:
            result = self.backend.delete(
                deletion.identity.persistence_key,
                condition=condition,
            )
        except RuntimePersistenceConflictError as exc:
            raise RuntimeStateStoreConflictError(
                str(exc)
            ) from exc

        return result.deleted

    def list(
        self,
        *,
        prefix: str | None = None,
        limit: int = 100,
        cursor: str | None = None,
        include_expired: bool = False,
    ) -> RuntimeStatePage:
        page = self.backend.list(
            self.namespace,
            prefix=prefix,
            limit=limit,
            cursor=cursor,
            include_expired=include_expired,
        )

        states = tuple(
            _stored_state_from_record(
                record
            )
            for record in page.records
        )

        for state in states:
            self._validate_identity(
                state.envelope.identity
            )

        return RuntimeStatePage(
            states=states,
            next_cursor=page.next_cursor,
            domain=self.domain,
            partition=self.partition,
        )

    def transact(
        self,
        *,
        mutations: Iterable[
            RuntimeStateMutation
        ] = (),
        deletions: Iterable[
            RuntimeStateDelete
        ] = (),
    ) -> RuntimeStateTransactionResult:
        mutation_tuple = tuple(mutations)
        deletion_tuple = tuple(deletions)

        if not mutation_tuple and not deletion_tuple:
            raise RuntimeStateStoreValidationError(
                "A state transaction requires at least "
                "one mutation or deletion."
            )

        operations: list[
            RuntimePersistenceOperation
        ] = []

        for mutation in mutation_tuple:
            if not isinstance(
                mutation,
                RuntimeStateMutation,
            ):
                raise RuntimeStateStoreValidationError(
                    "mutations must contain "
                    "RuntimeStateMutation values."
                )

            self._validate_identity(
                mutation.envelope.identity
            )

            operations.append(
                RuntimePersistenceOperation(
                    operation_type=(
                        RuntimePersistenceOperationType.PUT
                    ),
                    key=(
                        mutation.envelope.identity
                        .persistence_key
                    ),
                    value=(
                        mutation.envelope.to_dict()
                    ),
                    condition=_persistence_condition(
                        mode=mutation.mode,
                        expected_revision=(
                            mutation.expected_revision
                        ),
                        expected_fingerprint=(
                            mutation.expected_fingerprint
                        ),
                    ),
                    expires_at=(
                        mutation.envelope.expires_at
                    ),
                    metadata={
                        "store_id": self.store_id,
                        "domain": self.domain.value,
                        "partition": self.partition,
                        "schema_name": (
                            mutation.envelope.schema_name
                        ),
                        "schema_version": (
                            mutation.envelope
                            .schema_version
                        ),
                        "state_fingerprint": (
                            mutation.envelope
                            .fingerprint
                        ),
                    },
                )
            )

        for deletion in deletion_tuple:
            if not isinstance(
                deletion,
                RuntimeStateDelete,
            ):
                raise RuntimeStateStoreValidationError(
                    "deletions must contain "
                    "RuntimeStateDelete values."
                )

            self._validate_identity(
                deletion.identity
            )

            if (
                deletion.expected_revision is not None
                or deletion.expected_fingerprint
                is not None
            ):
                condition = (
                    RuntimePersistenceWriteCondition(
                        mode=(
                            RuntimePersistenceWriteMode
                            .COMPARE_AND_SET
                        ),
                        expected_revision=(
                            deletion.expected_revision
                        ),
                        expected_fingerprint=(
                            deletion.expected_fingerprint
                        ),
                    )
                )
            elif deletion.require_exists:
                condition = (
                    RuntimePersistenceWriteCondition(
                        mode=(
                            RuntimePersistenceWriteMode
                            .UPDATE_ONLY
                        )
                    )
                )
            else:
                condition = (
                    RuntimePersistenceWriteCondition()
                )

            operations.append(
                RuntimePersistenceOperation(
                    operation_type=(
                        RuntimePersistenceOperationType
                        .DELETE
                    ),
                    key=deletion.identity.persistence_key,
                    condition=condition,
                )
            )

        try:
            persistence_result = (
                self.backend.transact(
                    operations
                )
            )
        except Exception as exc:
            if isinstance(
                exc,
                RuntimeStateStoreError,
            ):
                raise

            raise RuntimeStateStoreConflictError(
                "Runtime state transaction failed."
            ) from exc

        writes = tuple(
            _stored_state_from_record(
                result.record
            )
            for result
            in persistence_result.write_results
        )

        deleted_ids = tuple(
            result.key.key
            for result
            in persistence_result.delete_results
            if result.deleted
        )

        payload = {
            "store_id": self.store_id,
            "persistence_fingerprint": (
                persistence_result.fingerprint
            ),
            "writes": [
                {
                    "identity": (
                        state.envelope.identity.canonical
                    ),
                    "revision": state.revision,
                    "fingerprint": (
                        state.persistence_fingerprint
                    ),
                }
                for state in writes
            ],
            "deleted_ids": list(
                deleted_ids
            ),
        }

        return RuntimeStateTransactionResult(
            committed=(
                persistence_result.committed
            ),
            writes=writes,
            deleted_ids=deleted_ids,
            persistence_result=(
                persistence_result
            ),
            fingerprint=_fingerprint(payload),
        )

    def snapshot(
        self,
    ) -> RuntimeStateStoreSnapshot:
        cursor: str | None = None
        fingerprints: list[str] = []
        record_count = 0

        while True:
            page = self.list(
                limit=1000,
                cursor=cursor,
                include_expired=True,
            )

            for state in page.states:
                fingerprints.append(
                    state.persistence_fingerprint
                )

            record_count += len(
                page.states
            )

            if page.next_cursor is None:
                break

            cursor = page.next_cursor

        payload = {
            "store_id": self.store_id,
            "domain": self.domain.value,
            "partition": self.partition,
            "record_count": record_count,
            "record_fingerprints": sorted(
                fingerprints
            ),
        }

        return RuntimeStateStoreSnapshot(
            store_id=self.store_id,
            domain=self.domain,
            partition=self.partition,
            record_count=record_count,
            captured_at=_utc_now(),
            fingerprint=_fingerprint(payload),
        )

    def _validate_identity(
        self,
        identity: RuntimeStateIdentity,
    ) -> None:
        if not isinstance(
            identity,
            RuntimeStateIdentity,
        ):
            raise RuntimeStateStoreValidationError(
                "identity must be a RuntimeStateIdentity."
            )

        if identity.domain is not self.domain:
            raise RuntimeStateStoreValidationError(
                "State domain does not match the "
                "logical store domain."
            )

        if identity.partition != self.partition:
            raise RuntimeStateStoreValidationError(
                "State partition does not match the "
                "logical store partition."
            )


@dataclass(frozen=True, slots=True)
class RuntimeStateStoreRegistrySnapshot:
    generation: int
    store_ids: tuple[str, ...]
    domains: tuple[str, ...]
    captured_at: datetime
    fingerprint: str


class RuntimeStateStoreRegistry:
    """Thread-safe registry of logical runtime state stores."""

    def __init__(self) -> None:
        self._stores: dict[
            str,
            RuntimeStateStore,
        ] = {}
        self._domain_index: dict[
            tuple[RuntimeStateDomain, str | None],
            str,
        ] = {}
        self._generation = 0
        self._lock = threading.RLock()

    @property
    def generation(self) -> int:
        with self._lock:
            return self._generation

    def register(
        self,
        store: RuntimeStateStore,
        *,
        replace: bool = False,
    ) -> RuntimeStateStore:
        if not isinstance(
            store,
            RuntimeStateStore,
        ):
            raise RuntimeStateStoreValidationError(
                "store must be a RuntimeStateStore."
            )

        domain_key = (
            store.domain,
            store.partition,
        )

        with self._lock:
            existing_by_id = self._stores.get(
                store.store_id
            )

            existing_domain_store_id = (
                self._domain_index.get(
                    domain_key
                )
            )

            if (
                existing_by_id is not None
                and not replace
            ):
                raise RuntimeStateStoreRegistrationError(
                    "A state store with this store_id "
                    "already exists."
                )

            if (
                existing_domain_store_id is not None
                and existing_domain_store_id
                != store.store_id
                and not replace
            ):
                raise RuntimeStateStoreRegistrationError(
                    "A state store already owns this "
                    "domain and partition."
                )

            if (
                existing_by_id is not None
                and replace
            ):
                old_domain_key = (
                    existing_by_id.domain,
                    existing_by_id.partition,
                )

                self._domain_index.pop(
                    old_domain_key,
                    None,
                )

            if (
                existing_domain_store_id is not None
                and existing_domain_store_id
                != store.store_id
                and replace
            ):
                self._stores.pop(
                    existing_domain_store_id,
                    None,
                )

            self._stores[
                store.store_id
            ] = store

            self._domain_index[
                domain_key
            ] = store.store_id

            self._generation += 1

            return store

    def get(
        self,
        store_id: str,
    ) -> RuntimeStateStore:
        normalised = _normalise_text(
            store_id,
            field_name="store_id",
        )

        with self._lock:
            store = self._stores.get(
                normalised
            )

            if store is None:
                raise RuntimeStateStoreNotFoundError(
                    f"State store not found: {normalised}"
                )

            return store

    def resolve(
        self,
        domain: RuntimeStateDomain,
        *,
        partition: str | None = None,
    ) -> RuntimeStateStore:
        if not isinstance(
            domain,
            RuntimeStateDomain,
        ):
            try:
                domain = RuntimeStateDomain(
                    domain
                )
            except Exception as exc:
                raise RuntimeStateStoreValidationError(
                    "domain is invalid."
                ) from exc

        normalised_partition = (
            _normalise_optional_text(
                partition,
                field_name="partition",
            )
        )

        with self._lock:
            store_id = self._domain_index.get(
                (
                    domain,
                    normalised_partition,
                )
            )

            if store_id is None:
                raise RuntimeStateStoreNotFoundError(
                    "No state store is registered for "
                    f"{domain.value} and partition "
                    f"{normalised_partition!r}."
                )

            return self._stores[
                store_id
            ]

    def remove(
        self,
        store_id: str,
    ) -> RuntimeStateStore:
        normalised = _normalise_text(
            store_id,
            field_name="store_id",
        )

        with self._lock:
            try:
                store = self._stores.pop(
                    normalised
                )
            except KeyError as exc:
                raise RuntimeStateStoreNotFoundError(
                    f"State store not found: {normalised}"
                ) from exc

            self._domain_index.pop(
                (
                    store.domain,
                    store.partition,
                ),
                None,
            )

            self._generation += 1

            return store

    def snapshot(
        self,
    ) -> RuntimeStateStoreRegistrySnapshot:
        with self._lock:
            stores = tuple(
                sorted(
                    self._stores.values(),
                    key=lambda item: item.store_id,
                )
            )

            store_ids = tuple(
                store.store_id
                for store in stores
            )

            domains = tuple(
                (
                    store.domain.value
                    + ":"
                    + (
                        store.partition
                        if store.partition
                        is not None
                        else "_"
                    )
                )
                for store in stores
            )

            payload = {
                "generation": self._generation,
                "store_ids": store_ids,
                "domains": domains,
            }

            return RuntimeStateStoreRegistrySnapshot(
                generation=self._generation,
                store_ids=store_ids,
                domains=domains,
                captured_at=_utc_now(),
                fingerprint=_fingerprint(payload),
            )


def create_default_runtime_state_stores(
    *,
    backend: RuntimePersistenceBackend,
    registry: RuntimeStateStoreRegistry | None = None,
) -> RuntimeStateStoreRegistry:
    effective_registry = (
        registry
        or RuntimeStateStoreRegistry()
    )

    for domain in RuntimeStateDomain:
        effective_registry.register(
            RuntimeStateStore(
                store_id=(
                    "runtime-state-"
                    + domain.value.replace(
                        "_",
                        "-",
                    )
                ),
                domain=domain,
                backend=backend,
            )
        )

    return effective_registry


_default_registry = RuntimeStateStoreRegistry()


def get_runtime_state_store_registry(
) -> RuntimeStateStoreRegistry:
    return _default_registry


def register_runtime_state_store(
    store: RuntimeStateStore,
    *,
    replace: bool = False,
) -> RuntimeStateStore:
    return _default_registry.register(
        store,
        replace=replace,
    )


__all__ = [
    "RuntimeStateDelete",
    "RuntimeStateDomain",
    "RuntimeStateEnvelope",
    "RuntimeStateIdentity",
    "RuntimeStateLifecycle",
    "RuntimeStateMutation",
    "RuntimeStateMutationMode",
    "RuntimeStatePage",
    "RuntimeStateStore",
    "RuntimeStateStoreConflictError",
    "RuntimeStateStoreError",
    "RuntimeStateStoreNotFoundError",
    "RuntimeStateStoreRegistrationError",
    "RuntimeStateStoreRegistry",
    "RuntimeStateStoreRegistrySnapshot",
    "RuntimeStateStoreSnapshot",
    "RuntimeStateStoreValidationError",
    "RuntimeStateTransactionResult",
    "RuntimeStoredState",
    "create_default_runtime_state_stores",
    "get_runtime_state_store_registry",
    "register_runtime_state_store",
]
'''


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def snapshot_protected_files() -> dict[str, str]:
    candidates = [
        PROJECT_ROOT / "backend" / "server" / "main.py",
        RUNTIME_DIR / "runtime_kernel.py",
        RUNTIME_DIR / "runtime_configuration.py",
        RUNTIME_DIR / "runtime_environment.py",
        RUNTIME_DIR / "runtime_service_registry.py",
        RUNTIME_DIR / "runtime_lifecycle.py",
        RUNTIME_DIR / "runtime_boot.py",
        RUNTIME_DIR / "runtime_shutdown.py",
        RUNTIME_DIR / "runtime_versioning.py",
        RUNTIME_DIR / "runtime_compatibility.py",
        RUNTIME_DIR / "runtime_feature_flags.py",
        RUNTIME_DIR / "runtime_capability_negotiation.py",
        RUNTIME_DIR / "runtime_persistence.py",
    ]

    return {
        str(path): sha256_file(path)
        for path in candidates
        if path.exists()
    }


def compile_python_file(path: Path) -> None:
    py_compile.compile(
        str(path),
        doraise=True,
    )


def import_runtime_module(
    module_name: str,
):
    runtime_path = str(RUNTIME_DIR)

    if runtime_path not in sys.path:
        sys.path.insert(
            0,
            runtime_path,
        )

    sys.modules.pop(
        module_name,
        None,
    )

    importlib.invalidate_caches()

    return importlib.import_module(
        module_name
    )


def verify_ast_contract(path: Path) -> None:
    tree = ast.parse(
        path.read_text(
            encoding="utf-8"
        ),
        filename=str(path),
    )

    class_names = {
        node.name
        for node in ast.walk(tree)
        if isinstance(
            node,
            ast.ClassDef,
        )
    }

    required_classes = {
        "RuntimeStateIdentity",
        "RuntimeStateEnvelope",
        "RuntimeStoredState",
        "RuntimeStateMutation",
        "RuntimeStateDelete",
        "RuntimeStatePage",
        "RuntimeStateStoreSnapshot",
        "RuntimeStateTransactionResult",
        "RuntimeStateStore",
        "RuntimeStateStoreRegistry",
        "RuntimeStateStoreRegistrySnapshot",
    }

    missing_classes = (
        required_classes - class_names
    )

    if missing_classes:
        raise AssertionError(
            "Missing required state-store classes: "
            + ", ".join(
                sorted(missing_classes)
            )
        )

    function_names = {
        node.name
        for node in ast.walk(tree)
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        )
    }

    required_functions = {
        "create_default_runtime_state_stores",
        "get_runtime_state_store_registry",
        "register_runtime_state_store",
    }

    missing_functions = (
        required_functions - function_names
    )

    if missing_functions:
        raise AssertionError(
            "Missing required state-store functions: "
            + ", ".join(
                sorted(missing_functions)
            )
        )


def verify_behavior(
    state_module,
    persistence_module,
) -> list[tuple[str, str]]:
    results: list[tuple[str, str]] = []

    Backend = (
        persistence_module
        .InMemoryRuntimePersistenceBackend
    )

    Domain = state_module.RuntimeStateDomain
    Identity = state_module.RuntimeStateIdentity
    Envelope = state_module.RuntimeStateEnvelope
    Lifecycle = (
        state_module.RuntimeStateLifecycle
    )
    Mutation = state_module.RuntimeStateMutation
    MutationMode = (
        state_module.RuntimeStateMutationMode
    )
    Delete = state_module.RuntimeStateDelete
    Store = state_module.RuntimeStateStore
    Registry = (
        state_module.RuntimeStateStoreRegistry
    )

    backend = Backend(
        backend_id="state-store-verification"
    )

    job_store = Store(
        store_id="runtime-state-jobs",
        domain=Domain.JOBS,
        backend=backend,
    )

    now = datetime.now(
        timezone.utc
    )

    identity = Identity(
        domain=Domain.JOBS,
        state_id="job-001",
    )

    envelope = Envelope(
        identity=identity,
        schema_name="runtime.job",
        schema_version="1.0.0",
        state={
            "status": "created",
            "attempts": 0,
        },
        owner_workspace_id="workspace-001",
        owner_organization_id="org-001",
        owner_user_id="user-001",
        correlation_id="correlation-001",
        trace_id="trace-001",
        created_at=now,
        updated_at=now,
        metadata={
            "source": "verification",
        },
    )

    created = job_store.create(
        envelope
    )

    assert created.revision == 1
    assert (
        created.envelope.identity
        == identity
    )

    loaded = job_store.require(
        "job-001"
    )

    assert (
        loaded.envelope.state["status"]
        == "created"
    )

    results.append(
        (
            "Typed logical state create and read",
            "PASS",
        )
    )

    try:
        job_store.create(
            envelope
        )
    except state_module.RuntimeStateStoreConflictError:
        pass
    else:
        raise AssertionError(
            "Duplicate state creation was accepted."
        )

    results.append(
        (
            "Create-only state enforcement",
            "PASS",
        )
    )

    updated_envelope = Envelope(
        identity=identity,
        schema_name="runtime.job",
        schema_version="1.0.0",
        state={
            "status": "running",
            "attempts": 1,
        },
        owner_workspace_id="workspace-001",
        owner_organization_id="org-001",
        owner_user_id="user-001",
        correlation_id="correlation-001",
        trace_id="trace-001",
        created_at=envelope.created_at,
        updated_at=now + timedelta(
            seconds=1
        ),
        metadata=envelope.metadata,
    )

    updated = job_store.update(
        updated_envelope,
        expected_revision=1,
    )

    assert updated.revision == 2
    assert (
        updated.envelope.state["status"]
        == "running"
    )

    try:
        job_store.update(
            updated_envelope,
            expected_revision=1,
        )
    except state_module.RuntimeStateStoreConflictError:
        pass
    else:
        raise AssertionError(
            "Stale state revision was accepted."
        )

    results.append(
        (
            "Revision-aware state updates",
            "PASS",
        )
    )

    current = job_store.require(
        "job-001"
    )

    completed_envelope = Envelope(
        identity=identity,
        schema_name="runtime.job",
        schema_version="1.0.0",
        state={
            "status": "completed",
            "attempts": 1,
        },
        owner_workspace_id="workspace-001",
        created_at=envelope.created_at,
        updated_at=now + timedelta(
            seconds=2
        ),
    )

    completed = job_store.update(
        completed_envelope,
        expected_fingerprint=(
            current.persistence_fingerprint
        ),
    )

    assert completed.revision == 3

    results.append(
        (
            "Fingerprint-aware state updates",
            "PASS",
        )
    )

    queue_store = Store(
        store_id="runtime-state-queues",
        domain=Domain.QUEUES,
        backend=backend,
    )

    try:
        queue_store.create(
            envelope
        )
    except state_module.RuntimeStateStoreValidationError:
        pass
    else:
        raise AssertionError(
            "Cross-domain state was accepted."
        )

    results.append(
        (
            "Logical namespace isolation",
            "PASS",
        )
    )

    partitioned_store = Store(
        store_id="runtime-state-jobs-region-a",
        domain=Domain.JOBS,
        partition="region-a",
        backend=backend,
    )

    partitioned_identity = Identity(
        domain=Domain.JOBS,
        state_id="job-001",
        partition="region-a",
    )

    partitioned_envelope = Envelope(
        identity=partitioned_identity,
        schema_name="runtime.job",
        schema_version="1.0.0",
        state={
            "status": "created",
        },
    )

    partitioned_store.create(
        partitioned_envelope
    )

    assert (
        job_store.require(
            "job-001"
        ).envelope.identity.partition
        is None
    )

    assert (
        partitioned_store.require(
            "job-001"
        ).envelope.identity.partition
        == "region-a"
    )

    results.append(
        (
            "Partition-aware namespace isolation",
            "PASS",
        )
    )

    for index in range(5):
        event_identity = Identity(
            domain=Domain.EVENTS,
            state_id=f"event-{index:03d}",
        )

        event_store = Store(
            store_id=(
                "runtime-state-events-temp"
            ),
            domain=Domain.EVENTS,
            backend=backend,
        )

        if index == 0:
            active_event_store = (
                event_store
            )

        active_event_store.create(
            Envelope(
                identity=event_identity,
                schema_name="runtime.event",
                schema_version="1.0.0",
                state={
                    "sequence": index,
                },
            )
        )

    first_page = active_event_store.list(
        prefix="event-",
        limit=2,
    )

    assert len(
        first_page.states
    ) == 2

    assert first_page.next_cursor is not None

    second_page = active_event_store.list(
        prefix="event-",
        limit=10,
        cursor=first_page.next_cursor,
    )

    assert len(
        second_page.states
    ) == 3

    results.append(
        (
            "Logical listing and pagination",
            "PASS",
        )
    )

    transaction_store = Store(
        store_id="runtime-state-batches",
        domain=Domain.BATCHES,
        backend=backend,
    )

    batch_one = Envelope(
        identity=Identity(
            domain=Domain.BATCHES,
            state_id="batch-001",
        ),
        schema_name="runtime.batch",
        schema_version="1.0.0",
        state={"status": "created"},
    )

    batch_two = Envelope(
        identity=Identity(
            domain=Domain.BATCHES,
            state_id="batch-002",
        ),
        schema_name="runtime.batch",
        schema_version="1.0.0",
        state={"status": "created"},
    )

    transaction_result = (
        transaction_store.transact(
            mutations=(
                Mutation(
                    envelope=batch_one,
                    mode=(
                        MutationMode.CREATE_ONLY
                    ),
                ),
                Mutation(
                    envelope=batch_two,
                    mode=(
                        MutationMode.CREATE_ONLY
                    ),
                ),
            )
        )
    )

    assert (
        transaction_result.committed
        is True
    )

    assert len(
        transaction_result.writes
    ) == 2

    assert len(
        transaction_result.fingerprint
    ) == 64

    results.append(
        (
            "Atomic logical state transaction",
            "PASS",
        )
    )

    rollback_state = Envelope(
        identity=Identity(
            domain=Domain.BATCHES,
            state_id="batch-rollback",
        ),
        schema_name="runtime.batch",
        schema_version="1.0.0",
        state={"status": "temporary"},
    )

    try:
        transaction_store.transact(
            mutations=(
                Mutation(
                    envelope=rollback_state,
                    mode=(
                        MutationMode.CREATE_ONLY
                    ),
                ),
                Mutation(
                    envelope=batch_one,
                    mode=(
                        MutationMode.CREATE_ONLY
                    ),
                ),
            )
        )
    except state_module.RuntimeStateStoreConflictError:
        pass
    else:
        raise AssertionError(
            "Failed logical transaction "
            "did not raise a conflict."
        )

    assert (
        transaction_store.get(
            "batch-rollback"
        )
        is None
    )

    results.append(
        (
            "Logical transaction rollback",
            "PASS",
        )
    )

    batch_two_stored = (
        transaction_store.require(
            "batch-002"
        )
    )

    deleted = transaction_store.delete(
        Delete(
            identity=batch_two.identity,
            expected_revision=(
                batch_two_stored.revision
            ),
        )
    )

    assert deleted is True

    assert (
        transaction_store.get(
            "batch-002"
        )
        is None
    )

    results.append(
        (
            "Conditional logical state deletion",
            "PASS",
        )
    )

    expiring_envelope = Envelope(
        identity=Identity(
            domain=Domain.LEASES,
            state_id="lease-001",
        ),
        schema_name="runtime.lease",
        schema_version="1.0.0",
        state={
            "owner": "worker-001",
        },
        expires_at=(
            now + timedelta(hours=1)
        ),
    )

    lease_store = Store(
        store_id="runtime-state-leases",
        domain=Domain.LEASES,
        backend=backend,
    )

    lease_store.create(
        expiring_envelope
    )

    assert (
        lease_store.require(
            "lease-001"
        ).envelope.expires_at
        is not None
    )

    results.append(
        (
            "State expiration propagation",
            "PASS",
        )
    )

    snapshot_one = job_store.snapshot()
    snapshot_two = job_store.snapshot()

    assert (
        snapshot_one.fingerprint
        == snapshot_two.fingerprint
    )

    assert snapshot_one.record_count == 1

    results.append(
        (
            "Deterministic state-store snapshots",
            "PASS",
        )
    )

    try:
        envelope.schema_name = "changed"
    except Exception:
        pass
    else:
        raise AssertionError(
            "State envelopes must be immutable."
        )

    try:
        created.revision = 99
    except Exception:
        pass
    else:
        raise AssertionError(
            "Stored-state contracts must be immutable."
        )

    results.append(
        (
            "Immutable state-store contracts",
            "PASS",
        )
    )

    registry = Registry()

    registry.register(
        job_store
    )

    registry.register(
        queue_store
    )

    assert (
        registry.get(
            job_store.store_id
        )
        is job_store
    )

    assert (
        registry.resolve(
            Domain.QUEUES
        )
        is queue_store
    )

    registry_snapshot_one = (
        registry.snapshot()
    )

    registry_snapshot_two = (
        registry.snapshot()
    )

    assert (
        registry_snapshot_one.fingerprint
        == registry_snapshot_two.fingerprint
    )

    registry.remove(
        queue_store.store_id
    )

    try:
        registry.resolve(
            Domain.QUEUES
        )
    except state_module.RuntimeStateStoreNotFoundError:
        pass
    else:
        raise AssertionError(
            "Removed logical store remained resolvable."
        )

    results.append(
        (
            "Logical state-store registry",
            "PASS",
        )
    )

    default_registry = (
        state_module
        .create_default_runtime_state_stores(
            backend=Backend(
                backend_id=(
                    "default-state-store-backend"
                )
            )
        )
    )

    default_snapshot = (
        default_registry.snapshot()
    )

    assert len(
        default_snapshot.store_ids
    ) == len(Domain)

    for domain in Domain:
        assert (
            default_registry.resolve(
                domain
            ).domain
            is domain
        )

    results.append(
        (
            "Default runtime state domains",
            "PASS",
        )
    )

    thread_errors: list[str] = []

    thread_store = Store(
        store_id="runtime-state-thread-test",
        domain=Domain.EVENTS,
        partition="thread-test",
        backend=backend,
    )

    def threaded_writer(
        thread_number: int,
    ) -> None:
        try:
            for iteration in range(100):
                threaded_identity = Identity(
                    domain=Domain.EVENTS,
                    state_id=(
                        f"thread-{thread_number}-"
                        f"{iteration}"
                    ),
                    partition="thread-test",
                )

                thread_store.create(
                    Envelope(
                        identity=threaded_identity,
                        schema_name=(
                            "runtime.thread-event"
                        ),
                        schema_version="1.0.0",
                        state={
                            "thread": thread_number,
                            "iteration": iteration,
                        },
                    )
                )

                if (
                    thread_store.get(
                        threaded_identity.state_id
                    )
                    is None
                ):
                    raise AssertionError(
                        "Threaded state was not readable."
                    )
        except Exception as exc:
            thread_errors.append(
                repr(exc)
            )

    threads = [
        threading.Thread(
            target=threaded_writer,
            args=(index,),
        )
        for index in range(8)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    assert not thread_errors

    thread_page = thread_store.list(
        limit=1000,
    )

    assert len(
        thread_page.states
    ) == 800

    results.append(
        (
            "Thread-safe logical state operations",
            "PASS",
        )
    )

    return results


def write_evidence(
    *,
    status: str,
    verification_results: list[
        tuple[str, str]
    ],
    protected_before: dict[str, str],
    protected_after: dict[str, str],
    error: str | None = None,
) -> None:
    EVIDENCE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    evidence = {
        "architecture": (
            "Universal Runtime Infrastructure"
        ),
        "phase": "1.1.13",
        "component": (
            "Runtime State Store Abstraction"
        ),
        "timestamp_utc": TIMESTAMP,
        "status": status,
        "target": str(TARGET),
        "backup": (
            str(BACKUP_FILE)
            if BACKUP_FILE.exists()
            else None
        ),
        "verification": [
            {
                "check": check,
                "status": check_status,
            }
            for check, check_status
            in verification_results
        ],
        "protected_files_before": (
            protected_before
        ),
        "protected_files_after": (
            protected_after
        ),
        "protected_files_unchanged": (
            protected_before
            == protected_after
        ),
        "persistence_interface_integration": (
            "PASS"
            if status == "PASS"
            else "FAIL"
        ),
        "production_backend_integration": (
            "PENDING"
        ),
        "runtime_schema_management_integration": (
            "PENDING"
        ),
        "application_boot_integration": (
            "PENDING"
        ),
        "owner_control_tower_integration": (
            "PENDING"
        ),
        "certification": "NOT CERTIFIED",
        "production_data_modified": False,
        "error": error,
    }

    EVIDENCE_JSON.write_text(
        json.dumps(
            evidence,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    lines = [
        "=" * 78,
        "UNIVERSAL RUNTIME INFRASTRUCTURE",
        (
            "1.1.13 — RUNTIME STATE STORE "
            "ABSTRACTION BUILD EVIDENCE"
        ),
        "=" * 78,
        "",
        f"Timestamp UTC: {TIMESTAMP}",
        f"Status:        {status}",
        f"Target:        {TARGET}",
        f"Backup:        {evidence['backup']}",
        "",
        "VERIFICATION",
        "-" * 78,
    ]

    for check, check_status in verification_results:
        lines.append(
            f"{check}: {check_status}"
        )

    lines.extend(
        [
            "",
            "INTEGRATION STATUS",
            "-" * 78,
            (
                "Persistence Interface integration: "
                + evidence[
                    "persistence_interface_integration"
                ]
            ),
            "Production backend integration:      PENDING",
            "Runtime Schema Management:           PENDING",
            "Application boot integration:        PENDING",
            "Owner Control Tower integration:     PENDING",
            "Certification:                       NOT CERTIFIED",
            "",
            "PROTECTED FILES",
            "-" * 78,
            (
                "Protected existing files unchanged: "
                + (
                    "PASS"
                    if protected_before
                    == protected_after
                    else "FAIL"
                )
            ),
            "",
            "NO PRODUCTION DATA WAS MODIFIED",
        ]
    )

    if error:
        lines.extend(
            [
                "",
                "ERROR",
                "-" * 78,
                error,
            ]
        )

    EVIDENCE_TEXT.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def rollback() -> None:
    if BACKUP_FILE.exists():
        shutil.copy2(
            BACKUP_FILE,
            TARGET,
        )
    elif TARGET.exists():
        TARGET.unlink()


def main() -> int:
    print("=" * 78)
    print("UNIVERSAL RUNTIME INFRASTRUCTURE")
    print(
        "1.1.13 — RUNTIME STATE STORE ABSTRACTION BUILD"
    )
    print("=" * 78)
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Target:       {TARGET}")
    print()

    if not PERSISTENCE_MODULE.exists():
        raise FileNotFoundError(
            "Runtime Persistence Interface is missing: "
            f"{PERSISTENCE_MODULE}"
        )

    RUNTIME_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    EVIDENCE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    protected_before = (
        snapshot_protected_files()
    )

    verification_results: list[
        tuple[str, str]
    ] = []

    if TARGET.exists():
        BACKUP_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.copy2(
            TARGET,
            BACKUP_FILE,
        )

    try:
        TARGET.write_text(
            MODULE_SOURCE,
            encoding="utf-8",
            newline="\n",
        )

        compile_python_file(
            TARGET
        )

        verification_results.append(
            (
                "Runtime State Store compilation",
                "PASS",
            )
        )

        phase_one_modules = [
            RUNTIME_DIR / "runtime_kernel.py",
            RUNTIME_DIR / "runtime_configuration.py",
            RUNTIME_DIR / "runtime_environment.py",
            RUNTIME_DIR / "runtime_service_registry.py",
            RUNTIME_DIR / "runtime_lifecycle.py",
            RUNTIME_DIR / "runtime_boot.py",
            RUNTIME_DIR / "runtime_shutdown.py",
            RUNTIME_DIR / "runtime_versioning.py",
            RUNTIME_DIR / "runtime_compatibility.py",
            RUNTIME_DIR / "runtime_feature_flags.py",
            RUNTIME_DIR / "runtime_capability_negotiation.py",
            RUNTIME_DIR / "runtime_persistence.py",
            TARGET,
        ]

        for module_path in phase_one_modules:
            if module_path.exists():
                compile_python_file(
                    module_path
                )

        verification_results.append(
            (
                "Phase 1 foundation compilation",
                "PASS",
            )
        )

        main_path = (
            PROJECT_ROOT
            / "backend"
            / "server"
            / "main.py"
        )

        if main_path.exists():
            compile_python_file(
                main_path
            )

        verification_results.append(
            (
                "main.py compilation",
                "PASS",
            )
        )

        verify_ast_contract(
            TARGET
        )

        verification_results.append(
            (
                "State Store AST contract",
                "PASS",
            )
        )

        # Import the dependency first under its canonical name.
        # runtime_state_store imports these exact class identities.
        persistence_module = (
            import_runtime_module(
                "runtime_persistence"
            )
        )

        state_module = (
            import_runtime_module(
                "runtime_state_store"
            )
        )

        verification_results.extend(
            verify_behavior(
                state_module,
                persistence_module,
            )
        )

        verification_results.append(
            (
                "Runtime Persistence integration",
                "PASS",
            )
        )

        source_text = TARGET.read_text(
            encoding="utf-8"
        ).lower()

        prohibited_terms = [
            "udare",
            "article_validation",
            "internal_link",
            "semantic_link",
            "website_article",
            "uploaded_document",
            "uucd",
        ]

        matches = [
            term
            for term in prohibited_terms
            if term in source_text
        ]

        if matches:
            raise AssertionError(
                "Pipeline-specific terms found: "
                + ", ".join(matches)
            )

        verification_results.append(
            (
                "Business-logic-agnostic boundary",
                "PASS",
            )
        )

        protected_after = (
            snapshot_protected_files()
        )

        if protected_before != protected_after:
            raise AssertionError(
                "One or more protected files changed."
            )

        verification_results.append(
            (
                "Protected existing files unchanged",
                "PASS",
            )
        )

        write_evidence(
            status="PASS",
            verification_results=(
                verification_results
            ),
            protected_before=protected_before,
            protected_after=protected_after,
        )

    except Exception:
        error_text = traceback.format_exc()

        rollback()

        protected_after_rollback = (
            snapshot_protected_files()
        )

        verification_results.append(
            (
                "Automatic rollback",
                "PASS",
            )
        )

        write_evidence(
            status="FAIL",
            verification_results=(
                verification_results
            ),
            protected_before=protected_before,
            protected_after=(
                protected_after_rollback
            ),
            error=error_text,
        )

        print("ROLLBACK COMPLETE")
        print(
            "The 1.1.13 build failed, so the previous "
            "Runtime State Store file was restored."
        )
        print()
        print(error_text)

        return 1

    print("BUILD VERIFICATION")
    print("-" * 78)

    for check, status in verification_results:
        print(f"{check + ':':<50} {status}")

    print()
    print("FILES")
    print("-" * 78)
    print(f"State Store:   {TARGET}")
    print(f"Evidence JSON: {EVIDENCE_JSON}")
    print(f"Evidence text: {EVIDENCE_TEXT}")
    print()
    print("1.1.13 RUNTIME STATE STORE ABSTRACTION")
    print("IMPLEMENTATION: PASS")
    print("ISOLATED VERIFICATION: PASS")
    print("LOGICAL STATE DOMAINS: PASS")
    print("TYPED STATE ENVELOPES: PASS")
    print("NAMESPACE ISOLATION: PASS")
    print("PARTITION ISOLATION: PASS")
    print("REVISION CONCURRENCY: PASS")
    print("FINGERPRINT CONCURRENCY: PASS")
    print("ATOMIC STATE TRANSACTIONS: PASS")
    print("TRANSACTION ROLLBACK: PASS")
    print("STATE EXPIRATION: PASS")
    print("STATE STORE REGISTRY: PASS")
    print("DETERMINISTIC SNAPSHOTS: PASS")
    print("THREAD SAFETY: PASS")
    print("RUNTIME PERSISTENCE INTEGRATION: PASS")
    print("PRODUCTION BACKEND INTEGRATION: PENDING")
    print("RUNTIME SCHEMA MANAGEMENT: PENDING")
    print("APPLICATION BOOT INTEGRATION: PENDING")
    print("OWNER CONTROL TOWER INTEGRATION: PENDING")
    print("CERTIFICATION: NOT CERTIFIED")
    print()
    print("NO PRODUCTION DATA WAS MODIFIED")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
