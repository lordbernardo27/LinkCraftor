"""
Runtime Registration for Connect Domain Pipeline 1.

Registered job:
    linking_target_pipeline_batch

This is foundational Runtime Registration only.
Full Universal Runtime Infrastructure integration remains deferred.
"""

from __future__ import annotations

from typing import Any, Dict

from backend.server.runtime.universal_runtime_registration import (
    register_runtime_handler,
)
from backend.server.pipelines.connect_domain.job_types import (
    LINKING_TARGET_PIPELINE_BATCH,
)
from backend.server.pipelines.connect_domain.linking_target_pipeline.coordinator import (
    run_linking_target_pipeline,
)


class _PipelinePayload:
    def __init__(
        self,
        *,
        workspace_id: str | None,
        domain: str | None,
    ) -> None:
        self.workspace_id = workspace_id
        self.domain = domain


def execute_linking_target_pipeline_job(
    job: Dict[str, Any] | None = None,
    payload: Dict[str, Any] | None = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Runtime handler for the Linking Target Pipeline.

    The flexible signature supports dispatchers that supply either:
    - the complete job record;
    - the payload directly; or
    - keyword arguments.
    """

    job_obj = job if isinstance(job, dict) else {}
    payload_obj = payload if isinstance(payload, dict) else {}

    if not payload_obj:
        nested_payload = job_obj.get("payload")

        if isinstance(nested_payload, dict):
            payload_obj = nested_payload
        elif job_obj:
            payload_obj = job_obj

    if kwargs:
        payload_obj = {
            **payload_obj,
            **kwargs,
        }

    workspace_id = str(
        payload_obj.get("workspace_id")
        or job_obj.get("workspace_id")
        or ""
    ).strip()

    domain = str(
        payload_obj.get("domain")
        or payload_obj.get("url")
        or ""
    ).strip()

    if not workspace_id:
        return {
            "ok": False,
            "error": "workspace_id_required",
            "job_type": LINKING_TARGET_PIPELINE_BATCH,
        }

    if not domain:
        return {
            "ok": False,
            "workspace_id": workspace_id,
            "error": "domain_required",
            "job_type": LINKING_TARGET_PIPELINE_BATCH,
        }

    result = run_linking_target_pipeline(
        _PipelinePayload(
            workspace_id=workspace_id,
            domain=domain,
        )
    )

    return {
        "ok": bool(result.get("ok")),
        "workspace_id": workspace_id,
        "domain": domain,
        "job_type": LINKING_TARGET_PIPELINE_BATCH,
        "pipeline": "linking_target_pipeline",
        "result": result,
    }


def ensure_linking_target_pipeline_registration() -> Dict[str, Any]:
    """
    Register or refresh the Pipeline 1 runtime handler.

    replace=True makes repeated application startup and route calls safe.
    persist=True records the registration for later runtime loading.
    """

    return register_runtime_handler(
        job_type=LINKING_TARGET_PIPELINE_BATCH,
        handler=execute_linking_target_pipeline_job,
        pipeline="linking_target_pipeline",
        stage=LINKING_TARGET_PIPELINE_BATCH,
        description=(
            "Build Site Sources, Site Pages, target pools, clusters, "
            "enrichment, Active Target Set, and URL Pool."
        ),
        required_payload_fields=[
            "workspace_id",
            "domain",
        ],
        predecessor_stages=[],
        successor_stages=[],
        idempotency_fields=[
            "workspace_id",
            "domain",
        ],
        retry_policy={
            "max_attempts": 3,
            "retryable": True,
        },
        concurrency_policy={
            "scope": "workspace",
            "max_concurrency": 1,
        },
        metadata={
            "architecture": "connect_domain_pipeline_1",
            "runtime_layer": "foundational_registration",
            "full_runtime_infrastructure": "deferred",
        },
        replace=True,
        persist=True,
    )
