from __future__ import annotations

"""
Lifecycle adapter for the existing LinkCraftor Universal Runtime Worker.

This module does not implement another queue, dispatcher, job store,
worker engine, or pipeline handler.

It delegates execution to run_one_universal_runtime_job_v1().
"""

import asyncio
from collections.abc import Callable
from typing import Any

from backend.server.runtime.runtime_feature_flag_gateway import (
    runtime_queue_claims_enabled,
)
from backend.server.runtime.universal_runtime_kernel import (
    RuntimeKernelState,
    UniversalRuntimeKernel,
)
from backend.server.runtime.universal_runtime_worker_v1 import (
    run_one_universal_runtime_job_v1,
)


class UniversalRuntimeWorkerService:
    """Lifecycle-managed adapter around the canonical worker."""

    def __init__(
        self,
        *,
        kernel: UniversalRuntimeKernel,
        poll_interval_seconds: float,
        enabled: bool = False,
        worker_id: str = "universal_runtime_worker_v1",
        allowed_job_ids: frozenset[str] | None = None,
        runner: Callable[..., dict[str, Any]] = (
            run_one_universal_runtime_job_v1
        ),
        authorization_check: Callable[..., bool] | None = None,
    ) -> None:
        if not isinstance(kernel, UniversalRuntimeKernel):
            raise TypeError("Canonical runtime kernel required.")

        if type(enabled) is not bool:
            raise TypeError("enabled must be bool.")

        if poll_interval_seconds <= 0:
            raise ValueError("Poll interval must be positive.")

        if not worker_id.strip():
            raise ValueError("Worker ID must not be empty.")

        if not callable(runner):
            raise TypeError("Worker runner must be callable.")

        if allowed_job_ids is not None:
            if (
                not isinstance(allowed_job_ids, frozenset)
                or not allowed_job_ids
                or any(
                    not isinstance(job_id, str)
                    or not job_id.strip()
                    for job_id in allowed_job_ids
                )
            ):
                raise ValueError(
                    'allowed_job_ids must be a nonempty '
                    'frozenset of job IDs.'
                )

        if enabled and allowed_job_ids is None:
            raise ValueError(
                'Worker activation requires an explicit job scope.'
            )

        self.kernel = kernel
        self.poll_interval_seconds = float(poll_interval_seconds)
        self.enabled = enabled
        self.worker_id = worker_id
        self.runner = runner
        self.allowed_job_ids = allowed_job_ids
        self.authorization_check = authorization_check

        self._task: asyncio.Task | None = None
        self._stop_event = asyncio.Event()
        self.last_result: dict[str, Any] | None = None
        self.last_error: str | None = None
        self.executions = 0
        self.shutdown_incomplete = False

    def runtime_initialize(self) -> None:
        """No queue access during initialization."""
        return None

    def runtime_ready(self) -> bool:
        """Service configuration is valid."""
        return True

    def _require_execution_scope(self) -> None:
        """Fail closed before any controlled worker execution."""
        scope = self.allowed_job_ids
        if (
            not isinstance(scope, frozenset)
            or not scope
            or any(
                not isinstance(job_id, str)
                or not job_id.strip()
                for job_id in scope
            )
        ):
            raise RuntimeError(
                'Worker execution blocked: valid job scope required.'
            )

    async def runtime_start(self) -> None:
        """Start a managed polling task only when explicitly enabled."""
        if not self.enabled:
            return

        self._require_execution_scope()
        self._require_preclaim_authorization()

        if self.shutdown_incomplete:
            raise RuntimeError(
                "Worker restart blocked: shutdown is incomplete."
            )

        if self._task is not None:
            if not self._task.done():
                return
            await self._task

        self._stop_event.clear()
        self.last_error = None
        self._task = asyncio.create_task(
            self._poll_loop(),
            name="linkcraftor_universal_runtime_worker",
        )


    def _require_preclaim_authorization(self) -> None:
        """Deny by default before invoking the canonical job runner.

        A trusted runtime integration must later supply the
        authorization_check callback. A caller-provided callback
        alone is not proof of authentication or production authority.
        """
        check = self.authorization_check

        if not callable(check):
            raise RuntimeError(
                "Worker execution denied: trusted "
                "authorization provider unavailable."
            )

        scope = self.allowed_job_ids

        self._require_execution_scope()

        decision = check(
            worker_id=self.worker_id,
            allowed_job_ids=scope,
        )

        if decision is not True:
            raise RuntimeError(
                "Worker execution denied: authorization "
                "decision was not an explicit True."
            )

    async def _poll_loop(self) -> None:
        """Use the existing worker and queue-claim authorization."""
        while not self._stop_event.is_set():
            try:
                kernel_running = (
                    self.kernel.snapshot().state
                    is RuntimeKernelState.RUNNING
                )

                if (
                    kernel_running
                    and runtime_queue_claims_enabled(
                        worker_id=self.worker_id
                    )
                ):
                    if not self.enabled:
                        return

                    self._require_execution_scope()
                    self._require_preclaim_authorization()

                    result = await asyncio.to_thread(
                        self.runner,
                        worker_id=self.worker_id,
                        allowed_job_ids=self.allowed_job_ids,
                    )

                    if not isinstance(result, dict):
                        raise TypeError(
                            "Canonical worker returned a non-mapping result."
                        )

                    self.last_result = result
                    self.executions += 1

                    if result.get("worker_status") == "FAILED":
                        self.last_error = (
                            "Canonical worker reported FAILED for "
                            + str(result.get("job_id"))
                        )
                        return

                try:
                    await asyncio.wait_for(
                        self._stop_event.wait(),
                        timeout=self.poll_interval_seconds,
                    )
                except asyncio.TimeoutError:
                    pass

            except Exception as exc:
                self.last_error = (
                    f"{type(exc).__name__}: {exc}"
                )
                return

    async def runtime_drain(self) -> None:
        """Stop new claims and await in-flight execution."""
        self._stop_event.set()

        if self._task is None:
            self.shutdown_incomplete = False
            return

        try:
            await asyncio.shield(self._task)
        except asyncio.CancelledError:
            self.shutdown_incomplete = not self._task.done()
            raise
        except Exception:
            self.shutdown_incomplete = not self._task.done()
            raise
        else:
            self.shutdown_incomplete = False

    async def runtime_resume(self) -> None:
        await self.runtime_start()

    async def runtime_stop(self) -> None:
        await self.runtime_drain()

    async def runtime_close(self) -> None:
        await self.runtime_drain()

    def snapshot(self) -> dict[str, Any]:
        return {
            "worker_id": self.worker_id,
            "enabled": self.enabled,
            "running": (
                self._task is not None
                and not self._task.done()
            ),
            "executions": self.executions,
            "shutdown_incomplete": self.shutdown_incomplete,
            "last_error": self.last_error,
            "last_result": self.last_result,
        }
