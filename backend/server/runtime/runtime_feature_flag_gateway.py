from __future__ import annotations

from backend.server.runtime.runtime_feature_flags import (
    RuntimeFeatureFlagContext,
    RuntimeFeatureFlagRegistry,
    get_runtime_feature_flag_registry,
)

GATEWAY_KEY = "runtime_feature_flags"
REGISTRY_KEY = "runtime_feature_flag_registry"


class RuntimeFeatureFlagGateway:
    """Runtime context adapter; the canonical registry owns evaluation."""

    def __init__(self, *, registry, environment, runtime_id):
        if not isinstance(registry, RuntimeFeatureFlagRegistry):
            raise TypeError("Expected the canonical feature-flag registry.")
        if not isinstance(environment, str) or not environment.strip():
            raise ValueError("environment must be a non-empty string.")
        if not isinstance(runtime_id, str) or not runtime_id.strip():
            raise ValueError("runtime_id must be a non-empty string.")
        self.registry = registry
        self.environment = environment.strip()
        self.runtime_id = runtime_id.strip()

    def evaluate(
        self, flag_key, *, evaluation_key=None, workspace_id=None,
        plan_id=None, worker_class=None, runtime_version=None,
        attributes=None, actor="runtime_feature_flag_gateway",
    ):
        context = RuntimeFeatureFlagContext(
            environment=self.environment,
            evaluation_key=(
                self.runtime_id if evaluation_key is None else evaluation_key
            ),
            workspace_id=workspace_id,
            plan_id=plan_id,
            worker_class=worker_class,
            runtime_version=runtime_version,
            attributes={} if attributes is None else attributes,
        )
        return self.registry.evaluate(flag_key, context, actor=actor)

    def is_enabled(self, flag_name):
        return self.evaluate(flag_name).enabled is True

    def snapshot(self):
        return self.registry.snapshot()

    def evidence(self):
        snapshot = self.snapshot()
        return {
            "runtime_id": self.runtime_id,
            "environment": self.environment,
            "generation": snapshot.generation,
            "flag_count": len(snapshot.flags),
            "snapshot_fingerprint": snapshot.fingerprint,
        }


def register_runtime_feature_flag_gateway(composition):
    registry = get_runtime_feature_flag_registry()
    gateway = RuntimeFeatureFlagGateway(
        registry=registry,
        environment=composition.configuration.environment,
        runtime_id=composition.configuration.runtime_id,
    )
    kernel = composition.kernel
    if kernel.has_component(REGISTRY_KEY) or kernel.has_component(GATEWAY_KEY):
        raise RuntimeError("Feature-flag kernel binding already exists.")
    kernel.bind_component(REGISTRY_KEY, registry)
    kernel.bind_component(GATEWAY_KEY, gateway)
    bind_runtime_queue_claim_gate(
        gateway, worker_enabled=composition.configuration.worker_enabled,
        kernel=composition.kernel
    )
    return gateway


# A1.11: process-local admission adapter; registry remains the authority.
from threading import RLock
from backend.server.runtime.runtime_feature_flags import (
    RuntimeFeatureFlag, RuntimeFeatureFlagState,
    RuntimeFeatureFlagNotFoundError, RuntimeFeatureFlagDecisionReason,
)

QUEUE_CLAIMS_FLAG = "runtime.queue.claims_enabled"
_claim_binding_lock = RLock()
_claim_binding = None


def bind_runtime_queue_claim_gate(gateway, *, worker_enabled, kernel):
    global _claim_binding
    if not isinstance(gateway, RuntimeFeatureFlagGateway):
        raise TypeError("Queue claims require the canonical gateway.")
    if not isinstance(kernel, UniversalRuntimeKernel):
        raise TypeError("Queue claims require the canonical kernel.")
    if type(worker_enabled) is not bool:
        raise TypeError("worker_enabled must be bool.")
    with _claim_binding_lock:
        if _claim_binding is not None:
            old, old_enabled, old_kernel = _claim_binding
            if (old_kernel is not kernel
                    and old_kernel.snapshot().state
                    is RuntimeKernelState.RUNNING):
                raise RuntimeError("Another runtime kernel is running.")
            if (old.registry is not gateway.registry
                    or old.runtime_id != gateway.runtime_id
                    or old.environment != gateway.environment
                    or old_enabled != worker_enabled):
                raise RuntimeError("Conflicting runtime queue-claim binding.")
        try:
            gateway.registry.get(QUEUE_CLAIMS_FLAG)
        except RuntimeFeatureFlagNotFoundError:
            gateway.registry.register(
                RuntimeFeatureFlag(
                    key=QUEUE_CLAIMS_FLAG,
                    state=(RuntimeFeatureFlagState.ENABLED if worker_enabled
                           else RuntimeFeatureFlagState.DISABLED),
                    owner="universal_runtime",
                    description="Admission of new queue claims.",
                    safe_default_enabled=False,
                ),
                actor="runtime_boot",
            )
        _claim_binding = (gateway, worker_enabled, kernel)


def runtime_queue_claims_enabled(*, worker_id=None):
    with _claim_binding_lock:
        binding = _claim_binding
    if binding is None:
        return False
    gateway, worker_enabled, kernel = binding
    if kernel.snapshot().state is not RuntimeKernelState.RUNNING:
        return False
    if not worker_enabled:
        return False
    decision = gateway.evaluate(
        QUEUE_CLAIMS_FLAG,
        evaluation_key=str(worker_id or gateway.runtime_id),
        actor="queue_claim_admission",
    )
    return (decision.enabled is True
            and decision.reason is RuntimeFeatureFlagDecisionReason.ENABLED)


from backend.server.runtime.universal_runtime_kernel import (
    UniversalRuntimeKernel,
    RuntimeKernelState,
)
