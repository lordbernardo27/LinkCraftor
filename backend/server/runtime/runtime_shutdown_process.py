from __future__ import annotations

"""
Universal Runtime Shutdown Process.

This module coordinates graceful draining, reverse-order service
shutdown, cleanup, timeout enforcement, and final boot-state
publication.

It does not execute jobs, implement pipeline stages, register product
handlers, create detached tasks, or run automatically during import.
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

from backend.server.runtime.runtime_boot_process import (
    RuntimeBootContext,
    RuntimeBootProcess,
    RuntimeBootStatus,
)
from backend.server.runtime.runtime_lifecycle_manager import (
    RuntimeLifecyclePhase,
    RuntimeLifecycleShutdownError,
)


__all__ = [
    "RuntimeShutdownConfigurationError",
    "RuntimeShutdownContext",
    "RuntimeShutdownError",
    "RuntimeShutdownEvent",
    "RuntimeShutdownFailureError",
    "RuntimeShutdownProcess",
    "RuntimeShutdownSnapshot",
    "RuntimeShutdownStatus",
    "RuntimeShutdownTimeoutError",
    "shutdown_runtime",
]


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class RuntimeShutdownError(RuntimeError):
    """Base runtime-shutdown failure."""


class RuntimeShutdownConfigurationError(
    RuntimeShutdownError
):
    """Raised when shutdown cannot identify an active runtime."""


class RuntimeShutdownTimeoutError(
    RuntimeShutdownError
):
    """Raised when the global shutdown deadline is exceeded."""

    def __init__(
        self,
        *,
        timeout_seconds: float,
    ) -> None:
        self.timeout_seconds = timeout_seconds

        super().__init__(
            "Runtime shutdown exceeded the global timeout "
            f"of {timeout_seconds} seconds."
        )


class RuntimeShutdownFailureError(
    RuntimeShutdownError
):
    """
    Raised after shutdown reaches STOPPED with recorded failures.

    context remains available so callers can inspect all cleanup
    failures without losing the final shutdown result.
    """

    def __init__(
        self,
        context: "RuntimeShutdownContext",
    ) -> None:
        self.context = context

        super().__init__(
            "Runtime shutdown completed with failures: "
            + "; ".join(context.failures)
        )


class RuntimeShutdownStatus(str, Enum):
    IDLE = "idle"
    SHUTTING_DOWN = "shutting_down"
    STOPPED = "stopped"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class RuntimeShutdownEvent:
    """Immutable shutdown-event record."""

    sequence: int
    timestamp: datetime
    status: RuntimeShutdownStatus
    stage: str
    outcome: str
    detail: str | None


@dataclass(frozen=True, slots=True)
class RuntimeShutdownContext:
    """Immutable result of a completed runtime shutdown."""

    shutdown_id: str
    attempt: int
    boot_id: str
    started_at: datetime
    completed_at: datetime
    drain_requested: bool
    drain_performed: bool
    service_count: int
    failures: tuple[str, ...]
    kernel_state: str
    lifecycle_phase: str
    boot_status: str


@dataclass(frozen=True, slots=True)
class RuntimeShutdownSnapshot:
    """Immutable point-in-time shutdown inspection record."""

    status: RuntimeShutdownStatus
    attempt: int
    shutdown_id: str | None
    stage: str
    generation: int
    event_count: int
    events: tuple[RuntimeShutdownEvent, ...]
    boot_id: str | None
    boot_status: str
    kernel_state: str | None
    lifecycle_phase: str | None
    failure_reason: str | None
    completed_failures: tuple[str, ...]


class RuntimeShutdownProcess:
    """
    Coordinate graceful shutdown for one RuntimeBootProcess.

    Shutdown order:

    1. Lock the boot controller against competing boot calls.
    2. Enter SHUTTING_DOWN.
    3. Drain services in reverse dependency order when RUNNING.
    4. Stop services in reverse dependency order.
    5. Close services in reverse dependency order.
    6. Publish STOPPED to the boot controller.
    7. Return an immutable shutdown context.

    Repeated and concurrent shutdown requests return the same context.
    """

    __slots__ = (
        "_boot_process",
        "_drain_before_stop",
        "_timeout_seconds",
        "_raise_on_failure",
        "_event_limit",
        "_status",
        "_attempt",
        "_shutdown_id",
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
        boot_process: RuntimeBootProcess,
        drain_before_stop: bool = True,
        timeout_seconds: float | None = None,
        raise_on_failure: bool = True,
        event_limit: int = 500,
    ) -> None:
        if boot_process is None:
            raise RuntimeShutdownConfigurationError(
                "A RuntimeBootProcess is required."
            )

        if timeout_seconds is not None:
            resolved_timeout = float(timeout_seconds)

            if not 0.01 <= resolved_timeout <= 86400.0:
                raise RuntimeShutdownConfigurationError(
                    "timeout_seconds must be between "
                    "0.01 and 86400 seconds."
                )
        else:
            resolved_timeout = None

        if isinstance(event_limit, bool):
            raise RuntimeShutdownConfigurationError(
                "event_limit must be an integer."
            )

        resolved_event_limit = int(event_limit)

        if not 10 <= resolved_event_limit <= 100000:
            raise RuntimeShutdownConfigurationError(
                "event_limit must be between 10 and 100000."
            )

        self._boot_process = boot_process
        self._drain_before_stop = bool(drain_before_stop)
        self._timeout_seconds = resolved_timeout
        self._raise_on_failure = bool(raise_on_failure)
        self._event_limit = resolved_event_limit
        self._status = RuntimeShutdownStatus.IDLE
        self._attempt = 0
        self._shutdown_id: str | None = None
        self._stage = "idle"
        self._generation = 0
        self._events: list[RuntimeShutdownEvent] = []
        self._context: RuntimeShutdownContext | None = None
        self._failure_reason: str | None = None
        self._lock = asyncio.Lock()

    @property
    def status(self) -> RuntimeShutdownStatus:
        return self._status

    @property
    def current_context(
        self,
    ) -> RuntimeShutdownContext | None:
        return self._context

    def _record_event(
        self,
        *,
        stage: str,
        outcome: str,
        detail: str | None = None,
    ) -> RuntimeShutdownEvent:
        self._generation += 1
        self._stage = str(stage)

        event = RuntimeShutdownEvent(
            sequence=self._generation,
            timestamp=_utc_now(),
            status=self._status,
            stage=self._stage,
            outcome=str(outcome),
            detail=detail,
        )

        self._events.append(event)

        if len(self._events) > self._event_limit:
            overflow = len(self._events) - self._event_limit
            del self._events[:overflow]

        return event

    def _resolve_timeout(
        self,
        context: RuntimeBootContext,
    ) -> float:
        if self._timeout_seconds is not None:
            return self._timeout_seconds

        per_service_timeout = float(
            context.configuration.shutdown_timeout_seconds
        )

        service_count = max(
            1,
            context.service_registry.service_count,
        )

        return max(
            1.0,
            per_service_timeout
            * ((service_count * 2) + 2),
        )

    async def _perform_shutdown(
        self,
        *,
        context: RuntimeBootContext,
        failures: list[str],
    ) -> bool:
        lifecycle = context.lifecycle_manager
        drain_performed = False

        if (
            self._drain_before_stop
            and lifecycle.phase
            is RuntimeLifecyclePhase.RUNNING
        ):
            self._record_event(
                stage="drain",
                outcome="started",
            )

            try:
                await lifecycle.drain()
                drain_performed = True

                self._record_event(
                    stage="drain",
                    outcome="completed",
                )
            except Exception as exc:
                failure = (
                    "drain="
                    f"{type(exc).__name__}: {exc}"
                )

                failures.append(failure)

                self._record_event(
                    stage="drain",
                    outcome="failed",
                    detail=failure,
                )

        elif (
            lifecycle.phase
            is RuntimeLifecyclePhase.DRAINING
        ):
            drain_performed = True

            self._record_event(
                stage="drain",
                outcome="already_draining",
            )

        else:
            self._record_event(
                stage="drain",
                outcome="skipped",
                detail=(
                    f"phase={lifecycle.phase.value}; "
                    f"requested={self._drain_before_stop}"
                ),
            )

        if (
            lifecycle.phase
            is not RuntimeLifecyclePhase.STOPPED
        ):
            self._record_event(
                stage="stop",
                outcome="started",
            )

            try:
                await lifecycle.stop()
            except RuntimeLifecycleShutdownError as exc:
                failures.extend(exc.failures)

                self._record_event(
                    stage="stop",
                    outcome="completed_with_failures",
                    detail="; ".join(exc.failures),
                )
            else:
                self._record_event(
                    stage="stop",
                    outcome="completed",
                )
        else:
            self._record_event(
                stage="stop",
                outcome="already_stopped",
            )

        return drain_performed

    async def shutdown(
        self,
    ) -> RuntimeShutdownContext:
        async with self._lock:
            if (
                self._status
                is RuntimeShutdownStatus.STOPPED
                and self._context is not None
            ):
                self._record_event(
                    stage="shutdown",
                    outcome="already_stopped",
                    detail=self._context.shutdown_id,
                )

                return self._context

            boot_context = (
                self._boot_process.current_context
            )

            if boot_context is None:
                raise RuntimeShutdownConfigurationError(
                    "No active runtime boot context is available."
                )

            self._attempt += 1
            self._shutdown_id = (
                f"runtime_shutdown_{self._attempt}_"
                f"{boot_context.boot_id}"
            )
            self._status = (
                RuntimeShutdownStatus.SHUTTING_DOWN
            )
            self._failure_reason = None
            self._context = None

            started_at = _utc_now()

            self._record_event(
                stage="shutdown",
                outcome="started",
                detail=boot_context.boot_id,
            )

            failures: list[str] = []
            timeout_seconds = self._resolve_timeout(
                boot_context
            )

            try:
                await self._boot_process.begin_shutdown(
                    context=boot_context
                )

                drain_performed = await asyncio.wait_for(
                    self._perform_shutdown(
                        context=boot_context,
                        failures=failures,
                    ),
                    timeout=timeout_seconds,
                )

                completed_at = _utc_now()

                failure_reason = (
                    "; ".join(failures)
                    if failures
                    else None
                )

                await self._boot_process.complete_shutdown(
                    context=boot_context,
                    failure_reason=failure_reason,
                )

                shutdown_context = RuntimeShutdownContext(
                    shutdown_id=self._shutdown_id,
                    attempt=self._attempt,
                    boot_id=boot_context.boot_id,
                    started_at=started_at,
                    completed_at=completed_at,
                    drain_requested=(
                        self._drain_before_stop
                    ),
                    drain_performed=drain_performed,
                    service_count=(
                        boot_context
                        .service_registry
                        .service_count
                    ),
                    failures=tuple(failures),
                    kernel_state=(
                        boot_context.kernel.state.value
                    ),
                    lifecycle_phase=(
                        boot_context
                        .lifecycle_manager
                        .phase
                        .value
                    ),
                    boot_status=(
                        self._boot_process
                        .status
                        .value
                    ),
                )

                self._context = shutdown_context
                self._status = (
                    RuntimeShutdownStatus.STOPPED
                )
                self._failure_reason = failure_reason

                self._record_event(
                    stage="shutdown",
                    outcome=(
                        "completed_with_failures"
                        if failures
                        else "completed"
                    ),
                    detail=failure_reason,
                )

                if (
                    failures
                    and self._raise_on_failure
                ):
                    raise RuntimeShutdownFailureError(
                        shutdown_context
                    )

                return shutdown_context

            except RuntimeShutdownFailureError:
                raise

            except asyncio.TimeoutError as exc:
                self._status = (
                    RuntimeShutdownStatus.FAILED
                )
                self._failure_reason = (
                    "Runtime shutdown exceeded "
                    f"{timeout_seconds} seconds."
                )

                await self._boot_process.fail_shutdown(
                    context=boot_context,
                    reason=self._failure_reason,
                )

                self._record_event(
                    stage="shutdown",
                    outcome="timeout",
                    detail=self._failure_reason,
                )

                raise RuntimeShutdownTimeoutError(
                    timeout_seconds=timeout_seconds
                ) from exc

            except Exception as exc:
                self._status = (
                    RuntimeShutdownStatus.FAILED
                )
                self._failure_reason = (
                    f"{type(exc).__name__}: {exc}"
                )

                try:
                    await self._boot_process.fail_shutdown(
                        context=boot_context,
                        reason=self._failure_reason,
                    )
                finally:
                    self._record_event(
                        stage="shutdown",
                        outcome="failed",
                        detail=self._failure_reason,
                    )

                raise RuntimeShutdownError(
                    "Runtime shutdown failed: "
                    + self._failure_reason
                ) from exc

    def snapshot(
        self,
    ) -> RuntimeShutdownSnapshot:
        boot_context = (
            self._boot_process.current_context
        )

        lifecycle = (
            None
            if boot_context is None
            else boot_context.lifecycle_manager
        )

        kernel = (
            None
            if boot_context is None
            else boot_context.kernel
        )

        return RuntimeShutdownSnapshot(
            status=self._status,
            attempt=self._attempt,
            shutdown_id=self._shutdown_id,
            stage=self._stage,
            generation=self._generation,
            event_count=len(self._events),
            events=tuple(self._events),
            boot_id=(
                None
                if boot_context is None
                else boot_context.boot_id
            ),
            boot_status=(
                self._boot_process.status.value
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
            failure_reason=self._failure_reason,
            completed_failures=(
                ()
                if self._context is None
                else self._context.failures
            ),
        )


async def shutdown_runtime(
    *,
    boot_process: RuntimeBootProcess,
    drain_before_stop: bool = True,
    timeout_seconds: float | None = None,
    raise_on_failure: bool = True,
) -> tuple[
    RuntimeShutdownProcess,
    RuntimeShutdownContext,
]:
    """Convenience entry point for graceful runtime shutdown."""

    process = RuntimeShutdownProcess(
        boot_process=boot_process,
        drain_before_stop=drain_before_stop,
        timeout_seconds=timeout_seconds,
        raise_on_failure=raise_on_failure,
    )

    context = await process.shutdown()

    return process, context
