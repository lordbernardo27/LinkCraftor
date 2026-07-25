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


BUILD_VERSION = "uri_phase_1_1_7_runtime_shutdown_process_v1"

PROJECT_ROOT = Path.cwd().resolve()

TARGET = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "runtime"
    / "runtime_shutdown_process.py"
)

BOOT_FILE = (
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
    / f"uri_phase1_1_7_runtime_shutdown_{TIMESTAMP}"
)

BACKUP_TARGET = (
    BACKUP_ROOT
    / "backend"
    / "server"
    / "runtime"
    / "runtime_shutdown_process.py"
)

BACKUP_BOOT = (
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
    / "1_1_7_runtime_shutdown_process"
)

EVIDENCE_JSON = (
    EVIDENCE_ROOT
    / f"runtime_shutdown_process_build_{TIMESTAMP}.json"
)

EVIDENCE_TEXT = (
    EVIDENCE_ROOT
    / f"runtime_shutdown_process_build_{TIMESTAMP}.txt"
)


SHUTDOWN_SOURCE = r'''from __future__ import annotations

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


def patch_boot_process(
    source: str,
) -> tuple[str, list[str]]:
    changes: list[str] = []
    updated = source

    status_before = '''class RuntimeBootStatus(str, Enum):
    IDLE = "idle"
    BOOTING = "booting"
    RUNNING = "running"
    FAILED = "failed"
    STOPPED = "stopped"
'''

    status_after = '''class RuntimeBootStatus(str, Enum):
    IDLE = "idle"
    BOOTING = "booting"
    RUNNING = "running"
    SHUTTING_DOWN = "shutting_down"
    FAILED = "failed"
    STOPPED = "stopped"
