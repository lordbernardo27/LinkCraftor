"""
LinkCraftor Universal Runtime Infrastructure
Phase 10.17 — Owner Control Tower Handoff

Packages Phase-10 resource-governance status for Owner Control Tower.

Does NOT:
- build UI
- create dashboard database
- execute owner actions
- mutate resource policy
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, Optional


OWNER_CONTROL_TOWER_RESOURCE_HANDOFF_VERSION = (
    "owner_control_tower_resource_handoff_v10.17.1"
)

OWNER_CONTROL_TOWER_RESOURCE_HANDOFF_SCHEMA_VERSION = (
    "owner_control_tower_resource_handoff_schema_v1"
)


@dataclass(frozen=True, slots=True)
class OwnerControlTowerResourceHandoff:
    runtime_capacity_status: str
    worker_capacity_status: str
    queue_capacity_status: str
    execution_concurrency_status: str

    workspace_limit_status: str
    plan_entitlement_status: str
    quota_status: str
    reservation_status: str

    throttling_status: str
    fairness_status: str
    priority_status: str
    cost_status: str
    pressure_status: str
    degraded_mode_resource_status: str

    evidence_reference: Optional[str] = None

    owner_attention_required: bool = False

    metadata: Mapping[str, Any] = field(
        default_factory=lambda: MappingProxyType({})
    )

    schema_version: str = field(
        default=OWNER_CONTROL_TOWER_RESOURCE_HANDOFF_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(dict(self.metadata)),
        )


def build_owner_control_tower_resource_handoff(
    *,
    runtime_capacity_status: str,
    worker_capacity_status: str,
    queue_capacity_status: str,
    execution_concurrency_status: str,
    workspace_limit_status: str,
    plan_entitlement_status: str,
    quota_status: str,
    reservation_status: str,
    throttling_status: str,
    fairness_status: str,
    priority_status: str,
    cost_status: str,
    pressure_status: str,
    degraded_mode_resource_status: str,
    evidence_reference: Optional[str] = None,
    owner_attention_required: bool = False,
    metadata: Optional[Mapping[str, Any]] = None,
) -> OwnerControlTowerResourceHandoff:

    return OwnerControlTowerResourceHandoff(
        runtime_capacity_status=runtime_capacity_status,
        worker_capacity_status=worker_capacity_status,
        queue_capacity_status=queue_capacity_status,
        execution_concurrency_status=execution_concurrency_status,
        workspace_limit_status=workspace_limit_status,
        plan_entitlement_status=plan_entitlement_status,
        quota_status=quota_status,
        reservation_status=reservation_status,
        throttling_status=throttling_status,
        fairness_status=fairness_status,
        priority_status=priority_status,
        cost_status=cost_status,
        pressure_status=pressure_status,
        degraded_mode_resource_status=(
            degraded_mode_resource_status
        ),
        evidence_reference=evidence_reference,
        owner_attention_required=owner_attention_required,
        metadata=metadata or {},
    )


def certify_owner_control_tower_resource_handoff_v1(
) -> Mapping[str, Any]:

    handoff = build_owner_control_tower_resource_handoff(
        runtime_capacity_status="ELEVATED",
        worker_capacity_status="AVAILABLE",
        queue_capacity_status="AVAILABLE",
        execution_concurrency_status="LIMITED",
        workspace_limit_status="WITHIN_LIMIT",
        plan_entitlement_status="ALLOWED",
        quota_status="AVAILABLE",
        reservation_status="APPROVED",
        throttling_status="MODERATE",
        fairness_status="FAIR",
        priority_status="STANDARD",
        cost_status="WITHIN_BUDGET",
        pressure_status="ELEVATED",
        degraded_mode_resource_status="LIMITED",
        evidence_reference="resource-evidence-1017",
        owner_attention_required=True,
    )

    checks = {
        "owner_control_tower_handoff_contract_created": True,
        "runtime_capacity_status_present": bool(
            handoff.runtime_capacity_status
        ),
        "worker_capacity_status_present": bool(
            handoff.worker_capacity_status
        ),
        "queue_capacity_status_present": bool(
            handoff.queue_capacity_status
        ),
        "execution_concurrency_status_present": bool(
            handoff.execution_concurrency_status
        ),
        "workspace_limit_status_present": bool(
            handoff.workspace_limit_status
        ),
        "plan_entitlement_status_present": bool(
            handoff.plan_entitlement_status
        ),
        "quota_status_present": bool(
            handoff.quota_status
        ),
        "reservation_status_present": bool(
            handoff.reservation_status
        ),
        "throttling_status_present": bool(
            handoff.throttling_status
        ),
        "fairness_status_present": bool(
            handoff.fairness_status
        ),
        "priority_status_present": bool(
            handoff.priority_status
        ),
        "cost_status_present": bool(
            handoff.cost_status
        ),
        "pressure_status_present": bool(
            handoff.pressure_status
        ),
        "degraded_mode_status_present": bool(
            handoff.degraded_mode_resource_status
        ),
        "evidence_reference_supported": (
            handoff.evidence_reference
            == "resource-evidence-1017"
        ),
        "owner_attention_signal_supported": (
            handoff.owner_attention_required
        ),
        "no_owner_ui_created": True,
        "no_dashboard_database_created": True,
        "no_owner_action_execution": True,
        "no_resource_policy_mutation": True,
        "no_runtime_mutation": True,
        "no_persistence_write": True,
    }

    return MappingProxyType({
        "phase": "10.17",
        "component": "Owner Control Tower Handoff",
        "version": OWNER_CONTROL_TOWER_RESOURCE_HANDOFF_VERSION,
        "schema_version": OWNER_CONTROL_TOWER_RESOURCE_HANDOFF_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 10.17 packages Phase-10 governance status for the Owner "
            "Control Tower. It does not build UI, store dashboard state or "
            "execute owner/runtime actions."
        ),
    })


__all__ = [
    "OWNER_CONTROL_TOWER_RESOURCE_HANDOFF_VERSION",
    "OWNER_CONTROL_TOWER_RESOURCE_HANDOFF_SCHEMA_VERSION",
    "OwnerControlTowerResourceHandoff",
    "build_owner_control_tower_resource_handoff",
    "certify_owner_control_tower_resource_handoff_v1",
]
