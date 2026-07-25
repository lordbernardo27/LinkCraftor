from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import os
import py_compile
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any


BUILD_VERSION = "uri_phase_1_1_3_runtime_environment_v1"

PROJECT_ROOT = Path.cwd().resolve()

TARGET = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "runtime"
    / "runtime_environment.py"
)

CONFIGURATION_FILE = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "runtime"
    / "runtime_configuration.py"
)

KERNEL_FILE = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_runtime_kernel.py"
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
    / f"uri_phase1_1_3_runtime_environment_{TIMESTAMP}"
)

BACKUP_TARGET = (
    BACKUP_ROOT
    / "backend"
    / "server"
    / "runtime"
    / "runtime_environment.py"
)

EVIDENCE_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime"
    / "uri_phase_1"
    / "1_1_3_runtime_environment"
)

EVIDENCE_JSON = (
    EVIDENCE_ROOT
    / f"runtime_environment_build_{TIMESTAMP}.json"
)

EVIDENCE_TEXT = (
    EVIDENCE_ROOT
    / f"runtime_environment_build_{TIMESTAMP}.txt"
)


ENVIRONMENT_SOURCE = r'''from __future__ import annotations

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
'''


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None

    return sha256_bytes(path.read_bytes())


def fail(message: str) -> None:
    raise RuntimeError(message)


def load_module(
    path: Path,
    module_name: str,
) -> Any:
    spec = importlib.util.spec_from_file_location(
        module_name,
        path,
    )

    if spec is None or spec.loader is None:
        fail(
            f"Could not create an import specification "
            f"for {path}."
        )

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module

    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(module_name, None)
        raise

    return module


def unload_module(module_name: str) -> None:
    sys.modules.pop(module_name, None)


def verify_ast_contract(
    path: Path,
) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text, filename=str(path))

    classes: dict[str, set[str]] = {}

    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue

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

    required_classes = {
        "RuntimeEnvironmentName",
        "RuntimeEnvironmentCapability",
        "RuntimeEnvironmentPolicy",
        "RuntimeEnvironmentSnapshot",
        "RuntimeEnvironmentManager",
        "RuntimeEnvironmentError",
        "RuntimeEnvironmentConfigurationError",
        "RuntimeEnvironmentMismatchError",
        "RuntimeEnvironmentCapabilityError",
    }

    required_manager_methods = {
        "coerce_name",
        "coerce_capability",
        "policy_for",
        "available_policies",
        "validate_configuration",
        "capability_allowed",
        "require_capability",
        "ensure_expected_environment",
        "context",
        "snapshot",
        "_assert_configuration_contract",
    }

    missing_classes = sorted(
        required_classes - set(classes)
    )

    missing_methods = sorted(
        required_manager_methods
        - classes.get(
            "RuntimeEnvironmentManager",
            set(),
        )
    )

    if missing_classes:
        fail(
            "Runtime environment AST contract is "
            "missing classes: "
            + ", ".join(missing_classes)
        )

    if missing_methods:
        fail(
            "RuntimeEnvironmentManager is missing "
            "methods: "
            + ", ".join(missing_methods)
        )

    forbidden_business_terms = (
        "udare",
        "website_article_integrity",
        "article_validation",
        "semantic_intelligence",
        "uploaded_document_unified_content",
        "universal_unified_content_document",
    )

    source_lower = text.lower()

    detected_forbidden_terms = [
        term
        for term in forbidden_business_terms
        if term in source_lower
    ]

    if detected_forbidden_terms:
        fail(
            "Runtime environment management contains "
            "pipeline-specific business terms: "
            + ", ".join(detected_forbidden_terms)
        )

    return {
        "required_classes": sorted(
            required_classes
        ),
        "missing_classes": missing_classes,
        "required_manager_methods": sorted(
            required_manager_methods
        ),
        "missing_manager_methods": missing_methods,
        "pipeline_business_terms_detected": (
            detected_forbidden_terms
        ),
    }


