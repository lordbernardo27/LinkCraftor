from __future__ import annotations

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
