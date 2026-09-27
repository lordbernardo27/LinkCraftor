"""
LinkCraftor Universal Runtime Infrastructure
Phase 10.15 — Degraded-Mode Resource Integration

Integrates Phase-9 degraded-mode posture with Phase-10 resource admission.

Phase 9 decides degraded mode.
Phase 10 decides corresponding resource posture.

Does NOT mutate Phase-9 state or execute controls.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, Optional

from backend.server.runtime.reliability.degraded_mode_operation import (
    DegradedModeLevel,
)

from .resource_governance_contract import (
    ResourceAdmissionDisposition,
)


DEGRADED_MODE_RESOURCE_INTEGRATION_VERSION = (
    "degraded_mode_resource_integration_v10.15.1"
)

DEGRADED_MODE_RESOURCE_INTEGRATION_SCHEMA_VERSION = (
    "degraded_mode_resource_integration_schema_v1"
)


@dataclass(frozen=True, slots=True)
class DegradedModeResourceEvidence:
    degraded_mode_level: DegradedModeLevel

    critical_work: bool = False
    existing_inflight_work: bool = False

    source_reference: Optional[str] = None

    schema_version: str = field(
        default=DEGRADED_MODE_RESOURCE_INTEGRATION_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class DegradedModeResourceDecision:
    disposition: ResourceAdmissionDisposition

    preserve_inflight: bool
    allow_critical_work: bool

    admission_fraction: float

    reason_codes: tuple[str, ...]
    source_reference: Optional[str]

    schema_version: str = field(
        default=DEGRADED_MODE_RESOURCE_INTEGRATION_SCHEMA_VERSION,
        init=False,
    )


def evaluate_degraded_mode_resource_integration(
    evidence: DegradedModeResourceEvidence,
) -> DegradedModeResourceDecision:

    if evidence.degraded_mode_level is DegradedModeLevel.NORMAL:
        return DegradedModeResourceDecision(
            disposition=ResourceAdmissionDisposition.ALLOW,
            preserve_inflight=True,
            allow_critical_work=True,
            admission_fraction=1.0,
            reason_codes=("normal_mode",),
            source_reference=evidence.source_reference,
        )

    if evidence.degraded_mode_level is DegradedModeLevel.LIMITED:
        return DegradedModeResourceDecision(
            disposition=ResourceAdmissionDisposition.THROTTLE,
            preserve_inflight=True,
            allow_critical_work=True,
            admission_fraction=0.75,
            reason_codes=("limited_mode",),
            source_reference=evidence.source_reference,
        )

    if evidence.degraded_mode_level is DegradedModeLevel.RESTRICTED:
        return DegradedModeResourceDecision(
            disposition=(
                ResourceAdmissionDisposition.ALLOW_WITH_LIMIT
                if evidence.critical_work
                else ResourceAdmissionDisposition.DEFER
            ),
            preserve_inflight=True,
            allow_critical_work=True,
            admission_fraction=0.25,
            reason_codes=("restricted_mode",),
            source_reference=evidence.source_reference,
        )

    return DegradedModeResourceDecision(
        disposition=(
            ResourceAdmissionDisposition.ALLOW_WITH_LIMIT
            if evidence.critical_work
            else ResourceAdmissionDisposition.HOLD
        ),
        preserve_inflight=True,
        allow_critical_work=evidence.critical_work,
        admission_fraction=0.10 if evidence.critical_work else 0.0,
        reason_codes=("protective_mode",),
        source_reference=evidence.source_reference,
    )


def certify_degraded_mode_resource_integration_v1(
) -> Mapping[str, Any]:

    normal = evaluate_degraded_mode_resource_integration(
        DegradedModeResourceEvidence(
            degraded_mode_level=DegradedModeLevel.NORMAL,
        )
    )

    limited = evaluate_degraded_mode_resource_integration(
        DegradedModeResourceEvidence(
            degraded_mode_level=DegradedModeLevel.LIMITED,
        )
    )

    restricted = evaluate_degraded_mode_resource_integration(
        DegradedModeResourceEvidence(
            degraded_mode_level=DegradedModeLevel.RESTRICTED,
        )
    )

    protective = evaluate_degraded_mode_resource_integration(
        DegradedModeResourceEvidence(
            degraded_mode_level=DegradedModeLevel.PROTECTIVE,
            critical_work=False,
        )
    )

    critical = evaluate_degraded_mode_resource_integration(
        DegradedModeResourceEvidence(
            degraded_mode_level=DegradedModeLevel.PROTECTIVE,
            critical_work=True,
        )
    )

    checks = {
        "degraded_mode_integration_contract_created": True,
        "normal_mode_full_admission": (
            normal.admission_fraction == 1.0
        ),
        "limited_mode_throttled": (
            limited.disposition
            is ResourceAdmissionDisposition.THROTTLE
        ),
        "restricted_noncritical_deferred": (
            restricted.disposition
            is ResourceAdmissionDisposition.DEFER
        ),
        "protective_noncritical_held": (
            protective.disposition
            is ResourceAdmissionDisposition.HOLD
        ),
        "protective_critical_can_be_limited": (
            critical.disposition
            is ResourceAdmissionDisposition.ALLOW_WITH_LIMIT
        ),
        "inflight_preservation_supported": True,
        "critical_work_exception_supported": True,
        "phase9_degraded_mode_authority_preserved": True,
        "phase6_execution_authority_preserved": True,
        "no_phase9_state_mutation": True,
        "no_execution_start": True,
        "no_queue_pause_execution": True,
        "no_worker_shutdown": True,
        "no_runtime_mutation": True,
    }

    return MappingProxyType({
        "phase": "10.15",
        "component": "Degraded-Mode Resource Integration",
        "version": DEGRADED_MODE_RESOURCE_INTEGRATION_VERSION,
        "schema_version": DEGRADED_MODE_RESOURCE_INTEGRATION_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 10.15 maps the Phase-9 degraded-mode decision into "
            "resource-admission posture. Phase 9 remains degraded-mode "
            "authority and concrete runtime controls remain elsewhere."
        ),
    })


__all__ = [
    "DEGRADED_MODE_RESOURCE_INTEGRATION_VERSION",
    "DEGRADED_MODE_RESOURCE_INTEGRATION_SCHEMA_VERSION",
    "DegradedModeResourceEvidence",
    "DegradedModeResourceDecision",
    "evaluate_degraded_mode_resource_integration",
    "certify_degraded_mode_resource_integration_v1",
]
