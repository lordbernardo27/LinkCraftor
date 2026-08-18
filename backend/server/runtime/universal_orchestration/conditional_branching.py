from __future__ import annotations

import enum
import hashlib
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Final, Iterable, Mapping

from backend.server.runtime.universal_orchestration.contract import (
    normalize_universal_orchestration_identifier,
)

from backend.server.runtime.universal_orchestration.fan_out_coordination import (
    UniversalOrchestrationFanOutCoordination,
)


UNIVERSAL_ORCHESTRATION_CONDITIONAL_BRANCHING_VERSION: Final[str] = (
    "universal_orchestration_conditional_branching_v5.1.10"
)

UNIVERSAL_ORCHESTRATION_CONDITIONAL_BRANCHING_SCHEMA_VERSION: Final[str] = (
    "universal_orchestration_conditional_branching_schema_v1"
)

UNIVERSAL_ORCHESTRATION_BRANCH_DECISION_HASH_ALGORITHM: Final[str] = (
    "sha256"
)


class UniversalOrchestrationConditionalBranchingError(
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


class UniversalOrchestrationBranchDisposition(
    str,
    enum.Enum,
):

    SELECTED = "selected"

    EXCLUDED = "excluded"

    UNRESOLVED = "unresolved"


class UniversalOrchestrationBranchResolution(
    str,
    enum.Enum,
):

    RESOLVED = "resolved"

    UNRESOLVED = "unresolved"


def _require_fan_out_coordination(
    value: Any,
) -> UniversalOrchestrationFanOutCoordination:

    if not isinstance(
        value,
        UniversalOrchestrationFanOutCoordination,
    ):

        raise UniversalOrchestrationConditionalBranchingError(
            (
                "fan_out_coordination must be a frozen "
                "UniversalOrchestrationFanOutCoordination."
            ),
            code="invalid_conditional_branching_fan_out",
            value=value,
        )

    if not value.is_fan_out:

        raise UniversalOrchestrationConditionalBranchingError(
            (
                "Conditional Branching requires a structural "
                "5.1.8 FAN_OUT locus with at least two "
                "direct downstream branches."
            ),
            code="conditional_branching_requires_fan_out",
            value=value.source_job_id,
        )

    return value


def _normalize_condition_evidence(
    value: Any,
    *,
    fan_out_coordination: UniversalOrchestrationFanOutCoordination,
) -> tuple[
    tuple[
        str,
        bool | None,
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

            raise UniversalOrchestrationConditionalBranchingError(
                (
                    "condition_evidence must be a mapping or "
                    "iterable of (job_id, bool|None) pairs."
                ),
                code="invalid_condition_evidence",
                value=value,
            )

        try:

            materialized = tuple(
                value
            )

        except TypeError as exc:

            raise UniversalOrchestrationConditionalBranchingError(
                (
                    "condition_evidence must be a mapping or "
                    "iterable of (job_id, bool|None) pairs."
                ),
                code="invalid_condition_evidence",
                value=value,
            ) from exc

    normalized = {}

    candidates = set(
        fan_out_coordination.direct_dependent_job_ids
    )

    for item in materialized:

        if not isinstance(
            item,
            (
                tuple,
                list,
            ),
        ):

            raise UniversalOrchestrationConditionalBranchingError(
                (
                    "Each condition_evidence entry must be "
                    "a two-item (job_id, evidence) pair."
                ),
                code="invalid_condition_evidence_entry",
                value=item,
            )

        if len(
            item
        ) != 2:

            raise UniversalOrchestrationConditionalBranchingError(
                (
                    "Each condition_evidence entry must contain "
                    "exactly two items."
                ),
                code="invalid_condition_evidence_entry",
                value=item,
            )

        raw_job_id = item[0]

        evidence = item[1]

        try:

            job_id = (
                normalize_universal_orchestration_identifier(
                    raw_job_id,
                    field_name="branch_job_id",
                )
            )

        except Exception as exc:

            raise UniversalOrchestrationConditionalBranchingError(
                (
                    "condition_evidence branch job_id must "
                    "satisfy the canonical orchestration "
                    "identifier contract."
                ),
                code="invalid_condition_evidence_job_id",
                value=raw_job_id,
            ) from exc

        if job_id not in candidates:

            raise UniversalOrchestrationConditionalBranchingError(
                (
                    "condition_evidence contains a job outside "
                    "the direct 5.1.8 fan-out membership."
                ),
                code="condition_evidence_job_outside_fan_out",
                value=job_id,
            )

        if job_id in normalized:

            raise UniversalOrchestrationConditionalBranchingError(
                (
                    "condition_evidence contains a duplicate "
                    "branch job_id."
                ),
                code="duplicate_condition_evidence_job_id",
                value=job_id,
            )

        if (
            evidence is not None
            and
            not isinstance(
                evidence,
                bool,
            )
        ):

            raise UniversalOrchestrationConditionalBranchingError(
                (
                    "condition evidence must be exactly "
                    "True, False, or None."
                ),
                code="invalid_condition_evidence_value",
                value=evidence,
            )

        normalized[
            job_id
        ] = evidence

    return tuple(
        (
            job_id,
            normalized.get(
                job_id,
                None,
            ),
        )
        for job_id
        in fan_out_coordination.direct_dependent_job_ids
    )


def _evidence_map(
    evidence: tuple[
        tuple[
            str,
            bool | None,
        ],
        ...,
    ],
) -> Mapping[
    str,
    bool | None,
]:

    return MappingProxyType(
        dict(
            evidence
        )
    )


def disposition_for_condition_evidence(
    value: bool | None,
) -> UniversalOrchestrationBranchDisposition:

    if value is True:

        return (
            UniversalOrchestrationBranchDisposition
            .SELECTED
        )

    if value is False:

        return (
            UniversalOrchestrationBranchDisposition
            .EXCLUDED
        )

    if value is None:

        return (
            UniversalOrchestrationBranchDisposition
            .UNRESOLVED
        )

    raise UniversalOrchestrationConditionalBranchingError(
        (
            "condition evidence must be exactly "
            "True, False, or None."
        ),
        code="invalid_condition_evidence_value",
        value=value,
    )


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalOrchestrationConditionalBranching:

    fan_out_coordination: UniversalOrchestrationFanOutCoordination

    condition_evidence: tuple[
        tuple[
            str,
            bool | None,
        ],
        ...,
    ]

    schema_version: str = (
        UNIVERSAL_ORCHESTRATION_CONDITIONAL_BRANCHING_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        fan_out = (
            _require_fan_out_coordination(
                self.fan_out_coordination
            )
        )

        evidence = (
            _normalize_condition_evidence(
                self.condition_evidence,
                fan_out_coordination=fan_out,
            )
        )

        if (
            self.schema_version
            !=
            UNIVERSAL_ORCHESTRATION_CONDITIONAL_BRANCHING_SCHEMA_VERSION
        ):

            raise UniversalOrchestrationConditionalBranchingError(
                (
                    "Invalid Conditional Branching "
                    "schema_version."
                ),
                code="invalid_conditional_branching_schema_version",
                value=self.schema_version,
            )

        object.__setattr__(
            self,
            "fan_out_coordination",
            fan_out,
        )

        object.__setattr__(
            self,
            "condition_evidence",
            evidence,
        )

    @property
    def identity(
        self,
    ):

        return (
            self.fan_out_coordination.identity
        )

    @property
    def execution_plan(
        self,
    ):

        return (
            self.fan_out_coordination.execution_plan
        )

    @property
    def source_job_id(
        self,
    ) -> str:

        return (
            self.fan_out_coordination.source_job_id
        )

    @property
    def source_job(
        self,
    ):

        return (
            self.fan_out_coordination.source_job
        )

    @property
    def candidate_branch_job_ids(
        self,
    ) -> tuple[
        str,
        ...,
    ]:

        return (
            self.fan_out_coordination
            .direct_dependent_job_ids
        )

    @property
    def candidate_branch_jobs(
        self,
    ) -> tuple[
        Any,
        ...,
    ]:

        return (
            self.fan_out_coordination
            .direct_dependent_jobs
        )

    @property
    def condition_evidence_map(
        self,
    ) -> Mapping[
        str,
        bool | None,
    ]:

        return (
            _evidence_map(
                self.condition_evidence
            )
        )

    @property
    def branch_dispositions(
        self,
    ) -> Mapping[
        str,
        UniversalOrchestrationBranchDisposition,
    ]:

        return MappingProxyType(
            {
                job_id:
                    disposition_for_condition_evidence(
                        evidence
                    )
                for job_id, evidence
                in self.condition_evidence
            }
        )

    @property
    def selected_job_ids(
        self,
    ) -> tuple[
        str,
        ...,
    ]:

        return tuple(
            job_id
            for job_id, evidence
            in self.condition_evidence
            if evidence is True
        )

    @property
    def excluded_job_ids(
        self,
    ) -> tuple[
        str,
        ...,
    ]:

        return tuple(
            job_id
            for job_id, evidence
            in self.condition_evidence
            if evidence is False
        )

    @property
    def unresolved_job_ids(
        self,
    ) -> tuple[
        str,
        ...,
    ]:

        return tuple(
            job_id
            for job_id, evidence
            in self.condition_evidence
            if evidence is None
        )

    @property
    def selected_jobs(
        self,
    ) -> tuple[
        Any,
        ...,
    ]:

        return tuple(
            self.execution_plan.job_map[
                job_id
            ]
            for job_id
            in self.selected_job_ids
        )

    @property
    def excluded_jobs(
        self,
    ) -> tuple[
        Any,
        ...,
    ]:

        return tuple(
            self.execution_plan.job_map[
                job_id
            ]
            for job_id
            in self.excluded_job_ids
        )

    @property
    def unresolved_jobs(
        self,
    ) -> tuple[
        Any,
        ...,
    ]:

        return tuple(
            self.execution_plan.job_map[
                job_id
            ]
            for job_id
            in self.unresolved_job_ids
        )

    @property
    def resolution(
        self,
    ) -> UniversalOrchestrationBranchResolution:

        if self.unresolved_job_ids:

            return (
                UniversalOrchestrationBranchResolution
                .UNRESOLVED
            )

        return (
            UniversalOrchestrationBranchResolution
            .RESOLVED
        )

    @property
    def is_resolved(
        self,
    ) -> bool:

        return (
            self.resolution
            is UniversalOrchestrationBranchResolution.RESOLVED
        )

    @property
    def has_selected(
        self,
    ) -> bool:

        return bool(
            self.selected_job_ids
        )

    @property
    def has_excluded(
        self,
    ) -> bool:

        return bool(
            self.excluded_job_ids
        )

    @property
    def has_unresolved(
        self,
    ) -> bool:

        return bool(
            self.unresolved_job_ids
        )

    @property
    def branch_decision_id(
        self,
    ) -> str:

        evidence_material = "|".join(
            (
                job_id
                + "="
                + (
                    "true"
                    if evidence is True
                    else
                    "false"
                    if evidence is False
                    else
                    "unresolved"
                )
            )
            for job_id, evidence
            in self.condition_evidence
        )

        material = "|".join(
            (
                "universal_orchestration_conditional_branch_decision_v1",
                self.identity.identity_fingerprint,
                self.source_job_id,
                evidence_material,
            )
        )

        return hashlib.sha256(
            material.encode(
                "utf-8"
            )
        ).hexdigest().upper()


def evaluate_universal_orchestration_conditional_branching(
    *,
    fan_out_coordination: Any,
    condition_evidence: Any = None,
) -> UniversalOrchestrationConditionalBranching:

    fan_out = (
        _require_fan_out_coordination(
            fan_out_coordination
        )
    )

    evidence = (
        _normalize_condition_evidence(
            condition_evidence,
            fan_out_coordination=fan_out,
        )
    )

    return UniversalOrchestrationConditionalBranching(
        fan_out_coordination=fan_out,
        condition_evidence=evidence,
    )


def explain_universal_orchestration_conditional_branching_v1(
) -> Mapping[
    str,
    Any,
]:

    return MappingProxyType(
        {
            "phase":
                "5.1.10",

            "component":
                "Universal Orchestration Conditional Branching",

            "version":
                UNIVERSAL_ORCHESTRATION_CONDITIONAL_BRANCHING_VERSION,

            "schema_version":
                UNIVERSAL_ORCHESTRATION_CONDITIONAL_BRANCHING_SCHEMA_VERSION,

            "stored_fields": (
                "fan_out_coordination",
                "condition_evidence",
                "schema_version",
            ),

            "branch_dispositions": (
                "selected",
                "excluded",
                "unresolved",
            ),

            "resolution_states": (
                "resolved",
                "unresolved",
            ),

            "evidence_rule": (
                "True selects a direct structural branch; "
                "False excludes it; None or omitted evidence "
                "leaves it unresolved."
            ),

            "unknown_false_boundary": (
                "Missing or unknown condition evidence is "
                "UNRESOLVED and is never treated as False."
            ),

            "topology_boundary": (
                "Candidate branches come exclusively from "
                "frozen 5.1.8 direct fan-out membership."
            ),

            "dag_boundary": (
                "5.1.10 does not modify frozen 5.1.5 "
                "execution-plan topology."
            ),

            "fan_in_boundary": (
                "Static 5.1.9 join membership remains unchanged; "
                "later progress/completion authorities may consume "
                "branch exclusion evidence when determining "
                "effective orchestration completion."
            ),

            "progress_boundary": (
                "5.1.11 owns orchestration progress tracking."
            ),

            "persistence_boundary": (
                "5.1.14 owns persistence of branch decisions."
            ),

            "completion_boundary": (
                "5.1.15 owns orchestration completion resolution."
            ),

            "evidence_record_boundary": (
                "5.1.17 owns permanent orchestration evidence "
                "and decision records."
            ),

            "prohibitions": (
                "does not define a domain condition language",
                "does not evaluate arbitrary expressions",
                "does not call eval",
                "does not call exec",
                "does not invoke condition callbacks",
                "does not import caller modules",
                "does not inspect UniversalJob.status",
                "does not inspect UniversalJob payload",
                "does not inspect UniversalJob metadata",
                "does not inspect result references",
                "does not read filesystem condition inputs",
                "does not read network condition inputs",
                "does not read database condition inputs",
                "does not use wall-clock condition inputs",
                "does not change execution-plan topology",
                "does not change fan-out topology",
                "does not change fan-in topology",
                "does not create UniversalJob SKIPPED status",
                "does not mutate UniversalJob.status",
                "does not cancel excluded jobs",
                "does not enqueue selected jobs",
                "does not schedule selected jobs",
                "does not claim selected jobs",
                "does not assign workers",
                "does not acquire worker leases",
                "does not evaluate stage readiness",
                "does not evaluate runtime handoff eligibility",
                "does not dispatch runtime handlers",
                "does not execute runtime handlers",
                "does not execute jobs",
                "does not transition orchestration state",
                "does not access Runtime State Store",
                "does not persist branch decisions",
                "does not record permanent evidence",
                "does not determine orchestration progress",
                "does not determine orchestration completion",
                "does not import Universal Coordination Framework",
                "does not invoke pipeline coordinators",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_ORCHESTRATION_CONDITIONAL_BRANCHING_VERSION",
    "UNIVERSAL_ORCHESTRATION_CONDITIONAL_BRANCHING_SCHEMA_VERSION",
    "UNIVERSAL_ORCHESTRATION_BRANCH_DECISION_HASH_ALGORITHM",
    "UniversalOrchestrationConditionalBranchingError",
    "UniversalOrchestrationBranchDisposition",
    "UniversalOrchestrationBranchResolution",
    "disposition_for_condition_evidence",
    "UniversalOrchestrationConditionalBranching",
    "evaluate_universal_orchestration_conditional_branching",
    "explain_universal_orchestration_conditional_branching_v1",
]
