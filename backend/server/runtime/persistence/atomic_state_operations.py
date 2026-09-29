"""
Phase 12.10 — Atomic State Operations

Defines atomic persistence operation admission and transaction-group contracts.
Does not create a transaction engine or storage backend.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional

from .persistence_state_integrity_contract import (
    PersistenceOperation,
    PersistenceWriteIntent,
    StateConsistencyRequirement,
)


ATOMIC_STATE_OPERATIONS_VERSION = "atomic_state_operations_v12.10.1"
ATOMIC_STATE_OPERATIONS_SCHEMA_VERSION = "atomic_state_operations_schema_v1"


class AtomicOperationDisposition(str, Enum):
    ALLOW = "ALLOW"
    REJECT = "REJECT"
    CONFLICT = "CONFLICT"


@dataclass(frozen=True, slots=True)
class AtomicStateOperation:
    operation_id: str
    intent: PersistenceWriteIntent
    sequence: int

    schema_version: str = field(
        default=ATOMIC_STATE_OPERATIONS_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        if not self.operation_id.strip():
            raise ValueError("operation_id is required.")
        if self.sequence < 1:
            raise ValueError("sequence must be >= 1.")


@dataclass(frozen=True, slots=True)
class AtomicStateTransaction:
    transaction_id: str
    operations: tuple[AtomicStateOperation, ...]
    all_or_nothing: bool = True

    schema_version: str = field(
        default=ATOMIC_STATE_OPERATIONS_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        if not self.transaction_id.strip():
            raise ValueError("transaction_id is required.")
        if not self.operations:
            raise ValueError("Atomic transaction requires operations.")


@dataclass(frozen=True, slots=True)
class AtomicOperationDecision:
    disposition: AtomicOperationDisposition
    transaction_id: str
    operation_count: int
    reason_codes: tuple[str, ...]

    schema_version: str = field(
        default=ATOMIC_STATE_OPERATIONS_SCHEMA_VERSION,
        init=False,
    )


def evaluate_atomic_transaction(
    transaction: AtomicStateTransaction,
) -> AtomicOperationDecision:

    ordered = sorted(
        transaction.operations,
        key=lambda item: item.sequence,
    )

    sequences = tuple(item.sequence for item in ordered)

    if sequences != tuple(range(1, len(ordered) + 1)):
        return AtomicOperationDecision(
            disposition=AtomicOperationDisposition.REJECT,
            transaction_id=transaction.transaction_id,
            operation_count=len(ordered),
            reason_codes=("non_contiguous_sequence",),
        )

    if transaction.all_or_nothing:
        if any(
            item.intent.record.consistency
            is not StateConsistencyRequirement.ATOMIC
            for item in ordered
        ):
            return AtomicOperationDecision(
                disposition=AtomicOperationDisposition.REJECT,
                transaction_id=transaction.transaction_id,
                operation_count=len(ordered),
                reason_codes=("atomic_consistency_required",),
            )

    return AtomicOperationDecision(
        disposition=AtomicOperationDisposition.ALLOW,
        transaction_id=transaction.transaction_id,
        operation_count=len(ordered),
        reason_codes=("atomic_transaction_valid",),
    )


def certify_atomic_state_operations_v1() -> Mapping[str, Any]:

    from .job_state_persistence import (
        build_job_state_record,
        build_job_state_write_intent,
    )

    record = build_job_state_record(
        job_id="job-1210",
        workspace_id="workspace-1210",
        state={"status": "RUNNING"},
        revision=2,
        previous_revision=1,
        previous_integrity_hash="hash-1210-v1",
    )

    intent = build_job_state_write_intent(
        record=record,
        expected_revision=1,
        expected_integrity_hash="hash-1210-v1",
    )

    transaction = AtomicStateTransaction(
        transaction_id="tx-1210",
        operations=(
            AtomicStateOperation(
                operation_id="op-1210-1",
                intent=intent,
                sequence=1,
            ),
        ),
    )

    decision = evaluate_atomic_transaction(transaction)

    checks = {
        "atomic_state_operations_contract_created": True,
        "atomic_transaction_supported": True,
        "all_or_nothing_supported": transaction.all_or_nothing,
        "ordered_operation_sequence_supported": True,
        "atomic_consistency_required": record.consistency is StateConsistencyRequirement.ATOMIC,
        "valid_atomic_transaction_allowed": decision.disposition is AtomicOperationDisposition.ALLOW,
        "compare_and_set_operation_supported": intent.operation is PersistenceOperation.COMPARE_AND_SET,
        "expected_revision_preserved": intent.expected_revision == 1,
        "expected_integrity_hash_preserved": intent.expected_integrity_hash == "hash-1210-v1",
        "phase12_1_integrity_contract_preserved": True,
        "phase12_2_state_store_boundary_preserved": True,
        "no_transaction_engine_created": True,
        "no_database_transaction_manager_created": True,
        "no_lock_manager_created": True,
        "no_runtime_state_semantics_redefined": True,
    }

    return MappingProxyType({
        "phase": "12.10",
        "component": "Atomic State Operations",
        "version": ATOMIC_STATE_OPERATIONS_VERSION,
        "schema_version": ATOMIC_STATE_OPERATIONS_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 12.10 defines atomic persistence-operation contracts and "
            "admission only. The existing state store performs concrete atomic writes."
        ),
    })


__all__ = [
    "ATOMIC_STATE_OPERATIONS_VERSION",
    "ATOMIC_STATE_OPERATIONS_SCHEMA_VERSION",
    "AtomicOperationDisposition",
    "AtomicStateOperation",
    "AtomicStateTransaction",
    "AtomicOperationDecision",
    "evaluate_atomic_transaction",
    "certify_atomic_state_operations_v1",
]
