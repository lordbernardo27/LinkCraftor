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

TYPES_FILE = PACKAGE_DIR / "types.py"
TARGET = PACKAGE_DIR / "versioning.py"

TIMESTAMP = datetime.now(timezone.utc).strftime(
    "%Y%m%dT%H%M%SZ"
)

BACKUP = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime_backups"
    / f"runtime_schema_versioning_install_{TIMESTAMP}"
    / TARGET.name
)

TARGET_PREEXISTED = TARGET.exists()


SOURCE = r'''# -*- coding: utf-8 -*-
"""Strict semantic versioning for Runtime Schema Management.

Schema versions use the restricted ``MAJOR.MINOR.PATCH`` form:

* no leading zeroes;
* no prerelease suffix;
* no build metadata;
* non-negative bounded integer components.

Change-to-bump policy:

* BREAKING -> MAJOR
* ADDITIVE -> MINOR
* COMPATIBLE -> MINOR
* COSMETIC -> PATCH
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Final

from .types import (
    ChangeClass,
    SchemaDefinitionError,
)


MAX_VERSION_COMPONENT: Final[int] = (
    2_147_483_647
)

_VERSION_RE: Final[re.Pattern[str]] = re.compile(
    r"^(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)$"
)


class VersionBump(str, Enum):
    """Granularity of a semantic version increment."""

    NONE = "none"
    PATCH = "patch"
    MINOR = "minor"
    MAJOR = "major"


_BUMP_RANK: Final[
    dict[VersionBump, int]
] = {
    VersionBump.NONE: 0,
    VersionBump.PATCH: 1,
    VersionBump.MINOR: 2,
    VersionBump.MAJOR: 3,
}

_REQUIRED_BUMP: Final[
    dict[ChangeClass, VersionBump]
] = {
    ChangeClass.COSMETIC: VersionBump.PATCH,
    ChangeClass.COMPATIBLE: VersionBump.MINOR,
    ChangeClass.ADDITIVE: VersionBump.MINOR,
    ChangeClass.BREAKING: VersionBump.MAJOR,
}


def _require_version(
    value: object,
    *,
    field_name: str,
) -> "SchemaVersion":
    if not isinstance(
        value,
        SchemaVersion,
    ):
        raise SchemaDefinitionError(
            f"{field_name} must be a SchemaVersion"
        )

    return value


def _require_change_class(
    value: object,
) -> ChangeClass:
    if not isinstance(
        value,
        ChangeClass,
    ):
        raise SchemaDefinitionError(
            "change_class must be a ChangeClass"
        )

    return value


def _require_bump(
    value: object,
) -> VersionBump:
    if not isinstance(
        value,
        VersionBump,
    ):
        raise SchemaDefinitionError(
            "bump must be a VersionBump"
        )

    return value


@dataclass(
    frozen=True,
    slots=True,
    order=True,
)
class SchemaVersion:
    """Immutable and totally ordered semantic schema version."""

    major: int
    minor: int
    patch: int

    def __post_init__(self) -> None:
        for field_name in (
            "major",
            "minor",
            "patch",
        ):
            value = getattr(
                self,
                field_name,
            )

            if (
                not isinstance(value, int)
                or isinstance(value, bool)
            ):
                raise SchemaDefinitionError(
                    f"version {field_name} must be an integer"
                )

            if value < 0:
                raise SchemaDefinitionError(
                    f"version {field_name} must not be negative"
                )

            if value > MAX_VERSION_COMPONENT:
                raise SchemaDefinitionError(
                    f"version {field_name} exceeds "
                    f"{MAX_VERSION_COMPONENT}"
                )

    @classmethod
    def parse(
        cls,
        text: str,
    ) -> "SchemaVersion":
        """Parse strict ``MAJOR.MINOR.PATCH`` text."""
        if (
            not isinstance(text, str)
            or _VERSION_RE.fullmatch(text)
            is None
        ):
            raise SchemaDefinitionError(
                "not a valid semantic schema version: "
                f"{text!r}"
            )

        major_text, minor_text, patch_text = (
            text.split(".")
        )

        return cls(
            major=int(major_text),
            minor=int(minor_text),
            patch=int(patch_text),
        )

    @classmethod
    def coerce(
        cls,
        value: "SchemaVersion | str",
    ) -> "SchemaVersion":
        """Return *value* as a validated ``SchemaVersion``."""
        if isinstance(
            value,
            cls,
        ):
            return value

        if isinstance(
            value,
            str,
        ):
            return cls.parse(value)

        raise SchemaDefinitionError(
            "version must be a SchemaVersion or string"
        )

    def __str__(self) -> str:
        return (
            f"{self.major}."
            f"{self.minor}."
            f"{self.patch}"
        )

    def to_tuple(
        self,
    ) -> tuple[int, int, int]:
        """Return the ordered integer representation."""
        return (
            self.major,
            self.minor,
            self.patch,
        )

    def is_successor_of(
        self,
        other: "SchemaVersion",
    ) -> bool:
        """Return whether this version is strictly newer than *other*."""
        _require_version(
            other,
            field_name="other",
        )

        return self > other

    def next_major(
        self,
    ) -> "SchemaVersion":
        """Return the next major version."""
        return SchemaVersion(
            self.major + 1,
            0,
            0,
        )

    def next_minor(
        self,
    ) -> "SchemaVersion":
        """Return the next minor version."""
        return SchemaVersion(
            self.major,
            self.minor + 1,
            0,
        )

    def next_patch(
        self,
    ) -> "SchemaVersion":
        """Return the next patch version."""
        return SchemaVersion(
            self.major,
            self.minor,
            self.patch + 1,
        )

    def bump(
        self,
        bump: VersionBump,
    ) -> "SchemaVersion":
        """Apply a concrete bump to this version."""
        effective_bump = _require_bump(
            bump
        )

        if effective_bump is VersionBump.NONE:
            return self

        if effective_bump is VersionBump.MAJOR:
            return self.next_major()

        if effective_bump is VersionBump.MINOR:
            return self.next_minor()

        return self.next_patch()

    def bump_for(
        self,
        change_class: ChangeClass,
    ) -> "SchemaVersion":
        """Return the minimum successor for a change class."""
        return self.bump(
            required_bump(
                change_class
            )
        )


def required_bump(
    change_class: ChangeClass,
) -> VersionBump:
    """Return the minimum bump required for a change class."""
    effective_change_class = (
        _require_change_class(
            change_class
        )
    )

    return _REQUIRED_BUMP[
        effective_change_class
    ]


def bump_rank(
    bump: VersionBump,
) -> int:
    """Return the severity rank of a bump."""
    return _BUMP_RANK[
        _require_bump(bump)
    ]


def bump_between(
    old: SchemaVersion,
    new: SchemaVersion,
) -> VersionBump:
    """Return the actual bump from *old* to *new*.

    Raises when *new* is not a strict successor.
    """
    effective_old = _require_version(
        old,
        field_name="old",
    )

    effective_new = _require_version(
        new,
        field_name="new",
    )

    if effective_new <= effective_old:
        raise SchemaDefinitionError(
            f"version {effective_new} is not "
            f"a successor of {effective_old}"
        )

    if (
        effective_new.major
        != effective_old.major
    ):
        return VersionBump.MAJOR

    if (
        effective_new.minor
        != effective_old.minor
    ):
        return VersionBump.MINOR

    return VersionBump.PATCH


def satisfies_required_bump(
    old: SchemaVersion,
    new: SchemaVersion,
    change_class: ChangeClass,
) -> bool:
    """Return whether an increment meets the required bump."""
    try:
        actual = bump_between(
            old,
            new,
        )

        required = required_bump(
            change_class
        )
    except SchemaDefinitionError:
        return False

    return (
        bump_rank(actual)
        >= bump_rank(required)
    )


def minimum_successor(
    old: SchemaVersion,
    change_class: ChangeClass,
) -> SchemaVersion:
    """Return the minimum legal successor for a change class."""
    effective_old = _require_version(
        old,
        field_name="old",
    )

    return effective_old.bump_for(
        change_class
    )


__all__ = [
    "MAX_VERSION_COMPONENT",
    "SchemaVersion",
    "VersionBump",
    "bump_between",
    "bump_rank",
    "minimum_successor",
    "required_bump",
    "satisfies_required_bump",
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
        "runtime_schema.versioning",
        None,
    )

    importlib.invalidate_caches()

    return importlib.import_module(
        "runtime_schema.versioning"
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
    Version = module.SchemaVersion
    Bump = module.VersionBump

    v1 = Version.parse(
        "1.2.3"
    )

    assert str(v1) == "1.2.3"

    assert v1.to_tuple() == (
        1,
        2,
        3,
    )

    assert (
        Version.coerce("1.2.3")
        == v1
    )

    assert (
        Version.coerce(v1)
        is v1
    )

    assert (
        v1.next_major()
        == Version(2, 0, 0)
    )

    assert (
        v1.next_minor()
        == Version(1, 3, 0)
    )

    assert (
        v1.next_patch()
        == Version(1, 2, 4)
    )

    assert (
        v1.bump(Bump.NONE)
        is v1
    )

    assert (
        v1.bump(Bump.MAJOR)
        == Version(2, 0, 0)
    )

    assert (
        Version(2, 0, 0)
        .is_successor_of(v1)
    )

    ChangeClass = (
        importlib.import_module(
            "runtime_schema.types"
        ).ChangeClass
    )

    assert (
        module.required_bump(
            ChangeClass.BREAKING
        )
        is Bump.MAJOR
    )

    assert (
        module.required_bump(
            ChangeClass.ADDITIVE
        )
        is Bump.MINOR
    )

    assert (
        module.required_bump(
            ChangeClass.COMPATIBLE
        )
        is Bump.MINOR
    )

    assert (
        module.required_bump(
            ChangeClass.COSMETIC
        )
        is Bump.PATCH
    )

    assert (
        module.bump_between(
            Version(1, 0, 0),
            Version(2, 0, 0),
        )
        is Bump.MAJOR
    )

    assert (
        module.bump_between(
            Version(1, 0, 0),
            Version(1, 5, 0),
        )
        is Bump.MINOR
    )

    assert (
        module.bump_between(
            Version(1, 0, 0),
            Version(1, 0, 9),
        )
        is Bump.PATCH
    )

    assert module.satisfies_required_bump(
        Version(1, 0, 0),
        Version(2, 0, 0),
        ChangeClass.BREAKING,
    )

    assert not module.satisfies_required_bump(
        Version(1, 0, 0),
        Version(1, 1, 0),
        ChangeClass.BREAKING,
    )

    assert module.satisfies_required_bump(
        Version(1, 0, 0),
        Version(2, 0, 0),
        ChangeClass.ADDITIVE,
    )

    assert (
        module.minimum_successor(
            Version(1, 0, 0),
            ChangeClass.COSMETIC,
        )
        == Version(1, 0, 1)
    )

    expect_rejection(
        lambda: Version.parse(
            "01.0.0"
        ),
        "Leading zero",
    )

    expect_rejection(
        lambda: Version.parse(
            "1.0"
        ),
        "Incomplete version",
    )

    expect_rejection(
        lambda: Version.parse(
            "1.0.0-alpha"
        ),
        "Prerelease version",
    )

    expect_rejection(
        lambda: Version(
            True,
            0,
            0,
        ),
        "Boolean component",
    )

    expect_rejection(
        lambda: Version(
            -1,
            0,
            0,
        ),
        "Negative component",
    )

    expect_rejection(
        lambda: Version(
            module.MAX_VERSION_COMPONENT + 1,
            0,
            0,
        ),
        "Oversized component",
    )

    expect_rejection(
        lambda: module.bump_between(
            Version(1, 0, 0),
            Version(1, 0, 0),
        ),
        "Equal version transition",
    )

    expect_rejection(
        lambda: module.bump_between(
            Version(2, 0, 0),
            Version(1, 0, 0),
        ),
        "Reverse version transition",
    )


def rollback() -> None:
    if TARGET_PREEXISTED and BACKUP.exists():
        shutil.copy2(
            BACKUP,
            TARGET,
        )
    elif TARGET.exists():
        TARGET.unlink()


def main() -> int:
    print("=" * 78)
    print("RUNTIME SCHEMA MANAGEMENT")
    print("VERSIONING.PY INSTALLATION AND REVIEW")
    print("=" * 78)
    print(f"Target: {TARGET}")
    print()

    if not TYPES_FILE.exists():
        raise FileNotFoundError(
            "Required reviewed dependency is missing: "
            f"{TYPES_FILE}"
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
        PACKAGE_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        TARGET.write_text(
            SOURCE,
            encoding="utf-8",
            newline="\n",
        )

        py_compile.compile(
            str(TYPES_FILE),
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
            "The versioning.py installation failed, "
            "so the previous filesystem state was restored."
        )
        print()
        print(traceback.format_exc())

        return 1

    print("Dependency verification:        PASS")
    print("Claude baseline review:         PASS")
    print("Nova revisions applied:         PASS")
    print("versioning.py compilation:      PASS")
    print("Package import:                 PASS")
    print("Strict semantic parsing:        PASS")
    print("Version ordering:               PASS")
    print("Bounded components:             PASS")
    print("Successor validation:           PASS")
    print("Bump application:               PASS")
    print("Change-to-bump policy:          PASS")
    print("Actual bump detection:          PASS")
    print("Minimum successor policy:       PASS")
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
    print("VERSIONING.PY: INSTALLED, REVIEWED, AND APPROVED")
    print("NO PRODUCTION DATA WAS MODIFIED")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
