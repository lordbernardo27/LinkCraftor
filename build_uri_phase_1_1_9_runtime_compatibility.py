from __future__ import annotations

import ast
import hashlib
import importlib
import json
import os
import py_compile
import shutil
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BUILD_VERSION = "uri_phase_1_1_9_runtime_compatibility_v1"

PROJECT_ROOT = Path.cwd().resolve()

TARGET = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "runtime"
    / "runtime_compatibility.py"
)

KERNEL_FILE = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_runtime_kernel.py"
)

CONFIGURATION_FILE = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "runtime"
    / "runtime_configuration.py"
)

ENVIRONMENT_FILE = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "runtime"
    / "runtime_environment.py"
)

SERVICE_REGISTRY_FILE = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "runtime"
    / "runtime_service_registry.py"
)

LIFECYCLE_FILE = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "runtime"
    / "runtime_lifecycle_manager.py"
)

BOOT_FILE = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "runtime"
    / "runtime_boot_process.py"
)

SHUTDOWN_FILE = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "runtime"
    / "runtime_shutdown_process.py"
)

VERSIONING_FILE = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "runtime"
    / "runtime_versioning.py"
)

EXISTING_RUNTIME_FACADE = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_runtime_infrastructure.py"
)

MAIN_FILE = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "main.py"
)

TIMESTAMP = datetime.now(timezone.utc).strftime(
    "%Y%m%dT%H%M%SZ"
)

BACKUP_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime_backups"
    / f"uri_phase1_1_9_runtime_compatibility_{TIMESTAMP}"
)

BACKUP_TARGET = (
    BACKUP_ROOT
    / "backend"
    / "server"
    / "runtime"
    / "runtime_compatibility.py"
)

EVIDENCE_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime"
    / "uri_phase_1"
    / "1_1_9_runtime_compatibility"
)

EVIDENCE_JSON = (
    EVIDENCE_ROOT
    / f"runtime_compatibility_build_{TIMESTAMP}.json"
)

EVIDENCE_TEXT = (
    EVIDENCE_ROOT
    / f"runtime_compatibility_build_{TIMESTAMP}.txt"
)


