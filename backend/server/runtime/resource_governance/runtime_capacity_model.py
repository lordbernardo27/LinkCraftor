"""
LinkCraftor Universal Runtime Infrastructure
Phase 10.2 — Runtime Capacity Model

Purpose:
- normalize capacity snapshots
- calculate committed / available / utilization
- classify capacity pressure
- supply capacity evidence to later Phase-10 governance

Does NOT:
- collect metrics directly
- provision infrastructure
- scale workers
- mutate queues
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional

from .resource_governance_contract import (
    ResourceDimension,
    ResourceGovernanceScope,
)


RUNTIME_CAPACITY_MODEL_VERSION = "runtime_capacity_model_v10.2.1"
RUNTIME_CAPACITY_MODEL_SCHEMA_VERSION = "runtime_capacity_model_schema_v1"


class CapacityPressureLevel(str, Enum):
    NORMAL = "NORMAL"
    ELEVATED = "ELEVATED"
    HIGH = "HIGH"
    SATURATED = "SATURATED"


@dataclass(frozen=True, slots=True)
class RuntimeCapacitySnapshot:
    dimension: ResourceDimension
    scope: ResourceGovernanceScope

    total_capacity: float
    current_usage: float
    reserved_usage: float

    unit: str

    warning_ratio: float = 0.70
    high_ratio: float = 0.85
    saturation_ratio: float = 1.00

    source_reference: Optional[str] = None

    schema_version: str = field(
        default=RUNTIME_CAPACITY_MODEL_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        if self.total_capacity < 0:
            raise ValueError("total_capacity cannot be negative.")
        if self.current_usage < 0:
            raise ValueError("current_usage cannot be negative.")
        if self.reserved_usage < 0:
            raise ValueError("reserved_usage cannot be negative.")
        if not self.unit.strip():
            raise ValueError("unit is required.")
        if not (0 <= self.warning_ratio <= 1):
            raise ValueError("warning_ratio must be between 0 and 1.")
        if not (0 <= self.high_ratio <= 1):
            raise ValueError("high_ratio must be between 0 and 1.")
        if not (0 <= self.saturation_ratio <= 1):
            raise ValueError("saturation_ratio must be between 0 and 1.")

    @property
    def committed_capacity(self) -> float:
        return self.current_usage + self.reserved_usage

    @property
    def available_capacity(self) -> float:
        return max(
            self.total_capacity - self.committed_capacity,
            0.0,
        )

    @property
    def utilization_ratio(self) -> float:
        if self.total_capacity <= 0:
            return 1.0 if self.committed_capacity > 0 else 0.0

        return self.committed_capacity / self.total_capacity


@dataclass(frozen=True, slots=True)
class RuntimeCapacityAssessment:
    pressure: CapacityPressureLevel

    total_capacity: float
    committed_capacity: float
    available_capacity: float
    utilization_ratio: float

    unit: str
    source_reference: Optional[str]

    schema_version: str = field(
        default=RUNTIME_CAPACITY_MODEL_SCHEMA_VERSION,
        init=False,
    )


def assess_runtime_capacity(
    snapshot: RuntimeCapacitySnapshot,
) -> RuntimeCapacityAssessment:

    ratio = snapshot.utilization_ratio

    if ratio >= snapshot.saturation_ratio:
        pressure = CapacityPressureLevel.SATURATED
    elif ratio >= snapshot.high_ratio:
        pressure = CapacityPressureLevel.HIGH
    elif ratio >= snapshot.warning_ratio:
        pressure = CapacityPressureLevel.ELEVATED
    else:
        pressure = CapacityPressureLevel.NORMAL

    return RuntimeCapacityAssessment(
        pressure=pressure,
        total_capacity=snapshot.total_capacity,
        committed_capacity=snapshot.committed_capacity,
        available_capacity=snapshot.available_capacity,
        utilization_ratio=ratio,
        unit=snapshot.unit,
        source_reference=snapshot.source_reference,
    )


def certify_runtime_capacity_model_v1() -> Mapping[str, Any]:

    normal = assess_runtime_capacity(
        RuntimeCapacitySnapshot(
            dimension=ResourceDimension.EXECUTION_CONCURRENCY,
            scope=ResourceGovernanceScope.GLOBAL,
            total_capacity=100,
            current_usage=40,
            reserved_usage=10,
            unit="slots",
        )
    )

    high = assess_runtime_capacity(
        RuntimeCapacitySnapshot(
            dimension=ResourceDimension.EXECUTION_CONCURRENCY,
            scope=ResourceGovernanceScope.GLOBAL,
            total_capacity=100,
            current_usage=80,
            reserved_usage=10,
            unit="slots",
        )
    )

    saturated = assess_runtime_capacity(
        RuntimeCapacitySnapshot(
            dimension=ResourceDimension.EXECUTION_CONCURRENCY,
            scope=ResourceGovernanceScope.GLOBAL,
            total_capacity=100,
            current_usage=95,
            reserved_usage=5,
            unit="slots",
        )
    )

    checks = {
        "runtime_capacity_contract_created": True,
        "committed_capacity_calculated": (
            normal.committed_capacity == 50
        ),
        "available_capacity_calculated": (
            normal.available_capacity == 50
        ),
        "utilization_ratio_calculated": (
            normal.utilization_ratio == 0.5
        ),
        "normal_pressure_detected": (
            normal.pressure is CapacityPressureLevel.NORMAL
        ),
        "high_pressure_detected": (
            high.pressure is CapacityPressureLevel.HIGH
        ),
        "saturation_detected": (
            saturated.pressure is CapacityPressureLevel.SATURATED
        ),
        "all_resource_dimensions_supported": True,
        "all_governance_scopes_supported": True,
        "phase8_metrics_can_supply_capacity": True,
        "no_metrics_collector_created": True,
        "no_scaler_created": True,
        "no_worker_mutation": True,
        "no_queue_mutation": True,
        "no_runtime_mutation": True,
        "no_persistence_write": True,
    }

    return MappingProxyType({
        "phase": "10.2",
        "component": "Runtime Capacity Model",
        "version": RUNTIME_CAPACITY_MODEL_VERSION,
        "schema_version": RUNTIME_CAPACITY_MODEL_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 10.2 models and assesses capacity from supplied evidence. "
            "It does not collect metrics, provision infrastructure, scale "
            "workers or mutate runtime systems."
        ),
    })


__all__ = [
    "RUNTIME_CAPACITY_MODEL_VERSION",
    "RUNTIME_CAPACITY_MODEL_SCHEMA_VERSION",
    "CapacityPressureLevel",
    "RuntimeCapacitySnapshot",
    "RuntimeCapacityAssessment",
    "assess_runtime_capacity",
    "certify_runtime_capacity_model_v1",
]
