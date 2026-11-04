"""AK.6: enforce persisted queue claim + live worker lease for protected jobs.

This is NOT independent worker authentication, issuer provisioning or replay control.
No in-memory or caller-provided job record can substitute for the persisted job.
"""
from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone

_REQUIRED = (
    "claimed_by_dequeue", "worker_id", "assigned_worker_id",
    "assigned_worker_instance_id", "lease_owner", "lease_id",
    "lease_started_at", "lease_expires_at", "lease_active", "lease_released",
)


def _utc(value):
    if not isinstance(value, str) or not value:
        raise PermissionError("AK6_DENY_INVALID_LEASE_TIME")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise PermissionError("AK6_DENY_INVALID_LEASE_TIME") from exc
    if parsed.tzinfo is None:
        raise PermissionError("AK6_DENY_NAIVE_LEASE_TIME")
    return parsed.astimezone(timezone.utc)


def require_persisted_ak6_lease(*, job, worker_id, job_loader=None, now=None):
    """Fail closed if execution metadata differs from a current persisted claim.

    Default loader imports the authoritative orchestration job store lazily.
    job_loader injection is intended ONLY for isolated tests.
    This does not authenticate the OS process; that remains an AK.6 blocker.
    """
    if not isinstance(job, Mapping):
        raise PermissionError("AK6_DENY_JOB_MAPPING")
    job_id = job.get("job_id")
    if not isinstance(job_id, str) or not job_id:
        raise PermissionError("AK6_DENY_JOB_ID")
    if not isinstance(worker_id, str) or not worker_id:
        raise PermissionError("AK6_DENY_WORKER_ID")
    if job_loader is None:
        from backend.server.orchestration.job_store import get_job
        job_loader = get_job
    try:
        stored = job_loader(job_id)
    except Exception as exc:
        raise PermissionError("AK6_DENY_STORE_UNAVAILABLE") from exc
    if stored is None:
        raise PermissionError("AK6_DENY_UNPERSISTED_JOB")
    if getattr(stored, "job_id", None) != job_id:
        raise PermissionError("AK6_DENY_STORED_JOB_ID")
    if getattr(stored, "workspace_id", None) != job.get("workspace_id"):
        raise PermissionError("AK6_DENY_STORED_WORKSPACE")
    if getattr(stored, "job_type", None) != (job.get("job_type") or job.get("stage")):
        raise PermissionError("AK6_DENY_STORED_STAGE")
    if getattr(stored, "status", None) != "running" or job.get("status") != "running":
        raise PermissionError("AK6_DENY_STORED_JOB_STATE")
    metadata = job.get("metadata")
    saved = getattr(stored, "metadata", None)
    if not isinstance(metadata, Mapping) or not isinstance(saved, Mapping):
        raise PermissionError("AK6_DENY_MISSING_CLAIM_METADATA")
    for key in _REQUIRED:
        if key not in saved or key not in metadata or saved[key] != metadata[key]:
            raise PermissionError("AK6_DENY_CLAIM_EVIDENCE_MISMATCH")
    if saved["claimed_by_dequeue"] is not True or saved["lease_active"] is not True:
        raise PermissionError("AK6_DENY_CLAIM_OR_LEASE_INACTIVE")
    if saved["lease_released"] is not False:
        raise PermissionError("AK6_DENY_LEASE_RELEASED")
    if saved["worker_id"] != worker_id or saved["assigned_worker_id"] != worker_id:
        raise PermissionError("AK6_DENY_LEASE_WORKER")
    for key in ("assigned_worker_instance_id", "lease_owner", "lease_id"):
        if not isinstance(saved[key], str) or not saved[key].strip():
            raise PermissionError("AK6_DENY_LEASE_IDENTITY")
    start, end = _utc(saved["lease_started_at"]), _utc(saved["lease_expires_at"])
    clock = now if now is not None else datetime.now(timezone.utc)
    if not isinstance(clock, datetime) or clock.tzinfo is None:
        raise PermissionError("AK6_DENY_CLOCK")
    clock = clock.astimezone(timezone.utc)
    if not (start <= clock < end):
        raise PermissionError("AK6_DENY_LEASE_EXPIRED_OR_FUTURE")
    return saved["lease_id"]
