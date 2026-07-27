# -*- coding: utf-8 -*-
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
