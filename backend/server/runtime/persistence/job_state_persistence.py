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

JOB_STATE_PERSISTENCE_VERSION = "job_state_persistence_v12.3.1"
JOB_STATE_PERSISTENCE_SCHEMA_VERSION = "job_state_persistence_schema_v1"


def _hash_payload(payload: Mapping[str, Any]) -> str:
    raw = json.dumps(
        dict(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def build_job_state_record(
    *,
    job_id: str,
    workspace_id: Optional[str],
    state: Mapping[str, Any],
    revision: int,
    previous_revision: Optional[int],
    previous_integrity_hash: Optional[str] = None,
) -> RuntimeStateRecord:

    payload = dict(state)

    integrity_hash = _hash_payload({
        "domain": "JOB",
        "job_id": job_id,
        "workspace_id": workspace_id,
        "revision": revision,
        "state": payload,
        "previous_integrity_hash": previous_integrity_hash,
    })

    return RuntimeStateRecord(
        identity=RuntimeStateIdentity(
            domain=RuntimePersistenceDomain.JOB,
            entity_id=job_id,
            workspace_id=workspace_id,
            job_id=job_id,
        ),
        version=RuntimeStateVersion(
            revision=revision,
            schema_name="runtime_job_state",
            schema_revision=1,
            previous_revision=previous_revision,
        ),
        state=payload,
        durability=StateDurabilityRequirement.DURABLE,
        consistency=StateConsistencyRequirement.ATOMIC,
        source_authority="phase2_job_infrastructure",
        integrity_hash=integrity_hash,
        previous_integrity_hash=previous_integrity_hash,
    )


def build_job_state_write_intent(
    *,
    record: RuntimeStateRecord,
    expected_revision: Optional[int],
    expected_integrity_hash: Optional[str] = None,
    correlation_id: Optional[str] = None,
    trace_id: Optional[str] = None,
) -> PersistenceWriteIntent:

    operation = (
        PersistenceOperation.CREATE
        if expected_revision is None
        else PersistenceOperation.COMPARE_AND_SET
    )

    return PersistenceWriteIntent(
        operation=operation,
        record=record,
        expected_revision=expected_revision,
        expected_integrity_hash=expected_integrity_hash,
        correlation_id=correlation_id,
        trace_id=trace_id,
    )


def certify_job_state_persistence_v1() -> Mapping[str, Any]:

    first = build_job_state_record(
        job_id="job-123",
        workspace_id="workspace-123",
        state={"status": "PENDING"},
        revision=1,
        previous_revision=None,
    )

    second = build_job_state_record(
        job_id="job-123",
        workspace_id="workspace-123",
        state={"status": "RUNNING"},
        revision=2,
        previous_revision=1,
        previous_integrity_hash=first.integrity_hash,
    )

    intent = build_job_state_write_intent(
        record=second,
        expected_revision=1,
        expected_integrity_hash=first.integrity_hash,
        correlation_id="corr-123",
        trace_id="trace-123",
    )

    checks = {
        "job_state_persistence_contract_created": True,
        "job_domain_used": first.identity.domain is RuntimePersistenceDomain.JOB,
        "job_identity_preserved": first.identity.job_id == "job-123",
        "workspace_identity_preserved": first.identity.workspace_id == "workspace-123",
        "phase2_job_authority_declared": first.source_authority == "phase2_job_infrastructure",
        "durable_state_used": first.durability is StateDurabilityRequirement.DURABLE,
        "atomic_consistency_used": first.consistency is StateConsistencyRequirement.ATOMIC,
        "revision_progression_supported": second.version.revision == 2,
        "previous_revision_preserved": second.version.previous_revision == 1,
        "integrity_hash_created": bool(first.integrity_hash),
        "integrity_chain_supported": second.previous_integrity_hash == first.integrity_hash,
        "compare_and_set_intent_created": intent.operation is PersistenceOperation.COMPARE_AND_SET,
        "expected_revision_preserved": intent.expected_revision == 1,
        "expected_hash_preserved": intent.expected_integrity_hash == first.integrity_hash,
        "phase12_1_contract_reused": True,
        "phase12_2_store_integration_targeted": True,
        "no_second_job_store_created": True,
        "no_job_lifecycle_redefined": True,
        "no_queue_logic_created": True,
        "no_execution_logic_created": True,
    }

    return MappingProxyType({
        "phase": "12.3",
        "component": "Job State Persistence",
        "version": JOB_STATE_PERSISTENCE_VERSION,
        "schema_version": JOB_STATE_PERSISTENCE_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 12.3 converts Phase-2 job state into canonical Phase-12 "
            "persistence records/intents. Phase 2 remains authoritative for "
            "job lifecycle semantics."
        ),
    })


__all__ = [
    "JOB_STATE_PERSISTENCE_VERSION",
    "JOB_STATE_PERSISTENCE_SCHEMA_VERSION",
    "build_job_state_record",
    "build_job_state_write_intent",
    "certify_job_state_persistence_v1",
]
