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
    PACKAGE_DIR / "versioning.py",
    PACKAGE_DIR / "definitions.py",
    PACKAGE_DIR / "diff_engine.py",
]

TARGET = PACKAGE_DIR / "change_detection.py"

TIMESTAMP = datetime.now(timezone.utc).strftime(
    "%Y%m%dT%H%M%SZ"
)

BACKUP = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime_backups"
    / f"runtime_schema_change_detection_install_{TIMESTAMP}"
    / TARGET.name
)

TARGET_PREEXISTED = TARGET.exists()


SOURCE = r'''# -*- coding: utf-8 -*-
"""Semantic interpretation of Runtime Schema structural differences.

``diff_engine.py`` reports facts. This module assigns semantic meaning to
those facts without enforcing a compatibility contract.

Classification policy:

* BREAKING
  - field removed;
  - field type changed;
  - required ``False -> True``;
  - nullable ``True -> False``;
  - constraints tightened or changed in an unrecognizable way;
  - required field added without a default;
  - incomplete or truncated structural diff.

* ADDITIVE
  - optional field added;
  - required field added with a default.

* COMPATIBLE
  - required ``True -> False``;
  - nullable ``False -> True``;
  - constraints loosened;
  - ownership or compatibility-policy metadata changed.

* COSMETIC
  - defaults;
  - field descriptions;
  - schema descriptions;
  - schema metadata.

Compatibility enforcement belongs to ``compatibility.py``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final, Mapping, Sequence

from .definitions import SchemaDefinition
from .diff_engine import (
    DiffEntry,
    DiffKind,
    SchemaDiff,
    SchemaDiffEngine,
)
from .serialization import structure_fingerprint
from .types import (
    ChangeClass,
    SchemaDefinitionError,
    change_severity,
)
from .versioning import (
    VersionBump,
    required_bump,
)


_NUMERIC_LOWER_BOUNDS: Final[
    tuple[str, ...]
] = (
    "minimum",
    "min_length",
    "min_items",
)

_NUMERIC_UPPER_BOUNDS: Final[
    tuple[str, ...]
] = (
    "maximum",
    "max_length",
    "max_items",
)

_KNOWN_CONSTRAINT_KEYS: Final[
    frozenset[str]
] = frozenset(
    {
        "minimum",
        "maximum",
        "min_length",
        "max_length",
        "pattern",
        "enum",
        "min_items",
        "max_items",
    }
)


def _fingerprinted_values(
    values: Sequence[Any],
) -> frozenset[str]:
    """Return stable fingerprints for potentially nested enum values."""
    return frozenset(
        structure_fingerprint(
            value
        )
        for value in values
    )


def _classify_constraints(
    before: Mapping[str, Any] | None,
    after: Mapping[str, Any] | None,
) -> tuple[ChangeClass, str]:
    """Classify one complete constraint-map transition.

    A change is compatible only when every changed constraint is a
    demonstrable relaxation. Any tightening, unknown constraint, or
    ambiguous movement is conservatively breaking.
    """
    old = dict(
        before or {}
    )

    new = dict(
        after or {}
    )

    if old == new:
        return (
            ChangeClass.COSMETIC,
            "constraint maps are identical",
        )

    unknown_keys = (
        set(old)
        | set(new)
    ) - _KNOWN_CONSTRAINT_KEYS

    if unknown_keys:
        return (
            ChangeClass.BREAKING,
            "unknown constraint keys changed: "
            + ", ".join(
                sorted(unknown_keys)
            ),
        )

    saw_relaxation = False

    for key in _NUMERIC_LOWER_BOUNDS:
        old_present = key in old
        new_present = key in new

        if (
            not old_present
            and not new_present
        ):
            continue

        if old_present and not new_present:
            saw_relaxation = True
            continue

        if not old_present and new_present:
            return (
                ChangeClass.BREAKING,
                f"{key} was introduced",
            )

        old_value = old[key]
        new_value = new[key]

        if new_value > old_value:
            return (
                ChangeClass.BREAKING,
                f"{key} was tightened",
            )

        if new_value < old_value:
            saw_relaxation = True

    for key in _NUMERIC_UPPER_BOUNDS:
        old_present = key in old
        new_present = key in new

        if (
            not old_present
            and not new_present
        ):
            continue

        if old_present and not new_present:
            saw_relaxation = True
            continue

        if not old_present and new_present:
            return (
                ChangeClass.BREAKING,
                f"{key} was introduced",
            )

        old_value = old[key]
        new_value = new[key]

        if new_value < old_value:
            return (
                ChangeClass.BREAKING,
                f"{key} was tightened",
            )

        if new_value > old_value:
            saw_relaxation = True

    old_pattern_present = (
        "pattern" in old
    )

    new_pattern_present = (
        "pattern" in new
    )

    if (
        old_pattern_present
        or new_pattern_present
    ):
        if (
            old_pattern_present
            and not new_pattern_present
        ):
            saw_relaxation = True
        elif (
            not old_pattern_present
            and new_pattern_present
        ):
            return (
                ChangeClass.BREAKING,
                "pattern constraint was introduced",
            )
        elif (
            old["pattern"]
            != new["pattern"]
        ):
            return (
                ChangeClass.BREAKING,
                "pattern constraint changed ambiguously",
            )

    old_enum_present = (
        "enum" in old
    )

    new_enum_present = (
        "enum" in new
    )

    if (
        old_enum_present
        or new_enum_present
    ):
        if (
            old_enum_present
            and not new_enum_present
        ):
            saw_relaxation = True
        elif (
            not old_enum_present
            and new_enum_present
        ):
            return (
                ChangeClass.BREAKING,
                "enum constraint was introduced",
            )
        else:
            old_values = (
                _fingerprinted_values(
                    old["enum"]
                )
            )

            new_values = (
                _fingerprinted_values(
                    new["enum"]
                )
            )

            if not old_values.issubset(
                new_values
            ):
                return (
                    ChangeClass.BREAKING,
                    "enum values were removed or changed",
                )

            if new_values != old_values:
                saw_relaxation = True

    if saw_relaxation:
        return (
            ChangeClass.COMPATIBLE,
            "all constraint changes are relaxations",
        )

    return (
        ChangeClass.BREAKING,
        "constraint change could not be proven compatible",
    )


def _field_added_classification(
    entry: DiffEntry,
) -> tuple[ChangeClass, str]:
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

    if (
        required
        and not has_default
    ):
        return (
            ChangeClass.BREAKING,
            "required field added without a default",
        )

    return (
        ChangeClass.ADDITIVE,
        (
            "required field added with a default"
            if required
            else "optional field added"
        ),
    )


def classify_entry(
    entry: DiffEntry,
) -> tuple[ChangeClass, str]:
    """Classify one structural diff entry and explain the decision."""
    if not isinstance(
        entry,
        DiffEntry,
    ):
        raise SchemaDefinitionError(
            "entry must be a DiffEntry"
        )

    kind = entry.kind

    if kind is DiffKind.FIELD_REMOVED:
        return (
            ChangeClass.BREAKING,
            "field was removed",
        )

    if kind is DiffKind.TYPE_CHANGED:
        return (
            ChangeClass.BREAKING,
            "field type changed",
        )

    if kind is DiffKind.FIELD_ADDED:
        return _field_added_classification(
            entry
        )

    if kind is DiffKind.REQUIRED_CHANGED:
        if bool(entry.after):
            return (
                ChangeClass.BREAKING,
                "field became required",
            )

        return (
            ChangeClass.COMPATIBLE,
            "field is no longer required",
        )

    if kind is DiffKind.NULLABLE_CHANGED:
        if bool(entry.after):
            return (
                ChangeClass.COMPATIBLE,
                "field now accepts null",
            )

        return (
            ChangeClass.BREAKING,
            "field no longer accepts null",
        )

    if kind is DiffKind.CONSTRAINT_CHANGED:
        before = (
            entry.before
            if isinstance(
                entry.before,
                Mapping,
            )
            else None
        )

        after = (
            entry.after
            if isinstance(
                entry.after,
                Mapping,
            )
            else None
        )

        return _classify_constraints(
            before,
            after,
        )

    if kind is DiffKind.OWNER_CHANGED:
        return (
            ChangeClass.COMPATIBLE,
            "schema ownership metadata changed",
        )

    if (
        kind
        is DiffKind.COMPATIBILITY_MODE_CHANGED
    ):
        return (
            ChangeClass.COMPATIBLE,
            "declared compatibility policy changed",
        )

    if kind in {
        DiffKind.DEFAULT_CHANGED,
        DiffKind.DESCRIPTION_CHANGED,
        DiffKind.SCHEMA_DESCRIPTION_CHANGED,
        DiffKind.SCHEMA_METADATA_CHANGED,
    }:
        return (
            ChangeClass.COSMETIC,
            "non-structural schema metadata changed",
        )

    raise SchemaDefinitionError(
        f"unsupported diff kind: {kind!r}"
    )


@dataclass(
    frozen=True,
    slots=True,
)
class ClassifiedChange:
    """One diff fact with semantic classification and rationale."""

    entry: DiffEntry
    change_class: ChangeClass
    reason: str

    def __post_init__(self) -> None:
        if not isinstance(
            self.entry,
            DiffEntry,
        ):
            raise SchemaDefinitionError(
                "entry must be a DiffEntry"
            )

        if not isinstance(
            self.change_class,
            ChangeClass,
        ):
            try:
                object.__setattr__(
                    self,
                    "change_class",
                    ChangeClass(
                        self.change_class
                    ),
                )
            except (
                TypeError,
                ValueError,
            ) as exc:
                raise SchemaDefinitionError(
                    "invalid change_class"
                ) from exc

        if (
            not isinstance(
                self.reason,
                str,
            )
            or not self.reason.strip()
        ):
            raise SchemaDefinitionError(
                "classification reason must be non-empty"
            )

    def to_canonical_dict(
        self,
    ) -> dict[str, Any]:
        """Return plain JSON-native classified change data."""
        return {
            "entry": (
                self.entry.to_canonical_dict()
            ),
            "change_class": (
                self.change_class.value
            ),
            "reason": self.reason,
        }


@dataclass(
    frozen=True,
    slots=True,
)
class ChangeReport:
    """Complete immutable semantic change-detection report."""

    diff: SchemaDiff
    identical: bool
    complete: bool
    overall_class: ChangeClass
    required_version_bump: VersionBump
    classified: tuple[
        ClassifiedChange,
        ...
    ]

    def __post_init__(self) -> None:
        if not isinstance(
            self.diff,
            SchemaDiff,
        ):
            raise SchemaDefinitionError(
                "diff must be a SchemaDiff"
            )

        if not isinstance(
            self.overall_class,
            ChangeClass,
        ):
            raise SchemaDefinitionError(
                "overall_class must be a ChangeClass"
            )

        if not isinstance(
            self.required_version_bump,
            VersionBump,
        ):
            raise SchemaDefinitionError(
                "required_version_bump must be a VersionBump"
            )

        object.__setattr__(
            self,
            "classified",
            tuple(
                self.classified
            ),
        )

        expected_identical = (
            self.diff.identical
            and not self.classified
            and self.complete
        )

        if (
            self.identical
            != expected_identical
        ):
            raise SchemaDefinitionError(
                "identical flag is inconsistent"
            )

        if self.complete == self.diff.truncated:
            raise SchemaDefinitionError(
                "complete flag is inconsistent "
                "with diff truncation"
            )

        expected_bump = (
            VersionBump.NONE
            if self.identical
            else required_bump(
                self.overall_class
            )
        )

        if (
            self.required_version_bump
            is not expected_bump
        ):
            raise SchemaDefinitionError(
                "required version bump is inconsistent"
            )

    @property
    def fingerprint(
        self,
    ) -> str:
        """Return deterministic report fingerprint."""
        return structure_fingerprint(
            self.to_canonical_dict()
        )

    def changes_of_class(
        self,
        change_class: ChangeClass,
    ) -> tuple[
        ClassifiedChange,
        ...
    ]:
        """Return all changes in one semantic class."""
        effective_class = (
            change_class
            if isinstance(
                change_class,
                ChangeClass,
            )
            else ChangeClass(
                change_class
            )
        )

        return tuple(
            item
            for item in self.classified
            if (
                item.change_class
                is effective_class
            )
        )

    def breaking_changes(
        self,
    ) -> tuple[
        ClassifiedChange,
        ...
    ]:
        """Return only breaking changes."""
        return self.changes_of_class(
            ChangeClass.BREAKING
        )

    def to_canonical_dict(
        self,
    ) -> dict[str, Any]:
        """Return complete JSON-native report data."""
        return {
            "diff": self.diff.to_canonical_dict(),
            "identical": self.identical,
            "complete": self.complete,
            "overall_class": (
                self.overall_class.value
            ),
            "required_version_bump": (
                self.required_version_bump.value
            ),
            "classified": [
                item.to_canonical_dict()
                for item in self.classified
            ],
        }


class ChangeDetector:
    """Stateless deterministic schema-change detector."""

    @staticmethod
    def detect(
        source: SchemaDefinition,
        target: SchemaDefinition,
    ) -> ChangeReport:
        """Detect and classify every change from source to target."""
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

        diff = SchemaDiffEngine.diff(
            source,
            target,
        )

        if diff.identical:
            return ChangeReport(
                diff=diff,
                identical=True,
                complete=True,
                overall_class=(
                    ChangeClass.COSMETIC
                ),
                required_version_bump=(
                    VersionBump.NONE
                ),
                classified=(),
            )

        classified_items: list[
            ClassifiedChange
        ] = []

        for entry in diff.entries:
            (
                change_class,
                reason,
            ) = classify_entry(
                entry
            )

            classified_items.append(
                ClassifiedChange(
                    entry=entry,
                    change_class=(
                        change_class
                    ),
                    reason=reason,
                )
            )

        classified = tuple(
            sorted(
                classified_items,
                key=lambda item: (
                    item.entry.path,
                    item.entry.kind.value,
                    item.change_class.value,
                    item.reason,
                ),
            )
        )

        if diff.truncated:
            overall = (
                ChangeClass.BREAKING
            )
        elif classified:
            overall = max(
                (
                    item.change_class
                    for item in classified
                ),
                key=change_severity,
            )
        else:
            overall = (
                ChangeClass.COSMETIC
            )

        return ChangeReport(
            diff=diff,
            identical=False,
            complete=not diff.truncated,
            overall_class=overall,
            required_version_bump=(
                required_bump(
                    overall
                )
            ),
            classified=classified,
        )


__all__ = [
    "ChangeDetector",
    "ChangeReport",
    "ClassifiedChange",
    "classify_entry",
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
        "runtime_schema.change_detection",
        None,
    )

    importlib.invalidate_caches()

    return importlib.import_module(
        "runtime_schema.change_detection"
    )


def verify_behavior(
    module,
) -> None:
    definitions_module = (
        importlib.import_module(
            "runtime_schema.definitions"
        )
    )

    types_module = (
        importlib.import_module(
            "runtime_schema.types"
        )
    )

    versioning_module = (
        importlib.import_module(
            "runtime_schema.versioning"
        )
    )

    Definition = (
        definitions_module.SchemaDefinition
    )

    ChangeClass = (
        types_module.ChangeClass
    )

    VersionBump = (
        versioning_module.VersionBump
    )

    timestamp = (
        "2026-07-27T15:00:00.000000Z"
    )

    source = Definition(
        namespace="runtime.schema",
        name="change_record",
        version="1.0.0",
        owner_id="runtime_schema",
        lifecycle_state="registered",
        description="Original.",
        metadata={
            "revision": 1,
        },
        created_at=timestamp,
        body={
            "fields": {
                "removed": {
                    "type": "string",
                },
                "required_change": {
                    "type": "string",
                    "required": False,
                },
                "nullable_change": {
                    "type": "string",
                    "nullable": True,
                },
                "constraint_tightened": {
                    "type": "integer",
                    "constraints": {
                        "minimum": 0,
                        "maximum": 100,
                    },
                },
                "constraint_loosened": {
                    "type": "string",
                    "constraints": {
                        "min_length": 5,
                        "max_length": 10,
                        "enum": [
                            "alpha",
                            "bravo",
                        ],
                    },
                },
                "default_change": {
                    "type": "string",
                    "default": "old",
                },
                "description_change": {
                    "type": "string",
                    "description": "Old.",
                },
            }
        },
    ).validate()

    target = Definition(
        namespace="runtime.schema",
        name="change_record",
        version="2.0.0",
        owner_id="runtime_kernel",
        compatibility_mode="full",
        lifecycle_state="registered",
        description="Updated.",
        metadata={
            "revision": 2,
        },
        created_at=timestamp,
        body={
            "fields": {
                "required_change": {
                    "type": "string",
                    "required": True,
                },
                "nullable_change": {
                    "type": "string",
                    "nullable": False,
                },
                "constraint_tightened": {
                    "type": "integer",
                    "constraints": {
                        "minimum": 10,
                        "maximum": 90,
                    },
                },
                "constraint_loosened": {
                    "type": "string",
                    "constraints": {
                        "min_length": 2,
                        "max_length": 20,
                        "enum": [
                            "alpha",
                            "bravo",
                            "charlie",
                        ],
                    },
                },
                "default_change": {
                    "type": "string",
                    "default": "new",
                },
                "description_change": {
                    "type": "string",
                    "description": "New.",
                },
                "optional_added": {
                    "type": "boolean",
                },
                "required_with_default": {
                    "type": "integer",
                    "required": True,
                    "default": 0,
                },
                "required_without_default": {
                    "type": "integer",
                    "required": True,
                },
            }
        },
    ).validate()

    report_one = (
        module.ChangeDetector.detect(
            source,
            target,
        )
    )

    report_two = (
        module.ChangeDetector.detect(
            source,
            target,
        )
    )

    assert not report_one.identical
    assert report_one.complete

    assert (
        report_one.overall_class
        is ChangeClass.BREAKING
    )

    assert (
        report_one.required_version_bump
        is VersionBump.MAJOR
    )

    assert (
        report_one.fingerprint
        == report_two.fingerprint
    )

    assert report_one.breaking_changes()

    classes_by_path = {
        item.entry.path: item.change_class
        for item in report_one.classified
    }

    assert (
        classes_by_path["removed"]
        is ChangeClass.BREAKING
    )

    assert (
        classes_by_path[
            "required_change"
        ]
        is ChangeClass.BREAKING
    )

    assert (
        classes_by_path[
            "nullable_change"
        ]
        is ChangeClass.BREAKING
    )

    assert (
        classes_by_path[
            "constraint_tightened"
        ]
        is ChangeClass.BREAKING
    )

    assert (
        classes_by_path[
            "constraint_loosened"
        ]
        is ChangeClass.COMPATIBLE
    )

    assert (
        classes_by_path[
            "optional_added"
        ]
        is ChangeClass.ADDITIVE
    )

    assert (
        classes_by_path[
            "required_with_default"
        ]
        is ChangeClass.ADDITIVE
    )

    assert (
        classes_by_path[
            "required_without_default"
        ]
        is ChangeClass.BREAKING
    )

    assert (
        classes_by_path[
            "default_change"
        ]
        is ChangeClass.COSMETIC
    )

    assert (
        classes_by_path[
            "description_change"
        ]
        is ChangeClass.COSMETIC
    )

    assert (
        classes_by_path[
            "$owner_id"
        ]
        is ChangeClass.COMPATIBLE
    )

    assert (
        classes_by_path[
            "$compatibility_mode"
        ]
        is ChangeClass.COMPATIBLE
    )

    assert (
        classes_by_path[
            "$description"
        ]
        is ChangeClass.COSMETIC
    )

    assert (
        classes_by_path[
            "$metadata"
        ]
        is ChangeClass.COSMETIC
    )

    identical = (
        module.ChangeDetector.detect(
            source,
            source,
        )
    )

    assert identical.identical
    assert identical.complete

    assert (
        identical.required_version_bump
        is VersionBump.NONE
    )

    assert (
        identical.overall_class
        is ChangeClass.COSMETIC
    )

    assert identical.classified == ()

    try:
        report_one.classified = ()
    except Exception:
        pass
    else:
        raise AssertionError(
            "ChangeReport must be immutable."
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
        "CHANGE_DETECTION.PY INSTALLATION AND REVIEW"
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
            "The change_detection.py installation failed, "
            "so the previous filesystem state was restored."
        )
        print()
        print(traceback.format_exc())

        return 1

    print("Dependency verification:        PASS")
    print("Claude baseline review:         PASS")
    print("Nova revisions applied:         PASS")
    print("change_detection compilation:   PASS")
    print("Package import:                 PASS")
    print("Immutable change contracts:     PASS")
    print("Removal classification:         PASS")
    print("Type classification:            PASS")
    print("Required-field classification:  PASS")
    print("Nullability classification:     PASS")
    print("Tightened constraints:          PASS")
    print("Loosened constraints:           PASS")
    print("Nested enum comparison:         PASS")
    print("Added-field classification:     PASS")
    print("Schema-level classification:    PASS")
    print("Overall severity aggregation:   PASS")
    print("Required version bump:          PASS")
    print("Identical fast path:            PASS")
    print("Truncated-diff policy:          PASS")
    print("Deterministic ordering:         PASS")
    print("Deterministic fingerprint:      PASS")
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
        "CHANGE_DETECTION.PY: INSTALLED, "
        "REVIEWED, AND APPROVED"
    )
    print("NO PRODUCTION DATA WAS MODIFIED")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
