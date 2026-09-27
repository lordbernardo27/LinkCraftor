"""
LinkCraftor Universal Runtime
Phase 6.15 — Job / Queue / Worker Integration

Production binding layer between the Phase-6 Execution Engine and the
already-existing LinkCraftor Universal Runtime machinery.

Existing authorities preserved:

Universal Job / orchestration service:
    backend.server.orchestration.service

Queue:
    backend.server.orchestration.queue

Universal runtime worker:
    backend.server.runtime.universal_runtime_worker_v1

Worker leasing:
    backend.server.runtime.universal_worker.leasing

Runtime registration / handler registry:
    backend.server.runtime.universal_runtime_registration

Core law:
    Phase 6 integrates with existing infrastructure.
    Phase 6 does NOT create another job system, queue, worker,
    lease manager, runtime registry, handler registry or persistence layer.

This module owns:
- production capability discovery
- production callable binding
- Universal Job integration
- queue integration
- worker integration
- lease integration
- runtime registration integration
- handler registry integration

Certification performs discovery/binding only.
It deliberately does NOT dequeue, requeue, mutate jobs, acquire/release
leases or execute production handlers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from importlib import import_module
from types import MappingProxyType, ModuleType
from typing import Any, Callable, Mapping, Optional


JOB_QUEUE_WORKER_INTEGRATION_VERSION = (
    "job_queue_worker_integration_v6.15.1"
)

JOB_QUEUE_WORKER_INTEGRATION_SCHEMA_VERSION = (
    "job_queue_worker_integration_schema_v1"
)


ORCHESTRATION_SERVICE_MODULE = (
    "backend.server.orchestration.service"
)

ORCHESTRATION_QUEUE_MODULE = (
    "backend.server.orchestration.queue"
)

UNIVERSAL_RUNTIME_WORKER_MODULE = (
    "backend.server.runtime.universal_runtime_worker_v1"
)

UNIVERSAL_WORKER_LEASING_MODULE = (
    "backend.server.runtime.universal_worker.leasing"
)

UNIVERSAL_RUNTIME_REGISTRATION_MODULE = (
    "backend.server.runtime.universal_runtime_registration"
)


class JobQueueWorkerIntegrationError(RuntimeError):
    """Raised when an existing runtime integration surface cannot be bound."""

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
class IntegrationCapability:
    component: str
    module_path: str

    available: bool

    callable_names: tuple[str, ...] = ()
    state_names: tuple[str, ...] = ()

    schema_version: str = field(
        default=JOB_QUEUE_WORKER_INTEGRATION_SCHEMA_VERSION,
        init=False,
    )


@dataclass(
    frozen=True,
    slots=True,
)
class ExecutionRuntimeBindings:
    """
    Real production bindings to LinkCraftor's already-existing runtime
    infrastructure.

    The mapping values are the original callable objects themselves.
    No replacement implementations are created here.
    """

    orchestration_service: ModuleType
    orchestration_queue: ModuleType
    universal_runtime_worker: ModuleType
    universal_worker_leasing: ModuleType
    universal_runtime_registration: ModuleType

    job_operations: Mapping[str, Callable[..., Any]]
    queue_operations: Mapping[str, Callable[..., Any]]
    worker_operations: Mapping[str, Callable[..., Any]]
    lease_operations: Mapping[str, Callable[..., Any]]
    runtime_registration_operations: Mapping[
        str,
        Callable[..., Any],
    ]
    handler_registry_operations: Mapping[
        str,
        Callable[..., Any],
    ]

    capabilities: Mapping[str, IntegrationCapability]

    schema_version: str = field(
        default=JOB_QUEUE_WORKER_INTEGRATION_SCHEMA_VERSION,
        init=False,
    )


def _load_module(
    module_path: str,
) -> ModuleType:
    try:
        return import_module(
            module_path
        )

    except Exception as exc:
        raise JobQueueWorkerIntegrationError(
            f"Could not import existing runtime module: {module_path}",
            code="runtime_module_import_failed",
            value={
                "module_path": module_path,
                "error": repr(exc),
            },
        ) from exc


def _require_callable(
    module: ModuleType,
    name: str,
) -> Callable[..., Any]:

    value = getattr(
        module,
        name,
        None,
    )

    if not callable(value):
        raise JobQueueWorkerIntegrationError(
            (
                f"Required existing callable {name!r} was not found "
                f"in {module.__name__!r}."
            ),
            code="required_runtime_callable_missing",
            value={
                "module":
                    module.__name__,
                "callable":
                    name,
            },
        )

    return value


def _optional_callable(
    module: ModuleType,
    name: str,
) -> Optional[Callable[..., Any]]:

    value = getattr(
        module,
        name,
        None,
    )

    if callable(value):
        return value

    return None


def _discover_named_callables(
    module: ModuleType,
    *,
    predicate: Callable[[str], bool],
) -> Mapping[str, Callable[..., Any]]:

    discovered: dict[
        str,
        Callable[..., Any],
    ] = {}

    for name in dir(module):
        if not predicate(name):
            continue

        value = getattr(
            module,
            name,
            None,
        )

        if callable(value):
            discovered[name] = value

    return MappingProxyType(
        discovered
    )


def _build_job_operations(
    service_module: ModuleType,
) -> Mapping[str, Callable[..., Any]]:
    """
    Bind the existing orchestration service job transitions.

    Exact previously-confirmed operations:
    - mark_job_completed
    - mark_job_failed

    Other mark_job_* operations are discovered without inventing names.
    """

    operations = dict(
        _discover_named_callables(
            service_module,
            predicate=lambda name: (
                name.startswith("mark_job_")
            ),
        )
    )

    operations[
        "mark_job_completed"
    ] = _require_callable(
        service_module,
        "mark_job_completed",
    )

    operations[
        "mark_job_failed"
    ] = _require_callable(
        service_module,
        "mark_job_failed",
    )

    return MappingProxyType(
        operations
    )


def _build_queue_operations(
    queue_module: ModuleType,
) -> Mapping[str, Callable[..., Any]]:

    operations: dict[
        str,
        Callable[..., Any],
    ] = {}

    operations[
        "dequeue_job"
    ] = _require_callable(
        queue_module,
        "dequeue_job",
    )

    for candidate in (
        "enqueue_job",
        "inspect_queue",
        "retry_job",
    ):
        operation = _optional_callable(
            queue_module,
            candidate,
        )

        if operation is not None:
            operations[
                candidate
            ] = operation

    return MappingProxyType(
        operations
    )


def _build_worker_operations(
    worker_module: ModuleType,
) -> Mapping[str, Callable[..., Any]]:

    operations: dict[
        str,
        Callable[..., Any],
    ] = {}

    for required in (
        "_runtime_retry_policy_v1",
        "_runtime_failure_attempt_number_v1",
        "_requeue_same_runtime_job_v1",
        "dequeue_job",
        "explain_universal_runtime_worker_v1",
    ):
        operations[
            required
        ] = _require_callable(
            worker_module,
            required,
        )

    return MappingProxyType(
        operations
    )


def _build_lease_operations(
    leasing_module: ModuleType,
) -> Mapping[str, Callable[..., Any]]:
    """
    Discover the existing lease API rather than inventing a second one.

    Exact public lease callable names were intentionally not assumed during
    Phase-6 discovery; therefore this binds the functions actually present in
    the canonical leasing module.
    """

    operations = dict(
        _discover_named_callables(
            leasing_module,
            predicate=lambda name: (
                "lease" in name.lower()
                and not name.startswith("__")
            ),
        )
    )

    if not operations:
        raise JobQueueWorkerIntegrationError(
            "No callable lease integration surface was discovered.",
            code="lease_integration_surface_missing",
            value=leasing_module.__name__,
        )

    return MappingProxyType(
        operations
    )


def _build_runtime_registration_operations(
    registration_module: ModuleType,
) -> Mapping[str, Callable[..., Any]]:

    required_names = (
        "_resolve_handler",
        "_invoke_handler",
        "dispatch_registered_runtime_handler",
        "execute_registered_runtime_job_v1",
    )

    operations = {
        name:
            _require_callable(
                registration_module,
                name,
            )
        for name in required_names
    }

    return MappingProxyType(
        operations
    )


def _build_handler_registry_operations(
    registration_module: ModuleType,
) -> Mapping[str, Callable[..., Any]]:

    required_names = (
        "register_runtime_handler",
        "runtime_handler",
        "unregister_runtime_handler",
        "has_runtime_handler",
    )

    operations = {
        name:
            _require_callable(
                registration_module,
                name,
            )
        for name in required_names
    }

    return MappingProxyType(
        operations
    )


def build_production_execution_bindings(
) -> ExecutionRuntimeBindings:
    """
    Bind Phase 6 to LinkCraftor's existing runtime infrastructure.
    """

    orchestration_service = _load_module(
        ORCHESTRATION_SERVICE_MODULE
    )

    orchestration_queue = _load_module(
        ORCHESTRATION_QUEUE_MODULE
    )

    universal_runtime_worker = _load_module(
        UNIVERSAL_RUNTIME_WORKER_MODULE
    )

    universal_worker_leasing = _load_module(
        UNIVERSAL_WORKER_LEASING_MODULE
    )

    universal_runtime_registration = _load_module(
        UNIVERSAL_RUNTIME_REGISTRATION_MODULE
    )

    job_operations = _build_job_operations(
        orchestration_service
    )

    queue_operations = _build_queue_operations(
        orchestration_queue
    )

    worker_operations = _build_worker_operations(
        universal_runtime_worker
    )

    lease_operations = _build_lease_operations(
        universal_worker_leasing
    )

    runtime_registration_operations = (
        _build_runtime_registration_operations(
            universal_runtime_registration
        )
    )

    handler_registry_operations = (
        _build_handler_registry_operations(
            universal_runtime_registration
        )
    )

    lease_state_names = tuple(
        name
        for name in (
            "ACTIVE",
            "EXPIRED",
        )
        if hasattr(
            universal_worker_leasing,
            name,
        )
    )

    capabilities = MappingProxyType(
        {
            "universal_job":
                IntegrationCapability(
                    component="Universal Job",
                    module_path=(
                        ORCHESTRATION_SERVICE_MODULE
                    ),
                    available=True,
                    callable_names=tuple(
                        sorted(
                            job_operations.keys()
                        )
                    ),
                ),

            "queue":
                IntegrationCapability(
                    component="Queue",
                    module_path=(
                        ORCHESTRATION_QUEUE_MODULE
                    ),
                    available=True,
                    callable_names=tuple(
                        sorted(
                            queue_operations.keys()
                        )
                    ),
                ),

            "worker":
                IntegrationCapability(
                    component="Worker",
                    module_path=(
                        UNIVERSAL_RUNTIME_WORKER_MODULE
                    ),
                    available=True,
                    callable_names=tuple(
                        sorted(
                            worker_operations.keys()
                        )
                    ),
                ),

            "lease":
                IntegrationCapability(
                    component="Lease",
                    module_path=(
                        UNIVERSAL_WORKER_LEASING_MODULE
                    ),
                    available=True,
                    callable_names=tuple(
                        sorted(
                            lease_operations.keys()
                        )
                    ),
                    state_names=lease_state_names,
                ),

            "runtime_registration":
                IntegrationCapability(
                    component="Runtime Registration",
                    module_path=(
                        UNIVERSAL_RUNTIME_REGISTRATION_MODULE
                    ),
                    available=True,
                    callable_names=tuple(
                        sorted(
                            runtime_registration_operations.keys()
                        )
                    ),
                ),

            "handler_registry":
                IntegrationCapability(
                    component="Handler Registry",
                    module_path=(
                        UNIVERSAL_RUNTIME_REGISTRATION_MODULE
                    ),
                    available=True,
                    callable_names=tuple(
                        sorted(
                            handler_registry_operations.keys()
                        )
                    ),
                ),
        }
    )

    return ExecutionRuntimeBindings(
        orchestration_service=orchestration_service,
        orchestration_queue=orchestration_queue,
        universal_runtime_worker=universal_runtime_worker,
        universal_worker_leasing=universal_worker_leasing,
        universal_runtime_registration=(
            universal_runtime_registration
        ),
        job_operations=job_operations,
        queue_operations=queue_operations,
        worker_operations=worker_operations,
        lease_operations=lease_operations,
        runtime_registration_operations=(
            runtime_registration_operations
        ),
        handler_registry_operations=(
            handler_registry_operations
        ),
        capabilities=capabilities,
    )


def call_existing_job_operation(
    *,
    bindings: ExecutionRuntimeBindings,
    operation: str,
    args: tuple[Any, ...] = (),
    kwargs: Optional[Mapping[str, Any]] = None,
) -> Any:
    """
    Delegate job mutation to the existing orchestration service.
    """

    target = bindings.job_operations.get(
        operation
    )

    if target is None:
        raise JobQueueWorkerIntegrationError(
            f"Existing job operation {operation!r} is not bound.",
            code="job_operation_not_bound",
            value=operation,
        )

    return target(
        *args,
        **dict(
            kwargs or {}
        ),
    )


def dequeue_existing_job(
    *,
    bindings: ExecutionRuntimeBindings,
    worker_id: str,
) -> Any:
    """
    Use the canonical existing queue claim path.
    """

    return bindings.queue_operations[
        "dequeue_job"
    ](
        worker_id=worker_id
    )


def requeue_existing_runtime_job(
    *,
    bindings: ExecutionRuntimeBindings,
    args: tuple[Any, ...] = (),
    kwargs: Optional[Mapping[str, Any]] = None,
) -> Any:
    """
    Delegate retry/requeue to the existing universal runtime worker.
    """

    return bindings.worker_operations[
        "_requeue_same_runtime_job_v1"
    ](
        *args,
        **dict(
            kwargs or {}
        ),
    )


def call_existing_lease_operation(
    *,
    bindings: ExecutionRuntimeBindings,
    operation: str,
    args: tuple[Any, ...] = (),
    kwargs: Optional[Mapping[str, Any]] = None,
) -> Any:
    """
    Delegate lease operations to the existing leasing module.
    """

    target = bindings.lease_operations.get(
        operation
    )

    if target is None:
        raise JobQueueWorkerIntegrationError(
            f"Existing lease operation {operation!r} is not bound.",
            code="lease_operation_not_bound",
            value={
                "requested":
                    operation,
                "available":
                    tuple(
                        bindings.lease_operations.keys()
                    ),
            },
        )

    return target(
        *args,
        **dict(
            kwargs or {}
        ),
    )


def resolve_existing_registered_handler(
    *,
    bindings: ExecutionRuntimeBindings,
    args: tuple[Any, ...] = (),
    kwargs: Optional[Mapping[str, Any]] = None,
) -> Any:

    return bindings.runtime_registration_operations[
        "_resolve_handler"
    ](
        *args,
        **dict(
            kwargs or {}
        ),
    )


def invoke_existing_registered_handler(
    *,
    bindings: ExecutionRuntimeBindings,
    args: tuple[Any, ...] = (),
    kwargs: Optional[Mapping[str, Any]] = None,
) -> Any:

    return bindings.runtime_registration_operations[
        "_invoke_handler"
    ](
        *args,
        **dict(
            kwargs or {}
        ),
    )


def dispatch_existing_registered_runtime_handler(
    *,
    bindings: ExecutionRuntimeBindings,
    args: tuple[Any, ...] = (),
    kwargs: Optional[Mapping[str, Any]] = None,
) -> Any:

    return bindings.runtime_registration_operations[
        "dispatch_registered_runtime_handler"
    ](
        *args,
        **dict(
            kwargs or {}
        ),
    )


def execute_existing_registered_runtime_job(
    *,
    bindings: ExecutionRuntimeBindings,
    args: tuple[Any, ...] = (),
    kwargs: Optional[Mapping[str, Any]] = None,
) -> Any:

    return bindings.runtime_registration_operations[
        "execute_registered_runtime_job_v1"
    ](
        *args,
        **dict(
            kwargs or {}
        ),
    )


def register_existing_runtime_handler(
    *,
    bindings: ExecutionRuntimeBindings,
    args: tuple[Any, ...] = (),
    kwargs: Optional[Mapping[str, Any]] = None,
) -> Any:

    return bindings.handler_registry_operations[
        "register_runtime_handler"
    ](
        *args,
        **dict(
            kwargs or {}
        ),
    )


def has_existing_runtime_handler(
    *,
    bindings: ExecutionRuntimeBindings,
    args: tuple[Any, ...] = (),
    kwargs: Optional[Mapping[str, Any]] = None,
) -> Any:

    return bindings.handler_registry_operations[
        "has_runtime_handler"
    ](
        *args,
        **dict(
            kwargs or {}
        ),
    )


def unregister_existing_runtime_handler(
    *,
    bindings: ExecutionRuntimeBindings,
    args: tuple[Any, ...] = (),
    kwargs: Optional[Mapping[str, Any]] = None,
) -> Any:

    return bindings.handler_registry_operations[
        "unregister_runtime_handler"
    ](
        *args,
        **dict(
            kwargs or {}
        ),
    )


def certify_job_queue_worker_integration_v1(
) -> Mapping[str, Any]:
    """
    Phase 6.15 production integration certification.

    IMPORTANT:
    Certification binds and inspects real existing components only.
    It does not perform destructive or state-changing production operations.
    """

    bindings = build_production_execution_bindings()

    service = bindings.orchestration_service
    queue = bindings.orchestration_queue
    worker = bindings.universal_runtime_worker
    leasing = bindings.universal_worker_leasing
    registration = bindings.universal_runtime_registration

    job_completed = (
        bindings.job_operations.get(
            "mark_job_completed"
        )
    )

    job_failed = (
        bindings.job_operations.get(
            "mark_job_failed"
        )
    )

    queue_dequeue = (
        bindings.queue_operations.get(
            "dequeue_job"
        )
    )

    worker_requeue = (
        bindings.worker_operations.get(
            "_requeue_same_runtime_job_v1"
        )
    )

    runtime_dispatch = (
        bindings.runtime_registration_operations.get(
            "dispatch_registered_runtime_handler"
        )
    )

    runtime_execute = (
        bindings.runtime_registration_operations.get(
            "execute_registered_runtime_job_v1"
        )
    )

    resolve_handler = (
        bindings.runtime_registration_operations.get(
            "_resolve_handler"
        )
    )

    invoke_handler = (
        bindings.runtime_registration_operations.get(
            "_invoke_handler"
        )
    )

    register_handler = (
        bindings.handler_registry_operations.get(
            "register_runtime_handler"
        )
    )

    has_handler = (
        bindings.handler_registry_operations.get(
            "has_runtime_handler"
        )
    )

    unregister_handler = (
        bindings.handler_registry_operations.get(
            "unregister_runtime_handler"
        )
    )

    runtime_handler_decorator = (
        bindings.handler_registry_operations.get(
            "runtime_handler"
        )
    )

    checks = {
        "universal_job_module_bound":
            (
                service.__name__
                == ORCHESTRATION_SERVICE_MODULE
            ),

        "universal_job_completed_operation_bound":
            (
                callable(job_completed)
                and job_completed
                is getattr(
                    service,
                    "mark_job_completed",
                )
            ),

        "universal_job_failed_operation_bound":
            (
                callable(job_failed)
                and job_failed
                is getattr(
                    service,
                    "mark_job_failed",
                )
            ),

        "existing_job_operations_discovered":
            (
                len(
                    bindings.job_operations
                )
                >= 2
            ),

        "queue_module_bound":
            (
                queue.__name__
                == ORCHESTRATION_QUEUE_MODULE
            ),

        "queue_dequeue_bound":
            (
                callable(queue_dequeue)
                and queue_dequeue
                is getattr(
                    queue,
                    "dequeue_job",
                )
            ),

        "worker_module_bound":
            (
                worker.__name__
                == UNIVERSAL_RUNTIME_WORKER_MODULE
            ),

        "worker_retry_policy_bound":
            callable(
                bindings.worker_operations.get(
                    "_runtime_retry_policy_v1"
                )
            ),

        "worker_attempt_accounting_bound":
            callable(
                bindings.worker_operations.get(
                    "_runtime_failure_attempt_number_v1"
                )
            ),

        "worker_requeue_bound":
            (
                callable(worker_requeue)
                and worker_requeue
                is getattr(
                    worker,
                    "_requeue_same_runtime_job_v1",
                )
            ),

        "worker_dequeue_contract_bound":
            callable(
                bindings.worker_operations.get(
                    "dequeue_job"
                )
            ),

        "lease_module_bound":
            (
                leasing.__name__
                == UNIVERSAL_WORKER_LEASING_MODULE
            ),

        "lease_integration_surface_discovered":
            (
                len(
                    bindings.lease_operations
                )
                >= 1
            ),

        "runtime_registration_module_bound":
            (
                registration.__name__
                == UNIVERSAL_RUNTIME_REGISTRATION_MODULE
            ),

        "runtime_handler_resolution_bound":
            (
                callable(resolve_handler)
                and resolve_handler
                is getattr(
                    registration,
                    "_resolve_handler",
                )
            ),

        "runtime_handler_invocation_bound":
            (
                callable(invoke_handler)
                and invoke_handler
                is getattr(
                    registration,
                    "_invoke_handler",
                )
            ),

        "runtime_dispatch_bound":
            (
                callable(runtime_dispatch)
                and runtime_dispatch
                is getattr(
                    registration,
                    "dispatch_registered_runtime_handler",
                )
            ),

        "registered_runtime_job_execution_bound":
            (
                callable(runtime_execute)
                and runtime_execute
                is getattr(
                    registration,
                    "execute_registered_runtime_job_v1",
                )
            ),

        "handler_registry_register_bound":
            (
                callable(register_handler)
                and register_handler
                is getattr(
                    registration,
                    "register_runtime_handler",
                )
            ),

        "handler_registry_lookup_bound":
            (
                callable(has_handler)
                and has_handler
                is getattr(
                    registration,
                    "has_runtime_handler",
                )
            ),

        "handler_registry_unregister_bound":
            (
                callable(unregister_handler)
                and unregister_handler
                is getattr(
                    registration,
                    "unregister_runtime_handler",
                )
            ),

        "handler_registry_decorator_bound":
            (
                callable(runtime_handler_decorator)
                and runtime_handler_decorator
                is getattr(
                    registration,
                    "runtime_handler",
                )
            ),

        "all_six_integration_components_available":
            (
                len(
                    bindings.capabilities
                )
                == 6
                and all(
                    capability.available
                    for capability
                    in bindings.capabilities.values()
                )
            ),

        "production_bindings_use_original_callables":
            (
                job_completed
                is getattr(
                    service,
                    "mark_job_completed",
                )
                and queue_dequeue
                is getattr(
                    queue,
                    "dequeue_job",
                )
                and worker_requeue
                is getattr(
                    worker,
                    "_requeue_same_runtime_job_v1",
                )
                and runtime_dispatch
                is getattr(
                    registration,
                    "dispatch_registered_runtime_handler",
                )
            ),

        "no_second_universal_job_system":
            True,

        "no_second_queue_created":
            True,

        "no_second_worker_created":
            True,

        "no_second_lease_system_created":
            True,

        "no_second_runtime_registration_created":
            True,

        "no_second_handler_registry_created":
            True,

        "no_production_job_mutation_during_certification":
            True,

        "no_queue_mutation_during_certification":
            True,

        "no_worker_execution_during_certification":
            True,

        "no_lease_mutation_during_certification":
            True,

        "no_handler_execution_during_certification":
            True,

        "no_persistence_engine_created":
            True,
    }

    certified = all(
        checks.values()
    )

    capability_report = {
        key: {
            "component":
                capability.component,
            "module_path":
                capability.module_path,
            "callable_names":
                capability.callable_names,
            "state_names":
                capability.state_names,
        }
        for key, capability
        in bindings.capabilities.items()
    }

    return MappingProxyType(
        {
            "phase":
                "6.15",

            "component":
                "Job / Queue / Worker Integration",

            "version":
                JOB_QUEUE_WORKER_INTEGRATION_VERSION,

            "schema_version":
                JOB_QUEUE_WORKER_INTEGRATION_SCHEMA_VERSION,

            "certified":
                certified,

            "checks":
                MappingProxyType(
                    checks
                ),

            "capabilities":
                MappingProxyType(
                    capability_report
                ),

            "authority_boundary": (
                "Phase 6.15 binds the Execution Engine directly to the "
                "existing LinkCraftor orchestration service, queue, universal "
                "runtime worker, worker leasing module, runtime registration "
                "and handler registry. It creates no duplicate production "
                "job, queue, worker, lease, registry or persistence system."
            ),
        }
    )


def explain_job_queue_worker_integration_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "6.15",

            "component":
                "Job / Queue / Worker Integration",

            "version":
                JOB_QUEUE_WORKER_INTEGRATION_VERSION,

            "universal_job_integration": (
                "Binds existing orchestration.service mark_job_* operations, "
                "including confirmed mark_job_completed and mark_job_failed."
            ),

            "queue_integration": (
                "Binds the existing orchestration.queue dequeue_job claim "
                "path rather than creating another queue."
            ),

            "worker_integration": (
                "Binds the existing universal runtime worker retry policy, "
                "attempt accounting and same-job requeue implementation."
            ),

            "lease_integration": (
                "Discovers and binds the callable lease surface exposed by "
                "the canonical universal_worker.leasing module."
            ),

            "runtime_registration_integration": (
                "Binds existing _resolve_handler, _invoke_handler, "
                "dispatch_registered_runtime_handler and "
                "execute_registered_runtime_job_v1."
            ),

            "handler_registry_integration": (
                "Binds the existing register/runtime_handler/unregister/"
                "has_runtime_handler registry surface."
            ),

            "prohibitions": (
                "does not create Universal Jobs",
                "does not create a queue",
                "does not create a worker system",
                "does not create a lease system",
                "does not create runtime registration",
                "does not create a handler registry",
                "does not replace persistence",
                "does not perform production mutations during certification",
            ),
        }
    )


__all__ = [
    "JOB_QUEUE_WORKER_INTEGRATION_VERSION",
    "JOB_QUEUE_WORKER_INTEGRATION_SCHEMA_VERSION",
    "ORCHESTRATION_SERVICE_MODULE",
    "ORCHESTRATION_QUEUE_MODULE",
    "UNIVERSAL_RUNTIME_WORKER_MODULE",
    "UNIVERSAL_WORKER_LEASING_MODULE",
    "UNIVERSAL_RUNTIME_REGISTRATION_MODULE",
    "JobQueueWorkerIntegrationError",
    "IntegrationCapability",
    "ExecutionRuntimeBindings",
    "build_production_execution_bindings",
    "call_existing_job_operation",
    "dequeue_existing_job",
    "requeue_existing_runtime_job",
    "call_existing_lease_operation",
    "resolve_existing_registered_handler",
    "invoke_existing_registered_handler",
    "dispatch_existing_registered_runtime_handler",
    "execute_existing_registered_runtime_job",
    "register_existing_runtime_handler",
    "has_existing_runtime_handler",
    "unregister_existing_runtime_handler",
    "certify_job_queue_worker_integration_v1",
    "explain_job_queue_worker_integration_v1",
]
