# -*- coding: utf-8 -*-
"""Certification for 1.1.14 Runtime Schema Management.

This module runs a deterministic, fail-closed certification matrix over the
reviewed Runtime Schema Management package.

Every behavioral check uses fresh in-memory fixtures. The module performs no
filesystem, database, network, application-boot, or external persistence work.
It does not mutate production registry state.

Timestamp-independent evidence:

* ``implementation_fingerprint`` binds reviewed module public contracts;
* ``matrix_fingerprint`` binds the complete check matrix and outcomes;
* ``certification_id`` binds the contract and deterministic evidence.

Timestamp-dependent evidence:

* ``generated_at`` records the individual run;
* ``report_fingerprint`` binds the complete report, including generated time.
"""

from __future__ import annotations

import importlib
import inspect
import threading
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Mapping

from .audit import (
    GENESIS_HASH,
    AuditLog,
)
from .change_detection import (
    ChangeDetector,
)
from .compatibility import (
    CompatibilityChecker,
)
from .definitions import (
    SchemaDefinition,
)
from .deprecation import (
    DeprecationEngine,
    DeprecationPolicy,
    require_legal_transition,
)
from .diff_engine import (
    SchemaDiffEngine,
)
from .loader import (
    RuntimeSchemaLoader,
)
from .migration import (
    MigrationPlanner,
)
from .ports import (
    RuntimeSchemaCertificationPort,
)
from .registry import (
    RuntimeSchemaRegistry,
)
from .serialization import (
    canonical_json,
    parse_canonical_json,
    structure_fingerprint,
)
from .snapshots import (
    SnapshotCollection,
    build_empty_snapshot,
    build_snapshot,
    compare_snapshots,
)
from .transition_validation import (
    DowngradeValidator,
    UpgradeValidator,
)
from .types import (
    AuditAction,
    CompatibilityMode,
    EnforcementLevel,
    SchemaLifecycleState,
    SchemaRegistryError,
    UnknownFieldPolicy,
    deep_freeze,
    deep_thaw,
    utc_now_iso,
)
from .validation import (
    DocumentValidator,
)
from .versioning import (
    SchemaVersion,
)


CERTIFICATION_CONTRACT_VERSION = "1.0.0"

SUBSYSTEM = (
    "1.1.14 Runtime Schema Management"
)

CERTIFICATION_STRUCTURE_KIND = (
    "runtime.schema.certification"
)

FIXTURE_TIMESTAMP = (
    "2026-07-28T18:30:00.000000Z"
)

REVIEWED_MODULE_NAMES = (
    "types",
    "fingerprint",
    "serialization",
    "versioning",
    "definitions",
    "namespaces",
    "ownership",
    "validation",
    "diff_engine",
    "change_detection",
    "compatibility",
    "migration",
    "transition_validation",
    "deprecation",
    "audit",
    "snapshots",
    "ports",
    "registry",
    "loader",
)

EXPECTED_SECTIONS = (
    "FOUNDATION",
    "DEFINITIONS",
    "VALIDATION",
    "DIFF_AND_CHANGE",
    "COMPATIBILITY",
    "MIGRATION_AND_TRANSITIONS",
    "DEPRECATION",
    "AUDIT",
    "SNAPSHOTS",
    "PORTS",
    "REGISTRY",
    "LOADER",
    "PACKAGE_BOUNDARY",
)


class CertificationStatus(
    str,
    Enum,
):
    PASS = "pass"
    FAIL = "fail"


@dataclass(
    frozen=True,
    slots=True,
)
class CertificationCheck:
    """One immutable certification check result."""

    check_id: str
    section: str
    requirement: str
    status: CertificationStatus
    detail: str

    def __post_init__(
        self,
    ) -> None:
        for field_name in (
            "check_id",
            "section",
            "requirement",
            "detail",
        ):
            value = getattr(
                self,
                field_name,
            )

            if (
                not isinstance(
                    value,
                    str,
                )
                or not value
            ):
                raise SchemaRegistryError(
                    f"{field_name} must be a non-empty string"
                )

        if not isinstance(
            self.status,
            CertificationStatus,
        ):
            raise SchemaRegistryError(
                "status must be a CertificationStatus"
            )

    @property
    def passed(
        self,
    ) -> bool:
        return (
            self.status
            is CertificationStatus.PASS
        )

    def identity_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "check_id": self.check_id,
            "section": self.section,
            "requirement": self.requirement,
            "status": self.status.value,
        }

    def to_canonical_dict(
        self,
    ) -> dict[str, Any]:
        return {
            **self.identity_dict(),
            "detail": self.detail,
        }


