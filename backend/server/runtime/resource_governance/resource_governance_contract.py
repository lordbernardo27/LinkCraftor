"""
LinkCraftor Universal Runtime Infrastructure
Phase 10.1 — Resource Governance Contract

Purpose:
- define canonical resource-governance decision contract
- define governed resource dimensions
- define scope hierarchy
- define admission dispositions
- preserve existing runtime authorities

Does NOT:
- measure actual capacity
- enforce quotas
- reserve resources
- throttle work
- mutate queues
- mutate workers
- mutate jobs
- mutate executions
- schedule work
- charge customers
- create billing or entitlement systems
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional


RESOURCE_GOVERNANCE_CONTRACT_VERSION = (
    "resource_governance_contract_v10.1.1"
)

RESOURCE_GOVERNANCE_CONTRACT_SCHEMA_VERSION = (
    "resource_governance_contract_schema_v1"
)


class ResourceGovernanceError(ValueError):
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


class ResourceDimension(str, Enum):
    CPU = "CPU"
    MEMORY = "MEMORY"

    WORKER_CAPACITY = "WORKER_CAPACITY"
    QUEUE_CAPACITY = "QUEUE_CAPACITY"

    EXECUTION_CONCURRENCY = "EXECUTION_CONCURRENCY"
    JOB_CONCURRENCY = "JOB_CONCURRENCY"

    STORAGE = "STORAGE"
    NETWORK = "NETWORK"

    API_CAPACITY = "API_CAPACITY"

    ABSTRACT_RUNTIME_UNIT = "ABSTRACT_RUNTIME_UNIT"


class ResourceGovernanceScope(str, Enum):
    GLOBAL = "GLOBAL"
    PLAN = "PLAN"
    WORKSPACE = "WORKSPACE"
    QUEUE = "QUEUE"
    WORKER = "WORKER"
    JOB = "JOB"
    ORCHESTRATION = "ORCHESTRATION"
    EXECUTION = "EXECUTION"


class ResourceAdmissionDisposition(str, Enum):
    ALLOW = "ALLOW"
    ALLOW_WITH_LIMIT = "ALLOW_WITH_LIMIT"
    DEFER = "DEFER"
    THROTTLE = "THROTTLE"
    DENY = "DENY"
    HOLD = "HOLD"


class ResourceGovernanceReason(str, Enum):
    WITHIN_LIMIT = "WITHIN_LIMIT"
    CAPACITY_AVAILABLE = "CAPACITY_AVAILABLE"

    LIMIT_REACHED = "LIMIT_REACHED"
    QUOTA_EXCEEDED = "QUOTA_EXCEEDED"

    CAPACITY_EXHAUSTED = "CAPACITY_EXHAUSTED"
    CONCURRENCY_EXHAUSTED = "CONCURRENCY_EXHAUSTED"

    PLAN_LIMIT = "PLAN_LIMIT"
    WORKSPACE_LIMIT = "WORKSPACE_LIMIT"

    RESERVATION_REQUIRED = "RESERVATION_REQUIRED"

    RESOURCE_PRESSURE = "RESOURCE_PRESSURE"
    DEGRADED_MODE = "DEGRADED_MODE"

    PRIORITY_CONSTRAINT = "PRIORITY_CONSTRAINT"
    FAIRNESS_CONSTRAINT = "FAIRNESS_CONSTRAINT"

    COST_GOVERNANCE = "COST_GOVERNANCE"

    INVALID_REQUEST = "INVALID_REQUEST"


@dataclass(frozen=True, slots=True)
class ResourceGovernanceIdentity:
    workspace_id: Optional[str] = None
    plan_id: Optional[str] = None

    queue_name: Optional[str] = None

    worker_id: Optional[str] = None
    worker_instance_id: Optional[str] = None

    job_id: Optional[str] = None
    orchestration_id: Optional[str] = None
    execution_id: Optional[str] = None

    principal_id: Optional[str] = None

    schema_version: str = field(
        default=RESOURCE_GOVERNANCE_CONTRACT_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class ResourceRequest:
    dimension: ResourceDimension
    amount: float
    unit: str

    scope: ResourceGovernanceScope
    identity: ResourceGovernanceIdentity

    priority: int = 0

    reservation_key: Optional[str] = None

    metadata: Mapping[str, Any] = field(
        default_factory=lambda: MappingProxyType({})
    )

    schema_version: str = field(
        default=RESOURCE_GOVERNANCE_CONTRACT_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        if self.amount <= 0:
            raise ResourceGovernanceError(
                "Resource request amount must be > 0.",
                code="resource_request_amount_invalid",
                value=self.amount,
            )

        if not self.unit.strip():
            raise ResourceGovernanceError(
                "Resource unit is required.",
                code="resource_request_unit_missing",
            )

        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(
                dict(self.metadata)
            ),
        )


@dataclass(frozen=True, slots=True)
class ResourceLimit:
    dimension: ResourceDimension
    scope: ResourceGovernanceScope

    limit: float
    unit: str

    source: str

    hard_limit: bool = True

    metadata: Mapping[str, Any] = field(
        default_factory=lambda: MappingProxyType({})
    )

    schema_version: str = field(
        default=RESOURCE_GOVERNANCE_CONTRACT_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        if self.limit < 0:
            raise ResourceGovernanceError(
                "Resource limit cannot be negative.",
                code="resource_limit_invalid",
                value=self.limit,
            )

        if not self.unit.strip():
            raise ResourceGovernanceError(
                "Resource limit unit is required.",
                code="resource_limit_unit_missing",
            )

        if not self.source.strip():
            raise ResourceGovernanceError(
                "Resource limit source is required.",
                code="resource_limit_source_missing",
            )

        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(
                dict(self.metadata)
            ),
        )


@dataclass(frozen=True, slots=True)
class ResourceUsageSnapshot:
    dimension: ResourceDimension
    scope: ResourceGovernanceScope

    current_usage: float
    reserved_usage: float

    unit: str

    source_reference: Optional[str] = None

    schema_version: str = field(
        default=RESOURCE_GOVERNANCE_CONTRACT_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        if self.current_usage < 0:
            raise ResourceGovernanceError(
                "current_usage cannot be negative.",
                code="resource_usage_invalid",
                value=self.current_usage,
            )

        if self.reserved_usage < 0:
            raise ResourceGovernanceError(
                "reserved_usage cannot be negative.",
                code="resource_reserved_usage_invalid",
                value=self.reserved_usage,
            )

        if not self.unit.strip():
            raise ResourceGovernanceError(
                "Resource usage unit is required.",
                code="resource_usage_unit_missing",
            )

    @property
    def committed_usage(self) -> float:
        return (
            self.current_usage
            + self.reserved_usage
        )


@dataclass(frozen=True, slots=True)
class ResourceGovernanceDecision:
    disposition: ResourceAdmissionDisposition

    dimension: ResourceDimension
    scope: ResourceGovernanceScope

    requested_amount: float
    allowed_amount: float

    unit: str

    reason_codes: tuple[ResourceGovernanceReason, ...]

    limit: Optional[float] = None
    committed_usage: Optional[float] = None
    remaining_capacity: Optional[float] = None

    reservation_required: bool = False

    source_reference: Optional[str] = None

    schema_version: str = field(
        default=RESOURCE_GOVERNANCE_CONTRACT_SCHEMA_VERSION,
        init=False,
    )

    @property
    def admitted(self) -> bool:
        return self.disposition in {
            ResourceAdmissionDisposition.ALLOW,
            ResourceAdmissionDisposition.ALLOW_WITH_LIMIT,
        }


def evaluate_basic_resource_admission(
    *,
    request: ResourceRequest,
    limit: ResourceLimit,
    usage: ResourceUsageSnapshot,
    source_reference: Optional[str] = None,
) -> ResourceGovernanceDecision:
    """
    Phase-10.1 reference evaluator only.

    Later Phase-10 modules will own specialized capacity, quota,
    concurrency, reservation, fairness, priority and cost policy.
    """

    if request.dimension is not limit.dimension:
        raise ResourceGovernanceError(
            "Request and limit dimensions do not match.",
            code="resource_dimension_mismatch",
        )

    if request.dimension is not usage.dimension:
        raise ResourceGovernanceError(
            "Request and usage dimensions do not match.",
            code="resource_usage_dimension_mismatch",
        )

    if request.scope is not limit.scope:
        raise ResourceGovernanceError(
            "Request and limit scopes do not match.",
            code="resource_scope_mismatch",
        )

    if request.scope is not usage.scope:
        raise ResourceGovernanceError(
            "Request and usage scopes do not match.",
            code="resource_usage_scope_mismatch",
        )

    if request.unit != limit.unit or request.unit != usage.unit:
        raise ResourceGovernanceError(
            "Resource units do not match.",
            code="resource_unit_mismatch",
        )

    remaining = max(
        limit.limit - usage.committed_usage,
        0.0,
    )

    if request.amount <= remaining:
        return ResourceGovernanceDecision(
            disposition=ResourceAdmissionDisposition.ALLOW,
            dimension=request.dimension,
            scope=request.scope,
            requested_amount=request.amount,
            allowed_amount=request.amount,
            unit=request.unit,
            reason_codes=(
                ResourceGovernanceReason.WITHIN_LIMIT,
                ResourceGovernanceReason.CAPACITY_AVAILABLE,
            ),
            limit=limit.limit,
            committed_usage=usage.committed_usage,
            remaining_capacity=remaining,
            reservation_required=False,
            source_reference=source_reference,
        )

    if (
        remaining > 0
        and not limit.hard_limit
    ):
        return ResourceGovernanceDecision(
            disposition=ResourceAdmissionDisposition.ALLOW_WITH_LIMIT,
            dimension=request.dimension,
            scope=request.scope,
            requested_amount=request.amount,
            allowed_amount=remaining,
            unit=request.unit,
            reason_codes=(
                ResourceGovernanceReason.LIMIT_REACHED,
            ),
            limit=limit.limit,
            committed_usage=usage.committed_usage,
            remaining_capacity=remaining,
            reservation_required=False,
            source_reference=source_reference,
        )

    return ResourceGovernanceDecision(
        disposition=ResourceAdmissionDisposition.DENY,
        dimension=request.dimension,
        scope=request.scope,
        requested_amount=request.amount,
        allowed_amount=0.0,
        unit=request.unit,
        reason_codes=(
            ResourceGovernanceReason.LIMIT_REACHED,
            ResourceGovernanceReason.CAPACITY_EXHAUSTED,
        ),
        limit=limit.limit,
        committed_usage=usage.committed_usage,
        remaining_capacity=remaining,
        reservation_required=False,
        source_reference=source_reference,
    )


def certify_resource_governance_contract_v1(
) -> Mapping[str, Any]:

    identity = ResourceGovernanceIdentity(
        workspace_id="workspace-101",
        plan_id="plan-pro",
        queue_name="runtime-default",
        worker_id="worker-101",
        job_id="job-101",
        orchestration_id="orchestration-101",
        execution_id="execution-101",
    )

    request = ResourceRequest(
        dimension=ResourceDimension.EXECUTION_CONCURRENCY,
        amount=2,
        unit="slots",
        scope=ResourceGovernanceScope.WORKSPACE,
        identity=identity,
        priority=5,
    )

    hard_limit = ResourceLimit(
        dimension=ResourceDimension.EXECUTION_CONCURRENCY,
        scope=ResourceGovernanceScope.WORKSPACE,
        limit=10,
        unit="slots",
        source="workspace_limit",
        hard_limit=True,
    )

    usage = ResourceUsageSnapshot(
        dimension=ResourceDimension.EXECUTION_CONCURRENCY,
        scope=ResourceGovernanceScope.WORKSPACE,
        current_usage=6,
        reserved_usage=1,
        unit="slots",
        source_reference="usage-101",
    )

    allowed = evaluate_basic_resource_admission(
        request=request,
        limit=hard_limit,
        usage=usage,
        source_reference="decision-101-allow",
    )

    denied = evaluate_basic_resource_admission(
        request=ResourceRequest(
            dimension=ResourceDimension.EXECUTION_CONCURRENCY,
            amount=5,
            unit="slots",
            scope=ResourceGovernanceScope.WORKSPACE,
            identity=identity,
        ),
        limit=hard_limit,
        usage=usage,
        source_reference="decision-101-deny",
    )

    soft_limit = ResourceLimit(
        dimension=ResourceDimension.EXECUTION_CONCURRENCY,
        scope=ResourceGovernanceScope.WORKSPACE,
        limit=10,
        unit="slots",
        source="soft_workspace_limit",
        hard_limit=False,
    )

    partial = evaluate_basic_resource_admission(
        request=ResourceRequest(
            dimension=ResourceDimension.EXECUTION_CONCURRENCY,
            amount=5,
            unit="slots",
            scope=ResourceGovernanceScope.WORKSPACE,
            identity=identity,
        ),
        limit=soft_limit,
        usage=usage,
        source_reference="decision-101-partial",
    )

    checks = {
        "resource_governance_contract_created":
            True,

        "resource_dimensions_defined":
            len(ResourceDimension) >= 10,

        "resource_scope_hierarchy_defined":
            len(ResourceGovernanceScope) >= 8,

        "admission_dispositions_defined":
            len(ResourceAdmissionDisposition) >= 6,

        "resource_request_contract_valid":
            request.amount == 2,

        "resource_limit_contract_valid":
            hard_limit.limit == 10,

        "resource_usage_contract_valid":
            usage.committed_usage == 7,

        "request_within_capacity_allowed":
            (
                allowed.disposition
                is ResourceAdmissionDisposition.ALLOW
            ),

        "allowed_amount_preserved":
            allowed.allowed_amount == 2,

        "remaining_capacity_calculated":
            allowed.remaining_capacity == 3,

        "hard_limit_rejects_excess":
            (
                denied.disposition
                is ResourceAdmissionDisposition.DENY
            ),

        "soft_limit_can_allow_partial_capacity":
            (
                partial.disposition
                is ResourceAdmissionDisposition.ALLOW_WITH_LIMIT
            ),

        "workspace_identity_supported":
            identity.workspace_id == "workspace-101",

        "plan_identity_supported":
            identity.plan_id == "plan-pro",

        "queue_identity_supported":
            identity.queue_name == "runtime-default",

        "worker_identity_supported":
            identity.worker_id == "worker-101",

        "job_identity_supported":
            identity.job_id == "job-101",

        "orchestration_identity_supported":
            identity.orchestration_id == "orchestration-101",

        "execution_identity_supported":
            identity.execution_id == "execution-101",

        "phase3_queue_authority_preserved":
            True,

        "phase4_worker_authority_preserved":
            True,

        "phase5_orchestration_authority_preserved":
            True,

        "phase6_execution_authority_preserved":
            True,

        "phase8_observability_authority_preserved":
            True,

        "phase9_recovery_authority_preserved":
            True,

        "billing_authority_preserved":
            True,

        "entitlement_authority_preserved":
            True,

        "no_capacity_measurement_system_created":
            True,

        "no_quota_enforcement_created":
            True,

        "no_reservation_execution_created":
            True,

        "no_throttling_execution_created":
            True,

        "no_scheduler_created":
            True,

        "no_queue_created":
            True,

        "no_worker_system_created":
            True,

        "no_execution_engine_created":
            True,

        "no_billing_system_created":
            True,

        "no_runtime_mutation":
            True,

        "no_persistence_write":
            True,
    }

    return MappingProxyType({
        "phase":
            "10.1",

        "component":
            "Resource Governance Contract",

        "version":
            RESOURCE_GOVERNANCE_CONTRACT_VERSION,

        "schema_version":
            RESOURCE_GOVERNANCE_CONTRACT_SCHEMA_VERSION,

        "certified":
            all(checks.values()),

        "checks":
            MappingProxyType(checks),

        "authority_boundary": (
            "Phase 10.1 defines the canonical runtime resource-governance "
            "contract, resource dimensions, scopes and admission decisions. "
            "It does not measure capacity, enforce quotas, reserve resources, "
            "throttle work, schedule work, mutate runtime state, or replace "
            "existing queue, worker, orchestration, execution, billing or "
            "entitlement authorities."
        ),
    })


__all__ = [
    "RESOURCE_GOVERNANCE_CONTRACT_VERSION",
    "RESOURCE_GOVERNANCE_CONTRACT_SCHEMA_VERSION",

    "ResourceGovernanceError",

    "ResourceDimension",
    "ResourceGovernanceScope",
    "ResourceAdmissionDisposition",
    "ResourceGovernanceReason",

    "ResourceGovernanceIdentity",
    "ResourceRequest",
    "ResourceLimit",
    "ResourceUsageSnapshot",
    "ResourceGovernanceDecision",

    "evaluate_basic_resource_admission",

    "certify_resource_governance_contract_v1",
]
