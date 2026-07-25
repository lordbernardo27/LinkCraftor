from __future__ import annotations

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
