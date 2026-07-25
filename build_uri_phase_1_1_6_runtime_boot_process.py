from __future__ import annotations

import ast
import asyncio
import hashlib
import importlib
import json
import os
import py_compile
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BUILD_VERSION = "uri_phase_1_1_6_runtime_boot_process_v1"

PROJECT_ROOT = Path.cwd().resolve()

TARGET = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "runtime"
    / "runtime_boot_process.py"
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
    / f"uri_phase1_1_6_runtime_boot_process_{TIMESTAMP}"
)

BACKUP_TARGET = (
    BACKUP_ROOT
    / "backend"
    / "server"
    / "runtime"
    / "runtime_boot_process.py"
)

EVIDENCE_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime"
    / "uri_phase_1"
    / "1_1_6_runtime_boot_process"
)

EVIDENCE_JSON = (
    EVIDENCE_ROOT
    / f"runtime_boot_process_build_{TIMESTAMP}.json"
)

EVIDENCE_TEXT = (
    EVIDENCE_ROOT
    / f"runtime_boot_process_build_{TIMESTAMP}.txt"
)


BOOT_SOURCE = r'''from __future__ import annotations

"""
Universal Runtime Boot Process.

This module composes and starts the Universal Runtime foundation in a
strict and deterministic order.

It does not run during module import, create detached tasks, execute
jobs, implement pipeline stages, or contain product business logic.
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping, Protocol, Sequence
from uuid import uuid4

from backend.server.runtime.runtime_configuration import (
    RuntimeConfiguration,
    RuntimeConfigurationLoader,
)
from backend.server.runtime.runtime_environment import (
    RuntimeEnvironmentManager,
)
from backend.server.runtime.runtime_lifecycle_manager import (
    RuntimeLifecycleManager,
    RuntimeLifecyclePhase,
)
from backend.server.runtime.runtime_service_registry import (
    RuntimeServiceRegistry,
)
from backend.server.runtime.universal_runtime_kernel import (
    UniversalRuntimeKernel,
)


__all__ = [
    "BOOT_REQUIRED_COMPONENT_KEYS",
    "RuntimeBootComposition",
    "RuntimeBootConfigurationError",
    "RuntimeBootContext",
    "RuntimeBootError",
    "RuntimeBootEvent",
    "RuntimeBootFailureError",
    "RuntimeBootProcess",
    "RuntimeBootSnapshot",
    "RuntimeBootStatus",
    "RuntimeServiceRegistrar",
    "boot_runtime",
]


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


BOOT_REQUIRED_COMPONENT_KEYS: tuple[str, ...] = (
    "configuration",
    "environment",
    "service_registry",
    "lifecycle_manager",
)


class RuntimeBootError(RuntimeError):
    """Base runtime-boot failure."""


class RuntimeBootConfigurationError(
    RuntimeBootError
):
    """Raised when the boot controller is configured incorrectly."""


class RuntimeBootFailureError(
    RuntimeBootError
):
    """Raised when runtime composition or startup fails."""

    def __init__(
        self,
        *,
        stage: str,
        cause: BaseException,
    ) -> None:
        self.stage = stage
        self.cause = cause

        super().__init__(
            f"Runtime boot failed during {stage!r}: "
            f"{type(cause).__name__}: {cause}"
        )


class RuntimeBootStatus(str, Enum):
    IDLE = "idle"
    BOOTING = "booting"
    RUNNING = "running"
    FAILED = "failed"
    STOPPED = "stopped"


class RuntimeServiceRegistrar(Protocol):
    """
    Generic callback used to register runtime services.

    Product-stage and job-handler registration remains separate from
    this runtime-service registration boundary.
    """

    def __call__(
        self,
        composition: "RuntimeBootComposition",
    ) -> None:
        ...


@dataclass(frozen=True, slots=True)
class RuntimeBootComposition:
    """Foundation objects available during service registration."""

    project_root: Path
    configuration: RuntimeConfiguration
    environment: RuntimeEnvironmentManager
    kernel: UniversalRuntimeKernel
    service_registry: RuntimeServiceRegistry


@dataclass(frozen=True, slots=True)
class RuntimeBootContext:
    """Immutable result of a successful runtime boot."""

    boot_id: str
    attempt: int
    project_root: Path
    configuration: RuntimeConfiguration
    environment: RuntimeEnvironmentManager
    kernel: UniversalRuntimeKernel
    service_registry: RuntimeServiceRegistry
    lifecycle_manager: RuntimeLifecycleManager
    service_keys: tuple[str, ...]
    booted_at: datetime


@dataclass(frozen=True, slots=True)
class RuntimeBootEvent:
    """Immutable runtime-boot event."""

    sequence: int
    timestamp: datetime
    status: RuntimeBootStatus
    stage: str
    outcome: str
    detail: str | None


@dataclass(frozen=True, slots=True)
class RuntimeBootSnapshot:
    """Immutable point-in-time boot inspection record."""

    status: RuntimeBootStatus
    attempt: int
    boot_id: str | None
    stage: str
    generation: int
    event_count: int
    events: tuple[RuntimeBootEvent, ...]
    runtime_id: str | None
    environment: str | None
    service_count: int
    kernel_state: str | None
    lifecycle_phase: str | None
    missing_foundation_components: tuple[str, ...]
    failure_reason: str | None


class RuntimeBootProcess:
    """
    Compose and start the Universal Runtime foundation.

    Composition order:

    1. Load Runtime Configuration.
    2. Validate Runtime Environment.
    3. Create Universal Runtime Kernel.
    4. Create and bind Runtime Service Registry.
    5. Execute controlled service registrars.
    6. Create and bind Runtime Lifecycle Manager.
    7. Validate required kernel components.
    8. Seal the service registry.
    9. Initialize services.
    10. Start services.
    11. Publish immutable boot context.

    Concurrent boot requests are serialized through one asyncio lock.
    Once running, repeated boot requests return the existing context.
    """

    __slots__ = (
        "_project_root",
        "_environ",
        "_overrides",
        "_registrars",
        "_event_limit",
        "_status",
        "_attempt",
        "_boot_id",
        "_stage",
        "_generation",
        "_events",
        "_context",
        "_failure_reason",
        "_lock",
    )

    def __init__(
        self,
        *,
        project_root: Path,
        environ: Mapping[str, str] | None = None,
        overrides: Mapping[str, Any] | None = None,
        service_registrars: Sequence[
            RuntimeServiceRegistrar
        ] = (),
        event_limit: int = 500,
    ) -> None:
        resolved_root = (
            Path(project_root)
            .expanduser()
            .resolve()
        )

        if (
            not resolved_root.exists()
            or not resolved_root.is_dir()
        ):
            raise RuntimeBootConfigurationError(
                "project_root must be an existing "
                f"directory: {resolved_root}"
            )

        if isinstance(event_limit, bool):
            raise RuntimeBootConfigurationError(
                "event_limit must be an integer."
            )

        resolved_event_limit = int(event_limit)

        if not 10 <= resolved_event_limit <= 100000:
            raise RuntimeBootConfigurationError(
                "event_limit must be between 10 and 100000."
            )

        registrars = tuple(service_registrars)

        invalid_registrar_indexes = tuple(
            index
            for index, registrar in enumerate(registrars)
            if not callable(registrar)
        )

        if invalid_registrar_indexes:
            raise RuntimeBootConfigurationError(
                "All service registrars must be callable. "
                "Invalid indexes: "
                + ", ".join(
                    str(index)
                    for index in invalid_registrar_indexes
                )
            )

        self._project_root = resolved_root

        self._environ = (
            None
            if environ is None
            else MappingProxyType(
                dict(environ)
            )
        )

        self._overrides = MappingProxyType(
            dict(overrides or {})
        )

        self._registrars = registrars
        self._event_limit = resolved_event_limit
        self._status = RuntimeBootStatus.IDLE
        self._attempt = 0
        self._boot_id: str | None = None
        self._stage = "idle"
        self._generation = 0
        self._events: list[RuntimeBootEvent] = []
        self._context: RuntimeBootContext | None = None
        self._failure_reason: str | None = None
        self._lock = asyncio.Lock()

    @property
    def status(self) -> RuntimeBootStatus:
        return self._status

    @property
    def current_context(
        self,
    ) -> RuntimeBootContext | None:
        return self._context

    def _record_event(
        self,
        *,
        stage: str,
        outcome: str,
        detail: str | None = None,
    ) -> RuntimeBootEvent:
        self._generation += 1
        self._stage = str(stage)

        event = RuntimeBootEvent(
            sequence=self._generation,
            timestamp=_utc_now(),
            status=self._status,
            stage=self._stage,
            outcome=str(outcome),
            detail=detail,
        )

        self._events.append(event)

        if len(self._events) > self._event_limit:
            overflow = (
                len(self._events)
                - self._event_limit
            )

            del self._events[:overflow]

        return event

    @staticmethod
    def _registrar_name(
        registrar: RuntimeServiceRegistrar,
    ) -> str:
        return str(
            getattr(
                registrar,
                "__qualname__",
                None,
            )
            or getattr(
                registrar,
                "__name__",
                None,
            )
            or type(registrar).__qualname__
        )

    async def _cleanup_failed_boot(
        self,
        *,
        kernel: UniversalRuntimeKernel | None,
        lifecycle_manager: (
            RuntimeLifecycleManager | None
        ),
    ) -> tuple[str, ...]:
        """
        Perform best-effort cleanup after failed composition or startup.
        """

        failures: list[str] = []

        if (
            lifecycle_manager is not None
            and lifecycle_manager.phase
            not in {
                RuntimeLifecyclePhase.CREATED,
                RuntimeLifecyclePhase.STOPPED,
            }
        ):
            try:
                await lifecycle_manager.stop()
            except Exception as exc:
                failures.append(
                    "lifecycle_cleanup="
                    f"{type(exc).__name__}: {exc}"
                )

        elif (
            kernel is not None
            and kernel.state.value
            not in {
                "failed",
                "stopped",
                "stopping",
            }
        ):
            try:
                kernel.mark_failed(
                    self._failure_reason
                    or "runtime boot failure"
                )
            except Exception as exc:
                failures.append(
                    "kernel_failure_mark="
                    f"{type(exc).__name__}: {exc}"
                )

        return tuple(failures)

    async def boot(
        self,
    ) -> RuntimeBootContext:
        """
        Compose and start the runtime.

        The asyncio lock creates a single-flight boot boundary. A second
        caller waits for the first caller and then receives the same
        successful context.
        """

        async with self._lock:
            if (
                self._status
                is RuntimeBootStatus.RUNNING
                and self._context is not None
            ):
                self._record_event(
                    stage="boot",
                    outcome="already_running",
                    detail=self._context.boot_id,
                )

                return self._context

            self._attempt += 1
            self._boot_id = (
                f"runtime_boot_{uuid4().hex}"
            )
            self._status = RuntimeBootStatus.BOOTING
            self._failure_reason = None
            self._context = None

            self._record_event(
                stage="boot",
                outcome="started",
                detail=f"attempt={self._attempt}",
            )

            kernel: UniversalRuntimeKernel | None = None

            lifecycle_manager: (
                RuntimeLifecycleManager | None
            ) = None

            stage = "configuration"

            try:
                loader = RuntimeConfigurationLoader(
                    project_root=self._project_root
                )

                configuration = loader.load(
                    environ=self._environ,
                    overrides=self._overrides,
                )

                self._record_event(
                    stage=stage,
                    outcome="completed",
                    detail=configuration.fingerprint(),
                )

                stage = "environment"

                environment = RuntimeEnvironmentManager(
                    configuration
                )

                self._record_event(
                    stage=stage,
                    outcome="completed",
                    detail=environment.name.value,
                )

                stage = "kernel"

                kernel = UniversalRuntimeKernel(
                    runtime_id=configuration.runtime_id,
                    product_name=configuration.product_name,
                )

                kernel.bind_component(
                    "configuration",
                    configuration,
                )

                kernel.bind_component(
                    "environment",
                    environment,
                )

                self._record_event(
                    stage=stage,
                    outcome="completed",
                    detail=configuration.runtime_id,
                )

                stage = "service_registry"

                service_registry = (
                    RuntimeServiceRegistry()
                )

                kernel.bind_component(
                    "service_registry",
                    service_registry,
                )

                self._record_event(
                    stage=stage,
                    outcome="created",
                )

                stage = "service_registration"

                composition = RuntimeBootComposition(
                    project_root=self._project_root,
                    configuration=configuration,
                    environment=environment,
                    kernel=kernel,
                    service_registry=service_registry,
                )

                for registrar in self._registrars:
                    registrar_name = (
                        self._registrar_name(
                            registrar
                        )
                    )

                    registrar(composition)

                    self._record_event(
                        stage=stage,
                        outcome="registrar_completed",
                        detail=registrar_name,
                    )

                stage = "lifecycle_manager"

                lifecycle_manager = (
                    RuntimeLifecycleManager(
                        kernel=kernel,
                        service_registry=(
                            service_registry
                        ),
                        startup_timeout_seconds=(
                            configuration
                            .startup_timeout_seconds
                        ),
                        shutdown_timeout_seconds=(
                            configuration
                            .shutdown_timeout_seconds
                        ),
                    )
                )

                kernel.bind_component(
                    "lifecycle_manager",
                    lifecycle_manager,
                )

                kernel.require_components(
                    list(
                        BOOT_REQUIRED_COMPONENT_KEYS
                    )
                )

                self._record_event(
                    stage=stage,
                    outcome="completed",
                )

                stage = "registry_seal"

                registry_snapshot = (
                    service_registry.seal()
                )

                self._record_event(
                    stage=stage,
                    outcome="completed",
                    detail=(
                        "services="
                        f"{registry_snapshot.service_count}"
                    ),
                )

                stage = "lifecycle_initialize"

                await lifecycle_manager.initialize()

                self._record_event(
                    stage=stage,
                    outcome="completed",
                )

                stage = "lifecycle_start"

                await lifecycle_manager.start()

                self._record_event(
                    stage=stage,
                    outcome="completed",
                )

                stage = "finalize"

                service_keys = (
                    service_registry
                    .dependency_order()
                )

                context = RuntimeBootContext(
                    boot_id=self._boot_id,
                    attempt=self._attempt,
                    project_root=self._project_root,
                    configuration=configuration,
                    environment=environment,
                    kernel=kernel,
                    service_registry=(
                        service_registry
                    ),
                    lifecycle_manager=(
                        lifecycle_manager
                    ),
                    service_keys=service_keys,
                    booted_at=_utc_now(),
                )

                self._context = context
                self._status = (
                    RuntimeBootStatus.RUNNING
                )

                self._record_event(
                    stage=stage,
                    outcome="completed",
                    detail=self._boot_id,
                )

                return context

            except Exception as exc:
                self._status = (
                    RuntimeBootStatus.FAILED
                )

                self._failure_reason = (
                    f"{type(exc).__name__}: {exc}"
                )

                self._record_event(
                    stage=stage,
                    outcome="failed",
                    detail=self._failure_reason,
                )

                cleanup_failures = (
                    await self._cleanup_failed_boot(
                        kernel=kernel,
                        lifecycle_manager=(
                            lifecycle_manager
                        ),
                    )
                )

                if cleanup_failures:
                    self._record_event(
                        stage="failure_cleanup",
                        outcome=(
                            "completed_with_failures"
                        ),
                        detail="; ".join(
                            cleanup_failures
                        ),
                    )
                else:
                    self._record_event(
                        stage="failure_cleanup",
                        outcome="completed",
                    )

                raise RuntimeBootFailureError(
                    stage=stage,
                    cause=exc,
                ) from exc

    def snapshot(
        self,
    ) -> RuntimeBootSnapshot:
        context = self._context

        kernel = (
            None
            if context is None
            else context.kernel
        )

        lifecycle = (
            None
            if context is None
            else context.lifecycle_manager
        )

        configuration = (
            None
            if context is None
            else context.configuration
        )

        registry = (
            None
            if context is None
            else context.service_registry
        )

        return RuntimeBootSnapshot(
            status=self._status,
            attempt=self._attempt,
            boot_id=self._boot_id,
            stage=self._stage,
            generation=self._generation,
            event_count=len(self._events),
            events=tuple(self._events),
            runtime_id=(
                None
                if configuration is None
                else configuration.runtime_id
            ),
            environment=(
                None
                if configuration is None
                else configuration.environment
            ),
            service_count=(
                0
                if registry is None
                else registry.service_count
            ),
            kernel_state=(
                None
                if kernel is None
                else kernel.state.value
            ),
            lifecycle_phase=(
                None
                if lifecycle is None
                else lifecycle.phase.value
            ),
            missing_foundation_components=(
                ()
                if kernel is None
                else (
                    kernel
                    .missing_foundation_components()
                )
            ),
            failure_reason=self._failure_reason,
        )


async def boot_runtime(
    *,
    project_root: Path,
    environ: Mapping[str, str] | None = None,
    overrides: Mapping[str, Any] | None = None,
    service_registrars: Sequence[
        RuntimeServiceRegistrar
    ] = (),
) -> tuple[
    RuntimeBootProcess,
    RuntimeBootContext,
]:
    """
    Convenience entry point returning both controller and context.
    """

    process = RuntimeBootProcess(
        project_root=project_root,
        environ=environ,
        overrides=overrides,
        service_registrars=service_registrars,
    )

    context = await process.boot()

    return process, context
'''


