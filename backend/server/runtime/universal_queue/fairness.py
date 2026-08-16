from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Iterable, Mapping


UNIVERSAL_QUEUE_FAIRNESS_VERSION = (
    "universal_queue_fairness_v3.1.12"
)

UNIVERSAL_QUEUE_FAIRNESS_CANDIDATE_SCHEMA_VERSION = (
    "universal_queue_fairness_candidate_schema_v1"
)

UNIVERSAL_QUEUE_FAIRNESS_DECISION_SCHEMA_VERSION = (
    "universal_queue_fairness_decision_schema_v1"
)


CANONICAL_UNIVERSAL_JOB_PRIORITIES = frozenset(
    {
        10,
        20,
        30,
        40,
        50,
    }
)


class UniversalQueueFairnessError(
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


def _normalize_nonblank_string(
    value: Any,
    *,
    field_name: str,
) -> str:

    if not isinstance(
        value,
        str,
    ):

        raise UniversalQueueFairnessError(
            f"{field_name} must be a string.",
            code="invalid_" + field_name + "_type",
            value=value,
        )

    normalized = value.strip()

    if not normalized:

        raise UniversalQueueFairnessError(
            f"{field_name} must not be blank.",
            code="blank_" + field_name,
            value=value,
        )

    return normalized


def normalize_universal_queue_fairness_workspace_id(
    value: Any,
) -> str:

    return _normalize_nonblank_string(
        value,
        field_name="workspace_id",
    )


def normalize_universal_queue_fairness_job_id(
    value: Any,
) -> str:

    return _normalize_nonblank_string(
        value,
        field_name="job_id",
    )


def normalize_universal_queue_fairness_priority(
    value: Any,
) -> int:

    if (
        isinstance(
            value,
            bool,
        )
        or not isinstance(
            value,
            int,
        )
    ):

        raise UniversalQueueFairnessError(
            "priority must be a canonical integer priority.",
            code="invalid_fairness_priority_type",
            value=value,
        )

    if value not in CANONICAL_UNIVERSAL_JOB_PRIORITIES:

        raise UniversalQueueFairnessError(
            (
                "priority must be one of "
                "10, 20, 30, 40, 50."
            ),
            code="unsupported_fairness_priority",
            value=value,
        )

    return value


def normalize_universal_queue_fairness_service_count(
    value: Any,
) -> int:

    if (
        isinstance(
            value,
            bool,
        )
        or not isinstance(
            value,
            int,
        )
    ):

        raise UniversalQueueFairnessError(
            "service_count must be a non-negative integer.",
            code="invalid_fairness_service_count_type",
            value=value,
        )

    if value < 0:

        raise UniversalQueueFairnessError(
            "service_count must not be negative.",
            code="negative_fairness_service_count",
            value=value,
        )

    return value


def normalize_universal_queue_fairness_created_at(
    value: Any,
) -> datetime:

    if isinstance(
        value,
        datetime,
    ):

        parsed = value

    elif isinstance(
        value,
        str,
    ):

        text = value.strip()

        if not text:

            raise UniversalQueueFairnessError(
                "created_at must not be blank.",
                code="blank_fairness_created_at",
                value=value,
            )

        if text.endswith(
            "Z"
        ):

            text = (
                text[:-1]
                + "+00:00"
            )

        try:

            parsed = datetime.fromisoformat(
                text
            )

        except ValueError as exc:

            raise UniversalQueueFairnessError(
                "created_at must be ISO-8601.",
                code="invalid_fairness_created_at",
                value=value,
            ) from exc

    else:

        raise UniversalQueueFairnessError(
            "created_at must be datetime or ISO-8601 string.",
            code="invalid_fairness_created_at_type",
            value=value,
        )

    if parsed.tzinfo is None:

        raise UniversalQueueFairnessError(
            "created_at must be timezone-aware.",
            code="naive_fairness_created_at",
            value=value,
        )

    return parsed.astimezone(
        timezone.utc
    )


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalQueueFairnessCandidate:

    workspace_id: str
    job_id: str
    priority: int
    created_at: datetime | str
    service_count: int
    schema_version: str = (
        UNIVERSAL_QUEUE_FAIRNESS_CANDIDATE_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        set_ = object.__setattr__

        set_(
            self,
            "workspace_id",
            normalize_universal_queue_fairness_workspace_id(
                self.workspace_id
            ),
        )

        set_(
            self,
            "job_id",
            normalize_universal_queue_fairness_job_id(
                self.job_id
            ),
        )

        set_(
            self,
            "priority",
            normalize_universal_queue_fairness_priority(
                self.priority
            ),
        )

        set_(
            self,
            "created_at",
            normalize_universal_queue_fairness_created_at(
                self.created_at
            ),
        )

        set_(
            self,
            "service_count",
            normalize_universal_queue_fairness_service_count(
                self.service_count
            ),
        )

        if (
            self.schema_version
            != UNIVERSAL_QUEUE_FAIRNESS_CANDIDATE_SCHEMA_VERSION
        ):

            raise UniversalQueueFairnessError(
                "Invalid fairness candidate schema_version.",
                code="invalid_fairness_candidate_schema_version",
                value=self.schema_version,
            )

    @property
    def fairness_key(
        self,
    ) -> tuple[Any, ...]:

        return (
            self.service_count,
            self.created_at,
            self.job_id,
            self.workspace_id,
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "schema_version":
                self.schema_version,

            "workspace_id":
                self.workspace_id,

            "job_id":
                self.job_id,

            "priority":
                self.priority,

            "created_at":
                self.created_at.isoformat(),

            "service_count":
                self.service_count,
        }


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalQueueFairnessDecision:

    selected_workspace_id: str
    selected_job_id: str
    priority: int
    selected_service_count: int
    selected_created_at: datetime | str
    candidate_count: int
    fairness_applied: bool
    mutation_required: bool
    reason: str
    schema_version: str = (
        UNIVERSAL_QUEUE_FAIRNESS_DECISION_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        set_ = object.__setattr__

        set_(
            self,
            "selected_workspace_id",
            normalize_universal_queue_fairness_workspace_id(
                self.selected_workspace_id
            ),
        )

        set_(
            self,
            "selected_job_id",
            normalize_universal_queue_fairness_job_id(
                self.selected_job_id
            ),
        )

        set_(
            self,
            "priority",
            normalize_universal_queue_fairness_priority(
                self.priority
            ),
        )

        set_(
            self,
            "selected_service_count",
            normalize_universal_queue_fairness_service_count(
                self.selected_service_count
            ),
        )

        set_(
            self,
            "selected_created_at",
            normalize_universal_queue_fairness_created_at(
                self.selected_created_at
            ),
        )

        if (
            isinstance(
                self.candidate_count,
                bool,
            )
            or not isinstance(
                self.candidate_count,
                int,
            )
            or self.candidate_count < 1
        ):

            raise UniversalQueueFairnessError(
                "candidate_count must be an integer >= 1.",
                code="invalid_fairness_candidate_count",
                value=self.candidate_count,
            )

        if not isinstance(
            self.fairness_applied,
            bool,
        ):

            raise UniversalQueueFairnessError(
                "fairness_applied must be bool.",
                code="invalid_fairness_applied_flag",
                value=self.fairness_applied,
            )

        expected_fairness_applied = (
            self.candidate_count > 1
        )

        if (
            self.fairness_applied
            is not expected_fairness_applied
        ):

            raise UniversalQueueFairnessError(
                "fairness_applied is inconsistent with candidate_count.",
                code="inconsistent_fairness_applied",
                value=self.fairness_applied,
            )

        if not isinstance(
            self.mutation_required,
            bool,
        ):

            raise UniversalQueueFairnessError(
                "mutation_required must be bool.",
                code="invalid_fairness_mutation_flag",
                value=self.mutation_required,
            )

        if self.mutation_required is not False:

            raise UniversalQueueFairnessError(
                (
                    "3.1.12 selects a logical fairness winner "
                    "but does not claim, dispatch or mutate."
                ),
                code="fairness_mutation_not_owned",
                value=self.mutation_required,
            )

        if not isinstance(
            self.reason,
            str,
        ):

            raise UniversalQueueFairnessError(
                "reason must be a string.",
                code="invalid_fairness_reason_type",
                value=self.reason,
            )

        reason = self.reason.strip()

        if not reason:

            raise UniversalQueueFairnessError(
                "reason must not be blank.",
                code="blank_fairness_reason",
                value=self.reason,
            )

        set_(
            self,
            "reason",
            reason,
        )

        if (
            self.schema_version
            != UNIVERSAL_QUEUE_FAIRNESS_DECISION_SCHEMA_VERSION
        ):

            raise UniversalQueueFairnessError(
                "Invalid fairness decision schema_version.",
                code="invalid_fairness_decision_schema_version",
                value=self.schema_version,
            )

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "schema_version":
                self.schema_version,

            "selected_workspace_id":
                self.selected_workspace_id,

            "selected_job_id":
                self.selected_job_id,

            "priority":
                self.priority,

            "selected_service_count":
                self.selected_service_count,

            "selected_created_at":
                self.selected_created_at.isoformat(),

            "candidate_count":
                self.candidate_count,

            "fairness_applied":
                self.fairness_applied,

            "mutation_required":
                self.mutation_required,

            "reason":
                self.reason,
        }


def create_universal_queue_fairness_candidate(
    *,
    workspace_id: str,
    job_id: str,
    priority: int,
    created_at: datetime | str,
    service_count: int,
) -> UniversalQueueFairnessCandidate:

    return UniversalQueueFairnessCandidate(
        workspace_id=workspace_id,
        job_id=job_id,
        priority=priority,
        created_at=created_at,
        service_count=service_count,
    )


def select_universal_queue_fairness_candidate(
    *,
    candidates: Iterable[
        UniversalQueueFairnessCandidate
    ],
) -> UniversalQueueFairnessDecision:

    if isinstance(
        candidates,
        (
            str,
            bytes,
            Mapping,
        ),
    ):

        raise UniversalQueueFairnessError(
            "candidates must be an iterable of fairness candidates.",
            code="invalid_fairness_candidates",
            value=candidates,
        )

    try:

        materialized = tuple(
            candidates
        )

    except TypeError as exc:

        raise UniversalQueueFairnessError(
            "candidates must be iterable.",
            code="invalid_fairness_candidates",
            value=candidates,
        ) from exc

    if not materialized:

        raise UniversalQueueFairnessError(
            "At least one fairness candidate is required.",
            code="empty_fairness_candidates",
            value=materialized,
        )

    for candidate in materialized:

        if not isinstance(
            candidate,
            UniversalQueueFairnessCandidate,
        ):

            raise UniversalQueueFairnessError(
                (
                    "Every fairness candidate must be a "
                    "UniversalQueueFairnessCandidate."
                ),
                code="invalid_fairness_candidate",
                value=candidate,
            )

    workspaces = [
        candidate.workspace_id
        for candidate
        in materialized
    ]

    if len(
        set(
            workspaces
        )
    ) != len(
        workspaces
    ):

        raise UniversalQueueFairnessError(
            (
                "Exactly one eligible head candidate per "
                "workspace is permitted."
            ),
            code="duplicate_fairness_workspace",
            value=tuple(
                workspaces
            ),
        )

    priorities = {
        candidate.priority
        for candidate
        in materialized
    }

    if len(
        priorities
    ) != 1:

        raise UniversalQueueFairnessError(
            (
                "A fairness cohort must contain exactly "
                "one canonical priority class."
            ),
            code="mixed_fairness_priority_cohort",
            value=tuple(
                sorted(
                    priorities
                )
            ),
        )

    selected = min(
        materialized,
        key=lambda candidate:
            candidate.fairness_key,
    )

    fairness_applied = (
        len(
            materialized
        )
        > 1
    )

    reason = (
        "single_workspace_candidate"
        if not fairness_applied
        else "least_served_workspace"
    )

    return UniversalQueueFairnessDecision(
        selected_workspace_id=selected.workspace_id,
        selected_job_id=selected.job_id,
        priority=selected.priority,
        selected_service_count=selected.service_count,
        selected_created_at=selected.created_at,
        candidate_count=len(
            materialized
        ),
        fairness_applied=fairness_applied,
        mutation_required=False,
        reason=reason,
    )


def explain_universal_queue_fairness_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "3.1.12",

            "component":
                "Universal Queue Fairness",

            "version":
                UNIVERSAL_QUEUE_FAIRNESS_VERSION,

            "candidate_schema":
                UNIVERSAL_QUEUE_FAIRNESS_CANDIDATE_SCHEMA_VERSION,

            "decision_schema":
                UNIVERSAL_QUEUE_FAIRNESS_DECISION_SCHEMA_VERSION,

            "scope":
                "LinkCraftor-wide",

            "canonical_fairness_identity":
                "workspace_id",

            "canonical_fairness_evidence":
                "service_count",

            "candidate_rule": (
                "caller supplies exactly one already-eligible "
                "head job candidate per workspace"
            ),

            "priority_rule": (
                "all candidates in one fairness cohort must share "
                "the same canonical Universal Job priority; 3.1.12 "
                "does not change or age priority"
            ),

            "selection_rule": (
                "least service_count wins; ties use created_at FIFO, "
                "then job_id, then workspace_id"
            ),

            "service_count_rule": (
                "service_count is caller-supplied fairness accounting "
                "evidence; 3.1.12 does not increment or persist it"
            ),

            "prioritization_relationship": (
                "3.1.3 determines canonical job priority and the "
                "eligible head candidate presented by each workspace; "
                "3.1.12 allocates the next service opportunity among "
                "same-priority workspace heads"
            ),

            "starvation_rule": (
                "least-served workspace selection prevents a workspace "
                "with a larger service_count from monopolizing "
                "same-priority service opportunities"
            ),

            "aging_rule": (
                "priority aging is not part of Queue Fairness v1"
            ),

            "round_robin_rule": (
                "3.1.12 maintains no persistent round-robin cursor; "
                "least-served caller evidence provides deterministic "
                "stateless fairness"
            ),

            "weighted_rule": (
                "weighted fairness is not part of Queue Fairness v1"
            ),

            "capacity_boundary": (
                "hard queue capacity belongs to "
                "3.1.11 Queue Capacity Limits"
            ),

            "backpressure_boundary": (
                "pressure classification belongs to "
                "3.1.10 Queue Backpressure"
            ),

            "rate_limit_boundary": (
                "rate limiting belongs to "
                "3.1.13 Queue Rate Limiting"
            ),

            "worker_boundary": (
                "claiming, leasing, dispatching and worker selection "
                "belong to Worker Infrastructure"
            ),

            "prohibitions": (
                "does not redefine Universal Job Priority",
                "does not mutate job priority",
                "does not implement priority aging",
                "does not maintain round-robin state",
                "does not implement weighted fairness",
                "does not create Universal Jobs",
                "does not mutate Universal Jobs",
                "does not mutate queues",
                "does not enqueue jobs",
                "does not dequeue jobs",
                "does not claim jobs",
                "does not lease jobs",
                "does not dispatch jobs",
                "does not select workers",
                "does not inspect worker capability",
                "does not increment service_count",
                "does not persist service_count",
                "does not read live queue state",
                "does not access orchestration",
                "does not access the Job Store",
                "does not access Runtime State Store",
                "does not apply Queue Backpressure",
                "does not enforce queue capacity",
                "does not implement rate limiting",
                "does not apply billing quotas",
                "does not apply subscription limits",
                "does not create physical queues",
                "does not perform filesystem I/O",
                "does not perform network I/O",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_QUEUE_FAIRNESS_VERSION",
    "UNIVERSAL_QUEUE_FAIRNESS_CANDIDATE_SCHEMA_VERSION",
    "UNIVERSAL_QUEUE_FAIRNESS_DECISION_SCHEMA_VERSION",
    "CANONICAL_UNIVERSAL_JOB_PRIORITIES",
    "UniversalQueueFairnessError",
    "UniversalQueueFairnessCandidate",
    "UniversalQueueFairnessDecision",
    "normalize_universal_queue_fairness_workspace_id",
    "normalize_universal_queue_fairness_job_id",
    "normalize_universal_queue_fairness_priority",
    "normalize_universal_queue_fairness_service_count",
    "normalize_universal_queue_fairness_created_at",
    "create_universal_queue_fairness_candidate",
    "select_universal_queue_fairness_candidate",
    "explain_universal_queue_fairness_v1",
]
