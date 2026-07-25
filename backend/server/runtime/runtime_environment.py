from __future__ import annotations

"""
Universal Runtime Environment Management.

This module defines and validates the operating environment of the
Universal Runtime Infrastructure.

It explicitly distinguishes development, testing, staging, and
production. It does not load configuration, boot the application,
execute jobs, initialize workers, or contain pipeline business logic.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping, Protocol


__all__ = [
    "RuntimeEnvironmentCapability",
    "RuntimeEnvironmentCapabilityError",
    "RuntimeEnvironmentConfigurationError",
    "RuntimeEnvironmentError",
    "RuntimeEnvironmentManager",
    "RuntimeEnvironmentMismatchError",
    "RuntimeEnvironmentName",
    "RuntimeEnvironmentPolicy",
    "RuntimeEnvironmentSnapshot",
]


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class RuntimeEnvironmentError(RuntimeError):
    """Base runtime-environment failure."""


class RuntimeEnvironmentConfigurationError(
    RuntimeEnvironmentError
):
    """Raised when configuration violates environment policy."""


class RuntimeEnvironmentMismatchError(
    RuntimeEnvironmentError
):
    """Raised when the active environment is not expected."""


class RuntimeEnvironmentCapabilityError(
    RuntimeEnvironmentError
):
    """Raised when an environment forbids a capability."""


class RuntimeEnvironmentName(str, Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class RuntimeEnvironmentCapability(str, Enum):
    DEBUG = "debug"
    MEMORY_STATE_BACKEND = "memory_state_backend"
    SCHEMA_AUTO_MIGRATE = "schema_auto_migrate"
    RELAXED_COMPATIBILITY = "relaxed_compatibility"
    BACKGROUND_WORKERS = "background_workers"


@dataclass(frozen=True, slots=True)
class RuntimeEnvironmentPolicy:
    """Immutable policy for one runtime environment."""

    name: RuntimeEnvironmentName
    production_like: bool
    allows_debug: bool
    allows_memory_state_backend: bool
    allows_schema_auto_migrate: bool
    allows_relaxed_compatibility: bool
    allows_background_workers: bool

    def capability_allowed(
        self,
        capability: RuntimeEnvironmentCapability | str,
    ) -> bool:
        resolved = RuntimeEnvironmentManager.coerce_capability(
            capability
        )

        if resolved is RuntimeEnvironmentCapability.DEBUG:
            return self.allows_debug

        if (
            resolved
            is RuntimeEnvironmentCapability.MEMORY_STATE_BACKEND
        ):
            return self.allows_memory_state_backend

        if (
            resolved
            is RuntimeEnvironmentCapability.SCHEMA_AUTO_MIGRATE
        ):
            return self.allows_schema_auto_migrate

        if (
            resolved
            is RuntimeEnvironmentCapability.RELAXED_COMPATIBILITY
        ):
            return self.allows_relaxed_compatibility

        if (
            resolved
            is RuntimeEnvironmentCapability.BACKGROUND_WORKERS
        ):
            return self.allows_background_workers

        raise RuntimeEnvironmentCapabilityError(
            f"Unsupported runtime capability: {resolved!r}"
        )


_ENVIRONMENT_POLICIES: Mapping[
    RuntimeEnvironmentName,
    RuntimeEnvironmentPolicy,
] = MappingProxyType(
    {
        RuntimeEnvironmentName.DEVELOPMENT: (
            RuntimeEnvironmentPolicy(
                name=RuntimeEnvironmentName.DEVELOPMENT,
                production_like=False,
                allows_debug=True,
                allows_memory_state_backend=True,
                allows_schema_auto_migrate=True,
                allows_relaxed_compatibility=True,
                allows_background_workers=True,
            )
        ),
        RuntimeEnvironmentName.TESTING: (
            RuntimeEnvironmentPolicy(
                name=RuntimeEnvironmentName.TESTING,
                production_like=False,
                allows_debug=True,
                allows_memory_state_backend=True,
                allows_schema_auto_migrate=True,
                allows_relaxed_compatibility=True,
                allows_background_workers=True,
            )
        ),
        RuntimeEnvironmentName.STAGING: (
            RuntimeEnvironmentPolicy(
                name=RuntimeEnvironmentName.STAGING,
                production_like=True,
                allows_debug=False,
                allows_memory_state_backend=False,
                allows_schema_auto_migrate=False,
                allows_relaxed_compatibility=False,
                allows_background_workers=True,
            )
        ),
        RuntimeEnvironmentName.PRODUCTION: (
            RuntimeEnvironmentPolicy(
                name=RuntimeEnvironmentName.PRODUCTION,
                production_like=True,
                allows_debug=False,
                allows_memory_state_backend=False,
                allows_schema_auto_migrate=False,
                allows_relaxed_compatibility=False,
                allows_background_workers=True,
            )
        ),
    }
)


class RuntimeConfigurationContract(Protocol):
    runtime_id: str
    product_name: str
    environment: str
    debug: bool
    data_root: Path
    state_backend: str
    worker_enabled: bool
    strict_compatibility: bool
    schema_auto_migrate: bool

    def fingerprint(self) -> str:
        ...


@dataclass(frozen=True, slots=True)
class RuntimeEnvironmentSnapshot:
    """Immutable environment-inspection record."""

    name: RuntimeEnvironmentName
    production_like: bool
    runtime_id: str
    product_name: str
    data_root: Path
    state_backend: str
    worker_enabled: bool
    configuration_fingerprint: str
    validated_at: datetime
    policy: RuntimeEnvironmentPolicy


class RuntimeEnvironmentManager:
    """
    Validate and expose the runtime operating environment.

    Responsibilities:

    - Resolve the configured environment name.
    - Apply environment-specific safety policy.
    - Detect deployment-environment mismatches.
    - Expose immutable policy and inspection records.
    - Provide explicit capability authorization.

    Non-responsibilities:

    - Reading os.environ.
    - Loading configuration files.
    - Creating directories.
    - Starting workers.
    - Booting or stopping the runtime.
    """

    __slots__ = (
        "_configuration",
        "_name",
        "_policy",
        "_validated_at",
    )

    def __init__(
        self,
        configuration: RuntimeConfigurationContract,
    ) -> None:
        self._assert_configuration_contract(
            configuration
        )

        name = self.coerce_name(
            configuration.environment
        )

        policy = self.policy_for(name)

        self._configuration = configuration
        self._name = name
        self._policy = policy
        self._validated_at = _utc_now()

        self.validate_configuration()

    @staticmethod
    def coerce_name(
        environment: RuntimeEnvironmentName | str,
    ) -> RuntimeEnvironmentName:
        if isinstance(
            environment,
            RuntimeEnvironmentName,
        ):
            return environment

        normalized = str(environment or "").strip().lower()

        try:
            return RuntimeEnvironmentName(normalized)
        except ValueError as exc:
            raise RuntimeEnvironmentConfigurationError(
                "Unknown runtime environment: "
                f"{environment!r}. Expected one of: "
                + ", ".join(
                    item.value
                    for item in RuntimeEnvironmentName
                )
            ) from exc

    @staticmethod
    def coerce_capability(
        capability: RuntimeEnvironmentCapability | str,
    ) -> RuntimeEnvironmentCapability:
        if isinstance(
            capability,
            RuntimeEnvironmentCapability,
        ):
            return capability

        normalized = str(capability or "").strip().lower()

        try:
            return RuntimeEnvironmentCapability(
                normalized
            )
        except ValueError as exc:
            raise RuntimeEnvironmentCapabilityError(
                "Unknown runtime-environment capability: "
                f"{capability!r}."
            ) from exc

    @staticmethod
    def policy_for(
        environment: RuntimeEnvironmentName | str,
    ) -> RuntimeEnvironmentPolicy:
        name = RuntimeEnvironmentManager.coerce_name(
            environment
        )

        return _ENVIRONMENT_POLICIES[name]

    @staticmethod
    def available_policies() -> Mapping[
        str,
        RuntimeEnvironmentPolicy,
    ]:
        return MappingProxyType(
            {
                name.value: policy
                for name, policy
                in _ENVIRONMENT_POLICIES.items()
            }
        )

    @property
    def name(self) -> RuntimeEnvironmentName:
        return self._name

    @property
    def policy(self) -> RuntimeEnvironmentPolicy:
        return self._policy

    @property
    def is_production_like(self) -> bool:
        return self._policy.production_like

    @property
    def validated_at(self) -> datetime:
        return self._validated_at

    def validate_configuration(self) -> None:
        configuration = self._configuration
        policy = self._policy

        if configuration.debug and not policy.allows_debug:
            raise RuntimeEnvironmentConfigurationError(
                f"Debug mode is forbidden in the "
                f"{self._name.value!r} environment."
            )

        if (
            configuration.state_backend == "memory"
            and not policy.allows_memory_state_backend
        ):
            raise RuntimeEnvironmentConfigurationError(
                "The memory state backend is forbidden in "
                f"the {self._name.value!r} environment."
            )

        if (
            configuration.schema_auto_migrate
            and not policy.allows_schema_auto_migrate
        ):
            raise RuntimeEnvironmentConfigurationError(
                "Automatic runtime schema migration is "
                f"forbidden in the {self._name.value!r} "
                "environment."
            )

        if (
            not configuration.strict_compatibility
            and not policy.allows_relaxed_compatibility
        ):
            raise RuntimeEnvironmentConfigurationError(
                "Relaxed runtime compatibility is forbidden "
                f"in the {self._name.value!r} environment."
            )

        if (
            configuration.worker_enabled
            and not policy.allows_background_workers
        ):
            raise RuntimeEnvironmentConfigurationError(
                "Background workers are forbidden in the "
                f"{self._name.value!r} environment."
            )

        if not Path(configuration.data_root).is_absolute():
            raise RuntimeEnvironmentConfigurationError(
                "The configured runtime data_root must be "
                "an absolute path before environment "
                "management begins."
            )

        if not str(configuration.runtime_id or "").strip():
            raise RuntimeEnvironmentConfigurationError(
                "The runtime_id must not be empty."
            )

        if not str(configuration.product_name or "").strip():
            raise RuntimeEnvironmentConfigurationError(
                "The product_name must not be empty."
            )

        fingerprint = configuration.fingerprint()

        if (
            not isinstance(fingerprint, str)
            or len(fingerprint) != 64
        ):
            raise RuntimeEnvironmentConfigurationError(
                "The runtime configuration fingerprint "
                "is invalid."
            )

    def capability_allowed(
        self,
        capability: RuntimeEnvironmentCapability | str,
    ) -> bool:
        return self._policy.capability_allowed(
            capability
        )

    def require_capability(
        self,
        capability: RuntimeEnvironmentCapability | str,
    ) -> RuntimeEnvironmentCapability:
        resolved = self.coerce_capability(
            capability
        )

        if not self.capability_allowed(resolved):
            raise RuntimeEnvironmentCapabilityError(
                f"Capability {resolved.value!r} is forbidden "
                f"in the {self._name.value!r} environment."
            )

        return resolved

    def ensure_expected_environment(
        self,
        *expected_environments: RuntimeEnvironmentName | str,
    ) -> RuntimeEnvironmentName:
        if not expected_environments:
            raise RuntimeEnvironmentMismatchError(
                "At least one expected environment is required."
            )

        expected = frozenset(
            self.coerce_name(item)
            for item in expected_environments
        )

        if self._name not in expected:
            raise RuntimeEnvironmentMismatchError(
                "Runtime environment mismatch: active "
                f"environment is {self._name.value!r}; "
                "expected one of: "
                + ", ".join(
                    sorted(
                        item.value
                        for item in expected
                    )
                )
            )

        return self._name

    def context(self) -> Mapping[str, Any]:
        """Return a read-only operational environment context."""

        configuration = self._configuration

        return MappingProxyType(
            {
                "environment": self._name.value,
                "production_like": (
                    self._policy.production_like
                ),
                "runtime_id": configuration.runtime_id,
                "product_name": configuration.product_name,
                "data_root": str(
                    configuration.data_root
                ),
                "state_backend": (
                    configuration.state_backend
                ),
                "worker_enabled": (
                    configuration.worker_enabled
                ),
                "strict_compatibility": (
                    configuration.strict_compatibility
                ),
            }
        )

    def snapshot(self) -> RuntimeEnvironmentSnapshot:
        configuration = self._configuration

        return RuntimeEnvironmentSnapshot(
            name=self._name,
            production_like=(
                self._policy.production_like
            ),
            runtime_id=configuration.runtime_id,
            product_name=configuration.product_name,
            data_root=Path(
                configuration.data_root
            ),
            state_backend=configuration.state_backend,
            worker_enabled=configuration.worker_enabled,
            configuration_fingerprint=(
                configuration.fingerprint()
            ),
            validated_at=self._validated_at,
            policy=self._policy,
        )

    @staticmethod
    def _assert_configuration_contract(
        configuration: RuntimeConfigurationContract,
    ) -> None:
        if configuration is None:
            raise RuntimeEnvironmentConfigurationError(
                "Runtime configuration is required."
            )

        required_attributes = (
            "runtime_id",
            "product_name",
            "environment",
            "debug",
            "data_root",
            "state_backend",
            "worker_enabled",
            "strict_compatibility",
            "schema_auto_migrate",
            "fingerprint",
        )

        missing = tuple(
            attribute
            for attribute in required_attributes
            if not hasattr(configuration, attribute)
        )

        if missing:
            raise RuntimeEnvironmentConfigurationError(
                "Runtime configuration does not satisfy "
                "the required contract. Missing: "
                + ", ".join(missing)
            )

        if not callable(configuration.fingerprint):
            raise RuntimeEnvironmentConfigurationError(
                "Runtime configuration fingerprint must "
                "be callable."
            )
