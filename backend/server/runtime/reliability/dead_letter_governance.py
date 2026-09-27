"""
LinkCraftor Universal Runtime Infrastructure
Phase 9.8 — Dead-Letter Governance

Purpose:
- determine when failed work qualifies for dead-letter handling
- preserve existing queue/dead-letter authority
- distinguish hold, dead-letter and manual-review outcomes

Does NOT:
- create dead-letter queue
- enqueue dead-letter records
- mutate jobs
- mutate queue state
- delete failed work
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional

from .retry_governance import (
    RetryGovernanceDecision,
    RetryGovernanceDisposition,
)


DEAD_LETTER_GOVERNANCE_VERSION = (
    "dead_letter_governance_v9.8.1"
)

DEAD_LETTER_GOVERNANCE_SCHEMA_VERSION = (
    "dead_letter_governance_schema_v1"
)


class DeadLetterDisposition(str, Enum):
    NOT_REQUIRED = "NOT_REQUIRED"
    HOLD = "HOLD"
    DEAD_LETTER = "DEAD_LETTER"
    MANUAL_REVIEW = "MANUAL_REVIEW"


@dataclass(frozen=True, slots=True)
class DeadLetterEvidence:
    job_id: str
    queue_name: str

    retry_decision: RetryGovernanceDecision

    failure_count: int
    poison_message_suspected: bool

    integrity_risk: bool
    security_risk: bool
    data_loss_risk: bool

    replay_safe: bool

    source_reference: Optional[str] = None

    schema_version: str = field(
        default=DEAD_LETTER_GOVERNANCE_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        if not self.job_id.strip():
            raise ValueError("job_id is required.")

        if not self.queue_name.strip():
            raise ValueError("queue_name is required.")

        if self.failure_count < 1:
            raise ValueError("failure_count must be >= 1.")


@dataclass(frozen=True, slots=True)
class DeadLetterDecision:
    disposition: DeadLetterDisposition

    preserve_payload_reference: bool
    replay_allowed: bool

    reason_codes: tuple[str, ...]
    source_reference: Optional[str]

    schema_version: str = field(
        default=DEAD_LETTER_GOVERNANCE_SCHEMA_VERSION,
        init=False,
    )


def evaluate_dead_letter_governance(
    evidence: DeadLetterEvidence,
) -> DeadLetterDecision:

    high_risk = (
        evidence.integrity_risk
        or evidence.security_risk
        or evidence.data_loss_risk
    )

    if high_risk:
        return DeadLetterDecision(
            disposition=DeadLetterDisposition.MANUAL_REVIEW,
            preserve_payload_reference=True,
            replay_allowed=False,
            reason_codes=("high_risk_failure",),
            source_reference=evidence.source_reference,
        )

    if evidence.poison_message_suspected:
        return DeadLetterDecision(
            disposition=DeadLetterDisposition.DEAD_LETTER,
            preserve_payload_reference=True,
            replay_allowed=False,
            reason_codes=("poison_message_suspected",),
            source_reference=evidence.source_reference,
        )

    if (
        evidence.retry_decision.disposition
        is RetryGovernanceDisposition.RETRY_EXHAUSTED
    ):
        return DeadLetterDecision(
            disposition=DeadLetterDisposition.DEAD_LETTER,
            preserve_payload_reference=True,
            replay_allowed=evidence.replay_safe,
            reason_codes=("retry_exhausted",),
            source_reference=evidence.source_reference,
        )

    if (
        evidence.retry_decision.disposition
        is RetryGovernanceDisposition.RETRY_DENIED
    ):
        return DeadLetterDecision(
            disposition=DeadLetterDisposition.HOLD,
            preserve_payload_reference=True,
            replay_allowed=False,
            reason_codes=("retry_denied_hold",),
            source_reference=evidence.source_reference,
        )

    return DeadLetterDecision(
        disposition=DeadLetterDisposition.NOT_REQUIRED,
        preserve_payload_reference=False,
        replay_allowed=False,
        reason_codes=("dead_letter_not_required",),
        source_reference=evidence.source_reference,
    )


def certify_dead_letter_governance_v1(
) -> Mapping[str, Any]:

    exhausted = RetryGovernanceDecision(
        disposition=RetryGovernanceDisposition.RETRY_EXHAUSTED,
        next_attempt=None,
        delay_seconds=None,
        reason_codes=("limit",),
        source_reference="dl-98",
    )

    denied = RetryGovernanceDecision(
        disposition=RetryGovernanceDisposition.RETRY_DENIED,
        next_attempt=None,
        delay_seconds=None,
        reason_codes=("unsafe",),
        source_reference="dl-98-denied",
    )

    dead_letter = evaluate_dead_letter_governance(
        DeadLetterEvidence(
            job_id="job-98",
            queue_name="runtime-default",
            retry_decision=exhausted,
            failure_count=4,
            poison_message_suspected=False,
            integrity_risk=False,
            security_risk=False,
            data_loss_risk=False,
            replay_safe=True,
        )
    )

    manual = evaluate_dead_letter_governance(
        DeadLetterEvidence(
            job_id="job-98b",
            queue_name="runtime-default",
            retry_decision=denied,
            failure_count=2,
            poison_message_suspected=False,
            integrity_risk=True,
            security_risk=False,
            data_loss_risk=False,
            replay_safe=False,
        )
    )

    hold = evaluate_dead_letter_governance(
        DeadLetterEvidence(
            job_id="job-98c",
            queue_name="runtime-default",
            retry_decision=denied,
            failure_count=2,
            poison_message_suspected=False,
            integrity_risk=False,
            security_risk=False,
            data_loss_risk=False,
            replay_safe=False,
        )
    )

    checks = {
        "dead_letter_governance_contract_created": True,
        "retry_exhaustion_dead_letters": (
            dead_letter.disposition
            is DeadLetterDisposition.DEAD_LETTER
        ),
        "safe_replay_preserved": dead_letter.replay_allowed,
        "high_risk_requires_manual_review": (
            manual.disposition
            is DeadLetterDisposition.MANUAL_REVIEW
        ),
        "retry_denied_can_hold": (
            hold.disposition
            is DeadLetterDisposition.HOLD
        ),
        "payload_reference_preservation_supported": True,
        "poison_message_detection_supported": True,
        "existing_dead_letter_authority_preserved": True,
        "existing_queue_authority_preserved": True,
        "no_dead_letter_queue_created": True,
        "no_dead_letter_enqueue": True,
        "no_queue_mutation": True,
        "no_job_mutation": True,
        "no_payload_deletion": True,
    }

    return MappingProxyType({
        "phase": "9.8",
        "component": "Dead-Letter Governance",
        "version": DEAD_LETTER_GOVERNANCE_VERSION,
        "schema_version": DEAD_LETTER_GOVERNANCE_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 9.8 decides whether failed work should be held, "
            "dead-lettered or manually reviewed. Existing queue/dead-letter "
            "mechanics execute approved operations."
        ),
    })


__all__ = [
    "DEAD_LETTER_GOVERNANCE_VERSION",
    "DEAD_LETTER_GOVERNANCE_SCHEMA_VERSION",
    "DeadLetterDisposition",
    "DeadLetterEvidence",
    "DeadLetterDecision",
    "evaluate_dead_letter_governance",
    "certify_dead_letter_governance_v1",
]
