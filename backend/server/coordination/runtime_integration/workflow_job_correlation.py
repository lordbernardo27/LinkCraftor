from __future__ import annotations

"""
LinkCraftor Universal Coordination Framework
Phase 5.3 - Workflow/Job Correlation

Responsibility:
    Bind one certified Phase 5.2 RuntimeJobMapping to one successfully
    submitted canonical Runtime job identity.

Owns:
    - immutable WorkflowJobCorrelation records
    - job_id -> correlation reverse lookup
    - exact duplicate idempotent reuse
    - conflicting duplicate fail-closed protection
    - deterministic in-process registry behavior

Does NOT:
    - create Universal Jobs
    - generate job_id
    - perform Runtime Registration lookup
    - submit jobs
    - persist Runtime jobs
    - enqueue Runtime jobs
    - dispatch handlers
    - execute business logic
    - mutate pipeline_run_id
    - generate orchestration_run_id
    - perform completion intake
    - perform failure intake
    - persist workflow state

Persistent correlation storage is deferred to Phase 8.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from threading import RLock
from types import MappingProxyType
from typing import Any

from backend.server.coordination.runtime_integration.runtime_job_mapping import (
    RuntimeJobMapping,
)


WORKFLOW_JOB_CORRELATION_VERSION = (
    "workflow_job_correlation_v5.3.0"
)

WORKFLOW_JOB_CORRELATION_SCHEMA_VERSION = (
    "workflow_job_correlation_schema_v1"
)

WORKFLOW_JOB_CORRELATION_FIELD_COUNT = 11


class WorkflowJobCorrelationError(ValueError):
    pass


class WorkflowJobCorrelationValidationError(
    WorkflowJobCorrelationError
):
    def __init__(
        self,
        message: str,
        *,
        violations: tuple[str, ...] = (),
    ) -> None:

        super().__init__(message)

        self.violations = tuple(
            str(item)
            for item in violations
        )


class WorkflowJobCorrelationConflictError(
    WorkflowJobCorrelationError
):
    def __init__(
        self,
        message: str,
        *,
        job_id: str,
    ) -> None:

        super().__init__(message)
        self.job_id = str(job_id)


def _clean_required_text(
    value: Any,
    *,
    field_name: str,
) -> str:

    normalized = str(
        value or ""
    ).strip()

    if not normalized:
        raise WorkflowJobCorrelationValidationError(
            f"{field_name} is required.",
            violations=(
                f"{field_name} is required",
            ),
        )

    return normalized


def _clean_wave_index(
    value: Any,
) -> int:

    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or value < 0
    ):
        raise WorkflowJobCorrelationValidationError(
            "wave_index must be a non-negative integer.",
            violations=(
                "wave_index must be a non-negative integer",
            ),
        )

    return value


def _require_submitted_job_mapping(
    value: Any,
) -> Mapping[str, Any]:

    if not isinstance(
        value,
        Mapping,
    ):
        raise WorkflowJobCorrelationValidationError(
            "submitted_job must be a mapping.",
            violations=(
                "submitted_job must be a mapping",
            ),
        )

    return value


@dataclass(
    frozen=True,
    slots=True,
)
class WorkflowJobCorrelation:
    workflow_id: str
    correlation_id: str
    stage_id: str
    stage_version: str
    workflow_type: str
    workspace_id: str
    job_id: str
    job_type: str
    pipeline_id: str
    runtime_stage: str
    wave_index: int

    def __post_init__(self) -> None:

        for field_name in (
            "workflow_id",
            "correlation_id",
            "stage_id",
            "stage_version",
            "workflow_type",
            "workspace_id",
            "job_id",
            "job_type",
            "pipeline_id",
            "runtime_stage",
        ):
            normalized = _clean_required_text(
                getattr(
                    self,
                    field_name,
                ),
                field_name=field_name,
            )

            object.__setattr__(
                self,
                field_name,
                normalized,
            )

        object.__setattr__(
            self,
            "wave_index",
            _clean_wave_index(
                self.wave_index
            ),
        )


class WorkflowJobCorrelationRegistry:
    def __init__(self) -> None:

        self._by_job_id: dict[
            str,
            WorkflowJobCorrelation,
        ] = {}

        self._lock = RLock()

    def register(
        self,
        correlation: WorkflowJobCorrelation,
    ) -> WorkflowJobCorrelation:

        if not isinstance(
            correlation,
            WorkflowJobCorrelation,
        ):
            raise WorkflowJobCorrelationValidationError(
                (
                    "correlation must be "
                    "WorkflowJobCorrelation."
                ),
                violations=(
                    (
                        "registry accepts only "
                        "WorkflowJobCorrelation"
                    ),
                ),
            )

        with self._lock:

            existing = self._by_job_id.get(
                correlation.job_id
            )

            if existing is None:
                self._by_job_id[
                    correlation.job_id
                ] = correlation

                return correlation

            if existing == correlation:
                return existing

            raise WorkflowJobCorrelationConflictError(
                (
                    "Canonical job_id is already bound "
                    "to a different workflow/job correlation."
                ),
                job_id=correlation.job_id,
            )

    def get_by_job_id(
        self,
        job_id: str,
    ) -> WorkflowJobCorrelation | None:

        normalized_job_id = _clean_required_text(
            job_id,
            field_name="job_id",
        )

        with self._lock:
            return self._by_job_id.get(
                normalized_job_id
            )

    def require_by_job_id(
        self,
        job_id: str,
    ) -> WorkflowJobCorrelation:

        correlation = self.get_by_job_id(
            job_id
        )

        if correlation is None:
            raise WorkflowJobCorrelationValidationError(
                (
                    "No Workflow/Job Correlation exists "
                    "for canonical job_id."
                ),
                violations=(
                    "job_id is not registered",
                ),
            )

        return correlation

    def all_for_workflow(
        self,
        workflow_id: str,
    ) -> tuple[
        WorkflowJobCorrelation,
        ...,
    ]:

        normalized_workflow_id = (
            _clean_required_text(
                workflow_id,
                field_name="workflow_id",
            )
        )

        with self._lock:
            return tuple(
                item
                for item
                in self._by_job_id.values()
                if item.workflow_id
                == normalized_workflow_id
            )

    def count(self) -> int:
        with self._lock:
            return len(
                self._by_job_id
            )

    def clear(self) -> None:
        with self._lock:
            self._by_job_id.clear()


def correlate_submitted_job(
    *,
    mapping: RuntimeJobMapping,
    submitted_job: Mapping[str, Any],
    registry: WorkflowJobCorrelationRegistry,
) -> WorkflowJobCorrelation:

    if not isinstance(
        mapping,
        RuntimeJobMapping,
    ):
        raise WorkflowJobCorrelationValidationError(
            "mapping must be RuntimeJobMapping.",
            violations=(
                (
                    "Phase 5.3 requires certified "
                    "Phase 5.2 mapping"
                ),
            ),
        )

    if not isinstance(
        registry,
        WorkflowJobCorrelationRegistry,
    ):
        raise WorkflowJobCorrelationValidationError(
            (
                "registry must be "
                "WorkflowJobCorrelationRegistry."
            ),
            violations=(
                (
                    "Phase 5.3 requires "
                    "WorkflowJobCorrelationRegistry"
                ),
            ),
        )

    submitted = _require_submitted_job_mapping(
        submitted_job
    )

    request = mapping.creation_request

    submitted_job_id = _clean_required_text(
        submitted.get("job_id"),
        field_name="submitted_job.job_id",
    )

    submitted_workspace_id = _clean_required_text(
        submitted.get("workspace_id"),
        field_name="submitted_job.workspace_id",
    )

    submitted_job_type = _clean_required_text(
        submitted.get("job_type"),
        field_name="submitted_job.job_type",
    )

    submitted_pipeline = _clean_required_text(
        submitted.get("pipeline"),
        field_name="submitted_job.pipeline",
    )

    submitted_stage = _clean_required_text(
        submitted.get("stage"),
        field_name="submitted_job.stage",
    )

    expected_workspace_id = _clean_required_text(
        request.workspace_id,
        field_name="creation_request.workspace_id",
    )

    expected_job_type = _clean_required_text(
        request.job_type,
        field_name="creation_request.job_type",
    )

    expected_pipeline = _clean_required_text(
        request.pipeline,
        field_name="creation_request.pipeline",
    )

    expected_stage = _clean_required_text(
        request.stage,
        field_name="creation_request.stage",
    )

    mismatches = []

    if submitted_workspace_id != expected_workspace_id:
        mismatches.append(
            "workspace_id mismatch"
        )

    if submitted_job_type != expected_job_type:
        mismatches.append(
            "job_type mismatch"
        )

    if submitted_pipeline != expected_pipeline:
        mismatches.append(
            "pipeline mismatch"
        )

    if submitted_stage != expected_stage:
        mismatches.append(
            "stage mismatch"
        )

    if mismatches:
        raise WorkflowJobCorrelationValidationError(
            (
                "Submitted Runtime job does not match "
                "the certified Phase 5.2 mapping."
            ),
            violations=tuple(
                mismatches
            ),
        )

    coordination = request.metadata.get(
        "coordination"
    )

    if not isinstance(
        coordination,
        Mapping,
    ):
        raise WorkflowJobCorrelationValidationError(
            (
                "Phase 5.2 creation request is missing "
                "coordination metadata."
            ),
            violations=(
                (
                    "creation_request.metadata.coordination "
                    "must exist"
                ),
            ),
        )

    workflow_id = _clean_required_text(
        mapping.workflow_id,
        field_name="workflow_id",
    )

    correlation_id = _clean_required_text(
        mapping.correlation_id,
        field_name="correlation_id",
    )

    stage_id = _clean_required_text(
        mapping.stage_id,
        field_name="stage_id",
    )

    metadata_workflow_id = _clean_required_text(
        coordination.get("workflow_id"),
        field_name="coordination.workflow_id",
    )

    metadata_correlation_id = _clean_required_text(
        coordination.get("correlation_id"),
        field_name="coordination.correlation_id",
    )

    metadata_stage_id = _clean_required_text(
        coordination.get("stage_id"),
        field_name="coordination.stage_id",
    )

    if metadata_workflow_id != workflow_id:
        raise WorkflowJobCorrelationValidationError(
            (
                "Phase 5.2 workflow identity evidence "
                "does not match RuntimeJobMapping."
            ),
            violations=(
                "workflow_id evidence mismatch",
            ),
        )

    if metadata_correlation_id != correlation_id:
        raise WorkflowJobCorrelationValidationError(
            (
                "Phase 5.2 correlation identity evidence "
                "does not match RuntimeJobMapping."
            ),
            violations=(
                "correlation_id evidence mismatch",
            ),
        )

    if metadata_stage_id != stage_id:
        raise WorkflowJobCorrelationValidationError(
            (
                "Phase 5.2 stage identity evidence "
                "does not match RuntimeJobMapping."
            ),
            violations=(
                "stage_id evidence mismatch",
            ),
        )

    correlation = WorkflowJobCorrelation(
        workflow_id=workflow_id,
        correlation_id=correlation_id,
        stage_id=stage_id,
        stage_version=_clean_required_text(
            coordination.get("stage_version"),
            field_name="coordination.stage_version",
        ),
        workflow_type=_clean_required_text(
            coordination.get("workflow_type"),
            field_name="coordination.workflow_type",
        ),
        workspace_id=submitted_workspace_id,
        job_id=submitted_job_id,
        job_type=submitted_job_type,
        pipeline_id=expected_pipeline,
        runtime_stage=expected_stage,
        wave_index=_clean_wave_index(
            mapping.wave_index
        ),
    )

    return registry.register(
        correlation
    )


def workflow_job_correlation_snapshot(
    correlation: WorkflowJobCorrelation,
) -> Mapping[str, Any]:

    if not isinstance(
        correlation,
        WorkflowJobCorrelation,
    ):
        raise WorkflowJobCorrelationValidationError(
            (
                "correlation must be "
                "WorkflowJobCorrelation."
            ),
            violations=(
                (
                    "snapshot input must be "
                    "WorkflowJobCorrelation"
                ),
            ),
        )

    return MappingProxyType(
        {
            "workflow_id":
                correlation.workflow_id,

            "correlation_id":
                correlation.correlation_id,

            "stage_id":
                correlation.stage_id,

            "stage_version":
                correlation.stage_version,

            "workflow_type":
                correlation.workflow_type,

            "workspace_id":
                correlation.workspace_id,

            "job_id":
                correlation.job_id,

            "job_type":
                correlation.job_type,

            "pipeline_id":
                correlation.pipeline_id,

            "runtime_stage":
                correlation.runtime_stage,

            "wave_index":
                correlation.wave_index,

            "version":
                WORKFLOW_JOB_CORRELATION_VERSION,

            "schema_version":
                WORKFLOW_JOB_CORRELATION_SCHEMA_VERSION,
        }
    )


def explain_workflow_job_correlation_v5_3(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "5.3",

            "component":
                "Workflow/Job Correlation",

            "version":
                WORKFLOW_JOB_CORRELATION_VERSION,

            "schema_version":
                WORKFLOW_JOB_CORRELATION_SCHEMA_VERSION,

            "coordination_input":
                "RuntimeJobMapping",

            "runtime_identity_input":
                "successful submitted canonical job",

            "binding_time":
                "after successful canonical submission",

            "primary_reverse_lookup":
                "job_id",

            "duplicate_policy":
                MappingProxyType(
                    {
                        "exact_duplicate":
                            "idempotent_reuse",

                        "conflicting_duplicate":
                            "fail_closed",
                    }
                ),

            "cross_validation":
                (
                    "workspace_id",
                    "job_type",
                    "pipeline",
                    "stage",
                ),

            "identity_boundaries":
                MappingProxyType(
                    {
                        "job_id_generation":
                            False,

                        "job_id_rewrite":
                            False,

                        "workflow_id_to_pipeline_run_id":
                            False,

                        "correlation_id_to_pipeline_run_id":
                            False,

                        "orchestration_run_id_generation":
                            False,
                    }
                ),

            "execution_properties":
                MappingProxyType(
                    {
                        "universal_job_creation":
                            False,

                        "runtime_registration_lookup":
                            False,

                        "submission":
                            False,

                        "runtime_persistence":
                            False,

                        "queue_write":
                            False,

                        "dispatch":
                            False,

                        "business_execution":
                            False,

                        "workflow_lifecycle_transition":
                            False,

                        "completion_processing":
                            False,

                        "failure_processing":
                            False,

                        "persistent_correlation_storage":
                            False,
                    }
                ),

            "persistence_owner":
                "Phase 8 Workflow State Persistence",
        }
    )


_default_registry = WorkflowJobCorrelationRegistry()


def get_workflow_job_correlation_registry(
) -> WorkflowJobCorrelationRegistry:

    return _default_registry


def register_workflow_job_correlation(
    *,
    mapping: RuntimeJobMapping,
    submitted_job: Mapping[str, Any],
    registry: WorkflowJobCorrelationRegistry | None = None,
) -> WorkflowJobCorrelation:

    effective_registry = (
        registry
        if registry is not None
        else _default_registry
    )

    return correlate_submitted_job(
        mapping=mapping,
        submitted_job=submitted_job,
        registry=effective_registry,
    )


def resolve_workflow_job_correlation(
    *,
    job_id: str,
    registry: WorkflowJobCorrelationRegistry | None = None,
) -> WorkflowJobCorrelation:

    effective_registry = (
        registry
        if registry is not None
        else _default_registry
    )

    return effective_registry.require_by_job_id(
        job_id
    )


__all__ = (
    "WORKFLOW_JOB_CORRELATION_VERSION",
    "WORKFLOW_JOB_CORRELATION_SCHEMA_VERSION",
    "WORKFLOW_JOB_CORRELATION_FIELD_COUNT",
    "WorkflowJobCorrelationError",
    "WorkflowJobCorrelationValidationError",
    "WorkflowJobCorrelationConflictError",
    "WorkflowJobCorrelation",
    "WorkflowJobCorrelationRegistry",
    "correlate_submitted_job",
    "register_workflow_job_correlation",
    "resolve_workflow_job_correlation",
    "get_workflow_job_correlation_registry",
    "workflow_job_correlation_snapshot",
    "explain_workflow_job_correlation_v5_3",
)
