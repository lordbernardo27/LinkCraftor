"""Universal Runtime persisted worker-claim verification.

Reuses existing AK6 persisted-lease evidence validation.
This is not worker authentication or a signed authorization grant.
"""
from __future__ import annotations

from backend.server.runtime.security.ak6_authoritative_lease import (
    require_persisted_ak6_lease,
)


class CanonicalWorkerClaimDenied(PermissionError):
    """Persisted worker ownership or lease verification denied."""


def require_canonical_worker_claim_v1(
    *,
    claimed_job,
    worker_id: str,
) -> str:
    """Verify the current persisted claim and active worker lease."""
    if not isinstance(worker_id, str) or not worker_id.strip():
        raise CanonicalWorkerClaimDenied("DENY_MISSING_WORKER_ID")

    if claimed_job is None:
        raise CanonicalWorkerClaimDenied("DENY_MISSING_CLAIMED_JOB")

    required = ("job_id", "workspace_id", "job_type", "status")

    job = {}

    for field in required:
        value = getattr(claimed_job, field, None)

        if not isinstance(value, str) or not value.strip():
            raise CanonicalWorkerClaimDenied(
                f"DENY_INVALID_CLAIMED_JOB_{field.upper()}"
            )

        job[field] = value

    metadata = getattr(claimed_job, "metadata", None)

    if not isinstance(metadata, dict):
        raise CanonicalWorkerClaimDenied("DENY_INVALID_CLAIM_METADATA")

    job["metadata"] = dict(metadata)

    # The existing validator reloads the authoritative persisted job.
    # Passing the claimed object alone does not authorize execution.
    try:
        return require_persisted_ak6_lease(
            job=job,
            worker_id=worker_id,
        )
    except PermissionError as exc:
        raise CanonicalWorkerClaimDenied(str(exc)) from exc
