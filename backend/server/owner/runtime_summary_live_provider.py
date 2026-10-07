"""
Universal Runtime Owner Control Tower
Phase 2.18 — Live Runtime Summary Provider

Read-only production projection.

Authority rules:
- Runtime Observability remains top-level health authority.
- Canonical orchestration job/queue persistence remains job/queue authority.
- Owner layer does not mutate jobs, queues, workers, leases, executions,
  orchestration, persistence, recovery, or security.
- Missing operational surfaces remain empty/UNKNOWN rather than fabricated.
"""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional


RUNTIME_SUMMARY_LIVE_PROVIDER_VERSION = (
    "runtime_owner_summary_live_provider_v2.18.1"
)

RUNTIME_SUMMARY_LIVE_PROVIDER_SCHEMA_VERSION = (
    "runtime_owner_summary_live_provider_schema_v1"
)


def _mapping(value: Any) -> dict[str, Any]:
    if value is None:
        return {}

    if isinstance(value, Mapping):
        return dict(value)

    to_dict = getattr(value, "to_dict", None)

    if callable(to_dict):
        payload = to_dict()

        if isinstance(payload, Mapping):
            return dict(payload)

    if is_dataclass(value):
        return asdict(value)

    raw = getattr(value, "__dict__", None)

    if isinstance(raw, Mapping):
        return dict(raw)

    return {}


def _job_payload(job: Any) -> dict[str, Any]:
    payload = _mapping(job)

    metadata = payload.get("metadata")

    if not isinstance(metadata, Mapping):
        metadata = {}

    payload["metadata"] = dict(metadata)

    return payload


def _status(
    payload: Mapping[str, Any],
) -> str:
    return str(
        payload.get("status") or ""
    ).strip().upper()


def _parse_datetime(
    value: Any,
) -> Optional[datetime]:

    if isinstance(value, datetime):
        result = value

    elif value is None:
        return None

    else:
        text = str(value).strip()

        if not text:
            return None

        try:
            result = datetime.fromisoformat(
                text.replace("Z", "+00:00")
            )
        except ValueError:
            return None

    if result.tzinfo is None:
        result = result.replace(
            tzinfo=timezone.utc
        )

    return result.astimezone(
        timezone.utc
    )


def _oldest_queue_age_seconds(
    queued_jobs: Iterable[Mapping[str, Any]],
) -> float:

    now = datetime.now(
        timezone.utc
    )

    created = []

    for job in queued_jobs:

        parsed = _parse_datetime(
            job.get("created_at")
        )

        if parsed is not None:
            created.append(
                parsed
            )

    if not created:
        return 0.0

    age = (
        now - min(created)
    ).total_seconds()

    return max(
        0.0,
        float(age),
    )


def _assigned_workers(
    jobs: Iterable[Mapping[str, Any]],
) -> tuple[dict[str, Any], ...]:

    worker_ids = set()

    for job in jobs:

        if _status(job) != "RUNNING":
            continue

        worker_id = (
            job.get("assigned_worker_id")
            or job.get("worker_id")
        )

        if worker_id is None:
            continue

        text = str(
            worker_id
        ).strip()

        if text:
            worker_ids.add(
                text
            )

    return tuple(
        {
            "worker_id": worker_id,
            "active": True,
            "status": "ACTIVE",
        }
        for worker_id
        in sorted(worker_ids)
    )


def _lease_evidence(
    jobs: Iterable[Mapping[str, Any]],
) -> tuple[dict[str, Any], ...]:

    leases = []

    for job in jobs:

        metadata = job.get(
            "metadata"
        )

        if not isinstance(
            metadata,
            Mapping,
        ):
            metadata = {}

        lease_id = (
            job.get("lease_id")
            or metadata.get("lease_id")
        )

        if not lease_id:
            continue

        lease_state = str(
            job.get("lease_state")
            or metadata.get("lease_state")
            or ""
        ).strip().upper()

        active = (
            lease_state == "ACTIVE"
        )

        leases.append(
            {
                "lease_id":
                    str(lease_id),

                "job_id":
                    str(
                        job.get("job_id")
                        or ""
                    ),

                "active":
                    active,

                "status":
                    (
                        lease_state
                        or "UNKNOWN"
                    ),
            }
        )

    return tuple(
        leases
    )


def _execution_evidence(
    jobs: Iterable[Mapping[str, Any]],
) -> tuple[dict[str, Any], ...]:
    """
    Only expose executions when a real execution identity is present in
    persisted job/metadata evidence.

    Job status is NOT silently converted into execution status.
    """

    executions = []

    for job in jobs:

        metadata = job.get(
            "metadata"
        )

        if not isinstance(
            metadata,
            Mapping,
        ):
            metadata = {}

        execution_id = (
            job.get("execution_id")
            or metadata.get("execution_id")
        )

        if not execution_id:
            continue

        state = str(
            job.get("execution_state")
            or metadata.get("execution_state")
            or metadata.get("execution_status")
            or ""
        ).strip().upper()

        executions.append(
            {
                "execution_id":
                    str(execution_id),

                "job_id":
                    str(
                        job.get("job_id")
                        or ""
                    ),

                "status":
                    state or "UNKNOWN",

                "active":
                    state == "RUNNING",
            }
        )

    return tuple(
        executions
    )


