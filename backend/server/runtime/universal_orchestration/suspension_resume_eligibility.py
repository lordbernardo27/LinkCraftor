from __future__ import annotations

import enum
import hashlib

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Final, Mapping

from backend.server.runtime.universal_orchestration.state_model import (
    UniversalOrchestrationState,
    UniversalOrchestrationStateSnapshot,
    can_transition_universal_orchestration_state,
    is_terminal_universal_orchestration_state,
)

from backend.server.runtime.universal_orchestration.progress_tracking import (
    UniversalOrchestrationProgressSnapshot,
)


UNIVERSAL_ORCHESTRATION_SUSPENSION_RESUME_ELIGIBILITY_VERSION: Final[str] = (
    "universal_orchestration_suspension_resume_eligibility_v5.1.12"
)

UNIVERSAL_ORCHESTRATION_SUSPENSION_RESUME_ELIGIBILITY_SCHEMA_VERSION: Final[str] = (
    "universal_orchestration_suspension_resume_eligibility_schema_v1"
)

UNIVERSAL_ORCHESTRATION_SUSPENSION_RESUME_DECISION_HASH_ALGORITHM: Final[str] = (
    "sha256"
)


class UniversalOrchestrationSuspensionResumeEligibilityError(
    ValueError
):

    def __init__(
        self,
        message: str,
        *,
        code: str,
        value: Any = None,
    ) -> None:

        super().__init__(
            message
        )

        self.code = str(
            code
        )

        self.value = value


class UniversalOrchestrationSuspensionDisposition(
    str,
    enum.Enum,
):

    ELIGIBLE = "eligible"
    DEFERRED = "deferred"
    INELIGIBLE = "ineligible"
    UNRESOLVED = "unresolved"


class UniversalOrchestrationResumeDisposition(
    str,
    enum.Enum,
):

    ELIGIBLE = "eligible"
    INELIGIBLE = "ineligible"
    UNRESOLVED = "unresolved"


class UniversalOrchestrationSuspensionReason(
    str,
    enum.Enum,
):

    TERMINAL_ORCHESTRATION = "terminal_orchestration"
    ALREADY_SUSPENDED = "already_suspended"
    STATE_CANNOT_SUSPEND = "state_cannot_suspend"

    NO_EFFECTIVE_WORK = "no_effective_work"
    ALL_EFFECTIVE_WORK_TERMINAL = "all_effective_work_terminal"

    MISSING_STATUS_EVIDENCE = "missing_status_evidence"
    UNRESOLVED_BRANCH_ACTIVITY = "unresolved_branch_activity"

    ACTIVE_EXECUTION_PRESENT = "active_execution_present"

    QUIESCENT_AND_SUSPENDABLE = "quiescent_and_suspendable"


class UniversalOrchestrationResumeReason(
    str,
    enum.Enum,
):

    TERMINAL_ORCHESTRATION = "terminal_orchestration"
    ORCHESTRATION_NOT_SUSPENDED = "orchestration_not_suspended"

    NO_EFFECTIVE_WORK = "no_effective_work"
    ALL_EFFECTIVE_WORK_TERMINAL = "all_effective_work_terminal"

    MISSING_STATUS_EVIDENCE = "missing_status_evidence"
    UNRESOLVED_BRANCH_ACTIVITY = "unresolved_branch_activity"

    ACTIVE_EXECUTION_CONTRADICTION = "active_execution_contradiction"

    SUSPENDED_AND_RESUMABLE = "suspended_and_resumable"


def _require_state_snapshot(
    value: Any,
) -> UniversalOrchestrationStateSnapshot:

    if not isinstance(
        value,
        UniversalOrchestrationStateSnapshot,
    ):

        raise UniversalOrchestrationSuspensionResumeEligibilityError(
            (
                "state_snapshot must be a "
                "UniversalOrchestrationStateSnapshot."
            ),
            code="invalid_suspension_resume_state_snapshot",
            value=value,
        )

    return value


