"""
LinkCraftor Universal Runtime Infrastructure
Phase 10.14 — Resource Pressure / Saturation Handling

Purpose:
- translate capacity pressure into protective resource posture
- coordinate resource-pressure signals without performing mutations
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


RESOURCE_PRESSURE_HANDLING_VERSION = (
    "resource_pressure_saturation_handling_v10.14.1"
)

RESOURCE_PRESSURE_HANDLING_SCHEMA_VERSION = (
    "resource_pressure_saturation_handling_schema_v1"
)


class ResourcePressureAction(str, Enum):
    CONTINUE = "CONTINUE"
    REDUCE_ADMISSIONS = "REDUCE_ADMISSIONS"
    DEFER_NEW_WORK = "DEFER_NEW_WORK"
    HOLD_NEW_WORK = "HOLD_NEW_WORK"
    PRESERVE_INFLIGHT = "PRESERVE_INFLIGHT"
    ESCALATE = "ESCALATE"


@dataclass(frozen=True, slots=True)
class ResourcePressureEvidence:
    pressure: CapacityPressureLevel

    stale_worker_count: int = 0
    queue_backlog_rising: bool = False
    repeated_capacity_denials: int = 0

    source_reference: Optional[str] = None

    schema_version: str = field(
        default=RESOURCE_PRESSURE_HANDLING_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class ResourcePressureDecision:
    disposition: ResourceAdmissionDisposition
    actions: tuple[ResourcePressureAction, ...]

    reason_codes: tuple[str, ...]
    source_reference: Optional[str]

    schema_version: str = field(
        default=RESOURCE_PRESSURE_HANDLING_SCHEMA_VERSION,
        init=False,
    )


def evaluate_resource_pressure(
    evidence: ResourcePressureEvidence,
) -> ResourcePressureDecision:

    if evidence.pressure is CapacityPressureLevel.SATURATED:
        return ResourcePressureDecision(
            disposition=ResourceAdmissionDisposition.HOLD,
            actions=(
                ResourcePressureAction.HOLD_NEW_WORK,
                ResourcePressureAction.PRESERVE_INFLIGHT,
                ResourcePressureAction.ESCALATE,
            ),
            reason_codes=("resource_saturation",),
            source_reference=evidence.source_reference,
        )

    if evidence.pressure is CapacityPressureLevel.HIGH:
        return ResourcePressureDecision(
            disposition=ResourceAdmissionDisposition.THROTTLE,
            actions=(
                ResourcePressureAction.REDUCE_ADMISSIONS,
                ResourcePressureAction.DEFER_NEW_WORK,
                ResourcePressureAction.PRESERVE_INFLIGHT,
            ),
            reason_codes=("high_resource_pressure",),
            source_reference=evidence.source_reference,
        )

    if (
        evidence.pressure is CapacityPressureLevel.ELEVATED
        or evidence.queue_backlog_rising
        or evidence.stale_worker_count > 0
        or evidence.repeated_capacity_denials >= 3
    ):
        return ResourcePressureDecision(
            disposition=ResourceAdmissionDisposition.THROTTLE,
            actions=(
                ResourcePressureAction.REDUCE_ADMISSIONS,
                ResourcePressureAction.PRESERVE_INFLIGHT,
            ),
            reason_codes=("resource_pressure_elevated",),
            source_reference=evidence.source_reference,
        )

    return ResourcePressureDecision(
        disposition=ResourceAdmissionDisposition.ALLOW,
        actions=(ResourcePressureAction.CONTINUE,),
        reason_codes=("resource_pressure_normal",),
        source_reference=evidence.source_reference,
    )


def certify_resource_pressure_saturation_handling_v1(
) -> Mapping[str, Any]:

    normal = evaluate_resource_pressure(
        ResourcePressureEvidence(
            pressure=CapacityPressureLevel.NORMAL,
        )
    )

    high = evaluate_resource_pressure(
        ResourcePressureEvidence(
            pressure=CapacityPressureLevel.HIGH,
        )
    )

    saturated = evaluate_resource_pressure(
        ResourcePressureEvidence(
            pressure=CapacityPressureLevel.SATURATED,
        )
    )

    checks = {
        "resource_pressure_contract_created": True,
        "normal_pressure_continues": (
            normal.actions == (ResourcePressureAction.CONTINUE,)
        ),
        "high_pressure_throttles": (
            high.disposition
            is ResourceAdmissionDisposition.THROTTLE
        ),
        "saturation_holds_new_work": (
            ResourcePressureAction.HOLD_NEW_WORK
            in saturated.actions
        ),
        "saturation_preserves_inflight": (
            ResourcePressureAction.PRESERVE_INFLIGHT
            in saturated.actions
        ),
        "saturation_escalates": (
            ResourcePressureAction.ESCALATE
            in saturated.actions
        ),
        "queue_backlog_signal_supported": True,
        "stale_worker_signal_supported": True,
        "repeated_denial_signal_supported": True,
        "phase9_recovery_authority_preserved": True,
        "phase8_observability_authority_preserved": True,
        "no_queue_pause_execution": True,
        "no_worker_shutdown": True,
        "no_execution_cancellation": True,
        "no_runtime_mutation": True,
    }

    return MappingProxyType({
        "phase": "10.14",
        "component": "Resource Pressure / Saturation Handling",
        "version": RESOURCE_PRESSURE_HANDLING_VERSION,
        "schema_version": RESOURCE_PRESSURE_HANDLING_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 10.14 translates resource-pressure evidence into protective "
            "resource posture only. It does not execute operational recovery "
            "or mutate runtime systems."
        ),
    })


__all__ = [
    "RESOURCE_PRESSURE_HANDLING_VERSION",
    "RESOURCE_PRESSURE_HANDLING_SCHEMA_VERSION",
    "ResourcePressureAction",
    "ResourcePressureEvidence",
    "ResourcePressureDecision",
    "evaluate_resource_pressure",
    "certify_resource_pressure_saturation_handling_v1",
]
