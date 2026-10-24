from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any

from backend.server.coordination.dependency_planning.cycle_detection import (
    require_acyclic_dependency_graph,
)
from backend.server.coordination.dependency_planning.dependency_graph import (
    DependencyEdge,
    DependencyGraph,
    create_dependency_graph,
)
from backend.server.coordination.dependency_planning.dependency_validation import (
    require_valid_dependency_graph,
)
from backend.server.coordination.dependency_planning.execution_planner import (
    ExecutionPlan,
    ExecutionWave,
    create_execution_plan,
)
from backend.server.coordination.dependency_planning.planning_certification import (
    PlanningCertificationResult,
    certify_dependency_planning,
)
from backend.server.coordination.dependency_planning.runnable_stage_resolver import (
    RunnableStageResolution,
    create_runnable_stage_state,
    resolve_runnable_stages,
)
from backend.server.coordination.universal_stages.contract import (
    StageExecutionTarget,
    UniversalStageReference,
)
from backend.server.runtime.universal_runtime_registration import (
    ensure_persisted_runtime_registrations_loaded,
    get_runtime_registration,
)


CONNECTED_DOMAIN_MANIFEST_SCHEMA_VERSION = (
    "connected_domain_pipeline_manifest_v1"
)
CONNECTED_DOMAIN_MANIFEST_VERSION = (
    "connected_domain_pipeline_manifest_v1.0.0"
)
CONNECTED_DOMAIN_PIPELINE_ID = "connect_domain"
CONNECTED_DOMAIN_WORKFLOW_TYPE = "connect_domain"
CONNECTED_DOMAIN_WORKFLOW_VERSION = "1.0.0"
CONNECTED_DOMAIN_WORKFLOW_CONTRACT_VERSION = (
    "universal_workflow_contract_v1.1.0"
)
CONNECTED_DOMAIN_STAGE_VERSION = "1.0.0"

CONNECTED_DOMAIN_STAGE_IDS = (
    "connect_domain",
    "site_sources",
    "url_cleaner",
    "site_pages",
    "live_domain_target_pool",
    "active_target_set",
)

CONNECTED_DOMAIN_STAGE_JOB_TYPES = tuple(
    stage_id + "_stage"
    for stage_id in CONNECTED_DOMAIN_STAGE_IDS
)

CONNECTED_DOMAIN_DEPENDENCIES = tuple(
    zip(
        CONNECTED_DOMAIN_STAGE_IDS,
        CONNECTED_DOMAIN_STAGE_IDS[1:],
    )
)


class ConnectedDomainPipelineManifestError(RuntimeError):
    """Connected Domain manifest construction failed closed."""


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType(
            {
                str(key): _freeze(item)
                for key, item in value.items()
            }
        )

    if isinstance(value, (tuple, list)):
        return tuple(
            _freeze(item)
            for item in value
        )

    if isinstance(value, (set, frozenset)):
        return tuple(
            sorted(
                (_freeze(item) for item in value),
                key=repr,
            )
        )

    return value


def _plain(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            str(key): _plain(item)
            for key, item in value.items()
        }

    if isinstance(value, (tuple, list)):
        return [
            _plain(item)
            for item in value
        ]

    if isinstance(value, (set, frozenset)):
        return sorted(
            (_plain(item) for item in value),
            key=repr,
        )

    if isinstance(value, Enum):
        return value.value

    return value


