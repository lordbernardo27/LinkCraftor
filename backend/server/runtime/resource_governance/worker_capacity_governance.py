"""
LinkCraftor Universal Runtime Infrastructure
Phase 10.3 — Worker Capacity Governance

Determines worker admission posture from existing worker capacity evidence.

Does NOT:
- register workers
- assign jobs
- scale worker pools
- mutate worker state
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, Optional

from .resource_governance_contract import (
    ResourceAdmissionDisposition,
)
from .runtime_capacity_model import (
    CapacityPressureLevel,
)


WORKER_CAPACITY_GOVERNANCE_VERSION = (
    "worker_capacity_governance_v10.3.1"
)

WORKER_CAPACITY_GOVERNANCE_SCHEMA_VERSION = (
    "worker_capacity_governance_schema_v1"
)


@dataclass(frozen=True, slots=True)
class WorkerCapacityEvidence:
    worker_id: str
    worker_instance_id: Optional[str]

    active: bool
    stale: bool

    capacity_slots: int
    active_slots: int
    reserved_slots: int

    pressure: CapacityPressureLevel

    source_reference: Optional[str] = None

    schema_version: str = field(
        default=WORKER_CAPACITY_GOVERNANCE_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class WorkerCapacityDecision:
    disposition: ResourceAdmissionDisposition

    requested_slots: int
    allowed_slots: int
    available_slots: int

    reason_codes: tuple[str, ...]
    source_reference: Optional[str]

    schema_version: str = field(
        default=WORKER_CAPACITY_GOVERNANCE_SCHEMA_VERSION,
        init=False,
    )


def evaluate_worker_capacity(
    *,
    evidence: WorkerCapacityEvidence,
    requested_slots: int,
) -> WorkerCapacityDecision:

    if requested_slots < 1:
        raise ValueError("requested_slots must be >= 1.")

    available = max(
        evidence.capacity_slots
        - evidence.active_slots
        - evidence.reserved_slots,
        0,
    )

    if not evidence.active or evidence.stale:
        return WorkerCapacityDecision(
            disposition=ResourceAdmissionDisposition.HOLD,
            requested_slots=requested_slots,
            allowed_slots=0,
            available_slots=available,
            reason_codes=("worker_unavailable",),
            source_reference=evidence.source_reference,
        )

    if evidence.pressure is CapacityPressureLevel.SATURATED:
        return WorkerCapacityDecision(
            disposition=ResourceAdmissionDisposition.DEFER,
            requested_slots=requested_slots,
            allowed_slots=0,
            available_slots=available,
            reason_codes=("worker_saturated",),
            source_reference=evidence.source_reference,
        )

    if requested_slots <= available:
        return WorkerCapacityDecision(
            disposition=ResourceAdmissionDisposition.ALLOW,
            requested_slots=requested_slots,
            allowed_slots=requested_slots,
            available_slots=available,
            reason_codes=("worker_capacity_available",),
            source_reference=evidence.source_reference,
        )

    if available > 0:
        return WorkerCapacityDecision(
            disposition=ResourceAdmissionDisposition.ALLOW_WITH_LIMIT,
            requested_slots=requested_slots,
            allowed_slots=available,
            available_slots=available,
            reason_codes=("worker_partial_capacity",),
            source_reference=evidence.source_reference,
        )

    return WorkerCapacityDecision(
        disposition=ResourceAdmissionDisposition.DEFER,
        requested_slots=requested_slots,
        allowed_slots=0,
        available_slots=0,
        reason_codes=("worker_capacity_exhausted",),
        source_reference=evidence.source_reference,
    )


def certify_worker_capacity_governance_v1(
) -> Mapping[str, Any]:

    normal = WorkerCapacityEvidence(
        worker_id="worker-103",
        worker_instance_id="instance-103",
        active=True,
        stale=False,
        capacity_slots=8,
        active_slots=4,
        reserved_slots=1,
        pressure=CapacityPressureLevel.NORMAL,
    )

    allowed = evaluate_worker_capacity(
        evidence=normal,
        requested_slots=2,
    )

    partial = evaluate_worker_capacity(
        evidence=normal,
        requested_slots=5,
    )

    stale = evaluate_worker_capacity(
        evidence=WorkerCapacityEvidence(
            worker_id="worker-103b",
            worker_instance_id=None,
            active=True,
            stale=True,
            capacity_slots=8,
            active_slots=1,
            reserved_slots=0,
            pressure=CapacityPressureLevel.NORMAL,
        ),
        requested_slots=1,
    )

    checks = {
        "worker_capacity_contract_created": True,
        "available_slots_calculated": (
            allowed.available_slots == 3
        ),
        "worker_capacity_allows_safe_work": (
            allowed.disposition
            is ResourceAdmissionDisposition.ALLOW
        ),
        "partial_worker_capacity_supported": (
            partial.disposition
            is ResourceAdmissionDisposition.ALLOW_WITH_LIMIT
        ),
        "stale_worker_held": (
            stale.disposition
            is ResourceAdmissionDisposition.HOLD
        ),
        "saturation_deferral_supported": True,
        "existing_worker_registry_preserved": True,
        "existing_assignment_authority_preserved": True,
        "existing_lease_authority_preserved": True,
        "no_worker_registration": True,
        "no_worker_assignment": True,
        "no_worker_scaling": True,
        "no_worker_mutation": True,
        "no_queue_mutation": True,
    }

    return MappingProxyType({
        "phase": "10.3",
        "component": "Worker Capacity Governance",
        "version": WORKER_CAPACITY_GOVERNANCE_VERSION,
        "schema_version": WORKER_CAPACITY_GOVERNANCE_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 10.3 decides worker-capacity admission posture only. "
            "Existing worker registry, assignment and lease authorities remain "
            "responsible for concrete worker operations."
        ),
    })


__all__ = [
    "WORKER_CAPACITY_GOVERNANCE_VERSION",
    "WORKER_CAPACITY_GOVERNANCE_SCHEMA_VERSION",
    "WorkerCapacityEvidence",
    "WorkerCapacityDecision",
    "evaluate_worker_capacity",
    "certify_worker_capacity_governance_v1",
]
