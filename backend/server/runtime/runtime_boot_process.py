from __future__ import annotations

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
    SHUTTING_DOWN = "shutting_down"
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
                is RuntimeBootStatus.SHUTTING_DOWN
            ):
                raise RuntimeBootConfigurationError(
                    "Runtime boot is unavailable while "
                    "shutdown is in progress."
                )

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

    async def begin_shutdown(
        self,
        *,
        context: RuntimeBootContext,
    ) -> None:
        """Lock the boot controller into SHUTTING_DOWN."""

        async with self._lock:
            if self._context is not context:
                raise RuntimeBootConfigurationError(
                    "Shutdown context does not match the "
                    "active runtime boot context."
                )

            if (
                self._status
                is RuntimeBootStatus.STOPPED
            ):
                return

            if (
                self._status
                is not RuntimeBootStatus.RUNNING
            ):
                raise RuntimeBootConfigurationError(
                    "Runtime shutdown can begin only while "
                    f"boot status is 'running', not "
                    f"{self._status.value!r}."
                )

            self._status = (
                RuntimeBootStatus.SHUTTING_DOWN
            )

            self._record_event(
                stage="shutdown",
                outcome="started",
                detail=context.boot_id,
            )

    async def complete_shutdown(
        self,
        *,
        context: RuntimeBootContext,
        failure_reason: str | None = None,
    ) -> None:
        """Publish a completed runtime shutdown."""

        async with self._lock:
            if self._context is not context:
                raise RuntimeBootConfigurationError(
                    "Shutdown context does not match the "
                    "active runtime boot context."
                )

            if (
                context.lifecycle_manager.phase.value
                != "stopped"
            ):
                raise RuntimeBootConfigurationError(
                    "Runtime shutdown cannot be completed "
                    "before the lifecycle reaches STOPPED."
                )

            if self._status not in {
                RuntimeBootStatus.SHUTTING_DOWN,
                RuntimeBootStatus.STOPPED,
            }:
                raise RuntimeBootConfigurationError(
                    "Runtime shutdown completion is invalid "
                    f"while boot status is "
                    f"{self._status.value!r}."
                )

            self._status = RuntimeBootStatus.STOPPED
            self._failure_reason = failure_reason

            self._record_event(
                stage="shutdown",
                outcome=(
                    "completed_with_failures"
                    if failure_reason
                    else "completed"
                ),
                detail=(
                    failure_reason
                    or context.boot_id
                ),
            )

    async def fail_shutdown(
        self,
        *,
        context: RuntimeBootContext,
        reason: str,
    ) -> None:
        """Publish an incomplete or failed shutdown."""

        normalized_reason = str(reason or "").strip()

        if not normalized_reason:
            raise RuntimeBootConfigurationError(
                "A shutdown-failure reason is required."
            )

        async with self._lock:
            if self._context is not context:
                raise RuntimeBootConfigurationError(
                    "Shutdown context does not match the "
                    "active runtime boot context."
                )

            self._status = RuntimeBootStatus.FAILED
            self._failure_reason = normalized_reason

            self._record_event(
                stage="shutdown",
                outcome="failed",
                detail=normalized_reason,
            )

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
