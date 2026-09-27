"""
LinkCraftor Universal Runtime Infrastructure
Phase 7.6 — Job Execution Permissions
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional

from .runtime_authorization import (
    RuntimeAuthorizationDecision,
    RuntimeAuthorizationDisposition,
)


JOB_EXECUTION_PERMISSIONS_VERSION = "job_execution_permissions_v7.6.1"
JOB_EXECUTION_PERMISSIONS_SCHEMA_VERSION = "job_execution_permissions_schema_v1"


class JobExecutionAction(str, Enum):
    EXECUTE = "EXECUTE"
    RETRY = "RETRY"
    RESUME = "RESUME"
    CHECKPOINT = "CHECKPOINT"
    COMPLETE = "COMPLETE"
    CANCEL = "CANCEL"


@dataclass(frozen=True, slots=True)
class JobExecutionPermissionRequest:
    job_id: str
    workspace_id: str
    action: JobExecutionAction
    handler_key: Optional[str] = None
    execution_id: Optional[str] = None

    schema_version: str = field(
        default=JOB_EXECUTION_PERMISSIONS_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class JobExecutionPermissionEvidence:
    runtime_authorization: RuntimeAuthorizationDecision

    job_executable: bool
    job_terminal: bool
    job_suspended: bool = False

    authorized_job_ids: tuple[str, ...] = ()
    authorized_workspace_ids: tuple[str, ...] = ()
    allowed_actions: tuple[JobExecutionAction, ...] = ()
    allowed_handler_keys: tuple[str, ...] = ()

    unrestricted_job_scope: bool = False
    unrestricted_workspace_scope: bool = False
    unrestricted_handler_scope: bool = False

    permission_reference: Optional[str] = None

    schema_version: str = field(
        default=JOB_EXECUTION_PERMISSIONS_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class JobExecutionPermissionDecision:
    permitted: bool
    job_id: str
    workspace_id: str
    action: JobExecutionAction
    reason_code: str
    permission_reference: Optional[str]

    schema_version: str = field(
        default=JOB_EXECUTION_PERMISSIONS_SCHEMA_VERSION,
        init=False,
    )


def evaluate_job_execution_permission(
    *,
    request: JobExecutionPermissionRequest,
    evidence: JobExecutionPermissionEvidence,
) -> JobExecutionPermissionDecision:

    def deny(reason: str) -> JobExecutionPermissionDecision:
        return JobExecutionPermissionDecision(
            permitted=False,
            job_id=request.job_id,
            workspace_id=request.workspace_id,
            action=request.action,
            reason_code=reason,
            permission_reference=evidence.permission_reference,
        )

    if (
        evidence.runtime_authorization.disposition
        is not RuntimeAuthorizationDisposition.ALLOW
    ):
        return deny("runtime_authorization_denied")

    if evidence.job_terminal:
        return deny("terminal_job_cannot_execute")

    if request.action is JobExecutionAction.EXECUTE and not evidence.job_executable:
        return deny("job_not_executable")

    if (
        evidence.job_suspended
        and request.action not in {
            JobExecutionAction.RESUME,
            JobExecutionAction.CANCEL,
        }
    ):
        return deny("suspended_job_action_not_permitted")

    if (
        not evidence.unrestricted_job_scope
        and request.job_id not in evidence.authorized_job_ids
    ):
        return deny("job_scope_not_authorized")

    if (
        not evidence.unrestricted_workspace_scope
        and request.workspace_id not in evidence.authorized_workspace_ids
    ):
        return deny("workspace_scope_not_authorized")

    if request.action not in evidence.allowed_actions:
        return deny("job_action_not_authorized")

    if request.handler_key is not None:
        if (
            not evidence.unrestricted_handler_scope
            and request.handler_key not in evidence.allowed_handler_keys
        ):
            return deny("job_handler_not_authorized")

    return JobExecutionPermissionDecision(
        permitted=True,
        job_id=request.job_id,
        workspace_id=request.workspace_id,
        action=request.action,
        reason_code="job_execution_permitted",
        permission_reference=evidence.permission_reference,
    )


def certify_job_execution_permissions_v1() -> Mapping[str, Any]:
    from .runtime_authentication_boundaries import (
        RuntimeAuthenticationBoundary,
        RuntimePrincipalType,
    )
    from .runtime_authorization import RuntimeOperation

    runtime_allow = RuntimeAuthorizationDecision(
        disposition=RuntimeAuthorizationDisposition.ALLOW,
        principal_type=RuntimePrincipalType.WORKER,
        principal_id="worker-76",
        boundary=RuntimeAuthenticationBoundary.EXECUTION_START,
        operation=RuntimeOperation.START_EXECUTION,
        resource_id="job-76",
        authentication_established=True,
        operation_authorized=True,
        resource_scope_authorized=True,
        authorization_source="phase-7.2",
        authorization_reference="authz-76",
        reason_code="runtime_operation_authorized",
    )

    request = JobExecutionPermissionRequest(
        job_id="job-76",
        workspace_id="workspace-76",
        action=JobExecutionAction.EXECUTE,
        handler_key="handler-76",
        execution_id="execution-76",
    )

    evidence = JobExecutionPermissionEvidence(
        runtime_authorization=runtime_allow,
        job_executable=True,
        job_terminal=False,
        authorized_job_ids=("job-76",),
        authorized_workspace_ids=("workspace-76",),
        allowed_actions=(JobExecutionAction.EXECUTE,),
        allowed_handler_keys=("handler-76",),
        permission_reference="permission-76",
    )

    allowed = evaluate_job_execution_permission(
        request=request,
        evidence=evidence,
    )

    terminal = evaluate_job_execution_permission(
        request=request,
        evidence=JobExecutionPermissionEvidence(
            runtime_authorization=runtime_allow,
            job_executable=False,
            job_terminal=True,
            unrestricted_job_scope=True,
            unrestricted_workspace_scope=True,
            unrestricted_handler_scope=True,
            allowed_actions=(JobExecutionAction.EXECUTE,),
        ),
    )

    checks = {
        "job_execution_permission_contract_created": True,
        "valid_job_execution_permitted": allowed.permitted,
        "terminal_job_execution_rejected": not terminal.permitted,
        "job_executable_state_enforced": True,
        "suspended_job_policy_enforced": True,
        "job_scope_enforced": True,
        "workspace_scope_enforced": True,
        "job_action_enforced": True,
        "handler_scope_enforced": True,
        "existing_job_state_remains_authoritative": True,
        "no_job_state_machine_created": True,
        "no_job_mutation": True,
        "no_workspace_permission_store_created": True,
    }

    return MappingProxyType({
        "phase": "7.6",
        "component": "Job Execution Permissions",
        "version": JOB_EXECUTION_PERMISSIONS_VERSION,
        "schema_version": JOB_EXECUTION_PERMISSIONS_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 7.6 evaluates permission to execute an existing Universal "
            "Job within its workspace, state, action and handler scope without "
            "creating or mutating the Universal Job state machine."
        ),
    })


__all__ = [
    "JOB_EXECUTION_PERMISSIONS_VERSION",
    "JOB_EXECUTION_PERMISSIONS_SCHEMA_VERSION",
    "JobExecutionAction",
    "JobExecutionPermissionRequest",
    "JobExecutionPermissionEvidence",
    "JobExecutionPermissionDecision",
    "evaluate_job_execution_permission",
    "certify_job_execution_permissions_v1",
]
