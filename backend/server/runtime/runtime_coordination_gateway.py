from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

from backend.server.coordination.coordinator_registry.registry import (
    coordinator_registry_snapshot,
)
from backend.server.coordination.runtime_integration.coordination_runtime_bridge import (
    bridge_execution_plan_to_runtime as _bridge_execution_plan_to_runtime,
)
from backend.server.coordination.runtime_integration.runtime_job_mapping import (
    map_runtime_handoffs_to_job_requests as _map_runtime_handoffs_to_job_requests,
)
from backend.server.coordination.runtime_integration.runtime_execution_gateway import (
    intake_runtime_terminal_stage_result as _intake_runtime_terminal_stage_result,
    submit_runtime_execution_wave as _submit_runtime_execution_wave,
    submit_runtime_job_mapping as _submit_runtime_job_mapping,
)
from backend.server.coordination.workflow_persistence.repository import WorkflowRepository
from backend.server.coordination.universal_workflows.contract import UniversalWorkflowStatus
from backend.server.coordination.workflow_lifecycle.transition_validation import require_valid_workflow_transition
from backend.server.coordination.workflow_lifecycle.terminal_state_protection import require_terminal_state_mutation_allowed
from backend.server.coordination.workflow_lifecycle.lifecycle_history import (
    LifecycleHistoryEntry,
    append_lifecycle_history,
    create_lifecycle_history_entry,
)
from backend.server.coordination.workflow_registry.registry import workflow_registry_snapshot
from backend.server.runtime.universal_runtime_kernel import UniversalRuntimeKernel


RUNTIME_COORDINATION_GATEWAY_KEY = "runtime_coordination"
RUNTIME_COORDINATION_GATEWAY_VERSION = "runtime_coordination_gateway_v1.2.0"


class RuntimeCoordinationGatewayError(RuntimeError):
    pass


