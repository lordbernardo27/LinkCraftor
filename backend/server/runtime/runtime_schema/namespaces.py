# -*- coding: utf-8 -*-
"""Runtime Schema Namespace Management.

Namespaces partition the runtime schema universe.

The frozen ``runtime`` and ``runtime.*`` namespace family belongs exclusively
to the Universal Runtime Infrastructure. Product or pipeline code cannot
register, replace, remove, or use those namespaces unless acting explicitly
as the runtime itself.

This module remains business-logic agnostic.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from .serialization import structure_fingerprint
from .types import (
    MAX_DESCRIPTION_LENGTH,
    RESERVED_RUNTIME_PREFIX,
    RESERVED_RUNTIME_ROOT,
    CompatibilityMode,
    SchemaRegistryError,
    is_canonical_timestamp,
    is_reserved_runtime_namespace,
    is_valid_identifier,
    is_valid_namespace,
    utc_now_iso,
)


def is_reserved_namespace(
    namespace: object,
) -> bool:
    """Return whether *namespace* belongs to ``runtime`` or ``runtime.*``."""
    return is_reserved_runtime_namespace(
        namespace
    )


@dataclass(
    frozen=True,
    slots=True,
)
class NamespaceRecord:
    """Immutable registration record for one schema namespace."""

    namespace: str
    owner_id: str
    default_compatibility_mode: CompatibilityMode = (
        CompatibilityMode.BACKWARD
    )
    description: str = ""
    registered_at: str = field(
        default_factory=utc_now_iso
    )

    def __post_init__(self) -> None:
        if not is_valid_namespace(
            self.namespace
        ):
            raise SchemaRegistryError(
                f"invalid namespace: {self.namespace!r}"
            )

        if not is_valid_identifier(
            self.owner_id
        ):
            raise SchemaRegistryError(
                f"invalid owner_id: {self.owner_id!r}"
            )

        if not isinstance(
            self.default_compatibility_mode,
            CompatibilityMode,
        ):
            try:
                object.__setattr__(
                    self,
                    "default_compatibility_mode",
                    CompatibilityMode(
                        self.default_compatibility_mode
                    ),
                )
            except (
                TypeError,
                ValueError,
            ) as exc:
                raise SchemaRegistryError(
                    "invalid default compatibility mode"
                ) from exc

        if not isinstance(
            self.description,
            str,
        ):
            raise SchemaRegistryError(
                "description must be a string"
            )

        if (
            len(self.description)
            > MAX_DESCRIPTION_LENGTH
        ):
            raise SchemaRegistryError(
                "description exceeds "
                f"{MAX_DESCRIPTION_LENGTH} characters"
            )

        if not is_canonical_timestamp(
            self.registered_at
        ):
            raise SchemaRegistryError(
                "registered_at must be a canonical "
                "UTC timestamp"
            )

    @property
    def reserved(self) -> bool:
        """Return whether this record belongs to the frozen runtime family."""
        return is_reserved_namespace(
            self.namespace
        )

    @property
    def fingerprint(self) -> str:
        """Return deterministic record fingerprint."""
        return structure_fingerprint(
            self.to_canonical_dict()
        )

    def to_canonical_dict(
        self,
    ) -> dict[str, Any]:
        """Return the complete JSON-native registration record."""
        return {
            "namespace": self.namespace,
            "owner_id": self.owner_id,
            "default_compatibility_mode": (
                self.default_compatibility_mode.value
            ),
            "description": self.description,
            "registered_at": self.registered_at,
            "reserved": self.reserved,
        }


@dataclass(
    frozen=True,
    slots=True,
)
class NamespaceRegistrySnapshot:
    """Immutable deterministic namespace-registry snapshot."""

    generation: int
    records: tuple[NamespaceRecord, ...]
    fingerprint: str

    def __post_init__(self) -> None:
        if (
            not isinstance(
                self.generation,
                int,
            )
            or isinstance(
                self.generation,
                bool,
            )
            or self.generation < 0
        ):
            raise SchemaRegistryError(
                "generation must be a non-negative integer"
            )

        object.__setattr__(
            self,
            "records",
            tuple(self.records),
        )


class NamespaceManager:
    """Thread-safe registry of schema namespaces."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._namespaces: dict[
            str,
            NamespaceRecord,
        ] = {}
        self._generation = 0

    @property
    def generation(self) -> int:
        """Return the current registry generation."""
        with self._lock:
            return self._generation

    def register_namespace(
        self,
        namespace: str,
        owner_id: str,
        *,
        runtime_actor: bool = False,
        default_compatibility_mode: CompatibilityMode = (
            CompatibilityMode.BACKWARD
        ),
        description: str = "",
        replace: bool = False,
    ) -> NamespaceRecord:
        """Register or explicitly replace one namespace.

        Reserved namespaces require ``runtime_actor=True``.

        Replacement is only allowed for the same owner unless the runtime is
        replacing a reserved runtime namespace.
        """
        if not is_valid_namespace(
            namespace
        ):
            raise SchemaRegistryError(
                f"invalid namespace: {namespace!r}"
            )

        if not is_valid_identifier(
            owner_id
        ):
            raise SchemaRegistryError(
                f"invalid owner_id: {owner_id!r}"
            )

        reserved = is_reserved_namespace(
            namespace
        )

        if reserved and not runtime_actor:
            raise SchemaRegistryError(
                f"namespace {namespace!r} is under "
                f"the frozen '{RESERVED_RUNTIME_PREFIX}*' "
                "runtime namespace"
            )

        record = NamespaceRecord(
            namespace=namespace,
            owner_id=owner_id,
            default_compatibility_mode=(
                default_compatibility_mode
            ),
            description=description,
        )

        with self._lock:
            existing = self._namespaces.get(
                namespace
            )

            if (
                existing is not None
                and not replace
            ):
                raise SchemaRegistryError(
                    "namespace already registered: "
                    f"{namespace!r}"
                )

            if (
                existing is not None
                and existing.owner_id != owner_id
                and not (
                    reserved
                    and runtime_actor
                )
            ):
                raise SchemaRegistryError(
                    "namespace replacement cannot "
                    "change ownership"
                )

            self._namespaces[
                namespace
            ] = record

            self._generation += 1

            return record

    def get(
        self,
        namespace: str,
    ) -> NamespaceRecord | None:
        """Return one namespace record or ``None``."""
        if not is_valid_namespace(
            namespace
        ):
            raise SchemaRegistryError(
                f"invalid namespace: {namespace!r}"
            )

        with self._lock:
            return self._namespaces.get(
                namespace
            )

    def require(
        self,
        namespace: str,
    ) -> NamespaceRecord:
        """Return one namespace record or raise."""
        record = self.get(
            namespace
        )

        if record is None:
            raise SchemaRegistryError(
                f"namespace not registered: {namespace!r}"
            )

        return record

    def list_namespaces(
        self,
    ) -> tuple[NamespaceRecord, ...]:
        """Return all records in deterministic namespace order."""
        with self._lock:
            return tuple(
                self._namespaces[name]
                for name in sorted(
                    self._namespaces
                )
            )

    def authorize_schema_namespace(
        self,
        namespace: str,
        *,
        actor_id: str,
        runtime_actor: bool = False,
    ) -> NamespaceRecord:
        """Authorize an actor to register schemas under a namespace."""
        if not is_valid_identifier(
            actor_id
        ):
            raise SchemaRegistryError(
                f"invalid actor_id: {actor_id!r}"
            )

        record = self.require(
            namespace
        )

        if (
            record.reserved
            and not runtime_actor
        ):
            raise SchemaRegistryError(
                f"schemas under '{RESERVED_RUNTIME_PREFIX}*' "
                "may only be registered by the runtime"
            )

        if (
            not record.reserved
            and record.owner_id != actor_id
        ):
            raise SchemaRegistryError(
                f"actor {actor_id!r} does not own "
                f"namespace {namespace!r}"
            )

        return record

    def remove_namespace(
        self,
        namespace: str,
        *,
        actor_id: str,
        runtime_actor: bool = False,
    ) -> NamespaceRecord:
        """Remove a namespace under strict ownership control."""
        if not is_valid_identifier(
            actor_id
        ):
            raise SchemaRegistryError(
                f"invalid actor_id: {actor_id!r}"
            )

        with self._lock:
            record = self._namespaces.get(
                namespace
            )

            if record is None:
                raise SchemaRegistryError(
                    f"namespace not registered: {namespace!r}"
                )

            if record.reserved:
                if not runtime_actor:
                    raise SchemaRegistryError(
                        "reserved runtime namespace "
                        "cannot be removed by a non-runtime actor"
                    )
            elif record.owner_id != actor_id:
                raise SchemaRegistryError(
                    "namespace can only be removed "
                    "by its owner"
                )

            removed = self._namespaces.pop(
                namespace
            )

            self._generation += 1

            return removed

    def snapshot(
        self,
    ) -> NamespaceRegistrySnapshot:
        """Return an immutable deterministic registry snapshot."""
        with self._lock:
            records = tuple(
                self._namespaces[name]
                for name in sorted(
                    self._namespaces
                )
            )

            payload = {
                "generation": self._generation,
                "records": [
                    record.to_canonical_dict()
                    for record in records
                ],
            }

            return NamespaceRegistrySnapshot(
                generation=self._generation,
                records=records,
                fingerprint=structure_fingerprint(
                    payload
                ),
            )

    def owner_index(
        self,
    ) -> Mapping[str, tuple[str, ...]]:
        """Return immutable owner-to-namespace index."""
        with self._lock:
            index: dict[
                str,
                list[str],
            ] = {}

            for record in self._namespaces.values():
                index.setdefault(
                    record.owner_id,
                    [],
                ).append(
                    record.namespace
                )

            frozen = {
                owner_id: tuple(
                    sorted(namespaces)
                )
                for owner_id, namespaces
                in sorted(index.items())
            }

            return MappingProxyType(
                frozen
            )


__all__ = [
    "NamespaceManager",
    "NamespaceRecord",
    "NamespaceRegistrySnapshot",
    "RESERVED_RUNTIME_PREFIX",
    "RESERVED_RUNTIME_ROOT",
    "is_reserved_namespace",
]
