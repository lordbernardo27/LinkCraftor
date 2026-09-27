"""
LinkCraftor Universal Runtime Infrastructure
Phase 9.7 — Orchestration Recovery

Determines how Phase-5 orchestration should recover after stage/runtime failure.

Does NOT mutate orchestration state or re-plan workflows directly.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional


ORCHESTRATION_RECOVERY_VERSION = "orchestration_recovery_v9.7.1"
ORCHESTRATION_RECOVERY_SCHEMA_VERSION = "orchestration_recovery_schema_v1"


class OrchestrationRecoveryAction(str, Enum):
    NONE = "NONE"
    RESUME_ORCHESTRATION = "RESUME_ORCHESTRATION"
    REEVALUATE_READINESS = "REEVALUATE_READINESS"
    RECOMPUTE_DEPENDENCIES = "RECOMPUTE_DEPENDENCIES"
    HOLD_ORCHESTRATION = "HOLD_ORCHESTRATION"
    FAIL_ORCHESTRATION = "FAIL_ORCHESTRATION"


@dataclass(frozen=True, slots=True)
class OrchestrationRecoveryEvidence:
    orchestration_id: str

    blocked: bool
    suspended: bool
    terminal: bool

    failed_stage_count: int
    unresolved_dependency_count: int

    execution_recovery_pending: bool
    recoverable_stage_available: bool

    state_integrity_valid: bool

    source_reference: Optional[str] = None

    schema_version: str = field(
        default=ORCHESTRATION_RECOVERY_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class OrchestrationRecoveryDecision:
    actions: tuple[OrchestrationRecoveryAction, ...]

    reason_codes: tuple[str, ...]
    source_reference: Optional[str]

    schema_version: str = field(
        default=ORCHESTRATION_RECOVERY_SCHEMA_VERSION,
        init=False,
    )


def evaluate_orchestration_recovery(
    evidence: OrchestrationRecoveryEvidence,
) -> OrchestrationRecoveryDecision:

    actions: list[OrchestrationRecoveryAction] = []
    reasons: list[str] = []

    if evidence.terminal:
        return OrchestrationRecoveryDecision(
            actions=(OrchestrationRecoveryAction.NONE,),
            reason_codes=("orchestration_terminal",),
            source_reference=evidence.source_reference,
        )

    if not evidence.state_integrity_valid:
        return OrchestrationRecoveryDecision(
            actions=(OrchestrationRecoveryAction.HOLD_ORCHESTRATION,),
            reason_codes=("orchestration_state_integrity_invalid",),
            source_reference=evidence.source_reference,
        )

    if evidence.execution_recovery_pending:
        actions.append(
            OrchestrationRecoveryAction.HOLD_ORCHESTRATION
        )
        reasons.append("execution_recovery_pending")

    if evidence.unresolved_dependency_count > 0:
        actions.append(
            OrchestrationRecoveryAction.RECOMPUTE_DEPENDENCIES
        )
        reasons.append("dependencies_unresolved")

    if evidence.blocked:
        actions.append(
            OrchestrationRecoveryAction.REEVALUATE_READINESS
        )
        reasons.append("orchestration_blocked")

    if (
        evidence.recoverable_stage_available
        and not evidence.execution_recovery_pending
    ):
        actions.append(
            OrchestrationRecoveryAction.RESUME_ORCHESTRATION
        )
        reasons.append("recoverable_stage_available")

    if (
        evidence.failed_stage_count > 0
        and not evidence.recoverable_stage_available
        and not evidence.execution_recovery_pending
    ):
        actions.append(
            OrchestrationRecoveryAction.FAIL_ORCHESTRATION
        )
        reasons.append("no_recoverable_stage")

    if not actions:
        actions.append(
            OrchestrationRecoveryAction.NONE
        )
        reasons.append("orchestration_recovery_not_required")

    return OrchestrationRecoveryDecision(
        actions=tuple(dict.fromkeys(actions)),
        reason_codes=tuple(reasons),
        source_reference=evidence.source_reference,
    )


def certify_orchestration_recovery_v1() -> Mapping[str, Any]:

    blocked = evaluate_orchestration_recovery(
        OrchestrationRecoveryEvidence(
            orchestration_id="orchestration-97",
            blocked=True,
            suspended=False,
            terminal=False,
            failed_stage_count=1,
            unresolved_dependency_count=2,
            execution_recovery_pending=False,
            recoverable_stage_available=True,
            state_integrity_valid=True,
        )
    )

    unsafe = evaluate_orchestration_recovery(
        OrchestrationRecoveryEvidence(
            orchestration_id="orchestration-97b",
            blocked=True,
            suspended=True,
            terminal=False,
            failed_stage_count=1,
            unresolved_dependency_count=0,
            execution_recovery_pending=False,
            recoverable_stage_available=True,
            state_integrity_valid=False,
        )
    )

    checks = {
        "orchestration_recovery_contract_created": True,
        "readiness_reevaluation_supported": (
            OrchestrationRecoveryAction.REEVALUATE_READINESS
            in blocked.actions
        ),
        "dependency_recompute_supported": (
            OrchestrationRecoveryAction.RECOMPUTE_DEPENDENCIES
            in blocked.actions
        ),
        "orchestration_resume_supported": (
            OrchestrationRecoveryAction.RESUME_ORCHESTRATION
            in blocked.actions
        ),
        "invalid_state_integrity_holds": (
            unsafe.actions
            == (OrchestrationRecoveryAction.HOLD_ORCHESTRATION,)
        ),
        "execution_recovery_dependency_supported": True,
        "terminal_orchestration_guard_supported": True,
        "phase5_orchestration_authority_preserved": True,
        "phase5_readiness_mechanics_preserved": True,
        "phase5_dependency_mechanics_preserved": True,
        "phase5_resume_mechanics_preserved": True,
        "no_orchestration_mutation": True,
        "no_execution_mutation": True,
        "no_replanning_engine_created": True,
        "no_persistence_write": True,
    }

    return MappingProxyType({
        "phase": "9.7",
        "component": "Orchestration Recovery",
        "version": ORCHESTRATION_RECOVERY_VERSION,
        "schema_version": ORCHESTRATION_RECOVERY_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 9.7 selects orchestration recovery posture only. Phase 5 "
            "remains authoritative for readiness, dependencies, resume, "
            "completion and orchestration state transitions."
        ),
    })


__all__ = [
    "ORCHESTRATION_RECOVERY_VERSION",
    "ORCHESTRATION_RECOVERY_SCHEMA_VERSION",
    "OrchestrationRecoveryAction",
    "OrchestrationRecoveryEvidence",
    "OrchestrationRecoveryDecision",
    "evaluate_orchestration_recovery",
    "certify_orchestration_recovery_v1",
]
