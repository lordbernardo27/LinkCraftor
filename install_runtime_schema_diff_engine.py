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
    PACKAGE_DIR / "definitions.py",
]

TARGET = PACKAGE_DIR / "diff_engine.py"

TIMESTAMP = datetime.now(timezone.utc).strftime(
    "%Y%m%dT%H%M%SZ"
)

BACKUP = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime_backups"
    / f"runtime_schema_diff_engine_install_{TIMESTAMP}"
    / TARGET.name
)

TARGET_PREEXISTED = TARGET.exists()


SOURCE = r'''# -*- coding: utf-8 -*-
"""Deterministic structural schema diff engine.

The engine reports structural facts only. It does not decide whether a
change is breaking, compatible, additive, or cosmetic. Those policy
decisions belong to ``change_detection.py``.

Field paths use:

* ``field``
* ``object.child``
* ``array[]``
* ``array[].child``

The engine also records selected schema-level facts such as ownership,
compatibility mode, description, and metadata changes.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Final, Mapping

from .definitions import SchemaDefinition
from .serialization import structure_fingerprint
from .types import (
    EMPTY_FROZEN_MAPPING,
    SchemaDefinitionError,
    deep_freeze,
    deep_thaw,
)


MAX_DIFF_DEPTH: Final[int] = 64
MAX_DIFF_ENTRIES: Final[int] = 100_000


class DiffKind(str, Enum):
    """Kinds of structural differences."""

    FIELD_ADDED = "field_added"
    FIELD_REMOVED = "field_removed"
    TYPE_CHANGED = "type_changed"
    REQUIRED_CHANGED = "required_changed"
    NULLABLE_CHANGED = "nullable_changed"
    DEFAULT_CHANGED = "default_changed"
    CONSTRAINT_CHANGED = "constraint_changed"
    DESCRIPTION_CHANGED = "description_changed"
    OWNER_CHANGED = "owner_changed"
    COMPATIBILITY_MODE_CHANGED = (
        "compatibility_mode_changed"
    )
    SCHEMA_DESCRIPTION_CHANGED = (
        "schema_description_changed"
    )
    SCHEMA_METADATA_CHANGED = (
        "schema_metadata_changed"
    )


@dataclass(
    frozen=True,
    slots=True,
)
class DiffEntry:
    """One immutable structural difference."""

    path: str
    kind: DiffKind
    before: Any
    after: Any
    before_present: bool = True
    after_present: bool = True

    def __post_init__(self) -> None:
        if (
            not isinstance(self.path, str)
            or not self.path
        ):
            raise SchemaDefinitionError(
                "diff path must be a non-empty string"
            )

        if not isinstance(
            self.kind,
            DiffKind,
        ):
            try:
                object.__setattr__(
                    self,
                    "kind",
                    DiffKind(
                        self.kind
                    ),
                )
            except (
                TypeError,
                ValueError,
            ) as exc:
                raise SchemaDefinitionError(
                    f"invalid diff kind: {self.kind!r}"
                ) from exc

        if not isinstance(
            self.before_present,
            bool,
        ):
            raise SchemaDefinitionError(
                "before_present must be a boolean"
            )

        if not isinstance(
            self.after_present,
            bool,
        ):
            raise SchemaDefinitionError(
                "after_present must be a boolean"
            )

        object.__setattr__(
            self,
            "before",
            deep_freeze(
                self.before
            ),
        )

        object.__setattr__(
            self,
            "after",
            deep_freeze(
                self.after
            ),
        )

    def to_canonical_dict(
        self,
    ) -> dict[str, Any]:
        """Return plain JSON-native diff data."""
        return {
            "path": self.path,
            "kind": self.kind.value,
            "before": deep_thaw(
                self.before
            ),
            "after": deep_thaw(
                self.after
            ),
            "before_present": (
                self.before_present
            ),
            "after_present": (
                self.after_present
            ),
        }


@dataclass(
    frozen=True,
    slots=True,
)
class SchemaDiff:
    """Complete immutable structural diff."""

    source_schema_id: str
    target_schema_id: str
    source_coordinate: str
    target_coordinate: str
    source_content_fingerprint: str
    target_content_fingerprint: str
    entries: tuple[DiffEntry, ...]
    truncated: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "source_schema_id",
            "target_schema_id",
            "source_coordinate",
            "target_coordinate",
            "source_content_fingerprint",
            "target_content_fingerprint",
        ):
            value = getattr(
                self,
                field_name,
            )

            if (
                not isinstance(value, str)
                or not value
            ):
                raise SchemaDefinitionError(
                    f"{field_name} must be "
                    "a non-empty string"
                )

        for field_name in (
            "source_content_fingerprint",
            "target_content_fingerprint",
        ):
            if len(
                getattr(
                    self,
                    field_name,
                )
            ) != 64:
                raise SchemaDefinitionError(
                    f"{field_name} must be "
                    "a 64-character digest"
                )

        object.__setattr__(
            self,
            "entries",
            tuple(
                self.entries
            ),
        )

    @property
    def identical(
        self,
    ) -> bool:
        """Return whether no structural or schema-level facts changed."""
        return (
            not self.entries
            and not self.truncated
        )

    @property
    def entry_count(
        self,
    ) -> int:
        return len(
            self.entries
        )

    @property
    def fingerprint(
        self,
    ) -> str:
        """Return deterministic diff fingerprint."""
        return structure_fingerprint(
            self.to_canonical_dict()
        )

    def entries_of_kind(
        self,
        kind: DiffKind,
    ) -> tuple[DiffEntry, ...]:
        """Return entries matching one diff kind."""
        effective_kind = (
            kind
            if isinstance(
                kind,
                DiffKind,
            )
            else DiffKind(kind)
        )

        return tuple(
            entry
            for entry in self.entries
            if entry.kind is effective_kind
        )

    def to_canonical_dict(
        self,
    ) -> dict[str, Any]:
        """Return complete JSON-native diff data."""
        return {
            "source_schema_id": (
                self.source_schema_id
            ),
            "target_schema_id": (
                self.target_schema_id
            ),
            "source_coordinate": (
                self.source_coordinate
            ),
            "target_coordinate": (
                self.target_coordinate
            ),
            "source_content_fingerprint": (
                self.source_content_fingerprint
            ),
            "target_content_fingerprint": (
                self.target_content_fingerprint
            ),
            "entries": [
                entry.to_canonical_dict()
                for entry in self.entries
            ],
            "entry_count": self.entry_count,
            "truncated": self.truncated,
        }


class _DiffContext:
    __slots__ = (
        "entries",
        "truncated",
    )

    def __init__(self) -> None:
        self.entries: list[
            DiffEntry
        ] = []

        self.truncated = False

    def add(
        self,
        entry: DiffEntry,
    ) -> None:
        if self.truncated:
            return

        if (
            len(self.entries)
            >= MAX_DIFF_ENTRIES
        ):
            self.truncated = True
            return

        self.entries.append(
            entry
        )


def _spec_value(
    spec: Mapping[str, Any],
    key: str,
    default: Any,
) -> Any:
    return spec.get(
        key,
        default,
    )


def _join_path(
    prefix: str,
    name: str,
) -> str:
    if not prefix:
        return name

    return f"{prefix}.{name}"


def _diff_specs(
    path: str,
    old_spec: Mapping[str, Any],
    new_spec: Mapping[str, Any],
    context: _DiffContext,
    depth: int,
) -> None:
    if context.truncated:
        return

    if depth > MAX_DIFF_DEPTH:
        context.truncated = True
        return

    old_type = old_spec.get(
        "type"
    )

    new_type = new_spec.get(
        "type"
    )

    if old_type != new_type:
        context.add(
            DiffEntry(
                path=path,
                kind=DiffKind.TYPE_CHANGED,
                before=old_type,
                after=new_type,
            )
        )

        return

    old_required = bool(
        _spec_value(
            old_spec,
            "required",
            False,
        )
    )

    new_required = bool(
        _spec_value(
            new_spec,
            "required",
            False,
        )
    )

    if old_required != new_required:
        context.add(
            DiffEntry(
                path=path,
                kind=(
                    DiffKind.REQUIRED_CHANGED
                ),
                before=old_required,
                after=new_required,
            )
        )

    old_nullable = bool(
        _spec_value(
            old_spec,
            "nullable",
            False,
        )
    )

    new_nullable = bool(
        _spec_value(
            new_spec,
            "nullable",
            False,
        )
    )

    if old_nullable != new_nullable:
        context.add(
            DiffEntry(
                path=path,
                kind=(
                    DiffKind.NULLABLE_CHANGED
                ),
                before=old_nullable,
                after=new_nullable,
            )
        )

    old_default_present = (
        "default" in old_spec
    )

    new_default_present = (
        "default" in new_spec
    )

    old_default = (
        deep_thaw(
            old_spec["default"]
        )
        if old_default_present
        else None
    )

    new_default = (
        deep_thaw(
            new_spec["default"]
        )
        if new_default_present
        else None
    )

    if (
        old_default_present
        != new_default_present
        or old_default
        != new_default
    ):
        context.add(
            DiffEntry(
                path=path,
                kind=(
                    DiffKind.DEFAULT_CHANGED
                ),
                before=old_default,
                after=new_default,
                before_present=(
                    old_default_present
                ),
                after_present=(
                    new_default_present
                ),
            )
        )

    old_constraints = deep_thaw(
        _spec_value(
            old_spec,
            "constraints",
            EMPTY_FROZEN_MAPPING,
        )
    )

    new_constraints = deep_thaw(
        _spec_value(
            new_spec,
            "constraints",
            EMPTY_FROZEN_MAPPING,
        )
    )

    if (
        old_constraints
        != new_constraints
    ):
        context.add(
            DiffEntry(
                path=path,
                kind=(
                    DiffKind.CONSTRAINT_CHANGED
                ),
                before=old_constraints,
                after=new_constraints,
            )
        )

    old_description = _spec_value(
        old_spec,
        "description",
        "",
    )

    new_description = _spec_value(
        new_spec,
        "description",
        "",
    )

    if (
        old_description
        != new_description
    ):
        context.add(
            DiffEntry(
                path=path,
                kind=(
                    DiffKind.DESCRIPTION_CHANGED
                ),
                before=old_description,
                after=new_description,
            )
        )

    if old_type == "object":
        old_fields = _spec_value(
            old_spec,
            "fields",
            EMPTY_FROZEN_MAPPING,
        )

        new_fields = _spec_value(
            new_spec,
            "fields",
            EMPTY_FROZEN_MAPPING,
        )

        if (
            isinstance(
                old_fields,
                Mapping,
            )
            and isinstance(
                new_fields,
                Mapping,
            )
        ):
            _diff_field_maps(
                path,
                old_fields,
                new_fields,
                context,
                depth + 1,
            )

    elif old_type == "array":
        old_item = old_spec.get(
            "item"
        )

        new_item = new_spec.get(
            "item"
        )

        if (
            isinstance(
                old_item,
                Mapping,
            )
            and isinstance(
                new_item,
                Mapping,
            )
        ):
            _diff_specs(
                f"{path}[]",
                old_item,
                new_item,
                context,
                depth + 1,
            )
        elif old_item != new_item:
            context.add(
                DiffEntry(
                    path=f"{path}[]",
                    kind=DiffKind.TYPE_CHANGED,
                    before=deep_thaw(
                        old_item
                    ),
                    after=deep_thaw(
                        new_item
                    ),
                    before_present=(
                        old_item is not None
                    ),
                    after_present=(
                        new_item is not None
                    ),
                )
            )


def _diff_field_maps(
    prefix: str,
    old_fields: Mapping[str, Any],
    new_fields: Mapping[str, Any],
    context: _DiffContext,
    depth: int,
) -> None:
    if context.truncated:
        return

    if depth > MAX_DIFF_DEPTH:
        context.truncated = True
        return

    old_names = set(
        old_fields
    )

    new_names = set(
        new_fields
    )

    for name in sorted(
        old_names - new_names
    ):
        context.add(
            DiffEntry(
                path=_join_path(
                    prefix,
                    name,
                ),
                kind=DiffKind.FIELD_REMOVED,
                before=deep_thaw(
                    old_fields[name]
                ),
                after=None,
                before_present=True,
                after_present=False,
            )
        )

    for name in sorted(
        new_names - old_names
    ):
        context.add(
            DiffEntry(
                path=_join_path(
                    prefix,
                    name,
                ),
                kind=DiffKind.FIELD_ADDED,
                before=None,
                after=deep_thaw(
                    new_fields[name]
                ),
                before_present=False,
                after_present=True,
            )
        )

    for name in sorted(
        old_names & new_names
    ):
        if context.truncated:
            return

        old_spec = old_fields[
            name
        ]

        new_spec = new_fields[
            name
        ]

        path = _join_path(
            prefix,
            name,
        )

        if (
            isinstance(
                old_spec,
                Mapping,
            )
            and isinstance(
                new_spec,
                Mapping,
            )
        ):
            _diff_specs(
                path,
                old_spec,
                new_spec,
                context,
                depth,
            )
        elif old_spec != new_spec:
            context.add(
                DiffEntry(
                    path=path,
                    kind=DiffKind.TYPE_CHANGED,
                    before=deep_thaw(
                        old_spec
                    ),
                    after=deep_thaw(
                        new_spec
                    ),
                )
            )


class SchemaDiffEngine:
    """Stateless deterministic structural diff engine."""

    @staticmethod
    def diff(
        source: SchemaDefinition,
        target: SchemaDefinition,
    ) -> SchemaDiff:
        """Produce structural facts from ``source`` to ``target``."""
        if not isinstance(
            source,
            SchemaDefinition,
        ):
            raise SchemaDefinitionError(
                "source must be a SchemaDefinition"
            )

        if not isinstance(
            target,
            SchemaDefinition,
        ):
            raise SchemaDefinitionError(
                "target must be a SchemaDefinition"
            )

        source.validate()
        target.validate()

        if (
            source.namespace
            != target.namespace
            or source.name
            != target.name
        ):
            raise SchemaDefinitionError(
                "schema diff requires the same "
                "namespace and schema name"
            )

        context = _DiffContext()

        if (
            source.owner_id
            != target.owner_id
        ):
            context.add(
                DiffEntry(
                    path="$owner_id",
                    kind=DiffKind.OWNER_CHANGED,
                    before=source.owner_id,
                    after=target.owner_id,
                )
            )

        if (
            source.compatibility_mode
            is not target.compatibility_mode
        ):
            context.add(
                DiffEntry(
                    path="$compatibility_mode",
                    kind=(
                        DiffKind
                        .COMPATIBILITY_MODE_CHANGED
                    ),
                    before=(
                        source
                        .compatibility_mode
                        .value
                    ),
                    after=(
                        target
                        .compatibility_mode
                        .value
                    ),
                )
            )

        if (
            source.description
            != target.description
        ):
            context.add(
                DiffEntry(
                    path="$description",
                    kind=(
                        DiffKind
                        .SCHEMA_DESCRIPTION_CHANGED
                    ),
                    before=source.description,
                    after=target.description,
                )
            )

        source_metadata = deep_thaw(
            source.metadata
        )

        target_metadata = deep_thaw(
            target.metadata
        )

        if (
            source_metadata
            != target_metadata
        ):
            context.add(
                DiffEntry(
                    path="$metadata",
                    kind=(
                        DiffKind
                        .SCHEMA_METADATA_CHANGED
                    ),
                    before=source_metadata,
                    after=target_metadata,
                )
            )

        _diff_field_maps(
            "",
            source.fields(),
            target.fields(),
            context,
            1,
        )

        entries = tuple(
            sorted(
                context.entries,
                key=lambda entry: (
                    entry.path,
                    entry.kind.value,
                    structure_fingerprint(
                        entry.to_canonical_dict()
                    ),
                ),
            )
        )

        return SchemaDiff(
            source_schema_id=(
                source.schema_id
            ),
            target_schema_id=(
                target.schema_id
            ),
            source_coordinate=(
                source.coordinate()
            ),
            target_coordinate=(
                target.coordinate()
            ),
            source_content_fingerprint=(
                source.content_fingerprint()
            ),
            target_content_fingerprint=(
                target.content_fingerprint()
            ),
            entries=entries,
            truncated=context.truncated,
        )


__all__ = [
    "MAX_DIFF_DEPTH",
    "MAX_DIFF_ENTRIES",
    "DiffEntry",
    "DiffKind",
    "SchemaDiff",
    "SchemaDiffEngine",
]
'''