COMPATIBILITY_SOURCE = r'''from __future__ import annotations

"""
Universal Runtime Compatibility Layer.

This module evaluates Universal Runtime version manifests against
explicit compatibility policies.

It does not assign versions, load configuration, boot the runtime,
execute jobs, migrate state, or contain product business logic.
"""

import hashlib
import json
import re
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from backend.server.runtime.runtime_versioning import (
    RuntimeSemanticVersion,
    RuntimeVersionManifest,
)


__all__ = [
    "DEFAULT_COMPATIBILITY_POLICY_VERSION",
    "RuntimeCompatibilityError",
    "RuntimeCompatibilityIncompatibleError",
    "RuntimeCompatibilityLayer",
    "RuntimeCompatibilityMode",
    "RuntimeCompatibilityPolicy",
    "RuntimeCompatibilityReport",
    "RuntimeCompatibilityResult",
    "RuntimeCompatibilitySnapshot",
    "RuntimeCompatibilityValidationError",
    "RuntimeVersionRequirement",
    "create_default_runtime_compatibility_layer",
]


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


DEFAULT_COMPATIBILITY_POLICY_VERSION = "0.1.0"


_CONTRACT_KEY_PATTERN = re.compile(
    r"^[a-z][a-z0-9_.:-]{1,127}$"
)

_POLICY_NAME_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9_.:-]{2,127}$"
)


class RuntimeCompatibilityError(RuntimeError):
    """Base runtime-compatibility failure."""


class RuntimeCompatibilityValidationError(
    RuntimeCompatibilityError
):
    """Raised when a compatibility policy is invalid."""


class RuntimeCompatibilityIncompatibleError(
    RuntimeCompatibilityError
):
    """Raised when strict compatibility enforcement fails."""

    def __init__(
        self,
        report: "RuntimeCompatibilityReport",
    ) -> None:
        self.report = report

        super().__init__(
            "Runtime compatibility validation failed for: "
            + ", ".join(report.failed_contracts)
        )


class RuntimeCompatibilityMode(str, Enum):
    EXACT = "exact"
    SAME_MAJOR = "same_major"
    SAME_MINOR = "same_minor"
    AT_LEAST = "at_least"
    RANGE = "range"


@dataclass(frozen=True, slots=True)
class RuntimeCompatibilityResult:
    """Immutable compatibility result for one version contract."""

    contract: str
    mode: RuntimeCompatibilityMode
    expected_version: RuntimeSemanticVersion
    actual_version: RuntimeSemanticVersion
    maximum_exclusive: RuntimeSemanticVersion | None
    allow_prerelease: bool
    required: bool
    compatible: bool
    reason: str


@dataclass(frozen=True, slots=True)
class RuntimeVersionRequirement:
    """One explicit version-compatibility requirement."""

    contract: str
    mode: RuntimeCompatibilityMode
    expected_version: RuntimeSemanticVersion
    maximum_exclusive: RuntimeSemanticVersion | None = None
    allow_prerelease: bool = False
    required: bool = True
    description: str | None = None

    def __post_init__(self) -> None:
        normalized_contract = str(
            self.contract or ""
        ).strip().lower()

        if not _CONTRACT_KEY_PATTERN.fullmatch(
            normalized_contract
        ):
            raise RuntimeCompatibilityValidationError(
                "contract must be 2-128 characters, begin "
                "with a lowercase letter, and contain only "
                "lowercase letters, numbers, dots, "
                "underscores, colons, or hyphens."
            )

        if isinstance(
            self.mode,
            RuntimeCompatibilityMode,
        ):
            resolved_mode = self.mode
        else:
            try:
                resolved_mode = RuntimeCompatibilityMode(
                    str(self.mode or "").strip().lower()
                )
            except ValueError as exc:
                raise RuntimeCompatibilityValidationError(
                    f"Unknown compatibility mode: "
                    f"{self.mode!r}"
                ) from exc

        resolved_expected = (
            RuntimeSemanticVersion.parse(
                self.expected_version
            )
        )

        resolved_maximum = (
            None
            if self.maximum_exclusive is None
            else RuntimeSemanticVersion.parse(
                self.maximum_exclusive
            )
        )

        if (
            resolved_mode
            is RuntimeCompatibilityMode.RANGE
            and resolved_maximum is None
        ):
            raise RuntimeCompatibilityValidationError(
                "RANGE compatibility requires "
                "maximum_exclusive."
            )

        if (
            resolved_mode
            is not RuntimeCompatibilityMode.RANGE
            and resolved_maximum is not None
        ):
            raise RuntimeCompatibilityValidationError(
                "maximum_exclusive is valid only for "
                "RANGE compatibility."
            )

        if (
            resolved_maximum is not None
            and resolved_expected.compare_precedence(
                resolved_maximum
            )
            >= 0
        ):
            raise RuntimeCompatibilityValidationError(
                "maximum_exclusive must have higher "
                "precedence than expected_version."
            )

        normalized_description = (
            None
            if self.description is None
            else str(self.description).strip()
        )

        object.__setattr__(
            self,
            "contract",
            normalized_contract,
        )

        object.__setattr__(
            self,
            "mode",
            resolved_mode,
        )

        object.__setattr__(
            self,
            "expected_version",
            resolved_expected,
        )

        object.__setattr__(
            self,
            "maximum_exclusive",
            resolved_maximum,
        )

        object.__setattr__(
            self,
            "allow_prerelease",
            bool(self.allow_prerelease),
        )

        object.__setattr__(
            self,
            "required",
            bool(self.required),
        )

        object.__setattr__(
            self,
            "description",
            normalized_description,
        )

    def evaluate(
        self,
        actual_version: RuntimeSemanticVersion | str,
    ) -> RuntimeCompatibilityResult:
        actual = RuntimeSemanticVersion.parse(
            actual_version
        )

        expected = self.expected_version
        compatible = False
        reason: str

        if (
            actual.prerelease
            and not self.allow_prerelease
            and not expected.prerelease
        ):
            compatible = False
            reason = (
                "Prerelease versions are not permitted "
                "by this compatibility requirement."
            )

        elif self.mode is RuntimeCompatibilityMode.EXACT:
            compatible = actual.same_precedence(
                expected
            )

            reason = (
                "Version precedence matches exactly."
                if compatible
                else (
                    f"Expected exact precedence "
                    f"{expected}; found {actual}."
                )
            )

        elif (
            self.mode
            is RuntimeCompatibilityMode.SAME_MAJOR
        ):
            compatible = (
                actual.major == expected.major
                and actual.compare_precedence(
                    expected
                )
                >= 0
            )

            reason = (
                "Version uses the required major line "
                "and satisfies the minimum baseline."
                if compatible
                else (
                    f"Expected major {expected.major} "
                    f"at or above {expected}; "
                    f"found {actual}."
                )
            )

        elif (
            self.mode
            is RuntimeCompatibilityMode.SAME_MINOR
        ):
            compatible = (
                actual.major == expected.major
                and actual.minor == expected.minor
                and actual.compare_precedence(
                    expected
                )
                >= 0
            )

            reason = (
                "Version uses the required major/minor "
                "line and satisfies the minimum baseline."
                if compatible
                else (
                    f"Expected {expected.major}."
                    f"{expected.minor}.x at or above "
                    f"{expected}; found {actual}."
                )
            )

        elif (
            self.mode
            is RuntimeCompatibilityMode.AT_LEAST
        ):
            compatible = (
                actual.compare_precedence(
                    expected
                )
                >= 0
            )

            reason = (
                "Version satisfies the minimum baseline."
                if compatible
                else (
                    f"Expected at least {expected}; "
                    f"found {actual}."
                )
            )

        elif self.mode is RuntimeCompatibilityMode.RANGE:
            maximum = self.maximum_exclusive

            if maximum is None:
                raise RuntimeCompatibilityValidationError(
                    "RANGE requirement has no "
                    "maximum_exclusive value."
                )

            compatible = (
                actual.compare_precedence(
                    expected
                )
                >= 0
                and actual.compare_precedence(
                    maximum
                )
                < 0
            )

            reason = (
                "Version is inside the permitted range."
                if compatible
                else (
                    f"Expected {expected} <= version "
                    f"< {maximum}; found {actual}."
                )
            )

        else:
            raise RuntimeCompatibilityValidationError(
                f"Unsupported compatibility mode: "
                f"{self.mode!r}"
            )

        return RuntimeCompatibilityResult(
            contract=self.contract,
            mode=self.mode,
            expected_version=expected,
            actual_version=actual,
            maximum_exclusive=(
                self.maximum_exclusive
            ),
            allow_prerelease=(
                self.allow_prerelease
            ),
            required=self.required,
            compatible=compatible,
            reason=reason,
        )


@dataclass(frozen=True, slots=True)
class RuntimeCompatibilityPolicy:
    """Immutable runtime-compatibility policy."""

    policy_name: str
    policy_version: RuntimeSemanticVersion
    strict: bool
    requirements: tuple[
        RuntimeVersionRequirement,
        ...
    ]

    def __post_init__(self) -> None:
        normalized_name = str(
            self.policy_name or ""
        ).strip()

        if not _POLICY_NAME_PATTERN.fullmatch(
            normalized_name
        ):
            raise RuntimeCompatibilityValidationError(
                "policy_name must be 3-128 characters "
                "and contain only letters, numbers, dots, "
                "underscores, colons, or hyphens."
            )

        resolved_version = (
            RuntimeSemanticVersion.parse(
                self.policy_version
            )
        )

        resolved_requirements = tuple(
            self.requirements
        )

        if not resolved_requirements:
            raise RuntimeCompatibilityValidationError(
                "A compatibility policy requires at "
                "least one version requirement."
            )

        invalid_requirement_types = tuple(
            index
            for index, requirement
            in enumerate(resolved_requirements)
            if not isinstance(
                requirement,
                RuntimeVersionRequirement,
            )
        )

        if invalid_requirement_types:
            raise RuntimeCompatibilityValidationError(
                "All compatibility requirements must "
                "be RuntimeVersionRequirement instances."
            )

        contracts = tuple(
            requirement.contract
            for requirement in resolved_requirements
        )

        duplicate_contracts = tuple(
            sorted(
                {
                    contract
                    for contract in contracts
                    if contracts.count(contract) > 1
                }
            )
        )

        if duplicate_contracts:
            raise RuntimeCompatibilityValidationError(
                "Duplicate compatibility contracts: "
                + ", ".join(duplicate_contracts)
            )

        object.__setattr__(
            self,
            "policy_name",
            normalized_name,
        )

        object.__setattr__(
            self,
            "policy_version",
            resolved_version,
        )

        object.__setattr__(
            self,
            "strict",
            bool(self.strict),
        )

        object.__setattr__(
            self,
            "requirements",
            resolved_requirements,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "policy_name": self.policy_name,
            "policy_version": str(
                self.policy_version
            ),
            "strict": self.strict,
            "requirements": [
                {
                    "contract": requirement.contract,
                    "mode": requirement.mode.value,
                    "expected_version": str(
                        requirement.expected_version
                    ),
                    "maximum_exclusive": (
                        None
                        if (
                            requirement
                            .maximum_exclusive
                            is None
                        )
                        else str(
                            requirement
                            .maximum_exclusive
                        )
                    ),
                    "allow_prerelease": (
                        requirement.allow_prerelease
                    ),
                    "required": requirement.required,
                    "description": (
                        requirement.description
                    ),
                }
                for requirement
                in self.requirements
            ],
        }

    def fingerprint(self) -> str:
        payload = json.dumps(
            self.to_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")

        return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True, slots=True)
class RuntimeCompatibilityReport:
    """Immutable result of evaluating one runtime manifest."""

    compatible: bool
    strict: bool
    policy_name: str
    policy_version: RuntimeSemanticVersion
    policy_fingerprint: str
    manifest_fingerprint: str
    evaluated_at: datetime
    results: tuple[
        RuntimeCompatibilityResult,
        ...
    ]
    failed_contracts: tuple[str, ...]
    warning_contracts: tuple[str, ...]

    def to_dict(
        self,
        *,
        include_evaluated_at: bool = True,
    ) -> dict[str, Any]:
        result: dict[str, Any] = {
            "compatible": self.compatible,
            "strict": self.strict,
            "policy_name": self.policy_name,
            "policy_version": str(
                self.policy_version
            ),
            "policy_fingerprint": (
                self.policy_fingerprint
            ),
            "manifest_fingerprint": (
                self.manifest_fingerprint
            ),
            "results": [
                {
                    "contract": item.contract,
                    "mode": item.mode.value,
                    "expected_version": str(
                        item.expected_version
                    ),
                    "actual_version": str(
                        item.actual_version
                    ),
                    "maximum_exclusive": (
                        None
                        if item.maximum_exclusive is None
                        else str(
                            item.maximum_exclusive
                        )
                    ),
                    "allow_prerelease": (
                        item.allow_prerelease
                    ),
                    "required": item.required,
                    "compatible": item.compatible,
                    "reason": item.reason,
                }
                for item in self.results
            ],
            "failed_contracts": list(
                self.failed_contracts
            ),
            "warning_contracts": list(
                self.warning_contracts
            ),
        }

        if include_evaluated_at:
            result["evaluated_at"] = (
                self.evaluated_at.isoformat()
            )

        return result

    def fingerprint(self) -> str:
        payload = json.dumps(
            self.to_dict(
                include_evaluated_at=False
            ),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")

        return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True, slots=True)
class RuntimeCompatibilitySnapshot:
    """Immutable compatibility-layer inspection record."""

    evaluation_count: int
    policy_fingerprint: str
    last_report: RuntimeCompatibilityReport | None


class RuntimeCompatibilityLayer:
    """
    Evaluate runtime version manifests against one explicit policy.

    The layer records the most recent report for operational inspection.
    It does not modify manifests or version registrations.
    """

    __slots__ = (
        "_policy",
        "_evaluation_count",
        "_last_report",
        "_lock",
    )

    def __init__(
        self,
        policy: RuntimeCompatibilityPolicy,
    ) -> None:
        if not isinstance(
            policy,
            RuntimeCompatibilityPolicy,
        ):
            raise RuntimeCompatibilityValidationError(
                "A RuntimeCompatibilityPolicy is required."
            )

        self._policy = policy
        self._evaluation_count = 0
        self._last_report: (
            RuntimeCompatibilityReport | None
        ) = None
        self._lock = threading.RLock()

    @property
    def policy(
        self,
    ) -> RuntimeCompatibilityPolicy:
        return self._policy

    @property
    def evaluation_count(self) -> int:
        with self._lock:
            return self._evaluation_count

    @staticmethod
    def manifest_contracts(
        manifest: RuntimeVersionManifest,
    ) -> dict[str, RuntimeSemanticVersion]:
        if not isinstance(
            manifest,
            RuntimeVersionManifest,
        ):
            raise RuntimeCompatibilityValidationError(
                "A RuntimeVersionManifest is required."
            )

        return {
            "manifest.schema": (
                manifest.manifest_schema_version
            ),
            "runtime.version": (
                manifest.runtime_version
            ),
            "kernel.api": (
                manifest.kernel_api_version
            ),
            "service.contract": (
                manifest.service_contract_version
            ),
            "job.contract": (
                manifest.job_contract_version
            ),
            "state.schema": (
                manifest.state_schema_version
            ),
            "configuration.schema": (
                manifest.configuration_schema_version
            ),
        }

    def evaluate(
        self,
        manifest: RuntimeVersionManifest,
    ) -> RuntimeCompatibilityReport:
        contracts = self.manifest_contracts(
            manifest
        )

        results: list[
            RuntimeCompatibilityResult
        ] = []

        for requirement in self._policy.requirements:
            try:
                actual_version = contracts[
                    requirement.contract
                ]
            except KeyError as exc:
                raise RuntimeCompatibilityValidationError(
                    "Compatibility policy references an "
                    "unknown runtime manifest contract: "
                    f"{requirement.contract!r}"
                ) from exc

            results.append(
                requirement.evaluate(
                    actual_version
                )
            )

        failed_contracts = tuple(
            item.contract
            for item in results
            if (
                not item.compatible
                and (
                    item.required
                    or self._policy.strict
                )
            )
        )

        warning_contracts = tuple(
            item.contract
            for item in results
            if (
                not item.compatible
                and not item.required
                and not self._policy.strict
            )
        )

        report = RuntimeCompatibilityReport(
            compatible=not failed_contracts,
            strict=self._policy.strict,
            policy_name=self._policy.policy_name,
            policy_version=(
                self._policy.policy_version
            ),
            policy_fingerprint=(
                self._policy.fingerprint()
            ),
            manifest_fingerprint=(
                manifest.fingerprint()
            ),
            evaluated_at=_utc_now(),
            results=tuple(results),
            failed_contracts=failed_contracts,
            warning_contracts=warning_contracts,
        )

        with self._lock:
            self._evaluation_count += 1
            self._last_report = report

        return report

    def require_compatible(
        self,
        manifest: RuntimeVersionManifest,
    ) -> RuntimeCompatibilityReport:
        report = self.evaluate(manifest)

        if not report.compatible:
            raise RuntimeCompatibilityIncompatibleError(
                report
            )

        return report

    def snapshot(
        self,
    ) -> RuntimeCompatibilitySnapshot:
        with self._lock:
            return RuntimeCompatibilitySnapshot(
                evaluation_count=(
                    self._evaluation_count
                ),
                policy_fingerprint=(
                    self._policy.fingerprint()
                ),
                last_report=self._last_report,
            )


def create_default_runtime_compatibility_layer(
    *,
    strict: bool = True,
) -> RuntimeCompatibilityLayer:
    """
    Create the initial Universal Runtime compatibility policy.

    The pre-1.0 runtime contracts use SAME_MINOR because minor-version
    changes may still contain breaking changes while the runtime is in
    active development.
    """

    policy = RuntimeCompatibilityPolicy(
        policy_name="uri.phase1.default",
        policy_version=(
            RuntimeSemanticVersion.parse(
                DEFAULT_COMPATIBILITY_POLICY_VERSION
            )
        ),
        strict=bool(strict),
        requirements=(
            RuntimeVersionRequirement(
                contract="manifest.schema",
                mode=RuntimeCompatibilityMode.EXACT,
                expected_version=(
                    RuntimeSemanticVersion.parse(
                        "1.0.0"
                    )
                ),
                required=True,
            ),
            RuntimeVersionRequirement(
                contract="runtime.version",
                mode=RuntimeCompatibilityMode.SAME_MINOR,
                expected_version=(
                    RuntimeSemanticVersion.parse(
                        "0.1.0"
                    )
                ),
                required=True,
            ),
            RuntimeVersionRequirement(
                contract="kernel.api",
                mode=RuntimeCompatibilityMode.SAME_MINOR,
                expected_version=(
                    RuntimeSemanticVersion.parse(
                        "0.1.0"
                    )
                ),
                required=True,
            ),
            RuntimeVersionRequirement(
                contract="service.contract",
                mode=RuntimeCompatibilityMode.SAME_MINOR,
                expected_version=(
                    RuntimeSemanticVersion.parse(
                        "0.1.0"
                    )
                ),
                required=True,
            ),
            RuntimeVersionRequirement(
                contract="job.contract",
                mode=RuntimeCompatibilityMode.SAME_MINOR,
                expected_version=(
                    RuntimeSemanticVersion.parse(
                        "0.1.0"
                    )
                ),
                required=True,
            ),
            RuntimeVersionRequirement(
                contract="state.schema",
                mode=RuntimeCompatibilityMode.SAME_MINOR,
                expected_version=(
                    RuntimeSemanticVersion.parse(
                        "0.1.0"
                    )
                ),
                required=True,
            ),
            RuntimeVersionRequirement(
                contract="configuration.schema",
                mode=RuntimeCompatibilityMode.SAME_MAJOR,
                expected_version=(
                    RuntimeSemanticVersion.parse(
                        "1.0.0"
                    )
                ),
                required=True,
            ),
        ),
    )

    return RuntimeCompatibilityLayer(policy)
'''


