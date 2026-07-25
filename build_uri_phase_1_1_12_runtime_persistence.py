from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import py_compile
import shutil
import sys
import threading
import traceback
from datetime import datetime, timezone
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
    / "runtime_persistence.py"
)

EVIDENCE_DIR = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime"
    / "uri_phase_1"
    / "1_1_12_runtime_persistence_interface"
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
    / f"uri_phase1_1_12_runtime_persistence_{TIMESTAMP}"
)

BACKUP_FILE = BACKUP_DIR / TARGET.name

EVIDENCE_JSON = (
    EVIDENCE_DIR
    / f"runtime_persistence_build_{TIMESTAMP}.json"
)

EVIDENCE_TEXT = (
    EVIDENCE_DIR
    / f"runtime_persistence_build_{TIMESTAMP}.txt"
)


MODULE_SOURCE = r'''from __future__ import annotations

"""
Universal Runtime Infrastructure
Phase 1.1.12 — Runtime Persistence Interface

This module defines the storage-agnostic persistence contracts used by the
Universal Runtime Infrastructure.

It does not select a production database or embed pipeline business logic.

Concrete adapters may implement these contracts using relational databases,
distributed key-value stores, durable queue stores, object stores, or other
approved persistence technologies.
"""

import copy
import hashlib
import json
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import Any, Iterable, Mapping


class RuntimePersistenceError(RuntimeError):
    """Base exception for runtime persistence failures."""


class RuntimePersistenceValidationError(RuntimePersistenceError):
    """Raised when persistence contracts are invalid."""


class RuntimePersistenceNotFoundError(RuntimePersistenceError):
    """Raised when a requested record or backend does not exist."""


class RuntimePersistenceConflictError(RuntimePersistenceError):
    """Raised when a write violates a persistence condition."""


class RuntimePersistenceBackendError(RuntimePersistenceError):
    """Raised when a persistence backend operation fails."""


class RuntimePersistenceTransactionError(RuntimePersistenceError):
    """Raised when an atomic transaction cannot be completed."""


class RuntimePersistenceCapability(str, Enum):
    ATOMIC_TRANSACTIONS = "atomic_transactions"
    COMPARE_AND_SET = "compare_and_set"
    CREATE_ONLY = "create_only"
    UPDATE_ONLY = "update_only"
    PREFIX_LISTING = "prefix_listing"
    PAGINATION = "pagination"
    EXPIRATION = "expiration"
    SNAPSHOTS = "snapshots"
    HEALTH_CHECKS = "health_checks"


class RuntimePersistenceWriteMode(str, Enum):
    UPSERT = "upsert"
    CREATE_ONLY = "create_only"
    UPDATE_ONLY = "update_only"
    COMPARE_AND_SET = "compare_and_set"


class RuntimePersistenceOperationType(str, Enum):
    PUT = "put"
    DELETE = "delete"


class RuntimePersistenceHealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _normalise_text(
    value: str,
    *,
    field_name: str,
) -> str:
    if not isinstance(value, str):
        raise RuntimePersistenceValidationError(
            f"{field_name} must be a string."
        )

    normalised = value.strip()

    if not normalised:
        raise RuntimePersistenceValidationError(
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
        raise RuntimePersistenceValidationError(
            f"{field_name} must be a datetime."
        )

    if value.tzinfo is None:
        raise RuntimePersistenceValidationError(
            f"{field_name} must be timezone-aware."
        )

    return value.astimezone(timezone.utc)


def _freeze_mapping(
    value: Mapping[str, Any] | None,
) -> Mapping[str, Any]:
    return MappingProxyType(
        copy.deepcopy(
            dict(value or {})
        )
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


@dataclass(frozen=True, slots=True)
class RuntimePersistenceKey:
    namespace: str
    key: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "namespace",
            _normalise_text(
                self.namespace,
                field_name="namespace",
            ),
        )

        object.__setattr__(
            self,
            "key",
            _normalise_text(
                self.key,
                field_name="key",
            ),
        )

    @property
    def canonical(self) -> str:
        return f"{self.namespace}:{self.key}"


@dataclass(frozen=True, slots=True)
class RuntimePersistenceRecord:
    key: RuntimePersistenceKey
    value: Mapping[str, Any]
    revision: int
    created_at: datetime
    updated_at: datetime
    expires_at: datetime | None = None
    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        if not isinstance(
            self.key,
            RuntimePersistenceKey,
        ):
            raise RuntimePersistenceValidationError(
                "key must be a RuntimePersistenceKey."
            )

        if not isinstance(self.revision, int):
            raise RuntimePersistenceValidationError(
                "revision must be an integer."
            )

        if self.revision < 1:
            raise RuntimePersistenceValidationError(
                "revision must be at least 1."
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
            raise RuntimePersistenceValidationError(
                "created_at and updated_at are required."
            )

        if updated_at < created_at:
            raise RuntimePersistenceValidationError(
                "updated_at must not be earlier than created_at."
            )

        if (
            expires_at is not None
            and expires_at <= created_at
        ):
            raise RuntimePersistenceValidationError(
                "expires_at must be later than created_at."
            )

        object.__setattr__(
            self,
            "value",
            _freeze_mapping(self.value),
        )

        object.__setattr__(
            self,
            "metadata",
            _freeze_mapping(self.metadata),
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

    @property
    def fingerprint(self) -> str:
        return _fingerprint(
            self.to_dict()
        )

    def is_expired(
        self,
        *,
        now: datetime | None = None,
    ) -> bool:
        if self.expires_at is None:
            return False

        reference = now or _utc_now()

        if reference.tzinfo is None:
            raise RuntimePersistenceValidationError(
                "now must be timezone-aware."
            )

        return (
            reference.astimezone(timezone.utc)
            >= self.expires_at
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "namespace": self.key.namespace,
            "key": self.key.key,
            "value": dict(self.value),
            "revision": self.revision,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "expires_at": (
                self.expires_at.isoformat()
                if self.expires_at is not None
                else None
            ),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class RuntimePersistenceWriteCondition:
    mode: RuntimePersistenceWriteMode = (
        RuntimePersistenceWriteMode.UPSERT
    )
    expected_revision: int | None = None
    expected_fingerprint: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(
            self.mode,
            RuntimePersistenceWriteMode,
        ):
            try:
                object.__setattr__(
                    self,
                    "mode",
                    RuntimePersistenceWriteMode(
                        self.mode
                    ),
                )
            except Exception as exc:
                raise RuntimePersistenceValidationError(
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
            raise RuntimePersistenceValidationError(
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
            is RuntimePersistenceWriteMode.COMPARE_AND_SET
            and self.expected_revision is None
            and self.expected_fingerprint is None
        ):
            raise RuntimePersistenceValidationError(
                "COMPARE_AND_SET requires an expected revision "
                "or expected fingerprint."
            )


@dataclass(frozen=True, slots=True)
class RuntimePersistenceWriteResult:
    record: RuntimePersistenceRecord
    created: bool
    previous_revision: int | None
    backend_id: str
    committed_at: datetime

    def __post_init__(self) -> None:
        if not isinstance(
            self.record,
            RuntimePersistenceRecord,
        ):
            raise RuntimePersistenceValidationError(
                "record must be a RuntimePersistenceRecord."
            )

        object.__setattr__(
            self,
            "backend_id",
            _normalise_text(
                self.backend_id,
                field_name="backend_id",
            ),
        )

        committed_at = _normalise_datetime(
            self.committed_at,
            field_name="committed_at",
        )

        if committed_at is None:
            raise RuntimePersistenceValidationError(
                "committed_at is required."
            )

        object.__setattr__(
            self,
            "committed_at",
            committed_at,
        )


@dataclass(frozen=True, slots=True)
class RuntimePersistenceDeleteResult:
    key: RuntimePersistenceKey
    deleted: bool
    previous_revision: int | None
    backend_id: str
    committed_at: datetime

    def __post_init__(self) -> None:
        if not isinstance(
            self.key,
            RuntimePersistenceKey,
        ):
            raise RuntimePersistenceValidationError(
                "key must be a RuntimePersistenceKey."
            )

        object.__setattr__(
            self,
            "backend_id",
            _normalise_text(
                self.backend_id,
                field_name="backend_id",
            ),
        )

        committed_at = _normalise_datetime(
            self.committed_at,
            field_name="committed_at",
        )

        if committed_at is None:
            raise RuntimePersistenceValidationError(
                "committed_at is required."
            )

        object.__setattr__(
            self,
            "committed_at",
            committed_at,
        )


@dataclass(frozen=True, slots=True)
class RuntimePersistencePage:
    records: tuple[RuntimePersistenceRecord, ...]
    next_cursor: str | None
    backend_id: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "records",
            tuple(self.records),
        )

        object.__setattr__(
            self,
            "next_cursor",
            _normalise_optional_text(
                self.next_cursor,
                field_name="next_cursor",
            ),
        )

        object.__setattr__(
            self,
            "backend_id",
            _normalise_text(
                self.backend_id,
                field_name="backend_id",
            ),
        )


@dataclass(frozen=True, slots=True)
class RuntimePersistenceOperation:
    operation_type: RuntimePersistenceOperationType
    key: RuntimePersistenceKey
    value: Mapping[str, Any] | None = None
    condition: RuntimePersistenceWriteCondition = field(
        default_factory=RuntimePersistenceWriteCondition
    )
    expires_at: datetime | None = None
    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        if not isinstance(
            self.operation_type,
            RuntimePersistenceOperationType,
        ):
            try:
                object.__setattr__(
                    self,
                    "operation_type",
                    RuntimePersistenceOperationType(
                        self.operation_type
                    ),
                )
            except Exception as exc:
                raise RuntimePersistenceValidationError(
                    "operation_type is invalid."
                ) from exc

        if not isinstance(
            self.key,
            RuntimePersistenceKey,
        ):
            raise RuntimePersistenceValidationError(
                "key must be a RuntimePersistenceKey."
            )

        if not isinstance(
            self.condition,
            RuntimePersistenceWriteCondition,
        ):
            raise RuntimePersistenceValidationError(
                "condition must be a RuntimePersistenceWriteCondition."
            )

        if (
            self.operation_type
            is RuntimePersistenceOperationType.PUT
            and self.value is None
        ):
            raise RuntimePersistenceValidationError(
                "PUT operations require a value."
            )

        if (
            self.operation_type
            is RuntimePersistenceOperationType.DELETE
            and self.value is not None
        ):
            raise RuntimePersistenceValidationError(
                "DELETE operations must not contain a value."
            )

        object.__setattr__(
            self,
            "value",
            (
                _freeze_mapping(self.value)
                if self.value is not None
                else None
            ),
        )

        object.__setattr__(
            self,
            "expires_at",
            _normalise_datetime(
                self.expires_at,
                field_name="expires_at",
            ),
        )

        object.__setattr__(
            self,
            "metadata",
            _freeze_mapping(self.metadata),
        )


@dataclass(frozen=True, slots=True)
class RuntimePersistenceTransactionResult:
    committed: bool
    write_results: tuple[
        RuntimePersistenceWriteResult,
        ...
    ]
    delete_results: tuple[
        RuntimePersistenceDeleteResult,
        ...
    ]
    backend_id: str
    committed_at: datetime
    fingerprint: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "write_results",
            tuple(self.write_results),
        )

        object.__setattr__(
            self,
            "delete_results",
            tuple(self.delete_results),
        )

        object.__setattr__(
            self,
            "backend_id",
            _normalise_text(
                self.backend_id,
                field_name="backend_id",
            ),
        )

        committed_at = _normalise_datetime(
            self.committed_at,
            field_name="committed_at",
        )

        if committed_at is None:
            raise RuntimePersistenceValidationError(
                "committed_at is required."
            )

        object.__setattr__(
            self,
            "committed_at",
            committed_at,
        )


@dataclass(frozen=True, slots=True)
class RuntimePersistenceHealth:
    backend_id: str
    status: RuntimePersistenceHealthStatus
    checked_at: datetime
    latency_ms: float
    details: Mapping[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "backend_id",
            _normalise_text(
                self.backend_id,
                field_name="backend_id",
            ),
        )

        if not isinstance(
            self.status,
            RuntimePersistenceHealthStatus,
        ):
            try:
                object.__setattr__(
                    self,
                    "status",
                    RuntimePersistenceHealthStatus(
                        self.status
                    ),
                )
            except Exception as exc:
                raise RuntimePersistenceValidationError(
                    "status is invalid."
                ) from exc

        checked_at = _normalise_datetime(
            self.checked_at,
            field_name="checked_at",
        )

        if checked_at is None:
            raise RuntimePersistenceValidationError(
                "checked_at is required."
            )

        if self.latency_ms < 0:
            raise RuntimePersistenceValidationError(
                "latency_ms must not be negative."
            )

        object.__setattr__(
            self,
            "checked_at",
            checked_at,
        )

        object.__setattr__(
            self,
            "details",
            _freeze_mapping(self.details),
        )


@dataclass(frozen=True, slots=True)
class RuntimePersistenceSnapshot:
    backend_id: str
    captured_at: datetime
    record_count: int
    namespace_counts: Mapping[str, int]
    fingerprint: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "backend_id",
            _normalise_text(
                self.backend_id,
                field_name="backend_id",
            ),
        )

        captured_at = _normalise_datetime(
            self.captured_at,
            field_name="captured_at",
        )

        if captured_at is None:
            raise RuntimePersistenceValidationError(
                "captured_at is required."
            )

        if self.record_count < 0:
            raise RuntimePersistenceValidationError(
                "record_count must not be negative."
            )

        object.__setattr__(
            self,
            "captured_at",
            captured_at,
        )

        object.__setattr__(
            self,
            "namespace_counts",
            MappingProxyType(
                dict(self.namespace_counts)
            ),
        )


class RuntimePersistenceBackend(ABC):
    """Abstract persistence interface for runtime state adapters."""

    @property
    @abstractmethod
    def backend_id(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def capabilities(
        self,
    ) -> frozenset[RuntimePersistenceCapability]:
        raise NotImplementedError

    @abstractmethod
    def get(
        self,
        key: RuntimePersistenceKey,
        *,
        include_expired: bool = False,
    ) -> RuntimePersistenceRecord | None:
        raise NotImplementedError

    @abstractmethod
    def put(
        self,
        key: RuntimePersistenceKey,
        value: Mapping[str, Any],
        *,
        condition: RuntimePersistenceWriteCondition | None = None,
        expires_at: datetime | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> RuntimePersistenceWriteResult:
        raise NotImplementedError

    @abstractmethod
    def delete(
        self,
        key: RuntimePersistenceKey,
        *,
        condition: RuntimePersistenceWriteCondition | None = None,
    ) -> RuntimePersistenceDeleteResult:
        raise NotImplementedError

    @abstractmethod
    def list(
        self,
        namespace: str,
        *,
        prefix: str | None = None,
        limit: int = 100,
        cursor: str | None = None,
        include_expired: bool = False,
    ) -> RuntimePersistencePage:
        raise NotImplementedError

    @abstractmethod
    def transact(
        self,
        operations: Iterable[RuntimePersistenceOperation],
    ) -> RuntimePersistenceTransactionResult:
        raise NotImplementedError

    @abstractmethod
    def health_check(
        self,
    ) -> RuntimePersistenceHealth:
        raise NotImplementedError

    @abstractmethod
    def snapshot(
        self,
    ) -> RuntimePersistenceSnapshot:
        raise NotImplementedError


class InMemoryRuntimePersistenceBackend(
    RuntimePersistenceBackend
):
    """
    Thread-safe reference backend used for tests and local verification.

    It is not automatically selected as the production persistence backend.
    """

    def __init__(
        self,
        *,
        backend_id: str = "runtime-memory-reference",
    ) -> None:
        self._backend_id = _normalise_text(
            backend_id,
            field_name="backend_id",
        )

        self._records: dict[
            str,
            RuntimePersistenceRecord,
        ] = {}

        self._lock = threading.RLock()

    @property
    def backend_id(self) -> str:
        return self._backend_id

    @property
    def capabilities(
        self,
    ) -> frozenset[RuntimePersistenceCapability]:
        return frozenset(
            RuntimePersistenceCapability
        )

    def get(
        self,
        key: RuntimePersistenceKey,
        *,
        include_expired: bool = False,
    ) -> RuntimePersistenceRecord | None:
        self._validate_key(key)

        with self._lock:
            record = self._records.get(
                key.canonical
            )

            if record is None:
                return None

            if (
                not include_expired
                and record.is_expired()
            ):
                return None

            return record

    def put(
        self,
        key: RuntimePersistenceKey,
        value: Mapping[str, Any],
        *,
        condition: RuntimePersistenceWriteCondition | None = None,
        expires_at: datetime | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> RuntimePersistenceWriteResult:
        self._validate_key(key)

        effective_condition = (
            condition
            or RuntimePersistenceWriteCondition()
        )

        if not isinstance(
            effective_condition,
            RuntimePersistenceWriteCondition,
        ):
            raise RuntimePersistenceValidationError(
                "condition must be a RuntimePersistenceWriteCondition."
            )

        if not isinstance(value, Mapping):
            raise RuntimePersistenceValidationError(
                "value must be a mapping."
            )

        normalised_expires_at = _normalise_datetime(
            expires_at,
            field_name="expires_at",
        )

        with self._lock:
            return self._put_locked(
                key=key,
                value=value,
                condition=effective_condition,
                expires_at=normalised_expires_at,
                metadata=metadata,
            )

    def delete(
        self,
        key: RuntimePersistenceKey,
        *,
        condition: RuntimePersistenceWriteCondition | None = None,
    ) -> RuntimePersistenceDeleteResult:
        self._validate_key(key)

        effective_condition = (
            condition
            or RuntimePersistenceWriteCondition()
        )

        with self._lock:
            return self._delete_locked(
                key=key,
                condition=effective_condition,
            )

    def list(
        self,
        namespace: str,
        *,
        prefix: str | None = None,
        limit: int = 100,
        cursor: str | None = None,
        include_expired: bool = False,
    ) -> RuntimePersistencePage:
        normalised_namespace = _normalise_text(
            namespace,
            field_name="namespace",
        )

        normalised_prefix = (
            prefix.strip()
            if isinstance(prefix, str)
            else None
        )

        if not isinstance(limit, int) or limit < 1:
            raise RuntimePersistenceValidationError(
                "limit must be a positive integer."
            )

        if limit > 10000:
            raise RuntimePersistenceValidationError(
                "limit must not exceed 10000."
            )

        start_index = 0

        if cursor is not None:
            try:
                start_index = int(cursor)
            except (TypeError, ValueError) as exc:
                raise RuntimePersistenceValidationError(
                    "cursor is invalid."
                ) from exc

            if start_index < 0:
                raise RuntimePersistenceValidationError(
                    "cursor must not be negative."
                )

        with self._lock:
            records = [
                record
                for record in self._records.values()
                if (
                    record.key.namespace
                    == normalised_namespace
                    and (
                        normalised_prefix is None
                        or record.key.key.startswith(
                            normalised_prefix
                        )
                    )
                    and (
                        include_expired
                        or not record.is_expired()
                    )
                )
            ]

            records.sort(
                key=lambda item: item.key.key
            )

            selected = records[
                start_index:
                start_index + limit
            ]

            next_index = start_index + len(
                selected
            )

            next_cursor = (
                str(next_index)
                if next_index < len(records)
                else None
            )

            return RuntimePersistencePage(
                records=tuple(selected),
                next_cursor=next_cursor,
                backend_id=self.backend_id,
            )

    def transact(
        self,
        operations: Iterable[
            RuntimePersistenceOperation
        ],
    ) -> RuntimePersistenceTransactionResult:
        operation_tuple = tuple(operations)

        if not operation_tuple:
            raise RuntimePersistenceValidationError(
                "A transaction requires at least one operation."
            )

        for operation in operation_tuple:
            if not isinstance(
                operation,
                RuntimePersistenceOperation,
            ):
                raise RuntimePersistenceValidationError(
                    "operations must contain "
                    "RuntimePersistenceOperation values."
                )

        with self._lock:
            original_records = dict(
                self._records
            )

            write_results: list[
                RuntimePersistenceWriteResult
            ] = []

            delete_results: list[
                RuntimePersistenceDeleteResult
            ] = []

            try:
                for operation in operation_tuple:
                    if (
                        operation.operation_type
                        is RuntimePersistenceOperationType.PUT
                    ):
                        assert operation.value is not None

                        write_results.append(
                            self._put_locked(
                                key=operation.key,
                                value=operation.value,
                                condition=operation.condition,
                                expires_at=(
                                    operation.expires_at
                                ),
                                metadata=(
                                    operation.metadata
                                ),
                            )
                        )
                    else:
                        delete_results.append(
                            self._delete_locked(
                                key=operation.key,
                                condition=operation.condition,
                            )
                        )
            except Exception as exc:
                self._records = original_records

                if isinstance(
                    exc,
                    RuntimePersistenceError,
                ):
                    raise RuntimePersistenceTransactionError(
                        "Transaction rolled back because an "
                        "operation failed."
                    ) from exc

                raise

            committed_at = _utc_now()

            payload = {
                "backend_id": self.backend_id,
                "writes": [
                    {
                        "key": result.record.key.canonical,
                        "revision": result.record.revision,
                        "created": result.created,
                    }
                    for result in write_results
                ],
                "deletes": [
                    {
                        "key": result.key.canonical,
                        "deleted": result.deleted,
                        "previous_revision": (
                            result.previous_revision
                        ),
                    }
                    for result in delete_results
                ],
            }

            return RuntimePersistenceTransactionResult(
                committed=True,
                write_results=tuple(write_results),
                delete_results=tuple(delete_results),
                backend_id=self.backend_id,
                committed_at=committed_at,
                fingerprint=_fingerprint(payload),
            )

    def health_check(
        self,
    ) -> RuntimePersistenceHealth:
        started = _utc_now()

        with self._lock:
            record_count = len(
                self._records
            )

        completed = _utc_now()

        latency_ms = (
            completed - started
        ).total_seconds() * 1000.0

        return RuntimePersistenceHealth(
            backend_id=self.backend_id,
            status=(
                RuntimePersistenceHealthStatus.HEALTHY
            ),
            checked_at=completed,
            latency_ms=latency_ms,
            details={
                "record_count": record_count,
                "backend_type": "in_memory_reference",
            },
        )

    def snapshot(
        self,
    ) -> RuntimePersistenceSnapshot:
        with self._lock:
            records = tuple(
                sorted(
                    self._records.values(),
                    key=lambda item: item.key.canonical,
                )
            )

            namespace_counts: dict[str, int] = {}

            for record in records:
                namespace_counts[
                    record.key.namespace
                ] = (
                    namespace_counts.get(
                        record.key.namespace,
                        0,
                    )
                    + 1
                )

            payload = {
                "backend_id": self.backend_id,
                "records": [
                    record.to_dict()
                    for record in records
                ],
                "namespace_counts": (
                    namespace_counts
                ),
            }

            return RuntimePersistenceSnapshot(
                backend_id=self.backend_id,
                captured_at=_utc_now(),
                record_count=len(records),
                namespace_counts=namespace_counts,
                fingerprint=_fingerprint(payload),
            )

    def _put_locked(
        self,
        *,
        key: RuntimePersistenceKey,
        value: Mapping[str, Any],
        condition: RuntimePersistenceWriteCondition,
        expires_at: datetime | None,
        metadata: Mapping[str, Any] | None,
    ) -> RuntimePersistenceWriteResult:
        existing = self._records.get(
            key.canonical
        )

        self._validate_write_condition(
            existing=existing,
            condition=condition,
        )

        now = _utc_now()

        created = existing is None

        revision = (
            1
            if existing is None
            else existing.revision + 1
        )

        record = RuntimePersistenceRecord(
            key=key,
            value=value,
            revision=revision,
            created_at=(
                now
                if existing is None
                else existing.created_at
            ),
            updated_at=now,
            expires_at=expires_at,
            metadata=metadata or {},
        )

        self._records[
            key.canonical
        ] = record

        return RuntimePersistenceWriteResult(
            record=record,
            created=created,
            previous_revision=(
                existing.revision
                if existing is not None
                else None
            ),
            backend_id=self.backend_id,
            committed_at=now,
        )

    def _delete_locked(
        self,
        *,
        key: RuntimePersistenceKey,
        condition: RuntimePersistenceWriteCondition,
    ) -> RuntimePersistenceDeleteResult:
        existing = self._records.get(
            key.canonical
        )

        self._validate_delete_condition(
            existing=existing,
            condition=condition,
        )

        now = _utc_now()

        if existing is None:
            return RuntimePersistenceDeleteResult(
                key=key,
                deleted=False,
                previous_revision=None,
                backend_id=self.backend_id,
                committed_at=now,
            )

        del self._records[
            key.canonical
        ]

        return RuntimePersistenceDeleteResult(
            key=key,
            deleted=True,
            previous_revision=existing.revision,
            backend_id=self.backend_id,
            committed_at=now,
        )

    @staticmethod
    def _validate_key(
        key: RuntimePersistenceKey,
    ) -> None:
        if not isinstance(
            key,
            RuntimePersistenceKey,
        ):
            raise RuntimePersistenceValidationError(
                "key must be a RuntimePersistenceKey."
            )

    @staticmethod
    def _validate_write_condition(
        *,
        existing: RuntimePersistenceRecord | None,
        condition: RuntimePersistenceWriteCondition,
    ) -> None:
        if (
            condition.mode
            is RuntimePersistenceWriteMode.CREATE_ONLY
            and existing is not None
        ):
            raise RuntimePersistenceConflictError(
                "CREATE_ONLY write rejected because "
                "the record already exists."
            )

        if (
            condition.mode
            is RuntimePersistenceWriteMode.UPDATE_ONLY
            and existing is None
        ):
            raise RuntimePersistenceConflictError(
                "UPDATE_ONLY write rejected because "
                "the record does not exist."
            )

        if (
            condition.mode
            is RuntimePersistenceWriteMode.COMPARE_AND_SET
        ):
            if existing is None:
                raise RuntimePersistenceConflictError(
                    "COMPARE_AND_SET rejected because "
                    "the record does not exist."
                )

            if (
                condition.expected_revision is not None
                and existing.revision
                != condition.expected_revision
            ):
                raise RuntimePersistenceConflictError(
                    "COMPARE_AND_SET revision mismatch."
                )

            if (
                condition.expected_fingerprint is not None
                and existing.fingerprint
                != condition.expected_fingerprint
            ):
                raise RuntimePersistenceConflictError(
                    "COMPARE_AND_SET fingerprint mismatch."
                )

    @staticmethod
    def _validate_delete_condition(
        *,
        existing: RuntimePersistenceRecord | None,
        condition: RuntimePersistenceWriteCondition,
    ) -> None:
        if (
            condition.mode
            is RuntimePersistenceWriteMode.UPDATE_ONLY
            and existing is None
        ):
            raise RuntimePersistenceConflictError(
                "Conditional delete rejected because "
                "the record does not exist."
            )

        if (
            condition.mode
            is RuntimePersistenceWriteMode.CREATE_ONLY
        ):
            raise RuntimePersistenceValidationError(
                "CREATE_ONLY is not valid for delete operations."
            )

        if (
            condition.mode
            is RuntimePersistenceWriteMode.COMPARE_AND_SET
        ):
            if existing is None:
                raise RuntimePersistenceConflictError(
                    "COMPARE_AND_SET delete rejected because "
                    "the record does not exist."
                )

            if (
                condition.expected_revision is not None
                and existing.revision
                != condition.expected_revision
            ):
                raise RuntimePersistenceConflictError(
                    "COMPARE_AND_SET delete revision mismatch."
                )

            if (
                condition.expected_fingerprint is not None
                and existing.fingerprint
                != condition.expected_fingerprint
            ):
                raise RuntimePersistenceConflictError(
                    "COMPARE_AND_SET delete fingerprint mismatch."
                )


@dataclass(frozen=True, slots=True)
class RuntimePersistenceRegistrySnapshot:
    generation: int
    active_backend_id: str | None
    backend_ids: tuple[str, ...]
    captured_at: datetime
    fingerprint: str


class RuntimePersistenceRegistry:
    """Thread-safe registry of approved runtime persistence backends."""

    def __init__(self) -> None:
        self._backends: dict[
            str,
            RuntimePersistenceBackend,
        ] = {}

        self._active_backend_id: str | None = None
        self._generation = 0
        self._lock = threading.RLock()

    @property
    def generation(self) -> int:
        with self._lock:
            return self._generation

    @property
    def active_backend_id(self) -> str | None:
        with self._lock:
            return self._active_backend_id

    def register(
        self,
        backend: RuntimePersistenceBackend,
        *,
        replace: bool = False,
        make_active: bool = False,
    ) -> RuntimePersistenceBackend:
        if not isinstance(
            backend,
            RuntimePersistenceBackend,
        ):
            raise RuntimePersistenceValidationError(
                "backend must implement RuntimePersistenceBackend."
            )

        backend_id = _normalise_text(
            backend.backend_id,
            field_name="backend_id",
        )

        with self._lock:
            if (
                backend_id in self._backends
                and not replace
            ):
                raise RuntimePersistenceConflictError(
                    f"Persistence backend already exists: {backend_id}"
                )

            self._backends[
                backend_id
            ] = backend

            if (
                make_active
                or self._active_backend_id is None
            ):
                self._active_backend_id = backend_id

            self._generation += 1

            return backend

    def remove(
        self,
        backend_id: str,
    ) -> RuntimePersistenceBackend:
        normalised = _normalise_text(
            backend_id,
            field_name="backend_id",
        )

        with self._lock:
            try:
                backend = self._backends.pop(
                    normalised
                )
            except KeyError as exc:
                raise RuntimePersistenceNotFoundError(
                    f"Persistence backend not found: {normalised}"
                ) from exc

            if self._active_backend_id == normalised:
                self._active_backend_id = (
                    sorted(self._backends)[0]
                    if self._backends
                    else None
                )

            self._generation += 1

            return backend

    def set_active(
        self,
        backend_id: str,
    ) -> None:
        normalised = _normalise_text(
            backend_id,
            field_name="backend_id",
        )

        with self._lock:
            if normalised not in self._backends:
                raise RuntimePersistenceNotFoundError(
                    f"Persistence backend not found: {normalised}"
                )

            self._active_backend_id = normalised
            self._generation += 1

    def get(
        self,
        backend_id: str,
    ) -> RuntimePersistenceBackend:
        normalised = _normalise_text(
            backend_id,
            field_name="backend_id",
        )

        with self._lock:
            backend = self._backends.get(
                normalised
            )

            if backend is None:
                raise RuntimePersistenceNotFoundError(
                    f"Persistence backend not found: {normalised}"
                )

            return backend

    def get_active(
        self,
    ) -> RuntimePersistenceBackend:
        with self._lock:
            if self._active_backend_id is None:
                raise RuntimePersistenceNotFoundError(
                    "No active runtime persistence backend is configured."
                )

            return self._backends[
                self._active_backend_id
            ]

    def snapshot(
        self,
    ) -> RuntimePersistenceRegistrySnapshot:
        with self._lock:
            backend_ids = tuple(
                sorted(self._backends)
            )

            payload = {
                "generation": self._generation,
                "active_backend_id": (
                    self._active_backend_id
                ),
                "backend_ids": backend_ids,
            }

            return RuntimePersistenceRegistrySnapshot(
                generation=self._generation,
                active_backend_id=(
                    self._active_backend_id
                ),
                backend_ids=backend_ids,
                captured_at=_utc_now(),
                fingerprint=_fingerprint(payload),
            )


_default_registry = RuntimePersistenceRegistry()


def get_runtime_persistence_registry(
) -> RuntimePersistenceRegistry:
    return _default_registry


def register_runtime_persistence_backend(
    backend: RuntimePersistenceBackend,
    *,
    replace: bool = False,
    make_active: bool = False,
) -> RuntimePersistenceBackend:
    return _default_registry.register(
        backend,
        replace=replace,
        make_active=make_active,
    )


def get_active_runtime_persistence_backend(
) -> RuntimePersistenceBackend:
    return _default_registry.get_active()


__all__ = [
    "InMemoryRuntimePersistenceBackend",
    "RuntimePersistenceBackend",
    "RuntimePersistenceBackendError",
    "RuntimePersistenceCapability",
    "RuntimePersistenceConflictError",
    "RuntimePersistenceDeleteResult",
    "RuntimePersistenceError",
    "RuntimePersistenceHealth",
    "RuntimePersistenceHealthStatus",
    "RuntimePersistenceKey",
    "RuntimePersistenceNotFoundError",
    "RuntimePersistenceOperation",
    "RuntimePersistenceOperationType",
    "RuntimePersistencePage",
    "RuntimePersistenceRecord",
    "RuntimePersistenceRegistry",
    "RuntimePersistenceRegistrySnapshot",
    "RuntimePersistenceSnapshot",
    "RuntimePersistenceTransactionError",
    "RuntimePersistenceTransactionResult",
    "RuntimePersistenceValidationError",
    "RuntimePersistenceWriteCondition",
    "RuntimePersistenceWriteMode",
    "RuntimePersistenceWriteResult",
    "get_active_runtime_persistence_backend",
    "get_runtime_persistence_registry",
    "register_runtime_persistence_backend",
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


def import_module_from_path(
    module_name: str,
    path: Path,
):
    sys.modules.pop(
        module_name,
        None,
    )

    spec = importlib.util.spec_from_file_location(
        module_name,
        path,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(
            f"Unable to import module: {path}"
        )

    module = importlib.util.module_from_spec(
        spec
    )

    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    return module


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
        if isinstance(node, ast.ClassDef)
    }

    required_classes = {
        "RuntimePersistenceKey",
        "RuntimePersistenceRecord",
        "RuntimePersistenceWriteCondition",
        "RuntimePersistenceWriteResult",
        "RuntimePersistenceDeleteResult",
        "RuntimePersistencePage",
        "RuntimePersistenceOperation",
        "RuntimePersistenceTransactionResult",
        "RuntimePersistenceHealth",
        "RuntimePersistenceSnapshot",
        "RuntimePersistenceBackend",
        "InMemoryRuntimePersistenceBackend",
        "RuntimePersistenceRegistry",
        "RuntimePersistenceRegistrySnapshot",
    }

    missing_classes = (
        required_classes - class_names
    )

    if missing_classes:
        raise AssertionError(
            "Missing required persistence classes: "
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
        "get_runtime_persistence_registry",
        "register_runtime_persistence_backend",
        "get_active_runtime_persistence_backend",
    }

    missing_functions = (
        required_functions - function_names
    )

    if missing_functions:
        raise AssertionError(
            "Missing required persistence functions: "
            + ", ".join(
                sorted(missing_functions)
            )
        )


def verify_behavior(
    module,
) -> list[tuple[str, str]]:
    results: list[tuple[str, str]] = []

    Key = module.RuntimePersistenceKey
    Condition = (
        module.RuntimePersistenceWriteCondition
    )
    Mode = module.RuntimePersistenceWriteMode
    Operation = module.RuntimePersistenceOperation
    OperationType = (
        module.RuntimePersistenceOperationType
    )
    Backend = (
        module.InMemoryRuntimePersistenceBackend
    )
    Registry = module.RuntimePersistenceRegistry
    Capability = module.RuntimePersistenceCapability

    backend = Backend(
        backend_id="verification-backend"
    )

    required_capabilities = {
        Capability.ATOMIC_TRANSACTIONS,
        Capability.COMPARE_AND_SET,
        Capability.CREATE_ONLY,
        Capability.UPDATE_ONLY,
        Capability.PREFIX_LISTING,
        Capability.PAGINATION,
        Capability.EXPIRATION,
        Capability.SNAPSHOTS,
        Capability.HEALTH_CHECKS,
    }

    assert required_capabilities.issubset(
        backend.capabilities
    )

    results.append(
        (
            "Persistence backend capability contract",
            "PASS",
        )
    )

    key = Key(
        namespace="runtime.jobs",
        key="job-001",
    )

    create_result = backend.put(
        key,
        {
            "status": "queued",
            "attempts": 0,
        },
        condition=Condition(
            mode=Mode.CREATE_ONLY,
        ),
        metadata={
            "workspace_id": "workspace-001",
        },
    )

    assert create_result.created is True
    assert create_result.record.revision == 1
    assert create_result.previous_revision is None

    stored = backend.get(key)

    assert stored is not None
    assert stored.value["status"] == "queued"
    assert stored.revision == 1

    results.append(
        (
            "Namespaced create and read",
            "PASS",
        )
    )

    try:
        backend.put(
            key,
            {"status": "duplicate"},
            condition=Condition(
                mode=Mode.CREATE_ONLY,
            ),
        )
    except module.RuntimePersistenceConflictError:
        pass
    else:
        raise AssertionError(
            "CREATE_ONLY did not reject an existing record."
        )

    results.append(
        (
            "Create-only conflict enforcement",
            "PASS",
        )
    )

    missing_key = Key(
        namespace="runtime.jobs",
        key="job-missing",
    )

    try:
        backend.put(
            missing_key,
            {"status": "running"},
            condition=Condition(
                mode=Mode.UPDATE_ONLY,
            ),
        )
    except module.RuntimePersistenceConflictError:
        pass
    else:
        raise AssertionError(
            "UPDATE_ONLY did not reject a missing record."
        )

    results.append(
        (
            "Update-only conflict enforcement",
            "PASS",
        )
    )

    update_result = backend.put(
        key,
        {
            "status": "running",
            "attempts": 1,
        },
        condition=Condition(
            mode=Mode.COMPARE_AND_SET,
            expected_revision=1,
        ),
    )

    assert update_result.created is False
    assert update_result.previous_revision == 1
    assert update_result.record.revision == 2
    assert (
        update_result.record.value["status"]
        == "running"
    )

    results.append(
        (
            "Revision compare-and-set",
            "PASS",
        )
    )

    try:
        backend.put(
            key,
            {"status": "invalid"},
            condition=Condition(
                mode=Mode.COMPARE_AND_SET,
                expected_revision=1,
            ),
        )
    except module.RuntimePersistenceConflictError:
        pass
    else:
        raise AssertionError(
            "Stale compare-and-set revision was accepted."
        )

    current = backend.get(key)

    assert current is not None

    fingerprint_update = backend.put(
        key,
        {
            "status": "completed",
            "attempts": 1,
        },
        condition=Condition(
            mode=Mode.COMPARE_AND_SET,
            expected_fingerprint=(
                current.fingerprint
            ),
        ),
    )

    assert fingerprint_update.record.revision == 3

    results.append(
        (
            "Fingerprint compare-and-set",
            "PASS",
        )
    )

    now = datetime.now(timezone.utc)

    expired_key = Key(
        namespace="runtime.leases",
        key="lease-expired",
    )

    backend.put(
        expired_key,
        {"worker_id": "worker-001"},
        expires_at=now.replace(
            year=now.year + 1
        ),
    )

    future_record = backend.get(
        expired_key
    )

    assert future_record is not None

    past_key = Key(
        namespace="runtime.leases",
        key="lease-expired-immediate",
    )

    past_record_result = backend.put(
        past_key,
        {"worker_id": "worker-002"},
    )

    internal_record = (
        past_record_result.record
    )

    manually_expired = (
        module.RuntimePersistenceRecord(
            key=internal_record.key,
            value=internal_record.value,
            revision=internal_record.revision,
            created_at=(
                internal_record.created_at
            ),
            updated_at=(
                internal_record.updated_at
            ),
            expires_at=(
                internal_record.created_at.replace(
                    year=(
                        internal_record.created_at.year
                        + 1
                    )
                )
            ),
            metadata=internal_record.metadata,
        )
    )

    assert manually_expired.is_expired(
        now=manually_expired.expires_at
    )

    results.append(
        (
            "Record expiration contract",
            "PASS",
        )
    )

    for index in range(5):
        backend.put(
            Key(
                namespace="runtime.events",
                key=f"event-{index:03d}",
            ),
            {
                "sequence": index,
            },
        )

    first_page = backend.list(
        "runtime.events",
        prefix="event-",
        limit=2,
    )

    assert len(first_page.records) == 2
    assert first_page.next_cursor is not None

    second_page = backend.list(
        "runtime.events",
        prefix="event-",
        limit=2,
        cursor=first_page.next_cursor,
    )

    assert len(second_page.records) == 2

    third_page = backend.list(
        "runtime.events",
        prefix="event-",
        limit=2,
        cursor=second_page.next_cursor,
    )

    assert len(third_page.records) == 1
    assert third_page.next_cursor is None

    results.append(
        (
            "Prefix listing and pagination",
            "PASS",
        )
    )

    transaction_key_one = Key(
        namespace="runtime.transactions",
        key="record-001",
    )

    transaction_key_two = Key(
        namespace="runtime.transactions",
        key="record-002",
    )

    transaction_result = backend.transact(
        (
            Operation(
                operation_type=(
                    OperationType.PUT
                ),
                key=transaction_key_one,
                value={"value": 1},
                condition=Condition(
                    mode=Mode.CREATE_ONLY,
                ),
            ),
            Operation(
                operation_type=(
                    OperationType.PUT
                ),
                key=transaction_key_two,
                value={"value": 2},
                condition=Condition(
                    mode=Mode.CREATE_ONLY,
                ),
            ),
        )
    )

    assert transaction_result.committed is True
    assert len(
        transaction_result.write_results
    ) == 2
    assert len(
        transaction_result.fingerprint
    ) == 64

    assert backend.get(
        transaction_key_one
    ) is not None

    assert backend.get(
        transaction_key_two
    ) is not None

    results.append(
        (
            "Atomic multi-record transaction",
            "PASS",
        )
    )

    rollback_key = Key(
        namespace="runtime.transactions",
        key="rollback-record",
    )

    try:
        backend.transact(
            (
                Operation(
                    operation_type=(
                        OperationType.PUT
                    ),
                    key=rollback_key,
                    value={"value": "temporary"},
                    condition=Condition(
                        mode=Mode.CREATE_ONLY,
                    ),
                ),
                Operation(
                    operation_type=(
                        OperationType.PUT
                    ),
                    key=transaction_key_one,
                    value={"value": "conflict"},
                    condition=Condition(
                        mode=Mode.CREATE_ONLY,
                    ),
                ),
            )
        )
    except module.RuntimePersistenceTransactionError:
        pass
    else:
        raise AssertionError(
            "Failed transaction did not roll back."
        )

    assert backend.get(
        rollback_key
    ) is None

    assert (
        backend.get(
            transaction_key_one
        ).value["value"]
        == 1
    )

    results.append(
        (
            "Atomic transaction rollback",
            "PASS",
        )
    )

    transaction_record = backend.get(
        transaction_key_two
    )

    assert transaction_record is not None

    delete_result = backend.delete(
        transaction_key_two,
        condition=Condition(
            mode=Mode.COMPARE_AND_SET,
            expected_revision=(
                transaction_record.revision
            ),
        ),
    )

    assert delete_result.deleted is True
    assert backend.get(
        transaction_key_two
    ) is None

    results.append(
        (
            "Conditional record deletion",
            "PASS",
        )
    )

    health = backend.health_check()

    assert (
        health.status.value
        == "healthy"
    )

    assert health.latency_ms >= 0

    snapshot_one = backend.snapshot()
    snapshot_two = backend.snapshot()

    assert (
        snapshot_one.fingerprint
        == snapshot_two.fingerprint
    )

    assert snapshot_one.record_count >= 1

    results.append(
        (
            "Health checks and deterministic snapshots",
            "PASS",
        )
    )

    try:
        create_result.record.revision = 99
    except Exception:
        pass
    else:
        raise AssertionError(
            "Persistence records must be immutable."
        )

    try:
        transaction_result.committed = False
    except Exception:
        pass
    else:
        raise AssertionError(
            "Transaction results must be immutable."
        )

    results.append(
        (
            "Immutable persistence contracts",
            "PASS",
        )
    )

    registry = Registry()

    registry.register(
        backend,
        make_active=True,
    )

    assert (
        registry.get_active().backend_id
        == backend.backend_id
    )

    second_backend = Backend(
        backend_id="verification-secondary"
    )

    registry.register(
        second_backend
    )

    registry.set_active(
        second_backend.backend_id
    )

    assert (
        registry.get_active().backend_id
        == second_backend.backend_id
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
        second_backend.backend_id
    )

    assert (
        registry.get_active().backend_id
        == backend.backend_id
    )

    results.append(
        (
            "Persistence backend registry",
            "PASS",
        )
    )

    thread_errors: list[str] = []

    def threaded_writer(
        thread_number: int,
    ) -> None:
        try:
            for iteration in range(100):
                thread_key = Key(
                    namespace="runtime.thread-test",
                    key=(
                        f"thread-{thread_number}-"
                        f"{iteration}"
                    ),
                )

                backend.put(
                    thread_key,
                    {
                        "thread": thread_number,
                        "iteration": iteration,
                    },
                    condition=Condition(
                        mode=Mode.CREATE_ONLY,
                    ),
                )

                read_back = backend.get(
                    thread_key
                )

                if read_back is None:
                    raise AssertionError(
                        "Threaded write was not readable."
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

    threaded_page = backend.list(
        "runtime.thread-test",
        limit=1000,
    )

    assert len(
        threaded_page.records
    ) == 800

    results.append(
        (
            "Thread-safe persistence operations",
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
        "phase": "1.1.12",
        "component": (
            "Runtime Persistence Interface"
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
        "production_backend_selection": (
            "PENDING"
        ),
        "runtime_state_store_integration": (
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
            "1.1.12 — RUNTIME PERSISTENCE "
            "INTERFACE BUILD EVIDENCE"
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
            "Production backend selection:       PENDING",
            "Runtime State Store integration:    PENDING",
            "Application boot integration:       PENDING",
            "Owner Control Tower integration:    PENDING",
            "Certification:                      NOT CERTIFIED",
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
        "1.1.12 — RUNTIME PERSISTENCE INTERFACE BUILD"
    )
    print("=" * 78)
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Target:       {TARGET}")
    print()

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
                "Runtime Persistence compilation",
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
                "Persistence AST contract",
                "PASS",
            )
        )

        module = import_module_from_path(
            (
                "uri_runtime_persistence_"
                "verification"
            ),
            TARGET,
        )

        verification_results.extend(
            verify_behavior(module)
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
            "The 1.1.12 build failed, so the previous "
            "Runtime Persistence file was restored."
        )
        print()
        print(error_text)

        return 1

    print("BUILD VERIFICATION")
    print("-" * 78)

    for check, status in verification_results:
        print(f"{check + ':':<48} {status}")

    print()
    print("FILES")
    print("-" * 78)
    print(f"Persistence interface: {TARGET}")
    print(f"Evidence JSON:         {EVIDENCE_JSON}")
    print(f"Evidence text:         {EVIDENCE_TEXT}")
    print()
    print("1.1.12 RUNTIME PERSISTENCE INTERFACE")
    print("IMPLEMENTATION: PASS")
    print("ISOLATED VERIFICATION: PASS")
    print("STORAGE-AGNOSTIC CONTRACT: PASS")
    print("NAMESPACED RECORDS: PASS")
    print("OPTIMISTIC CONCURRENCY: PASS")
    print("COMPARE-AND-SET: PASS")
    print("ATOMIC TRANSACTIONS: PASS")
    print("TRANSACTION ROLLBACK: PASS")
    print("PREFIX LISTING AND PAGINATION: PASS")
    print("EXPIRATION CONTRACT: PASS")
    print("HEALTH CHECKS: PASS")
    print("DETERMINISTIC SNAPSHOTS: PASS")
    print("BACKEND REGISTRY: PASS")
    print("THREAD SAFETY: PASS")
    print("PRODUCTION BACKEND SELECTION: PENDING")
    print("RUNTIME STATE STORE INTEGRATION: PENDING")
    print("APPLICATION BOOT INTEGRATION: PENDING")
    print("OWNER CONTROL TOWER INTEGRATION: PENDING")
    print("CERTIFICATION: NOT CERTIFIED")
    print()
    print("NO PRODUCTION DATA WAS MODIFIED")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
