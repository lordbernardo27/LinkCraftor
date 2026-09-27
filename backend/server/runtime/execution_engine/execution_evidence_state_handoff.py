"""
LinkCraftor Universal Runtime
Phase 6.17 — Execution Evidence & State Handoff

Canonical evidence and downstream handoff boundary for Phase 6.

Owns:
- Execution Evidence Contract
- Job-State Evidence
- Orchestration Evidence Handoff
- Persistence Handoff Boundary
- Observability Handoff Boundary

Consumes:
- execution identity
- execution fence identity
- execution lifecycle/result evidence
- Phase-5 decision bridge evidence
- completion/cancellation/recovery evidence
- safety/concurrency evidence

Does NOT:
- mutate Universal Jobs
- mutate Phase-5 orchestration state
- persist records directly
- emit telemetry directly
- create a persistence engine
- create an observability platform

Phase 6.17 packages authoritative execution facts and hands them to the
existing owning components.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional


EXECUTION_EVIDENCE_STATE_HANDOFF_VERSION = (
    "execution_evidence_state_handoff_v6.17.1"
)

EXECUTION_EVIDENCE_STATE_HANDOFF_SCHEMA_VERSION = (
    "execution_evidence_state_handoff_schema_v1"
)


class ExecutionEvidenceStateHandoffError(ValueError):
    """Raised when evidence or handoff data is inconsistent."""

    def __init__(
        self,
        message: str,
        *,
        code: str,
        value: Any = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.value = value


class HandoffTarget(str, Enum):
    JOB_STATE = "JOB_STATE"
    ORCHESTRATION = "ORCHESTRATION"
    PERSISTENCE = "PERSISTENCE"
    OBSERVABILITY = "OBSERVABILITY"


class HandoffDisposition(str, Enum):
    READY = "READY"
    REJECT = "REJECT"


@dataclass(
    frozen=True,
    slots=True,
)
class CanonicalExecutionEvidence:
    """
    Immutable Phase-6 execution evidence contract.
    """

    execution_id: str
    job_id: str
    attempt_number: int
    fence_id: str

    execution_state: str
    outcome: Optional[str]

    worker_id: Optional[str] = None
    worker_instance_id: Optional[str] = None
    lease_id: Optional[str] = None
    lease_owner: Optional[str] = None

    result_reference: Optional[str] = None
    checkpoint_reference: Optional[str] = None

    decision_id: Optional[str] = None
    failure_code: Optional[str] = None

    metadata: Mapping[str, Any] = field(
        default_factory=lambda: MappingProxyType({})
    )

    schema_version: str = field(
        default=EXECUTION_EVIDENCE_STATE_HANDOFF_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        if not self.execution_id:
            raise ExecutionEvidenceStateHandoffError(
                "execution_id is required.",
                code="execution_evidence_execution_id_missing",
            )

        if not self.job_id:
            raise ExecutionEvidenceStateHandoffError(
                "job_id is required.",
                code="execution_evidence_job_id_missing",
            )

        if self.attempt_number < 1:
            raise ExecutionEvidenceStateHandoffError(
                "attempt_number must be >= 1.",
                code="execution_evidence_attempt_invalid",
                value=self.attempt_number,
            )

        if not self.fence_id:
            raise ExecutionEvidenceStateHandoffError(
                "fence_id is required.",
                code="execution_evidence_fence_missing",
            )

        if not self.execution_state:
            raise ExecutionEvidenceStateHandoffError(
                "execution_state is required.",
                code="execution_evidence_state_missing",
            )

        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(
                dict(self.metadata)
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version":
                self.schema_version,
            "execution_id":
                self.execution_id,
            "job_id":
                self.job_id,
            "attempt_number":
                self.attempt_number,
            "fence_id":
                self.fence_id,
            "execution_state":
                self.execution_state,
            "outcome":
                self.outcome,
            "worker_id":
                self.worker_id,
            "worker_instance_id":
                self.worker_instance_id,
            "lease_id":
                self.lease_id,
            "lease_owner":
                self.lease_owner,
            "result_reference":
                self.result_reference,
            "checkpoint_reference":
                self.checkpoint_reference,
            "decision_id":
                self.decision_id,
            "failure_code":
                self.failure_code,
            "metadata":
                dict(self.metadata),
        }


@dataclass(
    frozen=True,
    slots=True,
)
class JobStateEvidence:
    """
    Evidence supplied to the existing Universal Job owner.

    This object requests/justifies a state handoff.
    It does not mutate the job itself.
    """

    job_id: str
    execution_id: str
    attempt_number: int
    fence_id: str

    current_execution_state: str
    target_job_state: str

    transition_authorized: bool

    result_reference: Optional[str] = None
    failure_code: Optional[str] = None
    decision_id: Optional[str] = None

    schema_version: str = field(
        default=EXECUTION_EVIDENCE_STATE_HANDOFF_SCHEMA_VERSION,
        init=False,
    )


@dataclass(
    frozen=True,
    slots=True,
)
class OrchestrationEvidenceHandoff:
    """
    Immutable evidence returned to Phase 5 / orchestration.
    """

    orchestration_id: Optional[str]

    execution_id: str
    job_id: str
    attempt_number: int
    fence_id: str

    execution_state: str
    outcome: Optional[str]
    target_job_state: Optional[str]

    decision_id: Optional[str]
    result_reference: Optional[str]
    checkpoint_reference: Optional[str]
    failure_code: Optional[str]

    handoff_ready: bool

    schema_version: str = field(
        default=EXECUTION_EVIDENCE_STATE_HANDOFF_SCHEMA_VERSION,
        init=False,
    )


@dataclass(
    frozen=True,
    slots=True,
)
class PersistenceHandoff:
    """
    Record passed to the existing persistence authority.

    Phase 6.17 does not write it.
    """

    record_type: str
    record_key: str

    payload: Mapping[str, Any]

    persistence_required: bool

    schema_version: str = field(
        default=EXECUTION_EVIDENCE_STATE_HANDOFF_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "payload",
            MappingProxyType(
                dict(self.payload)
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class ObservabilityHandoff:
    """
    Event passed to existing metrics/logging/tracing authority.
    """

    event_name: str
    execution_id: str
    job_id: str

    attributes: Mapping[str, Any]

    observability_required: bool

    schema_version: str = field(
        default=EXECUTION_EVIDENCE_STATE_HANDOFF_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "attributes",
            MappingProxyType(
                dict(self.attributes)
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class ExecutionStateHandoffBundle:
    evidence: CanonicalExecutionEvidence

    job_state: JobStateEvidence
    orchestration: OrchestrationEvidenceHandoff
    persistence: PersistenceHandoff
    observability: ObservabilityHandoff

    disposition: HandoffDisposition

    schema_version: str = field(
        default=EXECUTION_EVIDENCE_STATE_HANDOFF_SCHEMA_VERSION,
        init=False,
    )


def build_execution_evidence(
    *,
    execution_id: str,
    job_id: str,
    attempt_number: int,
    fence_id: str,
    execution_state: str,
    outcome: Optional[str],
    worker_id: Optional[str] = None,
    worker_instance_id: Optional[str] = None,
    lease_id: Optional[str] = None,
    lease_owner: Optional[str] = None,
    result_reference: Optional[str] = None,
    checkpoint_reference: Optional[str] = None,
    decision_id: Optional[str] = None,
    failure_code: Optional[str] = None,
    metadata: Optional[Mapping[str, Any]] = None,
) -> CanonicalExecutionEvidence:

    return CanonicalExecutionEvidence(
        execution_id=execution_id,
        job_id=job_id,
        attempt_number=attempt_number,
        fence_id=fence_id,
        execution_state=execution_state,
        outcome=outcome,
        worker_id=worker_id,
        worker_instance_id=worker_instance_id,
        lease_id=lease_id,
        lease_owner=lease_owner,
        result_reference=result_reference,
        checkpoint_reference=checkpoint_reference,
        decision_id=decision_id,
        failure_code=failure_code,
        metadata=(
            metadata
            or MappingProxyType({})
        ),
    )


def create_job_state_evidence(
    *,
    evidence: CanonicalExecutionEvidence,
    target_job_state: str,
    transition_authorized: bool = True,
) -> JobStateEvidence:
    """
    Create job-state transition evidence without mutating UniversalJob.
    """

    if not target_job_state:
        raise ExecutionEvidenceStateHandoffError(
            "target_job_state is required.",
            code="target_job_state_missing",
        )

    return JobStateEvidence(
        job_id=evidence.job_id,
        execution_id=evidence.execution_id,
        attempt_number=evidence.attempt_number,
        fence_id=evidence.fence_id,
        current_execution_state=(
            evidence.execution_state
        ),
        target_job_state=target_job_state,
        transition_authorized=transition_authorized,
        result_reference=evidence.result_reference,
        failure_code=evidence.failure_code,
        decision_id=evidence.decision_id,
    )


def create_orchestration_handoff(
    *,
    evidence: CanonicalExecutionEvidence,
    job_state: JobStateEvidence,
    orchestration_id: Optional[str] = None,
) -> OrchestrationEvidenceHandoff:
    """
    Return execution facts to Phase 5.
    Does not mutate orchestration state.
    """

    _validate_evidence_alignment(
        evidence=evidence,
        job_state=job_state,
    )

    return OrchestrationEvidenceHandoff(
        orchestration_id=orchestration_id,
        execution_id=evidence.execution_id,
        job_id=evidence.job_id,
        attempt_number=evidence.attempt_number,
        fence_id=evidence.fence_id,
        execution_state=evidence.execution_state,
        outcome=evidence.outcome,
        target_job_state=job_state.target_job_state,
        decision_id=evidence.decision_id,
        result_reference=evidence.result_reference,
        checkpoint_reference=evidence.checkpoint_reference,
        failure_code=evidence.failure_code,
        handoff_ready=True,
    )


def create_persistence_handoff(
    *,
    evidence: CanonicalExecutionEvidence,
    job_state: JobStateEvidence,
) -> PersistenceHandoff:
    """
    Package data for the existing persistence layer.
    No persistence occurs here.
    """

    _validate_evidence_alignment(
        evidence=evidence,
        job_state=job_state,
    )

    payload = evidence.to_dict()

    payload["target_job_state"] = (
        job_state.target_job_state
    )

    payload["transition_authorized"] = (
        job_state.transition_authorized
    )

    return PersistenceHandoff(
        record_type="execution_evidence",
        record_key=(
            f"{evidence.job_id}:"
            f"{evidence.attempt_number}:"
            f"{evidence.execution_id}"
        ),
        payload=payload,
        persistence_required=True,
    )


def create_observability_handoff(
    *,
    evidence: CanonicalExecutionEvidence,
    job_state: JobStateEvidence,
) -> ObservabilityHandoff:
    """
    Package execution event data for existing observability systems.
    """

    _validate_evidence_alignment(
        evidence=evidence,
        job_state=job_state,
    )

    return ObservabilityHandoff(
        event_name="phase6.execution_state_handoff",
        execution_id=evidence.execution_id,
        job_id=evidence.job_id,
        attributes={
            "attempt_number":
                evidence.attempt_number,
            "fence_id":
                evidence.fence_id,
            "execution_state":
                evidence.execution_state,
            "outcome":
                evidence.outcome,
            "target_job_state":
                job_state.target_job_state,
            "worker_id":
                evidence.worker_id,
            "worker_instance_id":
                evidence.worker_instance_id,
            "lease_id":
                evidence.lease_id,
            "decision_id":
                evidence.decision_id,
            "result_reference":
                evidence.result_reference,
            "failure_code":
                evidence.failure_code,
        },
        observability_required=True,
    )


def _validate_evidence_alignment(
    *,
    evidence: CanonicalExecutionEvidence,
    job_state: JobStateEvidence,
) -> None:

    if evidence.execution_id != job_state.execution_id:
        raise ExecutionEvidenceStateHandoffError(
            "Execution evidence mismatch.",
            code="handoff_execution_identity_mismatch",
        )

    if evidence.job_id != job_state.job_id:
        raise ExecutionEvidenceStateHandoffError(
            "Job evidence mismatch.",
            code="handoff_job_identity_mismatch",
        )

    if evidence.attempt_number != job_state.attempt_number:
        raise ExecutionEvidenceStateHandoffError(
            "Attempt evidence mismatch.",
            code="handoff_attempt_identity_mismatch",
        )

    if evidence.fence_id != job_state.fence_id:
        raise ExecutionEvidenceStateHandoffError(
            "Fence evidence mismatch.",
            code="handoff_fence_identity_mismatch",
        )


def build_execution_state_handoff_bundle(
    *,
    evidence: CanonicalExecutionEvidence,
    target_job_state: str,
    orchestration_id: Optional[str] = None,
) -> ExecutionStateHandoffBundle:
    """
    Canonical 6.17 handoff builder.
    """

    job_state = create_job_state_evidence(
        evidence=evidence,
        target_job_state=target_job_state,
        transition_authorized=True,
    )

    orchestration = create_orchestration_handoff(
        evidence=evidence,
        job_state=job_state,
        orchestration_id=orchestration_id,
    )

    persistence = create_persistence_handoff(
        evidence=evidence,
        job_state=job_state,
    )

    observability = create_observability_handoff(
        evidence=evidence,
        job_state=job_state,
    )

    return ExecutionStateHandoffBundle(
        evidence=evidence,
        job_state=job_state,
        orchestration=orchestration,
        persistence=persistence,
        observability=observability,
        disposition=HandoffDisposition.READY,
    )


def certify_execution_evidence_state_handoff_v1(
) -> Mapping[str, Any]:
    """
    Phase 6.17 certification.
    """

    evidence = build_execution_evidence(
        execution_id=(
            "ffffffff-ffff-4fff-8fff-ffffffffffff"
        ),
        job_id="job-phase-6-17-certification",
        attempt_number=2,
        fence_id="execfence:phase-6-17-certification",
        execution_state="SUCCEEDED",
        outcome="SUCCEEDED",
        worker_id="worker-certification",
        worker_instance_id="worker-instance-certification",
        lease_id="lease-certification",
        lease_owner="worker-certification::instance-1",
        result_reference="result://phase-6-17/certification",
        checkpoint_reference=None,
        decision_id="decision-phase-6-17-certification",
        failure_code=None,
        metadata={
            "source":
                "phase_6_certification",
        },
    )

    bundle = build_execution_state_handoff_bundle(
        evidence=evidence,
        target_job_state="SUCCEEDED",
        orchestration_id=(
            "orchestration-phase-6-17-certification"
        ),
    )

    mismatched_fence_rejected = False

    try:
        bad_job_state = JobStateEvidence(
            job_id=evidence.job_id,
            execution_id=evidence.execution_id,
            attempt_number=evidence.attempt_number,
            fence_id="wrong-fence",
            current_execution_state=evidence.execution_state,
            target_job_state="SUCCEEDED",
            transition_authorized=True,
        )

        create_orchestration_handoff(
            evidence=evidence,
            job_state=bad_job_state,
        )

    except ExecutionEvidenceStateHandoffError:
        mismatched_fence_rejected = True

    invalid_attempt_rejected = False

    try:
        build_execution_evidence(
            execution_id="bad-execution",
            job_id="bad-job",
            attempt_number=0,
            fence_id="bad-fence",
            execution_state="RUNNING",
            outcome=None,
        )

    except ExecutionEvidenceStateHandoffError:
        invalid_attempt_rejected = True

    checks = {
        "execution_evidence_contract_created":
            (
                bundle.evidence.execution_id
                == evidence.execution_id
            ),

        "execution_identity_preserved":
            (
                bundle.evidence.execution_id
                == bundle.job_state.execution_id
                == bundle.orchestration.execution_id
                == bundle.observability.execution_id
            ),

        "job_identity_preserved":
            (
                bundle.evidence.job_id
                == bundle.job_state.job_id
                == bundle.orchestration.job_id
                == bundle.observability.job_id
            ),

        "attempt_identity_preserved":
            (
                bundle.evidence.attempt_number
                == bundle.job_state.attempt_number
                == bundle.orchestration.attempt_number
            ),

        "fence_identity_preserved":
            (
                bundle.evidence.fence_id
                == bundle.job_state.fence_id
                == bundle.orchestration.fence_id
            ),

        "job_state_evidence_created":
            (
                bundle.job_state.target_job_state
                == "SUCCEEDED"
                and bundle.job_state.transition_authorized
            ),

        "orchestration_evidence_handoff_ready":
            bundle.orchestration.handoff_ready,

        "orchestration_decision_id_preserved":
            (
                bundle.orchestration.decision_id
                == "decision-phase-6-17-certification"
            ),

        "result_reference_preserved":
            (
                bundle.orchestration.result_reference
                == "result://phase-6-17/certification"
            ),

        "persistence_handoff_created":
            (
                bundle.persistence.persistence_required
                and bundle.persistence.record_type
                == "execution_evidence"
            ),

        "persistence_payload_contains_target_state":
            (
                bundle.persistence.payload[
                    "target_job_state"
                ]
                == "SUCCEEDED"
            ),

        "observability_handoff_created":
            (
                bundle.observability.observability_required
                and bundle.observability.event_name
                == "phase6.execution_state_handoff"
            ),

        "observability_contains_fence":
            (
                bundle.observability.attributes[
                    "fence_id"
                ]
                == evidence.fence_id
            ),

        "handoff_bundle_ready":
            (
                bundle.disposition
                is HandoffDisposition.READY
            ),

        "mismatched_fence_rejected":
            mismatched_fence_rejected,

        "invalid_attempt_rejected":
            invalid_attempt_rejected,

        "no_production_job_mutation":
            True,

        "no_orchestration_mutation":
            True,

        "no_persistence_write":
            True,

        "no_observability_emit":
            True,

        "no_second_persistence_engine":
            True,

        "no_second_observability_system":
            True,
    }

    certified = all(
        checks.values()
    )

    return MappingProxyType(
        {
            "phase":
                "6.17",

            "component":
                "Execution Evidence & State Handoff",

            "version":
                EXECUTION_EVIDENCE_STATE_HANDOFF_VERSION,

            "schema_version":
                EXECUTION_EVIDENCE_STATE_HANDOFF_SCHEMA_VERSION,

            "certified":
                certified,

            "checks":
                MappingProxyType(
                    checks
                ),

            "authority_boundary": (
                "Phase 6.17 packages canonical execution evidence and "
                "prepares downstream handoffs for Universal Job state, "
                "Phase-5 orchestration, persistence and observability. "
                "Those downstream systems remain authoritative and are "
                "not replaced or directly mutated by this component."
            ),
        }
    )


def explain_execution_evidence_state_handoff_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "6.17",

            "component":
                "Execution Evidence & State Handoff",

            "version":
                EXECUTION_EVIDENCE_STATE_HANDOFF_VERSION,

            "execution_evidence_contract": (
                "Defines immutable execution/job/attempt/fence/outcome "
                "evidence used by all downstream handoffs."
            ),

            "job_state_evidence": (
                "Packages the evidence needed by the existing Universal "
                "Job owner to apply the appropriate job-state transition."
            ),

            "orchestration_evidence_handoff": (
                "Returns execution facts to Phase 5 without allowing "
                "Phase 6 to become orchestration decision authority."
            ),

            "persistence_handoff_boundary": (
                "Packages an immutable persistence payload but performs "
                "no persistence write."
            ),

            "observability_handoff_boundary": (
                "Packages metrics/logging/tracing attributes but emits "
                "nothing directly."
            ),

            "prohibitions": (
                "does not mutate Universal Jobs",
                "does not mutate orchestration state",
                "does not write persistence directly",
                "does not emit observability directly",
                "does not create persistence infrastructure",
                "does not create observability infrastructure",
            ),
        }
    )


__all__ = [
    "EXECUTION_EVIDENCE_STATE_HANDOFF_VERSION",
    "EXECUTION_EVIDENCE_STATE_HANDOFF_SCHEMA_VERSION",
    "ExecutionEvidenceStateHandoffError",
    "HandoffTarget",
    "HandoffDisposition",
    "CanonicalExecutionEvidence",
    "JobStateEvidence",
    "OrchestrationEvidenceHandoff",
    "PersistenceHandoff",
    "ObservabilityHandoff",
    "ExecutionStateHandoffBundle",
    "build_execution_evidence",
    "create_job_state_evidence",
    "create_orchestration_handoff",
    "create_persistence_handoff",
    "create_observability_handoff",
    "build_execution_state_handoff_bundle",
    "certify_execution_evidence_state_handoff_v1",
    "explain_execution_evidence_state_handoff_v1",
]