def _orchestration_evidence(
    jobs: Iterable[Mapping[str, Any]],
) -> tuple[dict[str, Any], ...]:
    """
    OrchestrationJob is the canonical persisted orchestration work item,
    therefore its persisted lifecycle is valid orchestration evidence.
    """

    return tuple(
        {
            "orchestration_id":
                str(
                    job.get("job_id")
                    or ""
                ),

            "job_id":
                str(
                    job.get("job_id")
                    or ""
                ),

            "status":
                _status(job),

            "active":
                _status(job)
                in {
                    "RUNNING",
                    "PROCESSING",
                    "ACTIVE",
                },
        }
        for job in jobs
    )


def _build_live_source_snapshot(
    application: Any,
) -> dict[str, Any]:

    from backend.server.orchestration.job_store import (
        load_jobs,
    )

    from backend.server.orchestration.queue import (
        queue_snapshot,
    )

    persisted = load_jobs()

    jobs = tuple(
        _job_payload(job)
        for job
        in persisted.values()
    )

    queue = queue_snapshot()

    queued_jobs = tuple(
        dict(item)
        for item
        in queue.get(
            "queued_jobs",
            (),
        )
        if isinstance(
            item,
            Mapping,
        )
    )

    workers = _assigned_workers(
        jobs
    )

    leases = _lease_evidence(
        jobs
    )

    executions = _execution_evidence(
        jobs
    )

    orchestrations = (
        _orchestration_evidence(
            jobs
        )
    )

    lifecycle_status = str(
        getattr(
            application.state,
            "runtime_lifecycle_status",
            "",
        )
        or ""
    ).strip().upper()

    runtime_available = (
        lifecycle_status == "RUNNING"
    )

    return {
        "jobs":
            jobs,

        "queue":
            queue,

        "queued_jobs":
            queued_jobs,

        "workers":
            workers,

        "leases":
            leases,

        "executions":
            executions,

        "orchestrations":
            orchestrations,

        "runtime_available":
            runtime_available,

        "runtime_lifecycle_status":
            lifecycle_status
            or "UNKNOWN",

        "oldest_queue_age_seconds":
            _oldest_queue_age_seconds(
                queued_jobs
            ),
    }