'''

    if status_before in updated:
        updated = updated.replace(
            status_before,
            status_after,
            1,
        )
        changes.append(
            "RuntimeBootStatus.SHUTTING_DOWN added"
        )
    elif status_after not in updated:
        fail(
            "Could not locate RuntimeBootStatus "
            "for controlled shutdown extension."
        )

    boot_lock_before = '''        async with self._lock:
            if (
                self._status
                is RuntimeBootStatus.RUNNING
'''

    boot_lock_after = '''        async with self._lock:
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
'''

    if boot_lock_before in updated:
        updated = updated.replace(
            boot_lock_before,
            boot_lock_after,
            1,
        )
        changes.append(
            "boot/shutdown race protection added"
        )
    elif boot_lock_after not in updated:
        fail(
            "Could not locate the RuntimeBootProcess "
            "single-flight boot boundary."
        )

    shutdown_methods = '''    async def begin_shutdown(
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

'''

    snapshot_marker = '''    def snapshot(
        self,
    ) -> RuntimeBootSnapshot:
'''

    if "async def begin_shutdown(" not in updated:
        if snapshot_marker not in updated:
            fail(
                "Could not locate RuntimeBootProcess.snapshot "
                "for shutdown-method insertion."
            )

        updated = updated.replace(
            snapshot_marker,
            shutdown_methods + snapshot_marker,
            1,
        )

        changes.append(
            "controlled shutdown publication methods added"
        )

    return updated, changes


def verify_boot_shutdown_contract(
    path: Path,
) -> dict[str, Any]:
    text = path.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(
        text,
        filename=str(path),
    )

    boot_methods: set[str] = set()
    statuses: set[str] = set()

    for node in tree.body:
        if (
            isinstance(node, ast.ClassDef)
            and node.name == "RuntimeBootProcess"
        ):
            boot_methods = {
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

        if (
            isinstance(node, ast.ClassDef)
            and node.name == "RuntimeBootStatus"
        ):
            statuses = {
                target.id
                for child in node.body
                if isinstance(child, ast.Assign)
                for target in child.targets
                if isinstance(target, ast.Name)
            }

    required_methods = {
        "begin_shutdown",
        "complete_shutdown",
        "fail_shutdown",
    }

    missing_methods = sorted(
        required_methods - boot_methods
    )

    if missing_methods:
        fail(
            "RuntimeBootProcess is missing shutdown "
            "integration methods: "
            + ", ".join(missing_methods)
        )

    if "SHUTTING_DOWN" not in statuses:
        fail(
            "RuntimeBootStatus.SHUTTING_DOWN is missing."
        )

    return {
        "required_methods": sorted(required_methods),
        "missing_methods": missing_methods,
        "shutting_down_status_present": True,
    }


def verify_shutdown_ast_contract(
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
        "RuntimeShutdownContext",
        "RuntimeShutdownEvent",
        "RuntimeShutdownSnapshot",
        "RuntimeShutdownProcess",
        "RuntimeShutdownStatus",
        "RuntimeShutdownError",
        "RuntimeShutdownConfigurationError",
        "RuntimeShutdownFailureError",
        "RuntimeShutdownTimeoutError",
    }

    required_methods = {
        "shutdown",
        "snapshot",
        "_record_event",
        "_resolve_timeout",
        "_perform_shutdown",
    }

    missing_classes = sorted(
        required_classes - set(classes)
    )

    missing_methods = sorted(
        required_methods
        - classes.get(
            "RuntimeShutdownProcess",
            set(),
        )
    )

    if missing_classes:
        fail(
            "Runtime shutdown AST contract is missing "
            "classes: "
            + ", ".join(missing_classes)
        )

    if missing_methods:
        fail(
            "RuntimeShutdownProcess is missing methods: "
            + ", ".join(missing_methods)
        )

    if "shutdown_runtime" not in functions:
        fail(
            "The shutdown_runtime entry point is missing."
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
            "Runtime shutdown process contains "
            "pipeline-specific business terms: "
            + ", ".join(detected_forbidden_terms)
        )

    if "asyncio.create_task" in text:
        fail(
            "Runtime shutdown must not create "
            "detached tasks."
        )

    if "@app.on_event" in text:
        fail(
            "Runtime shutdown must not wire itself "
            "directly into the application."
        )

    return {
        "required_classes": sorted(required_classes),
        "missing_classes": missing_classes,
        "required_methods": sorted(required_methods),
        "missing_methods": missing_methods,
        "shutdown_entry_point_present": True,
        "detached_task_creation_detected": False,
        "application_hook_detected": False,
        "pipeline_business_terms_detected": (
            detected_forbidden_terms
        ),
    }


def import_runtime_module(
    module_name: str,
) -> Any:
    sys.modules.pop(module_name, None)
    importlib.invalidate_caches()

    return importlib.import_module(module_name)


def verify_behavior(
    shutdown_module: Any,
    boot_module: Any,
) -> dict[str, Any]:
    BootProcess = boot_module.RuntimeBootProcess
    BootStatus = boot_module.RuntimeBootStatus

    ShutdownProcess = (
        shutdown_module.RuntimeShutdownProcess
    )

    ShutdownStatus = (
        shutdown_module.RuntimeShutdownStatus
    )

    ShutdownConfigurationError = (
        shutdown_module
        .RuntimeShutdownConfigurationError
    )

    ShutdownFailureError = (
        shutdown_module.RuntimeShutdownFailureError
    )

    ShutdownTimeoutError = (
        shutdown_module.RuntimeShutdownTimeoutError
    )

    assertions: dict[str, str] = {}

    class TraceService:
        def __init__(
            self,
            *,
            name: str,
            trace: list[str],
            fail_stop: bool = False,
            stop_delay: float = 0.0,
        ) -> None:
            self.name = name
            self.trace = trace
            self.fail_stop = fail_stop
            self.stop_delay = stop_delay

        async def initialize(self) -> None:
            self.trace.append(
                f"{self.name}.initialize"
            )

        async def ready(self) -> bool:
            self.trace.append(
                f"{self.name}.ready"
            )
            return True

        async def start(self) -> None:
            self.trace.append(
                f"{self.name}.start"
            )

        async def drain(self) -> None:
            self.trace.append(
                f"{self.name}.drain"
            )

        async def stop(self) -> None:
            self.trace.append(
                f"{self.name}.stop"
            )

            if self.stop_delay:
                await asyncio.sleep(
                    self.stop_delay
                )

            if self.fail_stop:
                raise RuntimeError(
                    f"{self.name} stop failure"
                )

        async def close(self) -> None:
            self.trace.append(
                f"{self.name}.close"
            )

    async def create_running_boot(
        temporary_root: Path,
        *,
        trace: list[str],
        fail_stop: bool = False,
        stop_delay: float = 0.0,
    ) -> tuple[Any, Any]:
        def registrar(
            composition: Any,
        ) -> None:
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
                    fail_stop=fail_stop,
                    stop_delay=stop_delay,
                ),
                dependencies=[
                    "state.store",
                ],
                startup_order=20,
                critical=True,
            )

        boot_process = BootProcess(
            project_root=temporary_root,
            overrides={
                "environment": "testing",
                "worker_enabled": False,
                "shutdown_timeout_seconds": 1.0,
            },
            service_registrars=[
                registrar,
            ],
        )

        context = await boot_process.boot()

        return boot_process, context

    async def normal_shutdown_test(
        temporary_root: Path,
    ) -> dict[str, Any]:
        trace: list[str] = []

        boot_process, boot_context = (
            await create_running_boot(
                temporary_root,
                trace=trace,
            )
        )

        process = ShutdownProcess(
            boot_process=boot_process,
            timeout_seconds=2.0,
        )

        context = await process.shutdown()

        expected_tail = [
            "event.drain",
            "state.drain",
            "event.stop",
            "state.stop",
            "event.close",
            "state.close",
        ]

        if trace[-6:] != expected_tail:
            fail(
                "Graceful shutdown ordering is incorrect: "
                f"{trace[-6:]!r}"
            )

        assertions[
            "drain_stop_close_order"
        ] = "PASS"

        if process.status is not ShutdownStatus.STOPPED:
            fail(
                "Shutdown process did not reach STOPPED."
            )

        if boot_process.status is not BootStatus.STOPPED:
            fail(
                "Boot controller did not publish STOPPED."
            )

        if boot_context.kernel.state.value != "stopped":
            fail(
                "Kernel did not reach STOPPED."
            )

        if (
            boot_context
            .lifecycle_manager
            .phase
            .value
            != "stopped"
        ):
            fail(
                "Lifecycle did not reach STOPPED."
            )

        assertions[
            "boot_kernel_lifecycle_synchronization"
        ] = "PASS"

        repeated = await process.shutdown()

        if repeated is not context:
            fail(
                "Repeated shutdown returned a new context."
            )

        assertions[
            "idempotent_shutdown"
        ] = "PASS"

        snapshot = process.snapshot()

        if snapshot.status is not ShutdownStatus.STOPPED:
            fail(
                "Shutdown snapshot status is incorrect."
            )

        snapshot_immutable = False

        try:
            snapshot.stage = "illegal"
        except (AttributeError, TypeError):
            snapshot_immutable = True

        if not snapshot_immutable:
            fail(
                "Shutdown snapshot was mutable."
            )

        assertions[
            "immutable_shutdown_snapshot"
        ] = "PASS"

        return {
            "trace": trace,
            "shutdown_id": context.shutdown_id,
            "event_count": snapshot.event_count,
        }

    async def concurrent_shutdown_test(
        temporary_root: Path,
    ) -> None:
        trace: list[str] = []

        boot_process, _ = await create_running_boot(
            temporary_root,
            trace=trace,
        )

        process = ShutdownProcess(
            boot_process=boot_process,
            timeout_seconds=2.0,
        )

        results = await asyncio.gather(
            process.shutdown(),
            process.shutdown(),
        )

        if results[0] is not results[1]:
            fail(
                "Concurrent shutdown calls did not "
                "return the same context."
            )

        if trace.count("event.stop") != 1:
            fail(
                "Concurrent shutdown executed service "
                "stop more than once."
            )

        assertions[
            "concurrent_single_flight_shutdown"
        ] = "PASS"

    async def failure_aggregation_test(
        temporary_root: Path,
    ) -> None:
        trace: list[str] = []

        boot_process, _ = await create_running_boot(
            temporary_root,
            trace=trace,
            fail_stop=True,
        )

        process = ShutdownProcess(
            boot_process=boot_process,
            timeout_seconds=2.0,
            raise_on_failure=False,
        )

        context = await process.shutdown()

        if not context.failures:
            fail(
                "Shutdown service failure was not recorded."
            )

        if boot_process.status is not BootStatus.STOPPED:
            fail(
                "Completed shutdown with failures did "
                "not publish STOPPED."
            )

        if "event.close" not in trace:
            fail(
                "Cleanup did not continue after stop failure."
            )

        assertions[
            "shutdown_failure_aggregation"
        ] = "PASS"

    async def raised_failure_context_test(
        temporary_root: Path,
    ) -> None:
        trace: list[str] = []

        boot_process, _ = await create_running_boot(
            temporary_root,
            trace=trace,
            fail_stop=True,
        )

        process = ShutdownProcess(
            boot_process=boot_process,
            timeout_seconds=2.0,
            raise_on_failure=True,
        )

        captured_context = None

        try:
            await process.shutdown()
        except ShutdownFailureError as exc:
            captured_context = exc.context

        if captured_context is None:
            fail(
                "Configured shutdown failure was not raised."
            )

        if process.current_context is not captured_context:
            fail(
                "Raised shutdown failure lost the "
                "completed context."
            )

        assertions[
            "completed_failure_context_preservation"
        ] = "PASS"

    async def timeout_test(
        temporary_root: Path,
    ) -> None:
        trace: list[str] = []

        boot_process, _ = await create_running_boot(
            temporary_root,
            trace=trace,
            stop_delay=0.1,
        )

        process = ShutdownProcess(
            boot_process=boot_process,
            drain_before_stop=False,
            timeout_seconds=0.01,
        )

        timed_out = False

        try:
            await process.shutdown()
        except ShutdownTimeoutError:
            timed_out = True

        if not timed_out:
            fail(
                "Global shutdown timeout was not enforced."
            )

        if process.status is not ShutdownStatus.FAILED:
            fail(
                "Timed-out shutdown did not reach FAILED."
            )

        if boot_process.status is not BootStatus.FAILED:
            fail(
                "Timed-out shutdown was not published "
                "to the boot controller."
            )

        assertions[
            "global_shutdown_timeout"
        ] = "PASS"

    async def missing_context_test(
        temporary_root: Path,
    ) -> None:
        boot_process = BootProcess(
            project_root=temporary_root
        )

        process = ShutdownProcess(
            boot_process=boot_process
        )

        rejected = False

        try:
            await process.shutdown()
        except ShutdownConfigurationError:
            rejected = True

        if not rejected:
            fail(
                "Shutdown accepted a boot process "
                "without an active context."
            )

        assertions[
            "active_context_requirement"
        ] = "PASS"

    async def convenience_entry_point_test(
        temporary_root: Path,
    ) -> None:
        trace: list[str] = []

        boot_process, _ = await create_running_boot(
            temporary_root,
            trace=trace,
        )

        process, context = (
            await shutdown_module.shutdown_runtime(
                boot_process=boot_process,
                timeout_seconds=2.0,
            )
        )

        if process.current_context is not context:
            fail(
                "shutdown_runtime returned mismatched "
                "process and context objects."
            )

        assertions[
            "shutdown_convenience_entry_point"
        ] = "PASS"

    with tempfile.TemporaryDirectory(
        prefix="uri_runtime_shutdown_test_"
    ) as temporary_directory:
        temporary_root = Path(
            temporary_directory
        ).resolve()

        normal_results = asyncio.run(
            normal_shutdown_test(
                temporary_root
            )
        )

        asyncio.run(
            concurrent_shutdown_test(
                temporary_root
            )
        )

        asyncio.run(
            failure_aggregation_test(
                temporary_root
            )
        )

        asyncio.run(
            raised_failure_context_test(
                temporary_root
            )
        )

        asyncio.run(
            timeout_test(
                temporary_root
            )
        )

        asyncio.run(
            missing_context_test(
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
        "normal_shutdown": normal_results,
    }


def rollback(
    *,
    target_existed: bool,
    boot_original: bytes,
) -> None:
    BOOT_FILE.write_bytes(
        boot_original
    )

    if target_existed:
        if not BACKUP_TARGET.exists():
            raise RuntimeError(
                "Runtime shutdown rollback backup "
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
    print("1.1.7 — RUNTIME SHUTDOWN PROCESS BUILD")
    print("=" * 78)
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Target:       {TARGET}")
    print()

    required_files = [
        BOOT_FILE,
        KERNEL_FILE,
        CONFIGURATION_FILE,
        ENVIRONMENT_FILE,
        SERVICE_REGISTRY_FILE,
        LIFECYCLE_FILE,
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

    boot_original = BOOT_FILE.read_bytes()
    boot_original_hash = sha256_file(
        BOOT_FILE
    )

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
        "lifecycle_manager": sha256_file(
            LIFECYCLE_FILE
        ),
        "runtime_facade": sha256_file(
            EXISTING_RUNTIME_FACADE
        ),
        "main": sha256_file(MAIN_FILE),
    }

    BACKUP_BOOT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    shutil.copy2(
        BOOT_FILE,
        BACKUP_BOOT,
    )

    if target_existed:
        BACKUP_TARGET.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.copy2(
            TARGET,
            BACKUP_TARGET,
        )

    TARGET.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    boot_module_name = (
        "backend.server.runtime."
        "runtime_boot_process"
    )

    shutdown_module_name = (
        "backend.server.runtime."
        "runtime_shutdown_process"
    )

    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(
            0,
            str(PROJECT_ROOT),
        )

    try:
        boot_text = boot_original.decode(
            "utf-8"
        )

        patched_boot_text, boot_changes = (
            patch_boot_process(
                boot_text
            )
        )

        BOOT_FILE.write_text(
            patched_boot_text,
            encoding="utf-8",
            newline="\n",
        )

        TARGET.write_text(
            SHUTDOWN_SOURCE,
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

        boot_contract = (
            verify_boot_shutdown_contract(
                BOOT_FILE
            )
        )

        shutdown_contract = (
            verify_shutdown_ast_contract(
                TARGET
            )
        )

        process_environment_before = dict(
            os.environ
        )

        boot_module = import_runtime_module(
            boot_module_name
        )

        shutdown_module = import_runtime_module(
            shutdown_module_name
        )

        if (
            dict(os.environ)
            != process_environment_before
        ):
            fail(
                "Importing runtime shutdown modules "
                "mutated os.environ."
            )

        behavioral_results = verify_behavior(
            shutdown_module,
            boot_module,
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
            "lifecycle_manager": sha256_file(
                LIFECYCLE_FILE
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
            boot_original=boot_original,
        )

        print()
        print("ROLLBACK COMPLETE")
        print(
            "Runtime shutdown verification failed. "
            "The previous filesystem state was restored."
        )

        raise

    finally:
        sys.modules.pop(
            shutdown_module_name,
            None,
        )

        sys.modules.pop(
            boot_module_name,
            None,
        )

    target_final_hash = sha256_file(
        TARGET
    )

    boot_final_hash = sha256_file(
        BOOT_FILE
    )

    evidence = {
        "build_version": BUILD_VERSION,
        "timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "project_root": str(PROJECT_ROOT),
        "target": str(TARGET),
        "boot_process": str(BOOT_FILE),
        "target_existed_before_build": (
            target_existed
        ),
        "target_backup": (
            str(BACKUP_TARGET)
            if target_existed
            else None
        ),
        "boot_backup": str(BACKUP_BOOT),
        "target_original_sha256": (
            target_original_hash
        ),
        "target_final_sha256": (
            target_final_hash
        ),
        "boot_original_sha256": (
            boot_original_hash
        ),
        "boot_final_sha256": (
            boot_final_hash
        ),
        "boot_changes": boot_changes,
        "protected_hashes_before": (
            protected_hashes_before
        ),
        "protected_hashes_after": (
            protected_hashes_after
        ),
        "verification": {
            "shutdown_py_compile": "PASS",
            "boot_py_compile": "PASS",
            "foundation_files_compile": "PASS",
            "main_py_compile": "PASS",
            "boot_shutdown_contract": "PASS",
            "shutdown_ast_contract": "PASS",
            "behavioral_contract": "PASS",
            "drain_contract": "PASS",
            "reverse_shutdown_contract": "PASS",
            "single_flight_shutdown": "PASS",
            "idempotent_shutdown": "PASS",
            "failure_aggregation": "PASS",
            "timeout_contract": "PASS",
            "state_synchronization": "PASS",
            "import_side_effect_protection": "PASS",
            "business_logic_agnostic_test": "PASS",
            "protected_files_unchanged": "PASS",
            "automatic_rollback_required": False,
        },
        "boot_contract_details": (
            boot_contract
        ),
        "shutdown_contract_details": (
            shutdown_contract
        ),
        "behavioral_results": (
            behavioral_results
        ),
        "phase_status": {
            "phase": "1",
            "item": "1.1.7",
            "name": "Runtime Shutdown Process",
            "implementation_status": "IMPLEMENTED",
            "verification_status": "PASS",
            "boot_shutdown_coordination": "PASS",
            "application_lifecycle_wiring": "PENDING",
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
        "1.1.7 — RUNTIME SHUTDOWN PROCESS EVIDENCE",
        "=" * 78,
        "",
        f"Build version: {BUILD_VERSION}",
        f"Timestamp UTC: {evidence['timestamp_utc']}",
        f"Shutdown target: {TARGET}",
        f"Boot process: {BOOT_FILE}",
        "",
        "VERIFICATION",
        "-" * 78,
        "Runtime Shutdown Process compilation: PASS",
        "Runtime Boot Process compilation: PASS",
        "Phase 1 foundation compilation: PASS",
        "main.py compilation: PASS",
        "Boot/shutdown coordination contract: PASS",
        "Shutdown AST contract: PASS",
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
            "1.1.1 kernel compatibility: PASS",
            "1.1.4 registry compatibility: PASS",
            "1.1.5 lifecycle shutdown coordination: PASS",
            "1.1.6 boot-controller coordination: PASS",
            "1.1.7 implementation: PASS",
            "1.1.7 isolated integration: PASS",
            "1.1.7 boot/shutdown race protection: PASS",
            (
                "1.1.7 application lifecycle wiring: "
                "PENDING"
            ),
            "1.1.7 certification: NOT CERTIFIED",
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
        "Runtime Shutdown Process compilation: PASS"
    )
    print(
        "Runtime Boot Process compilation:     PASS"
    )
    print(
        "Phase 1 foundation compilation:       PASS"
    )
    print(
        "main.py compilation:                  PASS"
    )
    print(
        "Boot/shutdown coordination contract:  PASS"
    )
    print(
        "Graceful drain coordination:          PASS"
    )
    print(
        "Reverse-order stop and cleanup:        PASS"
    )
    print(
        "Concurrent single-flight shutdown:    PASS"
    )
    print(
        "Idempotent repeated shutdown:         PASS"
    )
    print(
        "Shutdown failure aggregation:         PASS"
    )
    print(
        "Global shutdown timeout:              PASS"
    )
    print(
        "Boot/kernel/lifecycle synchronization: PASS"
    )
    print(
        "Import-time side-effect protection:   PASS"
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
    print(f"Shutdown process: {TARGET}")
    print(f"Boot process:     {BOOT_FILE}")
    print(f"Boot backup:      {BACKUP_BOOT}")
    print(f"Evidence JSON:    {EVIDENCE_JSON}")
    print(f"Evidence text:    {EVIDENCE_TEXT}")
    print()

    print("1.1.7 RUNTIME SHUTDOWN PROCESS")
    print("IMPLEMENTATION: PASS")
    print("ISOLATED INTEGRATION: PASS")
    print("BOOT/SHUTDOWN COORDINATION: PASS")
    print("APPLICATION LIFECYCLE WIRING: PENDING")
    print("CERTIFICATION: NOT CERTIFIED")
    print()
    print("NO PRODUCTION DATA WAS MODIFIED")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
