from __future__ import annotations

import enum
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Final, Mapping

from backend.server.runtime.universal_jobs.contract import (
    UniversalJob,
    UniversalJobStatus,
)

from backend.server.runtime.universal_jobs.status import (
    normalize_universal_job_status,
)

from backend.server.runtime.universal_orchestration.run_identity import (
    UniversalOrchestrationRunIdentity,
)


UNIVERSAL_ORCHESTRATION_DEPENDENCY_RESOLUTION_VERSION = (
    "universal_orchestration_dependency_resolution_v5.1.4"
)

UNIVERSAL_ORCHESTRATION_DEPENDENCY_RESOLUTION_SCHEMA_VERSION = (
    "universal_orchestration_dependency_resolution_schema_v1"
)


class UniversalOrchestrationDependencyResolutionError(
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


class UniversalOrchestrationDependencyClassification(
    str,
    enum.Enum,
):

    SATISFIED = "satisfied"

    UNRESOLVED = "unresolved"

    TERMINAL_UNSATISFIED = "terminal_unsatisfied"

    MISSING = "missing"


SATISFIED_UNIVERSAL_JOB_STATUSES: Final[
    frozenset[UniversalJobStatus]
] = frozenset(
    {
        UniversalJobStatus.SUCCEEDED,
    }
)


TERMINAL_UNSATISFIED_UNIVERSAL_JOB_STATUSES: Final[
    frozenset[UniversalJobStatus]
] = frozenset(
    {
        UniversalJobStatus.FAILED,
        UniversalJobStatus.CANCELLED,
        UniversalJobStatus.DEAD_LETTER,
        UniversalJobStatus.EXPIRED,
    }
)


UNRESOLVED_UNIVERSAL_JOB_STATUSES: Final[
    frozenset[UniversalJobStatus]
] = frozenset(
    {
        UniversalJobStatus.CREATED,
        UniversalJobStatus.QUEUED,
        UniversalJobStatus.SCHEDULED,
        UniversalJobStatus.LEASED,
        UniversalJobStatus.RUNNING,
        UniversalJobStatus.SUSPENDED,
    }
)


def _require_orchestration_run_identity(
    value: Any,
) -> UniversalOrchestrationRunIdentity:

    if not isinstance(
        value,
        UniversalOrchestrationRunIdentity,
    ):

        raise UniversalOrchestrationDependencyResolutionError(
            (
                "identity must be a "
                "UniversalOrchestrationRunIdentity."
            ),
            code="invalid_dependency_resolution_identity",
            value=value,
        )

    return value


def _require_universal_job(
    value: Any,
) -> UniversalJob:

    if not isinstance(
        value,
        UniversalJob,
    ):

        raise UniversalOrchestrationDependencyResolutionError(
            "target_job must be a UniversalJob.",
            code="invalid_dependency_resolution_target_job",
            value=value,
        )

    return value


def _normalize_dependency_statuses(
    *,
    dependency_job_ids: tuple[str, ...],
    dependency_statuses: Any,
) -> tuple[
    tuple[
        str,
        UniversalJobStatus,
    ],
    ...,
]:

    if dependency_statuses is None:

        dependency_statuses = {}

    if not isinstance(
        dependency_statuses,
        Mapping,
    ):

        raise UniversalOrchestrationDependencyResolutionError(
            "dependency_statuses must be a mapping.",
            code="invalid_dependency_status_mapping",
            value=dependency_statuses,
        )

    expected_ids = frozenset(
        dependency_job_ids
    )

    normalized_items = []

    seen_ids = set()

    for raw_job_id, raw_status in (
        dependency_statuses.items()
    ):

        if not isinstance(
            raw_job_id,
            str,
        ):

            raise UniversalOrchestrationDependencyResolutionError(
                "Dependency status keys must be job-id strings.",
                code="invalid_dependency_status_job_id",
                value=raw_job_id,
            )

        job_id = raw_job_id.strip()

        if not job_id:

            raise UniversalOrchestrationDependencyResolutionError(
                "Dependency status job-id must not be empty.",
                code="invalid_dependency_status_job_id",
                value=raw_job_id,
            )

        if any(
            character.isspace()
            for character in job_id
        ):

            raise UniversalOrchestrationDependencyResolutionError(
                (
                    "Dependency status job-id must not contain "
                    "internal whitespace."
                ),
                code="invalid_dependency_status_job_id",
                value=raw_job_id,
            )

        if job_id in seen_ids:

            raise UniversalOrchestrationDependencyResolutionError(
                "Duplicate dependency status evidence.",
                code="duplicate_dependency_status_evidence",
                value=job_id,
            )

        seen_ids.add(
            job_id
        )

        if job_id not in expected_ids:

            raise UniversalOrchestrationDependencyResolutionError(
                (
                    "Dependency status evidence was supplied for a "
                    "job that is not a dependency of target_job."
                ),
                code="extraneous_dependency_status_evidence",
                value=job_id,
            )

        try:

            status = (
                normalize_universal_job_status(
                    raw_status
                )
            )

        except Exception as exc:

            raise UniversalOrchestrationDependencyResolutionError(
                "Invalid dependency Universal Job status.",
                code="invalid_dependency_job_status",
                value=raw_status,
            ) from exc

        normalized_items.append(
            (
                job_id,
                status,
            )
        )

    return tuple(
        sorted(
            normalized_items,
            key=lambda item: item[0],
        )
    )


def classify_universal_orchestration_dependency_status(
    value: Any,
) -> UniversalOrchestrationDependencyClassification:

    try:

        status = (
            normalize_universal_job_status(
                value
            )
        )

    except Exception as exc:

        raise UniversalOrchestrationDependencyResolutionError(
            "Invalid dependency Universal Job status.",
            code="invalid_dependency_job_status",
            value=value,
        ) from exc

    if status in SATISFIED_UNIVERSAL_JOB_STATUSES:

        return (
            UniversalOrchestrationDependencyClassification.SATISFIED
        )

    if (
        status
        in TERMINAL_UNSATISFIED_UNIVERSAL_JOB_STATUSES
    ):

        return (
            UniversalOrchestrationDependencyClassification
            .TERMINAL_UNSATISFIED
        )

    if status in UNRESOLVED_UNIVERSAL_JOB_STATUSES:

        return (
            UniversalOrchestrationDependencyClassification.UNRESOLVED
        )

    raise UniversalOrchestrationDependencyResolutionError(
        "Universal Job status has no dependency classification.",
        code="unclassified_dependency_job_status",
        value=status,
    )


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalOrchestrationDependencyResolution:

    identity: UniversalOrchestrationRunIdentity

    target_job: UniversalJob

    dependency_statuses: tuple[
        tuple[
            str,
            UniversalJobStatus,
        ],
        ...,
    ] = ()

    schema_version: str = (
        UNIVERSAL_ORCHESTRATION_DEPENDENCY_RESOLUTION_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        identity = (
            _require_orchestration_run_identity(
                self.identity
            )
        )

        target_job = (
            _require_universal_job(
                self.target_job
            )
        )

        if (
            target_job.job_id
            not in identity.job_ids
        ):

            raise UniversalOrchestrationDependencyResolutionError(
                (
                    "target_job must belong to the "
                    "5.1.1 orchestration contract."
                ),
                code="target_job_outside_orchestration_contract",
                value=target_job.job_id,
            )

        if (
            target_job.workspace_id
            != identity.workspace_id
        ):

            raise UniversalOrchestrationDependencyResolutionError(
                (
                    "target_job workspace_id does not match "
                    "orchestration identity."
                ),
                code="dependency_target_workspace_mismatch",
                value=target_job.workspace_id,
            )

        if (
            target_job.pipeline
            != identity.pipeline
        ):

            raise UniversalOrchestrationDependencyResolutionError(
                (
                    "target_job pipeline does not match "
                    "orchestration identity."
                ),
                code="dependency_target_pipeline_mismatch",
                value=target_job.pipeline,
            )

        outside_contract = tuple(
            dependency_job_id
            for dependency_job_id
            in target_job.dependency_job_ids
            if dependency_job_id
            not in identity.job_ids
        )

        if outside_contract:

            raise UniversalOrchestrationDependencyResolutionError(
                (
                    "All target_job dependencies must belong "
                    "to the 5.1.1 orchestration contract."
                ),
                code="dependency_outside_orchestration_contract",
                value=outside_contract,
            )

        normalized_statuses = (
            _normalize_dependency_statuses(
                dependency_job_ids=(
                    target_job.dependency_job_ids
                ),
                dependency_statuses=dict(
                    self.dependency_statuses
                ),
            )
        )

        if (
            self.schema_version
            !=
            UNIVERSAL_ORCHESTRATION_DEPENDENCY_RESOLUTION_SCHEMA_VERSION
        ):

            raise UniversalOrchestrationDependencyResolutionError(
                (
                    "Invalid Dependency Resolution "
                    "schema_version."
                ),
                code="invalid_dependency_resolution_schema_version",
                value=self.schema_version,
            )

        object.__setattr__(
            self,
            "identity",
            identity,
        )

        object.__setattr__(
            self,
            "target_job",
            target_job,
        )

        object.__setattr__(
            self,
            "dependency_statuses",
            normalized_statuses,
        )

    @property
    def job_id(
        self,
    ) -> str:

        return self.target_job.job_id

    @property
    def dependency_job_ids(
        self,
    ) -> tuple[str, ...]:

        return (
            self.target_job.dependency_job_ids
        )

    @property
    def dependency_count(
        self,
    ) -> int:

        return len(
            self.dependency_job_ids
        )

    @property
    def dependency_status_map(
        self,
    ) -> Mapping[
        str,
        UniversalJobStatus,
    ]:

        return MappingProxyType(
            dict(
                self.dependency_statuses
            )
        )

    @property
    def satisfied_dependency_ids(
        self,
    ) -> tuple[str, ...]:

        statuses = (
            self.dependency_status_map
        )

        return tuple(
            dependency_job_id
            for dependency_job_id
            in self.dependency_job_ids
            if (
                dependency_job_id
                in statuses
                and
                statuses[
                    dependency_job_id
                ]
                in SATISFIED_UNIVERSAL_JOB_STATUSES
            )
        )

    @property
    def unresolved_dependency_ids(
        self,
    ) -> tuple[str, ...]:

        statuses = (
            self.dependency_status_map
        )

        return tuple(
            dependency_job_id
            for dependency_job_id
            in self.dependency_job_ids
            if (
                dependency_job_id
                in statuses
                and
                statuses[
                    dependency_job_id
                ]
                in UNRESOLVED_UNIVERSAL_JOB_STATUSES
            )
        )

    @property
    def terminal_unsatisfied_dependency_ids(
        self,
    ) -> tuple[str, ...]:

        statuses = (
            self.dependency_status_map
        )

        return tuple(
            dependency_job_id
            for dependency_job_id
            in self.dependency_job_ids
            if (
                dependency_job_id
                in statuses
                and
                statuses[
                    dependency_job_id
                ]
                in TERMINAL_UNSATISFIED_UNIVERSAL_JOB_STATUSES
            )
        )

    @property
    def missing_dependency_ids(
        self,
    ) -> tuple[str, ...]:

        statuses = (
            self.dependency_status_map
        )

        return tuple(
            dependency_job_id
            for dependency_job_id
            in self.dependency_job_ids
            if dependency_job_id
            not in statuses
        )

    @property
    def all_dependencies_satisfied(
        self,
    ) -> bool:

        return (
            len(
                self.satisfied_dependency_ids
            )
            == self.dependency_count
        )

    @property
    def has_unresolved_dependencies(
        self,
    ) -> bool:

        return bool(
            self.unresolved_dependency_ids
        )

    @property
    def has_terminal_dependency_failure(
        self,
    ) -> bool:

        return bool(
            self.terminal_unsatisfied_dependency_ids
        )

    @property
    def has_missing_dependency_evidence(
        self,
    ) -> bool:

        return bool(
            self.missing_dependency_ids
        )

    def classification_for_dependency(
        self,
        dependency_job_id: Any,
    ) -> UniversalOrchestrationDependencyClassification:

        if not isinstance(
            dependency_job_id,
            str,
        ):

            raise UniversalOrchestrationDependencyResolutionError(
                "dependency_job_id must be a string.",
                code="invalid_dependency_lookup_job_id",
                value=dependency_job_id,
            )

        normalized = (
            dependency_job_id.strip()
        )

        if (
            normalized
            not in self.dependency_job_ids
        ):

            raise UniversalOrchestrationDependencyResolutionError(
                (
                    "dependency_job_id is not a dependency "
                    "of target_job."
                ),
                code="unknown_dependency_lookup_job_id",
                value=dependency_job_id,
            )

        status = (
            self.dependency_status_map.get(
                normalized
            )
        )

        if status is None:

            return (
                UniversalOrchestrationDependencyClassification.MISSING
            )

        return (
            classify_universal_orchestration_dependency_status(
                status
            )
        )


def resolve_universal_orchestration_dependencies(
    *,
    identity: Any,
    target_job: Any,
    dependency_statuses: Any = None,
) -> UniversalOrchestrationDependencyResolution:

    canonical_identity = (
        _require_orchestration_run_identity(
            identity
        )
    )

    canonical_target_job = (
        _require_universal_job(
            target_job
        )
    )

    normalized_statuses = (
        _normalize_dependency_statuses(
            dependency_job_ids=(
                canonical_target_job.dependency_job_ids
            ),
            dependency_statuses=dependency_statuses,
        )
    )

    return UniversalOrchestrationDependencyResolution(
        identity=canonical_identity,
        target_job=canonical_target_job,
        dependency_statuses=normalized_statuses,
    )


def explain_universal_orchestration_dependency_resolution_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "5.1.4",

            "component":
                "Universal Orchestration Dependency Resolution",

            "version":
                UNIVERSAL_ORCHESTRATION_DEPENDENCY_RESOLUTION_VERSION,

            "schema_version":
                UNIVERSAL_ORCHESTRATION_DEPENDENCY_RESOLUTION_SCHEMA_VERSION,

            "stored_fields": (
                "identity",
                "target_job",
                "dependency_statuses",
                "schema_version",
            ),

            "classification": MappingProxyType(
                {
                    "satisfied": (
                        UniversalJobStatus.SUCCEEDED.value,
                    ),

                    "unresolved": tuple(
                        status.value
                        for status
                        in (
                            UniversalJobStatus.CREATED,
                            UniversalJobStatus.QUEUED,
                            UniversalJobStatus.SCHEDULED,
                            UniversalJobStatus.LEASED,
                            UniversalJobStatus.RUNNING,
                            UniversalJobStatus.SUSPENDED,
                        )
                    ),

                    "terminal_unsatisfied": tuple(
                        status.value
                        for status
                        in (
                            UniversalJobStatus.FAILED,
                            UniversalJobStatus.CANCELLED,
                            UniversalJobStatus.DEAD_LETTER,
                            UniversalJobStatus.EXPIRED,
                        )
                    ),

                    "missing": (
                        "no caller-supplied status evidence"
                    ),
                }
            ),

            "dependency_source_rule": (
                "dependency_job_ids come only from the canonical "
                "Universal Job target_job; 5.1.4 does not redefine "
                "or mutate Universal Job lineage."
            ),

            "membership_rule": (
                "target_job and every target_job dependency must "
                "belong to the frozen 5.1.1 orchestration contract."
            ),

            "parent_rule": (
                "parent_job_id remains Universal Job lineage evidence "
                "and is not implicitly treated as a dependency."
            ),

            "evidence_rule": (
                "Dependency status evidence is caller supplied; "
                "5.1.4 performs no persistence lookup."
            ),

            "missing_rule": (
                "A dependency without supplied status evidence is "
                "MISSING, not failed and not satisfied."
            ),

            "zero_dependency_rule": (
                "A target job with zero dependencies has "
                "all_dependencies_satisfied=True."
            ),

            "cycle_boundary": (
                "5.1.4 does not perform cross-job cycle detection; "
                "dependency graph structural validation belongs to "
                "5.1.5 Execution Planning."
            ),

            "planning_boundary": (
                "5.1.4 does not determine execution order; "
                "execution planning belongs to 5.1.5."
            ),

            "readiness_boundary": (
                "Dependency resolution evidence is not a READY or "
                "BLOCKED decision; readiness belongs to 5.1.6."
            ),

            "state_boundary": (
                "5.1.4 does not transition the 5.1.3 "
                "Orchestration State Model."
            ),

            "prohibitions": (
                "does not redefine dependency_job_ids",
                "does not mutate Universal Job lineage",
                "does not treat parent_job_id as an implicit dependency",
                "does not perform cross-job cycle detection",
                "does not read Runtime State Store",
                "does not query job persistence",
                "does not mutate Universal Jobs",
                "does not transition orchestration state",
                "does not determine execution order",
                "does not create execution plans",
                "does not determine READY",
                "does not determine BLOCKED",
                "does not enqueue jobs",
                "does not claim jobs",
                "does not assign workers",
                "does not acquire worker leases",
                "does not register runtime handlers",
                "does not dispatch runtime handlers",
                "does not execute runtime handlers",
                "does not execute jobs",
                "does not import Universal Coordination Framework",
                "does not invoke pipeline coordinators",
                "does not persist dependency resolution",
                "does not use wall clock",
                "does not perform filesystem I/O",
                "does not perform network I/O",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_ORCHESTRATION_DEPENDENCY_RESOLUTION_VERSION",
    "UNIVERSAL_ORCHESTRATION_DEPENDENCY_RESOLUTION_SCHEMA_VERSION",
    "UniversalOrchestrationDependencyResolutionError",
    "UniversalOrchestrationDependencyClassification",
    "SATISFIED_UNIVERSAL_JOB_STATUSES",
    "TERMINAL_UNSATISFIED_UNIVERSAL_JOB_STATUSES",
    "UNRESOLVED_UNIVERSAL_JOB_STATUSES",
    "classify_universal_orchestration_dependency_status",
    "UniversalOrchestrationDependencyResolution",
    "resolve_universal_orchestration_dependencies",
    "explain_universal_orchestration_dependency_resolution_v1",
]
