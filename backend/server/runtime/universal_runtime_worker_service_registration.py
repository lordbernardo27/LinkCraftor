from __future__ import annotations

"""
Register the existing Universal Runtime Worker with the
canonical runtime lifecycle.

Production execution remains explicitly disabled until
separate queue-safety and activation certification.
"""

from backend.server.runtime.universal_runtime_worker_service import (
    UniversalRuntimeWorkerService,
)
from backend.server.runtime.universal_runtime_worker_scope_contract import validate_trusted_worker_scope

WORKER_SERVICE_KEY = "universal_runtime_worker_service"


def register_universal_runtime_worker_service(composition, *, trusted_scope=None):
    verified_scope = (
        validate_trusted_worker_scope(trusted_scope)
        if trusted_scope is not None
        else None
    )
    service = UniversalRuntimeWorkerService(
        kernel=composition.kernel,
        poll_interval_seconds=(
            composition.configuration.queue_poll_interval_seconds
        ),
        enabled=False,
        allowed_job_ids=verified_scope,
    )

    composition.service_registry.register(
        WORKER_SERVICE_KEY,
        service,
        capabilities=("universal_runtime", "queue_worker"),
        startup_order=900,
        critical=True,
    )


    # AK_REGISTERED_WORKER_INSTANCE_BINDING
    # Verify exact runtime-owned service binding for
    # explicitly scoped Connected Domain registration.
    # This check is NOT execution authorization.
    if verified_scope is not None:
        from backend.server.runtime.universal_runtime_worker_scope_contract import (
            EXPECTED_SCOPE,
        )

        if verified_scope != EXPECTED_SCOPE:
            raise RuntimeError(
                "Worker registration rejected: "
                "noncanonical activation scope."
            )

        registered_service = (
            composition.service_registry.get(
                WORKER_SERVICE_KEY
            )
        )

        if registered_service is not service:
            raise RuntimeError(
                "Worker registration rejected: "
                "service instance identity mismatch."
            )

        if (
            service.worker_id != "universal_runtime_worker_v1"
            or service.allowed_job_ids != EXPECTED_SCOPE
            or service.enabled is not False
            or service.authorization_check is not None
        ):
            raise RuntimeError(
                "Worker registration rejected: "
                "unsafe worker activation configuration."
            )

    return service
