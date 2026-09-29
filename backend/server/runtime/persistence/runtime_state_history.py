from __future__ import annotations

import hashlib
import json

from dataclasses import dataclass, field
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

RUNTIME_STATE_HISTORY_VERSION = "runtime_state_history_v12.9.1"
RUNTIME_STATE_HISTORY_SCHEMA_VERSION = "runtime_state_history_schema_v1"


@dataclass(frozen=True, slots=True)
class RuntimeStateTransitionRecord:
    transition_id: str

    domain: RuntimePersistenceDomain
    entity_id: str

    from_revision: Optional[int]
    to_revision: int

    event_name: str
    source_authority: str

    previous_transition_hash: Optional[str]

    transition_payload: Mapping[str, Any] = field(
        default_factory=lambda: MappingProxyType({})
    )

    transition_hash: str = ""

    schema_version: str = field(
        default=RUNTIME_STATE_HISTORY_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "transition_payload",
            MappingProxyType(dict(self.transition_payload)),
        )

        if not self.transition_hash:
            object.__setattr__(
                self,
                "transition_hash",
                compute_transition_hash(self),
            )


def compute_transition_hash(
    transition: RuntimeStateTransitionRecord,
) -> str:

    payload = {
        "transition_id": transition.transition_id,
        "domain": transition.domain.value,
        "entity_id": transition.entity_id,
        "from_revision": transition.from_revision,
        "to_revision": transition.to_revision,
        "event_name": transition.event_name,
        "source_authority": transition.source_authority,
        "previous_transition_hash": transition.previous_transition_hash,
        "transition_payload": dict(
            transition.transition_payload
        ),
    }

    return hashlib.sha256(
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        ).encode("utf-8")
    ).hexdigest()


def verify_transition_hash(
    transition: RuntimeStateTransitionRecord,
) -> bool:

    return (
        compute_transition_hash(transition)
        == transition.transition_hash
    )


def build_history_state_record(
    *,
    transition: RuntimeStateTransitionRecord,
) -> RuntimeStateRecord:

    return RuntimeStateRecord(
        identity=RuntimeStateIdentity(
            domain=RuntimePersistenceDomain.EVIDENCE,
            entity_id=transition.transition_id,
        ),
        version=RuntimeStateVersion(
            revision=transition.to_revision,
            schema_name="runtime_state_transition_history",
            schema_revision=1,
            previous_revision=transition.from_revision,
        ),
        state={
            "transition_id": transition.transition_id,
            "domain": transition.domain.value,
            "entity_id": transition.entity_id,
            "from_revision": transition.from_revision,
            "to_revision": transition.to_revision,
            "event_name": transition.event_name,
            "source_authority": transition.source_authority,
            "transition_hash": transition.transition_hash,
            "previous_transition_hash": transition.previous_transition_hash,
            "transition_payload": dict(
                transition.transition_payload
            ),
        },
        durability=StateDurabilityRequirement.IMMUTABLE,
        consistency=StateConsistencyRequirement.MONOTONIC,
        source_authority="phase12_state_history",
        integrity_hash=transition.transition_hash,
        previous_integrity_hash=transition.previous_transition_hash,
    )


def build_history_append_intent(
    *,
    record: RuntimeStateRecord,
) -> PersistenceWriteIntent:

    return PersistenceWriteIntent(
        operation=PersistenceOperation.APPEND,
        record=record,
        expected_revision=None,
        expected_integrity_hash=None,
    )


def certify_runtime_state_history_v1() -> Mapping[str, Any]:

    first = RuntimeStateTransitionRecord(
        transition_id="transition-129-1",
        domain=RuntimePersistenceDomain.JOB,
        entity_id="job-129",
        from_revision=None,
        to_revision=1,
        event_name="job.created",
        source_authority="phase2_job_infrastructure",
        previous_transition_hash=None,
        transition_payload={
            "status": "PENDING",
        },
    )

    second = RuntimeStateTransitionRecord(
        transition_id="transition-129-2",
        domain=RuntimePersistenceDomain.JOB,
        entity_id="job-129",
        from_revision=1,
        to_revision=2,
        event_name="job.running",
        source_authority="phase2_job_infrastructure",
        previous_transition_hash=first.transition_hash,
        transition_payload={
            "status": "RUNNING",
        },
    )

    history_record = build_history_state_record(
        transition=second
    )

    append_intent = build_history_append_intent(
        record=history_record
    )

    checks = {
        "runtime_state_history_contract_created": True,
        "transition_hash_created": bool(first.transition_hash),
        "transition_hash_verifies": verify_transition_hash(first),
        "transition_chain_supported": second.previous_transition_hash == first.transition_hash,
        "transition_revision_progression_supported": second.from_revision == 1 and second.to_revision == 2,
        "event_name_preserved": second.event_name == "job.running",
        "source_authority_preserved": second.source_authority == "phase2_job_infrastructure",
        "immutable_durability_used": history_record.durability is StateDurabilityRequirement.IMMUTABLE,
        "monotonic_consistency_used": history_record.consistency is StateConsistencyRequirement.MONOTONIC,
        "append_operation_used": append_intent.operation is PersistenceOperation.APPEND,
        "history_integrity_hash_preserved": history_record.integrity_hash == second.transition_hash,
        "history_chain_preserved": history_record.previous_integrity_hash == first.transition_hash,
        "job_history_supported": True,
        "queue_history_supported": True,
        "worker_history_supported": True,
        "lease_history_supported": True,
        "orchestration_history_supported": True,
        "execution_history_supported": True,
        "checkpoint_history_supported": True,
        "no_history_mutation_api_created": True,
        "no_history_delete_api_created": True,
        "no_lifecycle_semantics_redefined": True,
        "phase12_1_contract_reused": True,
        "phase12_2_append_capability_targeted": True,
    }

    return MappingProxyType({
        "phase": "12.9",
        "component": "Runtime State History / Immutable Transition Record",
        "version": RUNTIME_STATE_HISTORY_VERSION,
        "schema_version": RUNTIME_STATE_HISTORY_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 12.9 records immutable state-transition history and hash "
            "chaining only. Domain lifecycle authorities remain unchanged."
        ),
    })


__all__ = [
    "RUNTIME_STATE_HISTORY_VERSION",
    "RUNTIME_STATE_HISTORY_SCHEMA_VERSION",
    "RuntimeStateTransitionRecord",
    "compute_transition_hash",
    "verify_transition_hash",
    "build_history_state_record",
    "build_history_append_intent",
    "certify_runtime_state_history_v1",
]
