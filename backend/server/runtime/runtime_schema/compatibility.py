# -*- coding: utf-8 -*-
"""Runtime Schema Compatibility.

This module enforces declared schema compatibility guarantees using the
semantic change facts produced by ``change_detection.py``.

Compatibility direction:

* BACKWARD:
  New readers must continue reading data written under prior schemas.

* FORWARD:
  Prior readers must continue reading data written under the new schema.

* FULL:
  Both backward and forward guarantees must hold.

* ``*_TRANSITIVE``:
  The guarantee is checked against every prior version rather than only the
  latest prior version.

* NONE:
  No structural compatibility guarantee is enforced.

The module remains independent of ``ports.py``. Runtime integration is
provided through a structural Protocol so ``ports.py`` can implement the
same contract later without creating an import cycle.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import (
    Any,
    Iterable,
    Protocol,
    Sequence,
    runtime_checkable,
)

from .change_detection import (
    ChangeDetector,
    ChangeReport,
    ClassifiedChange,
)
from .definitions import SchemaDefinition
from .diff_engine import DiffKind
from .serialization import structure_fingerprint
from .types import (
    ChangeClass,
    CompatibilityMode,
    SchemaCompatibilityError,
    SchemaDefinitionError,
)
from .versioning import SchemaVersion


@runtime_checkable
class RuntimeCompatibilityProvider(
    Protocol
):
    """Minimal runtime-version compatibility integration contract."""

    def is_runtime_compatible(
        self,
        required_runtime_version: str,
    ) -> bool:
        """Return whether the running runtime satisfies a requirement."""


@dataclass(
    frozen=True,
    slots=True,
    order=True,
)
class CompatibilityViolation:
    """One immutable compatibility-rule violation."""

    against_schema_id: str
    against_coordinate: str
    path: str
    direction: str
    rule: str
    detail: str
    change_class: ChangeClass

    def __post_init__(self) -> None:
        for field_name in (
            "against_schema_id",
            "against_coordinate",
            "path",
            "direction",
            "rule",
            "detail",
        ):
            value = getattr(
                self,
                field_name,
            )

            if (
                not isinstance(value, str)
                or not value
            ):
                raise SchemaCompatibilityError(
                    f"{field_name} must be a non-empty string"
                )

        if self.direction not in {
            "backward",
            "forward",
            "integrity",
        }:
            raise SchemaCompatibilityError(
                f"invalid compatibility direction: {self.direction!r}"
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
                raise SchemaCompatibilityError(
                    "invalid violation change class"
                ) from exc

    def to_canonical_dict(
        self,
    ) -> dict[str, Any]:
        """Return violation as plain JSON-native data."""
        return {
            "against_schema_id": (
                self.against_schema_id
            ),
            "against_coordinate": (
                self.against_coordinate
            ),
            "path": self.path,
            "direction": self.direction,
            "rule": self.rule,
            "detail": self.detail,
            "change_class": (
                self.change_class.value
            ),
        }


@dataclass(
    frozen=True,
    slots=True,
)
class CompatibilityReport:
    """Complete immutable schema-compatibility verdict."""

    candidate_schema_id: str
    candidate_coordinate: str
    mode: CompatibilityMode
    transitive: bool
    checked_against: tuple[str, ...]
    compatible: bool
    complete: bool
    violations: tuple[
        CompatibilityViolation,
        ...
    ]

    def __post_init__(self) -> None:
        for field_name in (
            "candidate_schema_id",
            "candidate_coordinate",
        ):
            value = getattr(
                self,
                field_name,
            )

            if (
                not isinstance(value, str)
                or not value
            ):
                raise SchemaCompatibilityError(
                    f"{field_name} must be a non-empty string"
                )

        if not isinstance(
            self.mode,
            CompatibilityMode,
        ):
            try:
                object.__setattr__(
                    self,
                    "mode",
                    CompatibilityMode(
                        self.mode
                    ),
                )
            except (
                TypeError,
                ValueError,
            ) as exc:
                raise SchemaCompatibilityError(
                    "invalid compatibility mode"
                ) from exc

        object.__setattr__(
            self,
            "checked_against",
            tuple(
                self.checked_against
            ),
        )

        object.__setattr__(
            self,
            "violations",
            tuple(
                self.violations
            ),
        )

        if (
            self.transitive
            != self.mode.is_transitive
        ):
            raise SchemaCompatibilityError(
                "transitive flag is inconsistent with mode"
            )

        expected_compatible = (
            self.complete
            and not self.violations
        )

        if (
            self.compatible
            != expected_compatible
        ):
            raise SchemaCompatibilityError(
                "compatible flag is inconsistent"
            )

    @property
    def violation_count(
        self,
    ) -> int:
        """Return total violation count."""
        return len(
            self.violations
        )

    @property
    def fingerprint(
        self,
    ) -> str:
        """Return deterministic report fingerprint."""
        return structure_fingerprint(
            self.to_canonical_dict()
        )

    def violations_for_direction(
        self,
        direction: str,
    ) -> tuple[
        CompatibilityViolation,
        ...
    ]:
        """Return violations for one compatibility direction."""
        if direction not in {
            "backward",
            "forward",
            "integrity",
        }:
            raise SchemaCompatibilityError(
                f"invalid compatibility direction: {direction!r}"
            )

        return tuple(
            violation
            for violation in self.violations
            if violation.direction == direction
        )

    def to_canonical_dict(
        self,
    ) -> dict[str, Any]:
        """Return report as plain JSON-native data."""
        return {
            "candidate_schema_id": (
                self.candidate_schema_id
            ),
            "candidate_coordinate": (
                self.candidate_coordinate
            ),
            "mode": self.mode.value,
            "transitive": self.transitive,
            "checked_against": list(
                self.checked_against
            ),
            "compatible": self.compatible,
            "complete": self.complete,
            "violations": [
                violation.to_canonical_dict()
                for violation in self.violations
            ],
            "violation_count": (
                self.violation_count
            ),
        }


def _violation(
    prior: SchemaDefinition,
    item: ClassifiedChange,
    *,
    direction: str,
    rule: str,
    detail: str,
) -> CompatibilityViolation:
    return CompatibilityViolation(
        against_schema_id=prior.schema_id,
        against_coordinate=(
            prior.coordinate()
        ),
        path=item.entry.path,
        direction=direction,
        rule=rule,
        detail=detail,
        change_class=(
            item.change_class
        ),
    )


def _backward_violations(
    prior: SchemaDefinition,
    classified: Sequence[
        ClassifiedChange
    ],
) -> list[
    CompatibilityViolation
]:
    """Return violations of new-reader compatibility."""
    violations: list[
        CompatibilityViolation
    ] = []

    for item in classified:
        entry = item.entry

        broken = False
        rule = ""
        detail = ""

        if (
            entry.kind
            is DiffKind.TYPE_CHANGED
        ):
            broken = True
            rule = "type_stability"
            detail = (
                "new readers cannot safely interpret "
                "prior data after a field type change"
            )

        elif (
            entry.kind
            is DiffKind.REQUIRED_CHANGED
            and bool(entry.after)
        ):
            broken = True
            rule = "required_field_tightening"
            detail = (
                "new readers require a field that "
                "may be absent from prior data"
            )

        elif (
            entry.kind
            is DiffKind.NULLABLE_CHANGED
            and not bool(entry.after)
        ):
            broken = True
            rule = "nullability_tightening"
            detail = (
                "new readers reject null values "
                "permitted by the prior schema"
            )

        elif (
            entry.kind
            is DiffKind.FIELD_ADDED
            and item.change_class
            is ChangeClass.BREAKING
        ):
            broken = True
            rule = "required_field_addition"
            detail = (
                "new required field has no default "
                "for prior data"
            )

        elif (
            entry.kind
            is DiffKind.CONSTRAINT_CHANGED
            and item.change_class
            is ChangeClass.BREAKING
        ):
            broken = True
            rule = "constraint_tightening"
            detail = (
                "new constraints reject values "
                "permitted by the prior schema"
            )

        if broken:
            violations.append(
                _violation(
                    prior,
                    item,
                    direction="backward",
                    rule=rule,
                    detail=detail,
                )
            )

    return violations


def _forward_violations(
    prior: SchemaDefinition,
    classified: Sequence[
        ClassifiedChange
    ],
) -> list[
    CompatibilityViolation
]:
    """Return violations of prior-reader compatibility."""
    violations: list[
        CompatibilityViolation
    ] = []

    for item in classified:
        entry = item.entry

        broken = False
        rule = ""
        detail = ""

        if (
            entry.kind
            is DiffKind.FIELD_REMOVED
        ):
            broken = True
            rule = "field_presence"
            detail = (
                "new data may omit a field required "
                "or expected by prior readers"
            )

        elif (
            entry.kind
            is DiffKind.TYPE_CHANGED
        ):
            broken = True
            rule = "type_stability"
            detail = (
                "prior readers cannot safely interpret "
                "the new field type"
            )

        elif (
            entry.kind
            is DiffKind.NULLABLE_CHANGED
            and bool(entry.after)
        ):
            broken = True
            rule = "nullability_relaxation"
            detail = (
                "new data may contain null values "
                "rejected by prior readers"
            )

        elif (
            entry.kind
            is DiffKind.REQUIRED_CHANGED
            and not bool(entry.after)
        ):
            broken = True
            rule = "required_field_relaxation"
            detail = (
                "new data may omit a field expected "
                "by prior readers"
            )

        elif (
            entry.kind
            is DiffKind.CONSTRAINT_CHANGED
            and item.change_class
            is ChangeClass.COMPATIBLE
        ):
            broken = True
            rule = "constraint_relaxation"
            detail = (
                "new data may contain values outside "
                "the prior schema constraints"
            )

        if broken:
            violations.append(
                _violation(
                    prior,
                    item,
                    direction="forward",
                    rule=rule,
                    detail=detail,
                )
            )

    return violations


def _validate_chain(
    candidate: SchemaDefinition,
    prior_versions: Iterable[
        SchemaDefinition
    ],
) -> tuple[
    SchemaDefinition,
    ...
]:
    """Validate, sort, and freeze the prior version chain."""
    if not isinstance(
        candidate,
        SchemaDefinition,
    ):
        raise SchemaCompatibilityError(
            "candidate must be a SchemaDefinition"
        )

    candidate.validate()

    priors = tuple(
        prior_versions
    )

    seen_versions: set[
        SchemaVersion
    ] = set()

    for prior in priors:
        if not isinstance(
            prior,
            SchemaDefinition,
        ):
            raise SchemaCompatibilityError(
                "every prior version must be a SchemaDefinition"
            )

        prior.validate()

        if (
            prior.namespace
            != candidate.namespace
            or prior.name
            != candidate.name
        ):
            raise SchemaCompatibilityError(
                "candidate and prior versions must "
                "belong to the same schema subject"
            )

        if prior.version in seen_versions:
            raise SchemaCompatibilityError(
                f"duplicate prior version: {prior.version}"
            )

        seen_versions.add(
            prior.version
        )

        if (
            prior.version
            >= candidate.version
        ):
            raise SchemaCompatibilityError(
                "candidate version must strictly succeed "
                f"every prior version; found {prior.version}"
            )

    return tuple(
        sorted(
            priors,
            key=lambda definition: (
                definition.version
            ),
        )
    )


class CompatibilityChecker:
    """Deterministic compatibility-policy evaluator."""

    def __init__(
        self,
        runtime_compatibility: (
            RuntimeCompatibilityProvider
            | None
        ) = None,
    ) -> None:
        if (
            runtime_compatibility
            is not None
            and not isinstance(
                runtime_compatibility,
                RuntimeCompatibilityProvider,
            )
        ):
            raise SchemaCompatibilityError(
                "runtime_compatibility does not "
                "satisfy RuntimeCompatibilityProvider"
            )

        self._runtime_compatibility = (
            runtime_compatibility
        )

    def check(
        self,
        candidate: SchemaDefinition,
        prior_versions: Iterable[
            SchemaDefinition
        ],
        mode: CompatibilityMode | str | None = None,
    ) -> CompatibilityReport:
        """Check candidate compatibility against a prior version chain."""
        priors = _validate_chain(
            candidate,
            prior_versions,
        )

        try:
            effective_mode = (
                candidate.compatibility_mode
                if mode is None
                else (
                    mode
                    if isinstance(
                        mode,
                        CompatibilityMode,
                    )
                    else CompatibilityMode(
                        mode
                    )
                )
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise SchemaCompatibilityError(
                f"invalid compatibility mode: {mode!r}"
            ) from exc

        if (
            effective_mode
            is CompatibilityMode.NONE
            or not priors
        ):
            return CompatibilityReport(
                candidate_schema_id=(
                    candidate.schema_id
                ),
                candidate_coordinate=(
                    candidate.coordinate()
                ),
                mode=effective_mode,
                transitive=(
                    effective_mode.is_transitive
                ),
                checked_against=(),
                compatible=True,
                complete=True,
                violations=(),
            )

        targets = (
            priors
            if effective_mode.is_transitive
            else priors[-1:]
        )

        base_mode = (
            effective_mode.base_mode
        )

        violations: list[
            CompatibilityViolation
        ] = []

        complete = True

        for prior in targets:
            change_report: ChangeReport = (
                ChangeDetector.detect(
                    prior,
                    candidate,
                )
            )

            if not change_report.complete:
                complete = False

                violations.append(
                    CompatibilityViolation(
                        against_schema_id=(
                            prior.schema_id
                        ),
                        against_coordinate=(
                            prior.coordinate()
                        ),
                        path="$",
                        direction="integrity",
                        rule="incomplete_diff",
                        detail=(
                            "compatibility cannot be certified "
                            "because structural analysis was truncated"
                        ),
                        change_class=(
                            ChangeClass.BREAKING
                        ),
                    )
                )

                continue

            if base_mode in {
                CompatibilityMode.BACKWARD,
                CompatibilityMode.FULL,
            }:
                violations.extend(
                    _backward_violations(
                        prior,
                        change_report.classified,
                    )
                )

            if base_mode in {
                CompatibilityMode.FORWARD,
                CompatibilityMode.FULL,
            }:
                violations.extend(
                    _forward_violations(
                        prior,
                        change_report.classified,
                    )
                )

        ordered_violations = tuple(
            sorted(
                violations,
                key=lambda violation: (
                    violation.against_coordinate,
                    violation.path,
                    violation.direction,
                    violation.rule,
                    violation.detail,
                ),
            )
        )

        return CompatibilityReport(
            candidate_schema_id=(
                candidate.schema_id
            ),
            candidate_coordinate=(
                candidate.coordinate()
            ),
            mode=effective_mode,
            transitive=(
                effective_mode.is_transitive
            ),
            checked_against=tuple(
                target.coordinate()
                for target in targets
            ),
            compatible=(
                complete
                and not ordered_violations
            ),
            complete=complete,
            violations=(
                ordered_violations
            ),
        )

    def runtime_requirement_satisfied(
        self,
        required_runtime_version: (
            str | None
        ),
    ) -> bool:
        """Return whether the runtime satisfies a declared requirement.

        No requirement means success. A declared requirement without a bound
        provider fails closed because compatibility cannot be demonstrated.
        """
        if required_runtime_version is None:
            return True

        if (
            not isinstance(
                required_runtime_version,
                str,
            )
            or not required_runtime_version.strip()
        ):
            raise SchemaCompatibilityError(
                "required_runtime_version must "
                "be a non-empty string or None"
            )

        SchemaVersion.parse(
            required_runtime_version
        )

        if self._runtime_compatibility is None:
            return False

        try:
            return bool(
                self._runtime_compatibility
                .is_runtime_compatible(
                    required_runtime_version
                )
            )
        except Exception as exc:
            raise SchemaCompatibilityError(
                "runtime compatibility provider failed"
            ) from exc


__all__ = [
    "CompatibilityChecker",
    "CompatibilityReport",
    "CompatibilityViolation",
    "RuntimeCompatibilityProvider",
]
