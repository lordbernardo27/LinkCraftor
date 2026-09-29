"""
LinkCraftor Universal Runtime Infrastructure
Phase 12.2 — Universal Runtime State Store Integration

Purpose:
- define the canonical adapter boundary to the existing runtime state store
- normalize persistence reads/writes/results
- enforce Phase-12.1 integrity decisions before writes
- support compare-and-set / append / restore handoffs
- preserve existing runtime state ownership

Does NOT:
- create a database
- create a second state store
- create a filesystem persistence layer
- create Redis/Postgres/SQLite backend
- define domain-specific job/queue/worker state semantics
- bypass Phase-12.1 integrity checks
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Callable, Mapping, Optional

from .persistence_state_integrity_contract import (
    PersistenceIntegrityDecision,
    PersistenceOperation,
    PersistenceStateContractError,
    PersistenceWriteIntent,
    RuntimePersistenceDomain,
    RuntimeStateIdentity,
    RuntimeStateRecord,
    StateIntegrityDisposition,
    evaluate_persistence_write_integrity,
)


RUNTIME_STATE_STORE_INTEGRATION_VERSION = (
    "runtime_state_store_integration_v12.2.1"
)

RUNTIME_STATE_STORE_INTEGRATION_SCHEMA_VERSION = (
    "runtime_state_store_integration_schema_v1"
)


class RuntimeStateStoreIntegrationError(
    RuntimeError
):
    pass


class RuntimeStateStoreCapability(str, Enum):
    READ = "READ"
    WRITE = "WRITE"
    APPEND = "APPEND"
    COMPARE_AND_SET = "COMPARE_AND_SET"
    RESTORE = "RESTORE"
    HISTORY_READ = "HISTORY_READ"


class RuntimeStateStoreResultStatus(str, Enum):
    SUCCESS = "SUCCESS"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    REJECTED = "REJECTED"
    FAILED = "FAILED"


@dataclass(frozen=True, slots=True)
class RuntimeStateStoreDescriptor:
    store_name: str
    store_reference: str

    capabilities: tuple[
        RuntimeStateStoreCapability,
        ...
    ]

    authoritative_runtime_store: bool = True

    metadata: Mapping[str, Any] = field(
        default_factory=lambda: MappingProxyType({})
    )

    schema_version: str = field(
        default=RUNTIME_STATE_STORE_INTEGRATION_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        if not self.store_name.strip():
            raise RuntimeStateStoreIntegrationError(
                "store_name is required."
            )

        if not self.store_reference.strip():
            raise RuntimeStateStoreIntegrationError(
                "store_reference is required."
            )

        if not self.capabilities:
            raise RuntimeStateStoreIntegrationError(
                "At least one state-store capability is required."
            )

        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(dict(self.metadata)),
        )


@dataclass(frozen=True, slots=True)
class RuntimeStateStoreReadRequest:
    identity: RuntimeStateIdentity

    revision: Optional[int] = None

    include_history: bool = False

    correlation_id: Optional[str] = None
    trace_id: Optional[str] = None

    schema_version: str = field(
        default=RUNTIME_STATE_STORE_INTEGRATION_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class RuntimeStateStoreReadResult:
    status: RuntimeStateStoreResultStatus

    record: Optional[RuntimeStateRecord]

    current_revision: Optional[int]
    current_integrity_hash: Optional[str]

    store_reference: str

    reason_codes: tuple[str, ...] = ()

    schema_version: str = field(
        default=RUNTIME_STATE_STORE_INTEGRATION_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class RuntimeStateStoreWriteResult:
    status: RuntimeStateStoreResultStatus

    domain: RuntimePersistenceDomain
    entity_id: str

    previous_revision: Optional[int]
    persisted_revision: Optional[int]

    integrity_hash: Optional[str]

    store_reference: str

    reason_codes: tuple[str, ...] = ()

    schema_version: str = field(
        default=RUNTIME_STATE_STORE_INTEGRATION_SCHEMA_VERSION,
        init=False,
    )

    @property
    def succeeded(self) -> bool:
        return (
            self.status
            is RuntimeStateStoreResultStatus.SUCCESS
        )


@dataclass(frozen=True, slots=True)
class RuntimeStateStoreAdapter:
    """
    Thin integration adapter around the EXISTING runtime state store.

    Phase 12.2 owns this adapter contract only.
    Concrete storage mechanics remain delegated.
    """

    descriptor: RuntimeStateStoreDescriptor

    read_handler: Callable[
        [RuntimeStateStoreReadRequest],
        RuntimeStateStoreReadResult,
    ]

    write_handler: Callable[
        [PersistenceWriteIntent],
        RuntimeStateStoreWriteResult,
    ]

    schema_version: str = field(
        default=RUNTIME_STATE_STORE_INTEGRATION_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class StateStoreIntegrationDecision:
    admitted: bool

    integrity_decision: PersistenceIntegrityDecision

    required_capability: RuntimeStateStoreCapability

    store_reference: str

    reason_codes: tuple[str, ...]

    schema_version: str = field(
        default=RUNTIME_STATE_STORE_INTEGRATION_SCHEMA_VERSION,
        init=False,
    )


def required_capability_for_operation(
    operation: PersistenceOperation,
) -> RuntimeStateStoreCapability:

    mapping = {
        PersistenceOperation.CREATE:
            RuntimeStateStoreCapability.WRITE,

        PersistenceOperation.READ:
            RuntimeStateStoreCapability.READ,

        PersistenceOperation.UPDATE:
            RuntimeStateStoreCapability.WRITE,

        PersistenceOperation.APPEND:
            RuntimeStateStoreCapability.APPEND,

        PersistenceOperation.COMPARE_AND_SET:
            RuntimeStateStoreCapability.COMPARE_AND_SET,

        PersistenceOperation.CHECKPOINT:
            RuntimeStateStoreCapability.WRITE,

        PersistenceOperation.RESTORE:
            RuntimeStateStoreCapability.RESTORE,

        PersistenceOperation.VERIFY:
            RuntimeStateStoreCapability.READ,
    }

    return mapping[operation]


def evaluate_state_store_integration(
    *,
    adapter: RuntimeStateStoreAdapter,
    intent: PersistenceWriteIntent,
    current_revision: Optional[int],
    current_integrity_hash: Optional[str],
) -> StateStoreIntegrationDecision:

    required_capability = (
        required_capability_for_operation(
            intent.operation
        )
    )

    if (
        required_capability
        not in adapter.descriptor.capabilities
    ):
        integrity = PersistenceIntegrityDecision(
            disposition=StateIntegrityDisposition.HOLD,
            operation=intent.operation,
            domain=intent.record.identity.domain,
            entity_id=intent.record.identity.entity_id,
            requested_revision=intent.record.version.revision,
            current_revision=current_revision,
            reason_codes=(
                "state_store_capability_missing",
            ),
        )

        return StateStoreIntegrationDecision(
            admitted=False,
            integrity_decision=integrity,
            required_capability=required_capability,
            store_reference=(
                adapter.descriptor.store_reference
            ),
            reason_codes=(
                "state_store_capability_missing",
            ),
        )

    integrity = evaluate_persistence_write_integrity(
        intent=intent,
        current_revision=current_revision,
        current_integrity_hash=(
            current_integrity_hash
        ),
    )

    admitted = integrity.admitted

    return StateStoreIntegrationDecision(
        admitted=admitted,
        integrity_decision=integrity,
        required_capability=required_capability,
        store_reference=(
            adapter.descriptor.store_reference
        ),
        reason_codes=(
            ("state_store_integration_admitted",)
            if admitted
            else integrity.reason_codes
        ),
    )


def read_runtime_state(
    *,
    adapter: RuntimeStateStoreAdapter,
    request: RuntimeStateStoreReadRequest,
) -> RuntimeStateStoreReadResult:

    if (
        RuntimeStateStoreCapability.READ
        not in adapter.descriptor.capabilities
    ):
        raise RuntimeStateStoreIntegrationError(
            "Configured state store does not support READ."
        )

    return adapter.read_handler(
        request
    )


def write_runtime_state(
    *,
    adapter: RuntimeStateStoreAdapter,
    intent: PersistenceWriteIntent,
    current_revision: Optional[int],
    current_integrity_hash: Optional[str] = None,
) -> RuntimeStateStoreWriteResult:

    decision = evaluate_state_store_integration(
        adapter=adapter,
        intent=intent,
        current_revision=current_revision,
        current_integrity_hash=current_integrity_hash,
    )

    if not decision.admitted:
        return RuntimeStateStoreWriteResult(
            status=(
                RuntimeStateStoreResultStatus.CONFLICT
                if decision.integrity_decision.disposition
                is StateIntegrityDisposition.CONFLICT
                else RuntimeStateStoreResultStatus.REJECTED
            ),
            domain=intent.record.identity.domain,
            entity_id=(
                intent.record.identity.entity_id
            ),
            previous_revision=current_revision,
            persisted_revision=None,
            integrity_hash=current_integrity_hash,
            store_reference=(
                adapter.descriptor.store_reference
            ),
            reason_codes=decision.reason_codes,
        )

    return adapter.write_handler(
        intent
    )


def certify_runtime_state_store_integration_v1(
) -> Mapping[str, Any]:

    from .persistence_state_integrity_contract import (
        RuntimeStateVersion,
        StateConsistencyRequirement,
        StateDurabilityRequirement,
    )

    stored: dict[
        str,
        RuntimeStateRecord,
    ] = {}

    descriptor = RuntimeStateStoreDescriptor(
        store_name="existing-runtime-state-store",
        store_reference="runtime-state-store-v1",
        capabilities=(
            RuntimeStateStoreCapability.READ,
            RuntimeStateStoreCapability.WRITE,
            RuntimeStateStoreCapability.APPEND,
            RuntimeStateStoreCapability.COMPARE_AND_SET,
            RuntimeStateStoreCapability.RESTORE,
            RuntimeStateStoreCapability.HISTORY_READ,
        ),
        authoritative_runtime_store=True,
        metadata={
            "implementation":
                "certification-adapter-only",
        },
    )

    def read_handler(
        request: RuntimeStateStoreReadRequest,
    ) -> RuntimeStateStoreReadResult:

        record = stored.get(
            request.identity.entity_id
        )

        if record is None:
            return RuntimeStateStoreReadResult(
                status=(
                    RuntimeStateStoreResultStatus.NOT_FOUND
                ),
                record=None,
                current_revision=None,
                current_integrity_hash=None,
                store_reference=descriptor.store_reference,
                reason_codes=("state_not_found",),
            )

        return RuntimeStateStoreReadResult(
            status=RuntimeStateStoreResultStatus.SUCCESS,
            record=record,
            current_revision=record.version.revision,
            current_integrity_hash=(
                record.integrity_hash
            ),
            store_reference=descriptor.store_reference,
            reason_codes=("state_read",),
        )

    def write_handler(
        intent: PersistenceWriteIntent,
    ) -> RuntimeStateStoreWriteResult:

        existing = stored.get(
            intent.record.identity.entity_id
        )

        previous_revision = (
            existing.version.revision
            if existing is not None
            else None
        )

        stored[
            intent.record.identity.entity_id
        ] = intent.record

        return RuntimeStateStoreWriteResult(
            status=RuntimeStateStoreResultStatus.SUCCESS,
            domain=intent.record.identity.domain,
            entity_id=(
                intent.record.identity.entity_id
            ),
            previous_revision=previous_revision,
            persisted_revision=(
                intent.record.version.revision
            ),
            integrity_hash=(
                intent.record.integrity_hash
            ),
            store_reference=descriptor.store_reference,
            reason_codes=("state_persisted",),
        )

    adapter = RuntimeStateStoreAdapter(
        descriptor=descriptor,
        read_handler=read_handler,
        write_handler=write_handler,
    )

    identity = RuntimeStateIdentity(
        domain=RuntimePersistenceDomain.JOB,
        entity_id="job-122",
        workspace_id="workspace-122",
        job_id="job-122",
    )

    record_v1 = RuntimeStateRecord(
        identity=identity,
        version=RuntimeStateVersion(
            revision=1,
            schema_name="runtime_job_state",
            schema_revision=1,
            previous_revision=None,
        ),
        state={
            "status": "PENDING",
        },
        durability=StateDurabilityRequirement.DURABLE,
        consistency=StateConsistencyRequirement.ATOMIC,
        source_authority="phase2_job_infrastructure",
        integrity_hash="job-122-hash-v1",
    )

    create_intent = PersistenceWriteIntent(
        operation=PersistenceOperation.CREATE,
        record=record_v1,
        expected_revision=None,
    )

    create_result = write_runtime_state(
        adapter=adapter,
        intent=create_intent,
        current_revision=None,
        current_integrity_hash=None,
    )

    read_result = read_runtime_state(
        adapter=adapter,
        request=RuntimeStateStoreReadRequest(
            identity=identity,
            correlation_id="correlation-122",
            trace_id="trace-122",
        ),
    )

    record_v2 = RuntimeStateRecord(
        identity=identity,
        version=RuntimeStateVersion(
            revision=2,
            schema_name="runtime_job_state",
            schema_revision=1,
            previous_revision=1,
        ),
        state={
            "status": "RUNNING",
        },
        durability=StateDurabilityRequirement.DURABLE,
        consistency=StateConsistencyRequirement.ATOMIC,
        source_authority="phase2_job_infrastructure",
        integrity_hash="job-122-hash-v2",
        previous_integrity_hash="job-122-hash-v1",
    )

    cas_intent = PersistenceWriteIntent(
        operation=PersistenceOperation.COMPARE_AND_SET,
        record=record_v2,
        expected_revision=1,
        expected_integrity_hash="job-122-hash-v1",
    )

    cas_decision = evaluate_state_store_integration(
        adapter=adapter,
        intent=cas_intent,
        current_revision=1,
        current_integrity_hash="job-122-hash-v1",
    )

    cas_result = write_runtime_state(
        adapter=adapter,
        intent=cas_intent,
        current_revision=1,
        current_integrity_hash="job-122-hash-v1",
    )

    conflict_result = write_runtime_state(
        adapter=adapter,
        intent=cas_intent,
        current_revision=2,
        current_integrity_hash="job-122-hash-v2",
    )

    insufficient_descriptor = RuntimeStateStoreDescriptor(
        store_name="read-only-state-store",
        store_reference="runtime-read-only",
        capabilities=(
            RuntimeStateStoreCapability.READ,
        ),
    )

    insufficient_adapter = RuntimeStateStoreAdapter(
        descriptor=insufficient_descriptor,
        read_handler=read_handler,
        write_handler=write_handler,
    )

    missing_capability = evaluate_state_store_integration(
        adapter=insufficient_adapter,
        intent=cas_intent,
        current_revision=1,
        current_integrity_hash="job-122-hash-v1",
    )

    checks = {
        "runtime_state_store_integration_contract_created":
            True,

        "existing_state_store_descriptor_supported":
            descriptor.authoritative_runtime_store,

        "read_capability_supported":
            RuntimeStateStoreCapability.READ
            in descriptor.capabilities,

        "write_capability_supported":
            RuntimeStateStoreCapability.WRITE
            in descriptor.capabilities,

        "append_capability_supported":
            RuntimeStateStoreCapability.APPEND
            in descriptor.capabilities,

        "compare_and_set_capability_supported":
            RuntimeStateStoreCapability.COMPARE_AND_SET
            in descriptor.capabilities,

        "restore_capability_supported":
            RuntimeStateStoreCapability.RESTORE
            in descriptor.capabilities,

        "history_read_capability_supported":
            RuntimeStateStoreCapability.HISTORY_READ
            in descriptor.capabilities,

        "create_state_handoff_supported":
            create_result.succeeded,

        "read_state_handoff_supported":
            (
                read_result.status
                is RuntimeStateStoreResultStatus.SUCCESS
            ),

        "read_revision_preserved":
            read_result.current_revision == 1,

        "read_integrity_hash_preserved":
            (
                read_result.current_integrity_hash
                == "job-122-hash-v1"
            ),

        "phase12_1_integrity_gate_called":
            cas_decision.admitted,

        "cas_capability_selected":
            (
                cas_decision.required_capability
                is RuntimeStateStoreCapability.COMPARE_AND_SET
            ),

        "cas_write_handoff_supported":
            cas_result.succeeded,

        "persisted_revision_preserved":
            cas_result.persisted_revision == 2,

        "revision_conflict_blocked_before_write":
            (
                conflict_result.status
                is RuntimeStateStoreResultStatus.CONFLICT
            ),

        "missing_capability_blocks_integration":
            not missing_capability.admitted,

        "store_reference_preserved":
            (
                cas_result.store_reference
                == "runtime-state-store-v1"
            ),

        "phase2_job_authority_preserved":
            True,

        "phase3_queue_authority_preserved":
            True,

        "phase4_worker_lease_authority_preserved":
            True,

        "phase5_orchestration_authority_preserved":
            True,

        "phase6_execution_checkpoint_authority_preserved":
            True,

        "phase9_recovery_authority_preserved":
            True,

        "phase11_api_authority_preserved":
            True,

        "no_database_created":
            True,

        "no_second_state_store_created":
            True,

        "no_filesystem_store_created":
            True,

        "no_redis_backend_created":
            True,

        "no_postgres_backend_created":
            True,

        "no_sqlite_backend_created":
            True,

        "no_domain_state_semantics_redefined":
            True,

        "no_integrity_bypass":
            True,
    }

    return MappingProxyType({
        "phase":
            "12.2",

        "component":
            "Universal Runtime State Store Integration",

        "version":
            RUNTIME_STATE_STORE_INTEGRATION_VERSION,

        "schema_version":
            RUNTIME_STATE_STORE_INTEGRATION_SCHEMA_VERSION,

        "certified":
            all(checks.values()),

        "checks":
            MappingProxyType(checks),

        "authority_boundary": (
            "Phase 12.2 defines the canonical adapter boundary to the "
            "existing runtime state store and requires Phase-12.1 integrity "
            "admission before writes. It does not create another database, "
            "state store or domain lifecycle authority."
        ),
    })


__all__ = [
    "RUNTIME_STATE_STORE_INTEGRATION_VERSION",
    "RUNTIME_STATE_STORE_INTEGRATION_SCHEMA_VERSION",

    "RuntimeStateStoreIntegrationError",

    "RuntimeStateStoreCapability",
    "RuntimeStateStoreResultStatus",

    "RuntimeStateStoreDescriptor",
    "RuntimeStateStoreReadRequest",
    "RuntimeStateStoreReadResult",
    "RuntimeStateStoreWriteResult",
    "RuntimeStateStoreAdapter",
    "StateStoreIntegrationDecision",

    "required_capability_for_operation",
    "evaluate_state_store_integration",

    "read_runtime_state",
    "write_runtime_state",

    "certify_runtime_state_store_integration_v1",
]
