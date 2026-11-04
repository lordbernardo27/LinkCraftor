"""
AK.6 ? Connected Domain job execution permission adapter.

Reuses existing Universal Runtime permission evaluators.

This component is NOT an authorization issuer.
It cannot independently authenticate a worker.
It cannot activate production execution.
"""

from backend.server.runtime.universal_runtime_worker_scope_contract import (
    EXPECTED_SCOPE,
    WORKSPACE_ID,
    STAGES,
)

from backend.server.runtime.security.job_execution_permissions import (
    JobExecutionAction,
    JobExecutionPermissionEvidence,
    JobExecutionPermissionRequest,
    evaluate_job_execution_permission,
)

from backend.server.runtime.security.runtime_authorization import (
    RuntimeAuthorizationDisposition,
    RuntimeOperation,
)

from backend.server.runtime.security.runtime_authentication_boundaries import (
    RuntimePrincipalType,
)

WORKER_ID = "universal_runtime_worker_v1"


def require_connected_domain_job_execution_permission(
    *,
    job_id,
    workspace_id,
    handler_key,
    worker_id,
    evidence,
):
    if not isinstance(job_id, str) or job_id not in EXPECTED_SCOPE:
        raise PermissionError("AK_DENY_JOB_SCOPE")

    if workspace_id != WORKSPACE_ID:
        raise PermissionError("AK_DENY_WORKSPACE_SCOPE")

    if worker_id != WORKER_ID:
        raise PermissionError("AK_DENY_WORKER_ID")

    if not isinstance(handler_key, str) or not handler_key.strip():
        raise PermissionError("AK_DENY_HANDLER_KEY")

    # AK6_CANONICAL_STAGE_HANDLER_BINDING
    # The handler key supplied by a caller must match the job's
    # frozen stage identity. Merely listing a key in evidence is
    # insufficient to authorize a different handler for this job.
    expected_stage = next(
        (stage for stage, canonical_job_id, _, _ in STAGES
         if canonical_job_id == job_id),
        None,
    )
    if handler_key != expected_stage:
        raise PermissionError("AK_DENY_STAGE_HANDLER_MISMATCH")

    if not isinstance(evidence, JobExecutionPermissionEvidence):
        raise PermissionError("AK_DENY_MISSING_EVIDENCE")

    runtime = evidence.runtime_authorization

    if runtime.disposition is not RuntimeAuthorizationDisposition.ALLOW:
        raise PermissionError("AK_DENY_RUNTIME_AUTHORIZATION")

    if (
        runtime.principal_type is not RuntimePrincipalType.WORKER
        or runtime.principal_id != WORKER_ID
        or runtime.operation is not RuntimeOperation.START_EXECUTION
        or runtime.resource_id != job_id
    ):
        raise PermissionError("AK_DENY_AUTHORIZATION_BINDING")

    if not (
        runtime.authentication_established is True
        and runtime.operation_authorized is True
        and runtime.resource_scope_authorized is True
    ):
        raise PermissionError("AK_DENY_AUTHORIZATION_CONDITIONS")

    if not (
        isinstance(runtime.authorization_reference, str)
        and runtime.authorization_reference.strip()
        and isinstance(evidence.permission_reference, str)
        and evidence.permission_reference.strip()
    ):
        raise PermissionError("AK_DENY_MISSING_REFERENCES")

    if (
        evidence.unrestricted_job_scope
        or evidence.unrestricted_workspace_scope
        or evidence.unrestricted_handler_scope
    ):
        raise PermissionError("AK_DENY_UNRESTRICTED_SCOPE")

    request = JobExecutionPermissionRequest(
        job_id=job_id,
        workspace_id=workspace_id,
        action=JobExecutionAction.EXECUTE,
        handler_key=handler_key,
    )

    decision = evaluate_job_execution_permission(
        request=request,
        evidence=evidence,
    )

    if (
        decision.permitted is not True
        or decision.job_id != job_id
        or decision.workspace_id != workspace_id
        or decision.action is not JobExecutionAction.EXECUTE
    ):
        raise PermissionError(
            "AK_DENY_EXECUTION_PERMISSION:"
            + str(decision.reason_code)
        )

    return decision
