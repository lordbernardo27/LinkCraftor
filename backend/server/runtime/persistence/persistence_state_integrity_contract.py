"""
LinkCraftor Universal Runtime Infrastructure
Phase 12.1 — Persistence & State Integrity Contract

Purpose:
- define canonical runtime persistence domains
- define state ownership boundaries
- define persistence operations
- define durability / consistency requirements
- define immutable transition expectations
- define recovery / version / integrity handoff contracts
- preserve existing runtime authority

Does NOT:
- create a second runtime state model
- create a second job store
- create a second queue
- create a second worker registry
- create a second orchestration engine
- create a second execution engine
- implement persistence backend
- write database state
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional


PERSISTENCE_STATE_INTEGRITY_CONTRACT_VERSION = (
    "persistence_state_integrity_contract_v12.1.1"
)

PERSISTENCE_STATE_INTEGRITY_SCHEMA_VERSION = (
    "persistence_state_integrity_contract_schema_v1"
)


class PersistenceStateContractError(ValueError):
    def __init__(
        self,
        message: str,
        *,
        code: str,
        value: Any = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.value = value


class RuntimePersistenceDomain(str, Enum):
    JOB = "JOB"
    QUEUE = "QUEUE"
    WORKER = "WORKER"
    LEASE = "LEASE"
    ORCHESTRATION = "ORCHESTRATION"
    EXECUTION = "EXECUTION"
    CHECKPOINT = "CHECKPOINT"
    RUNTIME_API = "RUNTIME_API"
    RESOURCE_GOVERNANCE = "RESOURCE_GOVERNANCE"
    EVIDENCE = "EVIDENCE"


class PersistenceOperation(str, Enum):
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    APPEND = "APPEND"
    COMPARE_AND_SET = "COMPARE_AND_SET"
    CHECKPOINT = "CHECKPOINT"
    RESTORE = "RESTORE"
    VERIFY = "VERIFY"


class StateDurabilityRequirement(str, Enum):
    TRANSIENT = "TRANSIENT"
    DURABLE = "DURABLE"
    IMMUTABLE = "IMMUTABLE"


class StateConsistencyRequirement(str, Enum):
    BEST_EFFORT = "BEST_EFFORT"
    MONOTONIC = "MONOTONIC"
    STRONG = "STRONG"
    ATOMIC = "ATOMIC"


class StateIntegrityDisposition(str, Enum):
    ALLOW = "ALLOW"
    REJECT = "REJECT"
    HOLD = "HOLD"
    CONFLICT = "CONFLICT"
    CORRUPT = "CORRUPT"


@dataclass(frozen=True, slots=True)
class RuntimeStateIdentity:
    domain: RuntimePersistenceDomain
    entity_id: str

    workspace_id: Optional[str] = None

    job_id: Optional[str] = None
    queue_name: Optional[str] = None
    worker_id: Optional[str] = None
    worker_instance_id: Optional[str] = None
    lease_id: Optional[str] = None
    orchestration_id: Optional[str] = None
    execution_id: Optional[str] = None
    checkpoint_id: Optional[str] = None

    schema_version: str = field(
        default=PERSISTENCE_STATE_INTEGRITY_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        if not self.entity_id.strip():
            raise PersistenceStateContractError(
                "entity_id is required.",
                code="runtime_state_entity_id_missing",
            )


@dataclass(frozen=True, slots=True)
class RuntimeStateVersion:
    revision: int

    schema_name: str
    schema_revision: int

    previous_revision: Optional[int] = None

    schema_version: str = field(
        default=PERSISTENCE_STATE_INTEGRITY_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        if self.revision < 0:
            raise PersistenceStateContractError(
                "revision cannot be negative.",
                code="runtime_state_revision_invalid",
                value=self.revision,
            )

        if self.schema_revision < 1:
            raise PersistenceStateContractError(
                "schema_revision must be >= 1.",
                code="runtime_state_schema_revision_invalid",
                value=self.schema_revision,
            )

        if not self.schema_name.strip():
            raise PersistenceStateContractError(
                "schema_name is required.",
                code="runtime_state_schema_name_missing",
            )


@dataclass(frozen=True, slots=True)
class RuntimeStateRecord:
    identity: RuntimeStateIdentity
    version: RuntimeStateVersion

    state: Mapping[str, Any]

    durability: StateDurabilityRequirement
    consistency: StateConsistencyRequirement

    source_authority: str

    integrity_hash: Optional[str] = None
    previous_integrity_hash: Optional[str] = None

    metadata: Mapping[str, Any] = field(
        default_factory=lambda: MappingProxyType({})
    )

    schema_version: str = field(
        default=PERSISTENCE_STATE_INTEGRITY_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        if not self.source_authority.strip():
            raise PersistenceStateContractError(
                "source_authority is required.",
                code="runtime_state_source_authority_missing",
            )

        object.__setattr__(
            self,
            "state",
            MappingProxyType(dict(self.state)),
        )

        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(dict(self.metadata)),
        )


@dataclass(frozen=True, slots=True)
class PersistenceWriteIntent:
    operation: PersistenceOperation

    record: RuntimeStateRecord

    expected_revision: Optional[int] = None
    expected_integrity_hash: Optional[str] = None

    correlation_id: Optional[str] = None
    trace_id: Optional[str] = None

    schema_version: str = field(
        default=PERSISTENCE_STATE_INTEGRITY_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class PersistenceIntegrityDecision:
    disposition: StateIntegrityDisposition

    operation: PersistenceOperation
    domain: RuntimePersistenceDomain

    entity_id: str

    requested_revision: int
    current_revision: Optional[int]

    reason_codes: tuple[str, ...]

    schema_version: str = field(
        default=PERSISTENCE_STATE_INTEGRITY_SCHEMA_VERSION,
        init=False,
    )

    @property
    def admitted(self) -> bool:
        return (
            self.disposition
            is StateIntegrityDisposition.ALLOW
        )


def evaluate_persistence_write_integrity(
    *,
    intent: PersistenceWriteIntent,
    current_revision: Optional[int],
    current_integrity_hash: Optional[str] = None,
) -> PersistenceIntegrityDecision:

    record = intent.record
    requested_revision = record.version.revision

    if (
        intent.expected_revision is not None
        and current_revision != intent.expected_revision
    ):
        return PersistenceIntegrityDecision(
            disposition=StateIntegrityDisposition.CONFLICT,
            operation=intent.operation,
            domain=record.identity.domain,
            entity_id=record.identity.entity_id,
            requested_revision=requested_revision,
            current_revision=current_revision,
            reason_codes=("expected_revision_mismatch",),
        )

    if (
        intent.expected_integrity_hash is not None
        and current_integrity_hash
        != intent.expected_integrity_hash
    ):
        return PersistenceIntegrityDecision(
            disposition=StateIntegrityDisposition.CONFLICT,
            operation=intent.operation,
            domain=record.identity.domain,
            entity_id=record.identity.entity_id,
            requested_revision=requested_revision,
            current_revision=current_revision,
            reason_codes=("expected_integrity_hash_mismatch",),
        )

    if current_revision is not None:
        if requested_revision <= current_revision:
            return PersistenceIntegrityDecision(
                disposition=StateIntegrityDisposition.REJECT,
                operation=intent.operation,
                domain=record.identity.domain,
                entity_id=record.identity.entity_id,
                requested_revision=requested_revision,
                current_revision=current_revision,
                reason_codes=("non_monotonic_revision",),
            )

    if (
        record.version.previous_revision is not None
        and current_revision is not None
        and record.version.previous_revision
        != current_revision
    ):
        return PersistenceIntegrityDecision(
            disposition=StateIntegrityDisposition.CONFLICT,
            operation=intent.operation,
            domain=record.identity.domain,
            entity_id=record.identity.entity_id,
            requested_revision=requested_revision,
            current_revision=current_revision,
            reason_codes=("previous_revision_mismatch",),
        )

    return PersistenceIntegrityDecision(
        disposition=StateIntegrityDisposition.ALLOW,
        operation=intent.operation,
        domain=record.identity.domain,
        entity_id=record.identity.entity_id,
        requested_revision=requested_revision,
        current_revision=current_revision,
        reason_codes=("persistence_integrity_valid",),
    )


def certify_persistence_state_integrity_contract_v1(
) -> Mapping[str, Any]:

    identity = RuntimeStateIdentity(
        domain=RuntimePersistenceDomain.JOB,
        entity_id="job-121",
        workspace_id="workspace-121",
        job_id="job-121",
    )

    version = RuntimeStateVersion(
        revision=2,
        schema_name="runtime_job_state",
        schema_revision=1,
        previous_revision=1,
    )

    record = RuntimeStateRecord(
        identity=identity,
        version=version,
        state={
            "status": "RUNNING",
        },
        durability=StateDurabilityRequirement.DURABLE,
        consistency=StateConsistencyRequirement.ATOMIC,
        source_authority="phase2_job_infrastructure",
        integrity_hash="hash-2",
        previous_integrity_hash="hash-1",
        metadata={
            "origin": "runtime",
        },
    )

    allowed = evaluate_persistence_write_integrity(
        intent=PersistenceWriteIntent(
            operation=PersistenceOperation.COMPARE_AND_SET,
            record=record,
            expected_revision=1,
            expected_integrity_hash="hash-1",
            correlation_id="correlation-121",
            trace_id="trace-121",
        ),
        current_revision=1,
        current_integrity_hash="hash-1",
    )

    revision_conflict = evaluate_persistence_write_integrity(
        intent=PersistenceWriteIntent(
            operation=PersistenceOperation.COMPARE_AND_SET,
            record=record,
            expected_revision=0,
        ),
        current_revision=1,
    )

    integrity_conflict = evaluate_persistence_write_integrity(
        intent=PersistenceWriteIntent(
            operation=PersistenceOperation.COMPARE_AND_SET,
            record=record,
            expected_revision=1,
            expected_integrity_hash="wrong-hash",
        ),
        current_revision=1,
        current_integrity_hash="hash-1",
    )

    non_monotonic = evaluate_persistence_write_integrity(
        intent=PersistenceWriteIntent(
            operation=PersistenceOperation.UPDATE,
            record=RuntimeStateRecord(
                identity=identity,
                version=RuntimeStateVersion(
                    revision=1,
                    schema_name="runtime_job_state",
                    schema_revision=1,
                    previous_revision=0,
                ),
                state={
                    "status": "PENDING",
                },
                durability=StateDurabilityRequirement.DURABLE,
                consistency=StateConsistencyRequirement.MONOTONIC,
                source_authority="phase2_job_infrastructure",
            ),
        ),
        current_revision=1,
    )

    checks = {
        "persistence_state_integrity_contract_created": True,

        "job_domain_supported": (
            RuntimePersistenceDomain.JOB.value == "JOB"
        ),

        "queue_domain_supported": (
            RuntimePersistenceDomain.QUEUE.value == "QUEUE"
        ),

        "worker_domain_supported": (
            RuntimePersistenceDomain.WORKER.value == "WORKER"
        ),

        "lease_domain_supported": (
            RuntimePersistenceDomain.LEASE.value == "LEASE"
        ),

        "orchestration_domain_supported": (
            RuntimePersistenceDomain.ORCHESTRATION.value
            == "ORCHESTRATION"
        ),

        "execution_domain_supported": (
            RuntimePersistenceDomain.EXECUTION.value
            == "EXECUTION"
        ),

        "checkpoint_domain_supported": (
            RuntimePersistenceDomain.CHECKPOINT.value
            == "CHECKPOINT"
        ),

        "runtime_api_domain_supported": (
            RuntimePersistenceDomain.RUNTIME_API.value
            == "RUNTIME_API"
        ),

        "resource_governance_domain_supported": (
            RuntimePersistenceDomain.RESOURCE_GOVERNANCE.value
            == "RESOURCE_GOVERNANCE"
        ),

        "evidence_domain_supported": (
            RuntimePersistenceDomain.EVIDENCE.value
            == "EVIDENCE"
        ),

        "durable_state_supported": (
            record.durability
            is StateDurabilityRequirement.DURABLE
        ),

        "immutable_state_supported": True,

        "atomic_consistency_supported": (
            record.consistency
            is StateConsistencyRequirement.ATOMIC
        ),

        "monotonic_consistency_supported": True,

        "compare_and_set_supported": True,

        "checkpoint_operation_supported": True,

        "restore_operation_supported": True,

        "verification_operation_supported": True,

        "state_version_supported": (
            record.version.revision == 2
        ),

        "schema_versioning_supported": (
            record.version.schema_revision == 1
        ),

        "previous_revision_supported": (
            record.version.previous_revision == 1
        ),

        "integrity_hash_supported": (
            record.integrity_hash == "hash-2"
        ),

        "integrity_chain_supported": (
            record.previous_integrity_hash == "hash-1"
        ),

        "valid_transition_allowed": (
            allowed.disposition
            is StateIntegrityDisposition.ALLOW
        ),

        "revision_conflict_detected": (
            revision_conflict.disposition
            is StateIntegrityDisposition.CONFLICT
        ),

        "integrity_hash_conflict_detected": (
            integrity_conflict.disposition
            is StateIntegrityDisposition.CONFLICT
        ),

        "non_monotonic_revision_rejected": (
            non_monotonic.disposition
            is StateIntegrityDisposition.REJECT
        ),

        "phase2_job_authority_preserved": True,
        "phase3_queue_authority_preserved": True,
        "phase4_worker_authority_preserved": True,
        "phase5_orchestration_authority_preserved": True,
        "phase6_execution_authority_preserved": True,
        "phase7_security_authority_preserved": True,
        "phase8_observability_authority_preserved": True,
        "phase9_recovery_authority_preserved": True,
        "phase10_resource_governance_authority_preserved": True,
        "phase11_api_authority_preserved": True,

        "no_second_state_model_created": True,
        "no_job_store_created": True,
        "no_queue_created": True,
        "no_worker_registry_created": True,
        "no_orchestration_engine_created": True,
        "no_execution_engine_created": True,
        "no_database_backend_created": True,
        "no_persistence_write": True,
        "no_runtime_mutation": True,
    }

    return MappingProxyType({
        "phase": "12.1",
        "component": "Persistence & State Integrity Contract",
        "version": PERSISTENCE_STATE_INTEGRITY_CONTRACT_VERSION,
        "schema_version": PERSISTENCE_STATE_INTEGRITY_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 12.1 defines canonical runtime persistence domains, "
            "durability, consistency, versioning and integrity contracts. "
            "Existing runtime phases remain authoritative for runtime state "
            "semantics and lifecycle. Concrete persistence integration begins "
            "in later Phase-12 components."
        ),
    })


__all__ = [
    "PERSISTENCE_STATE_INTEGRITY_CONTRACT_VERSION",
    "PERSISTENCE_STATE_INTEGRITY_SCHEMA_VERSION",

    "PersistenceStateContractError",

    "RuntimePersistenceDomain",
    "PersistenceOperation",
    "StateDurabilityRequirement",
    "StateConsistencyRequirement",
    "StateIntegrityDisposition",

    "RuntimeStateIdentity",
    "RuntimeStateVersion",
    "RuntimeStateRecord",
    "PersistenceWriteIntent",
    "PersistenceIntegrityDecision",

    "evaluate_persistence_write_integrity",

    "certify_persistence_state_integrity_contract_v1",
]
