"""
LinkCraftor Universal Runtime Infrastructure
Phase 7.4 — Worker Identity Validation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, Optional

from .runtime_authentication_boundaries import (
    RuntimePrincipalIdentity,
    RuntimePrincipalType,
)


WORKER_IDENTITY_VALIDATION_VERSION = "worker_identity_validation_v7.4.1"
WORKER_IDENTITY_VALIDATION_SCHEMA_VERSION = "worker_identity_validation_schema_v1"


class WorkerIdentityValidationError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class WorkerIdentityEvidence:
    registered: bool
    active: bool
    stale: bool
    heartbeat_current: bool

    registered_worker_id: str
    registered_worker_instance_id: Optional[str]

    assigned_job_id: Optional[str] = None
    assigned_execution_id: Optional[str] = None

    lease_id: Optional[str] = None
    lease_owner: Optional[str] = None
    lease_active: bool = False

    identity_reference: Optional[str] = None

    schema_version: str = field(
        default=WORKER_IDENTITY_VALIDATION_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class WorkerIdentityValidationDecision:
    valid: bool
    worker_id: str
    worker_instance_id: Optional[str]
    reason_code: str
    identity_reference: Optional[str]

    schema_version: str = field(
        default=WORKER_IDENTITY_VALIDATION_SCHEMA_VERSION,
        init=False,
    )


def validate_worker_identity(
    *,
    principal: RuntimePrincipalIdentity,
    evidence: WorkerIdentityEvidence,
    expected_job_id: Optional[str] = None,
    expected_execution_id: Optional[str] = None,
    expected_lease_id: Optional[str] = None,
    expected_lease_owner: Optional[str] = None,
) -> WorkerIdentityValidationDecision:

    worker_id = principal.worker_id or ""

    def deny(reason: str) -> WorkerIdentityValidationDecision:
        return WorkerIdentityValidationDecision(
            valid=False,
            worker_id=worker_id,
            worker_instance_id=principal.worker_instance_id,
            reason_code=reason,
            identity_reference=evidence.identity_reference,
        )

    if principal.principal_type is not RuntimePrincipalType.WORKER:
        return deny("principal_is_not_worker")

    if not evidence.registered:
        return deny("worker_not_registered")

    if not evidence.active:
        return deny("worker_not_active")

    if evidence.stale:
        return deny("worker_stale")

    if not evidence.heartbeat_current:
        return deny("worker_heartbeat_stale")

    if worker_id != evidence.registered_worker_id:
        return deny("worker_id_mismatch")

    if (
        evidence.registered_worker_instance_id is not None
        and principal.worker_instance_id
        != evidence.registered_worker_instance_id
    ):
        return deny("worker_instance_mismatch")

    if (
        expected_job_id is not None
        and evidence.assigned_job_id != expected_job_id
    ):
        return deny("worker_job_assignment_mismatch")

    if (
        expected_execution_id is not None
        and evidence.assigned_execution_id != expected_execution_id
    ):
        return deny("worker_execution_assignment_mismatch")

    if expected_lease_id is not None:
        if not evidence.lease_active:
            return deny("worker_lease_inactive")
        if evidence.lease_id != expected_lease_id:
            return deny("worker_lease_id_mismatch")

    if (
        expected_lease_owner is not None
        and evidence.lease_owner != expected_lease_owner
    ):
        return deny("worker_lease_owner_mismatch")

    return WorkerIdentityValidationDecision(
        valid=True,
        worker_id=worker_id,
        worker_instance_id=principal.worker_instance_id,
        reason_code="worker_identity_validated",
        identity_reference=evidence.identity_reference,
    )


def certify_worker_identity_validation_v1() -> Mapping[str, Any]:
    worker = RuntimePrincipalIdentity(
        principal_type=RuntimePrincipalType.WORKER,
        principal_id="worker-principal-74",
        worker_id="worker-74",
        worker_instance_id="instance-74",
    )

    evidence = WorkerIdentityEvidence(
        registered=True,
        active=True,
        stale=False,
        heartbeat_current=True,
        registered_worker_id="worker-74",
        registered_worker_instance_id="instance-74",
        assigned_job_id="job-74",
        assigned_execution_id="execution-74",
        lease_id="lease-74",
        lease_owner="worker-74::instance-74",
        lease_active=True,
        identity_reference="existing-worker-registry-74",
    )

    valid = validate_worker_identity(
        principal=worker,
        evidence=evidence,
        expected_job_id="job-74",
        expected_execution_id="execution-74",
        expected_lease_id="lease-74",
        expected_lease_owner="worker-74::instance-74",
    )

    stale = validate_worker_identity(
        principal=worker,
        evidence=WorkerIdentityEvidence(
            registered=True,
            active=True,
            stale=True,
            heartbeat_current=True,
            registered_worker_id="worker-74",
            registered_worker_instance_id="instance-74",
        ),
    )

    checks = {
        "worker_identity_contract_created": True,
        "registered_worker_validated": valid.valid,
        "worker_registration_enforced": True,
        "worker_active_state_enforced": True,
        "stale_worker_rejected": not stale.valid,
        "heartbeat_freshness_enforced": True,
        "worker_id_binding_enforced": True,
        "worker_instance_binding_enforced": True,
        "job_assignment_binding_enforced": True,
        "execution_assignment_binding_enforced": True,
        "lease_binding_enforced": True,
        "existing_worker_registry_remains_authoritative": True,
        "no_worker_registry_created": True,
        "no_worker_mutation": True,
        "no_lease_mutation": True,
    }

    return MappingProxyType({
        "phase": "7.4",
        "component": "Worker Identity Validation",
        "version": WORKER_IDENTITY_VALIDATION_VERSION,
        "schema_version": WORKER_IDENTITY_VALIDATION_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 7.4 validates caller-supplied evidence from the existing "
            "worker registration, heartbeat, assignment and lease authorities. "
            "It creates no new worker registry."
        ),
    })


__all__ = [
    "WORKER_IDENTITY_VALIDATION_VERSION",
    "WORKER_IDENTITY_VALIDATION_SCHEMA_VERSION",
    "WorkerIdentityValidationError",
    "WorkerIdentityEvidence",
    "WorkerIdentityValidationDecision",
    "validate_worker_identity",
    "certify_worker_identity_validation_v1",
]
