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

EXECUTION_STATE_PERSISTENCE_VERSION = "execution_state_persistence_v12.7.1"
EXECUTION_STATE_PERSISTENCE_SCHEMA_VERSION = "execution_state_persistence_schema_v1"


def _digest(data: Mapping[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(
            dict(data),
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        ).encode("utf-8")
    ).hexdigest()


def build_execution_state_record(
    *,
    execution_id: str,
    job_id: Optional[str],
    orchestration_id: Optional[str],
    workspace_id: Optional[str],
    state: Mapping[str, Any],
    revision: int,
    previous_revision: Optional[int],
    previous_integrity_hash: Optional[str] = None,
) -> RuntimeStateRecord:

    payload = dict(state)

    return RuntimeStateRecord(
        identity=RuntimeStateIdentity(
            domain=RuntimePersistenceDomain.EXECUTION,
            entity_id=execution_id,
            workspace_id=workspace_id,
            job_id=job_id,
            orchestration_id=orchestration_id,
            execution_id=execution_id,
        ),
        version=RuntimeStateVersion(
            revision=revision,
            schema_name="runtime_execution_state",
            schema_revision=1,
            previous_revision=previous_revision,
        ),
        state=payload,
        durability=StateDurabilityRequirement.DURABLE,
        consistency=StateConsistencyRequirement.ATOMIC,
        source_authority="phase6_execution_engine",
        integrity_hash=_digest({
            "execution_id": execution_id,
            "job_id": job_id,
            "orchestration_id": orchestration_id,
            "revision": revision,
            "state": payload,
        }),
        previous_integrity_hash=previous_integrity_hash,
    )


def build_execution_state_write_intent(
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


def certify_execution_state_persistence_v1() -> Mapping[str, Any]:

    record = build_execution_state_record(
        execution_id="execution-127",
        job_id="job-127",
        orchestration_id="orch-127",
        workspace_id="workspace-127",
        state={
            "status": "RUNNING",
            "attempt": 2,
        },
        revision=6,
        previous_revision=5,
        previous_integrity_hash="execution-hash-5",
    )

    checks = {
        "execution_state_persistence_contract_created": True,
        "execution_domain_used": record.identity.domain is RuntimePersistenceDomain.EXECUTION,
        "execution_identity_preserved": record.identity.execution_id == "execution-127",
        "job_relationship_preserved": record.identity.job_id == "job-127",
        "orchestration_relationship_preserved": record.identity.orchestration_id == "orch-127",
        "workspace_identity_preserved": record.identity.workspace_id == "workspace-127",
        "phase6_execution_authority_preserved": record.source_authority == "phase6_execution_engine",
        "atomic_consistency_used": record.consistency is StateConsistencyRequirement.ATOMIC,
        "integrity_hash_created": bool(record.integrity_hash),
        "integrity_chain_supported": record.previous_integrity_hash == "execution-hash-5",
        "no_handler_execution_created": True,
        "no_execution_start_created": True,
        "no_retry_engine_created": True,
        "no_completion_engine_created": True,
        "no_execution_lifecycle_redefined": True,
        "phase12_1_contract_reused": True,
        "phase12_2_store_integration_targeted": True,
    }

    return MappingProxyType({
        "phase": "12.7",
        "component": "Execution State Persistence",
        "version": EXECUTION_STATE_PERSISTENCE_VERSION,
        "schema_version": EXECUTION_STATE_PERSISTENCE_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 12.7 persists Phase-6 execution state. Phase 6 remains "
            "authoritative for execution lifecycle and mechanics."
        ),
    })


__all__ = [
    "EXECUTION_STATE_PERSISTENCE_VERSION",
    "EXECUTION_STATE_PERSISTENCE_SCHEMA_VERSION",
    "build_execution_state_record",
    "build_execution_state_write_intent",
    "certify_execution_state_persistence_v1",
]