def sha256_file(
    path: Path,
) -> str | None:
    if not path.exists():
        return None

    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def fail(message: str) -> None:
    raise RuntimeError(message)


def verify_ast_contract(
    path: Path,
) -> dict[str, Any]:
    text = path.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(
        text,
        filename=str(path),
    )

    classes: dict[str, set[str]] = {}
    functions: set[str] = set()

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            classes[node.name] = {
                child.name
                for child in node.body
                if isinstance(
                    child,
                    (
                        ast.FunctionDef,
                        ast.AsyncFunctionDef,
                    ),
                )
            }

        elif isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            functions.add(node.name)

    required_classes = {
        "RuntimeCompatibilityMode",
        "RuntimeCompatibilityResult",
        "RuntimeVersionRequirement",
        "RuntimeCompatibilityPolicy",
        "RuntimeCompatibilityReport",
        "RuntimeCompatibilitySnapshot",
        "RuntimeCompatibilityLayer",
        "RuntimeCompatibilityError",
        "RuntimeCompatibilityValidationError",
        "RuntimeCompatibilityIncompatibleError",
    }

    required_requirement_methods = {
        "evaluate",
    }

    required_policy_methods = {
        "to_dict",
        "fingerprint",
    }

    required_report_methods = {
        "to_dict",
        "fingerprint",
    }

    required_layer_methods = {
        "manifest_contracts",
        "evaluate",
        "require_compatible",
        "snapshot",
    }

    missing_classes = sorted(
        required_classes - set(classes)
    )

    missing_requirement_methods = sorted(
        required_requirement_methods
        - classes.get(
            "RuntimeVersionRequirement",
            set(),
        )
    )

    missing_policy_methods = sorted(
        required_policy_methods
        - classes.get(
            "RuntimeCompatibilityPolicy",
            set(),
        )
    )

    missing_report_methods = sorted(
        required_report_methods
        - classes.get(
            "RuntimeCompatibilityReport",
            set(),
        )
    )

    missing_layer_methods = sorted(
        required_layer_methods
        - classes.get(
            "RuntimeCompatibilityLayer",
            set(),
        )
    )

    if missing_classes:
        fail(
            "Runtime compatibility AST contract "
            "is missing classes: "
            + ", ".join(missing_classes)
        )

    if missing_requirement_methods:
        fail(
            "RuntimeVersionRequirement is missing "
            "methods: "
            + ", ".join(
                missing_requirement_methods
            )
        )

    if missing_policy_methods:
        fail(
            "RuntimeCompatibilityPolicy is missing "
            "methods: "
            + ", ".join(missing_policy_methods)
        )

    if missing_report_methods:
        fail(
            "RuntimeCompatibilityReport is missing "
            "methods: "
            + ", ".join(missing_report_methods)
        )

    if missing_layer_methods:
        fail(
            "RuntimeCompatibilityLayer is missing "
            "methods: "
            + ", ".join(missing_layer_methods)
        )

    if (
        "create_default_runtime_compatibility_layer"
        not in functions
    ):
        fail(
            "The default compatibility-layer "
            "factory is missing."
        )

    forbidden_business_terms = (
        "udare",
        "website_article_integrity",
        "article_validation",
        "semantic_intelligence",
        "uploaded_document_unified_content",
        "universal_unified_content_document",
    )

    lowered = text.lower()

    detected_forbidden_terms = [
        term
        for term in forbidden_business_terms
        if term in lowered
    ]

    if detected_forbidden_terms:
        fail(
            "Runtime compatibility contains "
            "pipeline-specific business terms: "
            + ", ".join(detected_forbidden_terms)
        )

    if "asyncio.create_task" in text:
        fail(
            "Runtime compatibility must not create "
            "detached tasks."
        )

    if "@app.on_event" in text:
        fail(
            "Runtime compatibility must not wire "
            "itself into the application."
        )

    return {
        "required_classes": sorted(
            required_classes
        ),
        "missing_classes": missing_classes,
        "missing_requirement_methods": (
            missing_requirement_methods
        ),
        "missing_policy_methods": (
            missing_policy_methods
        ),
        "missing_report_methods": (
            missing_report_methods
        ),
        "missing_layer_methods": (
            missing_layer_methods
        ),
        "default_factory_present": True,
        "pipeline_business_terms_detected": (
            detected_forbidden_terms
        ),
        "detached_task_creation_detected": False,
        "application_hook_detected": False,
    }


