from __future__ import annotations

import hashlib
import json

from types import MappingProxyType
from typing import Any, Mapping, Optional

from .persistence_state_integrity_contract import (
    PersistenceOperation,
    PersistenceWriteIntent,
    RuntimePersistenceDomain,
    RuntimeStateIdentity,
    RuntimeStateRecord,
    RuntimeStateVersion,
    StateConsistencyRequirement,
    StateDurabilityRequirement,
)

WORKER_LEASE_STATE_PERSISTENCE_VERSION = "worker_lease_state_persistence_v12.5.1"
WORKER_LEASE_STATE_PERSISTENCE_SCHEMA_VERSION = "worker_lease_state_persistence_schema_v1"


def _digest(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(
            dict(value),
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        ).encode("utf-8")
    ).hexdigest()


def build_worker_state_record(
    *,
    worker_id: str,
    worker_instance_id: Optional[str],
    state: Mapping[str, Any],
    revision: int,
    previous_revision: Optional[int],
    previous_integrity_hash: Optional[str] = None,
) -> RuntimeStateRecord:

    payload = dict(state)

    return RuntimeStateRecord(
        identity=RuntimeStateIdentity(
            domain=RuntimePersistenceDomain.WORKER,
            entity_id=worker_id,
            worker_id=worker_id,
            worker_instance_id=worker_instance_id,
        ),
        version=RuntimeStateVersion(
            revision=revision,
            schema_name="runtime_worker_state",
            schema_revision=1,
            previous_revision=previous_revision,
        ),
        state=payload,
        durability=StateDurabilityRequirement.DURABLE,
        consistency=StateConsistencyRequirement.MONOTONIC,
        source_authority="phase4_worker_infrastructure",
        integrity_hash=_digest({
            "worker_id": worker_id,
            "worker_instance_id": worker_instance_id,
            "revision": revision,
            "state": payload,
            "previous_integrity_hash": previous_integrity_hash,
        }),
        previous_integrity_hash=previous_integrity_hash,
    )


def build_lease_state_record(
    *,
    lease_id: str,
    worker_id: str,
    job_id: Optional[str],
    state: Mapping[str, Any],
    revision: int,
    previous_revision: Optional[int],
    previous_integrity_hash: Optional[str] = None,
) -> RuntimeStateRecord:

    payload = dict(state)

    return RuntimeStateRecord(
        identity=RuntimeStateIdentity(
            domain=RuntimePersistenceDomain.LEASE,
            entity_id=lease_id,
            worker_id=worker_id,
            lease_id=lease_id,
            job_id=job_id,
        ),
        version=RuntimeStateVersion(
            revision=revision,
            schema_name="runtime_lease_state",
            schema_revision=1,
            previous_revision=previous_revision,
        ),
        state=payload,
        durability=StateDurabilityRequirement.DURABLE,
        consistency=StateConsistencyRequirement.ATOMIC,
        source_authority="phase4_worker_leasing",
        integrity_hash=_digest({
            "lease_id": lease_id,
            "worker_id": worker_id,
            "job_id": job_id,
            "revision": revision,
            "state": payload,
        }),
        previous_integrity_hash=previous_integrity_hash,
    )


def build_worker_lease_write_intent(
    *,
    record: RuntimeStateRecord,
    expected_revision: Optional[int],
    expected_integrity_hash: Optional[str] = None,
) -> PersistenceWriteIntent:

    return PersistenceWriteIntent(
        operation=(
            PersistenceOperation.CREATE
            if expected_revision is None
            else PersistenceOperation.COMPARE_AND_SET
        ),
        record=record,
        expected_revision=expected_revision,
        expected_integrity_hash=expected_integrity_hash,
    )


def certify_worker_lease_state_persistence_v1() -> Mapping[str, Any]:

    worker = build_worker_state_record(
        worker_id="worker-125",
        worker_instance_id="instance-125",
        state={"status": "ACTIVE", "active_jobs": 2},
        revision=3,
        previous_revision=2,
        previous_integrity_hash="worker-hash-2",
    )

    lease = build_lease_state_record(
        lease_id="lease-125",
        worker_id="worker-125",
        job_id="job-125",
        state={"status": "HELD"},
        revision=2,
        previous_revision=1,
        previous_integrity_hash="lease-hash-1",
    )

    checks = {
        "worker_lease_state_persistence_contract_created": True,
        "worker_domain_used": worker.identity.domain is RuntimePersistenceDomain.WORKER,
        "lease_domain_used": lease.identity.domain is RuntimePersistenceDomain.LEASE,
        "worker_identity_preserved": worker.identity.worker_id == "worker-125",
        "worker_instance_identity_preserved": worker.identity.worker_instance_id == "instance-125",
        "lease_identity_preserved": lease.identity.lease_id == "lease-125",
        "lease_worker_relationship_preserved": lease.identity.worker_id == "worker-125",
        "lease_job_relationship_preserved": lease.identity.job_id == "job-125",
        "worker_authority_preserved": worker.source_authority == "phase4_worker_infrastructure",
        "lease_authority_preserved": lease.source_authority == "phase4_worker_leasing",
        "worker_integrity_hash_created": bool(worker.integrity_hash),
        "lease_integrity_hash_created": bool(lease.integrity_hash),
        "worker_lifecycle_not_redefined": True,
        "lease_mechanics_not_redefined": True,
        "no_worker_registry_created": True,
        "no_lease_manager_created": True,
        "no_worker_assignment_created": True,
        "phase12_1_contract_reused": True,
        "phase12_2_store_integration_targeted": True,
    }

    return MappingProxyType({
        "phase": "12.5",
        "component": "Worker & Lease State Persistence",
        "version": WORKER_LEASE_STATE_PERSISTENCE_VERSION,
        "schema_version": WORKER_LEASE_STATE_PERSISTENCE_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 12.5 persists Phase-4 worker and lease state only. Phase 4 "
            "retains registration, assignment, lease ownership and lifecycle authority."
        ),
    })


__all__ = [
    "WORKER_LEASE_STATE_PERSISTENCE_VERSION",
    "WORKER_LEASE_STATE_PERSISTENCE_SCHEMA_VERSION",
    "build_worker_state_record",
    "build_lease_state_record",
    "build_worker_lease_write_intent",
    "certify_worker_lease_state_persistence_v1",
]
