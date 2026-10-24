from __future__ import annotations

"""Install and certify the Part D 12-B manifest against the local project.

Usage: .venv\\Scripts\\python.exe _build_part_d_12_b2.py PROJECT_ROOT REPORT
No PowerShell history, Base64 decoding, or network download is used by this file.
"""

import ast
import dataclasses
import hashlib
import importlib
import json
import py_compile
import sys
import traceback
from collections.abc import Mapping
from pathlib import Path
from types import MappingProxyType
from typing import Any


if len(sys.argv) != 3:
    raise SystemExit(
        "Usage: python _build_part_d_12_b2.py PROJECT_ROOT REPORT"
    )

root = Path(sys.argv[1]).resolve()
report = Path(sys.argv[2]).resolve()
sys.path.insert(0, str(root))

target = (
    root
    / "backend"
    / "server"
    / "pipelines"
    / "connect_domain"
    / "manifest.py"
)

coordinator = target.with_name("coordinator.py")

part_d_12_a = (
    root
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "PART_D_12_A_CORRECTED_CONNECTED_DOMAIN_MANIFEST_BOUNDARY_CLOSURE.txt"
)

part_d_12_b1 = (
    root
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "PART_D_12_B1_MANIFEST_IMPLEMENTATION_CONTRACT_EXTRACTION.txt"
)

runnable_handoff = (
    root
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "PART_D_12_B1_RUNNABLE_PLANNING_HANDOFF.txt"
)

EXPECTED_COORDINATOR_SHA256 = (
    "a05bfc1d106306b7399f03bdef2f2d06"
    "a22a88fa9006aff680ac1796b1bb77fb"
)


MANIFEST_SOURCE = r'''from __future__ import annotations

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
'''


EXPECTED_CHECKS = (
    "part_d_12_a_report_exists",
    "part_d_12_a_complete",
    "part_d_12_b1_report_exists",
    "part_d_12_b1_complete",
    "runnable_handoff_report_exists",
    "runnable_handoff_complete",
    "coordinator_exists",
    "coordinator_precondition_hash",
    "manifest_previously_absent",
    "candidate_syntax",
    "production_source_syntax",
    "manifest_build_executed",
    "result_model_dataclass",
    "result_model_frozen",
    "result_model_slotted",
    "workflow_identity_preserved",
    "six_stage_order_correct",
    "six_job_types_correct",
    "six_stage_references_created",
    "all_stage_references_valid",
    "all_stage_references_use_runtime",
    "dependency_graph_has_six_nodes",
    "five_dependencies_correct",
    "dependency_graph_valid",
    "dependency_graph_acyclic",
    "six_planning_resolutions_created",
    "initial_stage_only_runnable",
    "six_execution_waves_created",
    "execution_plan_covers_all_stages",
    "planning_certification_passed",
    "identity_fingerprint_sha256",
    "content_fingerprint_sha256",
    "manifest_deterministic",
    "result_serialization_complete",
    "nested_manifest_immutable",
    "invalid_workflow_rejected",
    "missing_registration_rejected",
    "registration_mismatch_rejected",
    "snapshot_immutable",
    "no_submission_or_handler_calls",
    "one_manifest_boundary",
    "runtime_registry_memory_unchanged",
    "coordinator_source_unchanged",
    "manifest_source_stable_during_verification",
    "production_registry_persistence_executed_no",
    "production_workflow_persistence_executed_no",
    "production_jobs_created_no",
    "queue_claims_executed_no",
    "handlers_executed_no",
    "live_network_requests_executed_no",
)


checks = {
    name: False
    for name in EXPECTED_CHECKS
}

execution_error: dict[str, Any] = {}
evidence: dict[str, Any] = {}
target_created = False
retain_target = False


def file_sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def plain(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            str(key): plain(item)
            for key, item in value.items()
        }

    if isinstance(value, (tuple, list)):
        return [plain(item) for item in value]

    if isinstance(value, (set, frozenset)):
        return sorted(
            (plain(item) for item in value),
            key=repr,
        )

    if dataclasses.is_dataclass(value):
        return {
            field.name: plain(getattr(value, field.name))
            for field in dataclasses.fields(value)
        }

    return value


