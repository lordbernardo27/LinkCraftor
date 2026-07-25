from __future__ import annotations

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
