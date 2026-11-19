"""Canonical job lifecycle bridge for Universal Runtime.

Reuses the existing orchestration job store.
Does not create, claim, enqueue or authorize jobs.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from backend.server.orchestration import service as orchestration


class CanonicalJobLifecycleError(RuntimeError):
    pass


def _require_running_job(
    job: Mapping[str, Any],
) -> str:
    if not isinstance(job, Mapping):
        raise CanonicalJobLifecycleError(
            "Universal Runtime job mapping required."
        )

    identities = {}

    for field in ("job_id", "workspace_id", "job_type"):
        value = job.get(field)

        if not isinstance(value, str) or not value.strip():
            raise CanonicalJobLifecycleError(
                f"Missing canonical job identity: {field}"
            )

        identities[field] = value.strip()

    job_id = identities["job_id"]

    snapshot = orchestration.get_orchestration_job(job_id)

    if not isinstance(snapshot, Mapping):
        raise CanonicalJobLifecycleError(
            "Canonical orchestration job does not exist."
        )

    persisted = snapshot.get("job")

    if not isinstance(persisted, Mapping):
        raise CanonicalJobLifecycleError(
            "Canonical orchestration record is invalid."
        )

    for field, expected in identities.items():
        if persisted.get(field) != expected:
            raise CanonicalJobLifecycleError(
                f"Canonical job identity mismatch: {field}"
            )

    if persisted.get("status") != "running":
        raise CanonicalJobLifecycleError(
            "Job must already be claimed and RUNNING."
        )

    return job_id


def begin_registered_job_v1(
    job: Mapping[str, Any],
) -> Any:
    job_id = _require_running_job(job)

    return orchestration.update_orchestration_progress(
        job_id=job_id,
        progress_percent=10.0,
        current_step="runtime_registration_dispatch",
        progress_message="Registered handler execution started.",
    )


def complete_registered_job_v1(
    job: Mapping[str, Any],
) -> Any:
    job_id = _require_running_job(job)

    return orchestration.mark_job_completed(
        job_id=job_id,
        metadata={
            "runtime_registration_dispatch": "completed",
        },
    )


def fail_registered_job_v1(
    job: Mapping[str, Any],
    *,
    error_message: str,
) -> Any:
    job_id = _require_running_job(job)

    if not isinstance(error_message, str):
        raise CanonicalJobLifecycleError(
            "Failure message must be a string."
        )

    message = error_message.strip()

    if not message:
        raise CanonicalJobLifecycleError(
            "Failure message cannot be empty."
        )

    return orchestration.mark_job_failed(
        job_id=job_id,
        error_message=message,
        metadata={
            "runtime_registration_dispatch": "failed",
        },
    )
