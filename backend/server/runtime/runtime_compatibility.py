from __future__ import annotations

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