@dataclass(
    frozen=True,
    slots=True,
)
class CertificationSection:
    """Immutable certification section."""

    name: str
    checks: tuple[
        CertificationCheck,
        ...
    ]
    passed_checks: int
    failed_checks: int
    status: CertificationStatus

    @classmethod
    def build(
        cls,
        name: str,
        checks: tuple[
            CertificationCheck,
            ...
        ],
    ) -> "CertificationSection":
        if not checks:
            return cls(
                name=name,
                checks=(),
                passed_checks=0,
                failed_checks=0,
                status=(
                    CertificationStatus.FAIL
                ),
            )

        passed = sum(
            1
            for check in checks
            if check.passed
        )

        failed = (
            len(checks)
            - passed
        )

        return cls(
            name=name,
            checks=checks,
            passed_checks=passed,
            failed_checks=failed,
            status=(
                CertificationStatus.PASS
                if failed == 0
                else CertificationStatus.FAIL
            ),
        )

    def to_canonical_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "name": self.name,
            "passed_checks": (
                self.passed_checks
            ),
            "failed_checks": (
                self.failed_checks
            ),
            "status": self.status.value,
            "checks": [
                check.to_canonical_dict()
                for check in self.checks
            ],
        }


@dataclass(
    frozen=True,
    slots=True,
)
class RuntimeSchemaCertificationReport:
    """Complete immutable certification report."""

    certification_id: str
    subsystem: str
    certification_contract_version: str
    implementation_fingerprint: str
    matrix_fingerprint: str
    certified: bool
    complete: bool
    status: CertificationStatus
    passed_checks: int
    failed_checks: int
    total_checks: int
    sections: tuple[
        CertificationSection,
        ...
    ]
    failure_codes: tuple[
        str,
        ...
    ]
    generated_at: str
    report_fingerprint: str

    def __post_init__(
        self,
    ) -> None:
        object.__setattr__(
            self,
            "sections",
            tuple(
                self.sections
            ),
        )

        object.__setattr__(
            self,
            "failure_codes",
            tuple(
                self.failure_codes
            ),
        )

        expected_total = sum(
            len(section.checks)
            for section in self.sections
        )

        expected_passed = sum(
            section.passed_checks
            for section in self.sections
        )

        expected_failed = sum(
            section.failed_checks
            for section in self.sections
        )

        if self.total_checks != expected_total:
            raise SchemaRegistryError(
                "total_checks is inconsistent"
            )

        if self.passed_checks != expected_passed:
            raise SchemaRegistryError(
                "passed_checks is inconsistent"
            )

        if self.failed_checks != expected_failed:
            raise SchemaRegistryError(
                "failed_checks is inconsistent"
            )

        expected_complete = (
            tuple(
                section.name
                for section in self.sections
            )
            == EXPECTED_SECTIONS
            and all(
                section.checks
                for section in self.sections
            )
        )

        if self.complete != expected_complete:
            raise SchemaRegistryError(
                "complete flag is inconsistent"
            )

        expected_certified = (
            self.complete
            and self.failed_checks == 0
            and not self.failure_codes
        )

        if self.certified != expected_certified:
            raise SchemaRegistryError(
                "certified flag is inconsistent"
            )

        expected_status = (
            CertificationStatus.PASS
            if expected_certified
            else CertificationStatus.FAIL
        )

        if self.status is not expected_status:
            raise SchemaRegistryError(
                "status is inconsistent"
            )

    def to_canonical_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "certification_id": (
                self.certification_id
            ),
            "subsystem": self.subsystem,
            "certification_contract_version": (
                self.certification_contract_version
            ),
            "implementation_fingerprint": (
                self.implementation_fingerprint
            ),
            "matrix_fingerprint": (
                self.matrix_fingerprint
            ),
            "certified": self.certified,
            "complete": self.complete,
            "status": self.status.value,
            "passed_checks": (
                self.passed_checks
            ),
            "failed_checks": (
                self.failed_checks
            ),
            "total_checks": (
                self.total_checks
            ),
            "sections": [
                section.to_canonical_dict()
                for section in self.sections
            ],
            "failure_codes": list(
                self.failure_codes
            ),
            "generated_at": (
                self.generated_at
            ),
            "report_fingerprint": (
                self.report_fingerprint
            ),
        }


def _immutable_mapping(
    value: Mapping[str, Any],
):
    return deep_freeze(
        deep_thaw(
            value
        )
    )


def _definition(
    *,
    namespace: str = "product.certification",
    name: str = "record",
    version: str = "1.0.0",
    owner_id: str = "certification_service",
    lifecycle_state: str = "active",
    compatibility_mode: str = "backward",
    fields: Mapping[str, Any] | None = None,
) -> SchemaDefinition:
    return (
        SchemaDefinition(
            namespace=namespace,
            name=name,
            version=version,
            owner_id=owner_id,
            lifecycle_state=(
                lifecycle_state
            ),
            compatibility_mode=(
                compatibility_mode
            ),
            created_at=(
                FIXTURE_TIMESTAMP
            ),
            body={
                "fields": dict(
                    fields
                    if fields is not None
                    else {
                        "identifier": {
                            "type": "string",
                            "required": True,
                        }
                    }
                )
            },
        )
        .validate()
    )


def _registry(
    *,
    namespace: str = "product.certification",
    owner_id: str = "certification_service",
) -> RuntimeSchemaRegistry:
    registry = (
        RuntimeSchemaRegistry()
    )

    registry.register_namespace(
        namespace,
        owner_id,
        owner_id,
    )

    return registry


class _FeatureFlags:
    __slots__ = (
        "_enabled",
    )

    def __init__(
        self,
        enabled: bool,
    ) -> None:
        self._enabled = enabled

    def is_enabled(
        self,
        flag_name: str,
    ) -> bool:
        return self._enabled