def verify_behavior(
    environment_module: Any,
    configuration_module: Any,
    kernel_module: Any,
) -> dict[str, Any]:
    Loader = (
        configuration_module.RuntimeConfigurationLoader
    )

    Manager = (
        environment_module.RuntimeEnvironmentManager
    )

    EnvironmentName = (
        environment_module.RuntimeEnvironmentName
    )

    Capability = (
        environment_module.RuntimeEnvironmentCapability
    )

    ConfigurationError = (
        environment_module
        .RuntimeEnvironmentConfigurationError
    )

    MismatchError = (
        environment_module
        .RuntimeEnvironmentMismatchError
    )

    CapabilityError = (
        environment_module
        .RuntimeEnvironmentCapabilityError
    )

    Kernel = kernel_module.UniversalRuntimeKernel

    assertions: dict[str, str] = {}

    with tempfile.TemporaryDirectory(
        prefix="uri_runtime_environment_test_"
    ) as temporary_directory:
        temporary_root = Path(
            temporary_directory
        ).resolve()

        loader = Loader(
            project_root=temporary_root
        )

        configurations = {
            "development": loader.load(
                environ={},
                overrides={
                    "environment": "development",
                    "debug": True,
                    "state_backend": "memory",
                    "schema_auto_migrate": True,
                    "strict_compatibility": False,
                },
            ),
            "testing": loader.load(
                environ={},
                overrides={
                    "environment": "testing",
                    "debug": True,
                    "state_backend": "memory",
                    "schema_auto_migrate": True,
                    "strict_compatibility": False,
                },
            ),
            "staging": loader.load(
                environ={},
                overrides={
                    "environment": "staging",
                    "debug": False,
                    "state_backend": "filesystem",
                    "schema_auto_migrate": False,
                    "strict_compatibility": True,
                },
            ),
            "production": loader.load(
                environ={},
                overrides={
                    "environment": "production",
                    "debug": False,
                    "state_backend": "filesystem",
                    "schema_auto_migrate": False,
                    "strict_compatibility": True,
                },
            ),
        }

        managers = {
            name: Manager(configuration)
            for name, configuration
            in configurations.items()
        }

        if set(managers) != {
            "development",
            "testing",
            "staging",
            "production",
        }:
            fail(
                "Not all required runtime environments "
                "were resolved."
            )

        for name, manager in managers.items():
            if manager.name.value != name:
                fail(
                    f"Environment {name!r} resolved "
                    "incorrectly."
                )

        assertions[
            "four_environment_resolution"
        ] = "PASS"

        if managers["development"].is_production_like:
            fail(
                "Development was incorrectly classified "
                "as production-like."
            )

        if managers["testing"].is_production_like:
            fail(
                "Testing was incorrectly classified "
                "as production-like."
            )

        if not managers["staging"].is_production_like:
            fail(
                "Staging was not classified as "
                "production-like."
            )

        if not managers["production"].is_production_like:
            fail(
                "Production was not classified as "
                "production-like."
            )

        assertions[
            "production_like_classification"
        ] = "PASS"

        available_policies = Manager.available_policies()

        if set(available_policies) != {
            "development",
            "testing",
            "staging",
            "production",
        }:
            fail(
                "Available environment policies are "
                "incomplete."
            )

        policies_immutable = False

        try:
            available_policies["preview"] = object()
        except TypeError:
            policies_immutable = True

        if not policies_immutable:
            fail(
                "Environment-policy mapping was mutable."
            )

        assertions[
            "immutable_policy_registry"
        ] = "PASS"

        if not managers[
            "development"
        ].capability_allowed(Capability.DEBUG):
            fail(
                "Development debug capability was denied."
            )

        if managers[
            "production"
        ].capability_allowed(Capability.DEBUG):
            fail(
                "Production debug capability was allowed."
            )

        if managers[
            "staging"
        ].capability_allowed(
            Capability.MEMORY_STATE_BACKEND
        ):
            fail(
                "Staging memory state backend "
                "capability was allowed."
            )

        assertions[
            "capability_policy"
        ] = "PASS"

        managers["development"].require_capability(
            Capability.DEBUG
        )

        denied_capability = False

        try:
            managers["production"].require_capability(
                Capability.DEBUG
            )
        except CapabilityError:
            denied_capability = True

        if not denied_capability:
            fail(
                "A forbidden production capability "
                "was not rejected."
            )

        assertions[
            "capability_enforcement"
        ] = "PASS"

        managers["staging"].ensure_expected_environment(
            EnvironmentName.STAGING,
            EnvironmentName.PRODUCTION,
        )

        mismatch_rejected = False

        try:
            managers[
                "development"
            ].ensure_expected_environment(
                EnvironmentName.PRODUCTION
            )
        except MismatchError:
            mismatch_rejected = True

        if not mismatch_rejected:
            fail(
                "Deployment-environment mismatch "
                "was not rejected."
            )

        assertions[
            "environment_mismatch_detection"
        ] = "PASS"

        staging_debug_configuration = loader.load(
            environ={},
            overrides={
                "environment": "staging",
                "debug": True,
            },
        )

        staging_debug_rejected = False

        try:
            Manager(staging_debug_configuration)
        except ConfigurationError:
            staging_debug_rejected = True

        if not staging_debug_rejected:
            fail(
                "Staging debug mode was not rejected."
            )

        assertions[
            "staging_debug_protection"
        ] = "PASS"

        staging_memory_configuration = loader.load(
            environ={},
            overrides={
                "environment": "staging",
                "state_backend": "memory",
            },
        )

        staging_memory_rejected = False

        try:
            Manager(staging_memory_configuration)
        except ConfigurationError:
            staging_memory_rejected = True

        if not staging_memory_rejected:
            fail(
                "Staging memory state backend "
                "was not rejected."
            )

        assertions[
            "staging_state_backend_protection"
        ] = "PASS"

        staging_migration_configuration = loader.load(
            environ={},
            overrides={
                "environment": "staging",
                "schema_auto_migrate": True,
            },
        )

        staging_migration_rejected = False

        try:
            Manager(staging_migration_configuration)
        except ConfigurationError:
            staging_migration_rejected = True

        if not staging_migration_rejected:
            fail(
                "Staging automatic schema migration "
                "was not rejected."
            )

        assertions[
            "staging_migration_protection"
        ] = "PASS"

        staging_relaxed_configuration = loader.load(
            environ={},
            overrides={
                "environment": "staging",
                "strict_compatibility": False,
            },
        )

        staging_relaxed_rejected = False

        try:
            Manager(staging_relaxed_configuration)
        except ConfigurationError:
            staging_relaxed_rejected = True

        if not staging_relaxed_rejected:
            fail(
                "Staging relaxed compatibility "
                "was not rejected."
            )

        assertions[
            "staging_compatibility_protection"
        ] = "PASS"

        default_configuration = loader.load(
            environ={}
        )

        invalid_environment_object = SimpleNamespace(
            runtime_id=default_configuration.runtime_id,
            product_name=default_configuration.product_name,
            environment="preview",
            debug=default_configuration.debug,
            data_root=default_configuration.data_root,
            state_backend=default_configuration.state_backend,
            worker_enabled=default_configuration.worker_enabled,
            strict_compatibility=(
                default_configuration.strict_compatibility
            ),
            schema_auto_migrate=(
                default_configuration.schema_auto_migrate
            ),
            fingerprint=default_configuration.fingerprint,
        )

        unknown_environment_rejected = False

        try:
            Manager(invalid_environment_object)
        except ConfigurationError:
            unknown_environment_rejected = True

        if not unknown_environment_rejected:
            fail(
                "Unknown runtime environment "
                "was not rejected."
            )

        assertions[
            "unknown_environment_rejection"
        ] = "PASS"

        incomplete_configuration = SimpleNamespace(
            environment="development"
        )

        incomplete_contract_rejected = False

        try:
            Manager(incomplete_configuration)
        except ConfigurationError:
            incomplete_contract_rejected = True

        if not incomplete_contract_rejected:
            fail(
                "Incomplete configuration contract "
                "was not rejected."
            )

        assertions[
            "configuration_contract_validation"
        ] = "PASS"

        production_manager = managers["production"]
        context = production_manager.context()

        if context["environment"] != "production":
            fail(
                "Environment context is incorrect."
            )

        context_immutable = False

        try:
            context["environment"] = "development"
        except TypeError:
            context_immutable = True

        if not context_immutable:
            fail(
                "Environment context was mutable."
            )

        assertions[
            "immutable_environment_context"
        ] = "PASS"

        snapshot = production_manager.snapshot()

        if snapshot.name is not EnvironmentName.PRODUCTION:
            fail(
                "Environment snapshot name is incorrect."
            )

        if not snapshot.production_like:
            fail(
                "Environment snapshot lost "
                "production-like classification."
            )

        if (
            snapshot.configuration_fingerprint
            != configurations[
                "production"
            ].fingerprint()
        ):
            fail(
                "Environment snapshot configuration "
                "fingerprint is incorrect."
            )

        snapshot_immutable = False

        try:
            snapshot.worker_enabled = False
        except (AttributeError, TypeError):
            snapshot_immutable = True

        if not snapshot_immutable:
            fail(
                "Environment snapshot was mutable."
            )

        assertions[
            "immutable_environment_snapshot"
        ] = "PASS"

        original_process_environment = dict(
            os.environ
        )

        Manager(
            configurations["development"]
        ).snapshot()

        if dict(os.environ) != original_process_environment:
            fail(
                "Environment management mutated "
                "os.environ."
            )

        assertions[
            "process_environment_non_mutation"
        ] = "PASS"

        kernel = Kernel(
            runtime_id=(
                configurations[
                    "production"
                ].runtime_id
            ),
            product_name=(
                configurations[
                    "production"
                ].product_name
            ),
        )

        kernel.bind_component(
            "configuration",
            configurations["production"],
        )

        environment_binding = kernel.bind_component(
            "environment",
            production_manager,
        )

        if environment_binding.key != "environment":
            fail(
                "Kernel environment binding failed."
            )

        retrieved = kernel.get_component(
            "environment",
            Manager,
        )

        if retrieved is not production_manager:
            fail(
                "Kernel returned the wrong "
                "environment manager."
            )

        missing_foundation = set(
            kernel.missing_foundation_components()
        )

        if "configuration" in missing_foundation:
            fail(
                "Kernel reported configuration as missing."
            )

        if "environment" in missing_foundation:
            fail(
                "Kernel reported environment as missing."
            )

        assertions[
            "kernel_environment_binding"
        ] = "PASS"

        return {
            "assertions": assertions,
            "available_environments": sorted(
                available_policies
            ),
            "production_context": dict(context),
            "production_snapshot": {
                "name": snapshot.name.value,
                "production_like": (
                    snapshot.production_like
                ),
                "runtime_id": snapshot.runtime_id,
                "state_backend": (
                    snapshot.state_backend
                ),
                "worker_enabled": (
                    snapshot.worker_enabled
                ),
                "configuration_fingerprint": (
                    snapshot.configuration_fingerprint
                ),
            },
            "kernel_generation": kernel.generation,
            "kernel_missing_foundation_components": (
                sorted(missing_foundation)
            ),
        }


