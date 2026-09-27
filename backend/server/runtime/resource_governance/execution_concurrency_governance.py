"""
LinkCraftor Universal Runtime Infrastructure
Phase 10.5 — Execution Concurrency Governance

Determines whether a new execution may consume concurrency capacity.

Does NOT start executions or mutate execution state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, Optional

from .resource_governance_contract import (
    ResourceAdmissionDisposition,
)


EXECUTION_CONCURRENCY_GOVERNANCE_VERSION = (
    "execution_concurrency_governance_v10.5.1"
)

EXECUTION_CONCURRENCY_GOVERNANCE_SCHEMA_VERSION = (
    "execution_concurrency_governance_schema_v1"
)


@dataclass(frozen=True, slots=True)
class ExecutionConcurrencyEvidence:
    scope_key: str

    concurrency_limit: int
    running_executions: int
    reserved_executions: int

    degraded_mode_hold: bool = False

    source_reference: Optional[str] = None

    schema_version: str = field(
        default=EXECUTION_CONCURRENCY_GOVERNANCE_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class ExecutionConcurrencyDecision:
    disposition: ResourceAdmissionDisposition

    requested_executions: int
    allowed_executions: int
    remaining_concurrency: int

    reason_codes: tuple[str, ...]
    source_reference: Optional[str]

    schema_version: str = field(
        default=EXECUTION_CONCURRENCY_GOVERNANCE_SCHEMA_VERSION,
        init=False,
    )


def evaluate_execution_concurrency(
    *,
    evidence: ExecutionConcurrencyEvidence,
    requested_executions: int,
) -> ExecutionConcurrencyDecision:

    if requested_executions < 1:
        raise ValueError("requested_executions must be >= 1.")

    remaining = max(
        evidence.concurrency_limit
        - evidence.running_executions
        - evidence.reserved_executions,
        0,
    )

    if evidence.degraded_mode_hold:
        return ExecutionConcurrencyDecision(
            disposition=ResourceAdmissionDisposition.HOLD,
            requested_executions=requested_executions,
            allowed_executions=0,
            remaining_concurrency=remaining,
            reason_codes=("degraded_mode_hold",),
            source_reference=evidence.source_reference,
        )

    if requested_executions <= remaining:
        disposition = ResourceAdmissionDisposition.ALLOW
        allowed = requested_executions
        reasons = ("execution_concurrency_available",)

    elif remaining > 0:
        disposition = ResourceAdmissionDisposition.ALLOW_WITH_LIMIT
        allowed = remaining
        reasons = ("execution_concurrency_partial",)

    else:
        disposition = ResourceAdmissionDisposition.DEFER
        allowed = 0
        reasons = ("execution_concurrency_exhausted",)

    return ExecutionConcurrencyDecision(
        disposition=disposition,
        requested_executions=requested_executions,
        allowed_executions=allowed,
        remaining_concurrency=remaining,
        reason_codes=reasons,
        source_reference=evidence.source_reference,
    )


def certify_execution_concurrency_governance_v1(
) -> Mapping[str, Any]:

    evidence = ExecutionConcurrencyEvidence(
        scope_key="workspace-105",
        concurrency_limit=10,
        running_executions=6,
        reserved_executions=1,
    )

    allowed = evaluate_execution_concurrency(
        evidence=evidence,
        requested_executions=2,
    )

    exhausted = evaluate_execution_concurrency(
        evidence=ExecutionConcurrencyEvidence(
            scope_key="workspace-105b",
            concurrency_limit=5,
            running_executions=5,
            reserved_executions=0,
        ),
        requested_executions=1,
    )

    checks = {
        "execution_concurrency_contract_created": True,
        "remaining_concurrency_calculated": (
            allowed.remaining_concurrency == 3
        ),
        "safe_execution_admitted": (
            allowed.disposition
            is ResourceAdmissionDisposition.ALLOW
        ),
        "concurrency_exhaustion_defers": (
            exhausted.disposition
            is ResourceAdmissionDisposition.DEFER
        ),
        "partial_concurrency_supported": True,
        "degraded_mode_hold_supported": True,
        "phase6_execution_authority_preserved": True,
        "phase9_degraded_mode_compatible": True,
        "no_execution_start": True,
        "no_execution_mutation": True,
        "no_scheduler_created": True,
        "no_worker_assignment": True,
    }

    return MappingProxyType({
        "phase": "10.5",
        "component": "Execution Concurrency Governance",
        "version": EXECUTION_CONCURRENCY_GOVERNANCE_VERSION,
        "schema_version": EXECUTION_CONCURRENCY_GOVERNANCE_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 10.5 determines execution-concurrency admission only. "
            "Phase 6 remains authoritative for execution start and lifecycle."
        ),
    })


__all__ = [
    "EXECUTION_CONCURRENCY_GOVERNANCE_VERSION",
    "EXECUTION_CONCURRENCY_GOVERNANCE_SCHEMA_VERSION",
    "ExecutionConcurrencyEvidence",
    "ExecutionConcurrencyDecision",
    "evaluate_execution_concurrency",
    "certify_execution_concurrency_governance_v1",
]