class RuntimeCoordinationGatewayBindingError(RuntimeCoordinationGatewayError):
    pass


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({str(key): _freeze(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, (set, frozenset)):
        return tuple(sorted((_freeze(item) for item in value), key=repr))
    return value


@dataclass(frozen=True, slots=True)
class RuntimeWorkflowSubmissionResult:
    workflow_id: str
    correlation_id: str
    stage_ids: tuple[str, ...]
    job_ids: tuple[str, ...]
    bridge_result: Any
    mapping_result: Any
    submission_result: Any
    evidence: Mapping[str, Any]
    connection_version: str = "runtime_workflow_submission_connection_v1"

    def __post_init__(self) -> None:
        object.__setattr__(self, "stage_ids", tuple(self.stage_ids))
        object.__setattr__(self, "job_ids", tuple(self.job_ids))
        object.__setattr__(self, "evidence", _freeze(self.evidence))
        if not self.workflow_id or not self.correlation_id:
            raise RuntimeCoordinationGatewayError(
                "Workflow submission identity is incomplete."
            )
        if self.bridge_result.workflow_id != self.workflow_id:
            raise RuntimeCoordinationGatewayError(
                "Bridge workflow identity does not match submission identity."
            )
        if self.mapping_result.workflow_id != self.workflow_id:
            raise RuntimeCoordinationGatewayError(
                "Mapping workflow identity does not match submission identity."
            )
        if self.submission_result.workflow_id != self.workflow_id:
            raise RuntimeCoordinationGatewayError(
                "Runtime submission workflow identity does not match."
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "connection_version": self.connection_version,
            "workflow_id": self.workflow_id,
            "correlation_id": self.correlation_id,
            "stage_ids": list(self.stage_ids),
            "job_ids": list(self.job_ids),
            "bridge": dict(self.bridge_result.to_dict()),
            "mapping": {
                "workflow_id": self.mapping_result.workflow_id,
                "mapping_count": self.mapping_result.mapping_count,
                "stage_ids": list(self.mapping_result.stage_ids),
            },
            "submission": self.submission_result.to_dict(),
            "evidence": dict(self.evidence),
        }


@dataclass(frozen=True, slots=True)
class RuntimeWorkflowLifecycleResult:
    job_id: str
    workflow_id: str
    correlation_id: str
    stage_id: str
    disposition: str
    previous_status: str
    current_status: str
    workflow: Any
    terminal_intake: Any
    persistence_evidence: Any
    lifecycle_history_entry: Any
    evidence: Mapping[str, Any]
    connection_version: str = "runtime_workflow_lifecycle_connection_v1"

    def __post_init__(self) -> None:
        for field_name in (
            "job_id",
            "workflow_id",
            "correlation_id",
            "stage_id",
            "disposition",
            "previous_status",
            "current_status",
        ):
            if not str(getattr(self, field_name, "") or "").strip():
                raise RuntimeCoordinationGatewayError(
                    f"{field_name} is required."
                )
        object.__setattr__(self, "evidence", _freeze(self.evidence))

    def to_dict(self) -> dict[str, Any]:
        intake = (
            self.terminal_intake.to_dict()
            if hasattr(self.terminal_intake, "to_dict")
            else self.terminal_intake
        )
        persisted = (
            self.persistence_evidence.to_dict()
            if hasattr(self.persistence_evidence, "to_dict")
            else self.persistence_evidence
        )
        history = (
            dict(self.lifecycle_history_entry.to_dict())
            if self.lifecycle_history_entry is not None
            else None
        )
        return {
            "connection_version": self.connection_version,
            "job_id": self.job_id,
            "workflow_id": self.workflow_id,
            "correlation_id": self.correlation_id,
            "stage_id": self.stage_id,
            "disposition": self.disposition,
            "previous_status": self.previous_status,
            "current_status": self.current_status,
            "workflow": self.workflow.to_canonical_dict(),
            "terminal_intake": intake,
            "persistence_evidence": persisted,
            "lifecycle_history_entry": history,
            "evidence": dict(self.evidence),
        }


@dataclass(frozen=True, slots=True)
class RuntimeCoordinationGateway:
    project_root: Path
    workflow_root: Path
    workflow_repository: WorkflowRepository
    gateway_version: str = RUNTIME_COORDINATION_GATEWAY_VERSION

    def bridge_execution_plan_to_runtime(self, **kwargs: Any) -> Any:
        return _bridge_execution_plan_to_runtime(**kwargs)

    def submit_runtime_job_mapping(self, **kwargs: Any) -> Any:
        return _submit_runtime_job_mapping(**kwargs)

    def submit_runtime_execution_wave(self, **kwargs: Any) -> Any:
        return _submit_runtime_execution_wave(**kwargs)

    def submit_workflow_execution(
        self,
        *,
        execution_plan: Any,
        stage_references: Mapping[str, Any],
        context: Any,
        dependency_job_ids_by_stage: Mapping[str, Any] | None = None,
        execution_semantics: str = "parallel_eligible",
        submitter: Any = None,
        correlation_registry: Any = None,
        jobs_reader: Any = None,
    ) -> RuntimeWorkflowSubmissionResult:
        bridge_result = _bridge_execution_plan_to_runtime(
            execution_plan=execution_plan,
            stage_references=stage_references,
            context=context,
        )
        mapping_result = _map_runtime_handoffs_to_job_requests(
            bridge_result=bridge_result,
        )
        submission_arguments: dict[str, Any] = {
            "mapping_result": mapping_result,
            "dependency_job_ids_by_stage": dependency_job_ids_by_stage,
            "execution_semantics": execution_semantics,
        }
        if submitter is not None:
            submission_arguments["submitter"] = submitter
        if correlation_registry is not None:
            submission_arguments["correlation_registry"] = correlation_registry
        if jobs_reader is not None:
            submission_arguments["jobs_reader"] = jobs_reader
        submission_result = _submit_runtime_execution_wave(
            **submission_arguments,
        )
        correlation_id = str(getattr(context, "correlation_id", "") or "").strip()
        evidence = {
            "connection": "runtime_workflow_submission_connection_v1",
            "canonical_bridge": "bridge_execution_plan_to_runtime",
            "canonical_mapper": "map_runtime_handoffs_to_job_requests",
            "canonical_submitter": "submit_runtime_execution_wave",
            "canonical_correlation": "WorkflowJobCorrelationRegistry",
            "workflow_repository": type(self.workflow_repository).__name__,
            "direct_handler_dispatch": False,
            "second_queue_created": False,
            "second_registry_created": False,
            "second_submitter_created": False,
        }
        return RuntimeWorkflowSubmissionResult(
            workflow_id=bridge_result.workflow_id,
            correlation_id=correlation_id,
            stage_ids=tuple(mapping_result.stage_ids),
            job_ids=tuple(submission_result.job_ids),
            bridge_result=bridge_result,
            mapping_result=mapping_result,
            submission_result=submission_result,
            evidence=evidence,
        )

    def intake_runtime_terminal_stage_result(self, *, job_id: str, **kwargs: Any) -> Any:
        if "workflow_repository" in kwargs:
            raise RuntimeCoordinationGatewayError(
                "workflow_repository is owned by RuntimeCoordinationGateway."
            )
        return _intake_runtime_terminal_stage_result(
            job_id=job_id,
            workflow_repository=self.workflow_repository,
            **kwargs,
        )


    def apply_runtime_terminal_lifecycle(
        self,
        *,
        job_id: str,
        terminal_intake: Any = None,
        occurred_at: str | None = None,
        **kwargs: Any,
    ) -> RuntimeWorkflowLifecycleResult:
        if "workflow_repository" in kwargs:
            raise RuntimeCoordinationGatewayError(
                "workflow_repository is owned by RuntimeCoordinationGateway."
            )
        intake_authority = (
            _intake_runtime_terminal_stage_result
            if terminal_intake is None
            else terminal_intake
        )
        intake_result = intake_authority(
            job_id=job_id,
            workflow_repository=self.workflow_repository,
            **kwargs,
        )
        workflow_id = str(getattr(intake_result, "workflow_id", "") or "").strip()
        stage_id = str(getattr(intake_result, "stage_id", "") or "").strip()
        correlation_id = str(getattr(intake_result, "correlation_id", "") or "").strip()
        disposition = str(getattr(intake_result, "disposition", "") or "").strip().lower()
        if disposition not in {"completed", "failed"}:
            raise RuntimeCoordinationGatewayError(
                "Terminal intake disposition must be completed or failed."
            )
        record = self.workflow_repository.load_workflow_record(workflow_id)
        workflow = record.workflow
        if workflow.correlation_id != correlation_id:
            raise RuntimeCoordinationGatewayError(
                "Workflow correlation identity conflicts with terminal intake."
            )
        pending = tuple(item for item in workflow.pending_stages if item != stage_id)
        completed = tuple(workflow.completed_stages)
        failed = tuple(workflow.failed_stages)
        processed = dict(getattr(intake_result, "processed_result", {}) or {})
        timestamp = str(occurred_at or datetime.now(timezone.utc).isoformat()).strip()
        previous_status = workflow.status
        history_entry = None
        metadata = dict(workflow.metadata)

        if previous_status in {
            UniversalWorkflowStatus.COMPLETED,
            UniversalWorkflowStatus.FAILED,
            UniversalWorkflowStatus.CANCELLED,
            UniversalWorkflowStatus.ABORTED,
        }:
            require_terminal_state_mutation_allowed(
                previous_status,
                previous_status,
            )

        if disposition == "completed":
            if stage_id in failed:
                raise RuntimeCoordinationGatewayError(
                    "Completed stage is already recorded as failed."
                )
            if stage_id not in completed:
                completed = completed + (stage_id,)
            requested_status = (
                UniversalWorkflowStatus.COMPLETED
                if not pending
                else previous_status
            )
            changes = {
                "status": requested_status,
                "current_stage": None if not pending else pending[0],
                "completed_stages": completed,
                "pending_stages": pending,
                "updated_at": timestamp,
                "result_reference": processed.get("result_reference") or workflow.result_reference,
                "artifact_references": tuple(dict.fromkeys(
                    tuple(workflow.artifact_references)
                    + tuple(processed.get("artifact_references", ()) or ())
                )),
                "completed_at": timestamp if not pending else workflow.completed_at,
                "failure_code": None,
                "failure_message": None,
                "failure_details": {},
            }
        else:
            if stage_id in completed:
                raise RuntimeCoordinationGatewayError(
                    "Failed stage is already recorded as completed."
                )
            if stage_id not in failed:
                failed = failed + (stage_id,)
            requested_status = UniversalWorkflowStatus.FAILED
            changes = {
                "status": requested_status,
                "current_stage": None,
                "failed_stages": failed,
                "pending_stages": pending,
                "updated_at": timestamp,
                "failed_at": timestamp,
                "failure_code": str(processed.get("failure_code") or "runtime_stage_failed"),
                "failure_message": str(processed.get("failure_message") or "Runtime stage failed."),
                "failure_details": dict(processed.get("failure_details", {}) or {}),
            }

        if requested_status != previous_status:
            require_terminal_state_mutation_allowed(previous_status, requested_status)
            require_valid_workflow_transition(previous_status, requested_status)
            event_material = (
                f"{workflow_id}|{job_id}|{stage_id}|"
                f"{previous_status.value}|{requested_status.value}"
            )
            history_entry = create_lifecycle_history_entry(
                event_id="runtime_" + hashlib.sha256(event_material.encode("utf-8")).hexdigest(),
                workflow_id=workflow_id,
                correlation_id=correlation_id,
                from_state=previous_status,
                to_state=requested_status,
                occurred_at=timestamp,
                reason=f"Runtime stage {stage_id} {disposition}.",
                source="runtime_coordination_gateway",
                metadata={"job_id": job_id, "stage_id": stage_id, "disposition": disposition},
            )
            existing_history = tuple(metadata.get("lifecycle_history", ()) or ())
            history_objects = []
            for item in existing_history:
                if not isinstance(item, Mapping):
                    raise RuntimeCoordinationGatewayError(
                        "Stored lifecycle history entry must be a mapping."
                    )
                history_objects.append(
                    LifecycleHistoryEntry(
                        event_id=item["event_id"],
                        workflow_id=item["workflow_id"],
                        correlation_id=item["correlation_id"],
                        from_state=UniversalWorkflowStatus.coerce(item["from_state"]),
                        to_state=UniversalWorkflowStatus.coerce(item["to_state"]),
                        occurred_at=item["occurred_at"],
                        reason=item.get("reason"),
                        source=item.get("source"),
                        actor_id=item.get("actor_id"),
                        metadata=item.get("metadata", {}),
                        transition_validation_version=item["transition_validation_version"],
                        state_machine_version=item["state_machine_version"],
                        history_version=item["history_version"],
                    )
                )
            updated_history = append_lifecycle_history(tuple(history_objects), history_entry)
            metadata["lifecycle_history"] = tuple(dict(item.to_dict()) for item in updated_history)
            changes["metadata"] = metadata

        updated_workflow = replace(workflow, **changes)
        persistence = self.workflow_repository.save_workflow(
            updated_workflow,
            expected_current_fingerprint=(
                record.evidence.workflow_content_fingerprint
            ),
        )
        return RuntimeWorkflowLifecycleResult(
            job_id=str(job_id),
            workflow_id=workflow_id,
            correlation_id=correlation_id,
            stage_id=stage_id,
            disposition=disposition,
            previous_status=previous_status.value,
            current_status=updated_workflow.status.value,
            workflow=updated_workflow,
            terminal_intake=intake_result,
            persistence_evidence=persistence,
            lifecycle_history_entry=history_entry,
            evidence={
                "terminal_intake": "intake_runtime_terminal_stage_result",
                "transition_validation": "require_valid_workflow_transition",
                "terminal_protection": "require_terminal_state_mutation_allowed",
                "history_authority": "append_lifecycle_history",
                "persistence_authority": "WorkflowRepository.save_workflow",
                "optimistic_concurrency": True,
                "second_lifecycle_created": False,
                "second_repository_created": False,
                "handler_executed": False,
                "job_created": False,
                "queue_claimed": False,
            },
        )

    def snapshot(self) -> Mapping[str, Any]:
        return _freeze(
            {
                "schema_version": "runtime_coordination_gateway_snapshot_v1",
                "gateway_version": self.gateway_version,
                "component_key": RUNTIME_COORDINATION_GATEWAY_KEY,
                "project_root": str(self.project_root),
                "workflow_root": str(self.workflow_root),
                "workflow_registry": workflow_registry_snapshot(),
                "coordinator_registry": coordinator_registry_snapshot(),
                "authorities": (
                    "coordination_runtime_bridge",
                    "runtime_execution_gateway",
                    "workflow_repository",
                    "workflow_registry",
                    "coordinator_registry",
                ),
            }
        )

    def evidence(self) -> Mapping[str, Any]:
        snapshot = self.snapshot()
        return _freeze(
            {
                "schema_version": "runtime_coordination_gateway_evidence_v1",
                "gateway_version": self.gateway_version,
                "component_key": RUNTIME_COORDINATION_GATEWAY_KEY,
                "workflow_root": str(self.workflow_root),
                "workflow_registry_count": snapshot["workflow_registry"].get("count", 0),
                "coordinator_registry_count": snapshot["coordinator_registry"].get("count", 0),
                "boot_bound": True,
                "second_runtime_created": False,
                "second_registry_created": False,
                "second_queue_created": False,
            }
        )


def register_runtime_coordination_gateway(
    kernel: UniversalRuntimeKernel,
    project_root: Path | str | None = None,
    **_: Any,
) -> RuntimeCoordinationGateway:
    if kernel.has_component(RUNTIME_COORDINATION_GATEWAY_KEY):
        raise RuntimeCoordinationGatewayBindingError(
            "Runtime coordination gateway is already bound to the kernel."
        )
    resolved_root = Path(project_root or Path.cwd()).resolve()
    workflow_root = (
        resolved_root / "backend" / "server" / "data" / "coordination" / "workflows"
    )
    gateway = RuntimeCoordinationGateway(
        project_root=resolved_root,
        workflow_root=workflow_root,
        workflow_repository=WorkflowRepository(root=workflow_root),
    )
    kernel.bind_component(RUNTIME_COORDINATION_GATEWAY_KEY, gateway)
    return gateway