def build_live_runtime_owner_summary(
    application: Any,
) -> dict[str, Any]:

    from backend.server.owner.runtime_health_read_model import (
        build_runtime_owner_health_read_model,
    )

    from backend.server.owner.runtime_architecture_version_read_model import (
        build_runtime_architecture_version_read_model,
    )

    from backend.server.owner.runtime_activity_read_model import (
        build_runtime_activity_read_model,
    )

    from backend.server.owner.runtime_work_state_read_model import (
        build_runtime_work_state_read_model,
    )

    from backend.server.owner.runtime_infrastructure_health_read_model import (
        build_runtime_infrastructure_health_read_model,
    )

    from backend.server.owner.runtime_security_api_alert_attention_read_model import (
        build_runtime_security_api_alert_attention_read_model,
    )

    from backend.server.runtime.observability.runtime_health_signals import (
        RuntimeHealthEvidence,
        evaluate_runtime_health,
    )

    from backend.server.runtime.observability.alerting_boundaries import (
        RuntimeAlertEvidence,
        evaluate_runtime_alert_boundary,
    )

    source = _build_live_source_snapshot(
        application
    )

    jobs = source["jobs"]
    workers = source["workers"]
    leases = source["leases"]
    executions = source["executions"]
    orchestrations = source[
        "orchestrations"
    ]

    running_jobs = sum(
        1
        for job in jobs
        if _status(job) == "RUNNING"
    )

    failed_jobs = sum(
        1
        for job in jobs
        if _status(job) == "FAILED"
    )

    running_executions = sum(
        1
        for execution in executions
        if str(
            execution.get("status")
            or ""
        ).upper() == "RUNNING"
    )

    failed_executions = sum(
        1
        for execution in executions
        if str(
            execution.get("status")
            or ""
        ).upper()
        in {
            "FAILED",
            "CRASHED",
        }
    )

    health_evidence = (
        RuntimeHealthEvidence(
            runtime_available=(
                source[
                    "runtime_available"
                ]
            ),

            queue_depth=int(
                source["queue"].get(
                    "queue_length",
                    0,
                )
            ),

            oldest_queue_age_seconds=(
                source[
                    "oldest_queue_age_seconds"
                ]
            ),

            active_workers=len(
                workers
            ),

            # No canonical persisted stale-worker snapshot is currently
            # exposed by the production boot surface. Do not infer stale
            # workers from missing heartbeat evidence.
            stale_workers=0,

            running_jobs=(
                running_jobs
            ),

            failed_jobs=(
                failed_jobs
            ),

            running_executions=(
                running_executions
            ),

            failed_executions=(
                failed_executions
            ),

            critical_error_count=0,

            source_reference=(
                "runtime_owner_live_provider:"
                "orchestration_store+queue"
            ),
        )
    )

    health_signal = (
        evaluate_runtime_health(
            health_evidence
        )
    )

    alert_decision = (
        evaluate_runtime_alert_boundary(
            RuntimeAlertEvidence(
                health_signal=(
                    health_signal
                ),

                critical_error_count=0,

                queue_depth=(
                    health_evidence
                    .queue_depth
                ),

                stale_worker_count=(
                    health_evidence
                    .stale_workers
                ),

                source_reference=(
                    health_signal
                    .source_reference
                ),
            )
        )
    )

    observability_handoff = {
        "runtime_health":
            health_signal.status.value,

        "health_reasons":
            list(
                health_signal.reasons
            ),

        "source_reference":
            health_signal
            .source_reference,

        "alert_summary": {
            "active":
                (
                    1
                    if alert_decision
                    .alert_required
                    else 0
                ),

            "critical":
                (
                    1
                    if (
                        alert_decision
                        .alert_required
                        and
                        alert_decision
                        .severity.value
                        == "CRITICAL"
                    )
                    else 0
                ),

            "warning":
                (
                    1
                    if (
                        alert_decision
                        .alert_required
                        and
                        alert_decision
                        .severity.value
                        == "WARNING"
                    )
                    else 0
                ),

            "severity":
                alert_decision
                .severity.value,

            "reason_codes":
                list(
                    alert_decision
                    .reason_codes
                ),
        },

        "error_summary": {
            "critical": 0,
            "error": 0,
        },

        "owner_attention_required":
            alert_decision
            .alert_required,
    }

    # These supporting handoffs deliberately report UNKNOWN where no
    # live canonical governance handoff is registered. They do not
    # recompute Resource Governance, Persistence or Security authority.
    resource_handoff = {
        "runtime_capacity_status":
            "UNKNOWN",

        "worker_capacity_status":
            "UNKNOWN",

        "queue_capacity_status":
            "UNKNOWN",

        "pressure_status":
            "UNKNOWN",

        "owner_attention_required":
            False,

        "evidence_reference":
            "runtime_owner_live_provider:"
            "resource_handoff_unavailable",
    }

    persistence_handoff = {
        "persistence_health":
            "READABLE",

        "owner_attention_required":
            False,

        "evidence_reference":
            "runtime_owner_live_provider:"
            "orchestration_job_store_read",
    }

    runtime_api_handoff = {
        "api_health_status":
            "AVAILABLE",

        "security_integration_status":
            "UNKNOWN",

        "owner_attention_required":
            False,

        "evidence_reference":
            "runtime_owner_live_provider:"
            "owner_summary_api",
    }

    health = (
        build_runtime_owner_health_read_model(
            observability_handoff=(
                observability_handoff
            ),
            persistence_handoff=(
                persistence_handoff
            ),
            resource_handoff=(
                resource_handoff
            ),
            runtime_api_handoff=(
                runtime_api_handoff
            ),
        )
        .to_dict()
    )

    architecture = (
        build_runtime_architecture_version_read_model(
            runtime_root=Path(
                "backend/server/runtime"
            )
        )
        .to_dict()
    )

    activity = (
        build_runtime_activity_read_model(
            jobs=jobs,
            executions=executions,
            workers=workers,
            leases=leases,
        )
        .to_dict()
    )

    work_state = (
        build_runtime_work_state_read_model(
            orchestrations=(
                orchestrations
            ),
            jobs=jobs,
            executions=executions,
        )
        .to_dict()
    )

    infrastructure = (
        build_runtime_infrastructure_health_read_model(
            resource_handoff=(
                resource_handoff
            ),
            persistence_handoff=(
                persistence_handoff
            ),
        )
        .to_dict()
    )

    security_api_alert_attention = (
        build_runtime_security_api_alert_attention_read_model(
            runtime_api_handoff=(
                runtime_api_handoff
            ),
            observability_handoff=(
                observability_handoff
            ),
            resource_handoff=(
                resource_handoff
            ),
            persistence_handoff=(
                persistence_handoff
            ),
        )
        .to_dict()
    )

    return {
        "health":
            health,

        "architecture":
            architecture,

        "activity":
            activity,

        "work_state":
            work_state,

        "infrastructure":
            infrastructure,

        "security_api_alert_attention":
            security_api_alert_attention,
    }


def create_runtime_owner_summary_provider(
    application: Any,
):
    """
    Create the zero-argument provider expected by Phase 2.18.
    """

    def provider():
        return build_live_runtime_owner_summary(
            application
        )

    return provider


def install_live_runtime_owner_summary_provider(
    application: Any,
) -> None:

    from backend.server.owner.runtime_summary_api import (
        install_runtime_owner_summary_provider,
    )

    install_runtime_owner_summary_provider(
        application,
        create_runtime_owner_summary_provider(
            application
        ),
    )


__all__ = [
    "RUNTIME_SUMMARY_LIVE_PROVIDER_VERSION",
    "RUNTIME_SUMMARY_LIVE_PROVIDER_SCHEMA_VERSION",
    "build_live_runtime_owner_summary",
    "create_runtime_owner_summary_provider",
    "install_live_runtime_owner_summary_provider",
]
