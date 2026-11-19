"""UDARE persisted admission evidence verification.

This checks recorded evidence against canonical persisted state.
It does NOT authenticate a concurrency reservation or grant execution.
"""

from collections.abc import Mapping
from typing import Any


class UDAREAdmissionEvidenceDenied(PermissionError):
    """Canonical UDARE admission evidence is unavailable or invalid."""


_ADMISSION_FIELDS = (
    "runtime_registration_policy_schema_version",
    "runtime_registration_queue_action",
    "runtime_registration_policy_reason",
    "runtime_registration_job_type",
    "runtime_registration_concurrency_limit",
    "runtime_registration_active_count",
    "runtime_registration_existing_job_id",
    "runtime_registration_policy_evidence",
)


def require_udare_persisted_admission_evidence_v1(
    *,
    claimed_job: Any,
) -> dict[str, Any]:
    """Validate recorded admission evidence; never grant execution."""
    if getattr(claimed_job, "job_type", None) != "udare_reconstruction":
        raise UDAREAdmissionEvidenceDenied(
            "UDARE_DENY_INVALID_JOB_TYPE"
        )

    job_id = getattr(claimed_job, "job_id", None)
    workspace_id = getattr(claimed_job, "workspace_id", None)

    if (
        not isinstance(job_id, str)
        or not job_id.strip()
        or not isinstance(workspace_id, str)
        or not workspace_id.strip()
    ):
        raise UDAREAdmissionEvidenceDenied(
            "UDARE_DENY_INVALID_JOB_IDENTITY"
        )

    if getattr(claimed_job, "status", None) != "running":
        raise UDAREAdmissionEvidenceDenied(
            "UDARE_DENY_JOB_NOT_RUNNING"
        )

    from backend.server.orchestration.job_store import get_job
    from backend.server.runtime.universal_runtime_registration import (
        get_runtime_registration,
    )
    from backend.server.runtime.runtime_registration_execution_policy import (
        _concurrency_policy,
    )

    try:
        stored = get_job(job_id)
    except Exception as exc:
        raise UDAREAdmissionEvidenceDenied(
            "UDARE_DENY_JOB_STORE_UNAVAILABLE"
        ) from exc

    if (
        stored is None
        or getattr(stored, "job_id", None) != job_id
        or getattr(stored, "workspace_id", None) != workspace_id
        or getattr(stored, "job_type", None) != "udare_reconstruction"
        or getattr(stored, "status", None) != "running"
    ):
        raise UDAREAdmissionEvidenceDenied(
            "UDARE_DENY_PERSISTED_JOB_MISMATCH"
        )

    presented = getattr(claimed_job, "metadata", None)
    persisted = getattr(stored, "metadata", None)

    if not isinstance(presented, Mapping) or not isinstance(
        persisted, Mapping
    ):
        raise UDAREAdmissionEvidenceDenied(
            "UDARE_DENY_ADMISSION_METADATA_MISSING"
        )

    for field in _ADMISSION_FIELDS:
        if (
            field not in presented
            or field not in persisted
            or presented[field] != persisted[field]
        ):
            raise UDAREAdmissionEvidenceDenied(
                "UDARE_DENY_ADMISSION_EVIDENCE_MISMATCH"
            )

    try:
        registration = get_runtime_registration(
            "udare_reconstruction"
        )
    except Exception as exc:
        raise UDAREAdmissionEvidenceDenied(
            "UDARE_DENY_REGISTRATION_UNAVAILABLE"
        ) from exc

    if (
        not isinstance(registration, Mapping)
        or registration.get("job_type") != "udare_reconstruction"
    ):
        raise UDAREAdmissionEvidenceDenied(
            "UDARE_DENY_REGISTRATION_MISSING"
        )

    try:
        limit, scope = _concurrency_policy(registration)
    except Exception as exc:
        raise UDAREAdmissionEvidenceDenied(
            "UDARE_DENY_INVALID_CONCURRENCY_POLICY"
        ) from exc

    if limit is None:
        raise UDAREAdmissionEvidenceDenied(
            "UDARE_DENY_CONCURRENCY_POLICY_UNCONFIGURED"
        )

    if (
        persisted.get("runtime_registration_queue_action") != "claim"
        or persisted.get("runtime_registration_policy_reason")
        != "concurrency_capacity_available"
        or persisted.get("runtime_registration_job_type")
        != "udare_reconstruction"
        or persisted.get("runtime_registration_concurrency_limit")
        != limit
        or isinstance(
            persisted.get("runtime_registration_active_count"), bool
        )
        or not isinstance(
            persisted.get("runtime_registration_active_count"), int
        )
        or not (
            0 <= persisted["runtime_registration_active_count"] < limit
        )
        or persisted.get("runtime_registration_existing_job_id")
        is not None
    ):
        raise UDAREAdmissionEvidenceDenied(
            "UDARE_DENY_ADMISSION_POLICY_MISMATCH"
        )

    evidence = persisted.get(
        "runtime_registration_policy_evidence"
    )

    if (
        not isinstance(evidence, Mapping)
        or evidence.get("scope") != scope
    ):
        raise UDAREAdmissionEvidenceDenied(
            "UDARE_DENY_ADMISSION_SCOPE_MISMATCH"
        )

    return {
        "job_id": job_id,
        "workspace_id": workspace_id,
        "concurrency_limit": limit,
        "concurrency_scope": scope,
        "persisted_evidence_matched": True,
        "execution_authorized": False,
        "reservation_authenticated": False,
    }