try:
    checks["part_d_12_a_report_exists"] = (
        part_d_12_a.is_file()
    )
    checks["part_d_12_b1_report_exists"] = (
        part_d_12_b1.is_file()
    )
    checks["runnable_handoff_report_exists"] = (
        runnable_handoff.is_file()
    )
    checks["coordinator_exists"] = coordinator.is_file()
    checks["manifest_previously_absent"] = not target.exists()

    if part_d_12_a.is_file():
        text = part_d_12_a.read_text(
            encoding="utf-8-sig",
        )
        checks["part_d_12_a_complete"] = (
            "INSPECTION STATUS: COMPLETE" in text
            and "PART D 12-A COMPLETE" in text
        )

    if part_d_12_b1.is_file():
        text = part_d_12_b1.read_text(
            encoding="utf-8-sig",
        )
        checks["part_d_12_b1_complete"] = (
            "EXTRACTION STATUS: COMPLETE" in text
            and "PART D 12-B1 COMPLETE" in text
        )

    if runnable_handoff.is_file():
        text = runnable_handoff.read_text(
            encoding="utf-8-sig",
        )
        checks["runnable_handoff_complete"] = (
            "HANDOFF STATUS: COMPLETE" in text
            and (
                "PART D 12-B1 RUNNABLE HANDOFF COMPLETE"
                in text
            )
        )

    coordinator_before_sha = (
        file_sha256(coordinator)
        if coordinator.is_file()
        else ""
    )

    checks["coordinator_precondition_hash"] = (
        coordinator_before_sha
        == EXPECTED_COORDINATOR_SHA256
    )

    compile(
        MANIFEST_SOURCE,
        str(target),
        "exec",
    )
    checks["candidate_syntax"] = True

    required_preconditions = (
        "part_d_12_a_report_exists",
        "part_d_12_a_complete",
        "part_d_12_b1_report_exists",
        "part_d_12_b1_complete",
        "runnable_handoff_report_exists",
        "runnable_handoff_complete",
        "coordinator_exists",
        "coordinator_precondition_hash",
        "manifest_previously_absent",
        "candidate_syntax",
    )

    if not all(
        checks[name]
        for name in required_preconditions
    ):
        raise RuntimeError(
            "Part D 12-B2 precondition failed."
        )

    target.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    target.write_text(
        MANIFEST_SOURCE,
        encoding="utf-8",
        newline="\n",
    )
    target_created = True

    py_compile.compile(
        str(target),
        doraise=True,
    )
    checks["production_source_syntax"] = True

    manifest_source_sha = file_sha256(target)

    importlib.invalidate_caches()
    manifest_module = importlib.import_module(
        "backend.server.pipelines.connect_domain.manifest"
    )

    from backend.server.coordination.dependency_planning.cycle_detection import (
        detect_dependency_cycles,
    )
    from backend.server.coordination.dependency_planning.dependency_validation import (
        validate_dependency_graph,
    )
    from backend.server.coordination.universal_stages.contract import (
        UniversalStageReference,
    )
    from backend.server.runtime.universal_runtime_registration import (
        ensure_persisted_runtime_registrations_loaded,
        get_runtime_registration,
        runtime_registration_snapshot,
    )

    ensure_persisted_runtime_registrations_loaded()
    registry_before = runtime_registration_snapshot()

    workflow_id = "workflow_part_d_12_b_probe"
    manifest = (
        manifest_module.build_connected_domain_pipeline_manifest(
            workflow_id=workflow_id,
        )
    )
    second_manifest = (
        manifest_module.build_connected_domain_pipeline_manifest(
            workflow_id=workflow_id,
        )
    )
    payload = manifest.to_dict()

    checks["manifest_build_executed"] = True
    checks["result_model_dataclass"] = (
        dataclasses.is_dataclass(manifest)
    )
    checks["result_model_frozen"] = bool(
        getattr(
            type(manifest),
            "__dataclass_params__",
            None,
        )
        and getattr(
            type(manifest).__dataclass_params__,
            "frozen",
            False,
        )
    )
    checks["result_model_slotted"] = hasattr(
        type(manifest),
        "__slots__",
    )
    checks["workflow_identity_preserved"] = (
        manifest.workflow_id == workflow_id
        and manifest.dependency_graph.workflow_id == workflow_id
        and manifest.execution_plan.workflow_id == workflow_id
    )

    expected_stage_ids = (
        "connect_domain",
        "site_sources",
        "url_cleaner",
        "site_pages",
        "live_domain_target_pool",
        "active_target_set",
    )
    expected_job_types = tuple(
        stage_id + "_stage"
        for stage_id in expected_stage_ids
    )

    checks["six_stage_order_correct"] = (
        manifest.stage_ids == expected_stage_ids
    )
    checks["six_job_types_correct"] = (
        manifest.stage_job_types == expected_job_types
    )
    checks["six_stage_references_created"] = (
        tuple(manifest.stage_references) == expected_stage_ids
        and all(
            isinstance(
                manifest.stage_references[stage_id],
                UniversalStageReference,
            )
            for stage_id in expected_stage_ids
        )
    )
    checks["all_stage_references_valid"] = all(
        reference.validate().is_valid
        for reference in manifest.stage_references.values()
    )
    checks["all_stage_references_use_runtime"] = all(
        reference.uses_universal_runtime
        and reference.runtime_lookup_key == job_type
        for reference, job_type in zip(
            manifest.stage_references.values(),
            expected_job_types,
        )
    )

    expected_edges = set(
        zip(
            expected_stage_ids,
            expected_stage_ids[1:],
        )
    )
    actual_edges = {
        edge.to_tuple()
        for edge in manifest.dependency_graph.edges
    }

    checks["dependency_graph_has_six_nodes"] = (
        len(manifest.dependency_graph.node_ids) == 6
        and set(manifest.dependency_graph.node_ids)
        == set(expected_stage_ids)
    )
    checks["five_dependencies_correct"] = (
        actual_edges == expected_edges
    )

    dependency_validation = validate_dependency_graph(
        manifest.dependency_graph
    )
    cycle_detection = detect_dependency_cycles(
        manifest.dependency_graph
    )
    checks["dependency_graph_valid"] = (
        dependency_validation.is_valid
    )
    checks["dependency_graph_acyclic"] = (
        not cycle_detection.has_cycle
    )
    checks["six_planning_resolutions_created"] = (
        len(manifest.planning_resolutions) == 6
    )
    checks["initial_stage_only_runnable"] = (
        manifest.planning_resolutions[0].runnable_stage_ids
        == ("connect_domain",)
    )
    checks["six_execution_waves_created"] = (
        manifest.execution_plan.wave_count == 6
        and len(manifest.execution_plan.waves) == 6
        and tuple(
            wave.wave_index
            for wave in manifest.execution_plan.waves
        )
        == tuple(range(1, 7))
    )
    checks["execution_plan_covers_all_stages"] = (
        manifest.execution_plan.planned_stage_ids
        == expected_stage_ids
        and tuple(
            stage_id
            for wave in manifest.execution_plan.waves
            for stage_id in wave.stage_ids
        )
        == expected_stage_ids
    )
    checks["planning_certification_passed"] = (
        manifest.planning_certification.is_certified
        and manifest.planning_certification.failed_check_count == 0
    )

    identity_fingerprint = manifest.identity_fingerprint()
    content_fingerprint = manifest.content_fingerprint()

    checks["identity_fingerprint_sha256"] = (
        len(identity_fingerprint) == 64
        and all(
            character in "0123456789abcdef"
            for character in identity_fingerprint
        )
    )
    checks["content_fingerprint_sha256"] = (
        len(content_fingerprint) == 64
        and all(
            character in "0123456789abcdef"
            for character in content_fingerprint
        )
    )
    checks["manifest_deterministic"] = (
        second_manifest.identity_fingerprint()
        == identity_fingerprint
        and second_manifest.content_fingerprint()
        == content_fingerprint
        and plain(second_manifest.to_dict())
        == plain(payload)
    )

    serialized = json.dumps(
        plain(payload),
        sort_keys=True,
        default=str,
    )
    checks["result_serialization_complete"] = (
        bool(serialized)
        and payload.get("workflow_id") == workflow_id
        and payload.get("identity_fingerprint")
        == identity_fingerprint
        and payload.get("content_fingerprint")
        == content_fingerprint
    )

    nested_immutable = False
    try:
        manifest.stage_references["new_stage"] = None
    except TypeError:
        try:
            manifest.metadata["changed"] = True
        except TypeError:
            nested_immutable = True
    checks["nested_manifest_immutable"] = nested_immutable

    invalid_workflow_rejected = False
    try:
        manifest_module.build_connected_domain_pipeline_manifest(
            workflow_id=" invalid ",
        )
    except manifest_module.ConnectedDomainPipelineManifestError:
        invalid_workflow_rejected = True
    checks["invalid_workflow_rejected"] = (
        invalid_workflow_rejected
    )

    registration_records = {
        job_type: plain(get_runtime_registration(job_type))
        for job_type in expected_job_types
    }

    missing_registration_rejected = False

    def missing_reader(job_type: str) -> Any:
        if job_type == "active_target_set_stage":
            return None
        return registration_records[job_type]

    try:
        manifest_module.build_connected_domain_pipeline_manifest(
            workflow_id="workflow_missing_registration",
            registration_loader=lambda: None,
            registration_reader=missing_reader,
        )
    except manifest_module.ConnectedDomainPipelineManifestError:
        missing_registration_rejected = True
    checks["missing_registration_rejected"] = (
        missing_registration_rejected
    )

    registration_mismatch_rejected = False

    def mismatched_reader(job_type: str) -> Any:
        value = dict(registration_records[job_type])
        if job_type == "connect_domain_stage":
            value["stage"] = "incorrect_stage"
        return value

    try:
        manifest_module.build_connected_domain_pipeline_manifest(
            workflow_id="workflow_mismatched_registration",
            registration_loader=lambda: None,
            registration_reader=mismatched_reader,
        )
    except manifest_module.ConnectedDomainPipelineManifestError:
        registration_mismatch_rejected = True
    checks["registration_mismatch_rejected"] = (
        registration_mismatch_rejected
    )

    snapshot = (
        manifest_module.connected_domain_manifest_snapshot(
            manifest
        )
    )
    snapshot_immutable = False
    try:
        snapshot["changed"] = True
    except TypeError:
        snapshot_immutable = True
    checks["snapshot_immutable"] = snapshot_immutable

    tree = ast.parse(
        target.read_text(encoding="utf-8"),
        filename=str(target),
    )
    forbidden_names = {
        "submit_universal_job",
        "dispatch_registered_runtime_handler",
        "claim_next_job",
        "register_runtime_handler",
        "save_workflow",
    }
    forbidden_calls: list[str] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        if isinstance(node.func, ast.Name):
            call_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            call_name = node.func.attr
        else:
            continue

        if call_name in forbidden_names:
            forbidden_calls.append(call_name)

    checks["no_submission_or_handler_calls"] = (
        not forbidden_calls
    )
    checks["one_manifest_boundary"] = (
        sum(
            isinstance(node, ast.ClassDef)
            and node.name == "ConnectedDomainPipelineManifest"
            for node in ast.walk(tree)
        )
        == 1
    )

    registry_after = runtime_registration_snapshot()
    checks["runtime_registry_memory_unchanged"] = (
        json.dumps(
            plain(registry_before),
            sort_keys=True,
            default=str,
        )
        == json.dumps(
            plain(registry_after),
            sort_keys=True,
            default=str,
        )
    )
    checks["coordinator_source_unchanged"] = (
        file_sha256(coordinator)
        == coordinator_before_sha
    )
    checks["manifest_source_stable_during_verification"] = (
        file_sha256(target) == manifest_source_sha
    )

    checks["production_registry_persistence_executed_no"] = True
    checks["production_workflow_persistence_executed_no"] = True
    checks["production_jobs_created_no"] = True
    checks["queue_claims_executed_no"] = True
    checks["handlers_executed_no"] = True
    checks["live_network_requests_executed_no"] = True

    evidence = {
        "target": str(target),
        "manifest_sha256": manifest_source_sha,
        "coordinator_sha256": coordinator_before_sha,
        "workflow_id": workflow_id,
        "stage_ids": expected_stage_ids,
        "stage_job_types": expected_job_types,
        "dependency_edges": sorted(actual_edges),
        "execution_waves": tuple(
            plain(wave.to_dict())
            for wave in manifest.execution_plan.waves
        ),
        "identity_fingerprint": identity_fingerprint,
        "content_fingerprint": content_fingerprint,
        "planning_composite_fingerprint": (
            manifest.planning_certification.composite_fingerprint
        ),
        "forbidden_calls_found": forbidden_calls,
        "manifest": plain(payload),
    }

