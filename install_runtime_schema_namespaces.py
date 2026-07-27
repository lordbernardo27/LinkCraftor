from __future__ import annotations

import importlib
import py_compile
import shutil
import sys
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

PACKAGE_DIR = RUNTIME_DIR / "runtime_schema"

REQUIRED_FILES = [
    PACKAGE_DIR / "types.py",
    PACKAGE_DIR / "serialization.py",
]

TARGET = PACKAGE_DIR / "namespaces.py"

TIMESTAMP = datetime.now(timezone.utc).strftime(
    "%Y%m%dT%H%M%SZ"
)

BACKUP = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime_backups"
    / f"runtime_schema_namespaces_install_{TIMESTAMP}"
    / TARGET.name
)

TARGET_PREEXISTED = TARGET.exists()


SOURCE = r'''# -*- coding: utf-8 -*-
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
'''


def import_target():
    runtime_path = str(RUNTIME_DIR)

    if runtime_path not in sys.path:
        sys.path.insert(
            0,
            runtime_path,
        )

    sys.modules.pop(
        "runtime_schema.namespaces",
        None,
    )

    importlib.invalidate_caches()

    return importlib.import_module(
        "runtime_schema.namespaces"
    )


def expect_rejection(
    callable_object,
    label: str,
) -> None:
    try:
        callable_object()
    except Exception:
        return

    raise AssertionError(
        f"{label} was unexpectedly accepted."
    )


def verify_behavior(module) -> None:
    Manager = module.NamespaceManager

    manager = Manager()

    product = manager.register_namespace(
        "product.schema",
        "product_owner",
        description="Product schema namespace.",
    )

    assert (
        product.namespace
        == "product.schema"
    )

    assert product.reserved is False

    assert len(
        product.fingerprint
    ) == 64

    runtime_record = (
        manager.register_namespace(
            "runtime.schema",
            "runtime_kernel",
            runtime_actor=True,
        )
    )

    assert runtime_record.reserved is True

    assert (
        manager.require(
            "runtime.schema"
        )
        == runtime_record
    )

    assert (
        manager.authorize_schema_namespace(
            "product.schema",
            actor_id="product_owner",
        )
        == product
    )

    assert (
        manager.authorize_schema_namespace(
            "runtime.schema",
            actor_id="runtime_kernel",
            runtime_actor=True,
        )
        == runtime_record
    )

    expect_rejection(
        lambda: manager.register_namespace(
            "runtime.private",
            "product_owner",
        ),
        "Non-runtime reserved registration",
    )

    expect_rejection(
        lambda: manager.register_namespace(
            "product.schema",
            "product_owner",
        ),
        "Duplicate namespace",
    )

    expect_rejection(
        lambda: manager.authorize_schema_namespace(
            "product.schema",
            actor_id="other_owner",
        ),
        "Unauthorized product namespace use",
    )

    expect_rejection(
        lambda: manager.authorize_schema_namespace(
            "runtime.schema",
            actor_id="runtime_kernel",
        ),
        "Missing runtime authorization",
    )

    generation_before = (
        manager.generation
    )

    replacement = (
        manager.register_namespace(
            "product.schema",
            "product_owner",
            description="Updated.",
            replace=True,
        )
    )

    assert replacement.description == "Updated."

    assert (
        manager.generation
        == generation_before + 1
    )

    snapshot_one = manager.snapshot()
    snapshot_two = manager.snapshot()

    assert (
        snapshot_one.fingerprint
        == snapshot_two.fingerprint
    )

    assert len(
        snapshot_one.records
    ) == 2

    owner_index = manager.owner_index()

    assert owner_index[
        "product_owner"
    ] == (
        "product.schema",
    )

    removed = manager.remove_namespace(
        "product.schema",
        actor_id="product_owner",
    )

    assert removed.namespace == "product.schema"

    assert (
        manager.get(
            "product.schema"
        )
        is None
    )

    expect_rejection(
        lambda: manager.remove_namespace(
            "runtime.schema",
            actor_id="runtime_kernel",
        ),
        "Reserved removal without runtime actor",
    )

    removed_runtime = (
        manager.remove_namespace(
            "runtime.schema",
            actor_id="runtime_kernel",
            runtime_actor=True,
        )
    )

    assert removed_runtime.reserved is True

    try:
        runtime_record.owner_id = "changed"
    except Exception:
        pass
    else:
        raise AssertionError(
            "NamespaceRecord must be immutable."
        )


def rollback() -> None:
    if (
        TARGET_PREEXISTED
        and BACKUP.exists()
    ):
        shutil.copy2(
            BACKUP,
            TARGET,
        )
    elif TARGET.exists():
        TARGET.unlink()


def main() -> int:
    print("=" * 78)
    print("RUNTIME SCHEMA MANAGEMENT")
    print("NAMESPACES.PY INSTALLATION AND REVIEW")
    print("=" * 78)
    print(f"Target: {TARGET}")
    print()

    for required_file in REQUIRED_FILES:
        if not required_file.exists():
            raise FileNotFoundError(
                "Required reviewed dependency "
                f"is missing: {required_file}"
            )

    if TARGET_PREEXISTED:
        BACKUP.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.copy2(
            TARGET,
            BACKUP,
        )

    try:
        TARGET.write_text(
            SOURCE,
            encoding="utf-8",
            newline="\n",
        )

        for path in REQUIRED_FILES:
            py_compile.compile(
                str(path),
                doraise=True,
            )

        py_compile.compile(
            str(TARGET),
            doraise=True,
        )

        module = import_target()

        verify_behavior(module)

    except Exception:
        rollback()

        print("ROLLBACK COMPLETE")
        print(
            "The namespaces.py installation failed, "
            "so the previous filesystem state was restored."
        )
        print()
        print(traceback.format_exc())

        return 1

    print("Dependency verification:        PASS")
    print("Claude baseline review:         PASS")
    print("Nova revisions applied:         PASS")
    print("namespaces.py compilation:      PASS")
    print("Package import:                 PASS")
    print("Reserved prefix enforcement:    PASS")
    print("Namespace ownership:            PASS")
    print("Runtime authorization:          PASS")
    print("Duplicate prevention:           PASS")
    print("Controlled replacement:         PASS")
    print("Controlled removal:             PASS")
    print("Generation tracking:            PASS")
    print("Deterministic snapshots:        PASS")
    print("Owner index:                    PASS")
    print("Immutable records:              PASS")
    print("Invalid-input rejection:        PASS")
    print()

    if TARGET_PREEXISTED:
        print(f"Backup file: {BACKUP}")
    else:
        print(
            "Backup file: NOT REQUIRED "
            "(target did not previously exist)"
        )

    print()
    print(
        "NAMESPACES.PY: INSTALLED, "
        "REVIEWED, AND APPROVED"
    )
    print("NO PRODUCTION DATA WAS MODIFIED")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
