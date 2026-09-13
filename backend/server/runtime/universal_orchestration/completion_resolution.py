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
)

from backend.server.runtime.universal_orchestration.progress_tracking import (
    UniversalOrchestrationProgressSnapshot,
)


UNIVERSAL_ORCHESTRATION_COMPLETION_RESOLUTION_VERSION: Final[str] = (
    "universal_orchestration_completion_resolution_v5.1.15"
)

UNIVERSAL_ORCHESTRATION_COMPLETION_RESOLUTION_SCHEMA_VERSION: Final[str] = (
    "universal_orchestration_completion_resolution_schema_v1"
)

UNIVERSAL_ORCHESTRATION_COMPLETION_DECISION_HASH_ALGORITHM: Final[str] = (
    "sha256"
)


class UniversalOrchestrationCompletionError(
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


class UniversalOrchestrationCompletionDisposition(
    str,
    enum.Enum,
):

    NOT_READY = "not_ready"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    UNRESOLVED = "unresolved"
    DEFERRED_TO_TERMINATION = "deferred_to_termination"


class UniversalOrchestrationCompletionReason(
    str,
    enum.Enum,
):

    TERMINAL_ORCHESTRATION_SUCCEEDED = (
        "terminal_orchestration_succeeded"
    )

    TERMINAL_ORCHESTRATION_FAILED = (
        "terminal_orchestration_failed"
    )

    TERMINAL_ORCHESTRATION_CANCELLED = (
        "terminal_orchestration_cancelled"
    )

    MISSING_STATUS_EVIDENCE = (
        "missing_status_evidence"
    )

    UNRESOLVED_BRANCH_ACTIVITY = (
        "unresolved_branch_activity"
    )

    NO_EFFECTIVE_WORK = (
        "no_effective_work"
    )

    CANCELLED_EFFECTIVE_WORK = (
        "cancelled_effective_work"
    )

    NONTERMINAL_EFFECTIVE_WORK = (
        "nonterminal_effective_work"
    )

    ALL_EFFECTIVE_WORK_SUCCEEDED = (
        "all_effective_work_succeeded"
    )

    TERMINAL_UNSUCCESSFUL_EFFECTIVE_WORK = (
        "terminal_unsuccessful_effective_work"
    )


_NONTERMINAL_STATUS_VALUES: Final[
    frozenset[str]
] = frozenset(
    {
        "created",
        "queued",
        "scheduled",
        "leased",
        "running",
        "suspended",
    }
)


_SUCCESS_STATUS_VALUES: Final[
    frozenset[str]
] = frozenset(
    {
        "succeeded",
    }
)


_FAILURE_STATUS_VALUES: Final[
    frozenset[str]
] = frozenset(
    {
        "failed",
        "dead_letter",
        "expired",
    }
)


_CANCELLED_STATUS_VALUES: Final[
    frozenset[str]
] = frozenset(
    {
        "cancelled",
    }
)


def _require_state_snapshot(
    value: Any,
) -> UniversalOrchestrationStateSnapshot:

    if not isinstance(
        value,
        UniversalOrchestrationStateSnapshot,
    ):

        raise UniversalOrchestrationCompletionError(
            (
                "state_snapshot must be a "
                "UniversalOrchestrationStateSnapshot."
            ),
            code="invalid_completion_state_snapshot",
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

        raise UniversalOrchestrationCompletionError(
            (
                "progress_snapshot must be a "
                "UniversalOrchestrationProgressSnapshot."
            ),
            code="invalid_completion_progress_snapshot",
            value=value,
        )

    return value


def _identity_fingerprint(
    identity: Any,
) -> str:

    value = getattr(
        identity,
        "identity_fingerprint",
        None,
    )

    if (
        not isinstance(
            value,
            str,
        )
        or
        not value.strip()
    ):

        raise UniversalOrchestrationCompletionError(
            "Orchestration identity fingerprint is invalid.",
            code="invalid_completion_identity_fingerprint",
            value=value,
        )

    return (
        value
        .strip()
        .upper()
    )


def _validate_identity_alignment(
    *,
    state_snapshot: UniversalOrchestrationStateSnapshot,
    progress_snapshot: UniversalOrchestrationProgressSnapshot,
) -> None:

    state_identity = (
        _identity_fingerprint(
            state_snapshot.identity
        )
    )

    progress_identity = (
        _identity_fingerprint(
            progress_snapshot.identity
        )
    )

    if state_identity != progress_identity:

        raise UniversalOrchestrationCompletionError(
            (
                "state_snapshot and progress_snapshot must "
                "belong to the same orchestration identity."
            ),
            code="completion_identity_mismatch",
            value=(
                state_identity,
                progress_identity,
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

    raise UniversalOrchestrationCompletionError(
        "Canonical completion status evidence is invalid.",
        code="invalid_completion_status_evidence",
        value=value,
    )


def _effective_status_pairs(
    progress_snapshot: UniversalOrchestrationProgressSnapshot,
) -> tuple[
    tuple[
        str,
        str | None,
    ],
    ...,
]:

    status_map = (
        progress_snapshot.status_evidence_map
    )

    return tuple(
        (
            job_id,
            _status_value(
                status_map[
                    job_id
                ]
            ),
        )
        for job_id
        in progress_snapshot.possible_effective_job_ids
    )


def _job_ids_with_statuses(
    *,
    progress_snapshot: UniversalOrchestrationProgressSnapshot,
    statuses: frozenset[str],
) -> tuple[str, ...]:

    return tuple(
        job_id
        for job_id, status
        in _effective_status_pairs(
            progress_snapshot
        )
        if status in statuses
    )


def _evaluate_completion(
    *,
    state_snapshot: UniversalOrchestrationStateSnapshot,
    progress_snapshot: UniversalOrchestrationProgressSnapshot,
) -> tuple[
    UniversalOrchestrationCompletionDisposition,
    UniversalOrchestrationCompletionReason,
]:

    state = (
        state_snapshot.state
    )

    if (
        state
        is
        UniversalOrchestrationState.SUCCEEDED
    ):

        return (
            UniversalOrchestrationCompletionDisposition.SUCCEEDED,
            UniversalOrchestrationCompletionReason.TERMINAL_ORCHESTRATION_SUCCEEDED,
        )

    if (
        state
        is
        UniversalOrchestrationState.FAILED
    ):

        return (
            UniversalOrchestrationCompletionDisposition.FAILED,
            UniversalOrchestrationCompletionReason.TERMINAL_ORCHESTRATION_FAILED,
        )

    if (
        state
        is
        UniversalOrchestrationState.CANCELLED
    ):

        return (
            UniversalOrchestrationCompletionDisposition.DEFERRED_TO_TERMINATION,
            UniversalOrchestrationCompletionReason.TERMINAL_ORCHESTRATION_CANCELLED,
        )

    if progress_snapshot.has_missing_status_evidence:

        return (
            UniversalOrchestrationCompletionDisposition.UNRESOLVED,
            UniversalOrchestrationCompletionReason.MISSING_STATUS_EVIDENCE,
        )

    if progress_snapshot.has_unresolved_branch_activity:

        return (
            UniversalOrchestrationCompletionDisposition.UNRESOLVED,
            UniversalOrchestrationCompletionReason.UNRESOLVED_BRANCH_ACTIVITY,
        )

    if (
        progress_snapshot.possible_effective_job_count
        == 0
    ):

        return (
            UniversalOrchestrationCompletionDisposition.NOT_READY,
            UniversalOrchestrationCompletionReason.NO_EFFECTIVE_WORK,
        )

    cancelled_job_ids = (
        _job_ids_with_statuses(
            progress_snapshot=progress_snapshot,
            statuses=_CANCELLED_STATUS_VALUES,
        )
    )

    if cancelled_job_ids:

        return (
            UniversalOrchestrationCompletionDisposition.DEFERRED_TO_TERMINATION,
            UniversalOrchestrationCompletionReason.CANCELLED_EFFECTIVE_WORK,
        )

    nonterminal_job_ids = (
        _job_ids_with_statuses(
            progress_snapshot=progress_snapshot,
            statuses=_NONTERMINAL_STATUS_VALUES,
        )
    )

    if nonterminal_job_ids:

        return (
            UniversalOrchestrationCompletionDisposition.NOT_READY,
            UniversalOrchestrationCompletionReason.NONTERMINAL_EFFECTIVE_WORK,
        )

    success_job_ids = (
        _job_ids_with_statuses(
            progress_snapshot=progress_snapshot,
            statuses=_SUCCESS_STATUS_VALUES,
        )
    )

    if (
        len(
            success_job_ids
        )
        ==
        progress_snapshot.possible_effective_job_count
    ):

        return (
            UniversalOrchestrationCompletionDisposition.SUCCEEDED,
            UniversalOrchestrationCompletionReason.ALL_EFFECTIVE_WORK_SUCCEEDED,
        )

    failure_job_ids = (
        _job_ids_with_statuses(
            progress_snapshot=progress_snapshot,
            statuses=_FAILURE_STATUS_VALUES,
        )
    )

    if failure_job_ids:

        return (
            UniversalOrchestrationCompletionDisposition.FAILED,
            UniversalOrchestrationCompletionReason.TERMINAL_UNSUCCESSFUL_EFFECTIVE_WORK,
        )

    return (
        UniversalOrchestrationCompletionDisposition.UNRESOLVED,
        UniversalOrchestrationCompletionReason.MISSING_STATUS_EVIDENCE,
    )


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalOrchestrationCompletionDecision:

    state_snapshot: UniversalOrchestrationStateSnapshot

    progress_snapshot: UniversalOrchestrationProgressSnapshot

    schema_version: str = (
        UNIVERSAL_ORCHESTRATION_COMPLETION_RESOLUTION_SCHEMA_VERSION
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
            UNIVERSAL_ORCHESTRATION_COMPLETION_RESOLUTION_SCHEMA_VERSION
        ):

            raise UniversalOrchestrationCompletionError(
                "Invalid completion-resolution schema_version.",
                code="invalid_completion_schema_version",
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
    ) -> UniversalOrchestrationCompletionDisposition:

        disposition, _ = (
            _evaluate_completion(
                state_snapshot=self.state_snapshot,
                progress_snapshot=self.progress_snapshot,
            )
        )

        return disposition

    @property
    def reason(
        self,
    ) -> UniversalOrchestrationCompletionReason:

        _, reason = (
            _evaluate_completion(
                state_snapshot=self.state_snapshot,
                progress_snapshot=self.progress_snapshot,
            )
        )

        return reason

    @property
    def nonterminal_effective_job_ids(
        self,
    ) -> tuple[str, ...]:

        return (
            _job_ids_with_statuses(
                progress_snapshot=self.progress_snapshot,
                statuses=_NONTERMINAL_STATUS_VALUES,
            )
        )

    @property
    def succeeded_effective_job_ids(
        self,
    ) -> tuple[str, ...]:

        return (
            _job_ids_with_statuses(
                progress_snapshot=self.progress_snapshot,
                statuses=_SUCCESS_STATUS_VALUES,
            )
        )

    @property
    def failed_effective_job_ids(
        self,
    ) -> tuple[str, ...]:

        return (
            _job_ids_with_statuses(
                progress_snapshot=self.progress_snapshot,
                statuses=_FAILURE_STATUS_VALUES,
            )
        )

    @property
    def cancelled_effective_job_ids(
        self,
    ) -> tuple[str, ...]:

        return (
            _job_ids_with_statuses(
                progress_snapshot=self.progress_snapshot,
                statuses=_CANCELLED_STATUS_VALUES,
            )
        )

    @property
    def target_terminal_state(
        self,
    ) -> UniversalOrchestrationState | None:

        if (
            self.disposition
            is
            UniversalOrchestrationCompletionDisposition.SUCCEEDED
        ):

            return (
                UniversalOrchestrationState.SUCCEEDED
            )

        if (
            self.disposition
            is
            UniversalOrchestrationCompletionDisposition.FAILED
        ):

            return (
                UniversalOrchestrationState.FAILED
            )

        return None

    @property
    def is_complete(
        self,
    ) -> bool:

        return (
            self.disposition
            in (
                UniversalOrchestrationCompletionDisposition.SUCCEEDED,
                UniversalOrchestrationCompletionDisposition.FAILED,
            )
        )

    @property
    def is_successful(
        self,
    ) -> bool:

        return (
            self.disposition
            is
            UniversalOrchestrationCompletionDisposition.SUCCEEDED
        )

    @property
    def is_failed(
        self,
    ) -> bool:

        return (
            self.disposition
            is
            UniversalOrchestrationCompletionDisposition.FAILED
        )

    @property
    def is_unresolved(
        self,
    ) -> bool:

        return (
            self.disposition
            is
            UniversalOrchestrationCompletionDisposition.UNRESOLVED
        )

    @property
    def is_deferred_to_termination(
        self,
    ) -> bool:

        return (
            self.disposition
            is
            UniversalOrchestrationCompletionDisposition.DEFERRED_TO_TERMINATION
        )

    @property
    def is_target_state_already_realized(
        self,
    ) -> bool:

        target = (
            self.target_terminal_state
        )

        return (
            target is not None
            and
            target is self.orchestration_state
        )

    @property
    def may_transition_to_target(
        self,
    ) -> bool:

        target = (
            self.target_terminal_state
        )

        if target is None:

            return False

        if (
            target
            is
            self.orchestration_state
        ):

            return False

        return (
            can_transition_universal_orchestration_state(
                current_state=self.orchestration_state,
                target_state=target,
            )
        )

    @property
    def completion_decision_id(
        self,
    ) -> str:

        material = "|".join(
            (
                "universal_orchestration_completion_decision_v1",
                _identity_fingerprint(
                    self.identity
                ),
                self.orchestration_state.value,
                self.progress_snapshot.progress_snapshot_id,
            )
        )

        return hashlib.sha256(
            material.encode(
                "utf-8"
            )
        ).hexdigest().upper()


def resolve_universal_orchestration_completion(
    *,
    state_snapshot: Any,
    progress_snapshot: Any,
) -> UniversalOrchestrationCompletionDecision:

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
        UniversalOrchestrationCompletionDecision(
            state_snapshot=state,
            progress_snapshot=progress,
        )
    )


def explain_universal_orchestration_completion_resolution_v1(
) -> Mapping[
    str,
    Any,
]:

    return MappingProxyType(
        {
            "phase":
                "5.1.15",

            "component":
                "Universal Orchestration Completion Resolution",

            "version":
                UNIVERSAL_ORCHESTRATION_COMPLETION_RESOLUTION_VERSION,

            "schema_version":
                UNIVERSAL_ORCHESTRATION_COMPLETION_RESOLUTION_SCHEMA_VERSION,

            "stored_fields": (
                "state_snapshot",
                "progress_snapshot",
                "schema_version",
            ),

            "state_authority": (
                "Frozen 5.1.3 supplies orchestration lifecycle "
                "state and terminal-transition legality."
            ),

            "progress_authority": (
                "Frozen 5.1.11 supplies possible-effective work, "
                "status evidence and conditional-branch resolution."
            ),

            "effective_population_rule": (
                "Only 5.1.11 possible-effective jobs participate "
                "in completion; excluded structural work does not."
            ),

            "success_rule": (
                "A nonempty possible-effective population resolves "
                "SUCCEEDED only when every effective job is SUCCEEDED."
            ),

            "failure_rule": (
                "After all effective work is terminal, FAILED, "
                "DEAD_LETTER or EXPIRED effective work resolves "
                "the orchestration completion outcome as FAILED."
            ),

            "cancellation_boundary": (
                "CANCELLED effective work is deferred to 5.1.16 "
                "and is never converted into FAILED by 5.1.15."
            ),

            "recovery_boundary": (
                "5.1.15 does not import, reevaluate or execute "
                "5.1.13 recovery. Recovery eligibility and final "
                "execution completion answer different questions."
            ),

            "transition_boundary": (
                "5.1.15 derives SUCCEEDED/FAILED target state and "
                "5.1.3 transition legality but performs no transition."
            ),

            "persistence_boundary": (
                "5.1.14 owns the orchestration persistence interface; "
                "5.1.15 performs no persistence."
            ),

            "termination_boundary": (
                "5.1.16 owns cancellation and termination resolution."
            ),

            "evidence_boundary": (
                "5.1.17 owns permanent completion decision records."
            ),

            "prohibitions": (
                "does not transition orchestration state",
                "does not target CANCELLED",
                "does not reopen terminal orchestration states",
                "does not import orchestration recovery",
                "does not reevaluate orchestration recovery",
                "does not execute recovery",
                "does not inspect retry attempts",
                "does not inspect retry policy",
                "does not calculate retry backoff",
                "does not recompute conditional branches",
                "does not recompute progress",
                "does not invoke persistence port",
                "does not access Runtime State Store",
                "does not persist completion decisions",
                "does not record permanent audit evidence",
                "does not cancel orchestration",
                "does not terminate orchestration",
                "does not enqueue jobs",
                "does not dequeue jobs",
                "does not claim jobs",
                "does not assign workers",
                "does not manipulate leases",
                "does not dispatch runtime handlers",
                "does not execute jobs",
                "does not use wall clock",
                "does not perform filesystem I/O",
                "does not perform database I/O",
                "does not perform network I/O",
                "does not import Universal Coordination Framework",
                "does not invoke pipeline coordinators",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_ORCHESTRATION_COMPLETION_RESOLUTION_VERSION",
    "UNIVERSAL_ORCHESTRATION_COMPLETION_RESOLUTION_SCHEMA_VERSION",
    "UNIVERSAL_ORCHESTRATION_COMPLETION_DECISION_HASH_ALGORITHM",
    "UniversalOrchestrationCompletionError",
    "UniversalOrchestrationCompletionDisposition",
    "UniversalOrchestrationCompletionReason",
    "UniversalOrchestrationCompletionDecision",
    "resolve_universal_orchestration_completion",
    "explain_universal_orchestration_completion_resolution_v1",
]
