from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import os
import py_compile
import shutil
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BUILD_VERSION = "uri_phase_1_1_8_runtime_versioning_v1"

PROJECT_ROOT = Path.cwd().resolve()

TARGET = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "runtime"
    / "runtime_versioning.py"
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
    / f"uri_phase1_1_8_runtime_versioning_{TIMESTAMP}"
)

BACKUP_TARGET = (
    BACKUP_ROOT
    / "backend"
    / "server"
    / "runtime"
    / "runtime_versioning.py"
)

EVIDENCE_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime"
    / "uri_phase_1"
    / "1_1_8_runtime_versioning"
)

EVIDENCE_JSON = (
    EVIDENCE_ROOT
    / f"runtime_versioning_build_{TIMESTAMP}.json"
)

EVIDENCE_TEXT = (
    EVIDENCE_ROOT
    / f"runtime_versioning_build_{TIMESTAMP}.txt"
)


VERSIONING_SOURCE = r'''from __future__ import annotations

"""
Universal Runtime Versioning.

This module defines immutable version identifiers and manifests for the
Universal Runtime Infrastructure.

It records versions. It does not decide whether two versions are
compatible; compatibility policy belongs to the Runtime Compatibility
Layer.
"""

import hashlib
import json
import re
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping


__all__ = [
    "DEFAULT_CONFIGURATION_SCHEMA_VERSION",
    "DEFAULT_JOB_CONTRACT_VERSION",
    "DEFAULT_KERNEL_API_VERSION",
    "DEFAULT_RUNTIME_VERSION",
    "DEFAULT_SERVICE_CONTRACT_VERSION",
    "DEFAULT_STATE_SCHEMA_VERSION",
    "RUNTIME_VERSION_MANIFEST_SCHEMA_VERSION",
    "RuntimeComponentVersion",
    "RuntimeReleaseChannel",
    "RuntimeSemanticVersion",
    "RuntimeVersionError",
    "RuntimeVersionManifest",
    "RuntimeVersionManager",
    "RuntimeVersionMissingError",
    "RuntimeVersionRegistrationError",
    "RuntimeVersionSnapshot",
    "RuntimeVersionStateError",
    "RuntimeVersionValidationError",
    "create_default_runtime_version_manager",
]


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


RUNTIME_VERSION_MANIFEST_SCHEMA_VERSION = "1.0.0"

DEFAULT_RUNTIME_VERSION = "0.1.0"
DEFAULT_KERNEL_API_VERSION = "0.1.0"
DEFAULT_SERVICE_CONTRACT_VERSION = "0.1.0"
DEFAULT_JOB_CONTRACT_VERSION = "0.1.0"
DEFAULT_STATE_SCHEMA_VERSION = "0.1.0"
DEFAULT_CONFIGURATION_SCHEMA_VERSION = "1.0.0"


_SEMVER_PATTERN = re.compile(
    r"^(?P<major>0|[1-9][0-9]*)"
    r"\.(?P<minor>0|[1-9][0-9]*)"
    r"\.(?P<patch>0|[1-9][0-9]*)"
    r"(?:-(?P<prerelease>"
    r"(?:0|[1-9][0-9]*|[0-9A-Za-z-]*[A-Za-z-][0-9A-Za-z-]*)"
    r"(?:\.(?:0|[1-9][0-9]*|[0-9A-Za-z-]*[A-Za-z-][0-9A-Za-z-]*))*"
    r"))?"
    r"(?:\+(?P<build>"
    r"[0-9A-Za-z-]+"
    r"(?:\.[0-9A-Za-z-]+)*"
    r"))?$"
)

_COMPONENT_KEY_PATTERN = re.compile(
    r"^[a-z][a-z0-9_.-]{1,127}$"
)

_CONTRACT_KEY_PATTERN = re.compile(
    r"^[a-z][a-z0-9_.:-]{1,127}$"
)

_BUILD_ID_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$"
)

_METADATA_KEY_PATTERN = re.compile(
    r"^[A-Za-z][A-Za-z0-9_.:-]{0,127}$"
)


class RuntimeVersionError(RuntimeError):
    """Base runtime-versioning failure."""


class RuntimeVersionValidationError(
    RuntimeVersionError
):
    """Raised when a version or manifest is invalid."""


class RuntimeVersionRegistrationError(
    RuntimeVersionError
):
    """Raised when component-version registration is invalid."""


class RuntimeVersionMissingError(
    RuntimeVersionError
):
    """Raised when a component version is unavailable."""


class RuntimeVersionStateError(
    RuntimeVersionError
):
    """Raised when a sealed version manager is mutated."""


class RuntimeReleaseChannel(str, Enum):
    DEVELOPMENT = "development"
    ALPHA = "alpha"
    BETA = "beta"
    RELEASE_CANDIDATE = "release_candidate"
    STABLE = "stable"


@dataclass(frozen=True, slots=True)
class RuntimeSemanticVersion:
    """
    Strict Semantic Versioning 2.0.0 identifier.

    Build metadata is retained as identity information but does not
    influence precedence comparison.
    """

    major: int
    minor: int
    patch: int
    prerelease: tuple[str, ...] = ()
    build: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for field_name in (
            "major",
            "minor",
            "patch",
        ):
            value = getattr(self, field_name)

            if isinstance(value, bool) or value < 0:
                raise RuntimeVersionValidationError(
                    f"{field_name} must be a non-negative integer."
                )

        for identifier in self.prerelease:
            if not identifier:
                raise RuntimeVersionValidationError(
                    "Prerelease identifiers must not be empty."
                )

            if (
                identifier.isdigit()
                and len(identifier) > 1
                and identifier.startswith("0")
            ):
                raise RuntimeVersionValidationError(
                    "Numeric prerelease identifiers must not "
                    "contain leading zeroes."
                )

        for identifier in self.build:
            if not identifier:
                raise RuntimeVersionValidationError(
                    "Build identifiers must not be empty."
                )

    @classmethod
    def parse(
        cls,
        value: "RuntimeSemanticVersion | str",
    ) -> "RuntimeSemanticVersion":
        if isinstance(value, cls):
            return value

        normalized = str(value or "").strip()
        match = _SEMVER_PATTERN.fullmatch(normalized)

        if match is None:
            raise RuntimeVersionValidationError(
                f"Invalid Semantic Version: {value!r}"
            )

        prerelease_text = match.group("prerelease")
        build_text = match.group("build")

        return cls(
            major=int(match.group("major")),
            minor=int(match.group("minor")),
            patch=int(match.group("patch")),
            prerelease=(
                ()
                if prerelease_text is None
                else tuple(prerelease_text.split("."))
            ),
            build=(
                ()
                if build_text is None
                else tuple(build_text.split("."))
            ),
        )

    def __str__(self) -> str:
        value = (
            f"{self.major}."
            f"{self.minor}."
            f"{self.patch}"
        )

        if self.prerelease:
            value += "-" + ".".join(self.prerelease)

        if self.build:
            value += "+" + ".".join(self.build)

        return value

    def compare_precedence(
        self,
        other: "RuntimeSemanticVersion | str",
    ) -> int:
        """
        Compare Semantic Version precedence.

        Returns:
        -1 when self has lower precedence
         0 when precedence is equal
         1 when self has higher precedence
        """

        resolved = self.parse(other)

        self_core = (
            self.major,
            self.minor,
            self.patch,
        )

        other_core = (
            resolved.major,
            resolved.minor,
            resolved.patch,
        )

        if self_core < other_core:
            return -1

        if self_core > other_core:
            return 1

        if not self.prerelease and not resolved.prerelease:
            return 0

        if not self.prerelease:
            return 1

        if not resolved.prerelease:
            return -1

        for left, right in zip(
            self.prerelease,
            resolved.prerelease,
        ):
            if left == right:
                continue

            left_numeric = left.isdigit()
            right_numeric = right.isdigit()

            if left_numeric and right_numeric:
                left_number = int(left)
                right_number = int(right)

                return (
                    -1
                    if left_number < right_number
                    else 1
                )

            if left_numeric and not right_numeric:
                return -1

            if not left_numeric and right_numeric:
                return 1

            return -1 if left < right else 1

        if len(self.prerelease) < len(
            resolved.prerelease
        ):
            return -1

        if len(self.prerelease) > len(
            resolved.prerelease
        ):
            return 1

        return 0

    def same_precedence(
        self,
        other: "RuntimeSemanticVersion | str",
    ) -> bool:
        return self.compare_precedence(other) == 0


@dataclass(frozen=True, slots=True)
class RuntimeVersionManifest:
    """Immutable runtime foundation version manifest."""

    manifest_schema_version: RuntimeSemanticVersion
    runtime_name: str
    runtime_version: RuntimeSemanticVersion
    kernel_api_version: RuntimeSemanticVersion
    service_contract_version: RuntimeSemanticVersion
    job_contract_version: RuntimeSemanticVersion
    state_schema_version: RuntimeSemanticVersion
    configuration_schema_version: RuntimeSemanticVersion
    release_channel: RuntimeReleaseChannel
    created_at: datetime
    build_id: str | None
    metadata: Mapping[str, str]

    def __post_init__(self) -> None:
        runtime_name = str(
            self.runtime_name or ""
        ).strip()

        if not runtime_name:
            raise RuntimeVersionValidationError(
                "runtime_name must not be empty."
            )

        if len(runtime_name) > 128:
            raise RuntimeVersionValidationError(
                "runtime_name must not exceed 128 characters."
            )

        if (
            self.build_id is not None
            and not _BUILD_ID_PATTERN.fullmatch(
                self.build_id
            )
        ):
            raise RuntimeVersionValidationError(
                "build_id contains invalid characters."
            )

        if self.created_at.tzinfo is None:
            raise RuntimeVersionValidationError(
                "created_at must be timezone-aware."
            )

        normalized_metadata: dict[str, str] = {}

        for raw_key, raw_value in self.metadata.items():
            key = str(raw_key or "").strip()
            value = str(raw_value or "").strip()

            if not _METADATA_KEY_PATTERN.fullmatch(key):
                raise RuntimeVersionValidationError(
                    f"Invalid metadata key: {raw_key!r}"
                )

            if len(value) > 1024:
                raise RuntimeVersionValidationError(
                    f"Metadata value for {key!r} exceeds "
                    "1024 characters."
                )

            normalized_metadata[key] = value

        object.__setattr__(
            self,
            "runtime_name",
            runtime_name,
        )

        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(normalized_metadata),
        )

    def to_dict(
        self,
        *,
        include_created_at: bool = True,
    ) -> dict[str, Any]:
        result: dict[str, Any] = {
            "manifest_schema_version": str(
                self.manifest_schema_version
            ),
            "runtime_name": self.runtime_name,
            "runtime_version": str(
                self.runtime_version
            ),
            "kernel_api_version": str(
                self.kernel_api_version
            ),
            "service_contract_version": str(
                self.service_contract_version
            ),
            "job_contract_version": str(
                self.job_contract_version
            ),
            "state_schema_version": str(
                self.state_schema_version
            ),
            "configuration_schema_version": str(
                self.configuration_schema_version
            ),
            "release_channel": (
                self.release_channel.value
            ),
            "build_id": self.build_id,
            "metadata": dict(self.metadata),
        }

        if include_created_at:
            result["created_at"] = (
                self.created_at.isoformat()
            )

        return result

    def fingerprint(self) -> str:
        """
        Return a deterministic effective-version fingerprint.

        created_at is excluded because it does not change the effective
        version contract.
        """

        payload = json.dumps(
            self.to_dict(
                include_created_at=False
            ),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")

        return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True, slots=True)
class RuntimeComponentVersion:
    """Immutable version registration for one runtime component."""

    component_key: str
    version: RuntimeSemanticVersion
    contract: str
    registered_at: datetime
    generation: int


@dataclass(frozen=True, slots=True)
class RuntimeVersionSnapshot:
    """Immutable point-in-time version-manager snapshot."""

    sealed: bool
    generation: int
    component_count: int
    manifest_fingerprint: str
    version_graph_fingerprint: str
    manifest: RuntimeVersionManifest
    components: tuple[RuntimeComponentVersion, ...]


class RuntimeVersionManager:
    """
    Thread-safe version manifest and component-version registry.

    This class records exact versions. It deliberately does not make
    compatibility decisions.
    """

    __slots__ = (
        "_manifest",
        "_components",
        "_generation",
        "_sealed",
        "_lock",
    )

    def __init__(
        self,
        manifest: RuntimeVersionManifest,
    ) -> None:
        if not isinstance(
            manifest,
            RuntimeVersionManifest,
        ):
            raise RuntimeVersionValidationError(
                "A RuntimeVersionManifest is required."
            )

        self._manifest = manifest
        self._components: dict[
            str,
            RuntimeComponentVersion,
        ] = {}
        self._generation = 0
        self._sealed = False
        self._lock = threading.RLock()

    @staticmethod
    def normalize_component_key(
        component_key: str,
    ) -> str:
        key = str(component_key or "").strip().lower()

        if not _COMPONENT_KEY_PATTERN.fullmatch(key):
            raise RuntimeVersionRegistrationError(
                "component_key must be 2-128 characters, "
                "begin with a lowercase letter, and contain "
                "only lowercase letters, numbers, dots, "
                "underscores, or hyphens."
            )

        return key

    @staticmethod
    def normalize_contract(
        contract: str,
    ) -> str:
        normalized = str(contract or "").strip().lower()

        if not _CONTRACT_KEY_PATTERN.fullmatch(
            normalized
        ):
            raise RuntimeVersionRegistrationError(
                "contract must be 2-128 characters, begin "
                "with a lowercase letter, and contain only "
                "lowercase letters, numbers, dots, "
                "underscores, colons, or hyphens."
            )

        return normalized

    @property
    def manifest(
        self,
    ) -> RuntimeVersionManifest:
        return self._manifest

    @property
    def sealed(self) -> bool:
        with self._lock:
            return self._sealed

    @property
    def generation(self) -> int:
        with self._lock:
            return self._generation

    @property
    def component_count(self) -> int:
        with self._lock:
            return len(self._components)

    def _assert_mutable(self) -> None:
        if self._sealed:
            raise RuntimeVersionStateError(
                "The runtime version manager is sealed."
            )

    def _record_mutation(self) -> int:
        self._generation += 1
        return self._generation

    def register_component(
        self,
        component_key: str,
        version: RuntimeSemanticVersion | str,
        *,
        contract: str = "implementation",
        replace: bool = False,
    ) -> RuntimeComponentVersion:
        key = self.normalize_component_key(
            component_key
        )

        resolved_version = (
            RuntimeSemanticVersion.parse(version)
        )

        resolved_contract = self.normalize_contract(
            contract
        )

        with self._lock:
            self._assert_mutable()

            if key in self._components and not replace:
                raise RuntimeVersionRegistrationError(
                    f"Runtime component {key!r} already "
                    "has a registered version."
                )

            generation = self._record_mutation()

            registration = RuntimeComponentVersion(
                component_key=key,
                version=resolved_version,
                contract=resolved_contract,
                registered_at=_utc_now(),
                generation=generation,
            )

            self._components[key] = registration

            return registration

    def has_component(
        self,
        component_key: str,
    ) -> bool:
        key = self.normalize_component_key(
            component_key
        )

        with self._lock:
            return key in self._components

    def get_component_version(
        self,
        component_key: str,
    ) -> RuntimeComponentVersion:
        key = self.normalize_component_key(
            component_key
        )

        with self._lock:
            try:
                return self._components[key]
            except KeyError as exc:
                raise RuntimeVersionMissingError(
                    f"No version is registered for "
                    f"runtime component {key!r}."
                ) from exc

    def components_for_contract(
        self,
        contract: str,
    ) -> tuple[RuntimeComponentVersion, ...]:
        resolved_contract = self.normalize_contract(
            contract
        )

        with self._lock:
            return tuple(
                self._components[key]
                for key in sorted(self._components)
                if (
                    self._components[key].contract
                    == resolved_contract
                )
            )

    def version_graph_fingerprint(
        self,
    ) -> str:
        with self._lock:
            components = [
                {
                    "component_key": registration.component_key,
                    "version": str(registration.version),
                    "contract": registration.contract,
                }
                for registration in (
                    self._components[key]
                    for key in sorted(self._components)
                )
            ]

        payload = json.dumps(
            {
                "manifest_fingerprint": (
                    self._manifest.fingerprint()
                ),
                "components": components,
            },
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")

        return hashlib.sha256(payload).hexdigest()

    def seal(
        self,
    ) -> RuntimeVersionSnapshot:
        with self._lock:
            self._sealed = True
            self._record_mutation()

        return self.snapshot()

    def snapshot(
        self,
    ) -> RuntimeVersionSnapshot:
        with self._lock:
            components = tuple(
                self._components[key]
                for key in sorted(self._components)
            )

            return RuntimeVersionSnapshot(
                sealed=self._sealed,
                generation=self._generation,
                component_count=len(self._components),
                manifest_fingerprint=(
                    self._manifest.fingerprint()
                ),
                version_graph_fingerprint=(
                    self.version_graph_fingerprint()
                ),
                manifest=self._manifest,
                components=components,
            )


def create_default_runtime_version_manager(
    *,
    runtime_name: str = "Universal Runtime",
    runtime_version: RuntimeSemanticVersion | str = (
        DEFAULT_RUNTIME_VERSION
    ),
    kernel_api_version: RuntimeSemanticVersion | str = (
        DEFAULT_KERNEL_API_VERSION
    ),
    service_contract_version: (
        RuntimeSemanticVersion | str
    ) = DEFAULT_SERVICE_CONTRACT_VERSION,
    job_contract_version: (
        RuntimeSemanticVersion | str
    ) = DEFAULT_JOB_CONTRACT_VERSION,
    state_schema_version: (
        RuntimeSemanticVersion | str
    ) = DEFAULT_STATE_SCHEMA_VERSION,
    configuration_schema_version: (
        RuntimeSemanticVersion | str
    ) = DEFAULT_CONFIGURATION_SCHEMA_VERSION,
    release_channel: RuntimeReleaseChannel | str = (
        RuntimeReleaseChannel.DEVELOPMENT
    ),
    build_id: str | None = None,
    metadata: Mapping[str, str] | None = None,
) -> RuntimeVersionManager:
    """Create the initial Universal Runtime version manager."""

    if isinstance(
        release_channel,
        RuntimeReleaseChannel,
    ):
        resolved_channel = release_channel
    else:
        try:
            resolved_channel = RuntimeReleaseChannel(
                str(release_channel or "").strip().lower()
            )
        except ValueError as exc:
            raise RuntimeVersionValidationError(
                f"Unknown release channel: "
                f"{release_channel!r}"
            ) from exc

    manifest = RuntimeVersionManifest(
        manifest_schema_version=(
            RuntimeSemanticVersion.parse(
                RUNTIME_VERSION_MANIFEST_SCHEMA_VERSION
            )
        ),
        runtime_name=runtime_name,
        runtime_version=(
            RuntimeSemanticVersion.parse(
                runtime_version
            )
        ),
        kernel_api_version=(
            RuntimeSemanticVersion.parse(
                kernel_api_version
            )
        ),
        service_contract_version=(
            RuntimeSemanticVersion.parse(
                service_contract_version
            )
        ),
        job_contract_version=(
            RuntimeSemanticVersion.parse(
                job_contract_version
            )
        ),
        state_schema_version=(
            RuntimeSemanticVersion.parse(
                state_schema_version
            )
        ),
        configuration_schema_version=(
            RuntimeSemanticVersion.parse(
                configuration_schema_version
            )
        ),
        release_channel=resolved_channel,
        created_at=_utc_now(),
        build_id=build_id,
        metadata=MappingProxyType(
            dict(metadata or {})
        ),
    )

    return RuntimeVersionManager(manifest)
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


def unload_module(
    module_name: str,
) -> None:
    sys.modules.pop(module_name, None)


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
        "RuntimeSemanticVersion",
        "RuntimeVersionManifest",
        "RuntimeComponentVersion",
        "RuntimeVersionSnapshot",
        "RuntimeVersionManager",
        "RuntimeReleaseChannel",
        "RuntimeVersionError",
        "RuntimeVersionValidationError",
        "RuntimeVersionRegistrationError",
        "RuntimeVersionMissingError",
        "RuntimeVersionStateError",
    }

    required_semver_methods = {
        "parse",
        "compare_precedence",
        "same_precedence",
        "__str__",
    }

    required_manager_methods = {
        "normalize_component_key",
        "normalize_contract",
        "register_component",
        "has_component",
        "get_component_version",
        "components_for_contract",
        "version_graph_fingerprint",
        "seal",
        "snapshot",
    }

    missing_classes = sorted(
        required_classes - set(classes)
    )

    missing_semver_methods = sorted(
        required_semver_methods
        - classes.get(
            "RuntimeSemanticVersion",
            set(),
        )
    )

    missing_manager_methods = sorted(
        required_manager_methods
        - classes.get(
            "RuntimeVersionManager",
            set(),
        )
    )

    if missing_classes:
        fail(
            "Runtime versioning AST contract is "
            "missing classes: "
            + ", ".join(missing_classes)
        )

    if missing_semver_methods:
        fail(
            "RuntimeSemanticVersion is missing methods: "
            + ", ".join(missing_semver_methods)
        )

    if missing_manager_methods:
        fail(
            "RuntimeVersionManager is missing methods: "
            + ", ".join(missing_manager_methods)
        )

    if (
        "create_default_runtime_version_manager"
        not in functions
    ):
        fail(
            "The default runtime-version-manager "
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
            "Runtime versioning contains "
            "pipeline-specific business terms: "
            + ", ".join(detected_forbidden_terms)
        )

    if "asyncio.create_task" in text:
        fail(
            "Runtime versioning must not create "
            "detached tasks."
        )

    if "@app.on_event" in text:
        fail(
            "Runtime versioning must not wire itself "
            "into the application."
        )

    return {
        "required_classes": sorted(
            required_classes
        ),
        "missing_classes": missing_classes,
        "missing_semver_methods": (
            missing_semver_methods
        ),
        "missing_manager_methods": (
            missing_manager_methods
        ),
        "default_factory_present": True,
        "pipeline_business_terms_detected": (
            detected_forbidden_terms
        ),
        "detached_task_creation_detected": False,
        "application_hook_detected": False,
    }


def verify_behavior(
    versioning_module: Any,
    kernel_module: Any,
    registry_module: Any,
) -> dict[str, Any]:
    SemanticVersion = (
        versioning_module.RuntimeSemanticVersion
    )

    VersionManager = (
        versioning_module.RuntimeVersionManager
    )

    ValidationError = (
        versioning_module
        .RuntimeVersionValidationError
    )

    RegistrationError = (
        versioning_module
        .RuntimeVersionRegistrationError
    )

    MissingError = (
        versioning_module.RuntimeVersionMissingError
    )

    StateError = (
        versioning_module.RuntimeVersionStateError
    )

    Kernel = kernel_module.UniversalRuntimeKernel
    Registry = registry_module.RuntimeServiceRegistry

    assertions: dict[str, str] = {}

    simple = SemanticVersion.parse("1.2.3")

    if str(simple) != "1.2.3":
        fail(
            "Simple Semantic Version parsing failed."
        )

    complex_version = SemanticVersion.parse(
        "2.4.6-alpha.1+build.7"
    )

    if (
        str(complex_version)
        != "2.4.6-alpha.1+build.7"
    ):
        fail(
            "Complex Semantic Version parsing failed."
        )

    assertions[
        "semantic_version_parsing"
    ] = "PASS"

    invalid_versions = (
        "1.2",
        "1.02.3",
        "v1.2.3",
        "1.2.3-01",
        "1.2.3+",
        "",
    )

    for invalid_version in invalid_versions:
        rejected = False

        try:
            SemanticVersion.parse(
                invalid_version
            )
        except ValidationError:
            rejected = True

        if not rejected:
            fail(
                "Invalid Semantic Version was accepted: "
                f"{invalid_version!r}"
            )

    assertions[
        "invalid_version_rejection"
    ] = "PASS"

    precedence_pairs = (
        ("1.0.0-alpha", "1.0.0-alpha.1"),
        ("1.0.0-alpha.1", "1.0.0-alpha.beta"),
        ("1.0.0-beta", "1.0.0-beta.2"),
        ("1.0.0-beta.2", "1.0.0-beta.11"),
        ("1.0.0-rc.1", "1.0.0"),
        ("1.9.9", "2.0.0"),
    )

    for lower, higher in precedence_pairs:
        if (
            SemanticVersion.parse(
                lower
            ).compare_precedence(higher)
            != -1
        ):
            fail(
                "Semantic Version precedence failed: "
                f"{lower!r} < {higher!r}"
            )

    if not SemanticVersion.parse(
        "1.0.0+build.1"
    ).same_precedence(
        "1.0.0+build.2"
    ):
        fail(
            "Build metadata incorrectly changed "
            "Semantic Version precedence."
        )

    assertions[
        "semantic_version_precedence"
    ] = "PASS"

    manager = (
        versioning_module
        .create_default_runtime_version_manager(
            runtime_name=(
                "LinkCraftor Universal Runtime"
            ),
            runtime_version="0.1.0",
            release_channel="development",
            build_id="local.1",
            metadata={
                "source": "phase_1_build",
            },
        )
    )

    manifest = manager.manifest

    if (
        str(manifest.runtime_version)
        != "0.1.0"
    ):
        fail(
            "Default runtime version is incorrect."
        )

    if (
        manifest.release_channel.value
        != "development"
    ):
        fail(
            "Release channel resolution failed."
        )

    if len(manifest.fingerprint()) != 64:
        fail(
            "Manifest fingerprint is invalid."
        )

    assertions[
        "version_manifest_creation"
    ] = "PASS"

    manifest_immutable = False

    try:
        manifest.runtime_name = "illegal"
    except (AttributeError, TypeError):
        manifest_immutable = True

    if not manifest_immutable:
        fail(
            "Runtime version manifest was mutable."
        )

    metadata_immutable = False

    try:
        manifest.metadata["illegal"] = "value"
    except TypeError:
        metadata_immutable = True

    if not metadata_immutable:
        fail(
            "Runtime version metadata was mutable."
        )

    assertions[
        "immutable_version_manifest"
    ] = "PASS"

    component_versions = {
        "runtime.kernel": "0.1.0",
        "runtime.configuration": "0.1.0",
        "runtime.environment": "0.1.0",
        "runtime.service_registry": "0.1.0",
        "runtime.lifecycle_manager": "0.1.0",
        "runtime.boot_process": "0.1.0",
        "runtime.shutdown_process": "0.1.0",
    }

    for component_key, component_version in (
        component_versions.items()
    ):
        manager.register_component(
            component_key,
            component_version,
            contract="implementation",
        )

    if (
        manager.component_count
        != len(component_versions)
    ):
        fail(
            "Component-version registration count "
            "is incorrect."
        )

    assertions[
        "component_version_registration"
    ] = "PASS"

    duplicate_rejected = False

    try:
        manager.register_component(
            "runtime.kernel",
            "0.1.1",
        )
    except RegistrationError:
        duplicate_rejected = True

    if not duplicate_rejected:
        fail(
            "Duplicate component-version registration "
            "was not rejected."
        )

    assertions[
        "duplicate_registration_rejection"
    ] = "PASS"

    previous_generation = manager.generation

    replacement = manager.register_component(
        "runtime.kernel",
        "0.1.1",
        contract="implementation",
        replace=True,
    )

    if replacement.generation <= previous_generation:
        fail(
            "Explicit version replacement did not "
            "advance the generation."
        )

    if (
        str(
            manager.get_component_version(
                "runtime.kernel"
            ).version
        )
        != "0.1.1"
    ):
        fail(
            "Explicit component-version replacement "
            "did not take effect."
        )

    assertions[
        "explicit_version_replacement"
    ] = "PASS"

    missing_rejected = False

    try:
        manager.get_component_version(
            "runtime.missing"
        )
    except MissingError:
        missing_rejected = True

    if not missing_rejected:
        fail(
            "Missing component version was not rejected."
        )

    assertions[
        "missing_version_rejection"
    ] = "PASS"

    implementation_components = (
        manager.components_for_contract(
            "implementation"
        )
    )

    if (
        len(implementation_components)
        != len(component_versions)
    ):
        fail(
            "Contract-based version lookup returned "
            "an incorrect result."
        )

    assertions[
        "contract_version_lookup"
    ] = "PASS"

    graph_fingerprint = (
        manager.version_graph_fingerprint()
    )

    if len(graph_fingerprint) != 64:
        fail(
            "Version-graph fingerprint is invalid."
        )

    assertions[
        "version_graph_fingerprint"
    ] = "PASS"

    deterministic_a = (
        versioning_module
        .create_default_runtime_version_manager(
            runtime_name="Deterministic Runtime",
            runtime_version="0.2.0",
            release_channel="alpha",
            build_id="build.5",
            metadata={
                "commit": "abc123",
            },
        )
    )

    deterministic_b = (
        versioning_module
        .create_default_runtime_version_manager(
            runtime_name="Deterministic Runtime",
            runtime_version="0.2.0",
            release_channel="alpha",
            build_id="build.5",
            metadata={
                "commit": "abc123",
            },
        )
    )

    if (
        deterministic_a.manifest.fingerprint()
        != deterministic_b.manifest.fingerprint()
    ):
        fail(
            "Equal effective manifests produced "
            "different fingerprints."
        )

    deterministic_b.register_component(
        "runtime.extra",
        "0.1.0",
    )

    if (
        deterministic_a.version_graph_fingerprint()
        == deterministic_b.version_graph_fingerprint()
    ):
        fail(
            "Different version graphs produced "
            "the same fingerprint."
        )

    assertions[
        "deterministic_version_fingerprints"
    ] = "PASS"

    thread_manager = (
        versioning_module
        .create_default_runtime_version_manager(
            runtime_name="Thread Runtime"
        )
    )

    thread_errors: list[str] = []
    thread_count = 16

    def register_thread_component(
        index: int,
    ) -> None:
        try:
            thread_manager.register_component(
                f"thread.component_{index}",
                f"0.1.{index}",
                contract="thread.test",
            )
        except Exception as exc:
            thread_errors.append(
                f"{type(exc).__name__}: {exc}"
            )

    threads = [
        threading.Thread(
            target=register_thread_component,
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
            "Concurrent component-version registration "
            "failed: "
            + "; ".join(thread_errors)
        )

    if thread_manager.component_count != thread_count:
        fail(
            "Concurrent component-version registration "
            "produced an incorrect count."
        )

    assertions[
        "thread_safe_version_registration"
    ] = "PASS"

    snapshot = manager.snapshot()

    if snapshot.component_count != len(
        component_versions
    ):
        fail(
            "Version snapshot component count "
            "is incorrect."
        )

    snapshot_immutable = False

    try:
        snapshot.sealed = True
    except (AttributeError, TypeError):
        snapshot_immutable = True

    if not snapshot_immutable:
        fail(
            "Runtime version snapshot was mutable."
        )

    assertions[
        "immutable_version_snapshot"
    ] = "PASS"

    sealed_snapshot = manager.seal()

    if not sealed_snapshot.sealed:
        fail(
            "Runtime version manager did not seal."
        )

    mutation_after_seal_rejected = False

    try:
        manager.register_component(
            "runtime.late_component",
            "0.1.0",
        )
    except StateError:
        mutation_after_seal_rejected = True

    if not mutation_after_seal_rejected:
        fail(
            "Version registration was accepted "
            "after sealing."
        )

    assertions[
        "version_registry_sealing"
    ] = "PASS"

    service_registry = Registry()

    service_registry.register(
        "runtime.versioning",
        manager,
        capabilities=[
            "runtime.version.read",
        ],
        startup_order=-100,
        critical=True,
    )

    service_registry.seal()

    if (
        service_registry.get(
            "runtime.versioning",
            VersionManager,
        )
        is not manager
    ):
        fail(
            "Runtime Service Registry returned "
            "the wrong version manager."
        )

    assertions[
        "service_registry_version_binding"
    ] = "PASS"

    kernel = Kernel(
        runtime_id="linkcraftor.primary",
        product_name="LinkCraftor",
    )

    kernel.bind_component(
        "service_registry",
        service_registry,
    )

    binding = kernel.bind_component(
        "versioning",
        manager,
    )

    if binding.key != "versioning":
        fail(
            "Kernel versioning binding failed."
        )

    if (
        kernel.get_component(
            "versioning",
            VersionManager,
        )
        is not manager
    ):
        fail(
            "Kernel returned the wrong "
            "version manager."
        )

    assertions[
        "kernel_versioning_binding"
    ] = "PASS"

    return {
        "assertions": assertions,
        "runtime_version": str(
            manifest.runtime_version
        ),
        "release_channel": (
            manifest.release_channel.value
        ),
        "manifest_fingerprint": (
            manifest.fingerprint()
        ),
        "version_graph_fingerprint": (
            graph_fingerprint
        ),
        "component_count": (
            manager.component_count
        ),
        "manager_generation": (
            manager.generation
        ),
        "thread_component_count": (
            thread_manager.component_count
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
                "Runtime versioning rollback backup "
                "is missing."
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
    print("1.1.8 — RUNTIME VERSIONING BUILD")
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
            "Existing runtime versioning file "
            "backed up:"
        )
        print(BACKUP_TARGET)
        print()

    TARGET.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    versioning_module_name = (
        "_uri_phase_1_1_8_runtime_versioning_test"
    )

    kernel_module_name = (
        "_uri_phase_1_1_8_runtime_kernel_test"
    )

    registry_module_name = (
        "_uri_phase_1_1_8_runtime_registry_test"
    )

    try:
        TARGET.write_text(
            VERSIONING_SOURCE,
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

        versioning_module = load_module(
            TARGET,
            versioning_module_name,
        )

        kernel_module = load_module(
            KERNEL_FILE,
            kernel_module_name,
        )

        registry_module = load_module(
            SERVICE_REGISTRY_FILE,
            registry_module_name,
        )

        if (
            dict(os.environ)
            != process_environment_before
        ):
            fail(
                "Importing runtime versioning mutated "
                "os.environ."
            )

        behavioral_results = verify_behavior(
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
            "Runtime versioning verification failed. "
            "The previous filesystem state was restored."
        )

        raise

    finally:
        unload_module(versioning_module_name)
        unload_module(kernel_module_name)
        unload_module(registry_module_name)

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
            "versioning_py_compile": "PASS",
            "foundation_files_compile": "PASS",
            "main_py_compile": "PASS",
            "ast_contract": "PASS",
            "semantic_version_contract": "PASS",
            "manifest_contract": "PASS",
            "component_registration_contract": "PASS",
            "thread_safety_contract": "PASS",
            "fingerprint_contract": "PASS",
            "sealing_contract": "PASS",
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
            "item": "1.1.8",
            "name": "Runtime Versioning",
            "implementation_status": "IMPLEMENTED",
            "verification_status": "PASS",
            "kernel_binding_status": "PASS",
            "service_registry_binding_status": "PASS",
            "application_boot_integration": "PENDING",
            "compatibility_layer_integration": "PENDING",
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
        "1.1.8 — RUNTIME VERSIONING EVIDENCE",
        "=" * 78,
        "",
        f"Build version: {BUILD_VERSION}",
        f"Timestamp UTC: {evidence['timestamp_utc']}",
        f"Target: {TARGET}",
        "",
        "VERIFICATION",
        "-" * 78,
        "Runtime Versioning compilation: PASS",
        "Phase 1 foundation compilation: PASS",
        "main.py compilation: PASS",
        "Versioning AST contract: PASS",
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
            "VERSION MANIFEST",
            "-" * 78,
            (
                "Runtime version: "
                f"{behavioral_results['runtime_version']}"
            ),
            (
                "Release channel: "
                f"{behavioral_results['release_channel']}"
            ),
            (
                "Manifest fingerprint: "
                f"{behavioral_results['manifest_fingerprint']}"
            ),
            (
                "Version graph fingerprint: "
                f"{behavioral_results['version_graph_fingerprint']}"
            ),
            "",
            "CHECKLIST POSITION",
            "-" * 78,
            "1.1.1 kernel compatibility: PASS",
            "1.1.4 service-registry compatibility: PASS",
            "1.1.8 implementation: PASS",
            "1.1.8 isolated verification: PASS",
            "1.1.8 kernel binding: PASS",
            "1.1.8 service-registry binding: PASS",
            (
                "1.1.8 application boot integration: "
                "PENDING"
            ),
            (
                "1.1.8 compatibility-layer integration: "
                "PENDING"
            ),
            "1.1.8 certification: NOT CERTIFIED",
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
        "Runtime Versioning compilation:        PASS"
    )
    print(
        "Phase 1 foundation compilation:        PASS"
    )
    print(
        "main.py compilation:                   PASS"
    )
    print(
        "Versioning AST contract:               PASS"
    )
    print(
        "Semantic Version parsing/precedence:   PASS"
    )
    print(
        "Immutable version manifest:            PASS"
    )
    print(
        "Component-version registration:        PASS"
    )
    print(
        "Thread-safe version registration:      PASS"
    )
    print(
        "Deterministic version fingerprints:    PASS"
    )
    print(
        "Version-registry sealing:              PASS"
    )
    print(
        "Service-registry version binding:      PASS"
    )
    print(
        "Kernel versioning binding:             PASS"
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
    print(f"Runtime versioning: {TARGET}")
    print(f"Evidence JSON:      {EVIDENCE_JSON}")
    print(f"Evidence text:      {EVIDENCE_TEXT}")
    print()

    print("1.1.8 RUNTIME VERSIONING")
    print("IMPLEMENTATION: PASS")
    print("ISOLATED VERIFICATION: PASS")
    print("KERNEL BINDING: PASS")
    print("SERVICE-REGISTRY BINDING: PASS")
    print("APPLICATION BOOT INTEGRATION: PENDING")
    print("COMPATIBILITY-LAYER INTEGRATION: PENDING")
    print("CERTIFICATION: NOT CERTIFIED")
    print()
    print("NO PRODUCTION DATA WAS MODIFIED")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
