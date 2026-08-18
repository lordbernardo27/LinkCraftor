from __future__ import annotations

import hashlib
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Final, Mapping

from backend.server.runtime.universal_jobs.contract import (
    UniversalJobStatus,
)

from backend.server.runtime.universal_orchestration.contract import (
    normalize_universal_orchestration_identifier,
)

from backend.server.runtime.universal_orchestration.execution_planning import (
    UniversalOrchestrationExecutionPlan,
)

from backend.server.runtime.universal_orchestration.conditional_branching import (
    UniversalOrchestrationBranchDisposition,
    UniversalOrchestrationConditionalBranching,
)


UNIVERSAL_ORCHESTRATION_PROGRESS_TRACKING_VERSION: Final[str] = (
    "universal_orchestration_progress_tracking_v5.1.11"
)

UNIVERSAL_ORCHESTRATION_PROGRESS_TRACKING_SCHEMA_VERSION: Final[str] = (
    "universal_orchestration_progress_tracking_schema_v1"
)

UNIVERSAL_ORCHESTRATION_PROGRESS_SNAPSHOT_HASH_ALGORITHM: Final[str] = (
    "sha256"
)


NOT_STARTED_UNIVERSAL_JOB_STATUSES: Final[
    frozenset[UniversalJobStatus]
] = frozenset(
    {
        UniversalJobStatus.CREATED,
    }
)


PENDING_UNIVERSAL_JOB_STATUSES: Final[
    frozenset[UniversalJobStatus]
] = frozenset(
    {
        UniversalJobStatus.QUEUED,
        UniversalJobStatus.SCHEDULED,
    }
)


IN_PROGRESS_UNIVERSAL_JOB_STATUSES: Final[
    frozenset[UniversalJobStatus]
] = frozenset(
    {
        UniversalJobStatus.LEASED,
        UniversalJobStatus.RUNNING,
    }
)


SUSPENDED_UNIVERSAL_JOB_STATUSES: Final[
    frozenset[UniversalJobStatus]
] = frozenset(
    {
        UniversalJobStatus.SUSPENDED,
    }
)


TERMINAL_SUCCESS_UNIVERSAL_JOB_STATUSES: Final[
    frozenset[UniversalJobStatus]
] = frozenset(
    {
        UniversalJobStatus.SUCCEEDED,
    }
)


TERMINAL_UNSUCCESSFUL_UNIVERSAL_JOB_STATUSES: Final[
    frozenset[UniversalJobStatus]
] = frozenset(
    {
        UniversalJobStatus.FAILED,
        UniversalJobStatus.CANCELLED,
        UniversalJobStatus.DEAD_LETTER,
        UniversalJobStatus.EXPIRED,
    }
)


TERMINAL_PROGRESS_UNIVERSAL_JOB_STATUSES: Final[
    frozenset[UniversalJobStatus]
] = frozenset(
    TERMINAL_SUCCESS_UNIVERSAL_JOB_STATUSES
    |
    TERMINAL_UNSUCCESSFUL_UNIVERSAL_JOB_STATUSES
)