def _require_progress_snapshot(
    value: Any,
) -> UniversalOrchestrationProgressSnapshot:

    if not isinstance(
        value,
        UniversalOrchestrationProgressSnapshot,
    ):

        raise UniversalOrchestrationSuspensionResumeEligibilityError(
            (
                "progress_snapshot must be a "
                "UniversalOrchestrationProgressSnapshot."
            ),
            code="invalid_suspension_resume_progress_snapshot",
            value=value,
        )

    return value


def _identity_fingerprint(
    value: Any,
) -> str:

    fingerprint = getattr(
        value,
        "identity_fingerprint",
        None,
    )

    if (
        not isinstance(
            fingerprint,
            str,
        )
        or
        not fingerprint
    ):

        raise UniversalOrchestrationSuspensionResumeEligibilityError(
            "Orchestration identity fingerprint is invalid.",
            code="invalid_suspension_resume_identity_fingerprint",
            value=fingerprint,
        )

    return fingerprint


def _validate_identity_alignment(
    *,
    state_snapshot: UniversalOrchestrationStateSnapshot,
    progress_snapshot: UniversalOrchestrationProgressSnapshot,
) -> None:

    state_fingerprint = (
        _identity_fingerprint(
            state_snapshot.identity
        )
    )

    progress_fingerprint = (
        _identity_fingerprint(
            progress_snapshot.identity
        )
    )

    if state_fingerprint != progress_fingerprint:

        raise UniversalOrchestrationSuspensionResumeEligibilityError(
            (
                "state_snapshot and progress_snapshot must belong "
                "to the same orchestration identity."
            ),
            code="suspension_resume_identity_mismatch",
            value=(
                state_fingerprint,
                progress_fingerprint,
            ),
        )


def _all_possible_effective_work_terminal(
    progress_snapshot: UniversalOrchestrationProgressSnapshot,
) -> bool:

    possible_count = (
        progress_snapshot.possible_effective_job_count
    )

    if possible_count == 0:

        return False

    return (
        progress_snapshot.terminal_job_count
        ==
        possible_count
    )


def _evaluate_suspension(
    *,
    state_snapshot: UniversalOrchestrationStateSnapshot,
    progress_snapshot: UniversalOrchestrationProgressSnapshot,
) -> tuple[
    UniversalOrchestrationSuspensionDisposition,
    UniversalOrchestrationSuspensionReason,
]:

    state = (
        state_snapshot.state
    )

    if is_terminal_universal_orchestration_state(
        state
    ):

        return (
            UniversalOrchestrationSuspensionDisposition.INELIGIBLE,
            UniversalOrchestrationSuspensionReason.TERMINAL_ORCHESTRATION,
        )

    if state is UniversalOrchestrationState.SUSPENDED:

        return (
            UniversalOrchestrationSuspensionDisposition.INELIGIBLE,
            UniversalOrchestrationSuspensionReason.ALREADY_SUSPENDED,
        )

    if not can_transition_universal_orchestration_state(
        current_state=state,
        target_state=UniversalOrchestrationState.SUSPENDED,
    ):

        return (
            UniversalOrchestrationSuspensionDisposition.INELIGIBLE,
            UniversalOrchestrationSuspensionReason.STATE_CANNOT_SUSPEND,
        )

    if progress_snapshot.possible_effective_job_count == 0:

        return (
            UniversalOrchestrationSuspensionDisposition.INELIGIBLE,
            UniversalOrchestrationSuspensionReason.NO_EFFECTIVE_WORK,
        )

    if _all_possible_effective_work_terminal(
        progress_snapshot
    ):

        return (
            UniversalOrchestrationSuspensionDisposition.INELIGIBLE,
            UniversalOrchestrationSuspensionReason.ALL_EFFECTIVE_WORK_TERMINAL,
        )

    if progress_snapshot.has_missing_status_evidence:

        return (
            UniversalOrchestrationSuspensionDisposition.UNRESOLVED,
            UniversalOrchestrationSuspensionReason.MISSING_STATUS_EVIDENCE,
        )

    if progress_snapshot.has_unresolved_branch_activity:

        return (
            UniversalOrchestrationSuspensionDisposition.UNRESOLVED,
            UniversalOrchestrationSuspensionReason.UNRESOLVED_BRANCH_ACTIVITY,
        )

    if progress_snapshot.in_progress_job_ids:

        return (
            UniversalOrchestrationSuspensionDisposition.DEFERRED,
            UniversalOrchestrationSuspensionReason.ACTIVE_EXECUTION_PRESENT,
        )

    return (
        UniversalOrchestrationSuspensionDisposition.ELIGIBLE,
        UniversalOrchestrationSuspensionReason.QUIESCENT_AND_SUSPENDABLE,
    )


