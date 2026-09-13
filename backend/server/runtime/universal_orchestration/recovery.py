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


UNIVERSAL_ORCHESTRATION_RECOVERY_VERSION: Final[str] = (
    "universal_orchestration_recovery_v5.1.13"
)

UNIVERSAL_ORCHESTRATION_RECOVERY_SCHEMA_VERSION: Final[str] = (
    "universal_orchestration_recovery_schema_v1"
)

UNIVERSAL_ORCHESTRATION_RECOVERY_DECISION_HASH_ALGORITHM: Final[str] = (
    "sha256"
)


class UniversalOrchestrationRecoveryError(
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


class UniversalOrchestrationRecoveryDisposition(
    str,
    enum.Enum,
):

    NOT_REQUIRED = "not_required"
    RECOVERABLE = "recoverable"
    UNRECOVERABLE = "unrecoverable"
    UNRESOLVED = "unresolved"


class UniversalOrchestrationRecoveryReason(
    str,
    enum.Enum,
):

    TERMINAL_ORCHESTRATION = "terminal_orchestration"

    MISSING_STATUS_EVIDENCE = "missing_status_evidence"

    UNRESOLVED_BRANCH_ACTIVITY = (
        "unresolved_branch_activity"
    )

    CANCELLED_EFFECTIVE_WORK = (
        "cancelled_effective_work"
    )

    POLICY_DEPENDENT_TERMINAL_WORK = (
        "policy_dependent_terminal_work"
    )

    FAILED_EFFECTIVE_WORK = (
        "failed_effective_work"
    )

    NO_RECOVERY_REQUIRED = (
        "no_recovery_required"
    )


def _require_state_snapshot(
    value: Any,
) -> UniversalOrchestrationStateSnapshot:

    if not isinstance(
        value,
        UniversalOrchestrationStateSnapshot,
    ):

        raise UniversalOrchestrationRecoveryError(
            (
                "state_snapshot must be a "
                "UniversalOrchestrationStateSnapshot."
            ),
            code="invalid_orchestration_recovery_state_snapshot",
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

        raise UniversalOrchestrationRecoveryError(
            (
                "progress_snapshot must be a "
                "UniversalOrchestrationProgressSnapshot."
            ),
            code="invalid_orchestration_recovery_progress_snapshot",
            value=value,
        )

    return value


def _identity_fingerprint(
    identity: Any,
) -> str:

    fingerprint = getattr(
        identity,
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

        raise UniversalOrchestrationRecoveryError(
            "Orchestration identity fingerprint is invalid.",
            code="invalid_orchestration_recovery_identity_fingerprint",
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

    if (
        state_fingerprint
        !=
        progress_fingerprint
    ):

        raise UniversalOrchestrationRecoveryError(
            (
                "state_snapshot and progress_snapshot must "
                "belong to the same orchestration identity."
            ),
            code="orchestration_recovery_identity_mismatch",
            value=(
                state_fingerprint,
                progress_fingerprint,
            ),
        )


def _status_value(
    value: Any,
) -> str | None:

    if value is None:

        return None

    enum_value = getattr(
        value,
        "value",
        None,
    )

    if isinstance(
        enum_value,
        str,
    ):

        return (
            enum_value
            .strip()
            .lower()
        )

    if isinstance(
        value,
        str,
    ):

        return (
            value
            .strip()
            .lower()
        )

    raise UniversalOrchestrationRecoveryError(
        "Canonical progress status evidence is invalid.",
        code="invalid_orchestration_recovery_status_evidence",
        value=value,
    )


def _job_ids_with_statuses(
    *,
    progress_snapshot: UniversalOrchestrationProgressSnapshot,
    status_values: frozenset[str],
) -> tuple[str, ...]:

    status_map = (
        progress_snapshot.status_evidence_map
    )

    return tuple(
        job_id
        for job_id
        in progress_snapshot.possible_effective_job_ids
        if (
            _status_value(
                status_map[
                    job_id
                ]
            )
            in
            status_values
        )
    )


_FAILED_STATUS_VALUES: Final[
    frozenset[str]
] = frozenset(
    {
        "failed",
    }
)


_CANCELLED_STATUS_VALUES: Final[
    frozenset[str]
] = frozenset(
    {
        "cancelled",
    }
)


_POLICY_DEPENDENT_STATUS_VALUES: Final[
    frozenset[str]
] = frozenset(
    {
        "dead_letter",
        "expired",
    }
)


def _evaluate_recovery(
    *,
    state_snapshot: UniversalOrchestrationStateSnapshot,
    progress_snapshot: UniversalOrchestrationProgressSnapshot,
) -> tuple[
    UniversalOrchestrationRecoveryDisposition,
    UniversalOrchestrationRecoveryReason,
]:

    state = (
        state_snapshot.state
    )

    if is_terminal_universal_orchestration_state(
        state
    ):

        return (
            UniversalOrchestrationRecoveryDisposition.UNRECOVERABLE,
            UniversalOrchestrationRecoveryReason.TERMINAL_ORCHESTRATION,
        )

    if progress_snapshot.has_missing_status_evidence:

        return (
            UniversalOrchestrationRecoveryDisposition.UNRESOLVED,
            UniversalOrchestrationRecoveryReason.MISSING_STATUS_EVIDENCE,
        )

    if progress_snapshot.has_unresolved_branch_activity:

        return (
            UniversalOrchestrationRecoveryDisposition.UNRESOLVED,
            UniversalOrchestrationRecoveryReason.UNRESOLVED_BRANCH_ACTIVITY,
        )

    cancelled_job_ids = (
        _job_ids_with_statuses(
            progress_snapshot=progress_snapshot,
            status_values=_CANCELLED_STATUS_VALUES,
        )
    )

    if cancelled_job_ids:

        return (
            UniversalOrchestrationRecoveryDisposition.UNRECOVERABLE,
            UniversalOrchestrationRecoveryReason.CANCELLED_EFFECTIVE_WORK,
        )

    policy_dependent_job_ids = (
        _job_ids_with_statuses(
            progress_snapshot=progress_snapshot,
            status_values=_POLICY_DEPENDENT_STATUS_VALUES,
        )
    )

    if policy_dependent_job_ids:

        return (
            UniversalOrchestrationRecoveryDisposition.UNRESOLVED,
            UniversalOrchestrationRecoveryReason.POLICY_DEPENDENT_TERMINAL_WORK,
        )

    recovery_candidate_job_ids = (
        _job_ids_with_statuses(
            progress_snapshot=progress_snapshot,
            status_values=_FAILED_STATUS_VALUES,
        )
    )

    if recovery_candidate_job_ids:

        return (
            UniversalOrchestrationRecoveryDisposition.RECOVERABLE,
            UniversalOrchestrationRecoveryReason.FAILED_EFFECTIVE_WORK,
        )

    return (
        UniversalOrchestrationRecoveryDisposition.NOT_REQUIRED,
        UniversalOrchestrationRecoveryReason.NO_RECOVERY_REQUIRED,
    )


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalOrchestrationRecoveryDecision:

    state_snapshot: UniversalOrchestrationStateSnapshot

    progress_snapshot: UniversalOrchestrationProgressSnapshot

    schema_version: str = (
        UNIVERSAL_ORCHESTRATION_RECOVERY_SCHEMA_VERSION
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
            UNIVERSAL_ORCHESTRATION_RECOVERY_SCHEMA_VERSION
        ):

            raise UniversalOrchestrationRecoveryError(
                "Invalid orchestration recovery schema_version.",
                code="invalid_orchestration_recovery_schema_version",
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
    def disposition(
        self,
    ) -> UniversalOrchestrationRecoveryDisposition:

        disposition, _ = (
            _evaluate_recovery(
                state_snapshot=self.state_snapshot,
                progress_snapshot=self.progress_snapshot,
            )
        )

        return disposition

    @property
    def reason(
        self,
    ) -> UniversalOrchestrationRecoveryReason:

        _, reason = (
            _evaluate_recovery(
                state_snapshot=self.state_snapshot,
                progress_snapshot=self.progress_snapshot,
            )
        )

        return reason

    @property
    def recovery_candidate_job_ids(
        self,
    ) -> tuple[str, ...]:

        return (
            _job_ids_with_statuses(
                progress_snapshot=self.progress_snapshot,
                status_values=_FAILED_STATUS_VALUES,
            )
        )

    @property
    def cancelled_effective_job_ids(
        self,
    ) -> tuple[str, ...]:

        return (
            _job_ids_with_statuses(
                progress_snapshot=self.progress_snapshot,
                status_values=_CANCELLED_STATUS_VALUES,
            )
        )

    @property
    def policy_dependent_job_ids(
        self,
    ) -> tuple[str, ...]:

        return (
            _job_ids_with_statuses(
                progress_snapshot=self.progress_snapshot,
                status_values=_POLICY_DEPENDENT_STATUS_VALUES,
            )
        )

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
    def is_recovery_required(
        self,
    ) -> bool:

        return (
            self.disposition
            is
            UniversalOrchestrationRecoveryDisposition.RECOVERABLE
        )

    @property
    def is_unrecoverable(
        self,
    ) -> bool:

        return (
            self.disposition
            is
            UniversalOrchestrationRecoveryDisposition.UNRECOVERABLE
        )

    @property
    def is_unresolved(
        self,
    ) -> bool:

        return (
            self.disposition
            is
            UniversalOrchestrationRecoveryDisposition.UNRESOLVED
        )

    @property
    def is_recovery_not_required(
        self,
    ) -> bool:

        return (
            self.disposition
            is
            UniversalOrchestrationRecoveryDisposition.NOT_REQUIRED
        )

    @property
    def is_currently_recovering(
        self,
    ) -> bool:

        return (
            self.orchestration_state
            is
            UniversalOrchestrationState.RECOVERING
        )

    @property
    def may_enter_recovering(
        self,
    ) -> bool:

        if not self.is_recovery_required:

            return False

        if self.is_currently_recovering:

            return False

        return (
            can_transition_universal_orchestration_state(
                current_state=self.orchestration_state,
                target_state=UniversalOrchestrationState.RECOVERING,
            )
        )

    @property
    def recovery_decision_id(
        self,
    ) -> str:

        material = "|".join(
            (
                "universal_orchestration_recovery_decision_v1",
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


def evaluate_universal_orchestration_recovery(
    *,
    state_snapshot: Any,
    progress_snapshot: Any,
) -> UniversalOrchestrationRecoveryDecision:

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
        UniversalOrchestrationRecoveryDecision(
            state_snapshot=state,
            progress_snapshot=progress,
        )
    )


def explain_universal_orchestration_recovery_v1(
) -> Mapping[
    str,
    Any,
]:

    return MappingProxyType(
        {
            "phase":
                "5.1.13",

            "component":
                "Universal Orchestration Recovery",

            "version":
                UNIVERSAL_ORCHESTRATION_RECOVERY_VERSION,

            "schema_version":
                UNIVERSAL_ORCHESTRATION_RECOVERY_SCHEMA_VERSION,

            "stored_fields": (
                "state_snapshot",
                "progress_snapshot",
                "schema_version",
            ),

            "state_authority": (
                "Frozen 5.1.3 supplies orchestration lifecycle "
                "state and RECOVERING transition legality."
            ),

            "progress_authority": (
                "Frozen 5.1.11 supplies possible-effective work "
                "and normalized job-status evidence."
            ),

            "failed_rule": (
                "FAILED possible-effective jobs are canonical "
                "Phase-5 orchestration recovery candidates."
            ),

            "cancelled_rule": (
                "CANCELLED effective work is unrecoverable here; "
                "cancellation and termination resolution belongs "
                "to 5.1.16."
            ),

            "policy_dependent_rule": (
                "DEAD_LETTER and EXPIRED effective work are "
                "UNRESOLVED because retryability, attempts, and "
                "retry policy belong outside 5.1.13."
            ),

            "suspended_rule": (
                "SUSPENDED work is not classified as recovery "
                "failure; suspension/resume eligibility belongs "
                "to frozen 5.1.12."
            ),

            "terminal_orchestration_rule": (
                "Frozen terminal orchestration states are not "
                "reopened by 5.1.13."
            ),

            "recovering_rule": (
                "5.1.13 may describe recovery need while the "
                "orchestration is RECOVERING, but performs no "
                "state transition and executes no recovery."
            ),

            "execution_boundary": (
                "Actual retry, requeue, checkpoint restoration, "
                "handler execution, attempts, backoff, and retry "
                "scheduling remain outside 5.1.13."
            ),

            "worker_boundary": (
                "Phase 4 Worker Recovery remains worker-level "
                "authority and is not invoked by 5.1.13."
            ),

            "queue_boundary": (
                "Universal Queue Recovery remains queue-level "
                "authority and is not invoked by 5.1.13."
            ),

            "persistence_boundary": (
                "5.1.14 owns orchestration persistence."
            ),

            "completion_boundary": (
                "5.1.15 owns orchestration completion resolution."
            ),

            "termination_boundary": (
                "5.1.16 owns cancellation and termination "
                "resolution."
            ),

            "evidence_boundary": (
                "5.1.17 owns permanent orchestration evidence "
                "and decision records."
            ),

            "prohibitions": (
                "does not transition orchestration state",
                "does not reopen terminal orchestration states",
                "does not mutate UniversalJob.status",
                "does not mutate UniversalJob.progress",
                "does not calculate retry attempts",
                "does not enforce retry budgets",
                "does not calculate retry backoff",
                "does not schedule retries",
                "does not requeue jobs",
                "does not enqueue jobs",
                "does not dequeue jobs",
                "does not claim jobs",
                "does not invoke Queue Recovery",
                "does not invoke Worker Recovery",
                "does not restart workers",
                "does not assign workers",
                "does not acquire leases",
                "does not release leases",
                "does not restore checkpoints",
                "does not read checkpoint payloads",
                "does not dispatch runtime handlers",
                "does not execute jobs",
                "does not recompute dependency resolution",
                "does not evaluate stage readiness",
                "does not evaluate runtime handoff",
                "does not reevaluate conditional branches",
                "does not recompute progress topology",
                "does not access Runtime State Store",
                "does not persist recovery decisions",
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
    "UNIVERSAL_ORCHESTRATION_RECOVERY_VERSION",
    "UNIVERSAL_ORCHESTRATION_RECOVERY_SCHEMA_VERSION",
    "UNIVERSAL_ORCHESTRATION_RECOVERY_DECISION_HASH_ALGORITHM",
    "UniversalOrchestrationRecoveryError",
    "UniversalOrchestrationRecoveryDisposition",
    "UniversalOrchestrationRecoveryReason",
    "UniversalOrchestrationRecoveryDecision",
    "evaluate_universal_orchestration_recovery",
    "explain_universal_orchestration_recovery_v1",
]