class UniversalOrchestrationProgressTrackingError(
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


def _require_execution_plan(
    value: Any,
) -> UniversalOrchestrationExecutionPlan:

    if not isinstance(
        value,
        UniversalOrchestrationExecutionPlan,
    ):

        raise UniversalOrchestrationProgressTrackingError(
            (
                "execution_plan must be a "
                "UniversalOrchestrationExecutionPlan."
            ),
            code="invalid_progress_execution_plan",
            value=value,
        )

    return value


def _normalize_status_value(
    value: Any,
) -> UniversalJobStatus | None:

    if value is None:

        return None

    if isinstance(
        value,
        UniversalJobStatus,
    ):

        return value

    if not isinstance(
        value,
        str,
    ):

        raise UniversalOrchestrationProgressTrackingError(
            (
                "Status evidence must be UniversalJobStatus, "
                "a valid UniversalJobStatus string, or None."
            ),
            code="invalid_progress_status_evidence_value",
            value=value,
        )

    try:

        return UniversalJobStatus.coerce(
            value
        )

    except Exception as exc:

        raise UniversalOrchestrationProgressTrackingError(
            (
                "Status evidence contains an invalid "
                "UniversalJobStatus value."
            ),
            code="invalid_progress_status_evidence_value",
            value=value,
        ) from exc


def _normalize_status_evidence(
    value: Any,
    *,
    execution_plan: UniversalOrchestrationExecutionPlan,
) -> tuple[
    tuple[
        str,
        UniversalJobStatus | None,
    ],
    ...,
]:

    if value is None:

        materialized = ()

    elif isinstance(
        value,
        Mapping,
    ):

        materialized = tuple(
            value.items()
        )

    else:

        if isinstance(
            value,
            (
                str,
                bytes,
                bytearray,
            ),
        ):

            raise UniversalOrchestrationProgressTrackingError(
                (
                    "status_evidence must be a mapping or "
                    "iterable of (job_id, status|None) pairs."
                ),
                code="invalid_progress_status_evidence",
                value=value,
            )

        try:

            materialized = tuple(
                value
            )

        except TypeError as exc:

            raise UniversalOrchestrationProgressTrackingError(
                (
                    "status_evidence must be a mapping or "
                    "iterable of (job_id, status|None) pairs."
                ),
                code="invalid_progress_status_evidence",
                value=value,
            ) from exc

    normalized: dict[
        str,
        UniversalJobStatus | None,
    ] = {}

    structural_job_ids = frozenset(
        execution_plan.job_ids
    )

    for entry in materialized:

        if not isinstance(
            entry,
            (
                tuple,
                list,
            ),
        ):

            raise UniversalOrchestrationProgressTrackingError(
                (
                    "Every status_evidence entry must be a "
                    "two-item (job_id, status|None) pair."
                ),
                code="invalid_progress_status_evidence_entry",
                value=entry,
            )

        if len(
            entry
        ) != 2:

            raise UniversalOrchestrationProgressTrackingError(
                (
                    "Every status_evidence entry must contain "
                    "exactly two items."
                ),
                code="invalid_progress_status_evidence_entry",
                value=entry,
            )

        raw_job_id = entry[0]

        try:

            job_id = (
                normalize_universal_orchestration_identifier(
                    raw_job_id,
                    field_name="status_evidence_job_id",
                )
            )

        except Exception as exc:

            raise UniversalOrchestrationProgressTrackingError(
                (
                    "status_evidence job_id must satisfy the "
                    "canonical orchestration identifier contract."
                ),
                code="invalid_progress_status_evidence_job_id",
                value=raw_job_id,
            ) from exc

        if job_id not in structural_job_ids:

            raise UniversalOrchestrationProgressTrackingError(
                (
                    "status_evidence contains a job outside "
                    "the execution plan."
                ),
                code="progress_status_evidence_job_outside_plan",
                value=job_id,
            )

        if job_id in normalized:

            raise UniversalOrchestrationProgressTrackingError(
                (
                    "status_evidence contains a duplicate job_id."
                ),
                code="duplicate_progress_status_evidence_job_id",
                value=job_id,
            )

        normalized[
            job_id
        ] = (
            _normalize_status_value(
                entry[1]
            )
        )

    return tuple(
        (
            job_id,
            normalized.get(
                job_id,
                None,
            ),
        )
        for job_id
        in execution_plan.job_ids
    )


def _same_execution_plan(
    left: UniversalOrchestrationExecutionPlan,
    right: UniversalOrchestrationExecutionPlan,
) -> bool:

    return (
        left.identity.identity_fingerprint
        ==
        right.identity.identity_fingerprint
        and
        left.job_ids
        ==
        right.job_ids
        and
        left.dependency_map
        ==
        right.dependency_map
        and
        left.dependent_map
        ==
        right.dependent_map
    )


def _normalize_conditional_branching_decisions(
    value: Any,
    *,
    execution_plan: UniversalOrchestrationExecutionPlan,
) -> tuple[
    UniversalOrchestrationConditionalBranching,
    ...,
]:

    if value is None:

        materialized = ()

    elif isinstance(
        value,
        UniversalOrchestrationConditionalBranching,
    ):

        materialized = (
            value,
        )

    else:

        if isinstance(
            value,
            (
                str,
                bytes,
                bytearray,
                Mapping,
            ),
        ):

            raise UniversalOrchestrationProgressTrackingError(
                (
                    "conditional_branching_decisions must be "
                    "an iterable of frozen 5.1.10 decisions."
                ),
                code="invalid_progress_conditional_decisions",
                value=value,
            )

        try:

            materialized = tuple(
                value
            )

        except TypeError as exc:

            raise UniversalOrchestrationProgressTrackingError(
                (
                    "conditional_branching_decisions must be "
                    "an iterable of frozen 5.1.10 decisions."
                ),
                code="invalid_progress_conditional_decisions",
                value=value,
            ) from exc

    normalized: dict[
        str,
        UniversalOrchestrationConditionalBranching,
    ] = {}

    for decision in materialized:

        if not isinstance(
            decision,
            UniversalOrchestrationConditionalBranching,
        ):

            raise UniversalOrchestrationProgressTrackingError(
                (
                    "Every conditional decision must be a frozen "
                    "UniversalOrchestrationConditionalBranching."
                ),
                code="invalid_progress_conditional_decision",
                value=decision,
            )

        if not _same_execution_plan(
            decision.execution_plan,
            execution_plan,
        ):

            raise UniversalOrchestrationProgressTrackingError(
                (
                    "Conditional decision must belong to the "
                    "same orchestration identity and execution plan."
                ),
                code="progress_conditional_decision_plan_mismatch",
                value=decision.source_job_id,
            )

        source_job_id = (
            decision.source_job_id
        )

        if source_job_id in normalized:

            raise UniversalOrchestrationProgressTrackingError(
                (
                    "Only one conditional decision is allowed "
                    "per source_job_id."
                ),
                code="duplicate_progress_conditional_source",
                value=source_job_id,
            )

        normalized[
            source_job_id
        ] = decision

    return tuple(
        normalized[
            source_job_id
        ]
        for source_job_id
        in sorted(
            normalized
        )
    )


def _branch_edge_dispositions(
    decisions: tuple[
        UniversalOrchestrationConditionalBranching,
        ...,
    ],
) -> Mapping[
    tuple[
        str,
        str,
    ],
    UniversalOrchestrationBranchDisposition,
]:

    result: dict[
        tuple[
            str,
            str,
        ],
        UniversalOrchestrationBranchDisposition,
    ] = {}

    for decision in decisions:

        for (
            target_job_id,
            disposition,
        ) in decision.branch_dispositions.items():

            result[
                (
                    decision.source_job_id,
                    target_job_id,
                )
            ] = disposition

    return MappingProxyType(
        result
    )


def _effective_reachability(
    *,
    execution_plan: UniversalOrchestrationExecutionPlan,
    decisions: tuple[
        UniversalOrchestrationConditionalBranching,
        ...,
    ],
) -> tuple[
    tuple[str, ...],
    tuple[str, ...],
    tuple[str, ...],
    tuple[str, ...],
]:

    edge_dispositions = (
        _branch_edge_dispositions(
            decisions
        )
    )

    definite: set[str] = set(
        execution_plan.root_job_ids
    )

    possible: set[str] = set(
        execution_plan.root_job_ids
    )

    for job_id in execution_plan.topological_order:

        if job_id in execution_plan.root_job_ids:

            continue

        dependencies = (
            execution_plan.dependency_map[
                job_id
            ]
        )

        for dependency_job_id in dependencies:

            disposition = (
                edge_dispositions.get(
                    (
                        dependency_job_id,
                        job_id,
                    )
                )
            )

            definite_edge = (
                disposition is None
                or
                disposition
                is UniversalOrchestrationBranchDisposition.SELECTED
            )

            possible_edge = (
                disposition
                is not
                UniversalOrchestrationBranchDisposition.EXCLUDED
            )

            if (
                dependency_job_id in definite
                and
                definite_edge
            ):

                definite.add(
                    job_id
                )

            if (
                dependency_job_id in possible
                and
                possible_edge
            ):

                possible.add(
                    job_id
                )

    structural = tuple(
        execution_plan.job_ids
    )

    definite_ids = tuple(
        job_id
        for job_id
        in structural
        if job_id in definite
    )

    possible_ids = tuple(
        job_id
        for job_id
        in structural
        if job_id in possible
    )

    unresolved_ids = tuple(
        job_id
        for job_id
        in structural
        if (
            job_id in possible
            and
            job_id not in definite
        )
    )

    excluded_ids = tuple(
        job_id
        for job_id
        in structural
        if job_id not in possible
    )

    return (
        definite_ids,
        possible_ids,
        unresolved_ids,
        excluded_ids,
    )


def _status_map(
    evidence: tuple[
        tuple[
            str,
            UniversalJobStatus | None,
        ],
        ...,
    ],
) -> Mapping[
    str,
    UniversalJobStatus | None,
]:

    return MappingProxyType(
        dict(
            evidence
        )
    )


def _bucket_job_ids(
    *,
    job_ids: tuple[str, ...],
    status_map: Mapping[
        str,
        UniversalJobStatus | None,
    ],
) -> Mapping[
    str,
    tuple[str, ...],
]:

    buckets: dict[
        str,
        tuple[str, ...],
    ] = {}

    for status in UniversalJobStatus:

        buckets[
            status.value
        ] = tuple(
            job_id
            for job_id
            in job_ids
            if status_map[
                job_id
            ] is status
        )

    buckets[
        "missing"
    ] = tuple(
        job_id
        for job_id
        in job_ids
        if status_map[
            job_id
        ] is None
    )

    return MappingProxyType(
        buckets
    )


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalOrchestrationProgressSnapshot:

    execution_plan: UniversalOrchestrationExecutionPlan

    status_evidence: tuple[
        tuple[
            str,
            UniversalJobStatus | None,
        ],
        ...,
    ]

    conditional_branching_decisions: tuple[
        UniversalOrchestrationConditionalBranching,
        ...,
    ]

    schema_version: str = (
        UNIVERSAL_ORCHESTRATION_PROGRESS_TRACKING_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        plan = (
            _require_execution_plan(
                self.execution_plan
            )
        )

        status_evidence = (
            _normalize_status_evidence(
                self.status_evidence,
                execution_plan=plan,
            )
        )

        decisions = (
            _normalize_conditional_branching_decisions(
                self.conditional_branching_decisions,
                execution_plan=plan,
            )
        )

        if (
            self.schema_version
            !=
            UNIVERSAL_ORCHESTRATION_PROGRESS_TRACKING_SCHEMA_VERSION
        ):

            raise UniversalOrchestrationProgressTrackingError(
                "Invalid Progress Tracking schema_version.",
                code="invalid_progress_schema_version",
                value=self.schema_version,
            )

        object.__setattr__(
            self,
            "execution_plan",
            plan,
        )

        object.__setattr__(
            self,
            "status_evidence",
            status_evidence,
        )

        object.__setattr__(
            self,
            "conditional_branching_decisions",
            decisions,
        )

    @property
    def identity(
        self,
    ):

        return (
            self.execution_plan.identity
        )

    @property
    def structural_job_ids(
        self,
    ) -> tuple[str, ...]:

        return (
            self.execution_plan.job_ids
        )

    @property
    def structural_total_job_count(
        self,
    ) -> int:

        return len(
            self.structural_job_ids
        )

    @property
    def status_evidence_map(
        self,
    ) -> Mapping[
        str,
        UniversalJobStatus | None,
    ]:

        return (
            _status_map(
                self.status_evidence
            )
        )

    @property
    def branch_edge_dispositions(
        self,
    ) -> Mapping[
        tuple[str, str],
        UniversalOrchestrationBranchDisposition,
    ]:

        return (
            _branch_edge_dispositions(
                self.conditional_branching_decisions
            )
        )

    @property
    def definite_effective_job_ids(
        self,
    ) -> tuple[str, ...]:

        return (
            _effective_reachability(
                execution_plan=self.execution_plan,
                decisions=self.conditional_branching_decisions,
            )[0]
        )

    @property
    def possible_effective_job_ids(
        self,
    ) -> tuple[str, ...]:

        return (
            _effective_reachability(
                execution_plan=self.execution_plan,
                decisions=self.conditional_branching_decisions,
            )[1]
        )

    @property
    def unresolved_effective_job_ids(
        self,
    ) -> tuple[str, ...]:

        return (
            _effective_reachability(
                execution_plan=self.execution_plan,
                decisions=self.conditional_branching_decisions,
            )[2]
        )

    @property
    def excluded_effective_job_ids(
        self,
    ) -> tuple[str, ...]:

        return (
            _effective_reachability(
                execution_plan=self.execution_plan,
                decisions=self.conditional_branching_decisions,
            )[3]
        )

    @property
    def definite_effective_job_count(
        self,
    ) -> int:

        return len(
            self.definite_effective_job_ids
        )

    @property
    def possible_effective_job_count(
        self,
    ) -> int:

        return len(
            self.possible_effective_job_ids
        )

    @property
    def unresolved_effective_job_count(
        self,
    ) -> int:

        return len(
            self.unresolved_effective_job_ids
        )

    @property
    def excluded_effective_job_count(
        self,
    ) -> int:

        return len(
            self.excluded_effective_job_ids
        )

    @property
    def structural_status_buckets(
        self,
    ) -> Mapping[
        str,
        tuple[str, ...],
    ]:

        return (
            _bucket_job_ids(
                job_ids=self.structural_job_ids,
                status_map=self.status_evidence_map,
            )
        )

    @property
    def effective_status_buckets(
        self,
    ) -> Mapping[
        str,
        tuple[str, ...],
    ]:

        return (
            _bucket_job_ids(
                job_ids=self.possible_effective_job_ids,
                status_map=self.status_evidence_map,
            )
        )

    @property
    def not_started_job_ids(
        self,
    ) -> tuple[str, ...]:

        status_map = (
            self.status_evidence_map
        )

        return tuple(
            job_id
            for job_id
            in self.possible_effective_job_ids
            if status_map[
                job_id
            ]
            in NOT_STARTED_UNIVERSAL_JOB_STATUSES
        )

    @property
    def pending_job_ids(
        self,
    ) -> tuple[str, ...]:

        status_map = (
            self.status_evidence_map
        )

        return tuple(
            job_id
            for job_id
            in self.possible_effective_job_ids
            if status_map[
                job_id
            ]
            in PENDING_UNIVERSAL_JOB_STATUSES
        )

    @property
    def in_progress_job_ids(
        self,
    ) -> tuple[str, ...]:

        status_map = (
            self.status_evidence_map
        )

        return tuple(
            job_id
            for job_id
            in self.possible_effective_job_ids
            if status_map[
                job_id
            ]
            in IN_PROGRESS_UNIVERSAL_JOB_STATUSES
        )

    @property
    def suspended_job_ids(
        self,
    ) -> tuple[str, ...]:

        status_map = (
            self.status_evidence_map
        )

        return tuple(
            job_id
            for job_id
            in self.possible_effective_job_ids
            if status_map[
                job_id
            ]
            in SUSPENDED_UNIVERSAL_JOB_STATUSES
        )

    @property
    def successful_job_ids(
        self,
    ) -> tuple[str, ...]:

        status_map = (
            self.status_evidence_map
        )

        return tuple(
            job_id
            for job_id
            in self.possible_effective_job_ids
            if status_map[
                job_id
            ]
            in TERMINAL_SUCCESS_UNIVERSAL_JOB_STATUSES
        )

    @property
    def terminal_unsuccessful_job_ids(
        self,
    ) -> tuple[str, ...]:

        status_map = (
            self.status_evidence_map
        )

        return tuple(
            job_id
            for job_id
            in self.possible_effective_job_ids
            if status_map[
                job_id
            ]
            in TERMINAL_UNSUCCESSFUL_UNIVERSAL_JOB_STATUSES
        )

    @property
    def terminal_job_ids(
        self,
    ) -> tuple[str, ...]:

        status_map = (
            self.status_evidence_map
        )

        return tuple(
            job_id
            for job_id
            in self.possible_effective_job_ids
            if status_map[
                job_id
            ]
            in TERMINAL_PROGRESS_UNIVERSAL_JOB_STATUSES
        )

    @property
    def missing_status_job_ids(
        self,
    ) -> tuple[str, ...]:

        status_map = (
            self.status_evidence_map
        )

        return tuple(
            job_id
            for job_id
            in self.possible_effective_job_ids
            if status_map[
                job_id
            ] is None
        )

    @property
    def not_started_job_count(
        self,
    ) -> int:

        return len(
            self.not_started_job_ids
        )

    @property
    def pending_job_count(
        self,
    ) -> int:

        return len(
            self.pending_job_ids
        )

    @property
    def in_progress_job_count(
        self,
    ) -> int:

        return len(
            self.in_progress_job_ids
        )

    @property
    def suspended_job_count(
        self,
    ) -> int:

        return len(
            self.suspended_job_ids
        )

    @property
    def successful_job_count(
        self,
    ) -> int:

        return len(
            self.successful_job_ids
        )

    @property
    def terminal_unsuccessful_job_count(
        self,
    ) -> int:

        return len(
            self.terminal_unsuccessful_job_ids
        )

    @property
    def terminal_job_count(
        self,
    ) -> int:

        return len(
            self.terminal_job_ids
        )

    @property
    def missing_status_job_count(
        self,
    ) -> int:

        return len(
            self.missing_status_job_ids
        )

    @property
    def terminal_progress_numerator(
        self,
    ) -> int:

        return (
            self.terminal_job_count
        )

    @property
    def terminal_progress_denominator(
        self,
    ) -> int:

        return (
            self.possible_effective_job_count
        )

    @property
    def terminal_progress_ratio(
        self,
    ) -> tuple[
        int,
        int,
    ]:

        return (
            self.terminal_progress_numerator,
            self.terminal_progress_denominator,
        )

    @property
    def has_unresolved_branch_activity(
        self,
    ) -> bool:

        return bool(
            self.unresolved_effective_job_ids
        )

    @property
    def has_missing_status_evidence(
        self,
    ) -> bool:

        return bool(
            self.missing_status_job_ids
        )

    @property
    def progress_snapshot_id(
        self,
    ) -> str:

        status_material = "|".join(
            (
                job_id
                + "="
                + (
                    status.value
                    if status is not None
                    else
                    "missing"
                )
            )
            for job_id, status
            in self.status_evidence
        )

        decision_material = "|".join(
            decision.branch_decision_id
            for decision
            in self.conditional_branching_decisions
        )

        material = "|".join(
            (
                "universal_orchestration_progress_snapshot_v1",
                self.identity.identity_fingerprint,
                status_material,
                decision_material,
            )
        )

        return hashlib.sha256(
            material.encode(
                "utf-8"
            )
        ).hexdigest().upper()


def track_universal_orchestration_progress(
    *,
    execution_plan: Any,
    status_evidence: Any = None,
    conditional_branching_decisions: Any = None,
) -> UniversalOrchestrationProgressSnapshot:

    plan = (
        _require_execution_plan(
            execution_plan
        )
    )

    normalized_statuses = (
        _normalize_status_evidence(
            status_evidence,
            execution_plan=plan,
        )
    )

    normalized_decisions = (
        _normalize_conditional_branching_decisions(
            conditional_branching_decisions,
            execution_plan=plan,
        )
    )

    return UniversalOrchestrationProgressSnapshot(
        execution_plan=plan,
        status_evidence=normalized_statuses,
        conditional_branching_decisions=normalized_decisions,
    )


def explain_universal_orchestration_progress_tracking_v1(
) -> Mapping[
    str,
    Any,
]:

    return MappingProxyType(
        {
            "phase":
                "5.1.11",

            "component":
                "Universal Orchestration Progress Tracking",

            "version":
                UNIVERSAL_ORCHESTRATION_PROGRESS_TRACKING_VERSION,

            "schema_version":
                UNIVERSAL_ORCHESTRATION_PROGRESS_TRACKING_SCHEMA_VERSION,

            "stored_fields": (
                "execution_plan",
                "status_evidence",
                "conditional_branching_decisions",
                "schema_version",
            ),

            "status_rule": (
                "Status evidence is caller supplied and normalized "
                "against frozen UniversalJobStatus. Missing evidence "
                "remains explicitly missing."
            ),

            "terminal_progress_rule": (
                "SUCCEEDED, FAILED, CANCELLED, DEAD_LETTER, and "
                "EXPIRED count as terminated execution work. "
                "Only SUCCEEDED counts as successful work."
            ),

            "effective_topology_rule": (
                "Definite effective reachability uses unconditional "
                "and SELECTED edges. Possible effective reachability "
                "also includes UNRESOLVED conditional edges. "
                "EXCLUDED edges are removed only from the derived "
                "effective progress view."
            ),

            "shared_descendant_rule": (
                "A descendant remains effective when it is reachable "
                "through another non-excluded path, even when one "
                "incoming branch path is excluded."
            ),

            "dag_boundary": (
                "Frozen 5.1.5 execution-plan topology is never mutated."
            ),

            "conditional_boundary": (
                "5.1.11 consumes frozen 5.1.10 decisions and does not "
                "reevaluate condition evidence."
            ),

            "state_boundary": (
                "5.1.3 remains orchestration lifecycle-state authority."
            ),

            "suspension_boundary": (
                "5.1.12 owns orchestration suspension and resume eligibility."
            ),

            "recovery_boundary": (
                "5.1.13 owns orchestration recovery."
            ),

            "persistence_boundary": (
                "5.1.14 owns orchestration persistence."
            ),

            "completion_boundary": (
                "5.1.15 owns final orchestration completion and "
                "success/failure resolution."
            ),

            "evidence_record_boundary": (
                "5.1.17 owns permanent orchestration evidence "
                "and decision records."
            ),

            "prohibitions": (
                "does not read runtime storage",
                "does not read queue state",
                "does not read worker state",
                "does not read lease state",
                "does not inspect UniversalJob.status directly",
                "does not inspect UniversalJob.progress directly",
                "does not mutate UniversalJob.status",
                "does not mutate UniversalJob.progress",
                "does not perform dependency resolution",
                "does not evaluate stage readiness",
                "does not evaluate runtime handoff",
                "does not recompute fan-out",
                "does not recompute fan-in",
                "does not reevaluate conditional evidence",
                "does not mutate execution-plan topology",
                "does not enqueue jobs",
                "does not schedule jobs",
                "does not dequeue jobs",
                "does not claim jobs",
                "does not assign workers",
                "does not acquire leases",
                "does not dispatch runtime handlers",
                "does not execute jobs",
                "does not transition orchestration state",
                "does not determine orchestration completion",
                "does not determine orchestration success",
                "does not determine orchestration failure",
                "does not suspend or resume orchestration",
                "does not initiate recovery",
                "does not access Runtime State Store",
                "does not persist progress",
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
    "UNIVERSAL_ORCHESTRATION_PROGRESS_TRACKING_VERSION",
    "UNIVERSAL_ORCHESTRATION_PROGRESS_TRACKING_SCHEMA_VERSION",
    "UNIVERSAL_ORCHESTRATION_PROGRESS_SNAPSHOT_HASH_ALGORITHM",
    "NOT_STARTED_UNIVERSAL_JOB_STATUSES",
    "PENDING_UNIVERSAL_JOB_STATUSES",
    "IN_PROGRESS_UNIVERSAL_JOB_STATUSES",
    "SUSPENDED_UNIVERSAL_JOB_STATUSES",
    "TERMINAL_SUCCESS_UNIVERSAL_JOB_STATUSES",
    "TERMINAL_UNSUCCESSFUL_UNIVERSAL_JOB_STATUSES",
    "TERMINAL_PROGRESS_UNIVERSAL_JOB_STATUSES",
    "UniversalOrchestrationProgressTrackingError",
    "UniversalOrchestrationProgressSnapshot",
    "track_universal_orchestration_progress",
    "explain_universal_orchestration_progress_tracking_v1",
]
