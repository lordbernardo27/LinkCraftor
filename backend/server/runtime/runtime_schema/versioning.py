# -*- coding: utf-8 -*-
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
