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


UNIVERSAL_ORCHESTRATION_CANCELLATION_TERMINATION_VERSION: Final[str] = (
    "universal_orchestration_cancellation_termination_v5.1.16"
)

UNIVERSAL_ORCHESTRATION_CANCELLATION_REQUEST_SCHEMA_VERSION: Final[str] = (
    "universal_orchestration_cancellation_request_schema_v1"
)

UNIVERSAL_ORCHESTRATION_CANCELLATION_DECISION_SCHEMA_VERSION: Final[str] = (
    "universal_orchestration_cancellation_decision_schema_v1"
)

UNIVERSAL_ORCHESTRATION_CANCELLATION_HASH_ALGORITHM: Final[str] = (
    "sha256"
)


class UniversalOrchestrationCancellationTerminationError(
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


class UniversalOrchestrationCancellationDisposition(
    str,
    enum.Enum,
):

    NOT_REQUESTED = "not_requested"

    WAITING_FOR_TERMINATION = (
        "waiting_for_termination"
    )

    ELIGIBLE = "eligible"

    ALREADY_CANCELLED = (
        "already_cancelled"
    )

    INELIGIBLE = "ineligible"

    UNRESOLVED = "unresolved"


class UniversalOrchestrationCancellationReason(
    str,
    enum.Enum,
):

    ALREADY_CANCELLED = (
        "already_cancelled"
    )

    TERMINAL_SUCCEEDED = (
        "terminal_succeeded"
    )

    TERMINAL_FAILED = (
        "terminal_failed"
    )

    NO_CANCELLATION_REQUEST = (
        "no_cancellation_request"
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

    NONTERMINAL_EFFECTIVE_WORK = (
        "nonterminal_effective_work"
    )

    CANCELLED_EFFECTIVE_WORK = (
        "cancelled_effective_work"
    )

    TERMINAL_WORK_WITHOUT_CANCELLATION_EVIDENCE = (
        "terminal_work_without_cancellation_evidence"
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


_TERMINAL_STATUS_VALUES: Final[
    frozenset[str]
] = frozenset(
    {
        "succeeded",
        "failed",
        "cancelled",
        "dead_letter",
        "expired",
    }
)


def _normalize_required_text(
    value: Any,
    *,
    field_name: str,
    code: str,
) -> str:

    if not isinstance(
        value,
        str,
    ):

        raise UniversalOrchestrationCancellationTerminationError(
            field_name
            + " must be a non-empty string.",
            code=code,
            value=value,
        )

    normalized = (
        value.strip()
    )

    if not normalized:

        raise UniversalOrchestrationCancellationTerminationError(
            field_name
            + " must be a non-empty string.",
            code=code,
            value=value,
        )

    return normalized


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

        raise UniversalOrchestrationCancellationTerminationError(
            "Orchestration identity fingerprint is invalid.",
            code="invalid_cancellation_identity_fingerprint",
            value=value,
        )

    return (
        value.strip().upper()
    )


def _require_state_snapshot(
    value: Any,
) -> UniversalOrchestrationStateSnapshot:

    if not isinstance(
        value,
        UniversalOrchestrationStateSnapshot,
    ):

        raise UniversalOrchestrationCancellationTerminationError(
            (
                "state_snapshot must be a "
                "UniversalOrchestrationStateSnapshot."
            ),
            code="invalid_cancellation_state_snapshot",
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

        raise UniversalOrchestrationCancellationTerminationError(
            (
                "progress_snapshot must be a "
                "UniversalOrchestrationProgressSnapshot."
            ),
            code="invalid_cancellation_progress_snapshot",
            value=value,
        )

    return value


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

        raise UniversalOrchestrationCancellationTerminationError(
            (
                "state_snapshot and progress_snapshot must "
                "belong to the same orchestration identity."
            ),
            code="cancellation_identity_mismatch",
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
            enum_value.strip().lower()
        )

    if isinstance(
        value,
        str,
    ):

        return (
            value.strip().lower()
        )

    raise UniversalOrchestrationCancellationTerminationError(
        "Canonical cancellation status evidence is invalid.",
        code="invalid_cancellation_status_evidence",
        value=value,
    )


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalOrchestrationCancellationRequestSnapshot:

    request_id: str

    request_source: str

    reason: str

    schema_version: str = (
        UNIVERSAL_ORCHESTRATION_CANCELLATION_REQUEST_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        object.__setattr__(
            self,
            "request_id",
            _normalize_required_text(
                self.request_id,
                field_name="request_id",
                code="invalid_cancellation_request_id",
            ),
        )

        object.__setattr__(
            self,
            "request_source",
            _normalize_required_text(
                self.request_source,
                field_name="request_source",
                code="invalid_cancellation_request_source",
            ),
        )

        object.__setattr__(
            self,
            "reason",
            _normalize_required_text(
                self.reason,
                field_name="reason",
                code="invalid_cancellation_request_reason",
            ),
        )

        if (
            self.schema_version
            !=
            UNIVERSAL_ORCHESTRATION_CANCELLATION_REQUEST_SCHEMA_VERSION
        ):

            raise UniversalOrchestrationCancellationTerminationError(
                "Invalid cancellation request schema_version.",
                code="invalid_cancellation_request_schema_version",
                value=self.schema_version,
            )

    @property
    def request_fingerprint(
        self,
    ) -> str:

        material = "|".join(
            (
                "universal_orchestration_cancellation_request_v1",
                self.request_id,
                self.request_source,
                self.reason,
                self.schema_version,
            )
        )

        return hashlib.sha256(
            material.encode(
                "utf-8"
            )
        ).hexdigest().upper()


def create_universal_orchestration_cancellation_request(
    *,
    request_id: Any,
    request_source: Any,
    reason: Any,
) -> UniversalOrchestrationCancellationRequestSnapshot:

    return (
        UniversalOrchestrationCancellationRequestSnapshot(
            request_id=request_id,
            request_source=request_source,
            reason=reason,
        )
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


def _evaluate_cancellation(
    *,
    state_snapshot: UniversalOrchestrationStateSnapshot,
    progress_snapshot: UniversalOrchestrationProgressSnapshot,
    cancellation_request_snapshot: UniversalOrchestrationCancellationRequestSnapshot | None,
) -> tuple[
    UniversalOrchestrationCancellationDisposition,
    UniversalOrchestrationCancellationReason,
]:

    state = (
        state_snapshot.state
    )

    if (
        state
        is
        UniversalOrchestrationState.CANCELLED
    ):

        return (
            UniversalOrchestrationCancellationDisposition.ALREADY_CANCELLED,
            UniversalOrchestrationCancellationReason.ALREADY_CANCELLED,
        )

    if (
        state
        is
        UniversalOrchestrationState.SUCCEEDED
    ):

        return (
            UniversalOrchestrationCancellationDisposition.INELIGIBLE,
            UniversalOrchestrationCancellationReason.TERMINAL_SUCCEEDED,
        )

    if (
        state
        is
        UniversalOrchestrationState.FAILED
    ):

        return (
            UniversalOrchestrationCancellationDisposition.INELIGIBLE,
            UniversalOrchestrationCancellationReason.TERMINAL_FAILED,
        )

    if cancellation_request_snapshot is None:

        return (
            UniversalOrchestrationCancellationDisposition.NOT_REQUESTED,
            UniversalOrchestrationCancellationReason.NO_CANCELLATION_REQUEST,
        )

    if progress_snapshot.has_missing_status_evidence:

        return (
            UniversalOrchestrationCancellationDisposition.UNRESOLVED,
            UniversalOrchestrationCancellationReason.MISSING_STATUS_EVIDENCE,
        )

    if progress_snapshot.has_unresolved_branch_activity:

        return (
            UniversalOrchestrationCancellationDisposition.UNRESOLVED,
            UniversalOrchestrationCancellationReason.UNRESOLVED_BRANCH_ACTIVITY,
        )

    if (
        progress_snapshot.possible_effective_job_count
        == 0
    ):

        return (
            UniversalOrchestrationCancellationDisposition.ELIGIBLE,
            UniversalOrchestrationCancellationReason.NO_EFFECTIVE_WORK,
        )

    nonterminal_job_ids = (
        _job_ids_with_statuses(
            progress_snapshot=progress_snapshot,
            statuses=_NONTERMINAL_STATUS_VALUES,
        )
    )

    if nonterminal_job_ids:

        return (
            UniversalOrchestrationCancellationDisposition.WAITING_FOR_TERMINATION,
            UniversalOrchestrationCancellationReason.NONTERMINAL_EFFECTIVE_WORK,
        )

    cancelled_job_ids = (
        _job_ids_with_statuses(
            progress_snapshot=progress_snapshot,
            statuses=frozenset(
                {
                    "cancelled",
                }
            ),
        )
    )

    if cancelled_job_ids:

        return (
            UniversalOrchestrationCancellationDisposition.ELIGIBLE,
            UniversalOrchestrationCancellationReason.CANCELLED_EFFECTIVE_WORK,
        )

    terminal_job_ids = (
        _job_ids_with_statuses(
            progress_snapshot=progress_snapshot,
            statuses=_TERMINAL_STATUS_VALUES,
        )
    )

    if (
        len(
            terminal_job_ids
        )
        ==
        progress_snapshot.possible_effective_job_count
    ):

        return (
            UniversalOrchestrationCancellationDisposition.INELIGIBLE,
            UniversalOrchestrationCancellationReason.TERMINAL_WORK_WITHOUT_CANCELLATION_EVIDENCE,
        )

    return (
        UniversalOrchestrationCancellationDisposition.UNRESOLVED,
        UniversalOrchestrationCancellationReason.MISSING_STATUS_EVIDENCE,
    )


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalOrchestrationCancellationDecision:

    state_snapshot: UniversalOrchestrationStateSnapshot

    progress_snapshot: UniversalOrchestrationProgressSnapshot

    cancellation_request_snapshot: UniversalOrchestrationCancellationRequestSnapshot | None

    schema_version: str = (
        UNIVERSAL_ORCHESTRATION_CANCELLATION_DECISION_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        state = (
            _require_state_snapshot(
                self.state_snapshot
            )
        )

        progress = (
            _require_progress_snapshot(
                self.progress_snapshot
            )
        )

        _validate_identity_alignment(
            state_snapshot=state,
            progress_snapshot=progress,
        )

        request = (
            self.cancellation_request_snapshot
        )

        if (
            request is not None
            and
            not isinstance(
                request,
                UniversalOrchestrationCancellationRequestSnapshot,
            )
        ):

            raise UniversalOrchestrationCancellationTerminationError(
                (
                    "cancellation_request_snapshot must be "
                    "None or a "
                    "UniversalOrchestrationCancellationRequestSnapshot."
                ),
                code="invalid_cancellation_request_snapshot",
                value=request,
            )

        if (
            self.schema_version
            !=
            UNIVERSAL_ORCHESTRATION_CANCELLATION_DECISION_SCHEMA_VERSION
        ):

            raise UniversalOrchestrationCancellationTerminationError(
                "Invalid cancellation decision schema_version.",
                code="invalid_cancellation_decision_schema_version",
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
    ) -> UniversalOrchestrationCancellationDisposition:

        disposition, _ = (
            _evaluate_cancellation(
                state_snapshot=self.state_snapshot,
                progress_snapshot=self.progress_snapshot,
                cancellation_request_snapshot=(
                    self.cancellation_request_snapshot
                ),
            )
        )

        return disposition

    @property
    def reason(
        self,
    ) -> UniversalOrchestrationCancellationReason:

        _, reason = (
            _evaluate_cancellation(
                state_snapshot=self.state_snapshot,
                progress_snapshot=self.progress_snapshot,
                cancellation_request_snapshot=(
                    self.cancellation_request_snapshot
                ),
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
    def cancelled_effective_job_ids(
        self,
    ) -> tuple[str, ...]:

        return (
            _job_ids_with_statuses(
                progress_snapshot=self.progress_snapshot,
                statuses=frozenset(
                    {
                        "cancelled",
                    }
                ),
            )
        )

    @property
    def is_cancellation_requested(
        self,
    ) -> bool:

        return (
            self.cancellation_request_snapshot
            is not None
        )

    @property
    def is_waiting_for_termination(
        self,
    ) -> bool:

        return (
            self.disposition
            is
            UniversalOrchestrationCancellationDisposition.WAITING_FOR_TERMINATION
        )

    @property
    def is_eligible(
        self,
    ) -> bool:

        return (
            self.disposition
            is
            UniversalOrchestrationCancellationDisposition.ELIGIBLE
        )

    @property
    def is_already_cancelled(
        self,
    ) -> bool:

        return (
            self.disposition
            is
            UniversalOrchestrationCancellationDisposition.ALREADY_CANCELLED
        )

    @property
    def is_unresolved(
        self,
    ) -> bool:

        return (
            self.disposition
            is
            UniversalOrchestrationCancellationDisposition.UNRESOLVED
        )

    @property
    def target_terminal_state(
        self,
    ) -> UniversalOrchestrationState | None:

        if (
            self.disposition
            in (
                UniversalOrchestrationCancellationDisposition.ELIGIBLE,
                UniversalOrchestrationCancellationDisposition.ALREADY_CANCELLED,
            )
        ):

            return (
                UniversalOrchestrationState.CANCELLED
            )

        return None

    @property
    def is_target_state_already_realized(
        self,
    ) -> bool:

        return (
            self.target_terminal_state
            is
            UniversalOrchestrationState.CANCELLED
            and
            self.orchestration_state
            is
            UniversalOrchestrationState.CANCELLED
        )

    @property
    def may_transition_to_cancelled(
        self,
    ) -> bool:

        if (
            self.disposition
            is not
            UniversalOrchestrationCancellationDisposition.ELIGIBLE
        ):

            return False

        if (
            self.orchestration_state
            is
            UniversalOrchestrationState.CANCELLED
        ):

            return False

        return (
            can_transition_universal_orchestration_state(
                current_state=self.orchestration_state,
                target_state=UniversalOrchestrationState.CANCELLED,
            )
        )

    @property
    def cancellation_decision_id(
        self,
    ) -> str:

        request_marker = (
            "NO_REQUEST"
            if self.cancellation_request_snapshot is None
            else self.cancellation_request_snapshot.request_fingerprint
        )

        material = "|".join(
            (
                "universal_orchestration_cancellation_decision_v1",
                _identity_fingerprint(
                    self.identity
                ),
                self.orchestration_state.value,
                self.progress_snapshot.progress_snapshot_id,
                request_marker,
                self.schema_version,
            )
        )

        return hashlib.sha256(
            material.encode(
                "utf-8"
            )
        ).hexdigest().upper()


def resolve_universal_orchestration_cancellation_termination(
    *,
    state_snapshot: Any,
    progress_snapshot: Any,
    cancellation_request_snapshot: Any = None,
) -> UniversalOrchestrationCancellationDecision:

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
        UniversalOrchestrationCancellationDecision(
            state_snapshot=state,
            progress_snapshot=progress,
            cancellation_request_snapshot=(
                cancellation_request_snapshot
            ),
        )
    )


def explain_universal_orchestration_cancellation_termination_v1(
) -> Mapping[
    str,
    Any,
]:

    return MappingProxyType(
        {
            "phase":
                "5.1.16",

            "component":
                (
                    "Universal Orchestration Cancellation / "
                    "Termination Resolution"
                ),

            "version":
                UNIVERSAL_ORCHESTRATION_CANCELLATION_TERMINATION_VERSION,

            "decision_stored_fields": (
                "state_snapshot",
                "progress_snapshot",
                "cancellation_request_snapshot",
                "schema_version",
            ),

            "request_stored_fields": (
                "request_id",
                "request_source",
                "reason",
                "schema_version",
            ),

            "intent_rule": (
                "Job-level CANCELLED evidence does not itself "
                "create orchestration-level cancellation intent. "
                "Explicit caller-supplied cancellation intent is required."
            ),

            "state_authority": (
                "Frozen 5.1.3 supplies orchestration lifecycle state "
                "and CANCELLED transition legality."
            ),

            "progress_authority": (
                "Frozen 5.1.11 supplies possible-effective work, "
                "status evidence and branch resolution."
            ),

            "completion_boundary": (
                "Frozen 5.1.15 owns SUCCEEDED/FAILED completion. "
                "5.1.16 does not recompute completion."
            ),

            "quiescence_rule": (
                "Any possible-effective CREATED, QUEUED, SCHEDULED, "
                "LEASED, RUNNING or SUSPENDED work requires "
                "execution-side termination before final cancellation."
            ),

            "terminal_rule": (
                "A requested orchestration becomes cancellation-eligible "
                "when there is no effective work, or when effective work "
                "is terminal and includes cancellation evidence."
            ),

            "natural_completion_rule": (
                "Fully terminal effective work with no CANCELLED evidence "
                "is natural completion territory and is not rewritten "
                "as orchestration cancellation."
            ),

            "transition_boundary": (
                "5.1.16 derives CANCELLED eligibility and 5.1.3 "
                "transition legality but performs no transition."
            ),

            "persistence_boundary": (
                "5.1.14 owns persistence; 5.1.16 performs no persistence."
            ),

            "evidence_boundary": (
                "5.1.17 owns permanent cancellation and termination "
                "decision records."
            ),

            "execution_boundary": (
                "Actual job cancellation, queue removal, worker "
                "interruption, lease release/revocation and forced "
                "termination belong outside 5.1.16."
            ),

            "prohibitions": (
                "does not infer orchestration cancellation from one cancelled job",
                "does not transition orchestration state",
                "does not mutate UniversalJob status",
                "does not cancel jobs",
                "does not enqueue jobs",
                "does not dequeue jobs",
                "does not purge queues",
                "does not interrupt workers",
                "does not terminate workers",
                "does not drain workers",
                "does not release leases",
                "does not revoke leases",
                "does not inspect worker health",
                "does not inspect live lease state",
                "does not implement grace periods",
                "does not implement timeouts",
                "does not implement forced termination",
                "does not use wall clock",
                "does not recompute progress",
                "does not reevaluate completion",
                "does not reevaluate recovery",
                "does not invoke persistence port",
                "does not access Runtime State Store",
                "does not persist cancellation decisions",
                "does not record permanent audit evidence",
                "does not dispatch runtime handlers",
                "does not execute jobs",
                "does not perform filesystem I/O",
                "does not perform database I/O",
                "does not perform network I/O",
                "does not import Universal Coordination Framework",
                "does not invoke pipeline coordinators",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_ORCHESTRATION_CANCELLATION_TERMINATION_VERSION",
    "UNIVERSAL_ORCHESTRATION_CANCELLATION_REQUEST_SCHEMA_VERSION",
    "UNIVERSAL_ORCHESTRATION_CANCELLATION_DECISION_SCHEMA_VERSION",
    "UNIVERSAL_ORCHESTRATION_CANCELLATION_HASH_ALGORITHM",
    "UniversalOrchestrationCancellationTerminationError",
    "UniversalOrchestrationCancellationDisposition",
    "UniversalOrchestrationCancellationReason",
    "UniversalOrchestrationCancellationRequestSnapshot",
    "UniversalOrchestrationCancellationDecision",
    "create_universal_orchestration_cancellation_request",
    "resolve_universal_orchestration_cancellation_termination",
    "explain_universal_orchestration_cancellation_termination_v1",
]

