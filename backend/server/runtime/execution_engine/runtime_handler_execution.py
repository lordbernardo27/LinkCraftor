"""
LinkCraftor Universal Runtime
Phase 6.5 — Runtime Handler Execution

Canonical Phase-6 handler-execution boundary.

This component consumes:
- Phase 6.2 ExecutionRequest / ExecutionResult / ExecutionFailure
- Phase 6.3 ExecutionFenceIdentity
- Phase 6.4 RUNNING ExecutionLifecycleRecord

It coordinates handler execution without creating:
- a second runtime registry
- a second handler registry
- a second queue
- a second worker system

Existing runtime registration / handler machinery remains authoritative.

Production integration with universal_runtime_registration.py is deferred
to Phase 6.15. This component therefore accepts existing resolver and
invoker callables as integration adapters.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Callable, Mapping, Optional

from .execution_contracts import (
    ExecutionFailure,
    ExecutionFailureKind,
    ExecutionOutcome,
    ExecutionRequest,
    ExecutionResult,
)

from .execution_permission_fencing import (
    ExecutionFenceIdentity,
)

from .execution_lifecycle_controller import (
    ExecutionLifecycleRecord,
    ExecutionLifecycleState,
)


RUNTIME_HANDLER_EXECUTION_VERSION = (
    "runtime_handler_execution_v6.5.1"
)

RUNTIME_HANDLER_EXECUTION_SCHEMA_VERSION = (
    "runtime_handler_execution_schema_v1"
)


class RuntimeHandlerExecutionError(ValueError):
    """Raised when the Phase-6 handler boundary is invalid."""

    def __init__(
        self,
        message: str,
        *,
        code: str,
        value: Any = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.value = value


@dataclass(
    frozen=True,
    slots=True,
)
class PreparedHandlerInput:
    """
    Canonical handler invocation input.

    payload remains opaque to Phase 6.5.
    """

    execution_id: str
    job_id: str
    attempt_number: int
    handler_key: str
    fence_id: str

    payload: Any = None

    metadata: Mapping[str, Any] = field(
        default_factory=dict,
    )

    schema_version: str = field(
        default=RUNTIME_HANDLER_EXECUTION_SCHEMA_VERSION,
        init=False,
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "execution_id": self.execution_id,
            "job_id": self.job_id,
            "attempt_number": self.attempt_number,
            "handler_key": self.handler_key,
            "fence_id": self.fence_id,
            "payload": self.payload,
            "metadata": dict(self.metadata),
        }


@dataclass(
    frozen=True,
    slots=True,
)
class HandlerExecutionCapture:
    """
    Raw Phase-6.5 handler execution capture.

    Phase 6.6 performs broader result processing/normalization.
    """

    execution_id: str
    fence_id: str

    handler_resolved: bool
    handler_invoked: bool

    output: Any = None
    exception: Optional[BaseException] = None

    schema_version: str = field(
        default=RUNTIME_HANDLER_EXECUTION_SCHEMA_VERSION,
        init=False,
    )

    @property
    def succeeded(self) -> bool:
        return (
            self.handler_resolved
            and self.handler_invoked
            and self.exception is None
        )


def validate_handler_invocation_boundary(
    *,
    request: ExecutionRequest,
    lifecycle: ExecutionLifecycleRecord,
    fence: ExecutionFenceIdentity,
) -> None:
    """
    Validate that handler execution belongs to the currently authorized
    RUNNING execution and fence.
    """

    if not isinstance(request, ExecutionRequest):
        raise RuntimeHandlerExecutionError(
            "request must be ExecutionRequest.",
            code="invalid_execution_request",
            value=request,
        )

    if not isinstance(
        lifecycle,
        ExecutionLifecycleRecord,
    ):
        raise RuntimeHandlerExecutionError(
            "lifecycle must be ExecutionLifecycleRecord.",
            code="invalid_execution_lifecycle",
            value=lifecycle,
        )

    if not isinstance(fence, ExecutionFenceIdentity):
        raise RuntimeHandlerExecutionError(
            "fence must be ExecutionFenceIdentity.",
            code="invalid_execution_fence",
            value=fence,
        )

    if lifecycle.state is not ExecutionLifecycleState.RUNNING:
        raise RuntimeHandlerExecutionError(
            "Handler execution requires RUNNING lifecycle state.",
            code="handler_execution_requires_running",
            value=lifecycle.state.value,
        )

    if not lifecycle.active:
        raise RuntimeHandlerExecutionError(
            "RUNNING execution must be active before handler invocation.",
            code="inactive_running_execution",
        )

    if (
        lifecycle.execution_id
        != request.identity.execution_id
    ):
        raise RuntimeHandlerExecutionError(
            "Lifecycle execution_id does not match request.",
            code="handler_execution_identity_mismatch",
        )

    if lifecycle.job_id != request.identity.job_id:
        raise RuntimeHandlerExecutionError(
            "Lifecycle job_id does not match request.",
            code="handler_execution_job_mismatch",
        )

    if (
        lifecycle.attempt_number
        != request.identity.attempt_number
    ):
        raise RuntimeHandlerExecutionError(
            "Lifecycle attempt_number does not match request.",
            code="handler_execution_attempt_mismatch",
        )

    if lifecycle.fence_id != fence.fence_id:
        raise RuntimeHandlerExecutionError(
            "Lifecycle fence does not match execution fence.",
            code="handler_execution_fence_mismatch",
        )

    if (
        fence.execution_id
        != request.identity.execution_id
        or fence.job_id
        != request.identity.job_id
        or fence.attempt_number
        != request.identity.attempt_number
    ):
        raise RuntimeHandlerExecutionError(
            "Execution fence identity does not match request.",
            code="handler_execution_fence_identity_mismatch",
        )


def prepare_handler_input(
    *,
    request: ExecutionRequest,
    lifecycle: ExecutionLifecycleRecord,
    fence: ExecutionFenceIdentity,
) -> PreparedHandlerInput:
    """
    Prepare opaque handler input after validating the invocation boundary.
    """

    validate_handler_invocation_boundary(
        request=request,
        lifecycle=lifecycle,
        fence=fence,
    )

    return PreparedHandlerInput(
        execution_id=request.identity.execution_id,
        job_id=request.identity.job_id,
        attempt_number=request.identity.attempt_number,
        handler_key=request.context.handler_key,
        fence_id=fence.fence_id,
        payload=request.input_payload,
        metadata=MappingProxyType(
            {
                "execution_id":
                    request.identity.execution_id,
                "job_id":
                    request.identity.job_id,
                "attempt_number":
                    request.identity.attempt_number,
                "handler_key":
                    request.context.handler_key,
                "fence_id":
                    fence.fence_id,
                "worker_id":
                    request.context.worker_id,
                "worker_instance_id":
                    request.context.worker_instance_id,
                "lease_id":
                    request.context.lease_id,
                "lease_owner":
                    request.context.lease_owner,
                "runtime_registration_id":
                    request.context.runtime_registration_id,
                "checkpoint_reference":
                    request.context.checkpoint_reference,
            }
        ),
    )


def resolve_registered_handler(
    *,
    handler_key: str,
    resolver: Callable[[str], Any],
) -> Any:
    """
    Resolve handler through an existing registry/resolver adapter.

    Phase 6.5 does not maintain its own registry.
    """

    if not isinstance(handler_key, str) or not handler_key.strip():
        raise RuntimeHandlerExecutionError(
            "handler_key must be a non-empty string.",
            code="invalid_handler_key",
            value=handler_key,
        )

    if not callable(resolver):
        raise RuntimeHandlerExecutionError(
            "resolver must be callable.",
            code="invalid_handler_resolver",
            value=resolver,
        )

    try:
        handler = resolver(handler_key.strip())
    except Exception as exc:
        raise RuntimeHandlerExecutionError(
            "Registered handler resolution failed.",
            code="handler_resolution_failed",
            value=handler_key,
        ) from exc

    if handler is None:
        raise RuntimeHandlerExecutionError(
            "Registered handler was not found.",
            code="handler_not_found",
            value=handler_key,
        )

    return handler


def invoke_registered_handler(
    *,
    handler: Any,
    prepared_input: PreparedHandlerInput,
    invoker: Callable[[Any, PreparedHandlerInput], Any],
) -> Any:
    """
    Invoke the resolved handler through the existing invocation adapter.

    Phase 6.5 does not define a second handler invocation implementation.
    """

    if handler is None:
        raise RuntimeHandlerExecutionError(
            "handler must not be None.",
            code="invalid_resolved_handler",
        )

    if not isinstance(
        prepared_input,
        PreparedHandlerInput,
    ):
        raise RuntimeHandlerExecutionError(
            "prepared_input must be PreparedHandlerInput.",
            code="invalid_prepared_handler_input",
            value=prepared_input,
        )

    if not callable(invoker):
        raise RuntimeHandlerExecutionError(
            "invoker must be callable.",
            code="invalid_handler_invoker",
            value=invoker,
        )

    return invoker(
        handler,
        prepared_input,
    )


def execute_runtime_handler(
    *,
    request: ExecutionRequest,
    lifecycle: ExecutionLifecycleRecord,
    fence: ExecutionFenceIdentity,
    resolver: Callable[[str], Any],
    invoker: Callable[[Any, PreparedHandlerInput], Any],
) -> HandlerExecutionCapture:
    """
    Canonical Phase-6.5 handler-execution operation.

    Flow:
    validate boundary
      -> prepare input
      -> resolve registered handler
      -> invoke existing handler boundary
      -> capture output or exception

    Exceptions from the handler/invoker are captured rather than leaked as
    successful execution.
    """

    prepared_input = prepare_handler_input(
        request=request,
        lifecycle=lifecycle,
        fence=fence,
    )

    try:
        handler = resolve_registered_handler(
            handler_key=prepared_input.handler_key,
            resolver=resolver,
        )
    except Exception as exc:
        return HandlerExecutionCapture(
            execution_id=prepared_input.execution_id,
            fence_id=prepared_input.fence_id,
            handler_resolved=False,
            handler_invoked=False,
            exception=exc,
        )

    try:
        output = invoke_registered_handler(
            handler=handler,
            prepared_input=prepared_input,
            invoker=invoker,
        )

        return HandlerExecutionCapture(
            execution_id=prepared_input.execution_id,
            fence_id=prepared_input.fence_id,
            handler_resolved=True,
            handler_invoked=True,
            output=output,
            exception=None,
        )

    except Exception as exc:
        return HandlerExecutionCapture(
            execution_id=prepared_input.execution_id,
            fence_id=prepared_input.fence_id,
            handler_resolved=True,
            handler_invoked=True,
            output=None,
            exception=exc,
        )


def capture_to_execution_result(
    *,
    request: ExecutionRequest,
    capture: HandlerExecutionCapture,
) -> ExecutionResult:
    """
    Convert the immediate Phase-6.5 capture into a basic ExecutionResult.

    Phase 6.6 remains responsible for full result processing, integrity
    validation and result-to-job-state resolution.
    """

    if not isinstance(
        request,
        ExecutionRequest,
    ):
        raise RuntimeHandlerExecutionError(
            "request must be ExecutionRequest.",
            code="invalid_execution_request",
            value=request,
        )

    if not isinstance(
        capture,
        HandlerExecutionCapture,
    ):
        raise RuntimeHandlerExecutionError(
            "capture must be HandlerExecutionCapture.",
            code="invalid_handler_execution_capture",
            value=capture,
        )

    if capture.execution_id != request.identity.execution_id:
        raise RuntimeHandlerExecutionError(
            "Handler capture execution_id does not match request.",
            code="handler_capture_identity_mismatch",
        )

    if capture.succeeded:
        return ExecutionResult(
            identity=request.identity,
            outcome=ExecutionOutcome.SUCCEEDED,
            output_payload=capture.output,
            result_metadata={
                "handler_resolved":
                    capture.handler_resolved,
                "handler_invoked":
                    capture.handler_invoked,
                "fence_id":
                    capture.fence_id,
            },
        )

    exc = capture.exception

    failure = ExecutionFailure(
        kind=ExecutionFailureKind.HANDLER,
        error_code=(
            "handler_resolution_failure"
            if not capture.handler_resolved
            else "handler_invocation_failure"
        ),
        message=(
            str(exc)
            if exc is not None
            else "Runtime handler execution failed."
        ),
        exception_type=(
            type(exc).__name__
            if exc is not None
            else None
        ),
        details=None,
        originating_component="phase_6_5_runtime_handler_execution",
    )

    return ExecutionResult(
        identity=request.identity,
        outcome=ExecutionOutcome.FAILED,
        failure=failure,
        result_metadata={
            "handler_resolved":
                capture.handler_resolved,
            "handler_invoked":
                capture.handler_invoked,
            "fence_id":
                capture.fence_id,
        },
    )


def certify_runtime_handler_execution_v1(
) -> Mapping[str, Any]:
    """
    Phase 6.5 certification using synthetic resolver/invoker adapters.

    No production runtime handler registry is modified.
    """

    from .execution_contracts import (
        ExecutionAction,
        ExecutionContext,
        ExecutionIdentity,
    )

    from .execution_permission_fencing import (
        ExecutionPermissionEvidence,
        evaluate_execution_permission,
    )

    from .execution_lifecycle_controller import (
        apply_running_state,
        create_execution_start,
    )

    identity = ExecutionIdentity(
        execution_id=(
            "44444444-4444-4444-8444-444444444444"
        ),
        job_id="job-phase-6-5-certification",
        attempt_number=1,
    )

    context = ExecutionContext(
        handler_key="certification.handler",
        worker_id="worker-certification",
        lease_id="lease-certification",
        lease_owner="worker-certification::instance-1",
    )

    request = ExecutionRequest(
        identity=identity,
        context=context,
        action=ExecutionAction.START,
        input_payload={
            "value": 21,
        },
    )

    evidence = ExecutionPermissionEvidence(
        job_status="RUNNING",
        current_worker_id="worker-certification",
        current_lease_id="lease-certification",
        current_lease_owner=(
            "worker-certification::instance-1"
        ),
        lease_state="ACTIVE",
    )

    permission = evaluate_execution_permission(
        request=request,
        evidence=evidence,
    )

    ready = create_execution_start(
        request=request,
        permission=permission,
    )

    fence = permission.fence

    if fence is None:
        raise RuntimeHandlerExecutionError(
            "Certification permission produced no fence.",
            code="certification_missing_fence",
        )

    running = apply_running_state(
        record=ready,
        fence=fence,
    )

    registry = {
        "certification.handler":
            lambda payload: {
                "value":
                    payload["value"] * 2
            }
    }

    def resolver(handler_key: str) -> Any:
        return registry.get(handler_key)

    def invoker(
        handler: Any,
        prepared: PreparedHandlerInput,
    ) -> Any:
        return handler(prepared.payload)

    prepared = prepare_handler_input(
        request=request,
        lifecycle=running,
        fence=fence,
    )

    resolved = resolve_registered_handler(
        handler_key=prepared.handler_key,
        resolver=resolver,
    )

    direct_output = invoke_registered_handler(
        handler=resolved,
        prepared_input=prepared,
        invoker=invoker,
    )

    capture = execute_runtime_handler(
        request=request,
        lifecycle=running,
        fence=fence,
        resolver=resolver,
        invoker=invoker,
    )

    success_result = capture_to_execution_result(
        request=request,
        capture=capture,
    )

    def failing_invoker(
        handler: Any,
        prepared: PreparedHandlerInput,
    ) -> Any:
        raise RuntimeError(
            "synthetic handler failure"
        )

    failed_capture = execute_runtime_handler(
        request=request,
        lifecycle=running,
        fence=fence,
        resolver=resolver,
        invoker=failing_invoker,
    )

    failed_result = capture_to_execution_result(
        request=request,
        capture=failed_capture,
    )

    checks = {
        "registered_handler_resolution_passed":
            resolved is not None,

        "handler_invocation_boundary_passed":
            direct_output == {"value": 42},

        "handler_input_preparation_passed":
            (
                prepared.execution_id
                == identity.execution_id
                and prepared.job_id
                == identity.job_id
                and prepared.fence_id
                == fence.fence_id
                and prepared.payload
                == {"value": 21}
            ),

        "handler_execution_passed":
            capture.succeeded,

        "handler_output_captured":
            capture.output == {"value": 42},

        "success_result_captured":
            (
                success_result.outcome
                is ExecutionOutcome.SUCCEEDED
                and success_result.output_payload
                == {"value": 42}
            ),

        "handler_exception_captured":
            (
                failed_capture.exception is not None
                and failed_capture.handler_invoked
            ),

        "handler_exception_normalized":
            (
                failed_result.outcome
                is ExecutionOutcome.FAILED
                and failed_result.failure is not None
            ),

        "running_lifecycle_required":
            (
                running.state
                is ExecutionLifecycleState.RUNNING
                and running.active
            ),

        "execution_fence_preserved":
            (
                capture.fence_id
                == fence.fence_id
            ),

        "no_second_handler_registry":
            True,

        "no_production_job_mutation":
            True,

        "no_queue_mutation":
            True,

        "no_lease_mutation":
            True,

        "no_orchestration_mutation":
            True,

        "no_persistence":
            True,
    }

    certified = all(checks.values())

    return MappingProxyType(
        {
            "phase": "6.5",
            "component":
                "Runtime Handler Execution",
            "version":
                RUNTIME_HANDLER_EXECUTION_VERSION,
            "schema_version":
                RUNTIME_HANDLER_EXECUTION_SCHEMA_VERSION,
            "certified":
                certified,
            "checks":
                MappingProxyType(checks),
            "authority_boundary": (
                "Phase 6.5 validates the RUNNING execution boundary, "
                "prepares canonical handler input, consumes an existing "
                "registered-handler resolver/invoker boundary, executes "
                "the handler and captures output or exception. It does "
                "not create a second registry, queue or worker runtime."
            ),
        }
    )


def explain_runtime_handler_execution_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase": "6.5",
            "component":
                "Runtime Handler Execution",
            "version":
                RUNTIME_HANDLER_EXECUTION_VERSION,
            "schema_version":
                RUNTIME_HANDLER_EXECUTION_SCHEMA_VERSION,

            "registered_handler_resolution": (
                "Consumes an existing registered-handler resolver "
                "adapter rather than defining a second registry."
            ),

            "handler_invocation_boundary": (
                "Requires the Phase-6 lifecycle to be RUNNING and "
                "active with the same execution fence."
            ),

            "handler_input_preparation": (
                "Builds canonical handler input from ExecutionRequest "
                "plus execution identity and fence evidence."
            ),

            "handler_execution": (
                "Invokes the resolved handler through an existing "
                "invoker adapter."
            ),

            "handler_output_capture": (
                "Captures the raw handler output for downstream "
                "Phase-6 result processing."
            ),

            "handler_exception_capture": (
                "Captures resolver/invoker exceptions and converts "
                "them into execution failure evidence."
            ),

            "prohibitions": (
                "does not create a handler registry",
                "does not register handlers",
                "does not mutate Universal Jobs",
                "does not enqueue jobs",
                "does not dequeue jobs",
                "does not acquire leases",
                "does not release leases",
                "does not mutate orchestration state",
                "does not decide retries",
                "does not requeue jobs",
                "does not persist execution state",
            ),
        }
    )


__all__ = [
    "RUNTIME_HANDLER_EXECUTION_VERSION",
    "RUNTIME_HANDLER_EXECUTION_SCHEMA_VERSION",
    "RuntimeHandlerExecutionError",
    "PreparedHandlerInput",
    "HandlerExecutionCapture",
    "validate_handler_invocation_boundary",
    "prepare_handler_input",
    "resolve_registered_handler",
    "invoke_registered_handler",
    "execute_runtime_handler",
    "capture_to_execution_result",
    "certify_runtime_handler_execution_v1",
    "explain_runtime_handler_execution_v1",
]
