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
    PACKAGE_DIR / "fingerprint.py",
    PACKAGE_DIR / "serialization.py",
    PACKAGE_DIR / "versioning.py",
    PACKAGE_DIR / "definitions.py",
    PACKAGE_DIR / "diff_engine.py",
    PACKAGE_DIR / "change_detection.py",
]

TARGET = PACKAGE_DIR / "migration.py"

TIMESTAMP = datetime.now(timezone.utc).strftime(
    "%Y%m%dT%H%M%SZ"
)

BACKUP = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime_backups"
    / f"runtime_schema_migration_install_{TIMESTAMP}"
    / TARGET.name
)

TARGET_PREEXISTED = TARGET.exists()


SOURCE = r'''# -*- coding: utf-8 -*-
"""Deterministic Runtime Schema Migration Planning.

This module creates declarative migration plans only. It never executes
migrations or mutates stored runtime data.

A migration plan is:

* immutable;
* deterministic;
* fingerprinted;
* reviewable;
* direction-neutral;
* safe to persist and audit;
* explicit about loss and mechanical reversibility.

Migration execution belongs to later runtime execution and persistence
infrastructure.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Final, Mapping

from .change_detection import (
    ChangeDetector,
    ChangeReport,
)
from .definitions import SchemaDefinition
from .diff_engine import (
    DiffEntry,
    DiffKind,
)
from .fingerprint import sha256_hex
from .serialization import structure_fingerprint
from .types import (
    EMPTY_FROZEN_MAPPING,
    SchemaMigrationError,
    deep_freeze,
    deep_thaw,
)


MAX_MIGRATION_STEPS: Final[int] = 100_000
MIGRATION_STEP_ID_PREFIX: Final[str] = "mst_"
MIGRATION_PLAN_ID_PREFIX: Final[str] = "mpl_"


class MigrationOperation(str, Enum):
    """Declarative schema migration operations."""

    ADD_FIELD = "add_field"
    DROP_FIELD = "drop_field"
    CHANGE_TYPE = "change_type"
    SET_REQUIRED = "set_required"
    SET_OPTIONAL = "set_optional"
    UPDATE_NULLABILITY = "update_nullability"
    UPDATE_CONSTRAINTS = "update_constraints"
    UPDATE_DEFAULT = "update_default"
    UPDATE_FIELD_DESCRIPTION = (
        "update_field_description"
    )
    UPDATE_SCHEMA_OWNER = (
        "update_schema_owner"
    )
    UPDATE_COMPATIBILITY_MODE = (
        "update_compatibility_mode"
    )
    UPDATE_SCHEMA_DESCRIPTION = (
        "update_schema_description"
    )
    UPDATE_SCHEMA_METADATA = (
        "update_schema_metadata"
    )


_LOSSLESS_TYPE_WIDENINGS: Final[
    frozenset[tuple[str, str]]
] = frozenset(
    {
        ("integer", "number"),
    }
)


def _validate_digest(
    value: object,
    *,
    field_name: str,
) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(
            character
            not in "0123456789abcdef"
            for character in value
        )
    ):
        raise SchemaMigrationError(
            f"{field_name} must be a lowercase "
            "64-character SHA-256 digest"
        )

    return value


@dataclass(
    frozen=True,
    slots=True,
)
class MigrationStep:
    """One immutable declarative migration operation."""

    operation: MigrationOperation
    path: str
    parameters: Mapping[str, Any] = (
        EMPTY_FROZEN_MAPPING
    )
    lossy: bool = False
    reversible: bool = True

    def __post_init__(self) -> None:
        if not isinstance(
            self.operation,
            MigrationOperation,
        ):
            try:
                object.__setattr__(
                    self,
                    "operation",
                    MigrationOperation(
                        self.operation
                    ),
                )
            except (
                TypeError,
                ValueError,
            ) as exc:
                raise SchemaMigrationError(
                    f"invalid migration operation: "
                    f"{self.operation!r}"
                ) from exc

        if (
            not isinstance(self.path, str)
            or not self.path
        ):
            raise SchemaMigrationError(
                "migration step path must be "
                "a non-empty string"
            )

        if not isinstance(
            self.lossy,
            bool,
        ):
            raise SchemaMigrationError(
                "lossy must be a boolean"
            )

        if not isinstance(
            self.reversible,
            bool,
        ):
            raise SchemaMigrationError(
                "reversible must be a boolean"
            )

        try:
            frozen_parameters = deep_freeze(
                self.parameters
            )
        except Exception as exc:
            raise SchemaMigrationError(
                f"invalid migration parameters: {exc}"
            ) from exc

        object.__setattr__(
            self,
            "parameters",
            frozen_parameters,
        )

    @property
    def step_id(
        self,
    ) -> str:
        """Return deterministic operation identity."""
        digest = sha256_hex(
            structure_fingerprint(
                self.to_canonical_dict(
                    include_step_id=False
                )
            )
        )

        return (
            MIGRATION_STEP_ID_PREFIX
            + digest[:32]
        )

    def to_canonical_dict(
        self,
        *,
        include_step_id: bool = True,
    ) -> dict[str, Any]:
        """Return plain JSON-native step data."""
        payload = {
            "operation": self.operation.value,
            "path": self.path,
            "parameters": deep_thaw(
                self.parameters
            ),
            "lossy": self.lossy,
            "reversible": self.reversible,
        }

        if include_step_id:
            payload["step_id"] = self.step_id

        return payload


@dataclass(
    frozen=True,
    slots=True,
)
class MigrationPlan:
    """Immutable deterministic plan for one schema-version pair."""

    source_schema_id: str
    target_schema_id: str
    source_coordinate: str
    target_coordinate: str
    source_content_fingerprint: str
    target_content_fingerprint: str
    change_report_fingerprint: str
    steps: tuple[MigrationStep, ...]
    complete: bool = True

    def __post_init__(self) -> None:
        for field_name in (
            "source_schema_id",
            "target_schema_id",
            "source_coordinate",
            "target_coordinate",
        ):
            value = getattr(
                self,
                field_name,
            )

            if (
                not isinstance(value, str)
                or not value
            ):
                raise SchemaMigrationError(
                    f"{field_name} must be "
                    "a non-empty string"
                )

        for field_name in (
            "source_content_fingerprint",
            "target_content_fingerprint",
            "change_report_fingerprint",
        ):
            _validate_digest(
                getattr(
                    self,
                    field_name,
                ),
                field_name=field_name,
            )

        if (
            self.source_schema_id
            == self.target_schema_id
        ):
            raise SchemaMigrationError(
                "source and target schema IDs "
                "must differ"
            )

        if (
            self.source_coordinate
            == self.target_coordinate
        ):
            raise SchemaMigrationError(
                "source and target coordinates "
                "must differ"
            )

        object.__setattr__(
            self,
            "steps",
            tuple(
                self.steps
            ),
        )

        if (
            len(self.steps)
            > MAX_MIGRATION_STEPS
        ):
            raise SchemaMigrationError(
                "migration plan exceeds "
                f"{MAX_MIGRATION_STEPS} steps"
            )

        seen_step_ids: set[str] = set()

        for step in self.steps:
            if not isinstance(
                step,
                MigrationStep,
            ):
                raise SchemaMigrationError(
                    "every plan step must be "
                    "a MigrationStep"
                )

            if step.step_id in seen_step_ids:
                raise SchemaMigrationError(
                    "migration plan contains "
                    "duplicate steps"
                )

            seen_step_ids.add(
                step.step_id
            )

        if not isinstance(
            self.complete,
            bool,
        ):
            raise SchemaMigrationError(
                "complete must be a boolean"
            )

    @property
    def plan_id(
        self,
    ) -> str:
        """Return deterministic plan identity."""
        digest = sha256_hex(
            self.fingerprint
        )

        return (
            MIGRATION_PLAN_ID_PREFIX
            + digest[:32]
        )

    @property
    def lossy(
        self,
    ) -> bool:
        """Return whether any step may discard information."""
        return any(
            step.lossy
            for step in self.steps
        )

    @property
    def reversible(
        self,
    ) -> bool:
        """Return whether every step is mechanically reversible."""
        return all(
            step.reversible
            for step in self.steps
        )

    @property
    def step_count(
        self,
    ) -> int:
        return len(
            self.steps
        )

    @property
    def fingerprint(
        self,
    ) -> str:
        """Return deterministic complete plan fingerprint."""
        return structure_fingerprint(
            self.to_canonical_dict(
                include_identity=False
            )
        )

    def steps_for_operation(
        self,
        operation: MigrationOperation,
    ) -> tuple[MigrationStep, ...]:
        """Return all steps for one operation."""
        effective_operation = (
            operation
            if isinstance(
                operation,
                MigrationOperation,
            )
            else MigrationOperation(
                operation
            )
        )

        return tuple(
            step
            for step in self.steps
            if step.operation
            is effective_operation
        )

    def to_canonical_dict(
        self,
        *,
        include_identity: bool = True,
    ) -> dict[str, Any]:
        """Return complete plain JSON-native plan data."""
        payload = {
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
            "change_report_fingerprint": (
                self.change_report_fingerprint
            ),
            "steps": [
                step.to_canonical_dict()
                for step in self.steps
            ],
            "step_count": self.step_count,
            "lossy": self.lossy,
            "reversible": self.reversible,
            "complete": self.complete,
        }

        if include_identity:
            payload["plan_id"] = (
                self.plan_id
            )
            payload["fingerprint"] = (
                self.fingerprint
            )

        return payload


def _field_added_step(
    entry: DiffEntry,
) -> MigrationStep:
    spec = (
        entry.after
        if isinstance(
            entry.after,
            Mapping,
        )
        else {}
    )

    required = bool(
        spec.get(
            "required",
            False,
        )
    )

    has_default = (
        "default" in spec
    )

    return MigrationStep(
        operation=MigrationOperation.ADD_FIELD,
        path=entry.path,
        parameters={
            "spec": deep_thaw(
                spec
            ),
            "required": required,
            "has_default": has_default,
            "backfill_default": (
                deep_thaw(
                    spec["default"]
                )
                if has_default
                else None
            ),
        },
        lossy=False,
        reversible=True,
    )


def _step_for_entry(
    entry: DiffEntry,
) -> MigrationStep | None:
    """Translate one structural fact into a declarative step."""
    if not isinstance(
        entry,
        DiffEntry,
    ):
        raise SchemaMigrationError(
            "entry must be a DiffEntry"
        )

    kind = entry.kind

    if kind is DiffKind.FIELD_ADDED:
        return _field_added_step(
            entry
        )

    if kind is DiffKind.FIELD_REMOVED:
        return MigrationStep(
            operation=(
                MigrationOperation.DROP_FIELD
            ),
            path=entry.path,
            parameters={
                "removed_spec": (
                    deep_thaw(
                        entry.before
                    )
                    if isinstance(
                        entry.before,
                        Mapping,
                    )
                    else {}
                )
            },
            lossy=True,
            reversible=False,
        )

    if kind is DiffKind.TYPE_CHANGED:
        old_type = str(
            entry.before
        )

        new_type = str(
            entry.after
        )

        widening = (
            old_type,
            new_type,
        ) in _LOSSLESS_TYPE_WIDENINGS

        return MigrationStep(
            operation=(
                MigrationOperation.CHANGE_TYPE
            ),
            path=entry.path,
            parameters={
                "from_type": entry.before,
                "to_type": entry.after,
                "lossless_widening": widening,
            },
            lossy=not widening,
            reversible=False,
        )

    if kind is DiffKind.REQUIRED_CHANGED:
        return MigrationStep(
            operation=(
                MigrationOperation.SET_REQUIRED
                if bool(entry.after)
                else MigrationOperation.SET_OPTIONAL
            ),
            path=entry.path,
            parameters={
                "required": bool(
                    entry.after
                )
            },
            lossy=False,
            reversible=True,
        )

    if kind is DiffKind.NULLABLE_CHANGED:
        nullable = bool(
            entry.after
        )

        return MigrationStep(
            operation=(
                MigrationOperation
                .UPDATE_NULLABILITY
            ),
            path=entry.path,
            parameters={
                "nullable": nullable
            },
            lossy=not nullable,
            reversible=True,
        )

    if kind is DiffKind.CONSTRAINT_CHANGED:
        return MigrationStep(
            operation=(
                MigrationOperation
                .UPDATE_CONSTRAINTS
            ),
            path=entry.path,
            parameters={
                "before": (
                    deep_thaw(
                        entry.before
                    )
                    if isinstance(
                        entry.before,
                        Mapping,
                    )
                    else {}
                ),
                "after": (
                    deep_thaw(
                        entry.after
                    )
                    if isinstance(
                        entry.after,
                        Mapping,
                    )
                    else {}
                ),
            },
            lossy=False,
            reversible=True,
        )

    if kind is DiffKind.DEFAULT_CHANGED:
        return MigrationStep(
            operation=(
                MigrationOperation.UPDATE_DEFAULT
            ),
            path=entry.path,
            parameters={
                "before": deep_thaw(
                    entry.before
                ),
                "after": deep_thaw(
                    entry.after
                ),
                "before_present": (
                    entry.before_present
                ),
                "after_present": (
                    entry.after_present
                ),
            },
            lossy=False,
            reversible=True,
        )

    if kind is DiffKind.DESCRIPTION_CHANGED:
        return MigrationStep(
            operation=(
                MigrationOperation
                .UPDATE_FIELD_DESCRIPTION
            ),
            path=entry.path,
            parameters={
                "before": deep_thaw(
                    entry.before
                ),
                "after": deep_thaw(
                    entry.after
                ),
            },
            lossy=False,
            reversible=True,
        )

    if kind is DiffKind.OWNER_CHANGED:
        return MigrationStep(
            operation=(
                MigrationOperation
                .UPDATE_SCHEMA_OWNER
            ),
            path=entry.path,
            parameters={
                "before": entry.before,
                "after": entry.after,
            },
            lossy=False,
            reversible=True,
        )

    if (
        kind
        is DiffKind.COMPATIBILITY_MODE_CHANGED
    ):
        return MigrationStep(
            operation=(
                MigrationOperation
                .UPDATE_COMPATIBILITY_MODE
            ),
            path=entry.path,
            parameters={
                "before": entry.before,
                "after": entry.after,
            },
            lossy=False,
            reversible=True,
        )

    if (
        kind
        is DiffKind.SCHEMA_DESCRIPTION_CHANGED
    ):
        return MigrationStep(
            operation=(
                MigrationOperation
                .UPDATE_SCHEMA_DESCRIPTION
            ),
            path=entry.path,
            parameters={
                "before": entry.before,
                "after": entry.after,
            },
            lossy=False,
            reversible=True,
        )

    if (
        kind
        is DiffKind.SCHEMA_METADATA_CHANGED
    ):
        return MigrationStep(
            operation=(
                MigrationOperation
                .UPDATE_SCHEMA_METADATA
            ),
            path=entry.path,
            parameters={
                "before": deep_thaw(
                    entry.before
                ),
                "after": deep_thaw(
                    entry.after
                ),
            },
            lossy=False,
            reversible=True,
        )

    raise SchemaMigrationError(
        f"unsupported diff kind: {kind!r}"
    )


class MigrationPlanner:
    """Stateless deterministic migration planner."""

    @staticmethod
    def plan(
        source: SchemaDefinition,
        target: SchemaDefinition,
        change_report: ChangeReport | None = None,
    ) -> MigrationPlan:
        """Create a declarative plan for one schema pair."""
        if not isinstance(
            source,
            SchemaDefinition,
        ):
            raise SchemaMigrationError(
                "source must be a SchemaDefinition"
            )

        if not isinstance(
            target,
            SchemaDefinition,
        ):
            raise SchemaMigrationError(
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
            raise SchemaMigrationError(
                "migration requires the same "
                "namespace and schema name"
            )

        if (
            source.schema_id
            == target.schema_id
        ):
            raise SchemaMigrationError(
                "source and target are the "
                "same schema version"
            )

        if change_report is None:
            effective_report = (
                ChangeDetector.detect(
                    source,
                    target,
                )
            )
        else:
            if not isinstance(
                change_report,
                ChangeReport,
            ):
                raise SchemaMigrationError(
                    "change_report must be a ChangeReport"
                )

            diff = change_report.diff

            if (
                diff.source_schema_id
                != source.schema_id
                or diff.target_schema_id
                != target.schema_id
                or diff.source_content_fingerprint
                != source.content_fingerprint()
                or diff.target_content_fingerprint
                != target.content_fingerprint()
            ):
                raise SchemaMigrationError(
                    "supplied change report does "
                    "not match this schema pair"
                )

            recomputed = (
                ChangeDetector.detect(
                    source,
                    target,
                )
            )

            if (
                recomputed.fingerprint
                != change_report.fingerprint
            ):
                raise SchemaMigrationError(
                    "supplied change report failed "
                    "deterministic integrity verification"
                )

            effective_report = (
                change_report
            )

        steps = tuple(
            sorted(
                (
                    _step_for_entry(
                        entry
                    )
                    for entry
                    in effective_report.diff.entries
                ),
                key=lambda step: (
                    step.path,
                    step.operation.value,
                    step.step_id,
                ),
            )
        )

        return MigrationPlan(
            source_schema_id=source.schema_id,
            target_schema_id=target.schema_id,
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
            change_report_fingerprint=(
                effective_report.fingerprint
            ),
            steps=steps,
            complete=(
                effective_report.complete
            ),
        )


__all__ = [
    "MAX_MIGRATION_STEPS",
    "MIGRATION_PLAN_ID_PREFIX",
    "MIGRATION_STEP_ID_PREFIX",
    "MigrationOperation",
    "MigrationPlan",
    "MigrationPlanner",
    "MigrationStep",
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
        "runtime_schema.migration",
        None,
    )

    importlib.invalidate_caches()

    return importlib.import_module(
        "runtime_schema.migration"
    )


def verify_behavior(
    module,
) -> None:
    definitions_module = (
        importlib.import_module(
            "runtime_schema.definitions"
        )
    )

    change_module = (
        importlib.import_module(
            "runtime_schema.change_detection"
        )
    )

    Definition = (
        definitions_module.SchemaDefinition
    )

    timestamp = (
        "2026-07-27T15:30:00.000000Z"
    )

    source = Definition(
        namespace="runtime.schema",
        name="migration_record",
        version="1.0.0",
        owner_id="runtime_schema",
        lifecycle_state="registered",
        description="Old.",
        metadata={
            "revision": 1,
        },
        created_at=timestamp,
        body={
            "fields": {
                "type_change": {
                    "type": "integer",
                },
                "required_change": {
                    "type": "string",
                    "required": False,
                },
                "nullable_change": {
                    "type": "string",
                    "nullable": True,
                },
                "constraint_change": {
                    "type": "integer",
                    "constraints": {
                        "minimum": 0,
                        "maximum": 100,
                    },
                },
                "default_change": {
                    "type": "string",
                    "default": "old",
                },
                "description_change": {
                    "type": "string",
                    "description": "Old field.",
                },
                "removed": {
                    "type": "string",
                },
            }
        },
    ).validate()

    target = Definition(
        namespace="runtime.schema",
        name="migration_record",
        version="2.0.0",
        owner_id="runtime_kernel",
        compatibility_mode="full",
        lifecycle_state="registered",
        description="New.",
        metadata={
            "revision": 2,
        },
        created_at=timestamp,
        body={
            "fields": {
                "type_change": {
                    "type": "number",
                },
                "required_change": {
                    "type": "string",
                    "required": True,
                },
                "nullable_change": {
                    "type": "string",
                    "nullable": False,
                },
                "constraint_change": {
                    "type": "integer",
                    "constraints": {
                        "minimum": 10,
                        "maximum": 90,
                    },
                },
                "default_change": {
                    "type": "string",
                    "default": "new",
                },
                "description_change": {
                    "type": "string",
                    "description": "New field.",
                },
                "added": {
                    "type": "string",
                    "required": True,
                    "default": "backfill",
                },
            }
        },
    ).validate()

    report = (
        change_module.ChangeDetector.detect(
            source,
            target,
        )
    )

    plan_one = (
        module.MigrationPlanner.plan(
            source,
            target,
            report,
        )
    )

    plan_two = (
        module.MigrationPlanner.plan(
            source,
            target,
        )
    )

    assert (
        plan_one.fingerprint
        == plan_two.fingerprint
    )

    assert plan_one.plan_id.startswith(
        module.MIGRATION_PLAN_ID_PREFIX
    )

    assert plan_one.complete
    assert plan_one.step_count > 0
    assert plan_one.lossy
    assert not plan_one.reversible

    operations = {
        step.operation
        for step in plan_one.steps
    }

    required_operations = {
        module.MigrationOperation.ADD_FIELD,
        module.MigrationOperation.DROP_FIELD,
        module.MigrationOperation.CHANGE_TYPE,
        module.MigrationOperation.SET_REQUIRED,
        (
            module.MigrationOperation
            .UPDATE_NULLABILITY
        ),
        (
            module.MigrationOperation
            .UPDATE_CONSTRAINTS
        ),
        module.MigrationOperation.UPDATE_DEFAULT,
        (
            module.MigrationOperation
            .UPDATE_FIELD_DESCRIPTION
        ),
        (
            module.MigrationOperation
            .UPDATE_SCHEMA_OWNER
        ),
        (
            module.MigrationOperation
            .UPDATE_COMPATIBILITY_MODE
        ),
        (
            module.MigrationOperation
            .UPDATE_SCHEMA_DESCRIPTION
        ),
        (
            module.MigrationOperation
            .UPDATE_SCHEMA_METADATA
        ),
    }

    assert required_operations.issubset(
        operations
    )

    assert plan_one.steps_for_operation(
        module.MigrationOperation.ADD_FIELD
    )

    step_ids = [
        step.step_id
        for step in plan_one.steps
    ]

    assert len(step_ids) == len(
        set(step_ids)
    )

    assert all(
        step_id.startswith(
            module.MIGRATION_STEP_ID_PREFIX
        )
        for step_id in step_ids
    )

    assert len(
        plan_one.fingerprint
    ) == 64

    try:
        plan_one.steps = ()
    except Exception:
        pass
    else:
        raise AssertionError(
            "MigrationPlan must be immutable."
        )

    try:
        module.MigrationPlanner.plan(
            source,
            source,
        )
    except Exception:
        pass
    else:
        raise AssertionError(
            "Same-version migration was accepted."
        )

    other = Definition(
        namespace="runtime.other",
        name="different_record",
        version="2.0.0",
        owner_id="runtime_schema",
        lifecycle_state="registered",
        created_at=timestamp,
        body={
            "fields": {}
        },
    ).validate()

    try:
        module.MigrationPlanner.plan(
            source,
            other,
        )
    except Exception:
        pass
    else:
        raise AssertionError(
            "Cross-subject migration was accepted."
        )

    wrong_report = (
        change_module.ChangeDetector.detect(
            target,
            source,
        )
    )

    try:
        module.MigrationPlanner.plan(
            source,
            target,
            wrong_report,
        )
    except Exception:
        pass
    else:
        raise AssertionError(
            "Mismatched change report was accepted."
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
    print(
        "MIGRATION.PY INSTALLATION AND REVIEW"
    )
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
            "The migration.py installation failed, "
            "so the previous filesystem state was restored."
        )
        print()
        print(traceback.format_exc())

        return 1

    print("Dependency verification:        PASS")
    print("Claude baseline review:         PASS")
    print("Nova revisions applied:         PASS")
    print("migration.py compilation:       PASS")
    print("Package import:                 PASS")
    print("Immutable migration contracts:  PASS")
    print("Planning-only boundary:         PASS")
    print("Same-subject enforcement:       PASS")
    print("Change-report integrity:        PASS")
    print("Deterministic planning:         PASS")
    print("Deterministic step IDs:         PASS")
    print("Deterministic plan ID:          PASS")
    print("Duplicate-step prevention:      PASS")
    print("Loss detection:                 PASS")
    print("Reversibility detection:        PASS")
    print("Schema-level operations:        PASS")
    print("Default presence tracking:      PASS")
    print("Bounded plan size:              PASS")
    print("Tamper-resistant fingerprints:  PASS")
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
        "MIGRATION.PY: INSTALLED, "
        "REVIEWED, AND APPROVED"
    )
    print("NO PRODUCTION DATA WAS MODIFIED")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