def import_runtime_module(
    module_name: str,
) -> Any:
    sys.modules.pop(
        module_name,
        None,
    )

    importlib.invalidate_caches()

    return importlib.import_module(
        module_name
    )


def verify_behavior(
    compatibility_module: Any,
    versioning_module: Any,
    kernel_module: Any,
    registry_module: Any,
) -> dict[str, Any]:
    CompatibilityLayer = (
        compatibility_module.RuntimeCompatibilityLayer
    )

    CompatibilityMode = (
        compatibility_module.RuntimeCompatibilityMode
    )

    CompatibilityPolicy = (
        compatibility_module.RuntimeCompatibilityPolicy
    )

    VersionRequirement = (
        compatibility_module.RuntimeVersionRequirement
    )

    ValidationError = (
        compatibility_module
        .RuntimeCompatibilityValidationError
    )

    IncompatibleError = (
        compatibility_module
        .RuntimeCompatibilityIncompatibleError
    )

    SemanticVersion = (
        versioning_module.RuntimeSemanticVersion
    )

    VersionManager = (
        versioning_module.RuntimeVersionManager
    )

    Kernel = (
        kernel_module.UniversalRuntimeKernel
    )

    Registry = (
        registry_module.RuntimeServiceRegistry
    )

    assertions: dict[str, str] = {}

    default_layer = (
        compatibility_module
        .create_default_runtime_compatibility_layer(
            strict=True
        )
    )

    compatible_version_manager = (
        versioning_module
        .create_default_runtime_version_manager(
            runtime_name=(
                "LinkCraftor Universal Runtime"
            ),
            runtime_version="0.1.4",
            kernel_api_version="0.1.2",
            service_contract_version="0.1.3",
            job_contract_version="0.1.1",
            state_schema_version="0.1.5",
            configuration_schema_version="1.2.0",
            release_channel="development",
        )
    )

    compatible_report = (
        default_layer.require_compatible(
            compatible_version_manager.manifest
        )
    )

    if not compatible_report.compatible:
        fail(
            "A compatible runtime manifest "
            "was rejected."
        )

    if compatible_report.failed_contracts:
        fail(
            "Compatible report contains failed "
            "contracts."
        )

    assertions[
        "default_policy_compatible_manifest"
    ] = "PASS"

    incompatible_version_manager = (
        versioning_module
        .create_default_runtime_version_manager(
            runtime_name=(
                "Incompatible Universal Runtime"
            ),
            runtime_version="0.1.0",
            kernel_api_version="0.2.0",
            service_contract_version="0.1.0",
            job_contract_version="0.1.0",
            state_schema_version="0.1.0",
            configuration_schema_version="1.0.0",
            release_channel="development",
        )
    )

    incompatible_report = default_layer.evaluate(
        incompatible_version_manager.manifest
    )

    if incompatible_report.compatible:
        fail(
            "An incompatible kernel API version "
            "was accepted."
        )

    if (
        "kernel.api"
        not in incompatible_report.failed_contracts
    ):
        fail(
            "Kernel API incompatibility was not "
            "reported."
        )

    assertions[
        "incompatible_contract_detection"
    ] = "PASS"

    raised_incompatibility = False

    try:
        default_layer.require_compatible(
            incompatible_version_manager.manifest
        )
    except IncompatibleError as exc:
        raised_incompatibility = (
            exc.report is not None
            and "kernel.api"
            in exc.report.failed_contracts
        )

    if not raised_incompatibility:
        fail(
            "Strict compatibility enforcement "
            "did not raise the expected error."
        )

    assertions[
        "strict_incompatibility_enforcement"
    ] = "PASS"

    exact_requirement = VersionRequirement(
        contract="kernel.api",
        mode=CompatibilityMode.EXACT,
        expected_version=(
            SemanticVersion.parse("1.2.3")
        ),
    )

    if not exact_requirement.evaluate(
        "1.2.3+build.7"
    ).compatible:
        fail(
            "Exact version precedence incorrectly "
            "rejected build metadata."
        )

    if exact_requirement.evaluate(
        "1.2.4"
    ).compatible:
        fail(
            "Exact version requirement accepted "
            "a different patch version."
        )

    assertions[
        "exact_compatibility_mode"
    ] = "PASS"

    same_major_requirement = VersionRequirement(
        contract="configuration.schema",
        mode=CompatibilityMode.SAME_MAJOR,
        expected_version=(
            SemanticVersion.parse("2.1.0")
        ),
    )

    if not same_major_requirement.evaluate(
        "2.9.0"
    ).compatible:
        fail(
            "Same-major compatibility rejected "
            "a valid version."
        )

    if same_major_requirement.evaluate(
        "3.0.0"
    ).compatible:
        fail(
            "Same-major compatibility accepted "
            "a new major version."
        )

    assertions[
        "same_major_compatibility_mode"
    ] = "PASS"

    same_minor_requirement = VersionRequirement(
        contract="service.contract",
        mode=CompatibilityMode.SAME_MINOR,
        expected_version=(
            SemanticVersion.parse("0.4.2")
        ),
    )

    if not same_minor_requirement.evaluate(
        "0.4.9"
    ).compatible:
        fail(
            "Same-minor compatibility rejected "
            "a valid patch version."
        )

    if same_minor_requirement.evaluate(
        "0.5.0"
    ).compatible:
        fail(
            "Same-minor compatibility accepted "
            "a new minor version."
        )

    assertions[
        "same_minor_compatibility_mode"
    ] = "PASS"

    minimum_requirement = VersionRequirement(
        contract="runtime.version",
        mode=CompatibilityMode.AT_LEAST,
        expected_version=(
            SemanticVersion.parse("1.5.0")
        ),
    )

    if not minimum_requirement.evaluate(
        "2.0.0"
    ).compatible:
        fail(
            "Minimum-version compatibility rejected "
            "a higher version."
        )

    if minimum_requirement.evaluate(
        "1.4.9"
    ).compatible:
        fail(
            "Minimum-version compatibility accepted "
            "a lower version."
        )

    assertions[
        "minimum_compatibility_mode"
    ] = "PASS"

    range_requirement = VersionRequirement(
        contract="state.schema",
        mode=CompatibilityMode.RANGE,
        expected_version=(
            SemanticVersion.parse("3.2.0")
        ),
        maximum_exclusive=(
            SemanticVersion.parse("4.0.0")
        ),
    )

    if not range_requirement.evaluate(
        "3.9.9"
    ).compatible:
        fail(
            "Range compatibility rejected "
            "an in-range version."
        )

    if range_requirement.evaluate(
        "4.0.0"
    ).compatible:
        fail(
            "Range compatibility accepted its "
            "exclusive upper boundary."
        )

    assertions[
        "bounded_range_compatibility_mode"
    ] = "PASS"

    prerelease_requirement = VersionRequirement(
        contract="job.contract",
        mode=CompatibilityMode.AT_LEAST,
        expected_version=(
            SemanticVersion.parse("1.0.0")
        ),
        allow_prerelease=False,
    )

    if prerelease_requirement.evaluate(
        "2.0.0-beta.1"
    ).compatible:
        fail(
            "Prerelease protection accepted "
            "a forbidden prerelease version."
        )

    prerelease_allowed_requirement = (
        VersionRequirement(
            contract="job.contract",
            mode=CompatibilityMode.AT_LEAST,
            expected_version=(
                SemanticVersion.parse(
                    "2.0.0-alpha.1"
                )
            ),
            allow_prerelease=True,
        )
    )

    if not prerelease_allowed_requirement.evaluate(
        "2.0.0-beta.1"
    ).compatible:
        fail(
            "Prerelease compatibility rejected "
            "an explicitly permitted prerelease."
        )

    assertions[
        "prerelease_policy_enforcement"
    ] = "PASS"

    optional_policy = CompatibilityPolicy(
        policy_name="uri.optional.test",
        policy_version=(
            SemanticVersion.parse("0.1.0")
        ),
        strict=False,
        requirements=(
            VersionRequirement(
                contract="runtime.version",
                mode=CompatibilityMode.SAME_MINOR,
                expected_version=(
                    SemanticVersion.parse("0.9.0")
                ),
                required=False,
            ),
            VersionRequirement(
                contract="kernel.api",
                mode=CompatibilityMode.SAME_MINOR,
                expected_version=(
                    SemanticVersion.parse("0.1.0")
                ),
                required=True,
            ),
        ),
    )

    optional_layer = CompatibilityLayer(
        optional_policy
    )

    optional_report = optional_layer.evaluate(
        compatible_version_manager.manifest
    )

    if not optional_report.compatible:
        fail(
            "A non-strict optional incompatibility "
            "failed the complete report."
        )

    if (
        "runtime.version"
        not in optional_report.warning_contracts
    ):
        fail(
            "Optional incompatibility was not "
            "reported as a warning."
        )

    assertions[
        "optional_contract_warning"
    ] = "PASS"

    duplicate_policy_rejected = False

    try:
        CompatibilityPolicy(
            policy_name="uri.duplicate.test",
            policy_version=(
                SemanticVersion.parse("0.1.0")
            ),
            strict=True,
            requirements=(
                VersionRequirement(
                    contract="kernel.api",
                    mode=CompatibilityMode.EXACT,
                    expected_version=(
                        SemanticVersion.parse("0.1.0")
                    ),
                ),
                VersionRequirement(
                    contract="kernel.api",
                    mode=CompatibilityMode.EXACT,
                    expected_version=(
                        SemanticVersion.parse("0.1.0")
                    ),
                ),
            ),
        )
    except ValidationError:
        duplicate_policy_rejected = True

    if not duplicate_policy_rejected:
        fail(
            "Duplicate policy contracts "
            "were not rejected."
        )

    assertions[
        "duplicate_policy_contract_rejection"
    ] = "PASS"

    policy_fingerprint = (
        default_layer.policy.fingerprint()
    )

    report_fingerprint = (
        compatible_report.fingerprint()
    )

    if len(policy_fingerprint) != 64:
        fail(
            "Compatibility policy fingerprint "
            "is invalid."
        )

    if len(report_fingerprint) != 64:
        fail(
            "Compatibility report fingerprint "
            "is invalid."
        )

    deterministic_report = default_layer.evaluate(
        compatible_version_manager.manifest
    )

    if (
        deterministic_report.fingerprint()
        != compatible_report.fingerprint()
    ):
        fail(
            "Equal compatibility evaluations "
            "produced different fingerprints."
        )

    assertions[
        "deterministic_compatibility_fingerprints"
    ] = "PASS"

    policy_immutable = False

    try:
        default_layer.policy.strict = False
    except (AttributeError, TypeError):
        policy_immutable = True

    if not policy_immutable:
        fail(
            "Compatibility policy was mutable."
        )

    report_immutable = False

    try:
        compatible_report.compatible = False
    except (AttributeError, TypeError):
        report_immutable = True

    if not report_immutable:
        fail(
            "Compatibility report was mutable."
        )

    snapshot = default_layer.snapshot()

    snapshot_immutable = False

    try:
        snapshot.evaluation_count = 0
    except (AttributeError, TypeError):
        snapshot_immutable = True

    if not snapshot_immutable:
        fail(
            "Compatibility snapshot was mutable."
        )

    assertions[
        "immutable_policy_report_snapshot"
    ] = "PASS"

    thread_layer = (
        compatibility_module
        .create_default_runtime_compatibility_layer(
            strict=True
        )
    )

    thread_errors: list[str] = []
    thread_count = 16

    def evaluate_thread(
        index: int,
    ) -> None:
        try:
            report = thread_layer.require_compatible(
                compatible_version_manager.manifest
            )

            if not report.compatible:
                raise RuntimeError(
                    f"Thread {index} received an "
                    "incompatible report."
                )

        except Exception as exc:
            thread_errors.append(
                f"{type(exc).__name__}: {exc}"
            )

    threads = [
        threading.Thread(
            target=evaluate_thread,
            args=(index,),
            daemon=True,
        )
        for index in range(thread_count)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    if thread_errors:
        fail(
            "Concurrent compatibility evaluation "
            "failed: "
            + "; ".join(thread_errors)
        )

    if thread_layer.evaluation_count != thread_count:
        fail(
            "Concurrent compatibility evaluation "
            "produced an incorrect count."
        )

    assertions[
        "thread_safe_compatibility_evaluation"
    ] = "PASS"

    service_registry = Registry()

    service_registry.register(
        "runtime.versioning",
        compatible_version_manager,
        capabilities=[
            "runtime.version.read",
        ],
        startup_order=-100,
        critical=True,
    )

    service_registry.register(
        "runtime.compatibility",
        default_layer,
        capabilities=[
            "runtime.compatibility.evaluate",
            "runtime.compatibility.enforce",
        ],
        dependencies=[
            "runtime.versioning",
        ],
        startup_order=-90,
        critical=True,
    )

    dependency_order = (
        service_registry.dependency_order()
    )

    if dependency_order != (
        "runtime.versioning",
        "runtime.compatibility",
    ):
        fail(
            "Versioning/compatibility service order "
            "is incorrect."
        )

    service_registry.seal()

    if (
        service_registry.get(
            "runtime.versioning",
            VersionManager,
        )
        is not compatible_version_manager
    ):
        fail(
            "Service registry returned the wrong "
            "version manager."
        )

    if (
        service_registry.get(
            "runtime.compatibility",
            CompatibilityLayer,
        )
        is not default_layer
    ):
        fail(
            "Service registry returned the wrong "
            "compatibility layer."
        )

    assertions[
        "service_registry_compatibility_binding"
    ] = "PASS"

    kernel = Kernel(
        runtime_id="linkcraftor.primary",
        product_name="LinkCraftor",
    )

    kernel.bind_component(
        "service_registry",
        service_registry,
    )

    kernel.bind_component(
        "versioning",
        compatible_version_manager,
    )

    compatibility_binding = kernel.bind_component(
        "compatibility",
        default_layer,
    )

    if (
        compatibility_binding.key
        != "compatibility"
    ):
        fail(
            "Kernel compatibility binding failed."
        )

    if (
        kernel.get_component(
            "compatibility",
            CompatibilityLayer,
        )
        is not default_layer
    ):
        fail(
            "Kernel returned the wrong "
            "compatibility layer."
        )

    assertions[
        "kernel_compatibility_binding"
    ] = "PASS"

    return {
        "assertions": assertions,
        "policy_name": (
            default_layer.policy.policy_name
        ),
        "policy_version": str(
            default_layer.policy.policy_version
        ),
        "policy_fingerprint": (
            policy_fingerprint
        ),
        "compatible_report_fingerprint": (
            report_fingerprint
        ),
        "evaluated_contract_count": len(
            compatible_report.results
        ),
        "thread_evaluation_count": (
            thread_layer.evaluation_count
        ),
        "service_dependency_order": list(
            dependency_order
        ),
        "kernel_generation": (
            kernel.generation
        ),
    }


def rollback(
    *,
    target_existed: bool,
) -> None:
    if target_existed:
        if not BACKUP_TARGET.exists():
            raise RuntimeError(
                "Runtime compatibility rollback "
                "backup is missing."
            )

        TARGET.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.copy2(
            BACKUP_TARGET,
            TARGET,
        )

    elif TARGET.exists():
        TARGET.unlink()


def main() -> int:
    print("=" * 78)
    print("UNIVERSAL RUNTIME INFRASTRUCTURE")
    print("1.1.9 — RUNTIME COMPATIBILITY LAYER BUILD")
    print("=" * 78)
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Target:       {TARGET}")
    print()

    required_files = [
        KERNEL_FILE,
        CONFIGURATION_FILE,
        ENVIRONMENT_FILE,
        SERVICE_REGISTRY_FILE,
        LIFECYCLE_FILE,
        BOOT_FILE,
        SHUTDOWN_FILE,
        VERSIONING_FILE,
        EXISTING_RUNTIME_FACADE,
        MAIN_FILE,
    ]

    missing_files = [
        path
        for path in required_files
        if not path.exists()
    ]

    if missing_files:
        fail(
            "Required files are missing:\n"
            + "\n".join(
                str(path)
                for path in missing_files
            )
        )

    target_existed = TARGET.exists()
    target_original_hash = sha256_file(
        TARGET
    )

    protected_hashes_before = {
        "kernel": sha256_file(
            KERNEL_FILE
        ),
        "configuration": sha256_file(
            CONFIGURATION_FILE
        ),
        "environment": sha256_file(
            ENVIRONMENT_FILE
        ),
        "service_registry": sha256_file(
            SERVICE_REGISTRY_FILE
        ),
        "lifecycle_manager": sha256_file(
            LIFECYCLE_FILE
        ),
        "boot_process": sha256_file(
            BOOT_FILE
        ),
        "shutdown_process": sha256_file(
            SHUTDOWN_FILE
        ),
        "versioning": sha256_file(
            VERSIONING_FILE
        ),
        "runtime_facade": sha256_file(
            EXISTING_RUNTIME_FACADE
        ),
        "main": sha256_file(
            MAIN_FILE
        ),
    }

    if target_existed:
        BACKUP_TARGET.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.copy2(
            TARGET,
            BACKUP_TARGET,
        )

        print(
            "Existing runtime compatibility file "
            "backed up:"
        )
        print(BACKUP_TARGET)
        print()

    TARGET.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    compatibility_module_name = (
        "backend.server.runtime."
        "runtime_compatibility"
    )

    versioning_module_name = (
        "backend.server.runtime."
        "runtime_versioning"
    )

    kernel_module_name = (
        "backend.server.runtime."
        "universal_runtime_kernel"
    )

    registry_module_name = (
        "backend.server.runtime."
        "runtime_service_registry"
    )

    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(
            0,
            str(PROJECT_ROOT),
        )

    try:
        TARGET.write_text(
            COMPATIBILITY_SOURCE,
            encoding="utf-8",
            newline="\n",
        )

        for source_file in [
            *required_files,
            TARGET,
        ]:
            py_compile.compile(
                str(source_file),
                doraise=True,
            )

        ast_contract = verify_ast_contract(
            TARGET
        )

        process_environment_before = dict(
            os.environ
        )

        # Load dependencies before runtime_compatibility.
        #
        # runtime_compatibility imports RuntimeVersionManifest from the
        # canonical runtime_versioning module. Reloading runtime_versioning
        # after compatibility has imported it creates a second Python class
        # identity and causes valid manifests to fail isinstance checks.
        versioning_module = import_runtime_module(
            versioning_module_name
        )

        kernel_module = import_runtime_module(
            kernel_module_name
        )

        registry_module = import_runtime_module(
            registry_module_name
        )

        compatibility_module = import_runtime_module(
            compatibility_module_name
        )

        if (
            dict(os.environ)
            != process_environment_before
        ):
            fail(
                "Importing runtime compatibility "
                "mutated os.environ."
            )

        behavioral_results = verify_behavior(
            compatibility_module,
            versioning_module,
            kernel_module,
            registry_module,
        )

        protected_hashes_after = {
            "kernel": sha256_file(
                KERNEL_FILE
            ),
            "configuration": sha256_file(
                CONFIGURATION_FILE
            ),
            "environment": sha256_file(
                ENVIRONMENT_FILE
            ),
            "service_registry": sha256_file(
                SERVICE_REGISTRY_FILE
            ),
            "lifecycle_manager": sha256_file(
                LIFECYCLE_FILE
            ),
            "boot_process": sha256_file(
                BOOT_FILE
            ),
            "shutdown_process": sha256_file(
                SHUTDOWN_FILE
            ),
            "versioning": sha256_file(
                VERSIONING_FILE
            ),
            "runtime_facade": sha256_file(
                EXISTING_RUNTIME_FACADE
            ),
            "main": sha256_file(
                MAIN_FILE
            ),
        }

        if (
            protected_hashes_before
            != protected_hashes_after
        ):
            fail(
                "A protected runtime file changed "
                "unexpectedly."
            )

    except Exception:
        rollback(
            target_existed=target_existed,
        )

        print()
        print("ROLLBACK COMPLETE")
        print(
            "Runtime compatibility verification "
            "failed. The previous filesystem state "
            "was restored."
        )

        raise

    finally:
        for module_name in (
            compatibility_module_name,
            versioning_module_name,
            kernel_module_name,
            registry_module_name,
        ):
            sys.modules.pop(
                module_name,
                None,
            )

    target_final_hash = sha256_file(
        TARGET
    )

    evidence = {
        "build_version": BUILD_VERSION,
        "timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "project_root": str(PROJECT_ROOT),
        "target": str(TARGET),
        "target_existed_before_build": (
            target_existed
        ),
        "target_backup": (
            str(BACKUP_TARGET)
            if target_existed
            else None
        ),
        "target_original_sha256": (
            target_original_hash
        ),
        "target_final_sha256": (
            target_final_hash
        ),
        "protected_hashes_before": (
            protected_hashes_before
        ),
        "protected_hashes_after": (
            protected_hashes_after
        ),
        "verification": {
            "compatibility_py_compile": "PASS",
            "foundation_files_compile": "PASS",
            "main_py_compile": "PASS",
            "ast_contract": "PASS",
            "exact_mode": "PASS",
            "same_major_mode": "PASS",
            "same_minor_mode": "PASS",
            "minimum_mode": "PASS",
            "range_mode": "PASS",
            "prerelease_policy": "PASS",
            "strict_enforcement": "PASS",
            "optional_warning_contract": "PASS",
            "fingerprint_contract": "PASS",
            "immutability_contract": "PASS",
            "thread_safety_contract": "PASS",
            "versioning_integration": "PASS",
            "service_registry_binding": "PASS",
            "kernel_binding": "PASS",
            "import_side_effect_protection": "PASS",
            "business_logic_agnostic_test": "PASS",
            "protected_files_unchanged": "PASS",
            "automatic_rollback_required": False,
        },
        "ast_contract_details": (
            ast_contract
        ),
        "behavioral_results": (
            behavioral_results
        ),
        "phase_status": {
            "phase": "1",
            "item": "1.1.9",
            "name": "Runtime Compatibility Layer",
            "implementation_status": "IMPLEMENTED",
            "verification_status": "PASS",
            "versioning_integration": "PASS",
            "kernel_binding_status": "PASS",
            "service_registry_binding_status": "PASS",
            "application_boot_integration": "PENDING",
            "certification_status": "NOT_CERTIFIED",
        },
    }

    EVIDENCE_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    EVIDENCE_JSON.write_text(
        json.dumps(
            evidence,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    evidence_lines = [
        "=" * 78,
        "UNIVERSAL RUNTIME INFRASTRUCTURE",
        "1.1.9 — RUNTIME COMPATIBILITY LAYER EVIDENCE",
        "=" * 78,
        "",
        f"Build version: {BUILD_VERSION}",
        f"Timestamp UTC: {evidence['timestamp_utc']}",
        f"Target: {TARGET}",
        "",
        "VERIFICATION",
        "-" * 78,
        "Runtime Compatibility compilation: PASS",
        "Phase 1 foundation compilation: PASS",
        "main.py compilation: PASS",
        "Compatibility AST contract: PASS",
        "Import-time side-effect protection: PASS",
        "Business-logic-agnostic boundary: PASS",
        "Protected existing files unchanged: PASS",
        "",
        "BEHAVIORAL TESTS",
        "-" * 78,
    ]

    for name, status in behavioral_results[
        "assertions"
    ].items():
        evidence_lines.append(
            f"{name}: {status}"
        )

    evidence_lines.extend(
        [
            "",
            "COMPATIBILITY POLICY",
            "-" * 78,
            (
                "Policy name: "
                f"{behavioral_results['policy_name']}"
            ),
            (
                "Policy version: "
                f"{behavioral_results['policy_version']}"
            ),
            (
                "Policy fingerprint: "
                f"{behavioral_results['policy_fingerprint']}"
            ),
            (
                "Evaluated contracts: "
                f"{behavioral_results['evaluated_contract_count']}"
            ),
            "",
            "SERVICE ORDER",
            "-" * 78,
        ]
    )

    for service_key in behavioral_results[
        "service_dependency_order"
    ]:
        evidence_lines.append(
            service_key
        )

    evidence_lines.extend(
        [
            "",
            "CHECKLIST POSITION",
            "-" * 78,
            "1.1.1 kernel compatibility: PASS",
            "1.1.4 service-registry compatibility: PASS",
            "1.1.8 versioning integration: PASS",
            "1.1.9 implementation: PASS",
            "1.1.9 isolated verification: PASS",
            "1.1.9 kernel binding: PASS",
            "1.1.9 service-registry binding: PASS",
            (
                "1.1.9 application boot integration: "
                "PENDING"
            ),
            "1.1.9 certification: NOT CERTIFIED",
            "Phase 1 certification: NOT CERTIFIED",
            "",
        ]
    )

    EVIDENCE_TEXT.write_text(
        "\n".join(evidence_lines),
        encoding="utf-8",
    )

    print("BUILD VERIFICATION")
    print("-" * 78)
    print(
        "Runtime Compatibility compilation:     PASS"
    )
    print(
        "Phase 1 foundation compilation:        PASS"
    )
    print(
        "main.py compilation:                   PASS"
    )
    print(
        "Compatibility AST contract:            PASS"
    )
    print(
        "Exact compatibility mode:              PASS"
    )
    print(
        "Same-major compatibility mode:         PASS"
    )
    print(
        "Same-minor compatibility mode:         PASS"
    )
    print(
        "Minimum-version compatibility:         PASS"
    )
    print(
        "Bounded-range compatibility:           PASS"
    )
    print(
        "Prerelease policy enforcement:         PASS"
    )
    print(
        "Strict incompatibility enforcement:    PASS"
    )
    print(
        "Optional contract warnings:            PASS"
    )
    print(
        "Deterministic policy/report fingerprints: PASS"
    )
    print(
        "Immutable policy/report/snapshot:       PASS"
    )
    print(
        "Thread-safe compatibility evaluation:  PASS"
    )
    print(
        "Runtime Versioning integration:        PASS"
    )
    print(
        "Service-registry compatibility binding: PASS"
    )
    print(
        "Kernel compatibility binding:          PASS"
    )
    print(
        "Import-time side-effect protection:    PASS"
    )
    print(
        "Business-logic-agnostic boundary:      PASS"
    )
    print(
        "Protected existing files unchanged:    PASS"
    )
    print()

    print("FILES")
    print("-" * 78)
    print(f"Compatibility: {TARGET}")
    print(f"Evidence JSON: {EVIDENCE_JSON}")
    print(f"Evidence text: {EVIDENCE_TEXT}")
    print()

    print("1.1.9 RUNTIME COMPATIBILITY LAYER")
    print("IMPLEMENTATION: PASS")
    print("ISOLATED VERIFICATION: PASS")
    print("VERSIONING INTEGRATION: PASS")
    print("KERNEL BINDING: PASS")
    print("SERVICE-REGISTRY BINDING: PASS")
    print("APPLICATION BOOT INTEGRATION: PENDING")
    print("CERTIFICATION: NOT CERTIFIED")
    print()
    print("NO PRODUCTION DATA WAS MODIFIED")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
