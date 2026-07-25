from __future__ import annotations

import ast
import asyncio
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


BUILD_VERSION = "uri_phase_1_1_5_runtime_lifecycle_manager_v1"

PROJECT_ROOT = Path.cwd().resolve()

TARGET = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "runtime"
    / "runtime_lifecycle_manager.py"
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
    / f"uri_phase1_1_5_runtime_lifecycle_manager_{TIMESTAMP}"
)

BACKUP_TARGET = (
    BACKUP_ROOT
    / "backend"
    / "server"
    / "runtime"
    / "runtime_lifecycle_manager.py"
)

EVIDENCE_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime"
    / "uri_phase_1"
    / "1_1_5_runtime_lifecycle_manager"
)

EVIDENCE_JSON = (
    EVIDENCE_ROOT
    / f"runtime_lifecycle_manager_build_{TIMESTAMP}.json"
)

EVIDENCE_TEXT = (
    EVIDENCE_ROOT
    / f"runtime_lifecycle_manager_build_{TIMESTAMP}.txt"
)


LIFECYCLE_SOURCE = r'''from __future__ import annotations

"""
Universal Runtime Lifecycle Manager.

This module coordinates the ordered lifecycle of registered runtime
foundation services and keeps lifecycle state synchronized with the
Universal Runtime Kernel.

It does not execute jobs, operate queues, implement pipeline stages,
load configuration, or contain product-specific business logic.
"""

import asyncio
import inspect
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Protocol


__all__ = [
    "RuntimeLifecycleError",
    "RuntimeLifecycleEvent",
    "RuntimeLifecycleManager",
    "RuntimeLifecyclePhase",
    "RuntimeLifecycleServiceError",
    "RuntimeLifecycleShutdownError",
    "RuntimeLifecycleSnapshot",
    "RuntimeLifecycleStateError",
    "RuntimeLifecycleTimeoutError",
]


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class RuntimeLifecycleError(RuntimeError):
    """Base runtime-lifecycle failure."""


class RuntimeLifecycleStateError(
    RuntimeLifecycleError
):
    """Raised when a lifecycle transition is invalid."""


class RuntimeLifecycleServiceError(
    RuntimeLifecycleError
):
    """Raised when a critical runtime-service hook fails."""

    def __init__(
        self,
        *,
        service_key: str,
        action: str,
        cause: BaseException,
    ) -> None:
        self.service_key = service_key
        self.action = action
        self.cause = cause

        super().__init__(
            f"Runtime service {service_key!r} failed during "
            f"{action!r}: {type(cause).__name__}: {cause}"
        )


class RuntimeLifecycleTimeoutError(
    RuntimeLifecycleServiceError
):
    """Raised when a critical service hook exceeds its timeout."""


class RuntimeLifecycleShutdownError(
    RuntimeLifecycleError
):
    """Raised after shutdown completes with cleanup failures."""

    def __init__(
        self,
        failures: tuple[str, ...],
    ) -> None:
        self.failures = failures

        super().__init__(
            "Runtime shutdown completed with service failures: "
            + "; ".join(failures)
        )


class RuntimeLifecyclePhase(str, Enum):
    CREATED = "created"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    DRAINING = "draining"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class RuntimeLifecycleEvent:
    """Immutable lifecycle-event record."""

    sequence: int
    timestamp: datetime
    phase: RuntimeLifecyclePhase
    action: str
    status: str
    service_key: str | None
    detail: str | None


@dataclass(frozen=True, slots=True)
class RuntimeLifecycleSnapshot:
    """Immutable point-in-time lifecycle inspection record."""

    phase: RuntimeLifecyclePhase
    generation: int
    initialized_services: tuple[str, ...]
    started_services: tuple[str, ...]
    failed_services: tuple[str, ...]
    failure_reason: str | None
    event_count: int
    events: tuple[RuntimeLifecycleEvent, ...]


class RuntimeKernelContract(Protocol):
    @property
    def state(self) -> Any:
        ...

    def transition_state(
        self,
        *,
        expected_state: Any,
        target_state: Any,
        reason: str | None = None,
    ) -> Any:
        ...

    def mark_failed(
        self,
        reason: str,
    ) -> Any:
        ...


class RuntimeServiceRegistryContract(Protocol):
    @property
    def sealed(self) -> bool:
        ...

    def dependency_order(self) -> tuple[str, ...]:
        ...

    def get(
        self,
        service_key: str,
        expected_type: type[Any] | None = None,
    ) -> object:
        ...

    def snapshot(self) -> Any:
        ...


_HOOK_NAMES: dict[str, tuple[str, ...]] = {
    "initialize": (
        "runtime_initialize",
        "initialize",
    ),
    "ready": (
        "runtime_ready",
        "is_ready",
        "ready",
    ),
    "start": (
        "runtime_start",
        "start",
    ),
    "drain": (
        "runtime_drain",
        "drain",
    ),
    "resume": (
        "runtime_resume",
        "resume",
    ),
    "stop": (
        "runtime_stop",
        "stop",
    ),
    "close": (
        "runtime_close",
        "close",
    ),
}


class RuntimeLifecycleManager:
    """
    Coordinate runtime-service lifecycle operations.

    Lifecycle sequence:

    CREATED
      -> INITIALIZING
      -> READY
      -> RUNNING
      -> DRAINING
      -> RUNNING
      -> STOPPING
      -> STOPPED

    Any active phase may move to FAILED when a critical service fails.
    A failed runtime may still proceed through STOPPING to STOPPED so
    cleanup is not skipped.
    """

    __slots__ = (
        "_kernel",
        "_registry",
        "_phase",
        "_generation",
        "_initialized_services",
        "_started_services",
        "_failed_services",
        "_failure_reason",
        "_events",
        "_event_limit",
        "_startup_timeout_seconds",
        "_shutdown_timeout_seconds",
        "_lock",
    )

    def __init__(
        self,
        *,
        kernel: RuntimeKernelContract,
        service_registry: RuntimeServiceRegistryContract,
        startup_timeout_seconds: float = 30.0,
        shutdown_timeout_seconds: float = 30.0,
        event_limit: int = 500,
    ) -> None:
        if kernel is None:
            raise RuntimeLifecycleStateError(
                "A Universal Runtime Kernel is required."
            )

        if service_registry is None:
            raise RuntimeLifecycleStateError(
                "A Runtime Service Registry is required."
            )

        startup_timeout = float(
            startup_timeout_seconds
        )
        shutdown_timeout = float(
            shutdown_timeout_seconds
        )

        if not 0.01 <= startup_timeout <= 3600.0:
            raise ValueError(
                "startup_timeout_seconds must be between "
                "0.01 and 3600 seconds."
            )

        if not 0.01 <= shutdown_timeout <= 3600.0:
            raise ValueError(
                "shutdown_timeout_seconds must be between "
                "0.01 and 3600 seconds."
            )

        if isinstance(event_limit, bool):
            raise ValueError(
                "event_limit must be an integer."
            )

        resolved_event_limit = int(event_limit)

        if not 10 <= resolved_event_limit <= 100000:
            raise ValueError(
                "event_limit must be between 10 and 100000."
            )

        self._kernel = kernel
        self._registry = service_registry
        self._phase = RuntimeLifecyclePhase.CREATED
        self._generation = 0
        self._initialized_services: set[str] = set()
        self._started_services: set[str] = set()
        self._failed_services: set[str] = set()
        self._failure_reason: str | None = None
        self._events: list[RuntimeLifecycleEvent] = []
        self._event_limit = resolved_event_limit
        self._startup_timeout_seconds = startup_timeout
        self._shutdown_timeout_seconds = shutdown_timeout
        self._lock = asyncio.Lock()

        self._record_event(
            action="manager_created",
            status="completed",
            detail=None,
        )

    @property
    def phase(self) -> RuntimeLifecyclePhase:
        return self._phase

    @property
    def generation(self) -> int:
        return self._generation

    def _record_event(
        self,
        *,
        action: str,
        status: str,
        service_key: str | None = None,
        detail: str | None = None,
    ) -> RuntimeLifecycleEvent:
        self._generation += 1

        event = RuntimeLifecycleEvent(
            sequence=self._generation,
            timestamp=_utc_now(),
            phase=self._phase,
            action=str(action),
            status=str(status),
            service_key=service_key,
            detail=detail,
        )

        self._events.append(event)

        if len(self._events) > self._event_limit:
            overflow = len(self._events) - self._event_limit
            del self._events[:overflow]

        return event

    def _assert_phase(
        self,
        *allowed_phases: RuntimeLifecyclePhase,
    ) -> None:
        if self._phase not in allowed_phases:
            raise RuntimeLifecycleStateError(
                f"Lifecycle operation is invalid while phase is "
                f"{self._phase.value!r}. Allowed phases: "
                + ", ".join(
                    phase.value
                    for phase in allowed_phases
                )
            )

    def _service_metadata(
        self,
    ) -> dict[str, Any]:
        snapshot = self._registry.snapshot()

        return {
            binding.key: binding
            for binding in snapshot.services
        }

    def _service_order(
        self,
        *,
        reverse: bool = False,
    ) -> tuple[str, ...]:
        order = self._registry.dependency_order()

        if reverse:
            return tuple(reversed(order))

        return order

    def _resolve_hook(
        self,
        service: object,
        action: str,
    ) -> tuple[str, Any] | None:
        for hook_name in _HOOK_NAMES[action]:
            hook = getattr(service, hook_name, None)

            if callable(hook):
                return hook_name, hook

        return None

    async def _execute_hook(
        self,
        *,
        service_key: str,
        service: object,
        action: str,
        timeout_seconds: float,
    ) -> Any:
        resolved = self._resolve_hook(
            service,
            action,
        )

        if resolved is None:
            self._record_event(
                action=action,
                status="skipped",
                service_key=service_key,
                detail="No lifecycle hook was defined.",
            )
            return None

        hook_name, hook = resolved

        async def invoke() -> Any:
            result = hook()

            if inspect.isawaitable(result):
                return await result

            return result

        self._record_event(
            action=action,
            status="started",
            service_key=service_key,
            detail=f"hook={hook_name}",
        )

        try:
            result = await asyncio.wait_for(
                invoke(),
                timeout=timeout_seconds,
            )
        except asyncio.TimeoutError as exc:
            timeout_error = TimeoutError(
                f"Hook {hook_name!r} exceeded "
                f"{timeout_seconds} seconds."
            )

            raise RuntimeLifecycleTimeoutError(
                service_key=service_key,
                action=action,
                cause=timeout_error,
            ) from exc
        except RuntimeLifecycleServiceError:
            raise
        except Exception as exc:
            raise RuntimeLifecycleServiceError(
                service_key=service_key,
                action=action,
                cause=exc,
            ) from exc

        if action == "ready" and result is False:
            raise RuntimeLifecycleServiceError(
                service_key=service_key,
                action=action,
                cause=RuntimeError(
                    "The service reported not ready."
                ),
            )

        self._record_event(
            action=action,
            status="completed",
            service_key=service_key,
            detail=f"hook={hook_name}",
        )

        return result

    async def _run_service_action(
        self,
        *,
        action: str,
        service_order: tuple[str, ...],
        timeout_seconds: float,
        continue_after_critical_failure: bool = False,
    ) -> tuple[str, ...]:
        metadata = self._service_metadata()
        failures: list[str] = []

        for service_key in service_order:
            service = self._registry.get(service_key)
            binding = metadata[service_key]

            try:
                await self._execute_hook(
                    service_key=service_key,
                    service=service,
                    action=action,
                    timeout_seconds=timeout_seconds,
                )
            except RuntimeLifecycleServiceError as exc:
                self._failed_services.add(service_key)

                detail = str(exc)

                self._record_event(
                    action=action,
                    status="failed",
                    service_key=service_key,
                    detail=detail,
                )

                failures.append(detail)

                if (
                    binding.critical
                    and not continue_after_critical_failure
                ):
                    raise

        return tuple(failures)

    def _enter_failed(
        self,
        error: BaseException,
    ) -> None:
        reason = (
            f"{type(error).__name__}: {error}"
        )

        self._failure_reason = reason

        if self._phase is RuntimeLifecyclePhase.FAILED:
            return

        self._phase = RuntimeLifecyclePhase.FAILED

        try:
            self._kernel.mark_failed(reason)
        finally:
            self._record_event(
                action="runtime_failed",
                status="failed",
                detail=reason,
            )

    async def initialize(
        self,
    ) -> RuntimeLifecycleSnapshot:
        async with self._lock:
            self._assert_phase(
                RuntimeLifecyclePhase.CREATED
            )

            if not self._registry.sealed:
                raise RuntimeLifecycleStateError(
                    "The Runtime Service Registry must be "
                    "sealed before initialization."
                )

            self._phase = (
                RuntimeLifecyclePhase.INITIALIZING
            )

            self._kernel.transition_state(
                expected_state="created",
                target_state="initializing",
            )

            self._record_event(
                action="runtime_initialize",
                status="started",
            )

            order = self._service_order()

            try:
                await self._run_service_action(
                    action="initialize",
                    service_order=order,
                    timeout_seconds=(
                        self._startup_timeout_seconds
                    ),
                )

                self._initialized_services.update(order)

                await self._run_service_action(
                    action="ready",
                    service_order=order,
                    timeout_seconds=(
                        self._startup_timeout_seconds
                    ),
                )

            except Exception as exc:
                self._enter_failed(exc)
                raise

            self._phase = RuntimeLifecyclePhase.READY

            self._kernel.transition_state(
                expected_state="initializing",
                target_state="ready",
            )

            self._record_event(
                action="runtime_initialize",
                status="completed",
            )

            return self.snapshot()

    async def start(
        self,
    ) -> RuntimeLifecycleSnapshot:
        async with self._lock:
            self._assert_phase(
                RuntimeLifecyclePhase.READY
            )

            order = self._service_order()

            self._record_event(
                action="runtime_start",
                status="started",
            )

            try:
                await self._run_service_action(
                    action="start",
                    service_order=order,
                    timeout_seconds=(
                        self._startup_timeout_seconds
                    ),
                )
            except Exception as exc:
                self._enter_failed(exc)
                raise

            self._started_services.update(order)
            self._phase = RuntimeLifecyclePhase.RUNNING

            self._kernel.transition_state(
                expected_state="ready",
                target_state="running",
            )

            self._record_event(
                action="runtime_start",
                status="completed",
            )

            return self.snapshot()

    async def drain(
        self,
    ) -> RuntimeLifecycleSnapshot:
        async with self._lock:
            self._assert_phase(
                RuntimeLifecyclePhase.RUNNING
            )

            self._phase = RuntimeLifecyclePhase.DRAINING

            self._kernel.transition_state(
                expected_state="running",
                target_state="draining",
            )

            self._record_event(
                action="runtime_drain",
                status="started",
            )

            try:
                await self._run_service_action(
                    action="drain",
                    service_order=self._service_order(
                        reverse=True
                    ),
                    timeout_seconds=(
                        self._shutdown_timeout_seconds
                    ),
                )
            except Exception as exc:
                self._enter_failed(exc)
                raise

            self._record_event(
                action="runtime_drain",
                status="completed",
            )

            return self.snapshot()

    async def resume(
        self,
    ) -> RuntimeLifecycleSnapshot:
        async with self._lock:
            self._assert_phase(
                RuntimeLifecyclePhase.DRAINING
            )

            self._record_event(
                action="runtime_resume",
                status="started",
            )

            try:
                await self._run_service_action(
                    action="resume",
                    service_order=self._service_order(),
                    timeout_seconds=(
                        self._startup_timeout_seconds
                    ),
                )
            except Exception as exc:
                self._enter_failed(exc)
                raise

            self._phase = RuntimeLifecyclePhase.RUNNING

            self._kernel.transition_state(
                expected_state="draining",
                target_state="running",
            )

            self._record_event(
                action="runtime_resume",
                status="completed",
            )

            return self.snapshot()

    async def stop(
        self,
    ) -> RuntimeLifecycleSnapshot:
        async with self._lock:
            if self._phase is RuntimeLifecyclePhase.STOPPED:
                return self.snapshot()

            self._assert_phase(
                RuntimeLifecyclePhase.INITIALIZING,
                RuntimeLifecyclePhase.READY,
                RuntimeLifecyclePhase.RUNNING,
                RuntimeLifecyclePhase.DRAINING,
                RuntimeLifecyclePhase.FAILED,
            )

            previous_phase = self._phase
            previous_kernel_state = (
                previous_phase.value
            )

            self._phase = RuntimeLifecyclePhase.STOPPING

            self._kernel.transition_state(
                expected_state=previous_kernel_state,
                target_state="stopping",
            )

            self._record_event(
                action="runtime_stop",
                status="started",
            )

            reverse_order = self._service_order(
                reverse=True
            )

            failures: list[str] = []

            stop_failures = await self._run_service_action(
                action="stop",
                service_order=reverse_order,
                timeout_seconds=(
                    self._shutdown_timeout_seconds
                ),
                continue_after_critical_failure=True,
            )

            failures.extend(stop_failures)

            close_failures = await self._run_service_action(
                action="close",
                service_order=reverse_order,
                timeout_seconds=(
                    self._shutdown_timeout_seconds
                ),
                continue_after_critical_failure=True,
            )

            failures.extend(close_failures)

            self._phase = RuntimeLifecyclePhase.STOPPED

            self._kernel.transition_state(
                expected_state="stopping",
                target_state="stopped",
            )

            self._record_event(
                action="runtime_stop",
                status=(
                    "completed_with_failures"
                    if failures
                    else "completed"
                ),
                detail=(
                    "; ".join(failures)
                    if failures
                    else None
                ),
            )

            snapshot = self.snapshot()

            if failures:
                raise RuntimeLifecycleShutdownError(
                    tuple(failures)
                )

            return snapshot

    async def shutdown(
        self,
    ) -> RuntimeLifecycleSnapshot:
        """Alias for stop(), used by application shutdown wiring."""

        return await self.stop()

    def snapshot(
        self,
    ) -> RuntimeLifecycleSnapshot:
        return RuntimeLifecycleSnapshot(
            phase=self._phase,
            generation=self._generation,
            initialized_services=tuple(
                sorted(self._initialized_services)
            ),
            started_services=tuple(
                sorted(self._started_services)
            ),
            failed_services=tuple(
                sorted(self._failed_services)
            ),
            failure_reason=self._failure_reason,
            event_count=len(self._events),
            events=tuple(self._events),
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
        "RuntimeLifecycleEvent",
        "RuntimeLifecycleSnapshot",
        "RuntimeLifecyclePhase",
        "RuntimeLifecycleManager",
        "RuntimeLifecycleError",
        "RuntimeLifecycleStateError",
        "RuntimeLifecycleServiceError",
        "RuntimeLifecycleTimeoutError",
        "RuntimeLifecycleShutdownError",
    }

    required_manager_methods = {
        "initialize",
        "start",
        "drain",
        "resume",
        "stop",
        "shutdown",
        "snapshot",
        "_record_event",
        "_assert_phase",
        "_service_metadata",
        "_service_order",
        "_resolve_hook",
        "_execute_hook",
        "_run_service_action",
        "_enter_failed",
    }

    missing_classes = sorted(
        required_classes - set(classes)
    )

    missing_methods = sorted(
        required_manager_methods
        - classes.get(
            "RuntimeLifecycleManager",
            set(),
        )
    )

    if missing_classes:
        fail(
            "Runtime lifecycle AST contract is "
            "missing classes: "
            + ", ".join(missing_classes)
        )

    if missing_methods:
        fail(
            "RuntimeLifecycleManager is missing methods: "
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
            "Runtime lifecycle manager contains "
            "pipeline-specific business terms: "
            + ", ".join(detected_forbidden_terms)
        )

    return {
        "required_classes": sorted(required_classes),
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
    lifecycle_module: Any,
    registry_module: Any,
    kernel_module: Any,
) -> dict[str, Any]:
    LifecycleManager = (
        lifecycle_module.RuntimeLifecycleManager
    )

    LifecyclePhase = (
        lifecycle_module.RuntimeLifecyclePhase
    )

    LifecycleStateError = (
        lifecycle_module.RuntimeLifecycleStateError
    )

    LifecycleServiceError = (
        lifecycle_module.RuntimeLifecycleServiceError
    )

    LifecycleTimeoutError = (
        lifecycle_module.RuntimeLifecycleTimeoutError
    )

    Registry = registry_module.RuntimeServiceRegistry
    Kernel = kernel_module.UniversalRuntimeKernel

    assertions: dict[str, str] = {}

    class ExampleService:
        def __init__(
            self,
            *,
            name: str,
            trace: list[str],
            ready_result: bool = True,
            fail_action: str | None = None,
            delay_action: str | None = None,
            delay_seconds: float = 0.0,
        ) -> None:
            self.name = name
            self.trace = trace
            self.ready_result = ready_result
            self.fail_action = fail_action
            self.delay_action = delay_action
            self.delay_seconds = delay_seconds

        async def _action(
            self,
            action: str,
        ) -> Any:
            self.trace.append(
                f"{self.name}.{action}"
            )

            if (
                self.delay_action == action
                and self.delay_seconds > 0
            ):
                await asyncio.sleep(
                    self.delay_seconds
                )

            if self.fail_action == action:
                raise RuntimeError(
                    f"{self.name} failed {action}"
                )

            if action == "ready":
                return self.ready_result

            return None

        async def initialize(self) -> None:
            await self._action("initialize")

        async def ready(self) -> bool:
            result = await self._action("ready")
            return bool(result)

        async def start(self) -> None:
            await self._action("start")

        async def drain(self) -> None:
            await self._action("drain")

        async def resume(self) -> None:
            await self._action("resume")

        async def stop(self) -> None:
            await self._action("stop")

        async def close(self) -> None:
            await self._action("close")

    async def normal_lifecycle_test() -> dict[str, Any]:
        trace: list[str] = []

        registry = Registry()

        registry.register(
            "state.store",
            ExampleService(
                name="state",
                trace=trace,
            ),
            startup_order=10,
            critical=True,
        )

        registry.register(
            "event.store",
            ExampleService(
                name="event",
                trace=trace,
            ),
            dependencies=[
                "state.store",
            ],
            startup_order=20,
            critical=True,
        )

        registry.register(
            "metrics.service",
            ExampleService(
                name="metrics",
                trace=trace,
            ),
            dependencies=[
                "event.store",
            ],
            startup_order=30,
            critical=False,
        )

        registry.seal()

        kernel = Kernel(
            runtime_id="linkcraftor.primary",
            product_name="LinkCraftor",
        )

        kernel.bind_component(
            "service_registry",
            registry,
        )

        manager = LifecycleManager(
            kernel=kernel,
            service_registry=registry,
            startup_timeout_seconds=1.0,
            shutdown_timeout_seconds=1.0,
        )

        kernel.bind_component(
            "lifecycle_manager",
            manager,
        )

        await manager.initialize()

        if manager.phase is not LifecyclePhase.READY:
            fail(
                "Lifecycle manager did not reach READY."
            )

        expected_initialization = [
            "state.initialize",
            "event.initialize",
            "metrics.initialize",
            "state.ready",
            "event.ready",
            "metrics.ready",
        ]

        if trace != expected_initialization:
            fail(
                "Initialization/readiness order is incorrect: "
                f"{trace!r}"
            )

        assertions[
            "ordered_initialization_and_readiness"
        ] = "PASS"

        await manager.start()

        if manager.phase is not LifecyclePhase.RUNNING:
            fail(
                "Lifecycle manager did not reach RUNNING."
            )

        expected_start_tail = [
            "state.start",
            "event.start",
            "metrics.start",
        ]

        if trace[-3:] != expected_start_tail:
            fail(
                "Service startup order is incorrect."
            )

        assertions[
            "dependency_ordered_startup"
        ] = "PASS"

        await manager.drain()

        if manager.phase is not LifecyclePhase.DRAINING:
            fail(
                "Lifecycle manager did not reach DRAINING."
            )

        if trace[-3:] != [
            "metrics.drain",
            "event.drain",
            "state.drain",
        ]:
            fail(
                "Service drain order was not reversed."
            )

        assertions[
            "reverse_dependency_drain"
        ] = "PASS"

        await manager.resume()

        if manager.phase is not LifecyclePhase.RUNNING:
            fail(
                "Lifecycle manager did not resume RUNNING."
            )

        if trace[-3:] != [
            "state.resume",
            "event.resume",
            "metrics.resume",
        ]:
            fail(
                "Service resume order is incorrect."
            )

        assertions[
            "dependency_ordered_resume"
        ] = "PASS"

        snapshot = manager.snapshot()

        if snapshot.phase is not LifecyclePhase.RUNNING:
            fail(
                "Lifecycle snapshot phase is incorrect."
            )

        snapshot_immutable = False

        try:
            snapshot.failure_reason = "illegal"
        except (AttributeError, TypeError):
            snapshot_immutable = True

        if not snapshot_immutable:
            fail(
                "Lifecycle snapshot was mutable."
            )

        assertions[
            "immutable_lifecycle_snapshot"
        ] = "PASS"

        await manager.stop()

        if manager.phase is not LifecyclePhase.STOPPED:
            fail(
                "Lifecycle manager did not reach STOPPED."
            )

        expected_shutdown_tail = [
            "metrics.stop",
            "event.stop",
            "state.stop",
            "metrics.close",
            "event.close",
            "state.close",
        ]

        if trace[-6:] != expected_shutdown_tail:
            fail(
                "Reverse-order stop/close sequence "
                "is incorrect."
            )

        assertions[
            "reverse_dependency_shutdown"
        ] = "PASS"

        if kernel.state.value != "stopped":
            fail(
                "Kernel state did not synchronize "
                "with lifecycle shutdown."
            )

        assertions[
            "kernel_state_synchronization"
        ] = "PASS"

        stopped_snapshot = await manager.stop()

        if stopped_snapshot.phase is not LifecyclePhase.STOPPED:
            fail(
                "Idempotent stop did not preserve STOPPED."
            )

        assertions[
            "idempotent_stopped_shutdown"
        ] = "PASS"

        return {
            "trace": trace,
            "event_count": (
                manager.snapshot().event_count
            ),
            "kernel_generation": kernel.generation,
        }

    async def unsealed_registry_test() -> None:
        registry = Registry()

        registry.register(
            "state.store",
            object(),
        )

        kernel = Kernel(
            runtime_id="linkcraftor.unsealed",
            product_name="LinkCraftor",
        )

        manager = LifecycleManager(
            kernel=kernel,
            service_registry=registry,
        )

        rejected = False

        try:
            await manager.initialize()
        except LifecycleStateError:
            rejected = True

        if not rejected:
            fail(
                "Initialization accepted an unsealed registry."
            )

        assertions[
            "sealed_registry_requirement"
        ] = "PASS"

    async def concurrent_transition_test() -> None:
        trace: list[str] = []
        registry = Registry()

        registry.register(
            "slow.service",
            ExampleService(
                name="slow",
                trace=trace,
                delay_action="initialize",
                delay_seconds=0.03,
            ),
        )

        registry.seal()

        kernel = Kernel(
            runtime_id="linkcraftor.concurrent",
            product_name="LinkCraftor",
        )

        manager = LifecycleManager(
            kernel=kernel,
            service_registry=registry,
            startup_timeout_seconds=1.0,
        )

        results = await asyncio.gather(
            manager.initialize(),
            manager.initialize(),
            return_exceptions=True,
        )

        exception_count = sum(
            isinstance(
                result,
                LifecycleStateError,
            )
            for result in results
        )

        success_count = sum(
            not isinstance(result, BaseException)
            for result in results
        )

        if success_count != 1 or exception_count != 1:
            fail(
                "Concurrent lifecycle transitions "
                "were not serialized correctly."
            )

        assertions[
            "concurrent_transition_protection"
        ] = "PASS"

        await manager.stop()

    async def noncritical_failure_test() -> None:
        trace: list[str] = []
        registry = Registry()

        registry.register(
            "critical.service",
            ExampleService(
                name="critical",
                trace=trace,
            ),
            critical=True,
        )

        registry.register(
            "optional.service",
            ExampleService(
                name="optional",
                trace=trace,
                fail_action="start",
            ),
            dependencies=[
                "critical.service",
            ],
            critical=False,
        )

        registry.seal()

        kernel = Kernel(
            runtime_id="linkcraftor.noncritical",
            product_name="LinkCraftor",
        )

        manager = LifecycleManager(
            kernel=kernel,
            service_registry=registry,
        )

        await manager.initialize()
        await manager.start()

        if manager.phase is not LifecyclePhase.RUNNING:
            fail(
                "A noncritical service failure stopped "
                "the runtime."
            )

        if (
            "optional.service"
            not in manager.snapshot().failed_services
        ):
            fail(
                "Noncritical service failure was not recorded."
            )

        assertions[
            "noncritical_failure_tolerance"
        ] = "PASS"

        await manager.stop()

    async def critical_failure_test() -> None:
        trace: list[str] = []
        registry = Registry()

        registry.register(
            "critical.service",
            ExampleService(
                name="critical",
                trace=trace,
                fail_action="start",
            ),
            critical=True,
        )

        registry.seal()

        kernel = Kernel(
            runtime_id="linkcraftor.critical",
            product_name="LinkCraftor",
        )

        manager = LifecycleManager(
            kernel=kernel,
            service_registry=registry,
        )

        await manager.initialize()

        rejected = False

        try:
            await manager.start()
        except LifecycleServiceError:
            rejected = True

        if not rejected:
            fail(
                "Critical service failure did not "
                "fail runtime startup."
            )

        if manager.phase is not LifecyclePhase.FAILED:
            fail(
                "Lifecycle manager did not enter FAILED."
            )

        if kernel.state.value != "failed":
            fail(
                "Kernel did not enter FAILED."
            )

        assertions[
            "critical_failure_propagation"
        ] = "PASS"

        await manager.stop()

    async def timeout_test() -> None:
        trace: list[str] = []
        registry = Registry()

        registry.register(
            "timeout.service",
            ExampleService(
                name="timeout",
                trace=trace,
                delay_action="start",
                delay_seconds=0.1,
            ),
            critical=True,
        )

        registry.seal()

        kernel = Kernel(
            runtime_id="linkcraftor.timeout",
            product_name="LinkCraftor",
        )

        manager = LifecycleManager(
            kernel=kernel,
            service_registry=registry,
            startup_timeout_seconds=0.01,
            shutdown_timeout_seconds=1.0,
        )

        await manager.initialize()

        timeout_rejected = False

        try:
            await manager.start()
        except LifecycleTimeoutError:
            timeout_rejected = True

        if not timeout_rejected:
            fail(
                "Service startup timeout was not enforced."
            )

        if manager.phase is not LifecyclePhase.FAILED:
            fail(
                "Timeout did not move lifecycle to FAILED."
            )

        assertions[
            "startup_timeout_enforcement"
        ] = "PASS"

        await manager.stop()

    async def run_all() -> dict[str, Any]:
        normal_results = await normal_lifecycle_test()
        await unsealed_registry_test()
        await concurrent_transition_test()
        await noncritical_failure_test()
        await critical_failure_test()
        await timeout_test()

        return normal_results

    normal_results = asyncio.run(run_all())

    return {
        "assertions": assertions,
        "normal_trace": normal_results["trace"],
        "normal_event_count": (
            normal_results["event_count"]
        ),
        "normal_kernel_generation": (
            normal_results["kernel_generation"]
        ),
    }


def rollback(
    *,
    target_existed: bool,
) -> None:
    if target_existed:
        if not BACKUP_TARGET.exists():
            raise RuntimeError(
                "Runtime lifecycle rollback backup "
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
    print("1.1.5 — RUNTIME LIFECYCLE MANAGER BUILD")
    print("=" * 78)
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Target:       {TARGET}")
    print()

    required_files = [
        KERNEL_FILE,
        CONFIGURATION_FILE,
        ENVIRONMENT_FILE,
        SERVICE_REGISTRY_FILE,
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
        "service_registry": sha256_file(
            SERVICE_REGISTRY_FILE
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
            "Existing runtime lifecycle manager "
            "backed up:"
        )
        print(BACKUP_TARGET)
        print()

    TARGET.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    lifecycle_module_name = (
        "_uri_phase_1_1_5_runtime_lifecycle_test"
    )

    registry_module_name = (
        "_uri_phase_1_1_5_runtime_registry_test"
    )

    kernel_module_name = (
        "_uri_phase_1_1_5_runtime_kernel_test"
    )

    try:
        TARGET.write_text(
            LIFECYCLE_SOURCE,
            encoding="utf-8",
            newline="\n",
        )

        for source_file in required_files:
            py_compile.compile(
                str(source_file),
                doraise=True,
            )

        py_compile.compile(
            str(TARGET),
            doraise=True,
        )

        ast_contract = verify_ast_contract(TARGET)

        lifecycle_module = load_module(
            TARGET,
            lifecycle_module_name,
        )

        registry_module = load_module(
            SERVICE_REGISTRY_FILE,
            registry_module_name,
        )

        kernel_module = load_module(
            KERNEL_FILE,
            kernel_module_name,
        )

        behavioral_results = verify_behavior(
            lifecycle_module,
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
            "service_registry": sha256_file(
                SERVICE_REGISTRY_FILE
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
            "Runtime lifecycle verification failed. "
            "The previous filesystem state was restored."
        )
        raise

    finally:
        unload_module(lifecycle_module_name)
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
            "lifecycle_py_compile": "PASS",
            "foundation_files_compile": "PASS",
            "main_py_compile": "PASS",
            "ast_contract": "PASS",
            "behavioral_contract": "PASS",
            "ordered_initialization": "PASS",
            "readiness_checks": "PASS",
            "ordered_startup": "PASS",
            "drain_resume_contract": "PASS",
            "reverse_shutdown": "PASS",
            "critical_failure_contract": "PASS",
            "noncritical_failure_contract": "PASS",
            "timeout_contract": "PASS",
            "concurrent_transition_protection": "PASS",
            "kernel_state_synchronization": "PASS",
            "business_logic_agnostic_test": "PASS",
            "protected_files_unchanged": "PASS",
            "automatic_rollback_required": False,
        },
        "ast_contract_details": ast_contract,
        "behavioral_results": behavioral_results,
        "phase_status": {
            "phase": "1",
            "item": "1.1.5",
            "name": "Runtime Lifecycle Manager",
            "implementation_status": "IMPLEMENTED",
            "verification_status": "PASS",
            "kernel_binding_status": "PASS",
            "application_boot_integration": "PENDING",
            "application_shutdown_integration": "PENDING",
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
        "1.1.5 — RUNTIME LIFECYCLE MANAGER EVIDENCE",
        "=" * 78,
        "",
        f"Build version: {BUILD_VERSION}",
        f"Timestamp UTC: {evidence['timestamp_utc']}",
        f"Target: {TARGET}",
        "",
        "VERIFICATION",
        "-" * 78,
        "Runtime Lifecycle Manager compilation: PASS",
        "Existing Phase 1 foundation compilation: PASS",
        "main.py compilation: PASS",
        "Lifecycle AST contract: PASS",
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
            "CHECKLIST POSITION",
            "-" * 78,
            "1.1.1 kernel implementation: PASS",
            "1.1.2 configuration implementation: PASS",
            "1.1.3 environment implementation: PASS",
            "1.1.4 service registry implementation: PASS",
            "1.1.5 implementation: PASS",
            "1.1.5 isolated verification: PASS",
            "1.1.5 kernel-state synchronization: PASS",
            (
                "1.1.5 application boot integration: "
                "PENDING"
            ),
            (
                "1.1.5 application shutdown integration: "
                "PENDING"
            ),
            "1.1.5 certification: NOT CERTIFIED",
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
        "Runtime Lifecycle Manager compilation: PASS"
    )
    print(
        "Phase 1 foundation compilation:        PASS"
    )
    print(
        "main.py compilation:                   PASS"
    )
    print(
        "Lifecycle AST contract:                PASS"
    )
    print(
        "Lifecycle behavioral contract:         PASS"
    )
    print(
        "Ordered initialization/readiness:      PASS"
    )
    print(
        "Dependency-ordered startup:            PASS"
    )
    print(
        "Drain and resume coordination:         PASS"
    )
    print(
        "Reverse-order shutdown and cleanup:    PASS"
    )
    print(
        "Critical failure propagation:          PASS"
    )
    print(
        "Noncritical failure tolerance:         PASS"
    )
    print(
        "Startup timeout enforcement:           PASS"
    )
    print(
        "Concurrent transition protection:      PASS"
    )
    print(
        "Kernel-state synchronization:          PASS"
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
    print(f"Lifecycle manager: {TARGET}")
    print(f"Evidence JSON:      {EVIDENCE_JSON}")
    print(f"Evidence text:      {EVIDENCE_TEXT}")
    print()

    print("1.1.5 RUNTIME LIFECYCLE MANAGER")
    print("IMPLEMENTATION: PASS")
    print("ISOLATED VERIFICATION: PASS")
    print("KERNEL-STATE SYNCHRONIZATION: PASS")
    print("APPLICATION BOOT INTEGRATION: PENDING")
    print("APPLICATION SHUTDOWN INTEGRATION: PENDING")
    print("CERTIFICATION: NOT CERTIFIED")
    print()
    print("NO PRODUCTION DATA WAS MODIFIED")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