class RuntimeSchemaCertification(
    RuntimeSchemaCertificationPort
):
    """Thread-safe fail-closed certification runner."""

    __slots__ = (
        "_lock",
        "_last_report_text",
        "_last_report_fingerprint",
    )

    def __init__(
        self,
    ) -> None:
        self._lock = threading.RLock()
        self._last_report_text = None
        self._last_report_fingerprint = None

    def _implementation_fingerprint(
        self,
    ) -> str:
        modules = {}

        for module_name in (
            REVIEWED_MODULE_NAMES
        ):
            module = importlib.import_module(
                f"{__package__}.{module_name}"
            )

            modules[module_name] = {
                "public_api": sorted(
                    getattr(
                        module,
                        "__all__",
                        (),
                    )
                ),
                "module_name": (
                    module.__name__
                ),
            }

        return structure_fingerprint(
            {
                "kind": (
                    CERTIFICATION_STRUCTURE_KIND
                    + ".implementation"
                ),
                "contract_version": (
                    CERTIFICATION_CONTRACT_VERSION
                ),
                "modules": modules,
            }
        )

    @staticmethod
    def _run_check(
        section: str,
        check_id: str,
        requirement: str,
        operation: Callable[
            [],
            Any,
        ],
    ) -> CertificationCheck:
        try:
            detail = operation()

            return CertificationCheck(
                check_id=check_id,
                section=section,
                requirement=requirement,
                status=(
                    CertificationStatus.PASS
                ),
                detail=(
                    str(detail)
                    if detail
                    else "verified"
                ),
            )

        except Exception as exc:
            return CertificationCheck(
                check_id=check_id,
                section=section,
                requirement=requirement,
                status=(
                    CertificationStatus.FAIL
                ),
                detail=(
                    f"{type(exc).__name__}: {exc}"
                ),
            )

    @staticmethod
    def _expect(
        condition: bool,
        message: str,
    ) -> str:
        if not condition:
            raise AssertionError(
                message
            )

        return "verified"

    @staticmethod
    def _expect_raises(
        operation: Callable[
            [],
            Any,
        ],
    ) -> str:
        try:
            operation()
        except Exception:
            return "rejection verified"

        raise AssertionError(
            "operation unexpectedly succeeded"
        )

    def _foundation_checks(
        self,
    ) -> tuple[
        CertificationCheck,
        ...
    ]:
        section = "FOUNDATION"

        def imports():
            for name in (
                REVIEWED_MODULE_NAMES
            ):
                importlib.import_module(
                    f"{__package__}.{name}"
                )

            return (
                f"{len(REVIEWED_MODULE_NAMES)} "
                "reviewed modules import"
            )

        def canonical():
            first = canonical_json(
                {
                    "b": 2,
                    "a": 1,
                }
            )

            second = canonical_json(
                {
                    "a": 1,
                    "b": 2,
                }
            )

            self._expect(
                first == second,
                "canonical JSON is order-dependent",
            )

            self._expect(
                parse_canonical_json(
                    first
                )
                == {
                    "a": 1,
                    "b": 2,
                },
                "canonical JSON round trip failed",
            )

            return "canonical serialization"

        return (
            self._run_check(
                section,
                "foundation.imports",
                "all reviewed modules import",
                imports,
            ),
            self._run_check(
                section,
                "foundation.canonical",
                "canonical serialization is deterministic",
                canonical,
            ),
            self._run_check(
                section,
                "foundation.fingerprint",
                "structure fingerprints are deterministic",
                lambda: self._expect(
                    structure_fingerprint(
                        {
                            "value": 1
                        }
                    )
                    == structure_fingerprint(
                        {
                            "value": 1
                        }
                    ),
                    "fingerprints differ",
                ),
            ),
        )

    def _definition_checks(
        self,
    ) -> tuple[
        CertificationCheck,
        ...
    ]:
        section = "DEFINITIONS"

        def round_trip():
            original = _definition()

            rebuilt = (
                SchemaDefinition
                .from_canonical_dict(
                    original
                    .to_canonical_dict()
                )
            )

            self._expect(
                rebuilt.schema_id
                == original.schema_id,
                "schema ID changed",
            )

            self._expect(
                rebuilt
                .content_fingerprint()
                == original
                .content_fingerprint(),
                "content fingerprint changed",
            )

            self._expect(
                rebuilt
                .record_fingerprint()
                == original
                .record_fingerprint(),
                "record fingerprint changed",
            )

            return "definition round trip"

        return (
            self._run_check(
                section,
                "definitions.round_trip",
                "definitions reconstruct canonically",
                round_trip,
            ),
            self._run_check(
                section,
                "definitions.invalid",
                "invalid definitions are rejected",
                lambda: self._expect_raises(
                    lambda: (
                        SchemaDefinition
                        .from_canonical_dict(
                            {
                                "namespace": "broken"
                            }
                        )
                    )
                ),
            ),
        )

    def _validation_checks(
        self,
    ) -> tuple[
        CertificationCheck,
        ...
    ]:
        section = "VALIDATION"

        definition = _definition(
            fields={
                "identifier": {
                    "type": "string",
                    "required": True,
                },
                "count": {
                    "type": "integer",
                },
                "tags": {
                    "type": "array",
                    "item": {
                        "type": "string",
                    },
                },
            }
        )

        def valid_document():
            report = (
                DocumentValidator.validate(
                    {
                        "identifier": "abc",
                        "count": 2,
                        "tags": [
                            "one",
                            "two",
                        ],
                    },
                    definition,
                )
            )

            self._expect(
                report.valid,
                "valid document was rejected",
            )

            return "valid document accepted"

        def invalid_document():
            report = (
                DocumentValidator.validate(
                    {
                        "count": "wrong",
                    },
                    definition,
                )
            )

            self._expect(
                not report.valid,
                "invalid document was accepted",
            )

            return "invalid document rejected"

        def unknown_policy():
            document = {
                "identifier": "abc",
                "extra": True,
            }

            rejected = (
                DocumentValidator.validate(
                    document,
                    definition,
                    UnknownFieldPolicy.REJECT,
                )
            )

            ignored = (
                DocumentValidator.validate(
                    document,
                    definition,
                    UnknownFieldPolicy.IGNORE,
                )
            )

            self._expect(
                not rejected.valid,
                "REJECT policy accepted unknown field",
            )

            self._expect(
                ignored.valid,
                "IGNORE policy rejected unknown field",
            )

            return "unknown-field policy"

        return (
            self._run_check(
                section,
                "validation.valid",
                "valid documents are accepted",
                valid_document,
            ),
            self._run_check(
                section,
                "validation.invalid",
                "invalid documents are rejected",
                invalid_document,
            ),
            self._run_check(
                section,
                "validation.unknown_fields",
                "unknown-field policy is enforced",
                unknown_policy,
            ),
        )

    def _diff_checks(
        self,
    ) -> tuple[
        CertificationCheck,
        ...
    ]:
        section = "DIFF_AND_CHANGE"

        source = _definition(
            version="1.0.0",
            fields={
                "identifier": {
                    "type": "string",
                    "required": True,
                }
            },
        )

        target = _definition(
            version="1.1.0",
            fields={
                "identifier": {
                    "type": "string",
                    "required": True,
                },
                "optional_value": {
                    "type": "boolean",
                },
            },
        )

        def diff_check():
            first = (
                SchemaDiffEngine.diff(
                    source,
                    target,
                )
            )

            second = (
                SchemaDiffEngine.diff(
                    source,
                    target,
                )
            )

            self._expect(
                first
                .to_canonical_dict()
                == second
                .to_canonical_dict(),
                "diff is not deterministic",
            )

            self._expect(
                not first.identical,
                "addition was not detected",
            )

            return "structural diff"

        def change_check():
            first = (
                ChangeDetector.detect(
                    source,
                    target,
                )
            )

            second = (
                ChangeDetector.detect(
                    source,
                    target,
                )
            )

            self._expect(
                first.fingerprint
                == second.fingerprint,
                "change report is not deterministic",
            )

            self._expect(
                first.complete,
                "change report is incomplete",
            )

            return (
                first
                .overall_class
                .value
            )

        return (
            self._run_check(
                section,
                "diff.structural",
                "structural changes are detected",
                diff_check,
            ),
            self._run_check(
                section,
                "diff.classification",
                "changes are classified deterministically",
                change_check,
            ),
        )

    def _compatibility_checks(
        self,
    ) -> tuple[
        CertificationCheck,
        ...
    ]:
        section = "COMPATIBILITY"

        prior = _definition(
            version="1.0.0",
        )

        candidate = _definition(
            version="1.1.0",
            fields={
                "identifier": {
                    "type": "string",
                    "required": True,
                },
                "optional_value": {
                    "type": "boolean",
                },
            },
        )

        incompatible = _definition(
            version="2.0.0",
            fields={
                "identifier": {
                    "type": "integer",
                    "required": True,
                }
            },
        )

        checker = (
            CompatibilityChecker()
        )

        return (
            self._run_check(
                section,
                "compatibility.backward",
                "backward-compatible additions pass",
                lambda: self._expect(
                    checker.check(
                        candidate,
                        [prior],
                        CompatibilityMode.BACKWARD,
                    ).compatible,
                    "compatible candidate failed",
                ),
            ),
            self._run_check(
                section,
                "compatibility.breaking",
                "incompatible changes fail",
                lambda: self._expect(
                    not checker.check(
                        incompatible,
                        [prior],
                        CompatibilityMode.BACKWARD,
                    ).compatible,
                    "breaking candidate passed",
                ),
            ),
        )

    def _migration_checks(
        self,
    ) -> tuple[
        CertificationCheck,
        ...
    ]:
        section = (
            "MIGRATION_AND_TRANSITIONS"
        )

        source = _definition(
            version="1.0.0",
        )

        target = _definition(
            version="1.1.0",
            fields={
                "identifier": {
                    "type": "string",
                    "required": True,
                },
                "optional_value": {
                    "type": "boolean",
                },
            },
        )

        def planning():
            first = (
                MigrationPlanner.plan(
                    source,
                    target,
                )
            )

            second = (
                MigrationPlanner.plan(
                    source,
                    target,
                )
            )

            self._expect(
                first.fingerprint
                == second.fingerprint,
                "migration plan is not deterministic",
            )

            self._expect(
                not hasattr(
                    first,
                    "execute",
                ),
                "migration plan exposes execution",
            )

            return "deterministic planning only"

        def upgrade():
            plan = (
                MigrationPlanner.plan(
                    source,
                    target,
                )
            )

            report = (
                UpgradeValidator.validate(
                    plan,
                    source,
                    target,
                )
            )

            self._expect(
                report.valid,
                "valid upgrade was rejected",
            )

            return "upgrade validation"

        def drift():
            plan = (
                MigrationPlanner.plan(
                    source,
                    target,
                )
            )

            changed_target = _definition(
                version="1.2.0",
                fields={
                    "identifier": {
                        "type": "string",
                        "required": True,
                    },
                    "optional_value": {
                        "type": "boolean",
                    },
                    "other": {
                        "type": "string",
                    },
                },
            )

            report = (
                UpgradeValidator.validate(
                    plan,
                    source,
                    changed_target,
                )
            )

            self._expect(
                not report.valid,
                "plan drift was accepted",
            )

            return "plan drift detected"

        return (
            self._run_check(
                section,
                "migration.planning",
                "migration planning is deterministic",
                planning,
            ),
            self._run_check(
                section,
                "transitions.upgrade",
                "valid upgrades pass",
                upgrade,
            ),
            self._run_check(
                section,
                "transitions.drift",
                "plan drift is rejected",
                drift,
            ),
        )

    def _deprecation_checks(
        self,
    ) -> tuple[
        CertificationCheck,
        ...
    ]:
        section = "DEPRECATION"

        def lifecycle():
            require_legal_transition(
                SchemaLifecycleState.ACTIVE,
                SchemaLifecycleState.DEPRECATED,
            )

            return self._expect_raises(
                lambda: (
                    require_legal_transition(
                        SchemaLifecycleState.RETIRED,
                        SchemaLifecycleState.ACTIVE,
                    )
                )
            )

        def enforcement():
            policy = (
                DeprecationPolicy(
                    notice_period_days=0,
                    deprecated_at=(
                        FIXTURE_TIMESTAMP
                    ),
                    sunset_at=(
                        FIXTURE_TIMESTAMP
                    ),
                    enforcement=(
                        EnforcementLevel.BLOCK
                    ),
                )
            )

            disabled = (
                DeprecationEngine(
                    _FeatureFlags(
                        False
                    )
                )
            )

            enabled = (
                DeprecationEngine(
                    _FeatureFlags(
                        True
                    )
                )
            )

            self._expect(
                disabled
                .effective_enforcement(
                    policy
                )
                is EnforcementLevel.WARN,
                "disabled flag did not degrade enforcement",
            )

            self._expect(
                enabled
                .effective_enforcement(
                    policy
                )
                is EnforcementLevel.BLOCK,
                "enabled flag did not enforce blocking",
            )

            return "feature-flag staging"

        return (
            self._run_check(
                section,
                "deprecation.lifecycle",
                "lifecycle transitions are enforced",
                lifecycle,
            ),
            self._run_check(
                section,
                "deprecation.enforcement",
                "deprecation enforcement is staged",
                enforcement,
            ),
        )

    def _audit_checks(
        self,
    ) -> tuple[
        CertificationCheck,
        ...
    ]:
        section = "AUDIT"

        def chain():
            log = AuditLog()

            first = log.append(
                actor="certification_service",
                action=(
                    AuditAction
                    .SCHEMA_REGISTERED
                ),
                subject=(
                    "product.certification/"
                    "record@1.0.0"
                ),
                detail="first",
                timestamp=(
                    FIXTURE_TIMESTAMP
                ),
            )

            second = log.append(
                actor="certification_service",
                action=(
                    AuditAction
                    .LIFECYCLE_CHANGED
                ),
                subject=(
                    "product.certification/"
                    "record@1.0.0"
                ),
                detail="second",
                expected_head_hash=(
                    first.record_hash
                ),
                timestamp=(
                    "2026-07-28T18:30:01.000000Z"
                ),
            )

            self._expect(
                first.previous_hash
                == GENESIS_HASH,
                "first record does not bind genesis",
            )

            self._expect(
                second.previous_hash
                == first.record_hash,
                "second record is not chained",
            )

            self._expect(
                log.verify_chain().valid,
                "audit chain failed verification",
            )

            rebuilt = (
                AuditLog.from_records(
                    log.export_records()
                )
            )

            self._expect(
                rebuilt.head_hash
                == log.head_hash,
                "audit export/import changed chain",
            )

            return "append-only chain"

        return (
            self._run_check(
                section,
                "audit.chain",
                "audit records are hash chained",
                chain,
            ),
        )

    def _snapshot_checks(
        self,
    ) -> tuple[
        CertificationCheck,
        ...
    ]:
        section = "SNAPSHOTS"

        def empty():
            snapshot = (
                build_empty_snapshot(
                    created_at=(
                        FIXTURE_TIMESTAMP
                    )
                )
            )

            self._expect(
                snapshot
                .verify_integrity()
                .valid,
                "empty snapshot failed integrity",
            )

            return "empty snapshot"

        def comparison():
            first = build_snapshot(
                generation=1,
                registry_fingerprint=(
                    "1" * 64
                ),
                audit_head_fingerprint=(
                    GENESIS_HASH
                ),
                schema_count=1,
                namespace_count=1,
                schema_namespace_count=1,
                version_count=1,
                created_at=(
                    FIXTURE_TIMESTAMP
                ),
            )

            second = build_snapshot(
                generation=2,
                registry_fingerprint=(
                    "2" * 64
                ),
                audit_head_fingerprint=(
                    "3" * 64
                ),
                schema_count=1,
                namespace_count=1,
                schema_namespace_count=1,
                version_count=2,
                created_at=(
                    "2026-07-28T18:30:01.000000Z"
                ),
            )

            delta = (
                compare_snapshots(
                    first,
                    second,
                )
            )

            self._expect(
                delta.generation_delta == 1,
                "generation delta is incorrect",
            )

            collection = (
                SnapshotCollection(
                    snapshots=(
                        second,
                        first,
                    )
                )
            )

            self._expect(
                collection.generations()
                == (
                    1,
                    2,
                ),
                "collection ordering is incorrect",
            )

            self._expect(
                collection
                .verify_integrity()
                .valid,
                "collection integrity failed",
            )

            return "snapshot comparison and collection"

        return (
            self._run_check(
                section,
                "snapshots.empty",
                "generation-zero snapshots are valid",
                empty,
            ),
            self._run_check(
                section,
                "snapshots.collection",
                "snapshot collections are deterministic",
                comparison,
            ),
        )

    def _port_checks(
        self,
    ) -> tuple[
        CertificationCheck,
        ...
    ]:
        section = "PORTS"

        required = (
            "RuntimeSchemaRegistryPort",
            "RuntimeSchemaLoaderPort",
            "RuntimeSchemaSnapshotPort",
            "RuntimeSchemaValidationPort",
            "RuntimeSchemaMigrationPort",
            "RuntimeSchemaAuditPort",
            "RuntimeSchemaDiffPort",
            "RuntimeSchemaCompatibilityPort",
            "RuntimeSchemaCertificationPort",
        )

        def ports():
            module = importlib.import_module(
                f"{__package__}.ports"
            )

            for name in required:
                port = getattr(
                    module,
                    name,
                )

                self._expect(
                    inspect.isabstract(
                        port
                    ),
                    f"{name} is not abstract",
                )

                self._expect(
                    getattr(
                        port,
                        "__slots__",
                        None,
                    )
                    == (),
                    f"{name} does not use empty slots",
                )

                self._expect_raises(
                    port
                )

            return (
                f"{len(required)} ports verified"
            )

        return (
            self._run_check(
                section,
                "ports.contracts",
                "all approved ports remain abstract",
                ports,
            ),
        )

    def _registry_checks(
        self,
    ) -> tuple[
        CertificationCheck,
        ...
    ]:
        section = "REGISTRY"

        def registration():
            registry = _registry()

            first = _definition(
                version="1.0.0",
            )

            second = _definition(
                version="1.1.0",
                fields={
                    "identifier": {
                        "type": "string",
                        "required": True,
                    },
                    "optional_value": {
                        "type": "boolean",
                    },
                },
            )

            first_result = (
                registry.register_schema(
                    first
                    .to_canonical_dict(),
                    "certification_service",
                )
            )

            second_result = (
                registry.register_schema(
                    second
                    .to_canonical_dict(),
                    "certification_service",
                )
            )

            self._expect(
                first_result[
                    "first_version"
                ],
                "first registration not marked first",
            )

            self._expect(
                not second_result[
                    "first_version"
                ],
                "later registration marked first",
            )

            self._expect(
                len(
                    registry.list_versions(
                        "product.certification",
                        "record",
                    )
                )
                == 2,
                "version listing is incomplete",
            )

            self._expect(
                registry
                .verify_integrity()[
                    "valid"
                ],
                "registry integrity failed",
            )

            return "registration and integrity"

        def rollback():
            registry = _registry()

            definition = _definition()

            registry.register_schema(
                definition
                .to_canonical_dict(),
                "certification_service",
            )

            before = (
                registry
                .registry_measurements()
            )

            self._expect_raises(
                lambda: (
                    registry.register_schema(
                        definition
                        .to_canonical_dict(),
                        "certification_service",
                    )
                )
            )

            after = (
                registry
                .registry_measurements()
            )

            self._expect(
                before == after,
                "failed registration mutated registry",
            )

            return "transaction rollback"

        def lifecycle():
            registry = _registry()

            registry.register_schema(
                _definition()
                .to_canonical_dict(),
                "certification_service",
            )

            policy = {
                "notice_period_days": 0,
                "deprecated_at": (
                    FIXTURE_TIMESTAMP
                ),
                "sunset_at": (
                    FIXTURE_TIMESTAMP
                ),
                "enforcement": "warn",
                "reason": (
                    "Certification fixture."
                ),
            }

            result = (
                registry
                .transition_lifecycle(
                    "product.certification",
                    "record",
                    "1.0.0",
                    "deprecated",
                    "certification_service",
                    policy=policy,
                )
            )

            self._expect(
                result[
                    "new_state"
                ]
                == "deprecated",
                "lifecycle transition failed",
            )

            self._expect(
                registry.get_schema(
                    "product.certification",
                    "record",
                    "1.0.0",
                )
                is None,
                "inactive version remained active",
            )

            self._expect(
                registry.get_schema(
                    "product.certification",
                    "record",
                    "1.0.0",
                    include_inactive=True,
                )
                is not None,
                "inactive exact lookup failed",
            )

            return "lifecycle and lookup policy"

        return (
            self._run_check(
                section,
                "registry.registration",
                "schema registration and integrity pass",
                registration,
            ),
            self._run_check(
                section,
                "registry.rollback",
                "failed mutations roll back completely",
                rollback,
            ),
            self._run_check(
                section,
                "registry.lifecycle",
                "lifecycle and inactive lookups are enforced",
                lifecycle,
            ),
        )

    def _loader_checks(
        self,
    ) -> tuple[
        CertificationCheck,
        ...
    ]:
        section = "LOADER"

        def loading():
            registry = _registry()

            registry.register_schema(
                _definition(
                    version="1.0.0",
                ).to_canonical_dict(),
                "certification_service",
            )

            registry.register_schema(
                _definition(
                    version="1.1.0",
                    fields={
                        "identifier": {
                            "type": "string",
                            "required": True,
                        },
                        "optional_value": {
                            "type": "boolean",
                        },
                    },
                ).to_canonical_dict(),
                "certification_service",
            )

            loader = RuntimeSchemaLoader(
                registry
            )

            self._expect(
                loader.can_load(
                    "product.certification/record"
                ),
                "valid reference was rejected",
            )

            self._expect(
                not loader.can_load(
                    "broken-reference"
                ),
                "invalid reference was accepted",
            )

            latest = loader.load(
                "product.certification/record"
            )

            exact = loader.load(
                "product.certification/"
                "record@1.0.0"
            )

            self._expect(
                latest[
                    "version"
                ]
                == "1.1.0",
                "latest version resolution failed",
            )

            self._expect(
                exact[
                    "version"
                ]
                == "1.0.0",
                "exact version resolution failed",
            )

            batch = loader.load_all(
                [
                    "product.certification/"
                    "record@1.0.0",
                    "product.certification/record",
                    "product.certification/"
                    "record@1.0.0",
                ]
            )

            self._expect(
                len(batch) == 3,
                "batch order/position count changed",
            )

            return "reference validation and loading"

        return (
            self._run_check(
                section,
                "loader.loading",
                "registry-backed loading is deterministic",
                loading,
            ),
        )

    def _boundary_checks(
        self,
    ) -> tuple[
        CertificationCheck,
        ...
    ]:
        section = "PACKAGE_BOUNDARY"

        def boundary():
            forbidden = (
                "open",
                "Path",
                "socket",
                "requests",
                "sqlite3",
                "subprocess",
            )

            module = importlib.import_module(
                __name__
            )

            for name in forbidden:
                self._expect(
                    not hasattr(
                        module,
                        name,
                    ),
                    f"forbidden boundary symbol exposed: {name}",
                )

            self._expect(
                not hasattr(
                    module,
                    "main",
                ),
                "application entry point exposed",
            )

            return "no external I/O or boot boundary"

        return (
            self._run_check(
                section,
                "boundary.external_io",
                "certification has no external I/O or boot integration",
                boundary,
            ),
        )

    def _run_matrix(
        self,
    ) -> tuple[
        CertificationSection,
        ...
    ]:
        builders = (
            (
                "FOUNDATION",
                self._foundation_checks,
            ),
            (
                "DEFINITIONS",
                self._definition_checks,
            ),
            (
                "VALIDATION",
                self._validation_checks,
            ),
            (
                "DIFF_AND_CHANGE",
                self._diff_checks,
            ),
            (
                "COMPATIBILITY",
                self._compatibility_checks,
            ),
            (
                "MIGRATION_AND_TRANSITIONS",
                self._migration_checks,
            ),
            (
                "DEPRECATION",
                self._deprecation_checks,
            ),
            (
                "AUDIT",
                self._audit_checks,
            ),
            (
                "SNAPSHOTS",
                self._snapshot_checks,
            ),
            (
                "PORTS",
                self._port_checks,
            ),
            (
                "REGISTRY",
                self._registry_checks,
            ),
            (
                "LOADER",
                self._loader_checks,
            ),
            (
                "PACKAGE_BOUNDARY",
                self._boundary_checks,
            ),
        )

        sections = []

        for (
            section_name,
            builder,
        ) in builders:
            try:
                checks = tuple(
                    builder()
                )
            except Exception as exc:
                import traceback

                print("=" * 78)
                print(
                    "CERTIFICATION SECTION "
                    f"BUILDER FAILURE: {section_name}"
                )
                print("=" * 78)
                traceback.print_exc()
                print("=" * 78)

                checks = (
                    CertificationCheck(
                        check_id=(
                            section_name
                            .lower()
                            + ".builder"
                        ),
                        section=section_name,
                        requirement=(
                            "section builder must complete"
                        ),
                        status=(
                            CertificationStatus.FAIL
                        ),
                        detail=(
                            f"{type(exc).__name__}: {exc}"
                        ),
                    ),
                )

            sections.append(
                CertificationSection.build(
                    section_name,
                    checks,
                )
            )

        return tuple(
            sections
        )

    @staticmethod
    def _matrix_fingerprint(
        sections: tuple[
            CertificationSection,
            ...
        ],
    ) -> str:
        return structure_fingerprint(
            {
                "kind": (
                    CERTIFICATION_STRUCTURE_KIND
                    + ".matrix"
                ),
                "sections": [
                    {
                        "name": (
                            section.name
                        ),
                        "checks": [
                            check.identity_dict()
                            for check
                            in section.checks
                        ],
                    }
                    for section
                    in sections
                ],
            }
        )

    def _assemble_report(
        self,
        sections: tuple[
            CertificationSection,
            ...
        ],
    ) -> RuntimeSchemaCertificationReport:
        implementation_fingerprint = (
            self._implementation_fingerprint()
        )

        matrix_fingerprint = (
            self._matrix_fingerprint(
                sections
            )
        )

        total_checks = sum(
            len(section.checks)
            for section in sections
        )

        passed_checks = sum(
            section.passed_checks
            for section in sections
        )

        failed_checks = sum(
            section.failed_checks
            for section in sections
        )

        failure_codes = tuple(
            check.check_id
            for section in sections
            for check in section.checks
            if not check.passed
        )

        complete = (
            tuple(
                section.name
                for section in sections
            )
            == EXPECTED_SECTIONS
            and all(
                section.checks
                for section in sections
            )
        )

        certified = (
            complete
            and failed_checks == 0
            and not failure_codes
        )

        status = (
            CertificationStatus.PASS
            if certified
            else CertificationStatus.FAIL
        )

        certification_id = (
            "rsc-cert-"
            + structure_fingerprint(
                {
                    "contract": (
                        CERTIFICATION_CONTRACT_VERSION
                    ),
                    "implementation": (
                        implementation_fingerprint
                    ),
                    "matrix": (
                        matrix_fingerprint
                    ),
                }
            )[:24]
        )

        generated_at = utc_now_iso()

        report_core = {
            "certification_id": (
                certification_id
            ),
            "subsystem": SUBSYSTEM,
            "certification_contract_version": (
                CERTIFICATION_CONTRACT_VERSION
            ),
            "implementation_fingerprint": (
                implementation_fingerprint
            ),
            "matrix_fingerprint": (
                matrix_fingerprint
            ),
            "certified": certified,
            "complete": complete,
            "status": status.value,
            "passed_checks": (
                passed_checks
            ),
            "failed_checks": (
                failed_checks
            ),
            "total_checks": (
                total_checks
            ),
            "sections": [
                section.to_canonical_dict()
                for section in sections
            ],
            "failure_codes": list(
                failure_codes
            ),
            "generated_at": (
                generated_at
            ),
        }

        report_fingerprint = (
            structure_fingerprint(
                report_core
            )
        )

        return RuntimeSchemaCertificationReport(
            certification_id=(
                certification_id
            ),
            subsystem=SUBSYSTEM,
            certification_contract_version=(
                CERTIFICATION_CONTRACT_VERSION
            ),
            implementation_fingerprint=(
                implementation_fingerprint
            ),
            matrix_fingerprint=(
                matrix_fingerprint
            ),
            certified=certified,
            complete=complete,
            status=status,
            passed_checks=(
                passed_checks
            ),
            failed_checks=(
                failed_checks
            ),
            total_checks=(
                total_checks
            ),
            sections=sections,
            failure_codes=(
                failure_codes
            ),
            generated_at=(
                generated_at
            ),
            report_fingerprint=(
                report_fingerprint
            ),
        )

    def certify(
        self,
    ) -> Mapping[str, Any]:
        sections = self._run_matrix()

        report = self._assemble_report(
            sections
        )

        canonical_text = canonical_json(
            report.to_canonical_dict()
        )

        with self._lock:
            self._last_report_text = (
                canonical_text
            )

            self._last_report_fingerprint = (
                report.report_fingerprint
            )

        return _immutable_mapping(
            parse_canonical_json(
                canonical_text
            )
        )

    def last_report(
        self,
    ) -> Mapping[str, Any] | None:
        with self._lock:
            canonical_text = (
                self._last_report_text
            )

        if canonical_text is None:
            return None

        return _immutable_mapping(
            parse_canonical_json(
                canonical_text
            )
        )

    def certification_fingerprint(
        self,
    ) -> str | None:
        with self._lock:
            return (
                self
                ._last_report_fingerprint
            )


__all__ = [
    "CERTIFICATION_CONTRACT_VERSION",
    "CERTIFICATION_STRUCTURE_KIND",
    "EXPECTED_SECTIONS",
    "REVIEWED_MODULE_NAMES",
    "SUBSYSTEM",
    "CertificationCheck",
    "CertificationSection",
    "CertificationStatus",
    "RuntimeSchemaCertification",
    "RuntimeSchemaCertificationReport",
]