def sha256_file(
    path: Path,
) -> str | None:
    if not path.exists():
        return None

    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def fail(
    message: str,
) -> None:
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

    classes: dict[
        str,
        set[str],
    ] = {}

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
        "RuntimeBootComposition",
        "RuntimeBootContext",
        "RuntimeBootEvent",
        "RuntimeBootSnapshot",
        "RuntimeBootProcess",
        "RuntimeBootStatus",
        "RuntimeBootError",
        "RuntimeBootConfigurationError",
        "RuntimeBootFailureError",
    }

    required_process_methods = {
        "boot",
        "snapshot",
        "_record_event",
        "_registrar_name",
        "_cleanup_failed_boot",
    }

    missing_classes = sorted(
        required_classes - set(classes)
    )

    missing_methods = sorted(
        required_process_methods
        - classes.get(
            "RuntimeBootProcess",
            set(),
        )
    )

    if missing_classes:
        fail(
            "Runtime boot AST contract is missing "
            "classes: "
            + ", ".join(missing_classes)
        )

    if missing_methods:
        fail(
            "RuntimeBootProcess is missing methods: "
            + ", ".join(missing_methods)
        )

    if "boot_runtime" not in functions:
        fail(
            "The boot_runtime convenience entry point "
            "is missing."
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
            "Runtime boot process contains "
            "pipeline-specific business terms: "
            + ", ".join(
                detected_forbidden_terms
            )
        )

    if "@app.on_event" in text:
        fail(
            "The boot module must not wire itself "
            "directly into the application."
        )

    if "asyncio.create_task" in text:
        fail(
            "The boot module must not create detached "
            "background tasks."
        )

    return {
        "required_classes": sorted(
            required_classes
        ),
        "missing_classes": missing_classes,
        "required_process_methods": sorted(
            required_process_methods
        ),
        "missing_process_methods": (
            missing_methods
        ),
        "boot_entry_point_present": True,
        "application_hook_detected": False,
        "detached_task_creation_detected": False,
        "pipeline_business_terms_detected": (
            detected_forbidden_terms
        ),
    }


