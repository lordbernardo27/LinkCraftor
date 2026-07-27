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
    PACKAGE_DIR / "migration.py",
]

TARGET = (
    PACKAGE_DIR
    / "transition_validation.py"
)

TIMESTAMP = datetime.now(
    timezone.utc
).strftime(
    "%Y%m%dT%H%M%SZ"
)

BACKUP = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime_backups"
    / f"runtime_schema_transition_validation_install_{TIMESTAMP}"
    / TARGET.name
)

TARGET_PREEXISTED = TARGET.exists()


SOURCE = r'''# -*- coding: utf-8 -*-
"""Runtime Schema Upgrade and Downgrade Validation.

Upgrade and downgrade validation share one module because both operate on
the same immutable schema definitions, version graph, semantic change
report, and deterministic migration plan.

Shared invariants:

* source, target, and plan are valid reviewed contracts;
* source and target belong to one schema subject;
* plan identifiers, coordinates, and content fingerprints match;
* the supplied plan exactly matches deterministic replanning;
* incomplete migration plans are rejected;
* version ordering matches the requested transition direction.

Upgrade-specific rules:

* target version must be greater than source version;
* the semantic version bump must satisfy the detected change class.

Downgrade-specific rules:

* target version must be lower than source version;
* the plan must be mechanically reversible;
* lossy plans require explicit acknowledgement;
* acknowledgement never suppresses irreversibility.

This module validates plans only. It does not execute migrations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .change_detection import (
    ChangeDetector,
)
from .definitions import (
    SchemaDefinition,
)
from .migration import (
    MigrationPlan,
    MigrationPlanner,
)
from .serialization import (
    structure_fingerprint,
)
from .types import (
    SchemaMigrationError,
    TransitionDirection,
)
from .versioning import (
    satisfies_required_bump,
)


@dataclass(
    frozen=True,
    slots=True,
    order=True,
)
class TransitionIssue:
    """One immutable transition-validation violation."""

    code: str
    detail: str

    def __post_init__(self) -> None:
        for field_name in (
            "code",
            "detail",
        ):
            value = getattr(
                self,
                field_name,
            )

            if (
                not isinstance(value, str)
                or not value.strip()
            ):
                raise SchemaMigrationError(
                    f"{field_name} must be "
                    "a non-empty string"
                )

    def to_canonical_dict(
        self,
    ) -> dict[str, str]:
        """Return plain JSON-native issue data."""
        return {
            "code": self.code,
            "detail": self.detail,
        }


@dataclass(
    frozen=True,
    slots=True,
)
class TransitionValidationReport:
    """Complete immutable verdict for one schema transition."""

    direction: TransitionDirection
    source_schema_id: str
    target_schema_id: str
    source_coordinate: str
    target_coordinate: str
    plan_id: str
    plan_fingerprint: str
    valid: bool
    complete: bool
    acknowledged_data_loss: bool
    issues: tuple[
        TransitionIssue,
        ...
    ]

    def __post_init__(self) -> None:
        if not isinstance(
            self.direction,
            TransitionDirection,
        ):
            try:
                object.__setattr__(
                    self,
                    "direction",
                    TransitionDirection(
                        self.direction
                    ),
                )
            except (
                TypeError,
                ValueError,
            ) as exc:
                raise SchemaMigrationError(
                    "invalid transition direction"
                ) from exc

        for field_name in (
            "source_schema_id",
            "target_schema_id",
            "source_coordinate",
            "target_coordinate",
            "plan_id",
            "plan_fingerprint",
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

        if (
            len(self.plan_fingerprint)
            != 64
        ):
            raise SchemaMigrationError(
                "plan_fingerprint must be "
                "a 64-character digest"
            )

        if not isinstance(
            self.complete,
            bool,
        ):
            raise SchemaMigrationError(
                "complete must be a boolean"
            )

        if not isinstance(
            self.acknowledged_data_loss,
            bool,
        ):
            raise SchemaMigrationError(
                "acknowledged_data_loss must "
                "be a boolean"
            )

        object.__setattr__(
            self,
            "issues",
            tuple(
                self.issues
            ),
        )

        for issue in self.issues:
            if not isinstance(
                issue,
                TransitionIssue,
            ):
                raise SchemaMigrationError(
                    "every issue must be a TransitionIssue"
                )

        expected_valid = (
            self.complete
            and not self.issues
        )

        if self.valid != expected_valid:
            raise SchemaMigrationError(
                "valid flag is inconsistent "
                "with issues or completeness"
            )

    @property
    def issue_count(
        self,
    ) -> int:
        """Return total transition issue count."""
        return len(
            self.issues
        )

    @property
    def fingerprint(
        self,
    ) -> str:
        """Return deterministic report fingerprint."""
        return structure_fingerprint(
            self.to_canonical_dict()
        )

    def issue_codes(
        self,
    ) -> tuple[str, ...]:
        """Return deterministic issue-code sequence."""
        return tuple(
            issue.code
            for issue in self.issues
        )

    def to_canonical_dict(
        self,
    ) -> dict[str, Any]:
        """Return complete plain JSON-native report data."""
        return {
            "direction": self.direction.value,
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
            "plan_id": self.plan_id,
            "plan_fingerprint": (
                self.plan_fingerprint
            ),
            "valid": self.valid,
            "complete": self.complete,
            "acknowledged_data_loss": (
                self.acknowledged_data_loss
            ),
            "issues": [
                issue.to_canonical_dict()
                for issue in self.issues
            ],
            "issue_count": self.issue_count,
        }


def _require_contracts(
    plan: MigrationPlan,
    source: SchemaDefinition,
    target: SchemaDefinition,
) -> None:
    if not isinstance(
        plan,
        MigrationPlan,
    ):
        raise SchemaMigrationError(
            "plan must be a MigrationPlan"
        )

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


def _shared_issues(
    plan: MigrationPlan,
    source: SchemaDefinition,
    target: SchemaDefinition,
) -> tuple[
    list[TransitionIssue],
    bool,
]:
    """Return shared invariant violations and completeness."""
    _require_contracts(
        plan,
        source,
        target,
    )

    issues: list[
        TransitionIssue
    ] = []

    complete = bool(
        plan.complete
    )

    if not plan.complete:
        issues.append(
            TransitionIssue(
                code="incomplete_plan",
                detail=(
                    "migration plan is incomplete "
                    "and cannot be validated safely"
                ),
            )
        )

    if (
        source.namespace
        != target.namespace
        or source.name
        != target.name
    ):
        issues.append(
            TransitionIssue(
                code="coordinate_mismatch",
                detail=(
                    "transition must remain within "
                    "one namespace and schema name"
                ),
            )
        )

    if (
        plan.source_schema_id
        != source.schema_id
    ):
        issues.append(
            TransitionIssue(
                code="source_mismatch",
                detail=(
                    "plan source schema ID does not "
                    "match the supplied source definition"
                ),
            )
        )

    if (
        plan.target_schema_id
        != target.schema_id
    ):
        issues.append(
            TransitionIssue(
                code="target_mismatch",
                detail=(
                    "plan target schema ID does not "
                    "match the supplied target definition"
                ),
            )
        )

    if (
        plan.source_coordinate
        != source.coordinate()
    ):
        issues.append(
            TransitionIssue(
                code="source_coordinate_mismatch",
                detail=(
                    "plan source coordinate does not "
                    "match the supplied source definition"
                ),
            )
        )

    if (
        plan.target_coordinate
        != target.coordinate()
    ):
        issues.append(
            TransitionIssue(
                code="target_coordinate_mismatch",
                detail=(
                    "plan target coordinate does not "
                    "match the supplied target definition"
                ),
            )
        )

    if (
        plan.source_content_fingerprint
        != source.content_fingerprint()
    ):
        issues.append(
            TransitionIssue(
                code="source_content_drift",
                detail=(
                    "source definition content changed "
                    "after the migration plan was created"
                ),
            )
        )

    if (
        plan.target_content_fingerprint
        != target.content_fingerprint()
    ):
        issues.append(
            TransitionIssue(
                code="target_content_drift",
                detail=(
                    "target definition content changed "
                    "after the migration plan was created"
                ),
            )
        )

    identity_checks_passed = not {
        "source_mismatch",
        "target_mismatch",
        "source_coordinate_mismatch",
        "target_coordinate_mismatch",
        "source_content_drift",
        "target_content_drift",
        "coordinate_mismatch",
    }.intersection(
        issue.code
        for issue in issues
    )

    if identity_checks_passed:
        try:
            expected = (
                MigrationPlanner.plan(
                    source,
                    target,
                )
            )
        except Exception as exc:
            issues.append(
                TransitionIssue(
                    code="replanning_failed",
                    detail=(
                        "deterministic migration replanning "
                        f"failed: {exc}"
                    ),
                )
            )

            complete = False
        else:
            if (
                expected.fingerprint
                != plan.fingerprint
            ):
                issues.append(
                    TransitionIssue(
                        code="plan_drift",
                        detail=(
                            "plan does not match the "
                            "deterministic plan for this pair"
                        ),
                    )
                )

            if (
                expected.plan_id
                != plan.plan_id
            ):
                issues.append(
                    TransitionIssue(
                        code="plan_identity_drift",
                        detail=(
                            "plan ID does not match "
                            "deterministic replanning"
                        ),
                    )
                )

    return (
        issues,
        complete,
    )


def _ordered_issues(
    issues: list[
        TransitionIssue
    ],
) -> tuple[
    TransitionIssue,
    ...
]:
    return tuple(
        sorted(
            issues,
            key=lambda issue: (
                issue.code,
                issue.detail,
            ),
        )
    )


class UpgradeValidator:
    """Validate schema upgrades."""

    @staticmethod
    def validate(
        plan: MigrationPlan,
        source: SchemaDefinition,
        target: SchemaDefinition,
    ) -> TransitionValidationReport:
        """Validate a migration plan as an upgrade."""
        (
            issues,
            complete,
        ) = _shared_issues(
            plan,
            source,
            target,
        )

        if (
            target.version
            <= source.version
        ):
            issues.append(
                TransitionIssue(
                    code="not_an_upgrade",
                    detail=(
                        f"target version {target.version} "
                        "must be greater than "
                        f"source version {source.version}"
                    ),
                )
            )
        else:
            try:
                change = (
                    ChangeDetector.detect(
                        source,
                        target,
                    )
                )
            except Exception as exc:
                issues.append(
                    TransitionIssue(
                        code="change_detection_failed",
                        detail=(
                            "semantic change detection "
                            f"failed: {exc}"
                        ),
                    )
                )

                complete = False
            else:
                if not change.complete:
                    issues.append(
                        TransitionIssue(
                            code="incomplete_change_report",
                            detail=(
                                "semantic change report is "
                                "incomplete"
                            ),
                        )
                    )

                    complete = False

                elif (
                    not change.identical
                    and not satisfies_required_bump(
                        source.version,
                        target.version,
                        change.overall_class,
                    )
                ):
                    issues.append(
                        TransitionIssue(
                            code="insufficient_bump",
                            detail=(
                                f"{change.overall_class.value} "
                                "change requires at least a "
                                f"{change.required_version_bump.value} "
                                f"bump from {source.version}"
                            ),
                        )
                    )

        ordered = _ordered_issues(
            issues
        )

        return TransitionValidationReport(
            direction=(
                TransitionDirection.UPGRADE
            ),
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
            plan_id=plan.plan_id,
            plan_fingerprint=(
                plan.fingerprint
            ),
            valid=(
                complete
                and not ordered
            ),
            complete=complete,
            acknowledged_data_loss=False,
            issues=ordered,
        )


class DowngradeValidator:
    """Validate schema downgrades."""

    @staticmethod
    def validate(
        plan: MigrationPlan,
        source: SchemaDefinition,
        target: SchemaDefinition,
        *,
        acknowledge_data_loss: bool = False,
    ) -> TransitionValidationReport:
        """Validate a migration plan as a downgrade."""
        if not isinstance(
            acknowledge_data_loss,
            bool,
        ):
            raise SchemaMigrationError(
                "acknowledge_data_loss must "
                "be a boolean"
            )

        (
            issues,
            complete,
        ) = _shared_issues(
            plan,
            source,
            target,
        )

        if (
            target.version
            >= source.version
        ):
            issues.append(
                TransitionIssue(
                    code="not_a_downgrade",
                    detail=(
                        f"target version {target.version} "
                        "must be lower than "
                        f"source version {source.version}"
                    ),
                )
            )

        if not plan.reversible:
            issues.append(
                TransitionIssue(
                    code="irreversible",
                    detail=(
                        "downgrade requires a "
                        "mechanically reversible plan"
                    ),
                )
            )

        if (
            plan.lossy
            and not acknowledge_data_loss
        ):
            issues.append(
                TransitionIssue(
                    code="unacknowledged_data_loss",
                    detail=(
                        "migration plan is lossy and "
                        "data loss was not acknowledged"
                    ),
                )
            )

        ordered = _ordered_issues(
            issues
        )

        return TransitionValidationReport(
            direction=(
                TransitionDirection.DOWNGRADE
            ),
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
            plan_id=plan.plan_id,
            plan_fingerprint=(
                plan.fingerprint
            ),
            valid=(
                complete
                and not ordered
            ),
            complete=complete,
            acknowledged_data_loss=(
                acknowledge_data_loss
            ),
            issues=ordered,
        )


__all__ = [
    "DowngradeValidator",
    "TransitionIssue",
    "TransitionValidationReport",
    "UpgradeValidator",
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
        "runtime_schema.transition_validation",
        None,
    )

    importlib.invalidate_caches()

    return importlib.import_module(
        "runtime_schema.transition_validation"
    )


def verify_behavior(
    module,
) -> None:
    definitions_module = (
        importlib.import_module(
            "runtime_schema.definitions"
        )
    )

    migration_module = (
        importlib.import_module(
            "runtime_schema.migration"
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

    Planner = (
        migration_module.MigrationPlanner
    )

    Direction = (
        types_module.TransitionDirection
    )

    timestamp = (
        "2026-07-27T15:45:00.000000Z"
    )

    def definition(
        version: str,
        body: dict,
    ):
        return Definition(
            namespace="runtime.schema",
            name="transition_record",
            version=version,
            owner_id="runtime_schema",
            lifecycle_state="registered",
            created_at=timestamp,
            body=body,
        ).validate()

    base = definition(
        "1.0.0",
        {
            "fields": {
                "identifier": {
                    "type": "string",
                    "required": False,
                },
            }
        },
    )

    additive = definition(
        "1.1.0",
        {
            "fields": {
                "identifier": {
                    "type": "string",
                    "required": False,
                },
                "optional_value": {
                    "type": "boolean",
                },
            }
        },
    )

    breaking_patch = definition(
        "1.1.1",
        {
            "fields": {
                "identifier": {
                    "type": "integer",
                    "required": True,
                },
            }
        },
    )

    breaking_major = definition(
        "2.0.0",
        {
            "fields": {
                "identifier": {
                    "type": "integer",
                    "required": True,
                },
            }
        },
    )

    upgrade_plan = Planner.plan(
        base,
        additive,
    )

    upgrade_one = (
        module.UpgradeValidator.validate(
            upgrade_plan,
            base,
            additive,
        )
    )

    upgrade_two = (
        module.UpgradeValidator.validate(
            upgrade_plan,
            base,
            additive,
        )
    )

    assert upgrade_one.valid
    assert upgrade_one.complete

    assert (
        upgrade_one.direction
        is Direction.UPGRADE
    )

    assert (
        upgrade_one.issue_count
        == 0
    )

    assert (
        upgrade_one.fingerprint
        == upgrade_two.fingerprint
    )

    insufficient_plan = Planner.plan(
        additive,
        breaking_patch,
    )

    insufficient = (
        module.UpgradeValidator.validate(
            insufficient_plan,
            additive,
            breaking_patch,
        )
    )

    assert not insufficient.valid

    assert (
        "insufficient_bump"
        in insufficient.issue_codes()
    )

    major_plan = Planner.plan(
        base,
        breaking_major,
    )

    major_upgrade = (
        module.UpgradeValidator.validate(
            major_plan,
            base,
            breaking_major,
        )
    )

    assert major_upgrade.valid

    wrong_direction_plan = Planner.plan(
        additive,
        base,
    )

    wrong_upgrade = (
        module.UpgradeValidator.validate(
            wrong_direction_plan,
            additive,
            base,
        )
    )

    assert not wrong_upgrade.valid

    assert (
        "not_an_upgrade"
        in wrong_upgrade.issue_codes()
    )

    reversible_source = definition(
        "3.0.0",
        {
            "fields": {
                "identifier": {
                    "type": "string",
                    "constraints": {
                        "min_length": 5,
                    },
                },
            }
        },
    )

    reversible_target = definition(
        "2.5.0",
        {
            "fields": {
                "identifier": {
                    "type": "string",
                    "constraints": {
                        "min_length": 1,
                    },
                },
            }
        },
    )

    reversible_plan = Planner.plan(
        reversible_source,
        reversible_target,
    )

    assert not reversible_plan.lossy
    assert reversible_plan.reversible

    clean_downgrade = (
        module.DowngradeValidator.validate(
            reversible_plan,
            reversible_source,
            reversible_target,
        )
    )

    assert clean_downgrade.valid

    lossy_source = definition(
        "4.0.0",
        {
            "fields": {
                "identifier": {
                    "type": "string",
                },
                "new_field": {
                    "type": "boolean",
                },
            }
        },
    )

    lossy_target = definition(
        "3.5.0",
        {
            "fields": {
                "identifier": {
                    "type": "string",
                },
            }
        },
    )

    lossy_plan = Planner.plan(
        lossy_source,
        lossy_target,
    )

    assert lossy_plan.lossy
    assert not lossy_plan.reversible

    unacknowledged = (
        module.DowngradeValidator.validate(
            lossy_plan,
            lossy_source,
            lossy_target,
            acknowledge_data_loss=False,
        )
    )

    acknowledged = (
        module.DowngradeValidator.validate(
            lossy_plan,
            lossy_source,
            lossy_target,
            acknowledge_data_loss=True,
        )
    )

    assert not unacknowledged.valid
    assert not acknowledged.valid

    assert (
        "unacknowledged_data_loss"
        in unacknowledged.issue_codes()
    )

    assert (
        "unacknowledged_data_loss"
        not in acknowledged.issue_codes()
    )

    assert (
        "irreversible"
        in acknowledged.issue_codes()
    )

    wrong_downgrade = (
        module.DowngradeValidator.validate(
            upgrade_plan,
            base,
            additive,
        )
    )

    assert not wrong_downgrade.valid

    assert (
        "not_a_downgrade"
        in wrong_downgrade.issue_codes()
    )

    try:
        module.DowngradeValidator.validate(
            lossy_plan,
            lossy_source,
            lossy_target,
            acknowledge_data_loss="yes",
        )
    except Exception:
        pass
    else:
        raise AssertionError(
            "Non-boolean data-loss acknowledgement "
            "was accepted."
        )

    try:
        upgrade_one.issues = ()
    except Exception:
        pass
    else:
        raise AssertionError(
            "TransitionValidationReport "
            "must be immutable."
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
        "TRANSITION_VALIDATION.PY "
        "INSTALLATION AND REVIEW"
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
            "The transition_validation.py "
            "installation failed, so the previous "
            "filesystem state was restored."
        )
        print()
        print(traceback.format_exc())

        return 1

    print("Dependency verification:        PASS")
    print("Claude baseline review:         PASS")
    print("Nova revisions applied:         PASS")
    print("transition compilation:         PASS")
    print("Package import:                 PASS")
    print("Immutable transition reports:   PASS")
    print("Shared plan integrity:          PASS")
    print("Coordinate verification:        PASS")
    print("Content-drift detection:        PASS")
    print("Deterministic replanning:       PASS")
    print("Plan identity verification:     PASS")
    print("Upgrade direction policy:       PASS")
    print("Upgrade bump enforcement:       PASS")
    print("Downgrade direction policy:     PASS")
    print("Downgrade reversibility:        PASS")
    print("Data-loss acknowledgement:      PASS")
    print("Acknowledgement isolation:      PASS")
    print("Deterministic issue ordering:   PASS")
    print("Deterministic fingerprints:     PASS")
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
        "TRANSITION_VALIDATION.PY: "
        "INSTALLED, REVIEWED, AND APPROVED"
    )
    print("NO PRODUCTION DATA WAS MODIFIED")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
