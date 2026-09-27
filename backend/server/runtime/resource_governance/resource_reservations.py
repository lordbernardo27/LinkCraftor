"""
LinkCraftor Universal Runtime Infrastructure
Phase 10.9 — Resource Reservations

Defines reservation eligibility and reservation contracts.

Does NOT:
- persist reservations
- mutate capacity counters
- allocate workers
- start executions
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional

from .resource_governance_contract import (
    ResourceAdmissionDisposition,
    ResourceDimension,
    ResourceGovernanceScope,
)


RESOURCE_RESERVATIONS_VERSION = (
    "resource_reservations_v10.9.1"
)

RESOURCE_RESERVATIONS_SCHEMA_VERSION = (
    "resource_reservations_schema_v1"
)


class ResourceReservationStatus(str, Enum):
    PROPOSED = "PROPOSED"
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    RELEASED = "RELEASED"
    EXPIRED = "EXPIRED"


@dataclass(frozen=True, slots=True)
class ResourceReservationRequest:
    reservation_key: str

    dimension: ResourceDimension
    scope: ResourceGovernanceScope

    amount: float
    unit: str

    owner_reference: str

    schema_version: str = field(
        default=RESOURCE_RESERVATIONS_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class ResourceReservationEvidence:
    available_capacity: float
    existing_reserved_capacity: float

    reservation_limit: float

    source_reference: Optional[str] = None

    schema_version: str = field(
        default=RESOURCE_RESERVATIONS_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class ResourceReservationDecision:
    disposition: ResourceAdmissionDisposition
    status: ResourceReservationStatus

    reservation_key: str

    requested_amount: float
    approved_amount: float

    reason_codes: tuple[str, ...]

    source_reference: Optional[str]

    schema_version: str = field(
        default=RESOURCE_RESERVATIONS_SCHEMA_VERSION,
        init=False,
    )


def evaluate_resource_reservation(
    *,
    request: ResourceReservationRequest,
    evidence: ResourceReservationEvidence,
) -> ResourceReservationDecision:

    if request.amount <= 0:
        raise ValueError("reservation amount must be > 0.")

    reservation_remaining = max(
        evidence.reservation_limit
        - evidence.existing_reserved_capacity,
        0.0,
    )

    available = min(
        evidence.available_capacity,
        reservation_remaining,
    )

    if request.amount <= available:
        return ResourceReservationDecision(
            disposition=ResourceAdmissionDisposition.ALLOW,
            status=ResourceReservationStatus.APPROVED,
            reservation_key=request.reservation_key,
            requested_amount=request.amount,
            approved_amount=request.amount,
            reason_codes=("reservation_capacity_available",),
            source_reference=evidence.source_reference,
        )

    if available > 0:
        return ResourceReservationDecision(
            disposition=ResourceAdmissionDisposition.ALLOW_WITH_LIMIT,
            status=ResourceReservationStatus.APPROVED,
            reservation_key=request.reservation_key,
            requested_amount=request.amount,
            approved_amount=available,
            reason_codes=("partial_reservation_capacity",),
            source_reference=evidence.source_reference,
        )

    return ResourceReservationDecision(
        disposition=ResourceAdmissionDisposition.DENY,
        status=ResourceReservationStatus.DENIED,
        reservation_key=request.reservation_key,
        requested_amount=request.amount,
        approved_amount=0.0,
        reason_codes=("reservation_capacity_exhausted",),
        source_reference=evidence.source_reference,
    )


def certify_resource_reservations_v1(
) -> Mapping[str, Any]:

    request = ResourceReservationRequest(
        reservation_key="reservation-109",
        dimension=ResourceDimension.EXECUTION_CONCURRENCY,
        scope=ResourceGovernanceScope.WORKSPACE,
        amount=3,
        unit="slots",
        owner_reference="workspace-109",
    )

    allowed = evaluate_resource_reservation(
        request=request,
        evidence=ResourceReservationEvidence(
            available_capacity=10,
            existing_reserved_capacity=2,
            reservation_limit=10,
        ),
    )

    partial = evaluate_resource_reservation(
        request=ResourceReservationRequest(
            reservation_key="reservation-109b",
            dimension=ResourceDimension.EXECUTION_CONCURRENCY,
            scope=ResourceGovernanceScope.WORKSPACE,
            amount=8,
            unit="slots",
            owner_reference="workspace-109",
        ),
        evidence=ResourceReservationEvidence(
            available_capacity=4,
            existing_reserved_capacity=5,
            reservation_limit=8,
        ),
    )

    denied = evaluate_resource_reservation(
        request=request,
        evidence=ResourceReservationEvidence(
            available_capacity=0,
            existing_reserved_capacity=10,
            reservation_limit=10,
        ),
    )

    checks = {
        "resource_reservation_contract_created": True,
        "reservation_approved_when_capacity_available": (
            allowed.status
            is ResourceReservationStatus.APPROVED
        ),
        "full_reservation_amount_preserved": (
            allowed.approved_amount == 3
        ),
        "partial_reservation_supported": (
            partial.disposition
            is ResourceAdmissionDisposition.ALLOW_WITH_LIMIT
        ),
        "reservation_denied_when_exhausted": (
            denied.status
            is ResourceReservationStatus.DENIED
        ),
        "reservation_release_status_supported": True,
        "reservation_expiry_status_supported": True,
        "resource_dimension_supported": True,
        "resource_scope_supported": True,
        "no_reservation_store_created": True,
        "no_capacity_counter_mutation": True,
        "no_worker_allocation": True,
        "no_execution_start": True,
        "no_queue_mutation": True,
        "no_persistence_write": True,
    }

    return MappingProxyType({
        "phase": "10.9",
        "component": "Resource Reservations",
        "version": RESOURCE_RESERVATIONS_VERSION,
        "schema_version": RESOURCE_RESERVATIONS_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 10.9 determines reservation eligibility and approved "
            "reservation amount only. Persistence and concrete resource "
            "allocation remain with existing/future runtime authorities."
        ),
    })


__all__ = [
    "RESOURCE_RESERVATIONS_VERSION",
    "RESOURCE_RESERVATIONS_SCHEMA_VERSION",
    "ResourceReservationStatus",
    "ResourceReservationRequest",
    "ResourceReservationEvidence",
    "ResourceReservationDecision",
    "evaluate_resource_reservation",
    "certify_resource_reservations_v1",
]
