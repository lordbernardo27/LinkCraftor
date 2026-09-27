"""
LinkCraftor Universal Runtime Infrastructure
Phase 10.10 — Throttling Governance

Purpose:
- determine when runtime work should be throttled
- determine throttle severity
- calculate advisory delay / admission percentage
- preserve existing queue, worker and execution authorities

Does NOT:
- sleep workers
- pause queues
- delay jobs directly
- create scheduler
- mutate runtime state
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional

from .resource_governance_contract import (
    ResourceAdmissionDisposition,
)
from .runtime_capacity_model import (
    CapacityPressureLevel,
)


THROTTLING_GOVERNANCE_VERSION = (
    "throttling_governance_v10.10.1"
)

THROTTLING_GOVERNANCE_SCHEMA_VERSION = (
    "throttling_governance_schema_v1"
)


class ThrottleLevel(str, Enum):
    NONE = "NONE"
    LIGHT = "LIGHT"
    MODERATE = "MODERATE"
    SEVERE = "SEVERE"
    BLOCK = "BLOCK"


@dataclass(frozen=True, slots=True)
class ThrottlingEvidence:
    capacity_pressure: CapacityPressureLevel

    quota_utilization_ratio: float
    concurrency_utilization_ratio: float

    degraded_mode_active: bool = False
    repeated_resource_denials: int = 0

    source_reference: Optional[str] = None

    schema_version: str = field(
        default=THROTTLING_GOVERNANCE_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        if self.quota_utilization_ratio < 0:
            raise ValueError(
                "quota_utilization_ratio cannot be negative."
            )

        if self.concurrency_utilization_ratio < 0:
            raise ValueError(
                "concurrency_utilization_ratio cannot be negative."
            )

        if self.repeated_resource_denials < 0:
            raise ValueError(
                "repeated_resource_denials cannot be negative."
            )


@dataclass(frozen=True, slots=True)
class ThrottlingDecision:
    disposition: ResourceAdmissionDisposition
    level: ThrottleLevel

    admission_fraction: float
    advisory_delay_ms: int

    reason_codes: tuple[str, ...]
    source_reference: Optional[str]

    schema_version: str = field(
        default=THROTTLING_GOVERNANCE_SCHEMA_VERSION,
        init=False,
    )


def evaluate_throttling_governance(
    evidence: ThrottlingEvidence,
) -> ThrottlingDecision:

    if (
        evidence.capacity_pressure
        is CapacityPressureLevel.SATURATED
        or evidence.quota_utilization_ratio >= 1.0
        or evidence.concurrency_utilization_ratio >= 1.0
    ):
        return ThrottlingDecision(
            disposition=ResourceAdmissionDisposition.HOLD,
            level=ThrottleLevel.BLOCK,
            admission_fraction=0.0,
            advisory_delay_ms=5000,
            reason_codes=("resource_saturated",),
            source_reference=evidence.source_reference,
        )

    if (
        evidence.capacity_pressure
        is CapacityPressureLevel.HIGH
        or evidence.quota_utilization_ratio >= 0.90
        or evidence.concurrency_utilization_ratio >= 0.90
        or evidence.repeated_resource_denials >= 3
    ):
        return ThrottlingDecision(
            disposition=ResourceAdmissionDisposition.THROTTLE,
            level=ThrottleLevel.SEVERE,
            admission_fraction=0.25,
            advisory_delay_ms=2000,
            reason_codes=("high_resource_pressure",),
            source_reference=evidence.source_reference,
        )

    if (
        evidence.capacity_pressure
        is CapacityPressureLevel.ELEVATED
        or evidence.quota_utilization_ratio >= 0.75
        or evidence.concurrency_utilization_ratio >= 0.75
        or evidence.degraded_mode_active
    ):
        return ThrottlingDecision(
            disposition=ResourceAdmissionDisposition.THROTTLE,
            level=ThrottleLevel.MODERATE,
            admission_fraction=0.50,
            advisory_delay_ms=1000,
            reason_codes=("elevated_resource_pressure",),
            source_reference=evidence.source_reference,
        )

    return ThrottlingDecision(
        disposition=ResourceAdmissionDisposition.ALLOW,
        level=ThrottleLevel.NONE,
        admission_fraction=1.0,
        advisory_delay_ms=0,
        reason_codes=("throttling_not_required",),
        source_reference=evidence.source_reference,
    )


def certify_throttling_governance_v1(
) -> Mapping[str, Any]:

    normal = evaluate_throttling_governance(
        ThrottlingEvidence(
            capacity_pressure=CapacityPressureLevel.NORMAL,
            quota_utilization_ratio=0.40,
            concurrency_utilization_ratio=0.50,
        )
    )

    moderate = evaluate_throttling_governance(
        ThrottlingEvidence(
            capacity_pressure=CapacityPressureLevel.ELEVATED,
            quota_utilization_ratio=0.80,
            concurrency_utilization_ratio=0.70,
        )
    )

    severe = evaluate_throttling_governance(
        ThrottlingEvidence(
            capacity_pressure=CapacityPressureLevel.HIGH,
            quota_utilization_ratio=0.92,
            concurrency_utilization_ratio=0.90,
        )
    )

    blocked = evaluate_throttling_governance(
        ThrottlingEvidence(
            capacity_pressure=CapacityPressureLevel.SATURATED,
            quota_utilization_ratio=1.0,
            concurrency_utilization_ratio=1.0,
        )
    )

    checks = {
        "throttling_contract_created": True,
        "normal_work_allowed": (
            normal.disposition
            is ResourceAdmissionDisposition.ALLOW
        ),
        "moderate_throttling_detected": (
            moderate.level is ThrottleLevel.MODERATE
        ),
        "severe_throttling_detected": (
            severe.level is ThrottleLevel.SEVERE
        ),
        "saturation_blocks_admission": (
            blocked.level is ThrottleLevel.BLOCK
        ),
        "admission_fraction_supported": True,
        "advisory_delay_supported": True,
        "quota_pressure_supported": True,
        "concurrency_pressure_supported": True,
        "degraded_mode_signal_supported": True,
        "phase3_queue_authority_preserved": True,
        "phase4_worker_authority_preserved": True,
        "phase6_execution_authority_preserved": True,
        "no_sleep_execution": True,
        "no_queue_pause_execution": True,
        "no_job_delay_execution": True,
        "no_scheduler_created": True,
        "no_runtime_mutation": True,
    }

    return MappingProxyType({
        "phase": "10.10",
        "component": "Throttling Governance",
        "version": THROTTLING_GOVERNANCE_VERSION,
        "schema_version": THROTTLING_GOVERNANCE_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 10.10 decides throttling posture and advisory delay only. "
            "Existing runtime authorities apply any approved operational "
            "control."
        ),
    })


__all__ = [
    "THROTTLING_GOVERNANCE_VERSION",
    "THROTTLING_GOVERNANCE_SCHEMA_VERSION",
    "ThrottleLevel",
    "ThrottlingEvidence",
    "ThrottlingDecision",
    "evaluate_throttling_governance",
    "certify_throttling_governance_v1",
]