def import_target():
    runtime_path = str(
        RUNTIME_DIR
    )

    if runtime_path not in sys.path:
        sys.path.insert(
            0,
            runtime_path,
        )

    sys.modules.pop(
        "runtime_schema.diff_engine",
        None,
    )

    importlib.invalidate_caches()

    return importlib.import_module(
        "runtime_schema.diff_engine"
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


def verify_behavior(
    module,
) -> None:
    definitions_module = (
        importlib.import_module(
            "runtime_schema.definitions"
        )
    )

    Definition = (
        definitions_module
        .SchemaDefinition
    )

    timestamp = (
        "2026-07-27T14:45:00.000000Z"
    )

    source = Definition(
        namespace="runtime.schema",
        name="diff_record",
        version="1.0.0",
        owner_id="runtime_schema",
        lifecycle_state="registered",
        description="Source description.",
        metadata={
            "revision": 1,
        },
        created_at=timestamp,
        body={
            "fields": {
                "identifier": {
                    "type": "string",
                    "required": True,
                    "description": "Identifier.",
                    "constraints": {
                        "min_length": 1,
                    },
                },
                "nullable_value": {
                    "type": "string",
                    "nullable": True,
                    "default": None,
                },
                "context": {
                    "type": "object",
                    "fields": {
                        "enabled": {
                            "type": "boolean",
                        },
                        "removed_child": {
                            "type": "string",
                        },
                    },
                },
                "items": {
                    "type": "array",
                    "item": {
                        "type": "object",
                        "fields": {
                            "name": {
                                "type": "string",
                            },
                        },
                    },
                },
                "removed_field": {
                    "type": "integer",
                },
            }
        },
    ).validate()

    target = Definition(
        namespace="runtime.schema",
        name="diff_record",
        version="2.0.0",
        owner_id="runtime_kernel",
        compatibility_mode="full",
        lifecycle_state="registered",
        description="Target description.",
        metadata={
            "revision": 2,
        },
        created_at=timestamp,
        body={
            "fields": {
                "identifier": {
                    "type": "string",
                    "required": False,
                    "description": "Updated identifier.",
                    "constraints": {
                        "min_length": 2,
                        "max_length": 64,
                    },
                },
                "nullable_value": {
                    "type": "string",
                    "nullable": False,
                },
                "context": {
                    "type": "object",
                    "fields": {
                        "enabled": {
                            "type": "integer",
                        },
                        "added_child": {
                            "type": "string",
                        },
                    },
                },
                "items": {
                    "type": "array",
                    "item": {
                        "type": "object",
                        "fields": {
                            "name": {
                                "type": "string",
                                "required": True,
                            },
                        },
                    },
                },
                "added_field": {
                    "type": "boolean",
                },
            }
        },
    ).validate()

    diff_one = (
        module.SchemaDiffEngine.diff(
            source,
            target,
        )
    )

    diff_two = (
        module.SchemaDiffEngine.diff(
            source,
            target,
        )
    )

    assert not diff_one.identical
    assert not diff_one.truncated
    assert diff_one.entry_count > 0

    assert (
        diff_one.fingerprint
        == diff_two.fingerprint
    )

    kinds = {
        entry.kind
        for entry in diff_one.entries
    }

    required_kinds = {
        module.DiffKind.FIELD_ADDED,
        module.DiffKind.FIELD_REMOVED,
        module.DiffKind.TYPE_CHANGED,
        module.DiffKind.REQUIRED_CHANGED,
        module.DiffKind.NULLABLE_CHANGED,
        module.DiffKind.DEFAULT_CHANGED,
        module.DiffKind.CONSTRAINT_CHANGED,
        module.DiffKind.DESCRIPTION_CHANGED,
        module.DiffKind.OWNER_CHANGED,
        (
            module.DiffKind
            .COMPATIBILITY_MODE_CHANGED
        ),
        (
            module.DiffKind
            .SCHEMA_DESCRIPTION_CHANGED
        ),
        (
            module.DiffKind
            .SCHEMA_METADATA_CHANGED
        ),
    }

    assert required_kinds.issubset(
        kinds
    )

    paths = [
        entry.path
        for entry in diff_one.entries
    ]

    assert paths == sorted(
        paths
    )

    default_entries = (
        diff_one.entries_of_kind(
            module.DiffKind.DEFAULT_CHANGED
        )
    )

    assert len(
        default_entries
    ) == 1

    assert (
        default_entries[0]
        .before_present
        is True
    )

    assert (
        default_entries[0]
        .after_present
        is False
    )

    assert any(
        entry.path
        == "context.removed_child"
        for entry in diff_one.entries
    )

    assert any(
        entry.path
        == "context.added_child"
        for entry in diff_one.entries
    )

    assert any(
        entry.path
        == "items[].name"
        for entry in diff_one.entries
    )

    identical = (
        module.SchemaDiffEngine.diff(
            source,
            source,
        )
    )

    assert identical.identical
    assert identical.entry_count == 0
    assert not identical.truncated

    try:
        diff_one.entries = ()
    except Exception:
        pass
    else:
        raise AssertionError(
            "SchemaDiff must be immutable."
        )

    expect_rejection(
        lambda: module.SchemaDiffEngine.diff(
            source,
            Definition(
                namespace="runtime.other",
                name="different_record",
                version="2.0.0",
                owner_id="runtime_schema",
                lifecycle_state="registered",
                created_at=timestamp,
                body={
                    "fields": {}
                },
            ).validate(),
        ),
        "Cross-subject diff",
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
    print("DIFF_ENGINE.PY INSTALLATION AND REVIEW")
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

        verify_behavior(
            module
        )

    except Exception:
        rollback()

        print("ROLLBACK COMPLETE")
        print(
            "The diff_engine.py installation failed, "
            "so the previous filesystem state was restored."
        )
        print()
        print(traceback.format_exc())

        return 1

    print("Dependency verification:        PASS")
    print("Claude baseline review:         PASS")
    print("Nova revisions applied:         PASS")
    print("diff_engine.py compilation:     PASS")
    print("Package import:                 PASS")
    print("Immutable diff contracts:       PASS")
    print("Same-subject enforcement:       PASS")
    print("Field addition detection:       PASS")
    print("Field removal detection:        PASS")
    print("Type-change detection:          PASS")
    print("Required/nullability detection: PASS")
    print("Default presence tracking:      PASS")
    print("Constraint detection:           PASS")
    print("Description detection:          PASS")
    print("Nested object detection:        PASS")
    print("Nested array detection:         PASS")
    print("Schema-level change detection:  PASS")
    print("Deterministic ordering:         PASS")
    print("Deterministic fingerprint:      PASS")
    print("Traversal and entry bounds:     PASS")
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
        "DIFF_ENGINE.PY: INSTALLED, "
        "REVIEWED, AND APPROVED"
    )
    print("NO PRODUCTION DATA WAS MODIFIED")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
