from __future__ import annotations

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
