from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

from backend.server.coordination.universal_workflows.contract import (
    UniversalWorkflow,
    UniversalWorkflowStatus,
)
from backend.server.coordination.workflow_persistence.repository import (
    WorkflowPersistenceNotFoundError,
)
from backend.server.pipelines.connect_domain.coordinator import (
    CONNECTED_DOMAIN_STAGE_IDS,
    build_connected_domain_coordinator_contract,
    connect_connected_domain_to_universal_coordination,
    coordinate_connect_domain_pipeline,
)
from backend.server.pipelines.connect_domain.manifest import (
    build_connected_domain_pipeline_manifest,
)
from backend.server.pipelines.connect_domain.runtime_hydration import (
    CONNECTED_DOMAIN_HYDRATOR_REF,
)
from backend.server.runtime.runtime_payload_hydration import (
    RUNTIME_PAYLOAD_HYDRATOR_KEY,
)


CONNECTED_DOMAIN_ACTIVATION_VERSION = "connected_domain_activation_v1.0.0"


class ConnectedDomainActivationError(RuntimeError):
    pass


def _plain(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Mapping):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_plain(item) for item in value]
    for name in ("to_dict", "to_canonical_dict"):
        method = getattr(value, name, None)
        if callable(method):
            return _plain(method())
    if hasattr(value, "__dict__"):
        return _plain(vars(value))
    return str(value)


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def activate_connected_domain_pipeline(
    *,
    runtime_gateway: Any,
    workspace_id: str | None = None,
    workspace_name: str | None = None,
    domain: str | None = None,
    site_url: str | None = None,
    url: str | None = None,
    payload_by_stage: Mapping[str, Any] | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    repository = getattr(runtime_gateway, "workflow_repository", None)
    if repository is None:
        raise ConnectedDomainActivationError(
            "Runtime Coordination Gateway has no workflow repository."
        )
    supplied = dict(payload_by_stage or {})
    hydrated_payloads: dict[str, dict[str, Any]] = {}
    for stage_id in CONNECTED_DOMAIN_STAGE_IDS:
        stage_payload = supplied.get(stage_id, {})
        if not isinstance(stage_payload, Mapping):
            raise ConnectedDomainActivationError(
                f"Payload for {stage_id} must be a mapping."
            )
        hydrated_payloads[stage_id] = {
            **dict(stage_payload),
            RUNTIME_PAYLOAD_HYDRATOR_KEY: CONNECTED_DOMAIN_HYDRATOR_REF,
        }

    intent = coordinate_connect_domain_pipeline(
        workspace_id=workspace_id,
        workspace_name=workspace_name,
        domain=domain,
        site_url=site_url,
        url=url,
        payload_by_stage=hydrated_payloads,
        metadata={
            **dict(metadata or {}),
            "activation_authority": "activate_connected_domain_pipeline",
            "hydration_authority": CONNECTED_DOMAIN_HYDRATOR_REF,
        },
    )

    # A3.2: Validate the canonical workspace profile identity
    # before creating or submitting runtime work.
    from pathlib import Path as _WorkspacePath
    import json as _workspace_json

    _workspace_root = _WorkspacePath(
        "backend/server/data/workspaces"
    ).resolve()

    _workspace_id = str(intent.workspace_id)

    _workspace_dir = (
        _workspace_root / _workspace_id
    ).resolve()

    if (
        not _workspace_id
        or _workspace_dir.parent != _workspace_root
    ):
        raise ConnectedDomainActivationError(
            "Invalid canonical workspace directory identity."
        )

    _profile_path = (
        _workspace_dir / "workspace_profile.json"
    )

    _existing_profile = None

    if _profile_path.exists():
        try:
            _existing_profile = _workspace_json.loads(
                _profile_path.read_text(
                    encoding="utf-8-sig"
                )
            )
        except (OSError, ValueError) as exc:
            raise ConnectedDomainActivationError(
                "Existing workspace profile cannot be read."
            ) from exc

        if not isinstance(_existing_profile, dict):
            raise ConnectedDomainActivationError(
                "Existing workspace profile is invalid."
            )

        if (
            _existing_profile.get("workspace_id")
            != intent.workspace_id
            or str(
                _existing_profile.get("domain") or ""
            ).lower() != str(intent.domain).lower()
            or _existing_profile.get("workspace_mode")
            not in ("domain", "connect_domain")
        ):
            raise ConnectedDomainActivationError(
                "Existing workspace identity conflicts with "
                "Connected Domain activation."
            )

    manifest = build_connected_domain_pipeline_manifest(
        workflow_id=intent.workflow_id,
    )
    coordinator_contract = build_connected_domain_coordinator_contract()
    now = _timestamp()
    workflow = UniversalWorkflow(
        workflow_id=intent.workflow_id,
        workflow_type=coordinator_contract.workflow_type,
        workflow_version=coordinator_contract.workflow_version,
        workspace_id=intent.workspace_id,
        coordinator_id=coordinator_contract.coordinator_id,
        coordinator_version=coordinator_contract.coordinator_version,
        correlation_id=intent.correlation_id,
        parent_workflow_id=None,
        root_workflow_id=intent.workflow_id,
        status=UniversalWorkflowStatus.CREATED,
        input_reference=None,
        context=dict(intent.context),
        metadata={
            **dict(intent.metadata),
            "activation_version": CONNECTED_DOMAIN_ACTIVATION_VERSION,
            "manifest_identity_fingerprint": manifest.identity_fingerprint(),
            "manifest_content_fingerprint": manifest.content_fingerprint(),
        },
        current_stage=CONNECTED_DOMAIN_STAGE_IDS[0],
        pending_stages=CONNECTED_DOMAIN_STAGE_IDS,
        idempotency_key="connected_domain:" + intent.workflow_id,
        created_at=now,
        updated_at=now,
    )
    try:
        existing = repository.load_workflow_record(intent.workflow_id)
    except WorkflowPersistenceNotFoundError:
        persistence = repository.save_workflow(workflow)
        persisted_workflow = workflow
        workflow_created = True
    else:
        persisted_workflow = existing.workflow
        if (
            persisted_workflow.workspace_id != intent.workspace_id
            or persisted_workflow.correlation_id != intent.correlation_id
            or persisted_workflow.workflow_type != coordinator_contract.workflow_type
        ):
            raise ConnectedDomainActivationError(
                "Existing workflow identity conflicts with Connect Domain request."
            )
        persistence = existing.evidence
        workflow_created = False

    connection = connect_connected_domain_to_universal_coordination(
        runtime_gateway=runtime_gateway,
        execution_plan=manifest.execution_plan,
        stage_references=manifest.stage_references,
        workspace_id=intent.workspace_id,
        workspace_name=intent.workspace_name,
        domain=intent.domain,
        site_url=intent.site_url,
        workflow_id=intent.workflow_id,
        correlation_id=intent.correlation_id,
        payload_by_stage=hydrated_payloads,
        metadata=dict(intent.metadata),
        execution_semantics="dependency_ordered",
    )
    submission = connection.runtime_submission

    # Persist the workspace identity only after the canonical
    # runtime submission has returned successfully.
    # Never overwrite an existing customer workspace profile.
    if _existing_profile is None:
        if _profile_path.exists():
            raise ConnectedDomainActivationError(
                "Workspace profile appeared during activation; "
                "refusing to overwrite it."
            )

        from backend.server.pipelines.connect_domain.coordinator import (
            _persist_workspace_profile,
        )

        _persist_workspace_profile(
            workspace_id=intent.workspace_id,
            workspace_name=intent.workspace_name,
            workspace_mode="domain",
            domain=intent.domain,
            site_url=intent.site_url,
        )

    # Successful submission means processing, not completed.
    job_ids = tuple(getattr(submission, "job_ids", ()) or ())
    return {
        "ok": True,
        "connected": False,
        "connection_status": "processing",
        "execution_mode": "asynchronous",
        "workspace_id": intent.workspace_id,
        "workspace_name": intent.workspace_name,
        "workspace_mode": "connect_domain",
        "domain": intent.domain,
        "site_url": intent.site_url,
        "workflow_id": intent.workflow_id,
        "correlation_id": intent.correlation_id,
        "workflow_created": workflow_created,
        "workflow_status": persisted_workflow.status.value,
        "job_ids": list(job_ids),
        "stage_ids": list(CONNECTED_DOMAIN_STAGE_IDS),
        "pipeline": {
            "pipeline_id": "connect_domain",
            "manifest_finalized": True,
            "runtime_submission_connected": True,
            "hydration_connected": True,
        },
        "persistence": _plain(persistence),
        "runtime_submission": _plain(submission),
    }