def import_boot_module() -> Any:
    module_name = (
        "backend.server.runtime."
        "runtime_boot_process"
    )

    sys.modules.pop(
        module_name,
        None,
    )

    importlib.invalidate_caches()

    return importlib.import_module(
        module_name
    )


def verify_behavior(
    module: Any,
) -> dict[str, Any]:
    BootProcess = module.RuntimeBootProcess
    BootStatus = module.RuntimeBootStatus

    BootFailureError = (
        module.RuntimeBootFailureError
    )

    BootConfigurationError = (
        module.RuntimeBootConfigurationError
    )

    assertions: dict[str, str] = {}

    class TraceService:
        def __init__(
            self,
            *,
            name: str,
            trace: list[str],
            fail_action: str | None = None,
            delay_action: str | None = None,
            delay_seconds: float = 0.0,
        ) -> None:
            self.name = name
            self.trace = trace
            self.fail_action = fail_action
            self.delay_action = delay_action
            self.delay_seconds = delay_seconds

        async def _run(
            self,
            action: str,
        ) -> bool | None:
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
                return True

            return None

        async def initialize(
            self,
        ) -> None:
            await self._run("initialize")

        async def ready(
            self,
        ) -> bool:
            return bool(
                await self._run("ready")
            )

        async def start(
            self,
        ) -> None:
            await self._run("start")

        async def stop(
            self,
        ) -> None:
            await self._run("stop")

        async def close(
            self,
        ) -> None:
            await self._run("close")

    async def normal_boot_test(
        temporary_root: Path,
    ) -> dict[str, Any]:
        trace: list[str] = []

        registrar_calls = {
            "count": 0,
        }

        def registrar(
            composition: Any,
        ) -> None:
            registrar_calls["count"] += 1

            composition.service_registry.register(
                "state.store",
                TraceService(
                    name="state",
                    trace=trace,
                ),
                startup_order=10,
                critical=True,
            )

            composition.service_registry.register(
                "event.store",
                TraceService(
                    name="event",
                    trace=trace,
                ),
                dependencies=[
                    "state.store",
                ],
                startup_order=20,
                critical=True,
            )

        process = BootProcess(
            project_root=temporary_root,
            environ={
                (
                    "LINKCRAFTOR_RUNTIME_"
                    "ENVIRONMENT"
                ): "testing",
                (
                    "LINKCRAFTOR_RUNTIME_"
                    "DEBUG"
                ): "true",
                (
                    "LINKCRAFTOR_RUNTIME_"
                    "STATE_BACKEND"
                ): "memory",
                (
                    "LINKCRAFTOR_RUNTIME_"
                    "STRICT_COMPATIBILITY"
                ): "false",
                (
                    "LINKCRAFTOR_RUNTIME_"
                    "SCHEMA_AUTO_MIGRATE"
                ): "true",
            },
            overrides={
                "worker_enabled": False,
                "max_concurrency": 7,
            },
            service_registrars=[
                registrar,
            ],
        )

        context = await process.boot()

        if process.status is not BootStatus.RUNNING:
            fail(
                "Boot process did not reach RUNNING."
            )

        if (
            context.configuration.environment
            != "testing"
        ):
            fail(
                "Boot process did not resolve the "
                "configured environment."
            )

        if (
            context.configuration.max_concurrency
            != 7
        ):
            fail(
                "Boot overrides were not applied."
            )

        if context.environment.name.value != "testing":
            fail(
                "Runtime Environment Manager was not "
                "composed correctly."
            )

        if context.service_keys != (
            "state.store",
            "event.store",
        ):
            fail(
                "Boot service order is incorrect: "
                f"{context.service_keys!r}"
            )

        expected_trace = [
            "state.initialize",
            "event.initialize",
            "state.ready",
            "event.ready",
            "state.start",
            "event.start",
        ]

        if trace != expected_trace:
            fail(
                "Boot lifecycle trace is incorrect: "
                f"{trace!r}"
            )

        assertions[
            "deterministic_composition_and_startup"
        ] = "PASS"

        for key in (
            module.BOOT_REQUIRED_COMPONENT_KEYS
        ):
            if not context.kernel.has_component(
                key
            ):
                fail(
                    "Boot-required kernel component "
                    f"{key!r} is missing."
                )

        assertions[
            "required_kernel_bindings"
        ] = "PASS"

        if not context.service_registry.sealed:
            fail(
                "Boot process did not seal the "
                "service registry."
            )

        assertions[
            "registry_sealing_before_startup"
        ] = "PASS"

        second_context = await process.boot()

        if second_context is not context:
            fail(
                "Repeated boot returned a new context."
            )

        if registrar_calls["count"] != 1:
            fail(
                "Repeated boot executed service "
                "registration more than once."
            )

        assertions[
            "idempotent_boot"
        ] = "PASS"

        snapshot = process.snapshot()

        if snapshot.status is not BootStatus.RUNNING:
            fail(
                "Boot snapshot status is incorrect."
            )

        if snapshot.kernel_state != "running":
            fail(
                "Boot snapshot kernel state is incorrect."
            )

        if snapshot.lifecycle_phase != "running":
            fail(
                "Boot snapshot lifecycle phase "
                "is incorrect."
            )

        if snapshot.service_count != 2:
            fail(
                "Boot snapshot service count "
                "is incorrect."
            )

        snapshot_immutable = False

        try:
            snapshot.stage = "illegal"
        except (AttributeError, TypeError):
            snapshot_immutable = True

        if not snapshot_immutable:
            fail(
                "Boot snapshot was mutable."
            )

        assertions[
            "immutable_boot_snapshot"
        ] = "PASS"

        await context.lifecycle_manager.stop()

        return {
            "event_count": snapshot.event_count,
            "boot_id": context.boot_id,
            "trace": trace,
            "missing_foundation_components": list(
                snapshot
                .missing_foundation_components
            ),
        }

    async def concurrent_boot_test(
        temporary_root: Path,
    ) -> None:
        trace: list[str] = []

        registrar_calls = {
            "count": 0,
        }

        def registrar(
            composition: Any,
        ) -> None:
            registrar_calls["count"] += 1

            composition.service_registry.register(
                "slow.service",
                TraceService(
                    name="slow",
                    trace=trace,
                    delay_action="initialize",
                    delay_seconds=0.03,
                ),
            )

        process = BootProcess(
            project_root=temporary_root,
            overrides={
                "environment": "testing",
                "worker_enabled": False,
            },
            service_registrars=[
                registrar,
            ],
        )

        results = await asyncio.gather(
            process.boot(),
            process.boot(),
        )

        if results[0] is not results[1]:
            fail(
                "Concurrent boot calls did not "
                "return the same context."
            )

        if registrar_calls["count"] != 1:
            fail(
                "Concurrent boot executed service "
                "registration more than once."
            )

        assertions[
            "concurrent_single_flight_boot"
        ] = "PASS"

        await (
            results[0]
            .lifecycle_manager
            .stop()
        )

    async def registrar_failure_test(
        temporary_root: Path,
    ) -> None:
        def failing_registrar(
            composition: Any,
        ) -> None:
            raise RuntimeError(
                "registrar failure"
            )

        process = BootProcess(
            project_root=temporary_root,
            service_registrars=[
                failing_registrar,
            ],
        )

        rejected = False

        try:
            await process.boot()
        except BootFailureError as exc:
            rejected = (
                exc.stage
                == "service_registration"
            )

        if not rejected:
            fail(
                "Service registrar failure was not "
                "reported at the correct boot stage."
            )

        snapshot = process.snapshot()

        if (
            snapshot.status
            is not BootStatus.FAILED
        ):
            fail(
                "Registrar failure did not produce "
                "a failed boot snapshot."
            )

        if snapshot.failure_reason is None:
            fail(
                "Registrar failure reason was not recorded."
            )

        assertions[
            "registrar_failure_propagation"
        ] = "PASS"

    async def critical_start_failure_test(
        temporary_root: Path,
    ) -> None:
        trace: list[str] = []

        def registrar(
            composition: Any,
        ) -> None:
            composition.service_registry.register(
                "critical.service",
                TraceService(
                    name="critical",
                    trace=trace,
                    fail_action="start",
                ),
                critical=True,
            )

        process = BootProcess(
            project_root=temporary_root,
            service_registrars=[
                registrar,
            ],
        )

        rejected = False

        try:
            await process.boot()
        except BootFailureError as exc:
            rejected = (
                exc.stage
                == "lifecycle_start"
            )

        if not rejected:
            fail(
                "Critical service startup failure "
                "was not propagated."
            )

        if process.status is not BootStatus.FAILED:
            fail(
                "Critical startup failure did not "
                "mark boot as failed."
            )

        if "critical.stop" not in trace:
            fail(
                "Failed boot did not stop the "
                "critical service."
            )

        if "critical.close" not in trace:
            fail(
                "Failed boot did not close the "
                "critical service."
            )

        assertions[
            "failed_boot_cleanup"
        ] = "PASS"

    async def convenience_entry_point_test(
        temporary_root: Path,
    ) -> None:
        process, context = (
            await module.boot_runtime(
                project_root=temporary_root,
                overrides={
                    "environment": "testing",
                    "worker_enabled": False,
                },
            )
        )

        if process.current_context is not context:
            fail(
                "boot_runtime returned mismatched "
                "process and context objects."
            )

        assertions[
            "boot_convenience_entry_point"
        ] = "PASS"

        await context.lifecycle_manager.stop()

    with tempfile.TemporaryDirectory(
        prefix="uri_runtime_boot_test_"
    ) as temporary_directory:
        temporary_root = Path(
            temporary_directory
        ).resolve()

        invalid_root_rejected = False

        try:
            BootProcess(
                project_root=(
                    temporary_root
                    / "missing"
                )
            )
        except BootConfigurationError:
            invalid_root_rejected = True

        if not invalid_root_rejected:
            fail(
                "A missing project root was not rejected."
            )

        assertions[
            "boot_configuration_validation"
        ] = "PASS"

        normal_results = asyncio.run(
            normal_boot_test(
                temporary_root
            )
        )

        asyncio.run(
            concurrent_boot_test(
                temporary_root
            )
        )

        asyncio.run(
            registrar_failure_test(
                temporary_root
            )
        )

        asyncio.run(
            critical_start_failure_test(
                temporary_root
            )
        )

        asyncio.run(
            convenience_entry_point_test(
                temporary_root
            )
        )

    return {
        "assertions": assertions,
        "normal_boot": normal_results,
    }