def rollback(
    *,
    target_existed: bool,
) -> None:
    if target_existed:
        if not BACKUP_TARGET.exists():
            raise RuntimeError(
                "Runtime environment rollback "
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
    print("1.1.3 — RUNTIME ENVIRONMENT MANAGEMENT BUILD")
    print("=" * 78)
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Target:       {TARGET}")
    print()

    required_files = [
        CONFIGURATION_FILE,
        KERNEL_FILE,
        EXISTING_RUNTIME_FACADE,
        MAIN_FILE,
    ]

    missing_required_files = [
        path
        for path in required_files
        if not path.exists()
    ]

    if missing_required_files:
        fail(
            "Required files are missing:\n"
            + "\n".join(
                str(path)
                for path in missing_required_files
            )
        )

    target_existed = TARGET.exists()
    target_original_hash = sha256_file(TARGET)

    protected_hashes_before = {
        "configuration": sha256_file(
            CONFIGURATION_FILE
        ),
        "kernel": sha256_file(KERNEL_FILE),
        "runtime_facade": sha256_file(
            EXISTING_RUNTIME_FACADE
        ),
        "main": sha256_file(MAIN_FILE),
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
            "Existing runtime environment file "
            "backed up:"
        )
        print(BACKUP_TARGET)
        print()

    TARGET.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    environment_module_name = (
        "_uri_phase_1_1_3_runtime_environment_test"
    )

    configuration_module_name = (
        "_uri_phase_1_1_3_runtime_configuration_test"
    )

    kernel_module_name = (
        "_uri_phase_1_1_3_runtime_kernel_test"
    )

    try:
        TARGET.write_text(
            ENVIRONMENT_SOURCE,
            encoding="utf-8",
            newline="\n",
        )

        py_compile.compile(
            str(TARGET),
            doraise=True,
        )

        py_compile.compile(
            str(CONFIGURATION_FILE),
            doraise=True,
        )

        py_compile.compile(
            str(KERNEL_FILE),
            doraise=True,
        )

        py_compile.compile(
            str(MAIN_FILE),
            doraise=True,
        )

        ast_contract = verify_ast_contract(
            TARGET
        )

        environment_module = load_module(
            TARGET,
            environment_module_name,
        )

        configuration_module = load_module(
            CONFIGURATION_FILE,
            configuration_module_name,
        )

        kernel_module = load_module(
            KERNEL_FILE,
            kernel_module_name,
        )

        behavioral_results = verify_behavior(
            environment_module,
            configuration_module,
            kernel_module,
        )

        protected_hashes_after = {
            "configuration": sha256_file(
                CONFIGURATION_FILE
            ),
            "kernel": sha256_file(KERNEL_FILE),
            "runtime_facade": sha256_file(
                EXISTING_RUNTIME_FACADE
            ),
            "main": sha256_file(MAIN_FILE),
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
            "Runtime environment verification failed. "
            "The previous filesystem state was restored."
        )
        raise

    finally:
        unload_module(environment_module_name)
        unload_module(configuration_module_name)
        unload_module(kernel_module_name)

    target_final_hash = sha256_file(TARGET)

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
            "environment_py_compile": "PASS",
            "configuration_py_compile": "PASS",
            "kernel_py_compile": "PASS",
            "main_py_compile": "PASS",
            "ast_contract": "PASS",
            "behavioral_contract": "PASS",
            "four_environment_contract": "PASS",
            "policy_enforcement": "PASS",
            "deployment_mismatch_detection": "PASS",
            "immutability_contract": "PASS",
            "kernel_binding_contract": "PASS",
            "business_logic_agnostic_test": "PASS",
            "protected_files_unchanged": "PASS",
            "automatic_rollback_required": False,
        },
        "ast_contract_details": ast_contract,
        "behavioral_results": behavioral_results,
        "phase_status": {
            "phase": "1",
            "item": "1.1.3",
            "name": "Runtime Environment Management",
            "implementation_status": "IMPLEMENTED",
            "verification_status": "PASS",
            "kernel_binding_status": "PASS",
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
        "1.1.3 — RUNTIME ENVIRONMENT MANAGEMENT EVIDENCE",
        "=" * 78,
        "",
        f"Build version: {BUILD_VERSION}",
        f"Timestamp UTC: {evidence['timestamp_utc']}",
        f"Target: {TARGET}",
        "",
        "VERIFICATION",
        "-" * 78,
        "Runtime environment compilation: PASS",
        "Runtime configuration compilation: PASS",
        "Universal Runtime Kernel compilation: PASS",
        "main.py compilation: PASS",
        "Environment AST contract: PASS",
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
            "SUPPORTED ENVIRONMENTS",
            "-" * 78,
        ]
    )

    for environment_name in behavioral_results[
        "available_environments"
    ]:
        evidence_lines.append(
            environment_name
        )

    evidence_lines.extend(
        [
            "",
            "KERNEL INTEGRATION",
            "-" * 78,
            "Configuration kernel binding: PASS",
            "Environment kernel binding: PASS",
            (
                "Kernel generation after bindings: "
                f"{behavioral_results['kernel_generation']}"
            ),
            "",
            "CHECKLIST POSITION",
            "-" * 78,
            "1.1.1 kernel implementation: PASS",
            (
                "1.1.1 environment-binding "
                "compatibility: PASS"
            ),
            "1.1.1 full runtime integration: PENDING",
            "1.1.2 configuration implementation: PASS",
            "1.1.2 kernel binding: PASS",
            (
                "1.1.2 application boot integration: "
                "PENDING"
            ),
            "1.1.3 implementation: PASS",
            "1.1.3 isolated verification: PASS",
            "1.1.3 kernel binding: PASS",
            (
                "1.1.3 application boot integration: "
                "PENDING"
            ),
            "1.1.3 certification: NOT CERTIFIED",
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
        "Runtime environment compilation:       PASS"
    )
    print(
        "Runtime configuration compilation:     PASS"
    )
    print(
        "Universal Runtime Kernel compilation:  PASS"
    )
    print(
        "main.py compilation:                   PASS"
    )
    print(
        "Environment AST contract:              PASS"
    )
    print(
        "Environment behavioral contract:       PASS"
    )
    print(
        "Four-environment policy contract:      PASS"
    )
    print(
        "Environment safety enforcement:        PASS"
    )
    print(
        "Deployment mismatch detection:         PASS"
    )
    print(
        "Immutable context and snapshot:        PASS"
    )
    print(
        "Kernel environment binding:            PASS"
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
    print(f"Environment:   {TARGET}")
    print(f"Evidence JSON: {EVIDENCE_JSON}")
    print(f"Evidence text: {EVIDENCE_TEXT}")
    print()

    print("1.1.3 RUNTIME ENVIRONMENT MANAGEMENT")
    print("IMPLEMENTATION: PASS")
    print("ISOLATED VERIFICATION: PASS")
    print("KERNEL BINDING: PASS")
    print("APPLICATION BOOT INTEGRATION: PENDING")
    print("CERTIFICATION: NOT CERTIFIED")
    print()
    print("NO PRODUCTION DATA WAS MODIFIED")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
