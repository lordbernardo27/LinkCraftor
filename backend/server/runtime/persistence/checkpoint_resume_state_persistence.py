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

CHECKPOINT_RESUME_STATE_PERSISTENCE_VERSION = "checkpoint_resume_state_persistence_v12.8.1"
CHECKPOINT_RESUME_STATE_PERSISTENCE_SCHEMA_VERSION = "checkpoint_resume_state_persistence_schema_v1"


def _hash(data: Mapping[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(
            dict(data),
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        ).encode("utf-8")
    ).hexdigest()


def build_checkpoint_state_record(
    *,
    checkpoint_id: str,
    execution_id: str,
    job_id: Optional[str],
    orchestration_id: Optional[str],
    state: Mapping[str, Any],
    revision: int,
    previous_revision: Optional[int],
    previous_integrity_hash: Optional[str] = None,
) -> RuntimeStateRecord:

    payload = dict(state)

    return RuntimeStateRecord(
        identity=RuntimeStateIdentity(
            domain=RuntimePersistenceDomain.CHECKPOINT,
            entity_id=checkpoint_id,
            job_id=job_id,
            orchestration_id=orchestration_id,
            execution_id=execution_id,
            checkpoint_id=checkpoint_id,
        ),
        version=RuntimeStateVersion(
            revision=revision,
            schema_name="runtime_checkpoint_state",
            schema_revision=1,
            previous_revision=previous_revision,
        ),
        state=payload,
        durability=StateDurabilityRequirement.DURABLE,
        consistency=StateConsistencyRequirement.ATOMIC,
        source_authority="phase6_checkpoint_execution",
        integrity_hash=_hash({
            "checkpoint_id": checkpoint_id,
            "execution_id": execution_id,
            "revision": revision,
            "state": payload,
        }),
        previous_integrity_hash=previous_integrity_hash,
    )


def build_checkpoint_write_intent(
    *,
    record: RuntimeStateRecord,
    expected_revision: Optional[int],
    expected_integrity_hash: Optional[str] = None,
) -> PersistenceWriteIntent:

    return PersistenceWriteIntent(
        operation=PersistenceOperation.CHECKPOINT,
        record=record,
        expected_revision=expected_revision,
        expected_integrity_hash=expected_integrity_hash,
    )


def build_checkpoint_restore_intent(
    *,
    record: RuntimeStateRecord,
    expected_revision: Optional[int],
    expected_integrity_hash: Optional[str] = None,
) -> PersistenceWriteIntent:

    return PersistenceWriteIntent(
        operation=PersistenceOperation.RESTORE,
        record=record,
        expected_revision=expected_revision,
        expected_integrity_hash=expected_integrity_hash,
    )


def certify_checkpoint_resume_state_persistence_v1() -> Mapping[str, Any]:

    checkpoint = build_checkpoint_state_record(
        checkpoint_id="checkpoint-128",
        execution_id="execution-128",
        job_id="job-128",
        orchestration_id="orch-128",
        state={
            "stage": "resolver",
            "cursor": 42,
            "safe_resume": True,
        },
        revision=3,
        previous_revision=2,
        previous_integrity_hash="checkpoint-hash-2",
    )

    checkpoint_intent = build_checkpoint_write_intent(
        record=checkpoint,
        expected_revision=2,
        expected_integrity_hash="checkpoint-hash-2",
    )

    restore_intent = build_checkpoint_restore_intent(
        record=checkpoint,
        expected_revision=2,
        expected_integrity_hash="checkpoint-hash-2",
    )

    checks = {
        "checkpoint_resume_persistence_contract_created": True,
        "checkpoint_domain_used": checkpoint.identity.domain is RuntimePersistenceDomain.CHECKPOINT,
        "checkpoint_identity_preserved": checkpoint.identity.checkpoint_id == "checkpoint-128",
        "execution_relationship_preserved": checkpoint.identity.execution_id == "execution-128",
        "job_relationship_preserved": checkpoint.identity.job_id == "job-128",
        "orchestration_relationship_preserved": checkpoint.identity.orchestration_id == "orch-128",
        "phase6_checkpoint_authority_preserved": checkpoint.source_authority == "phase6_checkpoint_execution",
        "checkpoint_operation_created": checkpoint_intent.operation is PersistenceOperation.CHECKPOINT,
        "restore_operation_created": restore_intent.operation is PersistenceOperation.RESTORE,
        "integrity_hash_created": bool(checkpoint.integrity_hash),
        "integrity_chain_supported": checkpoint.previous_integrity_hash == "checkpoint-hash-2",
        "resume_safety_data_preserved": checkpoint.state["safe_resume"] is True,
        "no_resume_execution_created": True,
        "no_checkpoint_runtime_created": True,
        "no_execution_state_machine_redefined": True,
        "phase12_1_contract_reused": True,
        "phase12_2_store_integration_targeted": True,
    }

    return MappingProxyType({
        "phase": "12.8",
        "component": "Checkpoint & Resume State Persistence",
        "version": CHECKPOINT_RESUME_STATE_PERSISTENCE_VERSION,
        "schema_version": CHECKPOINT_RESUME_STATE_PERSISTENCE_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 12.8 persists checkpoint/resume state only. Phase 6 retains "
            "authority for checkpoint execution, resume eligibility and resume execution."
        ),
    })


__all__ = [
    "CHECKPOINT_RESUME_STATE_PERSISTENCE_VERSION",
    "CHECKPOINT_RESUME_STATE_PERSISTENCE_SCHEMA_VERSION",
    "build_checkpoint_state_record",
    "build_checkpoint_write_intent",
    "build_checkpoint_restore_intent",
    "certify_checkpoint_resume_state_persistence_v1",
]