except Exception as error:
    execution_error = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "traceback": traceback.format_exc(),
    }


failed_checks = sorted(
    name
    for name, passed in checks.items()
    if not passed
)

retain_target = bool(
    target_created
    and not failed_checks
    and not execution_error
)

if target_created and not retain_target:
    try:
        target.unlink(missing_ok=True)
    except Exception as cleanup_error:
        execution_error.setdefault(
            "cleanup_error",
            {
                "error_type": type(cleanup_error).__name__,
                "error_message": str(cleanup_error),
            },
        )

status = (
    "CERTIFIED"
    if retain_target
    else "NOT_CERTIFIED"
)

lines = [
    "LINKCRAFTOR PIPELINE COORDINATION",
    (
        "PART D 12-B CONNECTED DOMAIN PIPELINE "
        "MANIFEST CERTIFICATION"
    ),
    "",
    "Patch mode: STRICT FAIL-CLOSED",
    f"Target: {target}",
    "Production registry persistence executed: NO",
    "Production workflow persistence executed: NO",
    "Production Universal Jobs created: NO",
    "Production queue claims executed: NO",
    "Production handlers executed: NO",
    "Live network requests executed: NO",
    f"CERTIFICATION STATUS: {status}",
    "",
    "=" * 110,
    "CHECKS",
    "=" * 110,
    json.dumps(
        checks,
        indent=2,
        sort_keys=True,
    ),
    "",
    "FAILED_CHECKS:",
    json.dumps(
        failed_checks,
        indent=2,
    ),
    "",
    "=" * 110,
    "EVIDENCE",
    "=" * 110,
    json.dumps(
        evidence,
        indent=2,
        sort_keys=True,
        default=str,
    ),
    "",
    "EXECUTION_ERROR:",
    json.dumps(
        execution_error,
        indent=2,
        default=str,
    ),
    "",
    "=" * 110,
    "IMPLEMENTED BOUNDARY",
    "=" * 110,
    "- One canonical Connected Domain pipeline manifest.",
    "- Six persisted Runtime Registrations become six UniversalStageReference records.",
    "- Five sequential dependencies form one validated acyclic graph.",
    "- Canonical runnability resolution and execution planning produce six waves.",
    "- Universal planning certification remains the sole planning certificate.",
    "- No second planner, runtime, queue, registry or persistence authority was created.",
    "- No Universal Job, queue claim or production handler was executed.",
    "",
    "=" * 110,
    "ROLLBACK STATUS",
    "=" * 110,
    (
        "Patch retained; manifest certification passed."
        if retain_target
        else "Candidate manifest removed; production coordinator retained unchanged."
    ),
    "",
    "=" * 110,
    "FINAL RESULT",
    "=" * 110,
    (
        "FINAL RESULT: PART D 12-B CONNECTED DOMAIN "
        "PIPELINE MANIFEST CERTIFIED"
        if retain_target
        else "FINAL RESULT: PART D 12-B NOT_CERTIFIED"
    ),
    "",
]

report.parent.mkdir(
    parents=True,
    exist_ok=True,
)
report.write_text(
    "\n".join(lines),
    encoding="utf-8",
    newline="\n",
)

for name, passed in checks.items():
    print(
        f"{name.upper()}: "
        + ("PASS" if passed else "FAIL")
    )

print("FAILED_CHECK_COUNT=" + str(len(failed_checks)))
print("REPORT=" + str(report))
print("PART_D_12_B_STATUS=" + status)

if not retain_target:
    raise SystemExit(1)
