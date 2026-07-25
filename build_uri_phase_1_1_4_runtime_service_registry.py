from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import py_compile
import shutil
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BUILD_VERSION = "uri_phase_1_1_4_runtime_service_registry_v1"

PROJECT_ROOT = Path.cwd().resolve()

TARGET = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "runtime"
    / "runtime_service_registry.py"
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
    / f"uri_phase1_1_4_runtime_service_registry_{TIMESTAMP}"
)

BACKUP_TARGET = (
    BACKUP_ROOT
    / "backend"
    / "server"
    / "runtime"
    / "runtime_service_registry.py"
)

EVIDENCE_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime"
    / "uri_phase_1"
    / "1_1_4_runtime_service_registry"
)

EVIDENCE_JSON = (
    EVIDENCE_ROOT
    / f"runtime_service_registry_build_{TIMESTAMP}.json"
)

EVIDENCE_TEXT = (
    EVIDENCE_ROOT
    / f"runtime_service_registry_build_{TIMESTAMP}.txt"
)


REGISTRY_SOURCE = r'''from __future__ import annotations

"""
Universal Runtime Service Registry.

This module owns registration and resolution of runtime foundation
services. It is deliberately separate from pipeline-stage, job-handler,
and worker-capability registration.

The registry does not start services, execute jobs, manage workers,
load configuration, or contain product-specific business logic.
"""

import re
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping, TypeVar, cast


__all__ = [
    "RuntimeServiceBinding",
    "RuntimeServiceDependencyError",
    "RuntimeServiceMissingError",
    "RuntimeServiceRegistrationError",
    "RuntimeServiceRegistry",
    "RuntimeServiceRegistryError",
    "RuntimeServiceRegistrySnapshot",
    "RuntimeServiceRegistryStateError",
]


T = TypeVar("T")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _qualified_type_name(value: object) -> str:
    value_type = type(value)

    return (
        f"{value_type.__module__}."
        f"{value_type.__qualname__}"
    )


_SERVICE_KEY_PATTERN = re.compile(
    r"^[a-z][a-z0-9_.-]{1,127}$"
)

_CAPABILITY_PATTERN = re.compile(
    r"^[a-z][a-z0-9_.:-]{1,127}$"
)


class RuntimeServiceRegistryError(RuntimeError):
    """Base runtime-service-registry failure."""


class RuntimeServiceRegistrationError(
    RuntimeServiceRegistryError
):
    """Raised when a service registration is invalid."""


class RuntimeServiceMissingError(
    RuntimeServiceRegistryError
):
    """Raised when a required runtime service is unavailable."""


class RuntimeServiceDependencyError(
    RuntimeServiceRegistryError
):
    """Raised when service dependencies are invalid."""


class RuntimeServiceRegistryStateError(
    RuntimeServiceRegistryError
):
    """Raised when a sealed registry is mutated."""


@dataclass(frozen=True, slots=True)
class RuntimeServiceBinding:
    """Immutable metadata for one registered runtime service."""

    key: str
    service_type: str
    capabilities: tuple[str, ...]
    dependencies: tuple[str, ...]
    startup_order: int
    critical: bool
    registered_at: datetime
    generation: int


@dataclass(frozen=True, slots=True)
class RuntimeServiceRegistrySnapshot:
    """Immutable point-in-time registry inspection record."""

    sealed: bool
    generation: int
    service_count: int
    services: tuple[RuntimeServiceBinding, ...]
    unresolved_dependencies: tuple[
        tuple[str, str],
        ...
    ]


class RuntimeServiceRegistry:
    """
    Thread-safe registry for Universal Runtime services.

    Responsibilities:

    - Register runtime foundation services by logical key.
    - Reject accidental duplicate registration.
    - Resolve services with optional type validation.
    - Record generic service capabilities.
    - Record and validate service dependencies.
    - Produce deterministic dependency-aware startup order.
    - Seal registration before lifecycle startup.
    - Expose immutable inspection snapshots.

    Non-responsibilities:

    - Starting or stopping services.
    - Executing jobs or pipeline stages.
    - Registering product pipeline handlers.
    - Persisting registry state.
    """

    __slots__ = (
        "_services",
        "_bindings",
        "_generation",
        "_sealed",
        "_lock",
    )

    def __init__(self) -> None:
        self._services: dict[str, object] = {}
        self._bindings: dict[
            str,
            RuntimeServiceBinding,
        ] = {}
        self._generation = 0
        self._sealed = False
        self._lock = threading.RLock()

    @staticmethod
    def normalize_service_key(
        service_key: str,
    ) -> str:
        key = str(service_key or "").strip().lower()

        if not _SERVICE_KEY_PATTERN.fullmatch(key):
            raise RuntimeServiceRegistrationError(
                "service_key must be 2-128 characters, begin "
                "with a lowercase letter, and contain only "
                "lowercase letters, numbers, dots, underscores, "
                "or hyphens."
            )

        return key

    @staticmethod
    def normalize_capability(
        capability: str,
    ) -> str:
        normalized = str(capability or "").strip().lower()

        if not _CAPABILITY_PATTERN.fullmatch(normalized):
            raise RuntimeServiceRegistrationError(
                "capability must be 2-128 characters, begin "
                "with a lowercase letter, and contain only "
                "lowercase letters, numbers, dots, underscores, "
                "colons, or hyphens."
            )

        return normalized

    @property
    def generation(self) -> int:
        with self._lock:
            return self._generation

    @property
    def service_count(self) -> int:
        with self._lock:
            return len(self._services)

    @property
    def sealed(self) -> bool:
        with self._lock:
            return self._sealed

    def _assert_mutable(self) -> None:
        if self._sealed:
            raise RuntimeServiceRegistryStateError(
                "The runtime service registry is sealed."
            )

    def _record_mutation(self) -> int:
        self._generation += 1
        return self._generation

    def register(
        self,
        service_key: str,
        service: object,
        *,
        capabilities: tuple[str, ...] | list[str] = (),
        dependencies: tuple[str, ...] | list[str] = (),
        startup_order: int = 100,
        critical: bool = True,
        replace: bool = False,
    ) -> RuntimeServiceBinding:
        """
        Register one runtime service.

        Dependency keys may refer to services registered later. Complete
        dependency validation occurs before sealing or startup ordering.
        """

        key = self.normalize_service_key(service_key)

        if service is None:
            raise RuntimeServiceRegistrationError(
                "A registered runtime service cannot be None."
            )

        if isinstance(startup_order, bool):
            raise RuntimeServiceRegistrationError(
                "startup_order must be an integer."
            )

        try:
            resolved_startup_order = int(startup_order)
        except (TypeError, ValueError) as exc:
            raise RuntimeServiceRegistrationError(
                "startup_order must be an integer."
            ) from exc

        if not -100000 <= resolved_startup_order <= 100000:
            raise RuntimeServiceRegistrationError(
                "startup_order must be between "
                "-100000 and 100000."
            )

        resolved_capabilities = tuple(
            sorted(
                {
                    self.normalize_capability(item)
                    for item in capabilities
                }
            )
        )

        resolved_dependencies = tuple(
            sorted(
                {
                    self.normalize_service_key(item)
                    for item in dependencies
                }
            )
        )

        if key in resolved_dependencies:
            raise RuntimeServiceDependencyError(
                f"Service {key!r} cannot depend on itself."
            )

        with self._lock:
            self._assert_mutable()

            if key in self._services and not replace:
                raise RuntimeServiceRegistrationError(
                    f"Runtime service {key!r} is already registered."
                )

            generation = self._record_mutation()

            binding = RuntimeServiceBinding(
                key=key,
                service_type=_qualified_type_name(service),
                capabilities=resolved_capabilities,
                dependencies=resolved_dependencies,
                startup_order=resolved_startup_order,
                critical=bool(critical),
                registered_at=_utc_now(),
                generation=generation,
            )

            previous_service = self._services.get(key)
            previous_binding = self._bindings.get(key)

            self._services[key] = service
            self._bindings[key] = binding

            try:
                self._detect_cycles(
                    allow_missing_dependencies=True
                )
            except Exception:
                if previous_binding is None:
                    self._services.pop(key, None)
                    self._bindings.pop(key, None)
                else:
                    self._services[key] = previous_service
                    self._bindings[key] = previous_binding

                self._generation -= 1
                raise

            return binding

    def unregister(
        self,
        service_key: str,
    ) -> object:
        """Remove and return a runtime service."""

        key = self.normalize_service_key(service_key)

        with self._lock:
            self._assert_mutable()

            if key not in self._services:
                raise RuntimeServiceMissingError(
                    f"Runtime service {key!r} is not registered."
                )

            dependents = tuple(
                binding.key
                for binding in self._bindings.values()
                if key in binding.dependencies
            )

            if dependents:
                raise RuntimeServiceDependencyError(
                    f"Runtime service {key!r} is required by: "
                    + ", ".join(sorted(dependents))
                )

            service = self._services.pop(key)
            self._bindings.pop(key, None)
            self._record_mutation()

            return service

    def has(
        self,
        service_key: str,
    ) -> bool:
        key = self.normalize_service_key(service_key)

        with self._lock:
            return key in self._services

    def get(
        self,
        service_key: str,
        expected_type: type[T] | None = None,
    ) -> T | object:
        """Resolve a registered runtime service."""

        key = self.normalize_service_key(service_key)

        with self._lock:
            if key not in self._services:
                raise RuntimeServiceMissingError(
                    f"Runtime service {key!r} is not registered."
                )

            service = self._services[key]

        if (
            expected_type is not None
            and not isinstance(service, expected_type)
        ):
            raise RuntimeServiceRegistrationError(
                f"Runtime service {key!r} has type "
                f"{_qualified_type_name(service)!r}, not "
                f"{expected_type.__module__}."
                f"{expected_type.__qualname__}."
            )

        if expected_type is not None:
            return cast(T, service)

        return service

    def require(
        self,
        service_keys: tuple[str, ...] | list[str],
    ) -> Mapping[str, object]:
        """
        Resolve several services atomically.

        The returned mapping is read-only.
        """

        keys = tuple(
            self.normalize_service_key(key)
            for key in service_keys
        )

        with self._lock:
            missing = tuple(
                key
                for key in keys
                if key not in self._services
            )

            if missing:
                raise RuntimeServiceMissingError(
                    "Missing required runtime services: "
                    + ", ".join(sorted(missing))
                )

            selected = {
                key: self._services[key]
                for key in keys
            }

        return MappingProxyType(selected)

    def services_with_capability(
        self,
        capability: str,
    ) -> tuple[str, ...]:
        """Return service keys advertising a capability."""

        normalized = self.normalize_capability(capability)

        with self._lock:
            return tuple(
                sorted(
                    binding.key
                    for binding in self._bindings.values()
                    if normalized in binding.capabilities
                )
            )

    def unresolved_dependencies(
        self,
    ) -> tuple[tuple[str, str], ...]:
        """
        Return pairs of service key and missing dependency key.
        """

        with self._lock:
            registered = frozenset(self._services)

            unresolved = tuple(
                sorted(
                    (
                        binding.key,
                        dependency,
                    )
                    for binding in self._bindings.values()
                    for dependency in binding.dependencies
                    if dependency not in registered
                )
            )

        return unresolved

    def validate_dependencies(self) -> None:
        """Validate missing dependencies and dependency cycles."""

        unresolved = self.unresolved_dependencies()

        if unresolved:
            formatted = ", ".join(
                f"{service}->{dependency}"
                for service, dependency in unresolved
            )

            raise RuntimeServiceDependencyError(
                "Unresolved runtime-service dependencies: "
                + formatted
            )

        with self._lock:
            self._detect_cycles(
                allow_missing_dependencies=False
            )

    def dependency_order(self) -> tuple[str, ...]:
        """
        Return deterministic dependency-aware startup order.

        Dependencies always appear before their dependents. Services at
        the same dependency level are ordered by startup_order and key.
        """

        self.validate_dependencies()

        with self._lock:
            bindings = dict(self._bindings)

        indegree = {
            key: len(binding.dependencies)
            for key, binding in bindings.items()
        }

        dependents: dict[str, set[str]] = {
            key: set()
            for key in bindings
        }

        for key, binding in bindings.items():
            for dependency in binding.dependencies:
                dependents[dependency].add(key)

        ready = [
            key
            for key, degree in indegree.items()
            if degree == 0
        ]

        ordered: list[str] = []

        while ready:
            ready.sort(
                key=lambda key: (
                    bindings[key].startup_order,
                    key,
                )
            )

            key = ready.pop(0)
            ordered.append(key)

            for dependent in sorted(dependents[key]):
                indegree[dependent] -= 1

                if indegree[dependent] == 0:
                    ready.append(dependent)

        if len(ordered) != len(bindings):
            raise RuntimeServiceDependencyError(
                "A runtime-service dependency cycle exists."
            )

        return tuple(ordered)

    def seal(self) -> RuntimeServiceRegistrySnapshot:
        """
        Validate and seal the registry against further mutation.
        """

        self.validate_dependencies()
        self.dependency_order()

        with self._lock:
            self._sealed = True
            self._record_mutation()

        return self.snapshot()

    def snapshot(self) -> RuntimeServiceRegistrySnapshot:
        """Return an immutable registry inspection snapshot."""

        with self._lock:
            services = tuple(
                self._bindings[key]
                for key in sorted(self._bindings)
            )

            registered = frozenset(self._services)

            unresolved = tuple(
                sorted(
                    (
                        binding.key,
                        dependency,
                    )
                    for binding in self._bindings.values()
                    for dependency in binding.dependencies
                    if dependency not in registered
                )
            )

            return RuntimeServiceRegistrySnapshot(
                sealed=self._sealed,
                generation=self._generation,
                service_count=len(self._services),
                services=services,
                unresolved_dependencies=unresolved,
            )

    def _detect_cycles(
        self,
        *,
        allow_missing_dependencies: bool,
    ) -> None:
        bindings = dict(self._bindings)
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(key: str) -> None:
            if key in visited:
                return

            if key in visiting:
                raise RuntimeServiceDependencyError(
                    "A runtime-service dependency cycle "
                    f"includes {key!r}."
                )

            visiting.add(key)

            for dependency in bindings[key].dependencies:
                if dependency not in bindings:
                    if allow_missing_dependencies:
                        continue

                    raise RuntimeServiceDependencyError(
                        f"Runtime service {key!r} depends on "
                        f"missing service {dependency!r}."
                    )

                visit(dependency)

            visiting.remove(key)
            visited.add(key)

        for service_key in sorted(bindings):
            visit(service_key)
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
        "RuntimeServiceBinding",
        "RuntimeServiceRegistrySnapshot",
        "RuntimeServiceRegistry",
        "RuntimeServiceRegistryError",
        "RuntimeServiceRegistrationError",
        "RuntimeServiceMissingError",
        "RuntimeServiceDependencyError",
        "RuntimeServiceRegistryStateError",
    }

    required_registry_methods = {
        "normalize_service_key",
        "normalize_capability",
        "register",
        "unregister",
        "has",
        "get",
        "require",
        "services_with_capability",
        "unresolved_dependencies",
        "validate_dependencies",
        "dependency_order",
        "seal",
        "snapshot",
        "_detect_cycles",
    }

    missing_classes = sorted(
        required_classes - set(classes)
    )

    missing_methods = sorted(
        required_registry_methods
        - classes.get(
            "RuntimeServiceRegistry",
            set(),
        )
    )

    if missing_classes:
        fail(
            "Runtime service registry AST contract "
            "is missing classes: "
            + ", ".join(missing_classes)
        )

    if missing_methods:
        fail(
            "RuntimeServiceRegistry is missing methods: "
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
            "Runtime service registry contains "
            "pipeline-specific business terms: "
            + ", ".join(detected_forbidden_terms)
        )

    return {
        "required_classes": sorted(required_classes),
        "missing_classes": missing_classes,
        "required_registry_methods": sorted(
            required_registry_methods
        ),
        "missing_registry_methods": missing_methods,
        "pipeline_business_terms_detected": (
            detected_forbidden_terms
        ),
    }


def verify_behavior(
    registry_module: Any,
    kernel_module: Any,
) -> dict[str, Any]:
    Registry = registry_module.RuntimeServiceRegistry

    RegistrationError = (
        registry_module.RuntimeServiceRegistrationError
    )

    MissingError = (
        registry_module.RuntimeServiceMissingError
    )

    DependencyError = (
        registry_module.RuntimeServiceDependencyError
    )

    StateError = (
        registry_module.RuntimeServiceRegistryStateError
    )

    Kernel = kernel_module.UniversalRuntimeKernel

    assertions: dict[str, str] = {}

    class ExampleService:
        def __init__(self, name: str) -> None:
            self.name = name

    registry = Registry()

    state_service = ExampleService("state")
    event_service = ExampleService("event")
    metrics_service = ExampleService("metrics")

    state_binding = registry.register(
        "state.store",
        state_service,
        capabilities=[
            "state.read",
            "state.write",
        ],
        startup_order=10,
        critical=True,
    )

    if state_binding.key != "state.store":
        fail("State service binding key is incorrect.")

    assertions["service_registration"] = "PASS"

    duplicate_rejected = False

    try:
        registry.register(
            "state.store",
            ExampleService("duplicate"),
        )
    except RegistrationError:
        duplicate_rejected = True

    if not duplicate_rejected:
        fail(
            "Duplicate service registration "
            "was not rejected."
        )

    assertions[
        "duplicate_registration_rejection"
    ] = "PASS"

    replacement_service = ExampleService(
        "replacement-state"
    )

    replacement_binding = registry.register(
        "state.store",
        replacement_service,
        capabilities=[
            "state.read",
            "state.write",
        ],
        startup_order=10,
        critical=True,
        replace=True,
    )

    if (
        replacement_binding.generation
        <= state_binding.generation
    ):
        fail(
            "Explicit service replacement did not "
            "advance the registry generation."
        )

    if (
        registry.get(
            "state.store",
            ExampleService,
        )
        is not replacement_service
    ):
        fail(
            "Explicit replacement did not update "
            "the registered service."
        )

    assertions["explicit_replacement"] = "PASS"

    registry.register(
        "event.store",
        event_service,
        capabilities=[
            "event.read",
            "event.write",
        ],
        dependencies=[
            "state.store",
        ],
        startup_order=20,
    )

    registry.register(
        "metrics.service",
        metrics_service,
        capabilities=[
            "metrics.read",
        ],
        dependencies=[
            "event.store",
        ],
        startup_order=30,
        critical=False,
    )

    assertions[
        "dependency_registration"
    ] = "PASS"

    if not registry.has("event.store"):
        fail(
            "Registered service was not found."
        )

    if (
        registry.get(
            "event.store",
            ExampleService,
        )
        is not event_service
    ):
        fail(
            "Typed service resolution returned "
            "the wrong object."
        )

    assertions["typed_service_resolution"] = "PASS"

    missing_rejected = False

    try:
        registry.get("missing.service")
    except MissingError:
        missing_rejected = True

    if not missing_rejected:
        fail(
            "Missing service resolution was not rejected."
        )

    assertions[
        "missing_service_rejection"
    ] = "PASS"

    required_services = registry.require(
        [
            "state.store",
            "event.store",
        ]
    )

    if (
        required_services["state.store"]
        is not replacement_service
    ):
        fail(
            "Required service mapping is incorrect."
        )

    immutable_required_mapping = False

    try:
        required_services["illegal.service"] = object()
    except TypeError:
        immutable_required_mapping = True

    if not immutable_required_mapping:
        fail(
            "Required service mapping was mutable."
        )

    assertions[
        "immutable_required_mapping"
    ] = "PASS"

    state_capability_services = (
        registry.services_with_capability(
            "state.read"
        )
    )

    if state_capability_services != (
        "state.store",
    ):
        fail(
            "Capability-based service lookup "
            "returned an incorrect result."
        )

    assertions[
        "capability_lookup"
    ] = "PASS"

    dependency_order = registry.dependency_order()

    if dependency_order != (
        "state.store",
        "event.store",
        "metrics.service",
    ):
        fail(
            "Dependency-aware startup order is incorrect: "
            f"{dependency_order!r}"
        )

    assertions[
        "dependency_startup_order"
    ] = "PASS"

    dependent_unregistration_rejected = False

    try:
        registry.unregister("state.store")
    except DependencyError:
        dependent_unregistration_rejected = True

    if not dependent_unregistration_rejected:
        fail(
            "Unregistration of a required service "
            "was not rejected."
        )

    assertions[
        "dependent_unregistration_protection"
    ] = "PASS"

    missing_dependency_registry = Registry()

    missing_dependency_registry.register(
        "dependent.service",
        ExampleService("dependent"),
        dependencies=[
            "absent.service",
        ],
    )

    missing_dependency_rejected = False

    try:
        missing_dependency_registry.validate_dependencies()
    except DependencyError:
        missing_dependency_rejected = True

    if not missing_dependency_rejected:
        fail(
            "Missing service dependency "
            "was not rejected."
        )

    assertions[
        "missing_dependency_rejection"
    ] = "PASS"

    cycle_registry = Registry()

    cycle_registry.register(
        "cycle.alpha",
        ExampleService("alpha"),
        dependencies=[
            "cycle.beta",
        ],
    )

    cycle_rejected = False

    try:
        cycle_registry.register(
            "cycle.beta",
            ExampleService("beta"),
            dependencies=[
                "cycle.alpha",
            ],
        )
    except DependencyError:
        cycle_rejected = True

    if not cycle_rejected:
        fail(
            "Service dependency cycle "
            "was not rejected."
        )

    assertions[
        "dependency_cycle_rejection"
    ] = "PASS"

    thread_registry = Registry()
    thread_errors: list[str] = []
    thread_count = 16

    def register_thread_service(index: int) -> None:
        try:
            thread_registry.register(
                f"thread.service_{index}",
                ExampleService(
                    f"thread-{index}"
                ),
                capabilities=[
                    "thread.test",
                ],
            )
        except Exception as exc:
            thread_errors.append(
                f"{type(exc).__name__}: {exc}"
            )

    threads = [
        threading.Thread(
            target=register_thread_service,
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
            "Concurrent service registration failed: "
            + "; ".join(thread_errors)
        )

    if thread_registry.service_count != thread_count:
        fail(
            "Concurrent registration produced "
            "an incorrect service count."
        )

    assertions[
        "thread_safe_registration"
    ] = "PASS"

    snapshot_before_seal = registry.snapshot()

    if snapshot_before_seal.sealed:
        fail(
            "Registry was sealed before seal() was called."
        )

    if snapshot_before_seal.service_count != 3:
        fail(
            "Registry snapshot service count is incorrect."
        )

    snapshot_immutable = False

    try:
        snapshot_before_seal.sealed = True
    except (AttributeError, TypeError):
        snapshot_immutable = True

    if not snapshot_immutable:
        fail(
            "Registry snapshot was mutable."
        )

    assertions[
        "immutable_registry_snapshot"
    ] = "PASS"

    sealed_snapshot = registry.seal()

    if not sealed_snapshot.sealed:
        fail(
            "Registry did not become sealed."
        )

    mutation_after_seal_rejected = False

    try:
        registry.register(
            "late.service",
            ExampleService("late"),
        )
    except StateError:
        mutation_after_seal_rejected = True

    if not mutation_after_seal_rejected:
        fail(
            "Registry accepted registration "
            "after sealing."
        )

    assertions[
        "registry_sealing"
    ] = "PASS"

    kernel = Kernel(
        runtime_id="linkcraftor.primary",
        product_name="LinkCraftor",
    )

    binding = kernel.bind_component(
        "service_registry",
        registry,
    )

    if binding.key != "service_registry":
        fail(
            "Kernel service-registry binding failed."
        )

    retrieved = kernel.get_component(
        "service_registry",
        Registry,
    )

    if retrieved is not registry:
        fail(
            "Kernel returned the wrong "
            "service registry."
        )

    if (
        "service_registry"
        in kernel.missing_foundation_components()
    ):
        fail(
            "Kernel still reported the "
            "service registry as missing."
        )

    assertions[
        "kernel_service_registry_binding"
    ] = "PASS"

    return {
        "assertions": assertions,
        "service_count": registry.service_count,
        "registry_generation": registry.generation,
        "sealed": registry.sealed,
        "dependency_order": list(
            dependency_order
        ),
        "thread_service_count": (
            thread_registry.service_count
        ),
        "kernel_generation": kernel.generation,
        "kernel_missing_foundation_components": (
            list(
                kernel.missing_foundation_components()
            )
        ),
    }


def rollback(
    *,
    target_existed: bool,
) -> None:
    if target_existed:
        if not BACKUP_TARGET.exists():
            raise RuntimeError(
                "Runtime service registry rollback "
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
    print("1.1.4 — RUNTIME SERVICE REGISTRY BUILD")
    print("=" * 78)
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Target:       {TARGET}")
    print()

    required_files = [
        KERNEL_FILE,
        CONFIGURATION_FILE,
        ENVIRONMENT_FILE,
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
        "kernel": sha256_file(KERNEL_FILE),
        "configuration": sha256_file(
            CONFIGURATION_FILE
        ),
        "environment": sha256_file(
            ENVIRONMENT_FILE
        ),
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
            "Existing runtime service registry "
            "backed up:"
        )
        print(BACKUP_TARGET)
        print()

    TARGET.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    registry_module_name = (
        "_uri_phase_1_1_4_runtime_service_registry_test"
    )

    kernel_module_name = (
        "_uri_phase_1_1_4_runtime_kernel_test"
    )

    try:
        TARGET.write_text(
            REGISTRY_SOURCE,
            encoding="utf-8",
            newline="\n",
        )

        py_compile.compile(
            str(TARGET),
            doraise=True,
        )

        py_compile.compile(
            str(KERNEL_FILE),
            doraise=True,
        )

        py_compile.compile(
            str(CONFIGURATION_FILE),
            doraise=True,
        )

        py_compile.compile(
            str(ENVIRONMENT_FILE),
            doraise=True,
        )

        py_compile.compile(
            str(MAIN_FILE),
            doraise=True,
        )

        ast_contract = verify_ast_contract(TARGET)

        registry_module = load_module(
            TARGET,
            registry_module_name,
        )

        kernel_module = load_module(
            KERNEL_FILE,
            kernel_module_name,
        )

        behavioral_results = verify_behavior(
            registry_module,
            kernel_module,
        )

        protected_hashes_after = {
            "kernel": sha256_file(KERNEL_FILE),
            "configuration": sha256_file(
                CONFIGURATION_FILE
            ),
            "environment": sha256_file(
                ENVIRONMENT_FILE
            ),
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
                "A protected runtime file "
                "changed unexpectedly."
            )

    except Exception:
        rollback(
            target_existed=target_existed,
        )

        print()
        print("ROLLBACK COMPLETE")
        print(
            "Runtime service registry verification "
            "failed. The previous filesystem state "
            "was restored."
        )
        raise

    finally:
        unload_module(registry_module_name)
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
            "registry_py_compile": "PASS",
            "kernel_py_compile": "PASS",
            "configuration_py_compile": "PASS",
            "environment_py_compile": "PASS",
            "main_py_compile": "PASS",
            "ast_contract": "PASS",
            "behavioral_contract": "PASS",
            "dependency_contract": "PASS",
            "cycle_detection": "PASS",
            "thread_safety": "PASS",
            "registry_sealing": "PASS",
            "kernel_binding_contract": "PASS",
            "business_logic_agnostic_test": "PASS",
            "protected_files_unchanged": "PASS",
            "automatic_rollback_required": False,
        },
        "ast_contract_details": ast_contract,
        "behavioral_results": behavioral_results,
        "phase_status": {
            "phase": "1",
            "item": "1.1.4",
            "name": "Runtime Service Registry",
            "implementation_status": "IMPLEMENTED",
            "verification_status": "PASS",
            "kernel_binding_status": "PASS",
            "existing_handler_registry_bridge": "PENDING",
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
        "1.1.4 — RUNTIME SERVICE REGISTRY EVIDENCE",
        "=" * 78,
        "",
        f"Build version: {BUILD_VERSION}",
        f"Timestamp UTC: {evidence['timestamp_utc']}",
        f"Target: {TARGET}",
        "",
        "VERIFICATION",
        "-" * 78,
        "Runtime service registry compilation: PASS",
        "Universal Runtime Kernel compilation: PASS",
        "Runtime Configuration compilation: PASS",
        "Runtime Environment compilation: PASS",
        "main.py compilation: PASS",
        "Service registry AST contract: PASS",
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
            "DEPENDENCY ORDER",
            "-" * 78,
        ]
    )

    for service_key in behavioral_results[
        "dependency_order"
    ]:
        evidence_lines.append(service_key)

    evidence_lines.extend(
        [
            "",
            "KERNEL INTEGRATION",
            "-" * 78,
            "Service registry kernel binding: PASS",
            (
                "Kernel generation after binding: "
                f"{behavioral_results['kernel_generation']}"
            ),
            "",
            "CHECKLIST POSITION",
            "-" * 78,
            "1.1.1 kernel implementation: PASS",
            (
                "1.1.1 service-registry binding "
                "compatibility: PASS"
            ),
            "1.1.1 full runtime integration: PENDING",
            "1.1.2 configuration implementation: PASS",
            "1.1.3 environment implementation: PASS",
            "1.1.4 implementation: PASS",
            "1.1.4 isolated verification: PASS",
            "1.1.4 kernel binding: PASS",
            (
                "1.1.4 existing handler-registry bridge: "
                "PENDING"
            ),
            (
                "1.1.4 application boot integration: "
                "PENDING"
            ),
            "1.1.4 certification: NOT CERTIFIED",
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
        "Runtime service registry compilation: PASS"
    )
    print(
        "Universal Runtime Kernel compilation: PASS"
    )
    print(
        "Runtime Configuration compilation:    PASS"
    )
    print(
        "Runtime Environment compilation:      PASS"
    )
    print(
        "main.py compilation:                   PASS"
    )
    print(
        "Service registry AST contract:        PASS"
    )
    print(
        "Service registry behavioral contract: PASS"
    )
    print(
        "Dependency validation and ordering:   PASS"
    )
    print(
        "Dependency-cycle detection:           PASS"
    )
    print(
        "Thread-safe service registration:     PASS"
    )
    print(
        "Registry sealing:                     PASS"
    )
    print(
        "Kernel service-registry binding:      PASS"
    )
    print(
        "Business-logic-agnostic boundary:     PASS"
    )
    print(
        "Protected existing files unchanged:   PASS"
    )
    print()

    print("FILES")
    print("-" * 78)
    print(f"Service registry: {TARGET}")
    print(f"Evidence JSON:    {EVIDENCE_JSON}")
    print(f"Evidence text:    {EVIDENCE_TEXT}")
    print()

    print("1.1.4 RUNTIME SERVICE REGISTRY")
    print("IMPLEMENTATION: PASS")
    print("ISOLATED VERIFICATION: PASS")
    print("KERNEL BINDING: PASS")
    print("EXISTING HANDLER-REGISTRY BRIDGE: PENDING")
    print("APPLICATION BOOT INTEGRATION: PENDING")
    print("CERTIFICATION: NOT CERTIFIED")
    print()
    print("NO PRODUCTION DATA WAS MODIFIED")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
