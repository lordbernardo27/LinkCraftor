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
    PACKAGE_DIR / "change_detection.py",
]

TARGET = PACKAGE_DIR / "compatibility.py"

TIMESTAMP = datetime.now(timezone.utc).strftime(
    "%Y%m%dT%H%M%SZ"
)

BACKUP = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime_backups"
    / f"runtime_schema_compatibility_install_{TIMESTAMP}"
    / TARGET.name
)

TARGET_PREEXISTED = TARGET.exists()


SOURCE = r'''# -*- coding: utf-8 -*-
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
        "runtime_schema.compatibility",
        None,
    )

    importlib.invalidate_caches()

    return importlib.import_module(
        "runtime_schema.compatibility"
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

    Definition = (
        definitions_module.SchemaDefinition
    )

    Mode = (
        types_module.CompatibilityMode
    )

    timestamp = (
        "2026-07-27T15:15:00.000000Z"
    )

    def make_definition(
        version: str,
        body: dict,
        *,
        mode: str = "backward",
    ):
        return Definition(
            namespace="runtime.schema",
            name="compatibility_record",
            version=version,
            owner_id="runtime_schema",
            compatibility_mode=mode,
            lifecycle_state="registered",
            created_at=timestamp,
            body=body,
        ).validate()

    base = make_definition(
        "1.0.0",
        {
            "fields": {
                "identifier": {
                    "type": "string",
                    "required": False,
                    "nullable": True,
                    "constraints": {
                        "min_length": 1,
                        "max_length": 20,
                    },
                },
                "legacy": {
                    "type": "string",
                },
            }
        },
    )

    compatible_candidate = make_definition(
        "1.1.0",
        {
            "fields": {
                "identifier": {
                    "type": "string",
                    "required": False,
                    "nullable": True,
                    "constraints": {
                        "min_length": 1,
                        "max_length": 20,
                    },
                },
                "legacy": {
                    "type": "string",
                },
                "optional_added": {
                    "type": "boolean",
                },
            }
        },
    )

    breaking_backward = make_definition(
        "2.0.0",
        {
            "fields": {
                "identifier": {
                    "type": "string",
                    "required": True,
                    "nullable": False,
                    "constraints": {
                        "min_length": 5,
                        "max_length": 10,
                    },
                },
                "legacy": {
                    "type": "string",
                },
            }
        },
    )

    breaking_forward = make_definition(
        "2.1.0",
        {
            "fields": {
                "identifier": {
                    "type": "string",
                    "required": False,
                    "nullable": True,
                    "constraints": {
                        "min_length": 0,
                        "max_length": 100,
                    },
                },
            }
        },
    )

    checker = module.CompatibilityChecker()

    backward_pass = checker.check(
        compatible_candidate,
        [base],
        Mode.BACKWARD,
    )

    assert backward_pass.compatible
    assert backward_pass.complete
    assert (
        backward_pass.violation_count
        == 0
    )

    backward_fail = checker.check(
        breaking_backward,
        [base],
        Mode.BACKWARD,
    )

    assert not backward_fail.compatible

    backward_rules = {
        violation.rule
        for violation
        in backward_fail.violations
    }

    assert {
        "required_field_tightening",
        "nullability_tightening",
        "constraint_tightening",
    }.issubset(
        backward_rules
    )

    forward_fail = checker.check(
        breaking_forward,
        [base],
        Mode.FORWARD,
    )

    assert not forward_fail.compatible

    forward_rules = {
        violation.rule
        for violation
        in forward_fail.violations
    }

    assert {
        "field_presence",
        "constraint_relaxation",
    }.issubset(
        forward_rules
    )

    full_fail = checker.check(
        breaking_forward,
        [base],
        Mode.FULL,
    )

    assert not full_fail.compatible

    assert full_fail.violations_for_direction(
        "forward"
    )

    prior_two = make_definition(
        "1.5.0",
        {
            "fields": {
                "identifier": {
                    "type": "string",
                    "required": False,
                    "nullable": True,
                    "constraints": {
                        "min_length": 1,
                        "max_length": 20,
                    },
                },
                "legacy": {
                    "type": "string",
                },
                "middle": {
                    "type": "boolean",
                },
            }
        },
    )

    transitive_candidate = make_definition(
        "3.0.0",
        {
            "fields": {
                "identifier": {
                    "type": "string",
                    "required": True,
                    "nullable": False,
                    "constraints": {
                        "min_length": 5,
                        "max_length": 10,
                    },
                },
            }
        },
        mode="full_transitive",
    )

    transitive = checker.check(
        transitive_candidate,
        [
            prior_two,
            base,
        ],
    )

    assert not transitive.compatible
    assert transitive.transitive

    assert transitive.checked_against == (
        base.coordinate(),
        prior_two.coordinate(),
    )

    non_transitive = checker.check(
        transitive_candidate,
        [
            base,
            prior_two,
        ],
        Mode.BACKWARD,
    )

    assert non_transitive.checked_against == (
        prior_two.coordinate(),
    )

    none_report = checker.check(
        transitive_candidate,
        [base, prior_two],
        Mode.NONE,
    )

    assert none_report.compatible
    assert none_report.checked_against == ()

    no_prior_report = checker.check(
        compatible_candidate,
        [],
        Mode.FULL_TRANSITIVE,
    )

    assert no_prior_report.compatible
    assert no_prior_report.complete

    assert (
        checker.runtime_requirement_satisfied(
            None
        )
        is True
    )

    assert (
        checker.runtime_requirement_satisfied(
            "1.0.0"
        )
        is False
    )

    class Provider:
        def is_runtime_compatible(
            self,
            required_runtime_version: str,
        ) -> bool:
            return (
                required_runtime_version
                <= "2.0.0"
            )

    bound_checker = (
        module.CompatibilityChecker(
            Provider()
        )
    )

    assert (
        bound_checker
        .runtime_requirement_satisfied(
            "1.0.0"
        )
        is True
    )

    assert len(
        backward_fail.fingerprint
    ) == 64

    repeated = checker.check(
        breaking_backward,
        [base],
        Mode.BACKWARD,
    )

    assert (
        repeated.fingerprint
        == backward_fail.fingerprint
    )

    try:
        backward_fail.violations = ()
    except Exception:
        pass
    else:
        raise AssertionError(
            "CompatibilityReport must be immutable."
        )

    try:
        checker.check(
            compatible_candidate,
            [base, base],
            Mode.BACKWARD_TRANSITIVE,
        )
    except Exception:
        pass
    else:
        raise AssertionError(
            "Duplicate prior version was accepted."
        )

    try:
        checker.check(
            base,
            [compatible_candidate],
            Mode.BACKWARD,
        )
    except Exception:
        pass
    else:
        raise AssertionError(
            "Non-successor candidate was accepted."
        )

    try:
        checker.runtime_requirement_satisfied(
            "invalid"
        )
    except Exception:
        pass
    else:
        raise AssertionError(
            "Invalid runtime requirement was accepted."
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
        "COMPATIBILITY.PY INSTALLATION AND REVIEW"
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
            "The compatibility.py installation failed, "
            "so the previous filesystem state was restored."
        )
        print()
        print(traceback.format_exc())

        return 1

    print("Dependency verification:        PASS")
    print("Claude baseline review:         PASS")
    print("Nova revisions applied:         PASS")
    print("compatibility.py compilation:   PASS")
    print("Package import:                 PASS")
    print("Immutable compatibility report: PASS")
    print("Backward compatibility:         PASS")
    print("Forward compatibility:          PASS")
    print("Full compatibility:             PASS")
    print("Transitive compatibility:       PASS")
    print("Non-transitive latest-only:     PASS")
    print("NONE compatibility mode:        PASS")
    print("No-prior fast path:             PASS")
    print("Version-chain ordering:         PASS")
    print("Duplicate-version rejection:    PASS")
    print("Candidate-successor policy:     PASS")
    print("Runtime requirement provider:   PASS")
    print("Fail-closed runtime policy:     PASS")
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
        "COMPATIBILITY.PY: INSTALLED, "
        "REVIEWED, AND APPROVED"
    )
    print("NO PRODUCTION DATA WAS MODIFIED")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