def rollback(
    *,
    target_existed: bool,
) -> None:
    if target_existed:
        if not BACKUP_TARGET.exists():
            raise RuntimeError(
                "Runtime boot-process rollback "
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
    print("1.1.6 — RUNTIME BOOT PROCESS BUILD")
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
            "Existing runtime boot process "
            "backed up:"
        )
        print(BACKUP_TARGET)
        print()

    TARGET.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    module_name = (
        "backend.server.runtime."
        "runtime_boot_process"
    )

    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(
            0,
            str(PROJECT_ROOT),
        )

    try:
        TARGET.write_text(
            BOOT_SOURCE,
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

        evidence_root_existed_before_import = (
            EVIDENCE_ROOT.exists()
        )

        module = import_boot_module()

        if (
            dict(os.environ)
            != process_environment_before
        ):
            fail(
                "Importing the boot module mutated "
                "os.environ."
            )

        if (
            not evidence_root_existed_before_import
            and EVIDENCE_ROOT.exists()
        ):
            fail(
                "Importing the boot module created "
                "an evidence directory."
            )

        behavioral_results = verify_behavior(
            module
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
            "Runtime boot-process verification failed. "
            "The previous filesystem state was restored."
        )

        raise

    finally:
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
            "boot_process_py_compile": "PASS",
            "foundation_files_compile": "PASS",
            "main_py_compile": "PASS",
            "ast_contract": "PASS",
            "behavioral_contract": "PASS",
            "deterministic_composition": "PASS",
            "single_flight_boot": "PASS",
            "idempotent_boot": "PASS",
            "failure_cleanup": "PASS",
            "kernel_binding_contract": "PASS",
            "registry_sealing_contract": "PASS",
            "import_side_effect_protection": "PASS",
            "business_logic_agnostic_test": "PASS",
            "protected_files_unchanged": "PASS",
            "automatic_rollback_required": False,
        },
        "ast_contract_details": ast_contract,
        "behavioral_results": behavioral_results,
        "phase_status": {
            "phase": "1",
            "item": "1.1.6",
            "name": "Runtime Boot Process",
            "implementation_status": "IMPLEMENTED",
            "verification_status": "PASS",
            "foundation_composition_status": "PASS",
            "application_startup_wiring": "PENDING",
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
        "1.1.6 — RUNTIME BOOT PROCESS EVIDENCE",
        "=" * 78,
        "",
        f"Build version: {BUILD_VERSION}",
        f"Timestamp UTC: {evidence['timestamp_utc']}",
        f"Target: {TARGET}",
        "",
        "VERIFICATION",
        "-" * 78,
        "Runtime Boot Process compilation: PASS",
        "Phase 1 foundation compilation: PASS",
        "main.py compilation: PASS",
        "Boot AST contract: PASS",
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
            "CHECKLIST POSITION",
            "-" * 78,
            (
                "1.1.1 kernel composition "
                "compatibility: PASS"
            ),
            (
                "1.1.2 configuration loading "
                "compatibility: PASS"
            ),
            (
                "1.1.3 environment composition "
                "compatibility: PASS"
            ),
            (
                "1.1.4 registry composition and "
                "sealing: PASS"
            ),
            (
                "1.1.5 lifecycle startup "
                "coordination: PASS"
            ),
            "1.1.6 implementation: PASS",
            (
                "1.1.6 isolated foundation "
                "integration: PASS"
            ),
            (
                "1.1.6 application startup wiring: "
                "PENDING"
            ),
            "1.1.6 certification: NOT CERTIFIED",
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
        "Runtime Boot Process compilation:      PASS"
    )
    print(
        "Phase 1 foundation compilation:        PASS"
    )
    print(
        "main.py compilation:                   PASS"
    )
    print(
        "Boot AST contract:                     PASS"
    )
    print(
        "Deterministic foundation composition:  PASS"
    )
    print(
        "Configuration/environment resolution:  PASS"
    )
    print(
        "Registry registration and sealing:     PASS"
    )
    print(
        "Lifecycle initialize/start sequence:   PASS"
    )
    print(
        "Concurrent single-flight boot:         PASS"
    )
    print(
        "Idempotent repeated boot:              PASS"
    )
    print(
        "Failed-boot cleanup:                   PASS"
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
    print(f"Boot process:  {TARGET}")
    print(f"Evidence JSON: {EVIDENCE_JSON}")
    print(f"Evidence text: {EVIDENCE_TEXT}")
    print()

    print("1.1.6 RUNTIME BOOT PROCESS")
    print("IMPLEMENTATION: PASS")
    print("ISOLATED FOUNDATION INTEGRATION: PASS")
    print("APPLICATION STARTUP WIRING: PENDING")
    print("CERTIFICATION: NOT CERTIFIED")
    print()
    print("NO PRODUCTION DATA WAS MODIFIED")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
