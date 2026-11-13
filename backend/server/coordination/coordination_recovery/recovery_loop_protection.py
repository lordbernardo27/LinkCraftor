"""
LinkCraftor — Universal Coordination Framework

Phase 9.6 — Recovery Loop Protection.

Pure workflow-level recovery-loop governance.

It determines whether another UCF recovery cycle is permitted.

It does NOT:
- retry/requeue Runtime jobs,
- mutate workflow lifecycle,
- persist attempts,
- execute compensation,
- invoke manual intervention.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Tuple


RECOVERY_LOOP_PROTECTION_VERSION = (
    "recovery_loop_protection_v9.6.0"
)

RECOVERY_LOOP_PROTECTION_SCHEMA_VERSION = (
    "recovery_loop_protection_schema_v1"
)


class RecoveryLoopProtectionError(
    ValueError
):
    pass


class RecoveryLoopDisposition(
    str,
    Enum,
):
    ALLOW_RECOVERY = "ALLOW_RECOVERY"
    MANUAL_INTERVENTION = "MANUAL_INTERVENTION"
    FAIL_WORKFLOW = "FAIL_WORKFLOW"


@dataclass(
    frozen=True,
    slots=True,
)
class RecoveryLoopEvidence:

    workflow_id: str
    stage_id: str
    failure_code: str

    total_recovery_attempts: int
    same_failure_recovery_attempts: int

    max_total_recovery_attempts: int = 3
    max_same_failure_attempts: int = 2

    prior_recovery_succeeded: bool = False


@dataclass(
    frozen=True,
    slots=True,
)
class RecoveryLoopDecision:

    disposition: RecoveryLoopDisposition

    next_recovery_attempt: int | None

    reason_codes: Tuple[
        str,
        ...
    ]

    loop_detected: bool

    protection_version: str = (
        RECOVERY_LOOP_PROTECTION_VERSION
    )

    schema_version: str = (
        RECOVERY_LOOP_PROTECTION_SCHEMA_VERSION
    )

    def to_dict(
        self,
    ) -> Mapping[str, Any]:

        return MappingProxyType({
            "disposition":
                self.disposition.value,

            "next_recovery_attempt":
                self.next_recovery_attempt,

            "reason_codes":
                self.reason_codes,

            "loop_detected":
                self.loop_detected,

            "protection_version":
                self.protection_version,

            "schema_version":
                self.schema_version,
        })


def evaluate_recovery_loop(
    evidence: RecoveryLoopEvidence,
) -> RecoveryLoopDecision:

    if not isinstance(
        evidence,
        RecoveryLoopEvidence,
    ):
        raise RecoveryLoopProtectionError(
            "evidence must be RecoveryLoopEvidence"
        )

    if evidence.total_recovery_attempts < 0:
        raise RecoveryLoopProtectionError(
            "total_recovery_attempts cannot be negative"
        )

    if evidence.same_failure_recovery_attempts < 0:
        raise RecoveryLoopProtectionError(
            "same_failure_recovery_attempts cannot be negative"
        )

    if evidence.max_total_recovery_attempts < 1:
        raise RecoveryLoopProtectionError(
            "max_total_recovery_attempts must be >= 1"
        )

    if evidence.max_same_failure_attempts < 1:
        raise RecoveryLoopProtectionError(
            "max_same_failure_attempts must be >= 1"
        )

    if evidence.prior_recovery_succeeded:
        return RecoveryLoopDecision(
            disposition=
                RecoveryLoopDisposition.ALLOW_RECOVERY,

            next_recovery_attempt=
                evidence.total_recovery_attempts
                + 1,

            reason_codes=(
                "prior_recovery_succeeded",
            ),

            loop_detected=
                False,
        )

    if (
        evidence.same_failure_recovery_attempts
        >= evidence.max_same_failure_attempts
    ):
        return RecoveryLoopDecision(
            disposition=
                RecoveryLoopDisposition.MANUAL_INTERVENTION,

            next_recovery_attempt=
                None,

            reason_codes=(
                "same_failure_recovery_loop_detected",
            ),

            loop_detected=
                True,
        )

    if (
        evidence.total_recovery_attempts
        >= evidence.max_total_recovery_attempts
    ):
        return RecoveryLoopDecision(
            disposition=
                RecoveryLoopDisposition.FAIL_WORKFLOW,

            next_recovery_attempt=
                None,

            reason_codes=(
                "total_recovery_attempt_limit_reached",
            ),

            loop_detected=
                True,
        )

    return RecoveryLoopDecision(
        disposition=
            RecoveryLoopDisposition.ALLOW_RECOVERY,

        next_recovery_attempt=
            evidence.total_recovery_attempts
            + 1,

        reason_codes=(
            "recovery_attempt_within_limits",
        ),

        loop_detected=
            False,
    )


__all__ = [
    "RECOVERY_LOOP_PROTECTION_VERSION",
    "RECOVERY_LOOP_PROTECTION_SCHEMA_VERSION",
    "RecoveryLoopProtectionError",
    "RecoveryLoopDisposition",
    "RecoveryLoopEvidence",
    "RecoveryLoopDecision",
    "evaluate_recovery_loop",
]