def _evaluate_resume(
    *,
    state_snapshot: UniversalOrchestrationStateSnapshot,
    progress_snapshot: UniversalOrchestrationProgressSnapshot,
) -> tuple[
    UniversalOrchestrationResumeDisposition,
    UniversalOrchestrationResumeReason,
]:

    state = (
        state_snapshot.state
    )

    if is_terminal_universal_orchestration_state(
        state
    ):

        return (
            UniversalOrchestrationResumeDisposition.INELIGIBLE,
            UniversalOrchestrationResumeReason.TERMINAL_ORCHESTRATION,
        )

    if state is not UniversalOrchestrationState.SUSPENDED:

        return (
            UniversalOrchestrationResumeDisposition.INELIGIBLE,
            UniversalOrchestrationResumeReason.ORCHESTRATION_NOT_SUSPENDED,
        )

    if progress_snapshot.possible_effective_job_count == 0:

        return (
            UniversalOrchestrationResumeDisposition.INELIGIBLE,
            UniversalOrchestrationResumeReason.NO_EFFECTIVE_WORK,
        )

    if _all_possible_effective_work_terminal(
        progress_snapshot
    ):

        return (
            UniversalOrchestrationResumeDisposition.INELIGIBLE,
            UniversalOrchestrationResumeReason.ALL_EFFECTIVE_WORK_TERMINAL,
        )

    if progress_snapshot.has_missing_status_evidence:

        return (
            UniversalOrchestrationResumeDisposition.UNRESOLVED,
            UniversalOrchestrationResumeReason.MISSING_STATUS_EVIDENCE,
        )

    if progress_snapshot.has_unresolved_branch_activity:

        return (
            UniversalOrchestrationResumeDisposition.UNRESOLVED,
            UniversalOrchestrationResumeReason.UNRESOLVED_BRANCH_ACTIVITY,
        )

    if progress_snapshot.in_progress_job_ids:

        return (
            UniversalOrchestrationResumeDisposition.UNRESOLVED,
            UniversalOrchestrationResumeReason.ACTIVE_EXECUTION_CONTRADICTION,
        )

    return (
        UniversalOrchestrationResumeDisposition.ELIGIBLE,
        UniversalOrchestrationResumeReason.SUSPENDED_AND_RESUMABLE,
    )


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalOrchestrationSuspensionResumeEligibility:

    state_snapshot: UniversalOrchestrationStateSnapshot

    progress_snapshot: UniversalOrchestrationProgressSnapshot

    schema_version: str = (
        UNIVERSAL_ORCHESTRATION_SUSPENSION_RESUME_ELIGIBILITY_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        state_snapshot = (
            _require_state_snapshot(
                self.state_snapshot
            )
        )

        progress_snapshot = (
            _require_progress_snapshot(
                self.progress_snapshot
            )
        )

        _validate_identity_alignment(
            state_snapshot=state_snapshot,
            progress_snapshot=progress_snapshot,
        )

        if (
            self.schema_version
            !=
            UNIVERSAL_ORCHESTRATION_SUSPENSION_RESUME_ELIGIBILITY_SCHEMA_VERSION
        ):

            raise UniversalOrchestrationSuspensionResumeEligibilityError(
                "Invalid suspension/resume eligibility schema_version.",
                code="invalid_suspension_resume_schema_version",
                value=self.schema_version,
            )

    @property
    def identity(
        self,
    ):

        return (
            self.progress_snapshot.identity
        )

    @property
    def orchestration_state(
        self,
    ) -> UniversalOrchestrationState:

        return (
            self.state_snapshot.state
        )

    @property
    def suspension_disposition(
        self,
    ) -> UniversalOrchestrationSuspensionDisposition:

        disposition, _ = (
            _evaluate_suspension(
                state_snapshot=self.state_snapshot,
                progress_snapshot=self.progress_snapshot,
            )
        )

        return disposition

    @property
    def suspension_reason(
        self,
    ) -> UniversalOrchestrationSuspensionReason:

        _, reason = (
            _evaluate_suspension(
                state_snapshot=self.state_snapshot,
                progress_snapshot=self.progress_snapshot,
            )
        )

        return reason

    @property
    def resume_disposition(
        self,
    ) -> UniversalOrchestrationResumeDisposition:

        disposition, _ = (
            _evaluate_resume(
                state_snapshot=self.state_snapshot,
                progress_snapshot=self.progress_snapshot,
            )
        )

        return disposition

    @property
    def resume_reason(
        self,
    ) -> UniversalOrchestrationResumeReason:

        _, reason = (
            _evaluate_resume(
                state_snapshot=self.state_snapshot,
                progress_snapshot=self.progress_snapshot,
            )
        )

        return reason

    @property
    def is_suspend_eligible(
        self,
    ) -> bool:

        return (
            self.suspension_disposition
            is
            UniversalOrchestrationSuspensionDisposition.ELIGIBLE
        )

    @property
    def is_suspend_deferred(
        self,
    ) -> bool:

        return (
            self.suspension_disposition
            is
            UniversalOrchestrationSuspensionDisposition.DEFERRED
        )

    @property
    def is_suspend_unresolved(
        self,
    ) -> bool:

        return (
            self.suspension_disposition
            is
            UniversalOrchestrationSuspensionDisposition.UNRESOLVED
        )

    @property
    def is_resume_eligible(
        self,
    ) -> bool:

        return (
            self.resume_disposition
            is
            UniversalOrchestrationResumeDisposition.ELIGIBLE
        )

    @property
    def is_resume_unresolved(
        self,
    ) -> bool:

        return (
            self.resume_disposition
            is
            UniversalOrchestrationResumeDisposition.UNRESOLVED
        )

    @property
    def blocking_job_ids(
        self,
    ) -> tuple[str, ...]:

        if self.is_suspend_deferred:

            return (
                self.progress_snapshot.in_progress_job_ids
            )

        if (
            self.resume_reason
            is
            UniversalOrchestrationResumeReason.ACTIVE_EXECUTION_CONTRADICTION
        ):

            return (
                self.progress_snapshot.in_progress_job_ids
            )

        return ()

    @property
    def missing_status_job_ids(
        self,
    ) -> tuple[str, ...]:

        return (
            self.progress_snapshot.missing_status_job_ids
        )

    @property
    def unresolved_effective_job_ids(
        self,
    ) -> tuple[str, ...]:

        return (
            self.progress_snapshot.unresolved_effective_job_ids
        )

    @property
    def in_progress_job_ids(
        self,
    ) -> tuple[str, ...]:

        return (
            self.progress_snapshot.in_progress_job_ids
        )

    @property
    def suspended_job_ids(
        self,
    ) -> tuple[str, ...]:

        return (
            self.progress_snapshot.suspended_job_ids
        )

    @property
    def eligibility_decision_id(
        self,
    ) -> str:

        material = "|".join(
            (
                "universal_orchestration_suspension_resume_eligibility_v1",
                self.identity.identity_fingerprint,
                self.orchestration_state.value,
                self.progress_snapshot.progress_snapshot_id,
            )
        )

        return hashlib.sha256(
            material.encode(
                "utf-8"
            )
        ).hexdigest().upper()


def evaluate_universal_orchestration_suspension_resume_eligibility(
    *,
    state_snapshot: Any,
    progress_snapshot: Any,
) -> UniversalOrchestrationSuspensionResumeEligibility:

    state = (
        _require_state_snapshot(
            state_snapshot
        )
    )

    progress = (
        _require_progress_snapshot(
            progress_snapshot
        )
    )

    return (
        UniversalOrchestrationSuspensionResumeEligibility(
            state_snapshot=state,
            progress_snapshot=progress,
        )
    )


def explain_universal_orchestration_suspension_resume_eligibility_v1(
) -> Mapping[
    str,
    Any,
]:

    return MappingProxyType(
        {
            "phase":
                "5.1.12",

            "component":
                "Universal Orchestration Suspension & Resume Eligibility",

            "version":
                UNIVERSAL_ORCHESTRATION_SUSPENSION_RESUME_ELIGIBILITY_VERSION,

            "schema_version":
                UNIVERSAL_ORCHESTRATION_SUSPENSION_RESUME_ELIGIBILITY_SCHEMA_VERSION,

            "stored_fields": (
                "state_snapshot",
                "progress_snapshot",
                "schema_version",
            ),

            "state_authority": (
                "Frozen 5.1.3 supplies orchestration lifecycle state "
                "and legal transition structure."
            ),

            "progress_authority": (
                "Frozen 5.1.11 supplies possible-effective work and "
                "normalized job-status evidence."
            ),

            "suspension_rule": (
                "Quiescent nonterminal effective work may be suspend "
                "eligible. LEASED/RUNNING effective work is DEFERRED "
                "because 5.1.12 does not checkpoint or pause execution."
            ),

            "resume_rule": (
                "Only an orchestration already in SUSPENDED may be "
                "resume eligible. Missing, unresolved, or contradictory "
                "active-execution evidence prevents a definitive "
                "resume-eligible decision."
            ),

            "terminal_rule": (
                "Terminal orchestration states and all-terminal "
                "effective work are not suspend/resume eligible; "
                "completion resolution belongs to 5.1.15."
            ),

            "checkpoint_boundary": (
                "Checkpoint save/restore and actual pause/resume "
                "execution belong to the later Execution/Pause-Resume "
                "authority, not 5.1.12."
            ),

            "recovery_boundary": (
                "5.1.13 owns orchestration recovery."
            ),

            "persistence_boundary": (
                "5.1.14 owns orchestration persistence."
            ),

            "completion_boundary": (
                "5.1.15 owns orchestration completion resolution."
            ),

            "termination_boundary": (
                "5.1.16 owns orchestration cancellation and "
                "termination resolution."
            ),

            "evidence_boundary": (
                "5.1.17 owns permanent orchestration evidence "
                "and decision records."
            ),

            "prohibitions": (
                "does not transition orchestration state",
                "does not suspend orchestration",
                "does not resume orchestration",
                "does not pause queues",
                "does not drain workers",
                "does not release leases",
                "does not acquire leases",
                "does not save checkpoints",
                "does not restore checkpoints",
                "does not read checkpoint payloads",
                "does not mutate UniversalJob.status",
                "does not mutate UniversalJob.progress",
                "does not evaluate stage readiness",
                "does not evaluate runtime handoff",
                "does not reevaluate conditional branches",
                "does not recompute progress topology",
                "does not enqueue jobs",
                "does not dequeue jobs",
                "does not claim jobs",
                "does not assign workers",
                "does not dispatch runtime handlers",
                "does not execute jobs",
                "does not initiate recovery",
                "does not access Runtime State Store",
                "does not persist eligibility decisions",
                "does not determine orchestration completion",
                "does not determine orchestration success",
                "does not determine orchestration failure",
                "does not cancel orchestration",
                "does not terminate orchestration",
                "does not record permanent evidence",
                "does not use wall clock",
                "does not perform filesystem I/O",
                "does not perform network I/O",
                "does not perform database I/O",
                "does not import Universal Coordination Framework",
                "does not invoke pipeline coordinators",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_ORCHESTRATION_SUSPENSION_RESUME_ELIGIBILITY_VERSION",
    "UNIVERSAL_ORCHESTRATION_SUSPENSION_RESUME_ELIGIBILITY_SCHEMA_VERSION",
    "UNIVERSAL_ORCHESTRATION_SUSPENSION_RESUME_DECISION_HASH_ALGORITHM",
    "UniversalOrchestrationSuspensionResumeEligibilityError",
    "UniversalOrchestrationSuspensionDisposition",
    "UniversalOrchestrationResumeDisposition",
    "UniversalOrchestrationSuspensionReason",
    "UniversalOrchestrationResumeReason",
    "UniversalOrchestrationSuspensionResumeEligibility",
    "evaluate_universal_orchestration_suspension_resume_eligibility",
    "explain_universal_orchestration_suspension_resume_eligibility_v1",
]