def _canonical_json(value: Any) -> str:
    return json.dumps(
        _plain(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )


def _sha256(value: Any) -> str:
    return hashlib.sha256(
        _canonical_json(value).encode("utf-8")
    ).hexdigest()


def _registration_record(
    registration: Any,
    *,
    job_type: str,
) -> dict[str, Any]:
    if registration is None:
        raise ConnectedDomainPipelineManifestError(
            "Required runtime registration is unavailable: "
            + job_type
        )

    if isinstance(registration, Mapping):
        return dict(registration)

    if hasattr(registration, "to_public_dict"):
        record = registration.to_public_dict()

        if isinstance(record, Mapping):
            return dict(record)

    raise ConnectedDomainPipelineManifestError(
        "Runtime registration is not publicly serializable: "
        + job_type
    )


def _expected_neighbors(
    stage_index: int,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    predecessors = (
        ()
        if stage_index == 0
        else (
            CONNECTED_DOMAIN_STAGE_IDS[
                stage_index - 1
            ],
        )
    )

    successors = (
        ()
        if stage_index
        == len(CONNECTED_DOMAIN_STAGE_IDS) - 1
        else (
            CONNECTED_DOMAIN_STAGE_IDS[
                stage_index + 1
            ],
        )
    )

    return predecessors, successors


def _validate_registration(
    record: Mapping[str, Any],
    *,
    stage_id: str,
    job_type: str,
    stage_index: int,
) -> None:
    expected_predecessors, expected_successors = (
        _expected_neighbors(stage_index)
    )

    violations: list[str] = []

    if record.get("job_type") != job_type:
        violations.append("job_type")

    if record.get("pipeline") != CONNECTED_DOMAIN_PIPELINE_ID:
        violations.append("pipeline")

    if record.get("stage") != stage_id:
        violations.append("stage")

    if record.get("persistent") is not True:
        violations.append("persistent")

    if tuple(record.get("predecessor_stages") or ()) != expected_predecessors:
        violations.append("predecessor_stages")

    if tuple(record.get("successor_stages") or ()) != expected_successors:
        violations.append("successor_stages")

    payload_fields = tuple(
        record.get("required_payload_fields")
        or ()
    )

    if not payload_fields:
        violations.append("required_payload_fields")

    handler_ref = str(
        record.get("handler_ref")
        or ""
    )

    if not handler_ref:
        violations.append("handler_ref")

    fingerprint = str(
        record.get("registration_fingerprint")
        or ""
    )

    if (
        len(fingerprint) != 64
        or any(
            character not in "0123456789abcdef"
            for character in fingerprint.lower()
        )
    ):
        violations.append("registration_fingerprint")

    if violations:
        raise ConnectedDomainPipelineManifestError(
            "Runtime registration contract mismatch for "
            + job_type
            + ": "
            + ", ".join(violations)
        )


def _stage_reference(
    record: Mapping[str, Any],
    *,
    stage_id: str,
    job_type: str,
    stage_index: int,
) -> UniversalStageReference:
    return UniversalStageReference(
        stage_id=stage_id,
        stage_version=CONNECTED_DOMAIN_STAGE_VERSION,
        pipeline_id=CONNECTED_DOMAIN_PIPELINE_ID,
        workflow_type=CONNECTED_DOMAIN_WORKFLOW_TYPE,
        workflow_contract_version=(
            CONNECTED_DOMAIN_WORKFLOW_CONTRACT_VERSION
        ),
        execution_target=(
            StageExecutionTarget.UNIVERSAL_RUNTIME
        ),
        job_type=job_type,
        runtime_stage=stage_id,
        required_payload_fields=tuple(
            record.get("required_payload_fields")
            or ()
        ),
        metadata={
            "handler_ref": record.get("handler_ref"),
            "pipeline_stage_order": stage_index + 1,
            "registration_fingerprint": record.get(
                "registration_fingerprint"
            ),
            "registration_persistent": True,
        },
    )


def _planning_certification_dict(
    result: PlanningCertificationResult,
) -> Mapping[str, Any]:
    return {
        "is_certified": result.is_certified,
        "check_count": result.check_count,
        "passed_check_count": result.passed_check_count,
        "failed_check_count": result.failed_check_count,
        "failed_checks": result.failed_checks,
        "checks": tuple(
            {
                "name": check.name,
                "passed": check.passed,
                "detail": check.detail,
            }
            for check in result.checks
        ),
        "component_shas": result.component_shas,
        "composite_fingerprint": result.composite_fingerprint,
        "dependency_graph_version": (
            result.dependency_graph_version
        ),
        "dependency_validation_version": (
            result.dependency_validation_version
        ),
        "cycle_detection_version": (
            result.cycle_detection_version
        ),
        "runnable_stage_resolver_version": (
            result.runnable_stage_resolver_version
        ),
        "execution_planner_version": (
            result.execution_planner_version
        ),
        "deep_chain_node_count": result.deep_chain_node_count,
        "certification_version": result.certification_version,
        "schema_version": result.schema_version,
    }


@dataclass(frozen=True, slots=True)
class ConnectedDomainPipelineManifest:
    workflow_id: str
    stage_ids: tuple[str, ...]
    stage_job_types: tuple[str, ...]
    stage_references: Mapping[str, UniversalStageReference]
    dependency_graph: DependencyGraph
    planning_resolutions: tuple[RunnableStageResolution, ...]
    execution_plan: ExecutionPlan
    planning_certification: PlanningCertificationResult
    metadata: Mapping[str, Any]
    schema_version: str = CONNECTED_DOMAIN_MANIFEST_SCHEMA_VERSION
    manifest_version: str = CONNECTED_DOMAIN_MANIFEST_VERSION
    pipeline_id: str = CONNECTED_DOMAIN_PIPELINE_ID
    workflow_type: str = CONNECTED_DOMAIN_WORKFLOW_TYPE
    workflow_version: str = CONNECTED_DOMAIN_WORKFLOW_VERSION

    def __post_init__(self) -> None:
        if (
            not isinstance(self.workflow_id, str)
            or not self.workflow_id
            or self.workflow_id != self.workflow_id.strip()
        ):
            raise ConnectedDomainPipelineManifestError(
                "workflow_id must be canonical and non-empty."
            )

        if self.stage_ids != CONNECTED_DOMAIN_STAGE_IDS:
            raise ConnectedDomainPipelineManifestError(
                "Connected Domain stage order is not canonical."
            )

        if self.stage_job_types != CONNECTED_DOMAIN_STAGE_JOB_TYPES:
            raise ConnectedDomainPipelineManifestError(
                "Connected Domain job types are not canonical."
            )

        if tuple(self.stage_references) != self.stage_ids:
            raise ConnectedDomainPipelineManifestError(
                "Stage-reference identities are incomplete or unordered."
            )

        if self.execution_plan.planned_stage_ids != self.stage_ids:
            raise ConnectedDomainPipelineManifestError(
                "Execution plan does not cover all six stages."
            )

        if not self.planning_certification.is_certified:
            raise ConnectedDomainPipelineManifestError(
                "Universal dependency planning is not certified."
            )

        object.__setattr__(
            self,
            "stage_references",
            _freeze(self.stage_references),
        )
        object.__setattr__(
            self,
            "metadata",
            _freeze(self.metadata),
        )

    def _identity_payload(self) -> Mapping[str, Any]:
        return {
            "manifest_version": self.manifest_version,
            "pipeline_id": self.pipeline_id,
            "workflow_id": self.workflow_id,
            "workflow_type": self.workflow_type,
            "workflow_version": self.workflow_version,
            "stage_ids": self.stage_ids,
            "stage_job_types": self.stage_job_types,
        }

    def _content_payload(self) -> Mapping[str, Any]:
        return {
            "schema_version": self.schema_version,
            "manifest_version": self.manifest_version,
            "pipeline_id": self.pipeline_id,
            "workflow_id": self.workflow_id,
            "workflow_type": self.workflow_type,
            "workflow_version": self.workflow_version,
            "stage_ids": self.stage_ids,
            "stage_job_types": self.stage_job_types,
            "stage_references": {
                stage_id: reference.to_dict()
                for stage_id, reference
                in self.stage_references.items()
            },
            "dependency_graph": {
                "workflow_id": self.dependency_graph.workflow_id,
                "node_ids": self.dependency_graph.node_ids,
                "edges": tuple(
                    edge.to_dict()
                    for edge in self.dependency_graph.edges
                ),
                "graph_version": self.dependency_graph.graph_version,
            },
            "planning_resolutions": tuple(
                resolution.to_dict()
                for resolution in self.planning_resolutions
            ),
            "execution_plan": self.execution_plan.to_dict(),
            "planning_certification": (
                _planning_certification_dict(
                    self.planning_certification
                )
            ),
            "metadata": self.metadata,
        }

    def identity_fingerprint(self) -> str:
        return _sha256(self._identity_payload())

    def content_fingerprint(self) -> str:
        return _sha256(self._content_payload())

    def to_dict(self) -> Mapping[str, Any]:
        payload = dict(
            _plain(self._content_payload())
        )
        payload["identity_fingerprint"] = (
            self.identity_fingerprint()
        )
        payload["content_fingerprint"] = (
            self.content_fingerprint()
        )
        return _freeze(payload)


def build_connected_domain_pipeline_manifest(
    *,
    workflow_id: str,
    registration_loader: Callable[[], Any] = (
        ensure_persisted_runtime_registrations_loaded
    ),
    registration_reader: Callable[[str], Any] = (
        get_runtime_registration
    ),
) -> ConnectedDomainPipelineManifest:
    if (
        not isinstance(workflow_id, str)
        or not workflow_id
        or workflow_id != workflow_id.strip()
    ):
        raise ConnectedDomainPipelineManifestError(
            "workflow_id must be canonical and non-empty."
        )

    registration_loader()

    stage_references: dict[
        str,
        UniversalStageReference,
    ] = {}

    for stage_index, (stage_id, job_type) in enumerate(
        zip(
            CONNECTED_DOMAIN_STAGE_IDS,
            CONNECTED_DOMAIN_STAGE_JOB_TYPES,
        )
    ):
        record = _registration_record(
            registration_reader(job_type),
            job_type=job_type,
        )

        _validate_registration(
            record,
            stage_id=stage_id,
            job_type=job_type,
            stage_index=stage_index,
        )

        reference = _stage_reference(
            record,
            stage_id=stage_id,
            job_type=job_type,
            stage_index=stage_index,
        )

        validation = reference.validate()

        if not validation.is_valid:
            raise ConnectedDomainPipelineManifestError(
                "Stage reference validation failed for "
                + stage_id
                + ": "
                + ", ".join(validation.violations)
            )

        stage_references[stage_id] = reference

    graph = create_dependency_graph(
        workflow_id=workflow_id,
        node_ids=CONNECTED_DOMAIN_STAGE_IDS,
        edges=tuple(
            DependencyEdge(
                prerequisite_stage_id=prerequisite,
                dependent_stage_id=dependent,
            )
            for prerequisite, dependent
            in CONNECTED_DOMAIN_DEPENDENCIES
        ),
    )

    validation = require_valid_dependency_graph(graph)
    cycle_detection = require_acyclic_dependency_graph(graph)

    completed: list[str] = []
    resolutions: list[RunnableStageResolution] = []
    waves: list[ExecutionWave] = []
    fragments: list[ExecutionPlan] = []

    for wave_index, stage_id in enumerate(
        CONNECTED_DOMAIN_STAGE_IDS
    ):
        pending = CONNECTED_DOMAIN_STAGE_IDS[
            wave_index:
        ]

        state = create_runnable_stage_state(
            workflow_id=workflow_id,
            completed_stage_ids=tuple(completed),
            pending_stage_ids=pending,
        )

        resolution = resolve_runnable_stages(
            graph,
            state,
        )

        if resolution.runnable_stage_ids != (stage_id,):
            raise ConnectedDomainPipelineManifestError(
                "Unexpected runnable stage wave: "
                + repr(resolution.runnable_stage_ids)
            )

        fragment = create_execution_plan(
            graph,
            resolution,
        )

        if (
            fragment.wave_count != 1
            or len(fragment.waves) != 1
            or fragment.planned_stage_ids != (stage_id,)
        ):
            raise ConnectedDomainPipelineManifestError(
                "Canonical planner returned an invalid stage wave."
            )

        source_wave = fragment.waves[0]

        waves.append(
            ExecutionWave(
                wave_index=wave_index + 1,
                stage_ids=source_wave.stage_ids,
                execution_semantics=(
                    source_wave.execution_semantics
                ),
            )
        )
        resolutions.append(resolution)
        fragments.append(fragment)
        completed.append(stage_id)

    first_fragment = fragments[0]

    execution_plan = ExecutionPlan(
        workflow_id=workflow_id,
        wave_count=len(waves),
        waves=tuple(waves),
        planned_stage_ids=CONNECTED_DOMAIN_STAGE_IDS,
        graph_version=first_fragment.graph_version,
        cycle_detection_version=(
            first_fragment.cycle_detection_version
        ),
        runnable_stage_resolver_version=(
            first_fragment.runnable_stage_resolver_version
        ),
        planner_version=first_fragment.planner_version,
    )

    planning_certification = certify_dependency_planning()

    if not planning_certification.is_certified:
        raise ConnectedDomainPipelineManifestError(
            "Canonical dependency planning certification failed."
        )

    return ConnectedDomainPipelineManifest(
        workflow_id=workflow_id,
        stage_ids=CONNECTED_DOMAIN_STAGE_IDS,
        stage_job_types=CONNECTED_DOMAIN_STAGE_JOB_TYPES,
        stage_references=stage_references,
        dependency_graph=graph,
        planning_resolutions=tuple(resolutions),
        execution_plan=execution_plan,
        planning_certification=planning_certification,
        metadata={
            "authority": (
                "build_connected_domain_pipeline_manifest"
            ),
            "dependency_validation_version": (
                validation.validation_version
            ),
            "cycle_detection_version": (
                cycle_detection.detection_version
            ),
            "planning_composite_fingerprint": (
                planning_certification.composite_fingerprint
            ),
            "runtime_registration_count": len(stage_references),
            "manifest_finalized": True,
            "runtime_submission_executed": False,
        },
    )


def connected_domain_manifest_snapshot(
    manifest: ConnectedDomainPipelineManifest,
) -> Mapping[str, Any]:
    if not isinstance(
        manifest,
        ConnectedDomainPipelineManifest,
    ):
        raise ConnectedDomainPipelineManifestError(
            "manifest must be a ConnectedDomainPipelineManifest."
        )

    return manifest.to_dict()
